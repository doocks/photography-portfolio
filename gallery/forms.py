from django import forms
from .models import Booking
from .models import Review

class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['client_name', 'client_email', 'rating', 'review_text', 'event_type']
        widgets = {
            'client_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}),
            'client_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email'}),
            'rating': forms.Select(attrs={'class': 'form-control'}),
            'review_text': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Share your experience...'}),
            'event_type': forms.Select(attrs={'class': 'form-control'}),
        }
        
class BookingForm(forms.ModelForm):
    event_date = forms.DateField(
        widget=forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
        required=True
    )

    class Meta:
        model = Booking
        fields = ['client_name', 'client_email', 'client_phone', 'event_date', 'package', 'message']
        widgets = {
            'client_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Full Name'}),
            'client_email': forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'your@email.com'}),
            'client_phone': forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+1 234 567 8900'}),
            'package': forms.Select(attrs={'class': 'form-control'}),
            'message': forms.Textarea(attrs={'class': 'form-control', 'rows': 4, 'placeholder': 'Tell me about your event...'}),
        }

class ContactForm(forms.Form):
    name = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}))
    email = forms.EmailField(widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'Your Email'}))
    subject = forms.CharField(max_length=200, widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Subject'}))
    message = forms.CharField(widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 5, 'placeholder': 'Your Message'}))

class ClientGalleryAccessForm(forms.Form):
    access_code = forms.CharField(
        max_length=50, 
        widget=forms.TextInput(attrs={
            'class': 'form-control', 
            'placeholder': 'Enter your access code',
            'autocomplete': 'off',
            'autocapitalize': 'characters'
        }),
        required=True
    )
    
    def clean_access_code(self):
        code = self.cleaned_data.get('access_code', '').strip()
        if not code:
            raise forms.ValidationError('Access code is required.')
        if len(code) < 4:
            raise forms.ValidationError('Invalid access code format.')
        return code