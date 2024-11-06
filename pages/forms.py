# forms.py
from django import forms

class TextGenerationForm(forms.Form):
    text_input = forms.CharField(label="Input Text", max_length=500, required=True)
    max_tokens = forms.IntegerField(label="Max Tokens", min_value=1, max_value=100, initial=20, required=True)
    bad_words = forms.CharField(label="Bad Words", max_length=200, required=False)
    stop_words = forms.CharField(label="Stop Words", max_length=200, required=False)
