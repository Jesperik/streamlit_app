import plotly.express as px
import pandas as pd
import numpy as np



class MyClass:
    def __init__(self):
        self.stocks = {'AAPL': 42, 'GOOGL': 43, 'NVDA': 44, 'AMZN': 45, 'TSLA': 46}
        self.ticker_to_name = {key: name for key, name in zip(self.stocks.keys(), 
           ['Apple', 'Google', 'Nvidia', 'Amazon', 'Tesla'])}
        self.start_date = None
        self.end_date = None
        self.stock_data = None
        self.stock_stats = {'max': None, 'min': None, 'avg': None, 'spread': None}
        self.ma = None

    def set_states(self, sd, ed, ma):
        self.start_date = pd.to_datetime(sd)
        self.end_date = pd.to_datetime(ed)
        self.ma = ma

    def generate_data(self, stock):
        date_range = pd.date_range(start=self.start_date, end=self.end_date)
        data_length = len(date_range)

        # Generate synthetic stock data
        np.random.seed(self.stocks[stock])  # For reproducible results
        prices = np.cumsum(np.random.randn(data_length)) + 100  # Random walk
        self.stock_data = pd.DataFrame(data={'Date': date_range, 'Close': prices})
        self.stock_data['MA'] = self.stock_data['Close'].rolling(window=self.ma).mean()

        date_mask = self.stock_data['Date'].between(self.start_date, self.end_date, inclusive='both')
        self.stock_stats['max'] = round(self.stock_data[date_mask]['Close'].max(), 1)
        self.stock_stats['min'] = round(self.stock_data[date_mask]['Close'].min(), 1)
        self.stock_stats['avg'] = round(self.stock_data[date_mask]['Close'].mean(), 1)
        self.stock_stats['spread'] = round(self.stock_stats['max'] - self.stock_stats['min'], 1)

    def plot_data(self, stock):
        melted_data = self.stock_data.melt(id_vars=['Date'], 
                                           value_vars=['Close', 'MA'], 
                                           var_name='Type', 
                                           value_name='Value')

        # Plotting the closing price and moving average
        fig = px.line(melted_data, 
                      x='Date',
                      y='Value',
                      color='Type',
                      color_discrete_map={'Close': 'deepskyblue', 'MA': 'crimson'},
                      title=f'{self.ticker_to_name[stock]} Closing Prices and {self.ma}-Day Moving Average')

        # Update layout
        fig.update_layout(xaxis_title='Date', yaxis_title='Price (USD)', template='plotly_dark')

        return fig
