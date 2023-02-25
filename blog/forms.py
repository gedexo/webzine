from django import forms
from django.forms.widgets import Textarea, TextInput

from .models import Review


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ("name", "review")
        widgets = {
            "name": TextInput(
                attrs={
                    "class": "form-control",
                    "placeholder": "Name",
                    "required": "required",
                    "autocomplete": "off",
                    "name": "name",
                }
            ),
            "review": Textarea(
                attrs={
                    "class": "form-control w-100",
                    "placeholder": "Write Comment",
                    "rows": "3",
                    "name": "comment",
                    "id": "comment",
                }
            ),
        }
