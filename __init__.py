# -*- coding: utf-8 -*-
"""
Objective:
    
    The module is a collection of python formula that can simulate trades
    This includes the following:
        1. Returns computation
        2. Stoploss and Take Profit Price
        3. Generate simulated trade direction
"""
#%%

import numpy as np
import pandas as pd
import random
import statistics
from scipy import stats

#%%
def KELLY_FORMULA(x: (np.ndarray) = None):
    
    """
    Based on your past trading performance, the Kelly Criterion tells you the position sizes you should be taking on your next trade.
    
    Kelly Formula = W - ( (1-W) / R )
    Where:
        W =  WinRate
        R = RiskRewardRatio
    
    Return
    ------
    np.ndarray
    """
    
    _win_rate = np.sum(x>0) / np.sum(~np.isnan(x)) 
    _risk_return_ratio = np.sum(x[x>0]) / abs(np.sum(x[x<0]))
    
    W =  _win_rate
    R = _risk_return_ratio
    
    _kelly_criterion = W - ( (1-W) / R )
    
    return _kelly_criterion 

#%% Create new column that will determine the kelly criterion

def CUMULATIVE_KELLY_CRITERION(data = None,
                                    _column_SingleTradePercentageChange: (str) = None):
    '''
    Creates multiple columns that shows the cumulative risk and return (30,60,90,180, 360 Days).
    This will be based on the percentage change per trade.
    
    Parameter
    --------
    data : Pandas Dataframe
    _column_SingleTradePercentageChange : String - Give the column name of the dataframe at which the return per trade can be found.
    
    
    Return
    --------
    Pandas DataFrame
    
    
    '''
    
    #Assertions: The index of the dataframe needs to be a type (pandas.core.indexes.datetimes.DatetimeIndex)
    
    AssertionError(type(data.index) == pd.core.indexes.datetimes.DatetimeIndex,
                   ''''Please set the date as your index. 
                   If your index is already a the date, make sure to set the data type to data.index.astype(datetime64[ns])''')
    

    #Create a cumulative win rate column and formula
    data['KellyCriterionCumulative'] = data[_column_SingleTradePercentageChange].expanding().apply(lambda x: KELLY_FORMULA(x) )
    
  
    return data

#%% Create new column that will determine the cumulative risk and return and the rolling win rate

def CUMULATIVE_AND_ROLLING_RISK_TO_RETURN_RATIO(data = None,
                                                _column_SingleTradePercentageChange: (str) = None,
                                                _boolean_apply_rolling_periods: (bool) = False):
    '''
    Creates multiple columns that shows the cumulative risk and return (30,60,90,180, 360 Days).
    This will be based on the percentage change per trade.
    
    Parameter
    --------
    data : Pandas Dataframe
    _column_SingleTradePercentageChange : String - Give the column name of the dataframe at which the return per trade can be found.
    
    
    Return
    --------
    Pandas DataFrame
    
    
    '''
    
    #Assertions: The index of the dataframe needs to be a type (pandas.core.indexes.datetimes.DatetimeIndex)
    
    AssertionError(type(data.index) == pd.core.indexes.datetimes.DatetimeIndex,
                   ''''Please set the date as your index. 
                   If your index is already a the date, make sure to set the data type to data.index.astype(datetime64[ns])''')
    
    
    
    #Create a cumulative win rate column and formula
    data['RiskReturnCumulative'] = data[_column_SingleTradePercentageChange].expanding().apply(lambda x: np.sum(x[x>0]) / abs(np.sum(x[x<0])) )
    
    if _boolean_apply_rolling_periods == True:
        #Create a rolling  win rate
        _frequency_days_list = [7,30,60,90,180,365]
        for _frequency in _frequency_days_list:
            data[f'RiskReturn{_frequency}DaysRolling'] = data[_column_SingleTradePercentageChange].rolling(f'{_frequency}D').apply(lambda x: np.sum(x[x>0]) / abs(np.sum(x[x<0])) )

    return data


#%% Create new column that will determine the cumulative win rate and the rolling win rate

