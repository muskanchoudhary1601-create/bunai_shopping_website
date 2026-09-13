from django import forms
from .models import Category, Product, Customer, Order, OrderItem, Review


class CheckoutForm(forms.Form):
    PAYMENT_CHOICES = [
        ('UPI', 'UPI / QR Code (Google Pay, PhonePe, Paytm)'),
        ('COD', 'Cash on Delivery (Pay at Doorstep)'),
        ('CARD', 'Credit / Debit Card (Visa, Mastercard, RuPay)'),
        ('NET_BANKING', 'Net Banking (All Major Indian Banks)'),
    ]

    full_name = forms.CharField(
        max_length=150,
        widget=forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'e.g., Ananya Sharma', 'required': True})
    )
    email = forms.EmailField(
        widget=forms.EmailInput(attrs={'class': 'form-control', 'placeholder': 'name@example.com', 'required': True})
    )
    phone = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': '+91 98765 43210', 'required': True})
    )
    shipping_address = forms.CharField(
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'House / Flat no., Street, Landmark', 'required': True})
    )
    city = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'City', 'required': True})
    )
    state = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'State / Province', 'required': True})
    )
    postal_code = forms.CharField(
        max_length=20,
        widget=forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'PIN / Postal Code', 'required': True})
    )
    payment_method = forms.ChoiceField(
        choices=PAYMENT_CHOICES,
        widget=forms.RadioSelect(attrs={'class': 'form-check-input'})
    )
    coupon_code = forms.CharField(
        max_length=50,
        required=False,
        widget=forms.TextInput(attrs={'class': 'form-control text-uppercase', 'placeholder': 'Promo Code'})
    )
    notes = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={'class': 'form-control', 'rows': 2, 'placeholder': 'Gift message or delivery instructions (optional)'})
    )


class OrderTrackingForm(forms.Form):
    order_number = forms.CharField(
        max_length=50,
        widget=forms.TextInput(attrs={'class': 'form-control form-control-lg font-monospace', 'placeholder': 'e.g. BN-202609-AB12', 'required': True})
    )
    contact_info = forms.CharField(
        max_length=100,
        widget=forms.TextInput(attrs={'class': 'form-control form-control-lg', 'placeholder': 'Phone number or Email used at checkout', 'required': True})
    )


class ReviewForm(forms.ModelForm):
    class Meta:
        model = Review
        fields = ['author_name', 'rating', 'comment']
        widgets = {
            'author_name': forms.TextInput(attrs={'class': 'form-control', 'placeholder': 'Your Name'}),
            'rating': forms.Select(choices=[(5, '5 Stars - Exceptional Craft'), (4, '4 Stars - Very Good'), (3, '3 Stars - Good'), (2, '2 Stars - Average'), (1, '1 Star - Poor')], attrs={'class': 'form-select'}),
            'comment': forms.Textarea(attrs={'class': 'form-control', 'rows': 3, 'placeholder': 'Share your experience with this handcrafted piece...'}),
        }
