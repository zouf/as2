from django import forms as forms

from models import Page


class PageForm(forms.Form):
    content = forms.CharField(widget=forms.Textarea())

