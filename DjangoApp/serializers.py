from rest_framework import serializers
from .models import *

class MemberSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = Member
        fields = ('fname', 'lname', 'email', 'passwd', 'age')

class CompanyContactSerializer(serializers.ModelSerializer):
    
    class Meta:
        model = CompanyContact
        fields = ('company', 'email')
        
class ImageToClassifySerializer(serializers.ModelSerializer):
    
    class Meta:
        model = ImageToClassify
        fields = ('image')