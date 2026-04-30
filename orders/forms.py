from django import forms
from .models import Order

class OrderForm(forms.ModelForm):
    quantity = forms.IntegerField(min_value=1, initial=1, required=False, widget=forms.NumberInput(attrs={'class': 'form-control'}))
    
    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['room_number'].required = False
        
    def clean(self):
        cleaned_data = super().clean()
        order_type = cleaned_data.get('order_type')
        room_number = cleaned_data.get('room_number')
        
        if order_type == 'Room Delivery' and not room_number:
            self.add_error('room_number', 'Room number is required for Room Delivery.')
            
        return cleaned_data

    class Meta:
        model = Order
        fields = ['order_type', 'room_number', 'delivery_date', 'delivery_time', 'want_it_now', 'delivery_details']
        widgets = {
            'order_type': forms.Select(attrs={'class': 'form-select'}),
            'room_number': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'e.g. IT Building Room 402'}),
            'delivery_date': forms.DateInput(attrs={'type': 'date', 'class': 'form-control'}),
            'delivery_time': forms.TimeInput(attrs={'type': 'time', 'class': 'form-control'}),
            'want_it_now': forms.CheckboxInput(attrs={'class': 'form-check-input'}),
            'delivery_details': forms.Textarea(attrs={'class': 'form-control', 'rows': 3}),
        }

class OrderStatusForm(forms.ModelForm):
    class Meta:
        model = Order
        fields = ['status']
        widgets = {
            'status': forms.Select(attrs={'class': 'form-select'})
        }

class CancelOrderForm(forms.ModelForm):
    CANCEL_REASONS = [
        ('Ordered by mistake', 'Ordered by mistake'),
        ('Found a better price', 'Found a better price'),
        ('Item no longer needed', 'Item no longer needed'),
        ('Expected delivery time too long', 'Expected delivery time too long'),
        ('Other', 'Other'),
    ]
    cancel_reason = forms.ChoiceField(choices=CANCEL_REASONS, widget=forms.Select(attrs={'class': 'form-select'}))
    
    class Meta:
        model = Order
        fields = ['cancel_reason', 'cancel_message']
        widgets = {
            'cancel_message': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Optional details...'})
        }
