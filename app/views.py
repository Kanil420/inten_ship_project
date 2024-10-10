from django.shortcuts import render

# Create your views here.
from app.forms import *
def insert_student(request):
    d={'STOE':Studentform()}
    return render(request,'insert_student.html',d)
