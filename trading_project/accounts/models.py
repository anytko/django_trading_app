from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone
from decimal import Decimal

class Portfolio(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    balance = models.DecimalField(max_digits=10, decimal_places=2, default=10000)

    def buy_stock(self, stock_symbol, stock_price, quantity, purchase_date=None):
        total_cost = stock_price * quantity
        if total_cost <= self.balance:
            self.balance -= total_cost
            self.save()
            
            # Check if the stock already exists in the portfolio
            stock, created = Stock.objects.get_or_create(
                portfolio=self,
                symbol=stock_symbol,
                defaults={
                    'quantity': quantity,
                    'purchase_price': stock_price,
                    'purchase_date': purchase_date or timezone.now()
                }
            )
            
            if not created:
                # If stock already exists, update the quantity and average purchase price
                new_quantity = stock.quantity + quantity
                new_purchase_price = ((stock.purchase_price * stock.quantity) + total_cost) / new_quantity
                stock.quantity = new_quantity
                stock.purchase_price = new_purchase_price
                stock.purchase_date = purchase_date or timezone.now()  # Update the purchase date to the latest purchase
                stock.save()

            return True, stock
        else:
            return False, None

class Stock(models.Model):
    portfolio = models.ForeignKey(Portfolio, on_delete=models.CASCADE)
    symbol = models.CharField(max_length=10)
    quantity = models.IntegerField()
    purchase_price = models.DecimalField(max_digits=10, decimal_places=2)
    purchase_date = models.DateTimeField(default=timezone.now)
    sell_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    sell_date = models.DateTimeField(null=True, blank=True)
    # Add a field for current_price
    current_price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)

    def update_current_price(self):
        # Fetch the current price for this stock symbol from an external source (e.g., API)
        try:
            # Example: Fetch current price using yfinance library
            stock = yf.Ticker(self.symbol)
            current_data = stock.history(period='1d')
            self.current_price = Decimal(str(current_data['Close'][0]))  # Convert to Decimal
            self.save()
        except Exception as e:
            # Handle exceptions appropriately (e.g., log error)
            print(f"Error updating current price for {self.symbol}: {e}")
