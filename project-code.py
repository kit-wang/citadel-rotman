import requests
API_KEY = {'X-API-key': '33BEFP3G'}
port = "10051"
s = requests.Session()
s.headers.update(API_KEY)
resp = s.get(f'http://localhost:{port}/v1/case')

def send_order(sym, side, price, size):
    resp = s.post('http://localhost:10027/v1/orders',params = {'ticker': sym, 'type': 'LIMIT', 'action': side,
                                                                'quantity': size, 'price': price})
    if resp.ok:
        print('SENT:', side, sym, size, '@', price)
        print('Order ID:', resp.json()['order_id'])
    else:
        print('failed to send order', side, sym, size, '@', price, ':', resp.text)
#send_order('APPL', 'BUY', 50.00, 10)
def get_tick(session):
    resp = session.get('http://localhost:10027/v1/case')
    if resp.ok:
        case = resp.json()
        return case['tick']
    raise ApiException('Authorization error. Please check API key.')

"""def ticker_bid_ask(session, ticker):
    payload = {'ticker': ticker}
    resp = session.get('http://localhost:10027/v1/securities/book', params = payload)
    if resp.ok:
        book = resp.json()
        return book['bids'][0]['price'], book['asks'][0]['price']
    raise ApiException('Authorization error. Please check API key.')
"""
def ticker_bid_ask(session, ticker):
    payload = {'ticker': ticker}
    resp = session.get('http://localhost:10027/v1/securities', params = payload)
    if resp.ok:
        book = resp.json()
        print(book)
        return book[0]['bid'], book[0]['ask']


n = 1
while n < 0:
    appleba = ticker_bid_ask(s, 'APPL')
    if appleba[1] - appleba[0] >= 2:
        send_order('APPL', 'BUY', appleba[0] + 1, 10)
        send_order('APPL', 'SELL', appleba[1] - 1, 10)
    n += 1
   # send_order('APPL', 'BUY', 50.00, 10)
   # send_order('APPL', 'SELL', 75.00, 10)
while False:
    send_order('APPL', 'BUY', 50.00, 10)
    send_order('APPL', 'SELL', 75.00, 10)

def get_market_fair(session, ticker):
    payload = {'ticker': ticker}
    resp = session.get('http://localhost:10044/v1/securities', params = payload)
    if resp.ok:
        case = resp.json()
        return case[0]['last']
    raise ApiException('Authorization error. Please check API key.')


# {'personal_appl': 50, 'personal_orng': 60, '4_appl': 400, '4_orng': 480}
news = []
fairs = {'APPL': (400, 81.65), 'ORNG': (480, 42.4264), 'FRUIT': (880, 92.0145), "FPUT": (80, 92.01)}

def get_recent_news():
    news = s.get(f'http://localhost:{port}/v1/news').json()
    if news == []: return -0.1
    news_id = news[0]['news_id']
    if news_id == 3 or news_id == 4: # four random farms
        headline = news[0]['headline'].split()
        num = int(headline[5])
        return num
    else: # personal harvest
    #elif news_id == 1 or news_id == 2:
        headline = news[0]['headline'].split()
        num = int(headline[-1][:-1])
    return num

def find_fair(tick):
  # no information
  if tick < 179:
    return fairs
  # personal apple out
  if tick >= 179:
    fairs['APPL'][0] = fairs['APPL'][0] - 50 + news[0]
    fairs['APPL'][1] = 76.376
    fairs['FRUIT'][1] = 87.369
  # personal orange out
  if tick >= 359:
    fairs['ORNG'][0] = fairs['ORNG'][0] - 60 + news[1]
    fairs['ORNG'][1] = 39.686
    fairs['FRUIT'][1] = 86.072
  # 4 apple out
  if tick >= 539:
    fairs['APPL'][0] = fairs['APPL'][0] - 200 + news[2]
    fairs['APPL'][1] = 57.735
    fairs['FRUIT'][0] = fairs['APPL'][0] + fairs['ORNG'][0]
    fairs['FRUIT'][1] = 70.0595
  # 4 orange out
  if tick >= 719:
    fairs['ORNG'][0] = fairs['ORNG'][0] - 240 + news[3]
    fairs['ORNG'][1] = 30
    fairs['FRUIT'][0] = fairs['APPL'][0] + fairs['ORNG'][0]
    fairs['FRUIT'][1] = 65.064

  return fairs

