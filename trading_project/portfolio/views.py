import io
import base64
import matplotlib
matplotlib.use('Agg')  
import matplotlib.pyplot as plt
from django.shortcuts import render, redirect
from .forms import StockForm, BuyForm
from accounts.models import Portfolio, Stock
import yfinance as yf
from decimal import Decimal
from collections import defaultdict
from django.http import HttpResponseRedirect
from django.urls import reverse
from collections import defaultdict
from django.contrib.auth.decorators import login_required
from transactions.models import Transaction
from django.utils import timezone


def generate_stock_chart(stock_name):
    try:
        # Fetch historical data for the last year with interval='1mo'
        stock = yf.Ticker(stock_name)
        hist = stock.history(period='1y', interval='1mo')

        plt.figure(figsize=(10, 5))
        plt.plot(hist.index, hist['Close'])
        plt.title(f'{stock_name} Price Over Last Year')
        plt.xlabel('Date')
        plt.ylabel('Price')
        plt.xticks(rotation=45)
        plt.tight_layout()

        # Convert the plot to a byte string
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()

        # Encode the image data as base64
        encoded_img = base64.b64encode(buf.getvalue()).decode('utf-8')

        return encoded_img
    except Exception as e:
        return None

def get_current_price(stock_name):
    try:
        stock = yf.Ticker(stock_name)
        current_data = stock.history(period='1d')
        current_price = Decimal(str(current_data['Close'][0]))
        return current_price
    except Exception as e:
        return None

