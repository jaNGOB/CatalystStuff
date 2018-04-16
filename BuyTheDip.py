import numpy as np
import pandas as pd
import talib as ta
import matplotlib.pyplot as plt
from catalyst import run_algorithm
from catalyst.exchange.utils.stats_utils import extract_transactions
from catalyst.api import (
    record,
    order,
    order_target_percent,
    symbol,
    get_order
)
from logbook import Logger

log = Logger('BuyTheDip')


def initialize(context):
    context.asset = symbol('btc_usdt')
    context.changes1Length = 2
    context.changes2Length = 2
    context.emaOfChanges1Length = 5
    context.emaOfChanges2Length = 5
    context.bar_count = 10
    context.order_size = 0.1
    context.slippage_allowed = 0.05


def handle_data(context, data):
    prices = data.history(
        context.asset,
        bar_count=context.bar_count,
        fields=['price', 'close'],
        frequency='1d')
    analysis = pd.DataFrame(index=prices.index)

    if prices.size >= 2:
        analysis['changes1History'] = prices.close.pct_change()
        change1 = prices.close.pct_change()

    if len(change1) >= 2:
        analysis['changes2History'] = change1.pct_change()
        change2 = change1.pct_change()

    if len(change2) >= 5:
        analysis['ema1'] = ta.EMA(analysis['changes1History'].as_matrix(), context.emaOfChanges1Length)
        analysis['ema2'] = ta.EMA(analysis['changes2History'].as_matrix(), context.emaOfChanges2Length)
        analysis['ema_test'] = np.where(analysis.ema1 > analysis.ema2, 1, 0)

    context.analysis = analysis
    context.price = data.current(context.asset, 'price')
    makeOrders(context, analysis)


def makeOrders(context, analysis):
    if context.asset in context.portfolio.positions:

        # Current position
        position = context.portfolio.positions[context.asset]
        if (position == 0):
            log.info('Position Zero')
            return

        # Cost Basis
        cost_basis = position.cost_basis

        log.info(
            'Holdings: {amount} @ {cost_basis}'.format(
                amount=position.amount,
                cost_basis=cost_basis
            )
        )

        # Sell when holding and got sell singnal
        if isSell(context, analysis):
            profit = (context.price * position.amount) - (
                cost_basis * position.amount)
            order_target_percent(
                asset=context.asset,
                target=0,
            )
            log.info(
                'Sold {amount} @ {price} Profit: {profit}'.format(
                    amount=position.amount,
                    price=context.price,
                    profit=profit
                )
            )
        else:
            log.info('no buy or sell opportunity found')
    else:
        # Buy when not holding and got buy signal
        if isBuy(context, analysis):
            order(
                asset=context.asset,
                amount=context.order_size
            )
            log.info(
                'Bought {amount} @ {price}'.format(
                    amount=context.order_size,
                    price=context.price
                )
            )


def isBuy(context, analysis):
    if getLast(analysis, 'ema_test') == 1:
        return True
    return False


def isSell(context, analysis):
    if getLast(analysis, 'ema_test') == 0:
        return True
    return False


def analyze(context, perf):
    import matplotlib.pyplot as plt
    perf.loc[:, ['portfolio_value']].plot()
    plt.show()


def getLast(arr, name):
    return arr[name][arr[name].index[-1]]


if __name__ == '__main__':
    live = False
    if live:
        run_algorithm(
            capital_base=1000,
            initialize=initialize,
            handle_data=handle_data,
            analyze=analyze,
            exchange_name='poloniex',
            live=True,
            algo_namespace='hedge',
            base_currency='usdt',
            simulate_orders=True,
        )
    else:
        run_algorithm(
            capital_base=10000,
            data_frequency='daily',
            initialize=initialize,
            handle_data=handle_data,
            analyze=analyze,
            exchange_name='poloniex',
            algo_namespace='hedge',
            base_currency='usdt',
            start=pd.to_datetime('2017-09-01', utc=True),
            end=pd.to_datetime('2018-04-02', utc=True),
        )