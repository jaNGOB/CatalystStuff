import time
import ccxt

exchange = ccxt.bitmex({
    'enableRateLimit': True,
    'apiKey': '',
    'secret': '',
})
if 'test' in exchange.urls:
    exchange.urls['api'] = exchange.urls['test']

ORDER_SIZE = 30
First_Order = 10
upper = 100
lower = 200
multiplyBy = 2
distance = 100
power = 0
pair = 'BTC/USD'

in_long = False
in_short = False
cost_basis = 1


def weAreLong(price):
    global in_long
    global in_short
    global power

    TP = cost_basis + upper
    SL = cost_basis - lower
    Crit = cost_basis - distance
    sellamount = (10 * (2 ** power))

    if price < Crit:
        amount = (ORDER_SIZE*(multiplyBy**power))
        createorder('sell', amount)
        in_long = False
        in_short = True
        print('Kill Long! GO SHORT! Sold {amount} @ {price}'.format(amount=amount, price=price))
        power += 1

    elif price > TP:
        in_long = False
        in_short = False
        createorder('sell', sellamount)
        power = 0
        print('We made it! Sold @ {price}'.format(price=price))

    elif price < SL:
        in_long = False
        in_short = False
        createorder('sell', sellamount)
        power = 0
        print('We lost it all! Sold @ {price}'.format(price=price))

    else:
        print('-------------------------------')
        print(whattimeisit())
        print('In Long with {} contracts:'.format(sellamount))
        print(' Bought       at {}'.format(cost_basis))
        print(' Now          at {}'.format(price))
        print(' Stop Loss    at {}'.format(SL))
        print(' Target Price at {}'.format(TP))
        print(' Change Pos.  at {}'.format(Crit))
        pass


def weAreShort(price):
    global in_long
    global in_short
    global power

    TP = cost_basis - lower
    SL = cost_basis + upper
    Crit = cost_basis
    sellamount = (10 * (2 ** power))

    if price > Crit:
        amount = (ORDER_SIZE*(multiplyBy**power))
        createorder('buy', amount)
        in_long = True
        in_short = False
        print('Kill Short! GO LONG! Bought {amount} @ {price}'.format(amount=amount, price=price))
        power += 1

    elif price < TP:
        in_long = False
        in_short = False
        createorder('buy', sellamount)
        power = 0
        print('We made it! Sold @ {price}'.format(price=price))

    elif price > SL:
        in_long = False
        in_short = False
        createorder('buy', sellamount)
        power = 0
        print('We lost it all! Sold @ {price}'.format(price=price))

    else:
        print('-------------------------------')
        print(whattimeisit())
        print('In Short with {} contracts:'.format(sellamount))
        print(' Sold         at {}'.format(cost_basis))
        print(' Now          at {}'.format(price))
        print(' Stop Loss    at {}'.format(SL))
        print(' Target Price at {}'.format(TP))
        print(' Change Pos.  at {}'.format(Crit))
        pass


def getcurrentprice():
    time.sleep(3)
    try:
        d = exchange.fetch_ticker(pair)
        price = d['bid']
        return price

    except (ccxt.ExchangeError, ccxt.AuthenticationError, ccxt.ExchangeNotAvailable, ccxt.RequestTimeout) as error:
        print('Got an error', type(error).__name__, error.args, ', retrying in 30 seconds...')
        time.sleep(30)
        getcurrentprice()


def createorder(side, amount):
    try:
        exchange.create_order(pair, 'market', side, amount)
    except (ccxt.ExchangeError, ccxt.AuthenticationError, ccxt.ExchangeNotAvailable, ccxt.RequestTimeout) as error:
        print('Got an error', type(error).__name__, error.args, ', retrying in 30 seconds...')
        time.sleep(30)
        createorder(side, amount)


def whattimeisit():
    try:
        now = exchange.seconds()
        human = time.ctime(now)
        return human
    except (ccxt.ExchangeError, ccxt.AuthenticationError, ccxt.ExchangeNotAvailable, ccxt.RequestTimeout) as error:
        print('Got an error', type(error).__name__, error.args, ', retrying in 30 seconds...')
        time.sleep(30)
        whattimeisit()


if __name__ == '__main__':

    print('Starting Sure Fire Hedge Strategy')

    while True:
        price = getcurrentprice()

        if in_long:
            weAreLong(price)

        elif in_short:
            weAreShort(price)

        else:
            createorder('buy', First_Order)
            in_long = True
            in_short = False
            cost_basis = price
            power = 0
            print('Bought {amount} @ {price}'.format(amount=First_Order, price=price))