def CUMULATIVE_AND_ROLLING_WIN_RATE(data = None,
                                    _column_SingleTradePercentageChange: (str) = None,
                                     _boolean_apply_rolling_periods: (bool) = False):
    '''
    Creates multiple columns that shows the cumulative win rate and rolling (30,60,90,180, 360 Days).
    This will be based on the percentage change per trade.
    
    Parameter
    --------
    data : Pandas Dataframe
    _column_SingleTradePercentageChange : String - Give the column name of the dataframe at which the return per trade can be found.
    
    
    Return
    --------
    Pandas DataFrame
    
    
    '''
    
    #Assertions: The index of the dataframe needs to be a type (pandas.core.indexes.datetimes.DatetimeIndex)
    
    AssertionError(type(data.index) == pd.core.indexes.datetimes.DatetimeIndex,
                   ''''Please set the date as your index. 
                   If your index is already a the date, make sure to set the data type to data.index.astype(datetime64[ns])''')
    
    
    
    #Create a cumulative win rate column and formula
    data['WinRateCumulative'] = data[_column_SingleTradePercentageChange].expanding().apply(lambda x: np.sum(x>0) / np.sum(~np.isnan(x)) )
    
    if _boolean_apply_rolling_periods == True:
        #Create a rolling  win rate
        _frequency_days_list = [7,30,60,90,180,365]
        for _frequency in _frequency_days_list:
            data[f'WinRate{_frequency}DaysRolling'] = data[_column_SingleTradePercentageChange].rolling(f'{_frequency}D').apply(lambda x: np.sum(x>0) / np.sum(~np.isnan(x)) )

    return data



#%%

def GET_EXIT_PRICE_BASED_ON_STATIC_STOPLOSS_AND_TAKE_PROFIT(data = None,
         _sl_or_tp = ('SL','TP'),
         _column_high_price: (str) = None,
         _column_low_price: (str) = None,
         _column_trade_direction: (str) = None,
         _column_takeprofit_price: (str) = None,
         _column_stoploss_price: (str) = None):

    
    gtlt =  GET_LOCATION_OF_FUTURE_GREATERTHAN_OR_LESSTHAN_PRICE()
   
    # Determine how many units in the future will the stoploss be triggered by the Low price
    
    #Add new column for the TP trigger date
    data['TakeProfitTriggerDate'] = pd.NA
    data['StopLossTriggerDate'] = pd.NA
    
    _last_row = data.shape[0]
    for _row_num in range(_last_row):
        _trade_direction = data[_column_trade_direction][_row_num]
        
        if _trade_direction == 'Long':
            #Take Profit analysis
            _take_profit_price = data[_column_takeprofit_price][_row_num]
            _series_future_high_price = data[_column_high_price][_row_num:_last_row]
            _takeprofit_hit_date = gtlt.TP_LONG_LOCATION(_take_profit_price, _series_future_high_price)
            data['TakeProfitTriggerDate'][_row_num] = _takeprofit_hit_date
            
            #Stop Loss Analysis
            _stop_loss_price = data[_column_stoploss_price][_row_num]
            _series_future_low_price = data[_column_low_price][_row_num:_last_row]
            _stoploss_hit_date = gtlt.SL_LONG_LOCATION(_stop_loss_price, _series_future_low_price)
            data['StopLossTriggerDate'][_row_num] = _stoploss_hit_date
            
        elif _trade_direction == 'Short':
            #Take Profit analysis
            _take_profit_price = data[_column_takeprofit_price][_row_num]
            _series_future_low_price = data[_column_low_price][_row_num:_last_row]
            _takeprofit_hit_date = gtlt.TP_SHORT_LOCATION(_take_profit_price, _series_future_low_price)
            data['TakeProfitTriggerDate'][_row_num] = _takeprofit_hit_date
            
            #Stop Loss Analysis
            _stop_loss_price = data[_column_stoploss_price][_row_num]
            _series_future_high_price = data[_column_high_price][_row_num:_last_row]
            _stoploss_hit_date = gtlt.SL_SHORT_LOCATION(_stop_loss_price, _series_future_high_price)
            data['StopLossTriggerDate'][_row_num] = _stoploss_hit_date
            
        elif _trade_direction == 'Hold':
             data['TakeProfitTriggerDate'][_row_num] = np.nan
             data['StopLossTriggerDate'][_row_num] = np.nan
                 
    # Check which is hit the earliest. TP or SL
    
    data['SLTPHit'] = np.nan
    data['SLTPHit'] = np.where(data['TakeProfitTriggerDate'] < data['StopLossTriggerDate'],
                               'TP',
                               data['SLTPHit'])
    
    data['SLTPHit'] = np.where(data['TakeProfitTriggerDate'] > data['StopLossTriggerDate'],
                               'SL',
                               data['SLTPHit'])
    
    data['SLTPHit'] = np.where(data['TakeProfitTriggerDate'] == data['StopLossTriggerDate'],
                               'SL',
                               data['SLTPHit'])
    
    data['SLTPHit'] = np.where((~pd.isnull(data['TakeProfitTriggerDate'])) &
                               (pd.isnull(data['StopLossTriggerDate'])),
                               'TP',
                               data['SLTPHit'])
            
    data['SLTPHit'] = np.where((pd.isnull(data['TakeProfitTriggerDate'])) &
                               (~pd.isnull(data['StopLossTriggerDate'])),
                               'SL',
                               data['SLTPHit'])
    
    # Determine the exit price based on the whether the TP or the SL got hit first
    
    data['ExitPrice'] = np.nan
    
    data['ExitPrice'] = np.where(data['SLTPHit'] == 'TP',
                                 data[_column_takeprofit_price],
                                 data['ExitPrice'])
    
    data['ExitPrice'] = np.where(data['SLTPHit'] == 'SL',
                                 data[_column_stoploss_price],
                                 data['ExitPrice'])
    
    # Identify Trade Duration
    data['TakeProfitTriggerDateDuration'] = data['TakeProfitTriggerDate'].astype('datetime64[ns]') - data.index
    data['StopLossTriggerDateDuration'] = data['StopLossTriggerDate'].astype('datetime64[ns]') - data.index
    
    return data

