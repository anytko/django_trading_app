from celery import shared_task
import yfinance as yf
import matplotlib.pyplot as plt
import io
import base64
from decimal import Decimal

@shared_task
def generate_stock_chart(stock_name):
    try:
        # Fetch historical data for the last year with interval = 1mo
        stock = yf.Ticker(stock_name)
        hist = stock.history(period='1y', interval='1mo')

        # Plotting
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