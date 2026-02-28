# %%
from langchain.tools import tool
from langchain_openai import ChatOpenAI
from langchain.agents import create_agent
from langchain.agents import AgentState
from langchain.agents.middleware import wrap_model_call, ModelRequest, ModelResponse, AgentMiddleware, SummarizationMiddleware
from langchain.messages import HumanMessage, AIMessage, SystemMessage
from langchain_core.prompts import ChatPromptTemplate
from langchain_core.prompts import PromptTemplate
from langchain_core.output_parsers import PydanticOutputParser
from dotenv import load_dotenv
import os
from pydantic import BaseModel, Field, model_validator
from typing import Literal, Optional
from enum import Enum
import json

load_dotenv()


basic_model = ChatOpenAI(model="gpt-4o-mini")


# ------ Section that handles the user's input ------

    
class MakeEnum(str, Enum):
    ford = "Ford"
    
# Pydantic Model for vehicle attributes
class VehiclePreferences(BaseModel):
    manufacturer: MakeEnum = Field(default=MakeEnum.ford, description="Manufacturer, must be Ford")
    model: Optional[str] = None
    body_style:  Optional[str] = None
    price_range:  Optional[str] = None
    mileage:  Optional[str] = None
    safety_rating:  Optional[str] = None
    color:  Optional[str] = None
    storage_space:  Optional[str] = None
    seat_capacity:  Optional[str] = None
    comfort:  Optional[str] = None
    luxury:  Optional[str] = None
    special_features: Optional[str] = None
    unwanted_features: Optional[str] = None
    
# Pydantic Model to validate user input
class UserQuery(BaseModel):
    intent: str = Field(..., description="A description of what the user is looking for.")
    preferences: list[VehiclePreferences] = Field(
        default_factory=list,
        description="List of parsed structured preferences about the Ford vehicle."
    )
    
    
inputParser = PydanticOutputParser(pydantic_object=VehiclePreferences)

extract_prompt = PromptTemplate(
    template=(
        "Extract all vehicle preferences from the following message.\n"
        "Return valid JSON matching the schema.\n\n"
        "Message: {input}\n\n"
        "{format_instructions}"
    ),
    partial_variables={"format_instructions": inputParser.get_format_instructions()},
    input_variables=["input"]
)

extract_chain = extract_prompt | basic_model | inputParser


@tool("extract_preferences")
def extract_prefs_tool(user_input: str):
    """Extract vehicle preferences from user prompt"""
    return extract_chain.invoke({"input": user_input})
    
    
# ------ End of section that handles the user's input ------
    
    
    
# ------ Section that handles the model's stored data ------

class PreferenceMemory:
    def __init__(self):
        self._prefs = VehiclePreferences()

    def update(self, new_prefs: VehiclePreferences):
        """Merge new preferences into memory."""
        updated = self._prefs.model_dump()
        for key, value in new_prefs.model_dump().items():
            if value is not None:
                updated[key] = value
        self._prefs = VehiclePreferences(**updated)

    def get(self) -> VehiclePreferences:
        """Return the full merged preference model."""
        return self._prefs

    def reset(self):
        """Optional: clear memory."""
        self._prefs = VehiclePreferences()
        
        

memory = PreferenceMemory()

@tool("update_preferences")
def update_preferences_tool(**kwargs):
    """Update user vehicle preferences."""
    new_prefs = VehiclePreferences(**kwargs)
    memory.update(new_prefs)
    return "Preferences updated."

@tool("get_preferences")
def get_preferences_tool(_=None):
    """Get current stored user vehicle preferences."""
    return memory.get().model_dump()

# ------ End of section that handles the model's stored data ------


    
# ------ Section that formats the model's response ------

# Pydantic model to structure model response
class BotResponse(BaseModel):
        message: str = Field(..., description="The chatbot response")

        link: Optional[str] = Field(None, description="URL of a Ford vehicle page. Only present when recommending a vehicle.")

        action_required: Optional[Literal["confirm", "clarify", "provide_info"]] = None

        @model_validator(mode="after")
        def validate_state_logic(self):
        # If confirming a selection -> must include link
            if self.action_required == "confirm" and not self.link:
                raise ValueError("confirm responses must include a vehicle link")

            # If clarifying -> must NOT include link
            if self.action_required == "clarify" and self.link:
                raise ValueError("clarification responses cannot include a link")

            return self
    
outputParser = PydanticOutputParser(pydantic_object=BotResponse)

outputPrompt = ChatPromptTemplate.from_messages(
    [
        (
            "system",
            """
            You must format your final answer as instructed below.
            The answer must be in a JSON format.

            {format_instructions}
            """
        ),
        ("human", "{final_answer}")
    ]
).partial(format_instructions=outputParser.get_format_instructions())


formatter_chain = outputPrompt | basic_model | outputParser


# ------ End of section that formats the model's response ------


SYSTEM_PROMPT = """
You are a helpful assistant that recommends Ford vehicles based on a user's
stated preferences and constraints. Try to recommend the best fit even if
the user's preferences are vague.

Your goals:
- Recommend the most suitable Ford vehicle
- Be concise, accurate, and user-friendly
"""


# Tool to send a query to ChatGPT and handle the response
@tool
def search(query: str) -> str:
    """Search for information."""
    return f"Results for: {query}"



# Agent constructor
agent = create_agent(
    model=basic_model,  # Default model
    tools=[search, extract_prefs_tool, update_preferences_tool, get_preferences_tool],
    middleware=[],
    system_prompt=SYSTEM_PROMPT
)

# %%
messages = []

while True:
    user_input = input("\nUser: ")

    if user_input.lower() in {"exit", "quit"}:
        break

    # 1 — add user message
    messages.append(HumanMessage(content=user_input))

    # 2 — run agent with full history
    result = agent.invoke({"messages": messages})

    # 3 — extract final agent reply
    ai_messages = [m for m in result["messages"] if isinstance(m, AIMessage)]
    ai_reply = ai_messages[-1]

    # 4 — append to history (critical for memory)
    messages.append(ai_reply)

    # 5 — structure the response
    structured: BotResponse = formatter_chain.invoke({
        "final_answer": ai_reply.content
    })

    # 6 — display
    print("\nAgent:", structured.message)

    if structured.link:
        print("Link:", structured.link)

    if structured.action_required:
        print("(Action:", structured.action_required, ")")


