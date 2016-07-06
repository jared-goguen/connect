from django import forms

class CreateForm(forms.Form):
    title = forms.CharField(max_length=30, label='Title', initial='New game')
