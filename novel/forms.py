from django import forms
from .models import Genre

class NewNovelForm(forms.Form):
    novel_image = forms.ImageField(
        label="Image (Required)",
        help_text="",
        widget=forms.FileInput(
            attrs={
                "class": "form-control"
            }
        )
    )
    title = forms.CharField(
        label="Title (Required)",
        widget=forms.TextInput(attrs={
            "class": "form-control"
        }),
        max_length=200
    )
    description = forms.CharField(
        label="Description (Required)",
        widget=forms.Textarea(
            attrs={
                "class": "form-control"
            }
        )
    )

    genres = forms.MultipleChoiceField(
        choices=[genre.serialize() for genre in Genre.objects.all()],
        widget=forms.CheckboxSelectMultiple
    )