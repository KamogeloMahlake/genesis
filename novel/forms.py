from django import forms

from .models import Genre

class NewNovelForm(forms.Form):
    title = forms.CharField(label="Title", max_length=200)
    description = forms.CharField(label="Description", widget=forms.Textarea)
    genres = forms.ModelMultipleChoiceField(
        queryset=Genre.objects.all(),
        widget=forms.CheckboxSelectMultiple,
        required=False
    )
    novel_image = forms.ImageField(label="Cover Image", required=False)