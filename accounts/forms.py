from django import forms

class TextGenerationForm(forms.Form):
    text_input = forms.CharField(widget=forms.Textarea(attrs={'placeholder': 'Enter text to generate...'}))
    max_tokens = forms.IntegerField(initial=50)
    
    # These fields will be hidden
    bad_words = forms.CharField(required=False, widget=forms.HiddenInput())
    stop_words = forms.CharField(required=False, widget=forms.HiddenInput())
    pad_id = forms.IntegerField(initial=2, widget=forms.HiddenInput())
    end_id = forms.IntegerField(initial=2, widget=forms.HiddenInput())
