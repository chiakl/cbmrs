from django import forms 
from django.forms import Form
from recommender_app.models import Courses, SessionYearModel, MovieLover
from recommender_app.movieloverViews import movielover_preference


class DateInput(forms.DateInput):
    input_type = "date"


class AddMovieLoverForm(forms.Form):
    email = forms.EmailField(label="Email", max_length=50, widget=forms.EmailInput(attrs={"class":"form-control"}))
    password = forms.CharField(label="Password", max_length=50, widget=forms.PasswordInput(attrs={"class":"form-control"}))
    username = forms.CharField(label="Username", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))


class EditMovieLoverForm(forms.Form):
    username = forms.CharField(label="Username", max_length=50, widget=forms.TextInput(attrs={"class":"form-control"}))
    

