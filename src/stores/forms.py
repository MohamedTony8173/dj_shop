from django import forms 
from .models import RatingReview

class RatingForm(forms.ModelForm):
    class Meta:
        model = RatingReview
        fields = ['review','rating','subject']