def update_news(tick):
    if tick >= 179 and tick <= 180:
        if len(news) == 0:
            news.append(get_recent_news())
    elif tick >= 359 and tick <= 360:
        if len(news) == 1:
            news.append(get_recent_news())
    elif tick >= 539 and tick <= 540:
        if len(news) == 2:
            news.append(get_recent_news())
    elif tick >= 719 and tick <= 720:
        if len(news) == 3:
            news.append(get_recent_news())
    fairs = find_fair(tick)

def arbitrage(session):
    tick = get_tick(s)
    if tick < 900:
        aapl_bid, aapl_ask = ticker_bid_ask(session, 'APPL')
        orng_bid, orng_ask = ticker_bid_ask(session, 'ORNG')
        fruit_bid, fruit_ask = ticker_bid_ask(session, 'FRUIT')
        
        # first arb approach 
        if aapl_bid + orng_bid > fruit_ask:
            # sell the individual fruits, buy the fruit ETF
            s.post(f'http://localhost:{port}/v1/orders', params={'ticker': 'APPL', 'type': 'MARKET', 'quantity': 10, 'action': 'SELL'})
            s.post(f'http://localhost:{port}/v1/orders', params={'ticker': 'ORNG', 'type': 'MARKET', 'quantity': 10, 'action': 'SELL'})
            
            s.post(f'http://localhost:{port}/v1/orders', params={'ticker': 'FRUIT', 'type': 'MARKET', 'quantity': 1, 'action': 'BUY'})
        
        # second arb approach
        if aapl_ask + orng_ask < fruit_bid:
            # buy the individual fruits, sell the fruit ETF
            session.post(f'http://localhost:{port}/v1/orders', params={'ticker': 'APPL', 'type': 'MARKET', 'quantity': 10, 'action': 'BUY'})
            session.post(f'http://localhost:{port}/v1/orders', params={'ticker': 'ORNG', 'type': 'MARKET', 'quantity': 10, 'action': 'BUY'})
            
            session.post(f'http://localhost:{port}/v1/orders', params={'ticker': 'FRUIT', 'type': 'MARKET', 'quantity': 1, 'action': 'SELL'})
    
        update_news()
        
def mm(session, ticker):
    last = get_market_fair(session, ticker)
    curr_bid, curr_ask = ticker_bid_ask(session, ticker)
    our_fair = fairs[ticker[0]]
    range = [fairs[ticker][0] - fairs[ticker][1], fairs[ticker][0] + fairs[ticker][1]]
    if our_fair > curr_bid and our_fair > last + fairs[ticker][1]:
        if curr_ask == last:
            if our_fair > last + fairs[ticker][1]:
                market_limit_order(ticker, 'BUY', 100, last + 0.01)
    elif our_fair < curr_bid and our_fair < last - fairs[ticker][1]:
        if curr_bid == last:
            market_limit_order(ticker, 'SELL', 100, last - 0.01)
    else:
        send_order(ticker, 'BUY', 25, curr_bid + 0.01)
        send_order(ticker, 'SELL', 25, curr_ask - 0.01)
curtick = -1
tick = 0
fput = False
while True:
    tick = get_tick(s)
    if tick != curtick:
        if tick % 2 == 0:
            arbitrage(s)
        for i in range(6):
            mm(s, 'APPL')
            mm(s, 'ORNG')
            mm(s, 'FRUIT')
        curtick = tick

# ticker_bid_ask(s, 'APPL')
# # print(get_tick(s))
# import requests

# data = []

# while True:
#     resp = (s.get(f'http://localhost:{port}/v1/news')).json()
#     if resp[0] == 'END':
#         print(resp[len(resp) - 1]['body'])