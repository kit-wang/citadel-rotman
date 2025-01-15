def arbitrage(session):
    while tick < 900:
        aapl_bid, aapl_ask = ticker_bid_ask(session, 'APPL')
        orng_bid, orng_ask = ticker_bid_ask(session, 'ORNG')
        fruit_bid, fruit_ask = ticker_bid_ask(session, 'FRUIT')

        # first arb approach 
        if aapl_bid + orng_bid > fruit_ask:
            # sell the individual fruits, buy the fruit ETF
            s.post('http://localhost:10044/v1/orders', params={'ticker': 'APPL', 'type': 'MARKET', 'quantity': 10, 'action': 'SELL'})
            s.post('http://localhost:10044/v1/orders', params={'ticker': 'ORNG', 'type': 'MARKET', 'quantity': 10, 'action': 'SELL'})

            s.post('http://localhost:10044/v1/orders', params={'ticker': 'FRUIT', 'type': 'MARKET', 'quantity': 1, 'action': 'BUY'})
        
            # second arb approach
        if aapl_ask + orng_ask < fruit_bid:
            # buy the individual fruits, sell the fruit ETF
            session.post('http://localhost:10044/v1/orders', params={'ticker': 'APPL', 'type': 'MARKET', 'quantity': 10, 'action': 'BUY'})
            session.post('http://localhost:10044/v1/orders', params={'ticker': 'ORNG', 'type': 'MARKET', 'quantity': 10, 'action': 'BUY'})

            session.post('http://localhost:10044/v1/orders', params={'ticker': 'FRUIT', 'type': 'MARKET', 'quantity': 1, 'action': 'SELL'})
       
API_KEY = {'X-API-key':'8ZAUTV7Y'} 
s = requests.Session()
s.headers.update(API_KEY)

while True:
    arbitrage(s)


def get_tick(session):
    resp = session.get('http://localhost:10044/v1/case')
    if resp.ok:
        case = resp.json()
        print(case)
        return case['tick']
    raise ApiException('Authorization error. Please check API key.')

def ticker_bid_ask(session, ticker):
    payload = {'ticker': ticker}
    resp = session.get('http://localhost:10044/v1/securities/book', params=payload)
    if resp.ok:
        book = resp.json()
        bid_ctr = 0
        ask_ctr = 0
        if len(book['bids']) > 0 and len(book['asks']) > 0:
            return book['bids'][0]['price'], book['asks'][0]['price']
        elif len(book['bids']) > 0 and not len(book['asks']) > 0:
            return book['bids'][0]['price']
        elif len(book['asks']) > 0 and not len(book['bids']) > 0:
            return book['asks'][0]['price']
        else:
            return (0, 0)
        
    raise ApiException('Authorization error. Please check API key.')

ticker_bid_ask(s, 'APPL')
# print(get_tick(s))
import requests

data = []
API_KEY = {'X-API-key':'8ZAUTV7Y'} 
        s = requests.Session()
        s.headers.update(API_KEY)
while True:
    resp = (s.get('http://localhost:10044/v1/news')).json()
    if resp[0] == 'END':
        print(resp[len(resp) - 1]['body'])
    
 
