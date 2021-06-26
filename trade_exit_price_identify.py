#%% import module 

import pandas as pd
import numpy as np

#%% genera

def GENERATE_FIX_AND_SEPARATE_LONG_SHORT_STOPLOSS(_df_data = None,
                                                _str_column_Open_price: (str) = None,
                                                _float_stoploss_rate: (float) = None):
    """
    Description:
    ------
    The objective of the formula is to create a separate column of stoploss for long and short position 
    based on exactly the same percentage from the open price

    Args:
        data ([type], optional): [description]. Defaults to None.
        _column_Open_price ([type], optional): [description]. Defaults to None.
        _stoploss_rate ([type], optional): [description]. Defaults to None.

    Returns:
        [type]: [description]
    """

    df_fx = _df_data.copy()
    
    df_fx['LongStopLossRelativetoOpenPrice'] = df_fx[_str_column_Open_price] * (1 - _float_stoploss_rate)
    
    df_fx['ShortStopLossRelativetoOpenPrice'] = df_fx[_str_column_Open_price] * (1 + _float_stoploss_rate)
    
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
