from django import forms
from .models import Genre, User
from django.contrib.auth.forms import UserChangeForm


class EditProfileForm(UserChangeForm):
    class Meta(UserChangeForm.Meta):
        model = User
        fields = [
            "username",
            "email",
            "gender",
            "location",
            "date_of_birth",
            "about",
            "user_image",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        for _, field in self.fields.items():
            field.widget.attrs["class"] = "form-control"


class NewNovelForm(forms.Form):
    novel_image = forms.ImageField(
        label="Image",
        help_text="",
        widget=forms.FileInput(attrs={"class": "form-control"}),
        required=False,
    )
    title = forms.CharField(
        label="Title (Required)",
        widget=forms.TextInput(attrs={"class": "form-control"}),
        max_length=200,
    )
    description = forms.CharField(
        label="Description (Required)",
        widget=forms.Textarea(attrs={"class": "form-control"}),
    )

    genres = forms.MultipleChoiceField(
        choices=[genre.serialize() for genre in Genre.objects.all()],
        widget=forms.CheckboxSelectMultiple,
    )


class NewChapterForm(forms.Form):
    num = forms.IntegerField(
        label="Chapter Number (Required)",
        widget=forms.NumberInput(
            attrs={
                "class": "form-control",
            }
        ),
    )
    title = forms.CharField(
        label="Title (Required)",
        widget=forms.TextInput(attrs={"class": "form-control"}),
        max_length=200,
    )
    content = forms.CharField(
        label="Chapter Content (Required)",
        widget=forms.Textarea(attrs={"class": "form-control", "rows": 50}),
    )
