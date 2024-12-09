from django import forms
from .models import Member, CompanyContact, ImageToClassify

class MemberForm(forms.ModelForm):
    class Meta:
        model = Member
        fields = ['fname', 'lname', 'email', 'passwd', 'age']
        
class CompanyForm(forms.ModelForm):
    class Meta:
        model = CompanyContact
        fields = ['company', 'email']
        
        
class ImageForm(forms.ModelForm):
    class Meta:
        model = ImageToClassify
        fields = ['image']