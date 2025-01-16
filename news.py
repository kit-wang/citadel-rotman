import requests
import time
API_KEY = {'X-API-key': '33BEFP3G'}
port = "10051"

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

period = 0
news = [{'personal_appl': 50, 'personal_orng': 60, '4_appl': 400, '4_orng': 480}]

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
    
    if tick >= 179 and tick <= 800:
        news['personal_appl'] = get_recent_news()
    elif tick >= 359 and tick <= 360:
        news['personal_orng'] = get_recent_news()
    elif tick >= 539 and tick <= 540:
        news['4_appl'] = get_recent_news()
    elif tick >= 719 and tick <= 720:
        news['4_orng'] = get_recent_news()
    
while True:
    arbitrage(s)

ticker_bid_ask(s, 'APPL')
# print(get_tick(s))
import requests

data = []

while True:
    resp = (s.get(f'http://localhost:{port}/v1/news')).json()
    if resp[0] == 'END':
        print(resp[len(resp) - 1]['body'])
