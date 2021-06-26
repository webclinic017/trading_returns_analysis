# -*- coding: utf-8 -*-
"""
Created on Sun Feb  7 10:36:05 2021

@author: recon
"""

#%% Set Variables

_currency = 'EURUSD'
_timeframe = 'D'
_hours_offset = 3
_from_date = '20001201'
_to_date = '20101231'
_takeprofit_rate = 0.0100
_stoploss_rate = 0.0030

#%% Import modules

import pandas as pd
import fx_histadata as fx
import numpy as np
from numba import njit

import warnings
from sqlconnect import read_sql_data
import module_trading_formula as tradingformula
import statistics
from scipy import stats


#%%
warnings.filterwarnings('ignore')

#%%
_sqlquery = open('sql_get_fx_data.txt','r').read().format(_currency = _currency,
                                                      _hours_offset = _hours_offset,
                                                      _from_date = _from_date,
                                                      _to_date = _to_date,
                                                      _time_frame = _timeframe)

df_fx_raw_data = read_sql_data(server = 'DESKTOP-SEQC76J\SQLEXPRESS',
                                database = 'fxalgo',
                                _sqlquery = _sqlquery
                                )

df_fx_raw_data = df_fx_raw_data.sort_values('Date', ascending = True)

df_fx_raw_data = df_fx_raw_data.set_index('Date')
                
#%% Create a copy of the raw data 

df_fx = df_fx_raw_data.copy()

#%%

#Calculate the daily percentage from high to low and take the absolute value
df_fx = tradingformula.GENERATE_HIGH_TO_LOW_VOLATILITY_SCORE(data = df_fx,

                                          _period_number = '30D',
                                          _column_high = 'High',
                                          _column_low = 'Low')

#%% Create a random sample of Long Short Hold

df_fx = tradingformula.GENERATE_RANDOM_TRADE_DIRECTION(data = df_fx)


#%%

df_fx['TradeDirection'] = np.where(df_fx['VolatilityRank'] >= 50, 
                                   df_fx['TradeDirection'],
                                   'Hold')



#%% Create a Long take profit of 2%

df_fx = tradingformula.GENERATE_FIX_TAKE_PROFIT_PRICE(data = df_fx,
                                                      _takeprofit_rate = _takeprofit_rate)

#%% Add column for Stoploss Price Relative to the open price

df_fx = tradingformula.GENERATE_FIX_AND_SEPARATE_LONG_SHORT_STOPLOSS(data = df_fx,
                                                                     _column_Open_price = 'Open',
                                                                     _stoploss_rate = _stoploss_rate)

#%% Create a new column that determines if the previous i
#period created a higher high or lower high or higher low or lower low

df_fx = tradingformula.GENERATE_HIGHER_HIGH_LOWER_LOW_COLUMN(data = df_fx,
                                                             _column_high_price = 'High',
                                                             _column_row_price = 'Low')
            

#%%

df_fx = tradingformula.GET_EXIT_PRICE_BASED_ON_TRAILING_STOP(data = df_fx,
                                                            _column_high_price = 'High',
                                                            _column_low_price = 'Low',
                                                            _column_TradeDirection = 'TradeDirection',
                                                            _column_LongStopLossRelativetoOpenPrice = 'LongStopLossRelativetoOpenPrice',
                                                            _column_ShortStopLossRelativetoOpenPrice = 'ShortStopLossRelativetoOpenPrice')
    
#%% Identify Static Take Profit Hit Date

df_fx = tradingformula.GET_TAKE_PROFIT_AND_DATE(data = df_fx,
                                                 _column_high_price = 'High',
                                                 _column_low_price = 'Low',
                                                 _column_TakeProfitPrice = 'TakeProfitPrice',
                                                 _column_TradeDirection = 'TradeDirection')

#%% Generate an exit price based on which was triggered first, is it the stoploss or the take profit

df_fx = tradingformula.GENERATE_FINAL_EXIT_PRICE(data = df_fx,
                                                 _column_TakeProfitHitDate = 'TakeProfitHitDate',
                                                 _column_TakeProfitPrice = 'TakeProfitPrice',
                                                 _column_TrailingExitStopLossDate = 'TrailingExitStopLossDate',
                                                 _column_TrailingStoplossExitPrice = 'TrailingStoplossExitPrice')

#%% Returns analysis gives you the cumulative return so as the rolling return

df_fx = tradingformula.RETURNS_ANALYSIS(data = df_fx,
                                          _column_trade_entry_price ='Open',
                                          _column_trade_direction = 'TradeDirection',
                                          _column_trade_exit_price = 'ExitPrice')
    


#%% Create new column that will determine the cumulative win rate and the rolling win rate


df_fx = tradingformula.CUMULATIVE_AND_ROLLING_WIN_RATE(df_fx, 'SingleTradePercentageChange')


#%% Create new column that will determine the cumulative risk and return and the rolling win rate


df_fx = tradingformula.CUMULATIVE_AND_ROLLING_RISK_TO_RETURN_RATIO(df_fx, 'SingleTradePercentageChange')


#%% Creates a new column that gives you the rate at which you need to increase or decrease your postion size

df_fx = tradingformula.CUMULATIVE_KELLY_CRITERION(df_fx, 'SingleTradePercentageChange')




#%% Generate a csv output

df_fx.to_csv('OutputManualSenseCheck.csv')



#%%
import plotly.io as pio
pio.renderers.default = 'browser'
from plotly.subplots import make_subplots
import plotly.graph_objects as go
fig = make_subplots(rows=4, cols=1)

fig.append_trace(go.Scatter(
    x=df_fx.index,
    y=df_fx['Open'],
), row=1, col=1)

fig.append_trace(go.Scatter(
    x=df_fx.index,
    y=df_fx['VolatilityRank'],
), row=2, col=1)

fig.append_trace(go.Scatter(
    x=df_fx.index,
    y=df_fx['Volatility']
), row=3, col=1)

fig.append_trace(go.Scatter(
    x=df_fx.index,
    y=df_fx['CumulativeReturn']
), row=4, col=1)

fig.update_layout(height=1000, width=2000, title_text="Stacked Subplots")
pio.show(fig)
    
    
    
    
    
    
    
    
    