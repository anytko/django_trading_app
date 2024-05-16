from django import forms

class StockForm(forms.Form):
    stock_name = forms.CharField(label='Stock Name:', max_length=20)