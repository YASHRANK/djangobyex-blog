from django import forms
from .models import Comment


class EmailPostForm(forms.Form):
    name = forms.CharField(
        max_length=25, widget=forms.TextInput(attrs={'class': 'input'}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'input'}))
    to = forms.EmailField(widget=forms.TextInput(attrs={'class': 'input'}))
    comments = forms.CharField(required=False,
                               widget=forms.Textarea(attrs={'class': 'input'}))


class CommentForm(forms.ModelForm):
    class Meta:
        model = Comment
        fields = ('name', 'email', 'body')
        widgets = {
            'name': forms.TextInput(attrs={'class': 'input'}),
            'email': forms.TextInput(attrs={'class': 'input'}),
            'body': forms.Textarea(attrs={'class': 'input', 'cols': 30, 'rows': 60}),
        }


class SearchForm(forms.Form):
    query = forms.CharField(widget=forms.TextInput(
        attrs={'class': 'input is-medium is-primary'}))
