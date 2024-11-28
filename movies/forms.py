from django import forms

from .models import Review, Rating


class RatingForm(forms.ModelForm):
    class Meta:
        model = Rating
        fields = ['value']


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['text']
        widgets = {
            'text': forms.Textarea(
                attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Write your review here...'}),
        }
