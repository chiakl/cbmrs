import django_filters
from .models import *

class MovieFilter(django_filters.FilterSet):
    class Meta:
        model = MovieData
        fields = '__all__'
        exclude = ['id', 'description']