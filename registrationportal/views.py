from django.shortcuts import render, redirect
from django.contrib import messages
from django.contrib.auth.decorators import login_required
from competitions.models import Competition,Module

# Create your views here.

def home(request):
    competitions = Competition.objects.all()
    modules=Module.objects.all()
    return render(request, 'home/index.html', {'competitions': competitions,'modules':modules})

@login_required(login_url='login')
def rulebook(request):
    return render(request, 'rules.html',{'active_page':'rulebook'})
  
@login_required(login_url='login')
def contact(request):
    return render(request, 'contactus.html',{'active_page':'contact'})