#%%
class GET_LOCATION_OF_FUTURE_GREATERTHAN_OR_LESSTHAN_PRICE:
    '''
    
    
    '''

    def TP_LONG_LOCATION(self, _value: (int) = None,
                         _series: (pd.core.series.Series)= None):
        try:
            _answer = _series[_series.gt(_value)].index[0]
        except:
            _answer = np.nan
        
        return _answer
      
        
    #%
    
    def SL_LONG_LOCATION(self, _value: (int) = None,
                         _series: (pd.core.series.Series)= None):
        try:
            _answer = _series[_series.lt(_value)].index[0]
        except:
            _answer = np.nan
        
        return _answer
      
    #%
    
    def TP_SHORT_LOCATION(self, _value: (int) = None,
                         _series: (pd.core.series.Series)= None):
        try:
            _answer = _series[_series.lt(_value)].index[0]
        except:
            _answer = np.nan
        
        return _answer
      
        
    #%
    
    def SL_SHORT_LOCATION(self, _value: (int) = None,
                         _series: (pd.core.series.Series)= None):
        try:
            _answer = _series[_series.gt(_value)].index[0]
        except:
            _answer = np.nan
        
        return _answer

#%%
def GET_EXIT_PRICE_BASED_ON_TRAILING_STOP(data = None,
                                         _column_high_price: (str) = None,
                                         _column_low_price: (str) = None,
                                         _column_TradeDirection: (str) = None,
                                         _column_LongStopLossRelativetoOpenPrice: (str) = None,
                                         _column_ShortStopLossRelativetoOpenPrice: (str) = None):
        
    df_fx = data.copy()
    
    df_fx['TrailingStoplossExitPrice'] = np.nan
    df_fx['TrailingExitStopLossDate'] = pd.NaT
    df_fx['TrailingHighLowDirection'] = pd.NA
    df_fx['FutureStopLossPrice'] = pd.NA
    df_fx['TrailingStopLoss'] = pd.NA
    
    
    _row_lenght = df_fx.shape[0]
    
    for _row_num in range(_row_lenght):
        print(f'_row_num: {_row_num}')
        _trade_direction = df_fx[_column_TradeDirection][_row_num]
        _future_long_stoploss = df_fx[_column_LongStopLossRelativetoOpenPrice][_row_num : _row_lenght]
        _future_short_stoploss = df_fx[_column_ShortStopLossRelativetoOpenPrice][_row_num : _row_lenght]
        
        _future_long_higher_low = df_fx['LongHigherHighHigherLow'][_row_num : _row_lenght]
        _future_short_lower_high = df_fx['ShortLowerHighLowerLow'][_row_num : _row_lenght]
        
        _future_low = df_fx[_column_low_price].ffill()[_row_num : _row_lenght]
        _future_high = df_fx[_column_high_price].ffill()[_row_num : _row_lenght]
        
        
        ############ need to fix ##################
        
        if _trade_direction == 'Long':
            _long_trailing_stoploss = TRAILING_STOPLOSS(_nparray_high_low = np.array(_future_long_higher_low), 
                                                            _nparray_stoploss = np.array(_future_long_stoploss), 
                                                            _nparray_trade_direction = _trade_direction)
            
            _condition = np.where(  _future_low <= _long_trailing_stoploss,
                                    True,
                                    False)
            
            try:
                _long_trailing_exit_price = _long_trailing_stoploss[_condition][0]
                _long_trailing_exit_date = _future_long_stoploss.index[_condition][0]
            except:
                _long_trailing_exit_price = np.nan
                _long_trailing_exit_date = np.nan
            
        elif _trade_direction == 'Short':                                                
            _short_trailing_stoploss = TRAILING_STOPLOSS(_nparray_high_low = np.array(_future_short_lower_high), 
                                                             _nparray_stoploss = np.array(_future_short_stoploss), 
                                                             _nparray_trade_direction = _trade_direction)
            
            _condition = np.where( _future_high >= _short_trailing_stoploss,
                                    True,
                                    False)
            try:
                _short_trailing_exit_price = _short_trailing_stoploss[_condition][0]
                _short_trailing_exit_date = _future_short_stoploss.index[_condition][0]
            except:
                _short_trailing_exit_price = np.nan
                _short_trailing_exit_date = np.nan
            
    
        ############ need to fix ##################
        
        if _trade_direction == 'Long':
            df_fx['FutureStopLossPrice'][_row_num] = np.array(_future_long_stoploss).astype(object)
            df_fx['TrailingHighLowDirection'][_row_num]  = np.array(_future_long_higher_low).astype(object)
            df_fx['TrailingStopLoss'][_row_num] = np.array(_long_trailing_stoploss).astype(object)
            df_fx['TrailingStoplossExitPrice'][_row_num] = _long_trailing_exit_price
            df_fx['TrailingExitStopLossDate'][_row_num] = _long_trailing_exit_date
        elif _trade_direction == 'Short':
            df_fx['FutureStopLossPrice'][_row_num] = np.array(_future_short_stoploss).astype(object)
            df_fx['TrailingHighLowDirection'][_row_num]  = np.array(_future_short_lower_high).astype(object)
            df_fx['TrailingStopLoss'][_row_num] = np.array(_short_trailing_stoploss).astype(object)
            df_fx['TrailingStoplossExitPrice'][_row_num] = _short_trailing_exit_price
            df_fx['TrailingExitStopLossDate'][_row_num] = _short_trailing_exit_date
        
    return df_fx
