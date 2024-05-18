# views.py
import io
import base64
import matplotlib.pyplot as plt
from django.shortcuts import render
from transactions.models import Transaction
from accounts.models import Portfolio
from django.contrib.auth.decorators import login_required
from datetime import timedelta
from matplotlib import dates as mdates 

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
        end_date = transactions.last().timestamp.date()
        date_range = [start_date + timedelta(days=i) for i in range((end_date - start_date).days + 1)]

        # Initialize variables for plotting
        portfolio_values = []

        # Calculate total portfolio value for each day
        current_portfolio_value = portfolio.balance
        for date in date_range:
            # Check if there's a transaction on the current date
            transactions_on_date = transactions.filter(timestamp__date=date)
            if transactions_on_date.exists():
                # Calculate the total stock value for the current date
                total_stock_value = sum(
                    stock.current_price * stock.quantity for stock in portfolio.stock_set.all()
                    if stock.current_price is not None and stock.quantity is not None
                )
                # Update the portfolio value with stock value and balance
                current_portfolio_value = total_stock_value + portfolio.balance

            # Append the current portfolio value to the list
            portfolio_values.append(current_portfolio_value)

        # Plot line chart
        plt.figure(figsize=(10, 6))
        plt.plot(date_range, portfolio_values, marker='o', linestyle='-')
        plt.title('Portfolio Value Fluctuations')
        plt.xlabel('Date')
        plt.ylabel('Portfolio Value')

        # Set x-axis ticks to show one day at a time
        plt.xticks(rotation=45)
        plt.gca().xaxis.set_major_locator(mdates.DayLocator())
        plt.gca().xaxis.set_major_formatter(mdates.DateFormatter('%Y-%m-%d'))

        # Limit x-axis to one month
        plt.xlim(date_range[0], date_range[0] + timedelta(days=30))

        plt.tight_layout()

        # Save the plot to a byte string
        buf = io.BytesIO()
        plt.savefig(buf, format='png')
        buf.seek(0)
        plt.close()

        # Encode the image data as base64
        encoded_img = base64.b64encode(buf.getvalue()).decode('utf-8')

        return encoded_img

    except Exception as e:
        print("Error generating transaction chart:", e)
        return None