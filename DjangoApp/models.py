from django.db import models

# Create your models here.

class Member(models.Model):
    fname = models.CharField(max_length = 20)
    lname = models.CharField(max_length = 20)
    email = models.EmailField(max_length = 30)
    passwd = models.CharField(max_length = 20)
    age = models.IntegerField()
    
    def __str__(self):
        return self.fname + ' ' + self.lname
    

class CompanyContact(models.Model):
    company = models.CharField(max_length = 50)
    email = models.EmailField(max_length = 50)
    

class ImageToClassify(models.Model):
    image = models.ImageField()