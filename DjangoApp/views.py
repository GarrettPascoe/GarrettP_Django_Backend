import requests
import json
from django.http import JsonResponse
from django.views.decorators.csrf import csrf_exempt
from django.shortcuts import render
from django.http import HttpResponse
from rest_framework import viewsets, permissions
from rest_framework.response import Response
from rest_framework.views import APIView
from .models import *
from .forms import *
from .serializers import *
#from .classification_model import *

# Gets a request -> Gives a response
# AKA a request handler or action
# Called a view in Django, but it is not a frontend HTML view.

#def home(request):
#    return HttpResponse("Hello, Django!")

# Each of these are essentially their own webpage

#home page
def say_hello(request):
    return render(request, 'Home.html', { 'name': 'Garrett'})

#member database
def members(request):
    all_members = Member.objects.all
    return render(request, 'members.html', {'all' : all_members})

#join form
def join(request):
    if request.method == "POST":
        #do form stuff
        form = MemberForm(request.POST or None)
        if form.is_valid():
            form.save()
        return render(request, 'join.html', {})

    else:
        return render(request, 'Join.html', {})

#resume - background and skills
def resume(request):
    return render(request, 'Resume.html', {})

#portfolio - list of projects
def portfolio(request):
    return render(request, 'Portfolio.html', {})

#machine learning showcase - will need a way for user input
def mlshowcase(request):
    return render(request, 'MLshowcase.html', {})

#database for test data - be careful to cite all sources
def database(request):
    return render(request, 'Database.html', {})

class CompanyViewset(viewsets.ViewSet):
    permission_classes = [permissions.AllowAny]
    queryset = CompanyContact.objects.all()
    serializer_class = CompanyContactSerializer
    
    def list(self, request):
        queryset = self.queryset
        serializer = self.serializer_class(queryset, many=True)
        return Response(serializer.data)
    
    def create(self, request):
        serializer = self.serializer_class(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=400)

    def retrieve(self, request, pk=None):
        company = self.queryset.get(pk=pk)
        serializer = self.serializer_class(company)
        return Response(serializer.data)

    def update(self, request, pk=None):
        company = self.queryset.get(pk=pk)
        serializer = self.serializer_class(company, data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        else:
            return Response(serializer.errors, status=400)

    def destroy(self, request, pk=None):
        company = self.queryset.get(pk=pk)
        company.delete()
        return Response(status=204)

#PredictionView goes here
        
        
        
        
# Section for FastAPI agent integration
        
AGENT_URL = "https://CarChooserGarrettP/run-agent"
CREATE_SESSION_URL = "https://CarChooserGarrettP/create-session"

@csrf_exempt
def carchooser(request):

    if request.method != "POST":
        return JsonResponse({"error": "POST required"}, status=405)

    body = json.loads(request.body)
    user_input = body.get("input")

    # Ensure session_id exists
    session_id = request.session.get("agent_session_id")

    if not session_id:
        response = requests.post(CREATE_SESSION_URL)
        session_id = response.json()["session_id"]
        request.session["agent_session_id"] = session_id

    # Get message history
    messages = request.session.get("chat_history", [])

    # Append user message
    messages.append({
        "type": "human",
        "content": user_input
    })

    # Call FastAPI agent
    response = requests.post(
        AGENT_URL,
        json={
            "session_id": session_id,
            "messages": messages
        },
        timeout=30
    )

    agent_reply = response.json()

    # Append AI response
    messages.append({
        "type": "ai",
        "content": agent_reply["message"]
    })

    # Save updated history
    request.session["chat_history"] = messages

    return JsonResponse({
        "reply": agent_reply,
        "messages": messages
    })
    
# End of FastAPI agent integration section