#%%

def TRAILING_STOPLOSS( _nparray_high_low = None, 
                       _nparray_stoploss = None, 
                       _nparray_trade_direction = None):
    """
    _nparray_high_low: Should contain
    _nparray_stoploss: Contains a floating point
    _nparray_trade_direction: Should contain Long and Short
    _nparray_high_low = np.array(_nparray_high_low)
    
    """


                      
    for _idx, _hl in enumerate(_nparray_high_low):
        #Modify only the succeding stoploss after the first one.
        if _idx > 0:
            if _nparray_trade_direction== 'Long':
                if _hl == 'LowerLow':
                    _nparray_stoploss[_idx] = _nparray_stoploss[_idx - 1]
                    
            elif _nparray_trade_direction == 'Short':
                if _hl == 'HigherHigh':
                    _nparray_stoploss[_idx] = _nparray_stoploss[_idx - 1]
    return _nparray_stoploss


def func(data = None,
         _column_high_price: (str) = None,
         _column_low_price: (str) = None,
         _column_TakeProfitPrice: (str) = None,
         _column_TradeDirection: (str) = None
         ):

    df_fx = data.copy()
    
    df_fx['TakeProfitHitDate'] = pd.NaT
    
    _total_row  = df_fx.shape[0]
    for _rownum in range(_total_row):
        print(_rownum)
        _list_future_high_price = df_fx[_column_high_price][_rownum : _total_row]
        _list_future_low_price = df_fx[_column_low_price][_rownum : _total_row]
        _take_profit_price = df_fx[_column_TakeProfitPrice][_rownum]
        _trade_direction = df_fx[_column_TradeDirection][_rownum]
        
        
        if float(_take_profit_price) > 0:
            if _trade_direction == 'Long':
                
                _condition = _list_future_high_price >= _take_profit_price
                
                if any(_condition) == True:
                    _take_profit_hit_date = _list_future_high_price.index[_condition][0]
                else:
                    _take_profit_hit_date = pd.NaT
                    
            elif _trade_direction == 'Short':
                
                _condition = _list_future_low_price <= _take_profit_price
                
                if any(_condition) == True:
                    _take_profit_hit_date = _list_future_low_price.index[_condition][0]
                else:
                    _take_profit_hit_date = pd.NaT
                    
            elif _trade_direction == 'Hold':
                _take_profit_hit_date = pd.NaT
            
            df_fx['TakeProfitHitDate'][_rownum] = _take_profit_hit_date
            
        return df_fx


