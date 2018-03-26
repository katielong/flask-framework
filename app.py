from flask import Flask, render_template, request, redirect
import pandas as pd
import requests
import re
import os
from bokeh.plotting import figure, output_file, show
from bokeh.models import ColumnDataSource
from bokeh.embed import components
from bokeh.core.properties import value
from bokeh.models.formatters import DatetimeTickFormatter

app = Flask(__name__)

#prepare dropdown data
tickersData = pd.read_csv('static/WIKI-datasets-codes.csv')
tickers = tickersData.Name
dropdown = []
for ticker in tickers:
  ticker = ticker.replace('WIKI/', '')
  dropdown.append(ticker)
dropdown = sorted(dropdown)
def input(ticker, prices):
  # setup
  baseURL = 'https://www.quandl.com/api/v3/datatables/WIKI/PRICES?'
  token = os.environ['TOKEN'] #Heroku
  ticker = ticker
  URL = baseURL + '&ticker=' + ticker + '&api_key=' + token
  palette = dict()
  palette['open'] = 'dodgerblue'
  palette['adj_open'] = 'deepskyblue'
  palette['close'] = 'red'
  palette['adj_close'] = 'salmon'
  #retrieve data
  response = requests.get(URL)
  json = response.json()
  data = json['datatable']
  columns = data['columns']
  names = []
  for column in columns:
      names.append(column['name'])
  df = pd.DataFrame(data['data'], columns=names)
  df.date = pd.to_datetime(df.date)
  ds = ColumnDataSource(df)
  #plot figure
  p = figure(x_axis_type="datetime", 
              title='Data Source: Quandl WIKI Prices', 
              plot_width=900, 
              plot_height=600)
  for i, price in enumerate(prices):
    p.line(source = ds, x = 'date', y=price, color=palette[price], legend= value(str(ticker + ': ' + price))) 
  p.legend.location='top_left'
  p.xaxis.axis_label = 'date'
  p.xaxis.formatter = DatetimeTickFormatter(months='%m/%Y')
  p.yaxis.axis_label = 'price ($)'
  #save javascript, html
  script, div = components(p)
  return {'script':script, 'div':div}

@app.route('/', methods=['GET', 'POST'])
def index():
    return render_template('index.html', data = dropdown)

@app.route('/graph',methods=['GET', 'POST'])
def graph():
  ticker = request.form['ticker']
  openP = request.form.get('open')
  adj_openP = request.form.get('adj_open')
  closeP = request.form.get('close')
  adj_closeP = request.form.get('adj_close')
  price = [openP, adj_openP, closeP, adj_closeP]
  price = filter(lambda a: a!=None, price)
  res = input(ticker, price)
  return render_template('graph.html', script = res['script'], div = res['div'])

@app.route('/about')
def about():
  return render_template('about.html')

if __name__ == '__main__':
  app.run(port=8000)