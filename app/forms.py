from django import forms
from app.models import *

class Studentform(forms.ModelForm):
    class Meta:
        modal=Student
        field='__all__'

        