def GET_TAKE_PROFIT_AND_DATE(data = None,
                             _column_high_price: (str) = None,
                             _column_low_price: (str) = None,
                             _column_TakeProfitPrice: (str) = None,
                             _column_TradeDirection: (str) = None
                             ):

    df_fx = data.copy()
    
    df_fx['TakeProfitHitDate'] = pd.NaT
    
    _total_row  = df_fx.shape[0]
    for _rownum in range(_total_row):
        print(_rownum)
        _list_future_high_price = df_fx[_column_high_price][_rownum : _total_row]
        _list_future_low_price = df_fx[_column_low_price][_rownum : _total_row]
        _take_profit_price = df_fx[_column_TakeProfitPrice][_rownum]
        _trade_direction = df_fx[_column_TradeDirection][_rownum]
        
        
        if float(_take_profit_price) > 0:
            if _trade_direction == 'Long':
                
                _condition = _list_future_high_price >= _take_profit_price
                
                if any(_condition) == True:
                    _take_profit_hit_date = _list_future_high_price.index[_condition][0]
                else:
                    _take_profit_hit_date = pd.NaT
                    
            elif _trade_direction == 'Short':
                
                _condition = _list_future_low_price <= _take_profit_price
                
                if any(_condition) == True:
                    _take_profit_hit_date = _list_future_low_price.index[_condition][0]
                else:
                    _take_profit_hit_date = pd.NaT
                    
            elif _trade_direction == 'Hold':
                _take_profit_hit_date = pd.NaT
            
            df_fx['TakeProfitHitDate'][_rownum] = _take_profit_hit_date
            
        return df_fx

#%%
def GENERATE_FINAL_EXIT_PRICE(data = None,
                             _column_TakeProfitHitDate: (str) = None,
                             _column_TakeProfitPrice: (str) = None,
                             _column_TrailingExitStopLossDate: (str) = None,
                             _column_TrailingStoplossExitPrice: (str) = None ):
    
    df_fx = data.copy()
    df_fx['ExitPrice'] = np.where(df_fx['TakeProfitHitDate'] < df_fx['TrailingExitStopLossDate'],
                              df_fx['TakeProfitPrice'],
                              df_fx['TrailingStoplossExitPrice'])
    return df_fx

#%% genera

def GENERATE_FIX_AND_SEPARATE_LONG_SHORT_STOPLOSS(data = None,
                            _column_Open_price: (str) = None,
                            _stoploss_rate: (float) = None):
    
    """
    The objective of the formula is to create a separate column of stoploss for long and short position 
    based on exactly the same percentage from the open price

    """
    df_fx = data.copy()
    
    df_fx['LongStopLossRelativetoOpenPrice'] = df_fx[_column_Open_price] * (1 - _stoploss_rate)
    
    df_fx['ShortStopLossRelativetoOpenPrice'] = df_fx[_column_Open_price] * (1 + _stoploss_rate)
    
    return df_fx

#%%
def GENERATE_HIGHER_HIGH_LOWER_LOW_COLUMN(data = None,
                                         _column_high_price: (str) = None,
                                         _column_row_price: (str) = None
                                         ):
    """
    Add column for Higher High and Lower low 1 period lag
    """
    
    df_fx = data.copy()
    df_fx['LongHigherHighHigherLow'] = np.nan
    df_fx['ShortLowerHighLowerLow'] = np.nan
    
    df_fx['LongHigherHighHigherLow'] = np.where(df_fx['Low'].shift(1) > df_fx['Low'].shift(2),
                                            'HigherLow',
                                            df_fx['LongHigherHighHigherLow'])
    
    df_fx['LongHigherHighHigherLow'] = np.where(df_fx['Low'].shift(1) < df_fx['Low'].shift(2),
                                            'LowerLow',
                                            df_fx['LongHigherHighHigherLow'])
    
    
    df_fx['ShortLowerHighLowerLow'] = np.where(df_fx['High'].shift(1) > df_fx['High'].shift(2),
                                            'HigherHigh',
                                            df_fx['ShortLowerHighLowerLow'])
    
    df_fx['ShortLowerHighLowerLow'] = np.where(df_fx['High'].shift(1) < df_fx['High'].shift(2),
                                            'LowerHigh',
                                            df_fx['ShortLowerHighLowerLow'])
    
    
    _columns = ['LongHigherHighHigherLow','ShortLowerHighLowerLow']
    
    df_fx[_columns] = df_fx[_columns].mask(df_fx == 'nan', np.nan).ffill()
    
    return df_fx