@login_required
def portfolio(request):
    context = {}

    # Fetch the user's portfolio
    portfolio, _ = Portfolio.objects.get_or_create(user=request.user)

    # Initialize both forms
    stock_form = StockForm()
    buy_form = BuyForm()

    if request.method == 'POST':
        if 'action' in request.POST:
            if request.POST['action'] == 'check_price':
                stock_form = StockForm(request.POST)
                if stock_form.is_valid():
                    stock_name = stock_form.cleaned_data['stock_name']

                    try:
                        # Get current stock price
                        current_price = get_current_price(stock_name)
                        if current_price:
                            context['current_price'] = current_price
                            context['stock_form'] = stock_form

                            # Generate stock chart
                            chart_data = generate_stock_chart(stock_name)
                            if chart_data:
                                context['chart'] = chart_data
                            else:
                                context['error'] = "Failed to fetch stock data or generate chart."
                        else:
                            context['error'] = "Failed to fetch current price of the stock."
                    except Exception as e:
                        context['error'] = f"Error processing request: {str(e)}"

            elif request.POST['action'] == 'buy':
                stock_name = request.POST.get('stock_name')
                buy_form = BuyForm(request.POST)
                if buy_form.is_valid():
                    quantity = buy_form.cleaned_data['quantity']
                    if quantity < 1:
                        context['error'] = "Quantity must be at least 1."
                    else:
                        try:
                            # Get current stock price
                            current_price = get_current_price(stock_name)

                            # Calculate total cost for the specified quantity of shares
                            total_cost = current_price * quantity

                            if total_cost <= portfolio.balance:

                                Transaction.objects.create(
                                user=request.user,
                                transaction_type='BUY',
                                stock_symbol=stock_name,
                                quantity=quantity,
                                price=current_price,
                                timestamp=timezone.now()
                                )
                                # Deduct the total cost from the balance
                                portfolio.balance -= total_cost
                                portfolio.save()

                                # Check if the stock already exists in the user's portfolio
                                stock_instance, created = Stock.objects.get_or_create(
                                    symbol=stock_name,
                                    portfolio=portfolio,
                                    defaults={'quantity': 0, 'purchase_price': current_price}
                                )

                                # If the stock already exists, update the quantity and purchase price
                                if not created:
                                    stock_instance.quantity += quantity
                                    stock_instance.purchase_price = current_price
                                else:
                                    stock_instance.quantity = quantity

                                stock_instance.save()

                                # Update context with success message
                                context['success_message'] = f"Bought {quantity} shares of {stock_name}"
                            else:
                                context['error'] = "Insufficient balance to buy the stock."

                        except Exception as e:
                            context['error'] = f"Error processing request: {str(e)}"

        elif any(key.startswith('action_sell_') for key in request.POST):
            for key in request.POST:
                if key.startswith('action_sell_'):
                    stock_symbol = key.replace('action_sell_', '')  # Extract stock symbol from the key
                    quantity_to_sell = int(request.POST.get(f'quantity_to_sell_{stock_symbol}', 0))

                    # Fetch the stock instance
                    stock_instance = Stock.objects.filter(symbol=stock_symbol, portfolio=portfolio).first()

                    if stock_instance:
                        if 0 < quantity_to_sell <= stock_instance.quantity:  # Check if quantity to sell is valid
                            try:
                                # Fetch the current price of the stock
                                current_price = get_current_price(stock_symbol)

                                if current_price:
                                    # Calculate earnings from selling the specified quantity of shares
                                    earnings = current_price * quantity_to_sell
                                    Transaction.objects.create(
                                    user=request.user,
                                    transaction_type='SELL',
                                    stock_symbol=stock_symbol,
                                    quantity=quantity_to_sell,
                                    price=current_price,
                                    timestamp=timezone.now()
                                    )
                                    # Update the portfolio and stock instance
                                    portfolio.balance += earnings
                                    stock_instance.quantity -= quantity_to_sell

                                    # If all shares are sold, remove the stock from the portfolio
                                    if stock_instance.quantity == 0:
                                        stock_instance.delete()
                                    else:
                                        stock_instance.save()

                                    portfolio.save()

                                    # Redirect back to the portfolio page after successful sale
                                    return HttpResponseRedirect(reverse('portfolio'))
                            except Exception as e:
                                # Handle errors appropriately
                                context['error'] = f"Error selling stock: {e}"
                        else:
                            # If trying to sell invalid quantity, return an error
                            context['error'] = "Invalid quantity to sell."
                    else:
                        # If stock instance does not exist, return an error
                        context['error'] = "Stock not found in portfolio."


    # Fetch user's current stocks and aggregate by symbol
    user_stocks = Stock.objects.filter(portfolio=portfolio)
    aggregated_stocks = defaultdict(lambda: {'quantity': 0, 'purchase_price': 0, 'current_price': 0})

    for stock in user_stocks:
        if stock.symbol in aggregated_stocks:
            aggregated_stocks[stock.symbol]['quantity'] += stock.quantity
            aggregated_stocks[stock.symbol]['purchase_price'] += stock.purchase_price * stock.quantity
            aggregated_stocks[stock.symbol]['current_price'] += get_current_price(stock.symbol) * stock.quantity
        else:
            aggregated_stocks[stock.symbol] = {
                'quantity': stock.quantity,
                'purchase_price': stock.purchase_price * stock.quantity,
                'current_price': get_current_price(stock.symbol) * stock.quantity
            }

    # Convert aggregated_stocks to a list of dictionaries
    context['aggregated_stocks'] = [{'symbol': k, 'quantity': v['quantity'], 'purchase_price': v['purchase_price'], 'current_price': v['current_price']} for k, v in aggregated_stocks.items()]

    # Fetch chart data for the overall portfolio
    chart_data = generate_stock_chart(portfolio)
    if chart_data:
        context['chart'] = chart_data

    # Update context with portfolio and forms
    context['portfolio'] = portfolio
    context['stock_form'] = stock_form
    context['buy_form'] = buy_form

    return render(request, 'portfolio/portfolio.html', context)



def reset_account(request):
    user = request.user
    initial_balance = 10000  # Set this to your desired initial balance

    # Delete all transactions for the user
    Transaction.objects.filter(user=user).delete()

    # Reset portfolio balance and delete all stocks
    portfolio, _ = Portfolio.objects.get_or_create(user=user)
    portfolio.balance = initial_balance
    portfolio.save()

    Stock.objects.filter(portfolio=portfolio).delete()

    return redirect('portfolio')