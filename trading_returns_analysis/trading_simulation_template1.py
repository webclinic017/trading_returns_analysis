# -*- coding: utf-8 -*-
"""
Created on Sun Feb  7 10:36:05 2021

@author: recon
"""

#%% Set Variables

_str_currency = 'EURUSD'
_str_timeframe = 'D'
_int_hours_offset = 3
_float_takeprofit_rate = 0.0100
_float_stoploss_rate = 0.0030

#%% Import modules


from numba.core.errors import HighlightColorScheme
import pandas as pd
import numpy as np
from numba import njit
import warnings
from sqlconnection import CONNECT_TO_SQL_SERVER as _module_sc
from asset_price_etl import etl_fx_histadata_001 as etl
import __init__ as tradingformula
import statistics
from scipy import stats
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots



#%% Remove warnings
warnings.filterwarnings('ignore')


#%% ETL load fx eurusd historical price

df_fx_raw_data = etl._function_extract(_str_valuedate_start = '1/1/2010',
                                        _str_valuedate_end = '12/31/2010')


#%% Sort datetimie into ascending order and set datetime as the index

df_fx_raw_data = df_fx_raw_data.sort_values('DateTime', ascending = True)

df_fx_raw_data = df_fx_raw_data.set_index('DateTime')

#%% Resample price into desire timeframe

df_fx_raw_data = df_fx_raw_data.resample(_str_timeframe).agg({'Open':'first',
                                                                'High':'max',
                                                                'Low':'min',
                                                                'Close':'last'
                                                                })


#%% Create a copy of the raw data 

df_fx = df_fx_raw_data.copy()

#%% Calculate the daily percentage from high to low and take the absolute value
df_fx['VolatilityRank'] = tradingformula.GENERATE_HIGH_TO_LOW_VOLATILITY_SCORE(_df_data = df_fx,
                                                                                _variant_number_of_period = '2D',
                                                                                _str_expanding_or_rolling_historical_volatility = 'rolling',
                                                                                _int_rolling_number_of_days = 30,
                                                                                _str_column_high = 'High',
                                                                                _str_column_low = 'Low')

#%% Create a plotly plot that shows the fx price together with the volatility

_obj_fig = make_subplots(rows = 2, cols=1, shared_xaxes=True)


_obj_fig.add_trace(go.Candlestick(
                                    x = df_fx.index,
                                    open = df_fx.Open,
                                    high = df_fx.High,
                                    low = df_fx.Low,
                                    close = df_fx.Close
                                    ),
                                row = 1,
                                col=1
                                )

_obj_fig.add_trace(go.Scatter(x = df_fx.index,y = df_fx.VolatilityRank),
                    row = 2,
                    col = 1)

_obj_fig.update_layout(xaxis_rangeslider_visible=False)

pio.renderers.default = 'browser'

pio.show(_obj_fig)

#%% Create a random sample of Long Short Hold

df_fx['TradeDirection'] = tradingformula.GENERATE_RANDOM_TRADE_DIRECTION(_df_data = df_fx)


#%% This is an example of volatility filter on when to trade and when not to trade at a specific volatility rank

df_fx['TradeDirection'] = np.where((df_fx['VolatilityRank'] >= 20) & (df_fx['VolatilityRank'] <= 80), 
                                   df_fx['TradeDirection'],
                                   'Hold')



#%% Create a Long take profit of 2%

df_fx['TakeProfitPrice'] = tradingformula.GENERATE_FIX_TAKE_PROFIT_PRICE(_df_data = df_fx,
                                                                         _float_takeprofit_rate = _float_takeprofit_rate)

#%% Add column for Stoploss Price Relative to the open price

df_fx = tradingformula.GENERATE_FIX_AND_SEPARATE_LONG_SHORT_STOPLOSS(_df_data = df_fx,
                                                                     _str_column_Open_price = 'Open',
                                                                     _float_stoploss_rate = _float_stoploss_rate)

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



    
    
    
    
    
    
    
    
    