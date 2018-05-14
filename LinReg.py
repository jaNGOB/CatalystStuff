#!/usr/bin/env python
# -*- coding: utf-8 -*-
import numpy
import pandas
import matplotlib.pyplot as plt
import matplotlib.dates as mdates
# Scikit's LinearRegression model
from sklearn.linear_model import LinearRegression
from scipy import stats
import math
import os
import requests
import ccxt
import json
import time
import random
import uuid
from time import localtime, strftime
import datetime
import calendar
import sys
import operator
import sched
from random import shuffle
import pytz

set(pytz.all_timezones_set)
YEAR_var = 2018

# ALL EPICS
main_epic_ids = [
    'LTC/BTC',
    'ETC/BTC',
    'ETH/BTC',
    'ZEC/BTC',
    'XMR/BTC',
    'DASH/BTC',
    'XRP/BTC',
    'IOTA/BTC',
    'EOS/BTC',
    'OMG/BTC',
    'EOS/BTC']
# ALL EPICS

exchange = ccxt.bitfinex({
    'rateLimit': 3000,
    'enableRateLimit': True,
    'apiKey': 'WCMQ2y5llalyOfGjJJgvsU3oMYlafV85qr5Lb3IIJEX',
    'secret': '5YB2Fn1XwcM76PMe9BcXv7M7jGFC3MsXI5VbXcDlYvF',
    # 'verbose': True,
})

##########################################################################
##########################END OF LOGIN CODE###############################
##########################END OF LOGIN CODE###############################
##########################END OF LOGIN CODE###############################
##########################END OF LOGIN CODE###############################
##########################################################################
# PROGRAMMABLE VALUES
orderType_value = "MARKET"
size_value = "5"
expiry_value = "DFB"
guaranteedStop_value = True
currencyCode_value = "GBP"
forceOpen_value = True
stopDistance_value = "15"  # Make this a global variable for ease!

SL_MULTIPLIER = 4
LOW_SL_WATERMARK = 10
HIGH_SL_WATERMARK = 90
STR_CHECK = ""


def is_between(time, time_range):
    if time_range[1] < time_range[0]:
        return time >= time_range[0] or time <= time_range[1]
    return time_range[0] <= time <= time_range[1]


def midpoint(p1, p2):
    mid_prices = []
    for e in range(len(p1)):
        mid_prices.append((p1[e] + p2[e]) / 2)
    return mid_prices


def distance(a, b):
    if (a == b):
        return 0
    elif (a < 0) and (b < 0) or (a > 0) and (b > 0):
        if (a < b):
            return (abs(abs(a) - abs(b)))
        else:
            return -(abs(abs(a) - abs(b)))
    else:
        return math.copysign((abs(a) + abs(b)), b)


def percentage(part, whole):
    return 100 * float(part) / float(whole)


def humanize_time(secs):
    mins, secs = divmod(secs, 60)
    hours, mins = divmod(mins, 60)
    return '%02d:%02d:%02d' % (hours, mins, secs)


def are_we_going_to_trade(epic_id, TRADE_DIRECTION, limit):

    if TRADE_DIRECTION == "NONE":
        return None

    limitDistance_value = str(limit)

    ##########################################################################
    print(
        "Order will be a " +
        str(TRADE_DIRECTION) +
        " Order, With a limit of: " +
        str(limitDistance_value))
    print(
        "stopDistance_value for " +
        str(epic_id) +
        " will bet set at " +
        str(stopDistance_value))
    ##########################################################################

    # MAKE AN ORDER
    # base_url = REAL_OR_NO_REAL + '/positions/otc'
    # data = {
    #     "direction": TRADE_DIRECTION,
    #     "epic": epic_id,
    #     "limitDistance": limitDistance_value,
    #     "orderType": orderType_value,
    #     "size": size_value,
    #     "expiry": expiry_value,
    #     "guaranteedStop": guaranteedStop_value,
    #     "currencyCode": currencyCode_value,
    #     "forceOpen": forceOpen_value,
    #     "stopDistance": stopDistance_value}
    # r = requests.post(
    #     base_url,
    #     data=json.dumps(data),
    #     headers=authenticated_headers)
    #
    # print("-----------------DEBUG-----------------")
    # print("#################DEBUG#################")
    # print(r.status_code)
    # print(r.reason)
    # print(r.text)
    # print("-----------------DEBUG-----------------")
    # print("#################DEBUG#################")
    #
    # d = json.loads(r.text)
    # deal_ref = d['dealReference']
    # time.sleep(1)
    # # CONFIRM MARKET ORDER
    # base_url = REAL_OR_NO_REAL + '/confirms/' + deal_ref
    # auth_r = requests.get(base_url, headers=authenticated_headers)
    # d = json.loads(auth_r.text)
    # DEAL_ID = d['dealId']
    # print("DEAL ID : " + str(d['dealId']))
    # print(d['dealStatus'])
    # print(d['reason'])
    #
    # if str(d['reason']) != "SUCCESS":
    #     print("!!DEBUG!!...!!some thing occurred ERROR!!")
    #     time.sleep(10)
    #     print("-----------------DEBUG-----------------")
    #     print("#################DEBUG#################")
    #     print("!!DEBUG!! Resuming...")
    #     print("-----------------DEBUG-----------------")
    #     print("#################DEBUG#################")
    # else:
    #     print("-----------------DEBUG-----------------")
    #     print("#################DEBUG#################")
    #     print("!!DEBUG!!...Yay, ORDER OPEN")
    #     time.sleep(10)
    #     print("-----------------DEBUG-----------------")
    #     print("#################DEBUG#################")


