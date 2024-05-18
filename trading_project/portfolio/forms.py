from django import forms


class StockForm(forms.Form):
    stock_name = forms.CharField(max_length=10, label='Stock Symbol')

class BuyForm(forms.Form):
    quantity = forms.IntegerField(label='Quantity')
