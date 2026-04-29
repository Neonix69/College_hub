from django import forms
from django.contrib.auth.forms import UserCreationForm

from .models import Course, Resource, User


class ResourceUploadForm(forms.ModelForm):
    class Meta:
        model = Resource
        fields = ["title", "resource_type", "exam_label", "year", "notes", "file"]
        widgets = {
            "notes": forms.Textarea(attrs={"rows": 3}),
        }


class UserRegistrationForm(UserCreationForm):
    course = forms.ModelChoiceField(
        queryset=Course.objects.none(),
        empty_label="Select your course",
        required=True,
    )
    enrollment_year = forms.IntegerField(
        required=True, min_value=2000, max_value=2100, help_text="Example: 2024"
    )
    about_me = forms.CharField(
        required=False, widget=forms.Textarea(attrs={"rows": 3})
    )
    avatar = forms.FileField(required=False)

    class Meta:
        model = User
        fields = [
            "username",
            "email",
            "course",
            "enrollment_year",
            "about_me",
            "avatar",
            "password1",
            "password2",
        ]

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["course"].queryset = Course.objects.order_by("code")


class UserProfileForm(forms.ModelForm):
    class Meta:
        model = User
        fields = ["course", "about_me", "avatar"]
        widgets = {
            "about_me": forms.Textarea(attrs={"rows": 4}),
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields["course"].queryset = Course.objects.order_by("code")