def Chandelier_Exit_formula(TRADE_DIR, ATR, Price):

    if TRADE_DIR == "BUY":

        return float(Price) - float(ATR) * 3

    elif TRADE_DIR == "SELL":

        return float(Price) + float(ATR) * 3


def calculate_stop_loss(d):

    price_ranges = []
    closing_prices = []
    first_time_round_loop = True
    TR_prices = []

    for i in range(len(d)):
        if first_time_round_loop:
            # First time round loop cannot get previous
            closePrice = d[i][4]
            closing_prices.append(closePrice)
            high_price = d[i][2]
            low_price = d[i][3]
            price_range = float(high_price - closePrice)
            price_ranges.append(price_range)
            first_time_round_loop = False
        else:
            prev_close = closing_prices[-1]
            ###############################
            closePrice = d[i][4]
            closing_prices.append(closePrice)
            high_price = d[i][2]
            low_price = d[i][3]
            price_range = float(high_price - closePrice)
            price_ranges.append(price_range)
            TR = max(high_price - low_price,
                     abs(high_price - prev_close),
                     abs(low_price - prev_close))
            TR_prices.append(TR)

    return str(int(float(max(TR_prices))))


if __name__ == '__main__':

    while True:

        try:
            deposit = exchange.fetch_used_balance()
            balance = exchange.fetch_total_balance()

            percent_used = percentage(deposit['BTC'], balance['BTC'])

            print("-----------------DEBUG-----------------")
            print("#################DEBUG#################")
            print(
                "!!DEBUG!!...Percent of account used ..." +
                str(percent_used))
            print("-----------------DEBUG-----------------")
            print("#################DEBUG#################")

            if float(percent_used) > 70:
                print("!!DEBUG!!...Don't trade, Too much margin used up already")
                time.sleep(60)
                continue
            else:
                print("!!DEBUG!!...OK to trade, Account balance OK!!")

            tradeable_epic_ids = main_epic_ids
            shuffle(tradeable_epic_ids)

        except Exception as e:
            print(e)
            print("!!DEBUG!!...No Suitable Epics...Yet!!, Try again!!")
            continue

        for epic_id in tradeable_epic_ids:

            d = exchange.fetch_ohlcv(epic_id, '15m')

            high_prices = [el[2] for el in d]
            low_prices = [el[3] for el in d]
            mid_prices = midpoint(high_prices, low_prices)
            close_prices = [el[4] for el in d]
            ATR = calculate_stop_loss(d)

            close_prices = numpy.asarray(close_prices)
            low_prices = numpy.asarray(low_prices)
            high_prices = numpy.asarray(high_prices)
            mid_prices = numpy.asarray(mid_prices)

            xi = numpy.arange(0, len(low_prices))

            close_prices_slope, close_prices_intercept, close_prices_r_value, close_prices_p_value, close_prices_std_err = stats.linregress(
                xi, close_prices)
            low_prices_slope, low_prices_intercept, low_prices_r_value, low_prices_p_value, low_prices_std_err = stats.linregress(
                xi, low_prices)
            high_prices_slope, high_prices_intercept, high_prices_r_value, high_prices_p_value, high_prices_std_err = stats.linregress(
                xi, high_prices)
            mid_prices_slope, mid_prices_intercept, mid_prices_r_value, mid_prices_p_value, mid_prices_std_err = stats.linregress(
                xi, mid_prices)

            d = exchange.fetch_ticker(epic_id)

            current_bid = d['bid']

            if distance(current_bid, mid_prices_intercept) > 1:
                TRADE_DIRECTION = "SELL"
                pip_limit = int(abs(float(max(high_prices)) -
                                    float(current_bid)) / SL_MULTIPLIER)
                print("-----------------DEBUG-----------------")
                print("#################DEBUG#################")
                print("!!DEBUG!!...BUY!!")
                print(str(epic_id))
                print(
                    "!!DEBUG!!...Take Profit@...." +
                    str(pip_limit) +
                    " pips")
                print("-----------------DEBUG-----------------")
                print("#################DEBUG#################")
                ce_stop = Chandelier_Exit_formula(
                    TRADE_DIRECTION, ATR, min(low_prices))
                tmp_stop = int(abs(float(current_bid) - (ce_stop)))
            elif distance(current_bid, mid_prices_intercept) < -1:
                TRADE_DIRECTION = "BUY"
                pip_limit = int(abs(float(min(low_prices)) -
                                    float(current_bid)) / SL_MULTIPLIER)
                print("-----------------DEBUG-----------------")
                print("#################DEBUG#################")
                print("!!DEBUG!!...SELL!!")
                print(str(epic_id))
                print(
                    "!!DEBUG!!...Take Profit@...." +
                    str(pip_limit) +
                    " pips")
                print("-----------------DEBUG-----------------")
                print("#################DEBUG#################")
                ce_stop = Chandelier_Exit_formula(
                    TRADE_DIRECTION, ATR, max(high_prices))
                tmp_stop = int(abs(float(current_bid) - (ce_stop)))

            else:
                pip_limit = 9999999
                tmp_stop = "999999"
                TRADE_DIRECTION = "NONE"
                print("!!DEBUG!!...Within trading range...Leave!!")

            if int(pip_limit) <= 1:
                print("!!DEBUG!!...No Trade!!, Pip Limit Under 1")
                TRADE_DIRECTION = "NONE"

            stopDistance_value = str(tmp_stop)

            if int(stopDistance_value) <= LOW_SL_WATERMARK or int(
                    stopDistance_value) >= HIGH_SL_WATERMARK:
                TRADE_DIRECTION = "NONE"

            try:
                are_we_going_to_trade(epic_id, TRADE_DIRECTION, pip_limit)
            except Exception as e:
                print(e)
                print("Something fucked up!!, Try again!!")
                continue