from django import forms
from django.utils.safestring import mark_safe
from django.contrib.auth.forms import AuthenticationForm

class LoginForm(forms.Form):
    user_name = forms.CharField( label='Username:', max_length=100)
    password  = forms.CharField( label='Password:', max_length=100, widget=forms.PasswordInput)


# note that in views the label suffix has been removed, so in this form I had to add them.
class EmailForm(forms.Form):
    first_name  = forms.CharField(  label = 'First name:',  max_length=30)
    last_name   = forms.CharField(  label = 'Last name:',   max_length=30)
    email       = forms.EmailField( label = 'Email:',       max_length=30)
    affiliation = forms.CharField(  label = 'Affiliation:', max_length=200, widget=forms.Textarea)
    position    = forms.CharField(  label = mark_safe('Position: <br /><span class = "description">(e.g. undergraduate, faculty)</span>'),
                                                      max_length=30)
    dept        = forms.CharField(  label = 'Department:',  max_length=30)
    institute   = forms.CharField(  label = 'Institute:',   max_length=30)
    country     = forms.CharField(  label = 'Country:',     max_length=30)
    body        = forms.CharField(  label = mark_safe('Reasons for wishing to access PRIMO data: <br /> \
                                                       <span class="description">(indicate types desired, \
                                                       uses to which data will be put, projects (briefly))</span>'),
                                                       widget=forms.Textarea)
