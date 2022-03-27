from django.shortcuts import render
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.forms import PasswordChangeForm
from django.contrib.auth import update_session_auth_hash
from django.conf import settings
from app import forms
from app.models import Post
from django.core.mail import send_mail
import pandas as pd
import sklearn
import numpy as np

def homepage(request):
    return render(request,'index.html')



def homepage(request):
    return render(request,'index.html')


