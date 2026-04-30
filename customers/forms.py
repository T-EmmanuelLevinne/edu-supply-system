from django import forms
from django.contrib.auth.models import User
from .models import Customer

class UserRegistrationForm(forms.ModelForm):
    first_name = forms.CharField(max_length=100, required=True, label="First Name")
    middle_name = forms.CharField(max_length=100, required=False, label="Middle Name")
    last_name = forms.CharField(max_length=100, required=True, label="Last Name")
    email = forms.EmailField(required=True, label="Email Address")
    password = forms.CharField(widget=forms.PasswordInput)
    password_confirm = forms.CharField(widget=forms.PasswordInput, label="Confirm Password")

    class Meta:
        model = User
        fields = ['username', 'email', 'first_name', 'last_name']

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get("password")
        password_confirm = cleaned_data.get("password_confirm")
        if password and password_confirm and password != password_confirm:
            raise forms.ValidationError("Passwords do not match!")
        return cleaned_data

class CustomerForm(forms.ModelForm):
    student_id = forms.CharField(max_length=50, required=True, label="Student ID Number")
    course = forms.CharField(max_length=150, required=True, label="Course")

    class Meta:
        model = Customer
        fields = ['student_id', 'course', 'phone', 'address']
