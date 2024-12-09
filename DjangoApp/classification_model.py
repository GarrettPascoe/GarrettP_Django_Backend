import torch
import torch.nn as nn
import torch.nn.functional as F
import torchvision
from torchvision import transforms
from torchvision.transforms import ToTensor
from torchvision.transforms import v2
from PIL import Image


class Net(nn.Module):
    def __init__(self):
        super().__init__()
        self.conv1 = nn.Conv2d(3, 6, 5)             # First Convolution Layer - Parameters: (3 (# channels for input images), 6 (# channels for output images), 5 (5x5 tiles))
                                                    
        self.conv2 = nn.Conv2d(6, 16, 5)            # Second Convolution Layer
        
        self.conv3 = nn.Conv2d(16, 32, 5)           # Third Convolution Layer
        
        self.conv4 = nn.Conv2d(32, 64, 5)           # Fourth Convolution Layer - Unused in current model
        
        self.pool = nn.MaxPool2d(2, 2)              # Max Pool Layer - Parameters: (2 (2x2 tile), 2 (shifts 2 pixels per stride))
        
        self.fc1 = nn.Linear(32 * 12 * 12, 1000)    # First Linear Layer - Parameters: (# of features for input samples, # of features for ouput samples)
        
        self.fc2 = nn.Linear(1000, 100)             # Second Linear Layer
        
        self.fc3 = nn.Linear(100, 3)                # Third Linear Layer
        
        #self.softmax = nn.Softmax(dim=1)

    def forward(self, x):
        
        x = self.pool(F.relu(self.conv1(x)))        # First Convolution Layer - Input: (32 (batch size), 3-Channels, 128 height, 128 width) - Output: (32, 6, 124, 124)
        
                                                    # First Max Pool Layer - Input: (32, 6, 124, 124) - Output: (32, 6, 62, 62)
        
        x = self.pool(F.relu(self.conv2(x)))        # Second Convolution Layer - Input: (32, 6, 62, 62) - Output: (32, 16, 58, 58)
        
                                                    # Second Max Pool Layer - Input: (32, 16, 58, 58) - Output: (32, 16, 29, 29)
        
        x = self.pool(F.relu(self.conv3(x)))        # Third Convolution Layer - Input: (32, 16, 29, 29) - Output: (32, 32, 25, 25)
        
                                                    # Third Max Pool Layer - Input: (32, 32, 25, 25) - Output: (32, 32, 12, 12)
        
        #x = self.pool(F.relu(self.conv4(x)))       # Unused in current model
        
        x = torch.flatten(x, 1)                     # Flatten all dimensions except batch_size
        
        x = F.relu(self.fc1(x))                     # First Linear Layer - Input: (4608 features) - Output: (1000 features) - ReLu
        
        x = F.relu(self.fc2(x))                     # Second Linear Layer - Input: (1000 features) - Output: (100 features) - ReLu
        
        x = self.fc3(x)                             # Third Linear Layer - Input: (100 features) - Output: (3 features)
        
        #x = self.softmax(x)
        
        return x                                    # The highest value between the final 3 features will determine the guess of the image's classification
    
    
def load_model():
    model = Net() # Replace YourModel with your actual model class
    model.load_state_dict(torch.load('D:/Projects/Open Projects/Full GP Website/DjangoProject/DjangoApp/classification_model3.pth', weights_only=True))
    model.eval()  # Set the model to evaluation mode
    return model