#%%
def RETURNS_ANALYSIS(data = None,
                     _column_trade_entry_price: (str) = None,
                     _column_trade_direction: (str) = None,
                     _column_trade_exit_price: (str) = None):
    
    # Get the percentage change between the exit price and the entry price
    
    
    
    data['SingleTradePercentageChange'] = (data[_column_trade_exit_price].astype('float64') /
                                           data[_column_trade_entry_price].astype('float64')
                                           - 1
                                           )
 
        
    data['SingleTradePercentageChange'] = np.where(data[_column_trade_direction] == 'Short',
                                                   data['SingleTradePercentageChange'] * -1,
                                                   data['SingleTradePercentageChange'])
    
    # Generate Cumulative Return
    
    data['CumulativeReturn'] = data['SingleTradePercentageChange'].expanding().apply(lambda x: np.prod(1+x)-1)
    
    data['Rolling30DReturn'] = data['SingleTradePercentageChange'].rolling('30D').apply(lambda x: np.prod(1+x)-1)
    
    data['Rolling3MReturn'] = data['SingleTradePercentageChange'].rolling('90D').apply(lambda x: np.prod(1+x)-1)
    
    data['Rolling6MReturn'] = data['SingleTradePercentageChange'].rolling('180D').apply(lambda x: np.prod(1+x)-1)
    
    data['Rolling9MReturn'] = data['SingleTradePercentageChange'].rolling('270D').apply(lambda x: np.prod(1+x)-1)
    
    return data


#%% Create a simulated trade based on random number generation between 0 & 2


def GENERATE_RANDOM_TRADE_DIRECTION(data = None):
    
    df_fx = data.copy()
    
    df_fx['TradeDirection'] = [random.randint(0, 2) for _ in range(df_fx.shape[0])]
    
    df_fx['TradeDirection'] = np.where(df_fx['TradeDirection'] == 0,
                                       'Short',
                                       df_fx['TradeDirection'])
    
    df_fx['TradeDirection'] = np.where(df_fx['TradeDirection'] == '1',
                                       'Long',
                                       df_fx['TradeDirection'])
    
    df_fx['TradeDirection'] = np.where(df_fx['TradeDirection'] == '2',
                                       'Hold',
                                       df_fx['TradeDirection'])
    
    return df_fx

#%% Generatefix take profit

def GENERATE_FIX_TAKE_PROFIT_PRICE(data = None,
                                   _takeprofit_rate: (float) = None):
    df_fx = data.copy()
    df_fx['TakeProfitPrice'] = np.nan
    df_fx['TakeProfitPrice'] = np.where(df_fx['TradeDirection'] =='Long',
                                            df_fx['Open'] * (1 + _takeprofit_rate),
                                            df_fx['TakeProfitPrice']
                                            )
                                            
    df_fx['TakeProfitPrice'] = np.where(df_fx['TradeDirection'] =='Short',
                                            df_fx['Open'] * (1 - _takeprofit_rate),
                                            df_fx['TakeProfitPrice']
                                            )
    return df_fx

#%% Generate volatility based of high and low price lagging by 1 unit and take the absolute value

def GENERATE_HIGH_TO_LOW_VOLATILITY_SCORE(data = None,
                                          _period_number = None,
                                          _column_high: (str) = None,
                                          _column_low: (str) = None):
    """
    generate volatility using standard deviation from the percentage change between high and low price
    and to get the percetage score overtime using expanding function
    
    """
    
    df_fx = data.copy()
    df_fx['PercentChangeHighToLow'] = abs(df_fx[_column_high].shift(1) / df_fx[_column_low].shift(1) - 1)   
    df_fx['Volatility'] = df_fx['PercentChangeHighToLow'].fillna(method = 'ffill').rolling(_period_number).apply(lambda x: statistics.stdev(list(x)))    
    df_fx['VolatilityRank'] = df_fx['Volatility'].expanding().apply(lambda x: stats.percentileofscore(x,x[-1]))
    
    return df_fx




























