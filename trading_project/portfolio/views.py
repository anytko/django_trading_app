import yfinance as yf
import matplotlib.pyplot as plt
import io
import multiprocessing
from django.shortcuts import render
from .forms import StockForm
import base64

def generate_stock_chart(stock_name, queue):
    try:
        # Fetch historical data for the last year with interval = 1mo
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

        queue.put(encoded_img)
    except Exception as e:
        queue.put(None)

def portfolio(request):
    context = {}
    if request.method == 'POST':
        form = StockForm(request.POST)
        if form.is_valid():
            stock_name = form.cleaned_data['stock_name']

            # Get current stock price
            try:
                stock = yf.Ticker(stock_name)
                current_data = stock.history(period='1d')
                current_price = current_data['Close'][0]
                context['current_price'] = current_price
            except Exception as e:
                context['current_price'] = "Price information not available"

            # Create a queue for communication between processes
            queue = multiprocessing.Queue()

            # Start a separate process to generate the chart
            process = multiprocessing.Process(target=generate_stock_chart, args=(stock_name, queue))
            process.start()
            process.join(timeout=10)  # Wait for 10 seconds for the process to finish

            # Check if the process terminated successfully
            if process.exitcode == 0:
                chart_data = queue.get()
                if chart_data:
                    context['chart'] = chart_data
                else:
                    context['error'] = "Failed to fetch stock data or generate chart."
            else:
                context['error'] = "Failed to generate chart."

        context['form'] = form
    else:
        form = StockForm()
        context['form'] = form
    return render(request, 'portfolio/portfolio.html', context)
