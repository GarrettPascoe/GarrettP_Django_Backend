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
        

