from django import forms
from .models import Genre

class RatingForm(forms.Form):
    story = forms.IntegerField(
        label="Story Rating(Out of Ten) (Required)",
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
            }
        ),
        max_value=10,
        min_value=1
    )
    world = forms.IntegerField(
        label="World Rating(Out of Ten) (Required)",
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
            }
        ),
        max_value=10,
        min_value=1
    )
    writing = forms.IntegerField(
        label="Writing Rating(Out of Ten) (Required)",
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
            }
        ),
        max_value=10,
        min_value=1
    )
    characters = forms.IntegerField(
        label="Characters Rating(Out of Ten) (Required)",
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
            }
        ),
        max_value=10,
        min_value=1
    )

class NewNovelForm(forms.Form):
    novel_image = forms.ImageField(
        label="Image",
        help_text="",
        widget=forms.FileInput(
            attrs={
                "class": "form-control"
            }
        ),
        required=False
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

class NewChapterForm(forms.Form):
    num = forms.IntegerField(
        label="Chapter Number (Required)",
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
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
    content = forms.CharField(
        label="Chapter Content (Required)",
        widget=forms.Textarea(
            attrs={
                "class": "form-control",
                "rows": 50
            }
        )
    )
        
     
