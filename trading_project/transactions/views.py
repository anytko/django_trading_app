# views.py
import io
import base64
import matplotlib.pyplot as plt
from django.shortcuts import render
from transactions.models import Transaction
from accounts.models import Portfolio, Stock
from django.contrib.auth.decorators import login_required
from datetime import timedelta
from matplotlib import dates as mdates 
from django.utils import timezone


@login_required
def transaction_history(request):
    try:
        user = request.user
        # Fetch the user's portfolio
        portfolio, _ = Portfolio.objects.get_or_create(user=user)

        # Fetch all transactions for the user
        transactions = Transaction.objects.filter(user=user).order_by('timestamp')

        # Generate transaction chart data
        chart_data = generate_transaction_chart(request)

        return render(request, 'transaction_history.html', {'transactions': transactions, 'chart_data': chart_data})

    except Exception as e:
        print("Error:", e)
        return render(request, 'transaction_history.html', {'transactions': [], 'chart_data': None})

def generate_transaction_chart(request):
    try:
        user = request.user
        # Fetch the user's portfolio
        portfolio, _ = Portfolio.objects.get_or_create(user=user)

        # Fetch all transactions for the user
        transactions = Transaction.objects.filter(user=user).order_by('timestamp')

        if not transactions.exists():
            print("No transactions found.")
            return None

        # Get the date range from the first to the last transaction date
        start_date = transactions.first().timestamp.date()
        end_date = transactions.last().timestamp.date() + timedelta(days=1)  # Include the end date
        date_range = [start_date + timedelta(days=i) for i in range((end_date - start_date).days)]

        # Initialize variables for plotting
        portfolio_values = []

        # Initialize portfolio value for the first day
        current_portfolio_value = portfolio.balance

        # Initialize variables to track the current day
        current_day = start_date

        # Iterate over each date in the date range
        for date in date_range:
            # Update current prices for all stocks in the portfolio
            for stock in portfolio.stock_set.all():
                stock.update_current_price()

            # Calculate the total stock value for the current date
            total_stock_value = sum(stock.current_price * stock.quantity for stock in portfolio.stock_set.all() if stock.current_price is not None and stock.quantity is not None)

            # Calculate the portfolio value for the current day
            current_portfolio_value = total_stock_value + portfolio.balance

            # Append the portfolio value for the current day
            portfolio_values.append(current_portfolio_value)

            # Move to the next day
            current_day += timedelta(days=1)

        # Plot line chart
        plt.figure(figsize=(10, 6))
        plt.plot(date_range, portfolio_values, marker='o', linestyle='-')
        plt.title('Portfolio Value Fluctuations')
        plt.xlabel('Date')
        plt.ylabel('Portfolio Value')

        # Set x-axis ticks to show one day at a time
        plt.xticks(date_range, rotation=45)  # Use date_range as ticks
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

        plt.tight_layout()

        # Save the plot to a byte string
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)

        # Encode the image data as base64
        encoded_img = base64.b64encode(buf.getvalue()).decode('utf-8')

        plt.close()

        return encoded_img

    except Exception as e:
        print("Error generating transaction chart:", e)
        return None
