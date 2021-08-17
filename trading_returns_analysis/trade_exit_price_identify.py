
#%% import module 

import pandas as pd
import numpy as np
from asset_price_etl import etl_fx_histadata_001 as etl
import warnings
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

#%% Supress warnings
pd.set_option('display.max_columns',500)
warnings.filterwarnings('ignore')

#%% Generatefix take profit

def GENERATE_FIX_TAKE_PROFIT_PRICE(_df_data = None,
                                   _str_takeprofit_rate_column_name: (float) = None,
                                   _str_column_name_trade_direction: str = None,
                                   _str_open_price_column_name = None):
    """s
    Description
    ----
        This function allows you to set a fix rate relative to the open price as the take profit

    Args:
        _df_data ([type], optional): [description]. Defaults to None.
        _str_takeprofit_rate_column_name ([type], optional): [description]. Defaults to None.
        _str_column_name_tradedirection (str, optional): [description]. Defaults to None.

    Returns:
        [type]: [description]
    """

    df_fx = _df_data.copy()
    df_fx['TakeProfitPrice'] = np.nan
    df_fx['TakeProfitPrice'] = np.where(df_fx[_str_column_name_trade_direction] =='Long',
                                            df_fx[_str_open_price_column_name] * (1 + df_fx[_str_takeprofit_rate_column_name]),
                                            df_fx['TakeProfitPrice']
                                            )
                                            
    df_fx['TakeProfitPrice'] = np.where(df_fx[_str_column_name_trade_direction] =='Short',
                                            df_fx[_str_open_price_column_name] * (1 - df_fx[_str_takeprofit_rate_column_name]),
                                            df_fx['TakeProfitPrice']
                                            )
    
    return pd.Series(df_fx['TakeProfitPrice'])

#%% genera

def GENERATE_FIX_AND_SEPARATE_LONG_SHORT_STOPLOSS(_df_data = None,
                                                _str_column_Open_price: (str) = None,
                                                _str_stoploss_rate_column_name: (str) = None):
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
    
    df_fx['LongStopLossRelativetoOpenPrice'] = df_fx[_str_column_Open_price] * (1 - df_fx[_str_stoploss_rate_column_name])
    
    df_fx['ShortStopLossRelativetoOpenPrice'] = df_fx[_str_column_Open_price] * (1 + df_fx[_str_stoploss_rate_column_name])
    
    return df_fx

#%%
def GENERATE_HIGHER_HIGH_LOWER_LOW_COLUMN(_df_data = None,
                                         _str_high_price_column_name : (str) = None,
                                         _str_low_price_column_name : (str) = None
                                         ):
    """
    Add column for Higher High and Lower low 1 period lag
    """
    
    
    _df_data['LongHigherHighHigherLow'] = np.nan
    _df_data['ShortLowerHighLowerLow'] = np.nan
    
    _df_data['LongHigherHighHigherLow'] = np.where(_df_data[_str_low_price_column_name].shift(1) > _df_data[_str_low_price_column_name],
                                            'HigherLow',
                                            _df_data['LongHigherHighHigherLow'])
    
    _df_data['LongHigherHighHigherLow'] = np.where(_df_data[_str_low_price_column_name].shift(1) < _df_data[_str_low_price_column_name],
                                            'LowerLow',
                                            _df_data['LongHigherHighHigherLow'])
    
    
    _df_data['ShortLowerHighLowerLow'] = np.where(_df_data[_str_high_price_column_name ].shift(1) > _df_data[_str_high_price_column_name ],
                                            'HigherHigh',
                                            _df_data['ShortLowerHighLowerLow'])
    
    _df_data['ShortLowerHighLowerLow'] = np.where(_df_data[_str_high_price_column_name ].shift(1) < _df_data[_str_high_price_column_name ],
                                            'LowerHigh',
                                            _df_data['ShortLowerHighLowerLow'])
    
    
    _columns = ['LongHigherHighHigherLow','ShortLowerHighLowerLow']
    
    _df_data[_columns] = _df_data[_columns].mask(_df_data == 'nan', np.nan).ffill()
    
    return _df_data

#%%

def TRAILING_STOPLOSS( _nparray_high_low = None, 
                       _nparray_stoploss = None, 
                       _nparray_trade_direction = None):
    """
    Description:
    ------
    
    
    Parameters:
    ------
    
    _nparray_high_low: Should contain
    _nparray_stoploss: Contains a floating point
    _nparray_trade_direction: Should contain Long and Short
    _nparray_high_low = np.array(_nparray_high_low)
    
    """


    _nparray_stoploss_trailing = []                  
    for _idx, _hl in enumerate(_nparray_high_low):
        #Modify only the succeding stoploss after the first one.
        if _idx > 0:
            if _nparray_trade_direction== 'Long':
                print(_hl)
                print(_nparray_stoploss_trailing)
                print(f"_idx {_idx}")
                print(_nparray_stoploss)
                if _hl == 'LowerLow':
                    if len(_nparray_stoploss_trailing) > 0:
                        _nparray_stoploss_trailing.append(_nparray_stoploss_trailing[_idx - 2])
                    else:
                        _nparray_stoploss_trailing.append(_nparray_stoploss[_idx])
                else:
                    _nparray_stoploss_trailing.append(_nparray_stoploss[_idx])
                    
            elif _nparray_trade_direction == 'Short':
                if _hl == 'HigherHigh':
                    if len(_nparray_stoploss_trailing) > 0:
                        _nparray_stoploss_trailing.append(_nparray_stoploss_trailing[_idx - 2])
                    else:
                        _nparray_stoploss_trailing.append(_nparray_stoploss[_idx])
                else:
                    _nparray_stoploss_trailing.append(_nparray_stoploss[_idx])
                    
    return _nparray_stoploss


#%% GET_EXIT_PRICE_BASED_ON_TRAILING_STOP
def GET_EXIT_PRICE_BASED_ON_TRAILING_STOP(_df_data = None,
                                         _str_high_price_column_name : (str) = None,
                                         _str_low_price_column_name : (str) = None,
                                         _str_trade_direction_column_name : (str) = None,
                                         _str_column_name_LongStopLossRelativetoOpenPrice: (str) = None,
                                         _str_column_name_ShortStopLossRelativetoOpenPrice: (str) = None):
    
    global _condition, _long_trailing_stoploss
    
    _df_data['TrailingStoplossExitPrice'] = np.nan
    _df_data['TrailingExitStopLossDate'] = pd.NaT
    _df_data['TrailingHighLowDirection'] = pd.NA
    _df_data['FutureStopLossPrice'] = pd.NA
    _df_data['TrailingStopLoss'] = pd.NA
    
    
    _row_lenght = _df_data.shape[0]
    
    for _row_num in range(_row_lenght):
        
        _trade_direction = _df_data[_str_trade_direction_column_name][_row_num]
        _future_long_stoploss = _df_data[_str_column_name_LongStopLossRelativetoOpenPrice][_row_num : _row_lenght]
        _future_short_stoploss = _df_data[_str_column_name_ShortStopLossRelativetoOpenPrice][_row_num : _row_lenght]
        
        _future_long_higher_low = _df_data['LongHigherHighHigherLow'][_row_num : _row_lenght]
        _future_short_lower_high = _df_data['ShortLowerHighLowerLow'][_row_num : _row_lenght]
        
        _future_low = _df_data[_str_low_price_column_name].ffill()[_row_num : _row_lenght]
        _future_high = _df_data[_str_high_price_column_name].ffill()[_row_num : _row_lenght]
        
        _ShortStopLossRelativetoOpenPrice = _df_data[_str_column_name_ShortStopLossRelativetoOpenPrice][_row_num ]
        _LongStopLossRelativetoOpenPrice = _df_data[_str_column_name_LongStopLossRelativetoOpenPrice][_row_num ]
        
        
        ############ need to fix ##################
        
        if _trade_direction == 'Long':
        
            _long_trailing_stoploss = TRAILING_STOPLOSS_V2(pdSeries_future_high_price = _future_high,
                                                            pdSeries_future_low_price = _future_low,
                                                            pdSeries_future_stoploss = _future_long_stoploss,
                                                            str_trade_direction = _trade_direction )                                          
########################## array vs single value to be resolved ####################

            """
            print(f'_future_low: {type(_future_low)}')
            print(f'_long_trailing_stoploss: {type(_long_trailing_stoploss)}')
            print(f'_future_low: {_future_low}')
            print(f'_long_trailing_stoploss: {_long_trailing_stoploss}')
            print((_future_low <= _long_trailing_stoploss))
            print((list(np.array(_future_low) <= _LongStopLossRelativetoOpenPrice)))
            _condition = np.where(  (_future_low <= _long_trailing_stoploss) or (list(np.array(_future_low) <= _LongStopLossRelativetoOpenPrice)) ,
                                    True,
                                    False)
                                    
            """
            
            print(f'_future_low: {type(_future_low)}')
            print(f'_long_trailing_stoploss: {type(_long_trailing_stoploss)}')
            print(f'_future_low: {_future_low}')
            print(f'_long_trailing_stoploss: {_long_trailing_stoploss}')
            print(list(_future_low <= _long_trailing_stoploss))
            print((list(np.array(_future_low) <= _LongStopLossRelativetoOpenPrice)))
            
           
            _condition = np.where(  (list(_future_low <= _long_trailing_stoploss)) ,
                                    True,
                                    False)
            
            print(f'_condition {len(_condition)} {_condition}')
            print(f'_long_trailing_stoploss {len(_long_trailing_stoploss)} {_long_trailing_stoploss}')

            try: 
            
                _long_trailing_exit_price = np.array(_long_trailing_stoploss)[_condition][0]
                _long_trailing_exit_date = _future_long_stoploss.index[_condition][0]
               
            except:
                _long_trailing_exit_price = np.nan
                _long_trailing_exit_date = np.nan
            
            print(f'_long_trailing_exit_price {_long_trailing_exit_price}')
            print(f'_long_trailing_exit_date {_long_trailing_exit_date}')
            
        elif _trade_direction == 'Short': 
           

            _short_trailing_stoploss = TRAILING_STOPLOSS_V2(pdSeries_future_high_price = _future_high,
                                                            pdSeries_future_low_price = _future_low,
                                                            pdSeries_future_stoploss = _future_short_stoploss,
                                                            str_trade_direction = _trade_direction ) 

         
            _condition = np.where( (list(_future_high >= _short_trailing_stoploss)) ,
                                    True,
                                    False)

            print(f'_condition {_condition}')
            print(f'_short_trailing_stoploss {_short_trailing_stoploss}')

            try:
                _short_trailing_exit_price = np.array(_short_trailing_stoploss)[_condition][0]
                _short_trailing_exit_date = _future_short_stoploss.index[_condition][0]
            except:
                _short_trailing_exit_price = np.nan
                _short_trailing_exit_date = np.nan
            
            print(f'_short_trailing_exit_price {_short_trailing_exit_price}')
            print(f'_short_trailing_exit_date {_short_trailing_exit_date}')
    
        ############ need to fix ##################
        
        if _trade_direction == 'Long':
            _df_data['FutureStopLossPrice'][_row_num] = np.array(_future_long_stoploss).astype(object)
            _df_data['TrailingHighLowDirection'][_row_num]  = np.array(_future_long_higher_low).astype(object)
            _df_data['TrailingStopLoss'][_row_num] = np.array(_long_trailing_stoploss).astype(object)
            _df_data['TrailingStoplossExitPrice'][_row_num] = _long_trailing_exit_price
            _df_data['TrailingExitStopLossDate'][_row_num] = _long_trailing_exit_date
        elif _trade_direction == 'Short':
            _df_data['FutureStopLossPrice'][_row_num] = np.array(_future_short_stoploss).astype(object)
            _df_data['TrailingHighLowDirection'][_row_num]  = np.array(_future_short_lower_high).astype(object)
            _df_data['TrailingStopLoss'][_row_num] = np.array(_short_trailing_stoploss).astype(object)
            _df_data['TrailingStoplossExitPrice'][_row_num] = _short_trailing_exit_price
            _df_data['TrailingExitStopLossDate'][_row_num] = _short_trailing_exit_date
        
    return _df_data


#%% GET_TAKE_PROFIT_AND_DATE

def GET_TAKE_PROFIT_AND_DATE(_df_data = None,
                             _str_high_price_column_name: (str) = None,
                             _str_low_price_column_name: (str) = None,
                             _str_column_name_TakeProfitPrice: (str) = None,
                             _str_column_name_TradeDirection: (str) = None
                             ):

    
    assert ( ['Long', 'Short', 'Hold'] in _df_data['TradeDirection'].unique() , 
            "Make sure that TradeDirection column only contains the following values ['Long', 'Short', 'Hold']"
            )
    
    _df_data['TakeProfitHitDate'] = pd.NaT
    
    _int_total_row  = _df_data.shape[0]
    
    for _int_rownum in range(_int_total_row):
        
        _list_future_high_price = _df_data[_str_high_price_column_name][_int_rownum : _int_total_row]
        _list_future_low_price = _df_data[_str_low_price_column_name][_int_rownum : _int_total_row]
        _float_take_profit_price = _df_data[_str_column_name_TakeProfitPrice][_int_rownum]
        _str_trade_direction = _df_data[_str_column_name_TradeDirection][_int_rownum]
        
        
        if float(_float_take_profit_price) > 0:
            if _str_trade_direction == 'Long':
                
                _condition = _list_future_high_price >= _float_take_profit_price
                
                if any(_condition) == True:
                    _take_profit_hit_date = _list_future_high_price.index[_condition][0]
                else:
                    _take_profit_hit_date = pd.NaT
                    
            elif _str_trade_direction == 'Short':
                
                _condition = _list_future_low_price <= _float_take_profit_price
                
                if any(_condition) == True:
                    _take_profit_hit_date = _list_future_low_price.index[_condition][0]
                else:
                    _take_profit_hit_date = pd.NaT
                    
            elif _str_trade_direction == 'Hold':
                _take_profit_hit_date = pd.NaT
            
            _df_data['TakeProfitHitDate'][_int_rownum] = _take_profit_hit_date
            
            
    return _df_data


#%% Generate final exit price
def GENERATE_FINAL_EXIT_PRICE(  _df_data = None,
                                _str_column_name_TakeProfitHitDate: (str) = None,
                                _str_column_name_TakeProfitPrice: (str) = None,
                                _str_column_name_TrailingExitStopLossDate: (str) = None,
                                _str_column_name_TrailingStoplossExitPrice: (str) = None ):
    
    
    _df_data['ExitPrice'] = np.where(_df_data[_str_column_name_TakeProfitHitDate] < _df_data[_str_column_name_TrailingExitStopLossDate],
                                    _df_data[_str_column_name_TakeProfitPrice],
                                    _df_data[_str_column_name_TrailingStoplossExitPrice]
                                    )
    
    _df_data['ExitDate'] = np.where(_df_data[_str_column_name_TakeProfitHitDate] < _df_data[_str_column_name_TrailingExitStopLossDate],
                                    _df_data[_str_column_name_TakeProfitHitDate],
                                     _df_data[_str_column_name_TrailingExitStopLossDate]
                                    )
    return _df_data


#%% Create a simulated trade based on random number generation between 0 & 2

def GENERATE_RANDOM_TRADE_DIRECTION(_df_data = None):
    """
    Description
    ---------- 
        This function enables you to generate a random trade direction for simulation purpose only

    Args:
    ---------- 
        _df_data (pandas.core.frame.DataFrame, required): A pandas dataframe. Defaults to None.

    Returns:
    ---------- 
        pandas.core.series.Series: pandas series

    Example:
    -----
    >>> df_fx['TradeDirection'] = tradingformula.GENERATE_RANDOM_TRADE_DIRECTION(_df_data = df_fx)
    """
    
    df_fx = _df_data.copy()
    

    np.random.seed(1)
    df_fx['TradeDirection'] = np.random.randint(3, size=df_fx.shape[0])
    
    df_fx['TradeDirection'] = np.where(df_fx['TradeDirection'] == 0,
                                    'Short',
                                    df_fx['TradeDirection'])
    
    df_fx['TradeDirection'] = np.where(df_fx['TradeDirection'] == '1',
                                    'Long',
                                    df_fx['TradeDirection'])
    
    df_fx['TradeDirection'] = np.where(df_fx['TradeDirection'] == '2',
                                    'Hold',
                                    df_fx['TradeDirection'])
    
    return pd.Series(df_fx['TradeDirection'])
    
#%% Generage fuuture Open High Low Close for checking puposes

def GENERATE_FUTURE_OPEN_HIGH_LOW_CLOSE_DATE_COLUMN(df_data = None,
                                                    str_open_price_column_name = None,
                                                    str_high_price_column_name = None,
                                                    str_low_price_column_name = None,
                                                    str_close_price_column_name = None,
                                                    str_date_column_name = None):
    df_data['FutureDate'] = pd.NA
    df_data['FutureOpenPrice'] = pd.NA
    df_data['FutureHighPrice'] = pd.NA
    df_data['FutureLowPrice'] = pd.NA
    df_data['FutureClosePrice'] = pd.NA
    
    int_total_row  = df_data.shape[0]
    
    for int_row_number in range(int_total_row):
        list_future_date = df_data[str_date_column_name].astype(str)[int_row_number : int_total_row]
        list_future_open_price = df_data[str_open_price_column_name][int_row_number : int_total_row]
        list_future_high_price = df_data[str_high_price_column_name][int_row_number : int_total_row]
        list_future_low_price = df_data[str_low_price_column_name][int_row_number : int_total_row]
        list_future_close_price = df_data[str_close_price_column_name][int_row_number : int_total_row]
        
        df_data['FutureDate'][int_row_number] = np.array(list_future_date).astype(object)
        df_data['FutureOpenPrice'][int_row_number] = np.array(list_future_open_price).astype(object)
        df_data['FutureHighPrice'][int_row_number] = np.array(list_future_high_price).astype(object)
        df_data['FutureLowPrice'][int_row_number] = np.array(list_future_low_price).astype(object)
        df_data['FutureClosePrice'][int_row_number] = np.array(list_future_close_price).astype(object)
        
        
    return df_data


def TRAILING_STOPLOSS_V2(pdSeries_future_high_price = None,
                         pdSeries_future_low_price = None,
                         pdSeries_future_stoploss = None,
                         str_trade_direction = None):

    pdSeries_trailing_stoploss = []
    if str_trade_direction == 'Long':

        for int_index, float_stoploss in enumerate(pdSeries_future_stoploss):
            if int_index < 2:
                pdSeries_trailing_stoploss.append(pdSeries_future_stoploss[0])
            else:
                if (pdSeries_future_low_price[int_index - 2] < pdSeries_future_low_price[int_index]) and (pdSeries_trailing_stoploss[int_index - 1] < pdSeries_future_stoploss[int_index]):
                    pdSeries_trailing_stoploss.append(pdSeries_future_stoploss[int_index])
                else:
                    pdSeries_trailing_stoploss.append(pdSeries_trailing_stoploss[int_index-1])   

    elif str_trade_direction == 'Short':

        for int_index, float_stoploss in enumerate(pdSeries_future_stoploss):
            if int_index < 2:
                pdSeries_trailing_stoploss.append(pdSeries_future_stoploss[0])
            else:
                if (pdSeries_future_high_price[int_index - 2] > pdSeries_future_high_price[int_index]) and (pdSeries_trailing_stoploss[int_index - 1] > pdSeries_future_stoploss[int_index]):
                    pdSeries_trailing_stoploss.append(pdSeries_future_stoploss[int_index])
                else:
                    pdSeries_trailing_stoploss.append(pdSeries_trailing_stoploss[int_index-1]) 


    return pdSeries_trailing_stoploss
#%% Main function

def _func_get_exit_price(_df_data = None,
                        _str_open_price_column_name = None,
                        _str_high_price_column_name = None,
                        _str_low_price_column_name = None,
                        _str_close_price_column_name = None,
                        _str_stoploss_rate_column_name = None,
                        _str_takeprofit_rate_column_name = None,
                        _str_trade_direction_column_name = None,
                        _str_column_name_LongStopLossRelativetoOpenPrice = None,
                        _str_column_name_ShortStopLossRelativetoOpenPrice = None):

    
    _df_data['TakeProfitPrice'] = GENERATE_FIX_TAKE_PROFIT_PRICE(  _df_data = _df_data,
                                                                _str_takeprofit_rate_column_name =  _str_takeprofit_rate_column_name,
                                                                _str_column_name_trade_direction = _str_trade_direction_column_name,
                                                                _str_open_price_column_name = _str_open_price_column_name )
    
    
    
    #%% Add column for Stoploss Price Relative to the open price

    _df_data = GENERATE_FIX_AND_SEPARATE_LONG_SHORT_STOPLOSS(_df_data = _df_data,
                                                            _str_column_Open_price = _str_open_price_column_name,
                                                            _str_stoploss_rate_column_name = _str_stoploss_rate_column_name)

    
    #%% Create a new column that determines if the previous i
    #period created a higher high or lower high or higher low or lower low

    _df_data = GENERATE_HIGHER_HIGH_LOWER_LOW_COLUMN(_df_data  = _df_data,
                                                    _str_high_price_column_name  = _str_high_price_column_name,
                                                    _str_low_price_column_name  = _str_low_price_column_name)
                
    
    #%% Get exit price based on trailing stop

    _df_data = GET_EXIT_PRICE_BASED_ON_TRAILING_STOP(_df_data = _df_data,
                                                     _str_column_name_LongStopLossRelativetoOpenPrice = 'LongStopLossRelativetoOpenPrice',
                                                     _str_column_name_ShortStopLossRelativetoOpenPrice = 'ShortStopLossRelativetoOpenPrice',
                                                    _str_high_price_column_name   = 'High',
                                                    _str_low_price_column_name  = 'Low',
                                                    _str_trade_direction_column_name  = 'TradeDirection')
    
    
    #%% Identify Static Take Profit Hit Date

    _df_data = GET_TAKE_PROFIT_AND_DATE(_df_data = _df_data,
                                        _str_high_price_column_name = 'High',
                                        _str_low_price_column_name = 'Low',
                                        _str_column_name_TakeProfitPrice = 'TakeProfitPrice',
                                        _str_column_name_TradeDirection = 'TradeDirection')

    
    #%% Generate an exit price based on which was triggered first, is it the stoploss or the take profit

    _df_data = GENERATE_FINAL_EXIT_PRICE(_df_data = _df_data,
                                        _str_column_name_TakeProfitHitDate = 'TakeProfitHitDate',
                                        _str_column_name_TakeProfitPrice = 'TakeProfitPrice',
                                        _str_column_name_TrailingExitStopLossDate = 'TrailingExitStopLossDate',
                                        _str_column_name_TrailingStoplossExitPrice = 'TrailingStoplossExitPrice')

    
    _df_data = GENERATE_FUTURE_OPEN_HIGH_LOW_CLOSE_DATE_COLUMN(df_data = _df_data.reset_index(),
                                                                str_open_price_column_name = 'Open',
                                                                str_high_price_column_name = 'High',
                                                                str_low_price_column_name = 'Low',
                                                                str_close_price_column_name = 'Close',
                                                                str_date_column_name = 'DateTime')
    
    _df_data['DateTime'] = _df_data['DateTime'].astype('datetime64[ns]')
    _df_data = _df_data.set_index('DateTime')
    
    return _df_data



#%% Testing

if __name__ == '__main__':
    #%% Download data
    df_data = etl._function_extract(_str_valuedate_start = '1/1/2018',
                                     _str_valuedate_end = '12/31/2018',
                                     _str_resample_frequency = 'W')
    
    
    #%% Create a simulated trade based on random number generation between 0 & 2
    df_data['TradeDirection'] = GENERATE_RANDOM_TRADE_DIRECTION(_df_data = df_data)
    
    
    #%% Set the take profit and stoploss rate
    df_data['TakeProfitRate'] = 0.02
    df_data['StoplossRate'] = 0.01
    

    #%% Generate exit price
    df_data = _func_get_exit_price(_df_data = df_data,
                                    _str_open_price_column_name = 'Open',
                                    _str_high_price_column_name = 'High',
                                    _str_low_price_column_name = 'Low',
                                    _str_close_price_column_name = 'Close',
                                    _str_stoploss_rate_column_name = 'StoplossRate',
                                    _str_takeprofit_rate_column_name = 'TakeProfitRate',
                                    _str_trade_direction_column_name = 'TradeDirection',
                                    _str_column_name_LongStopLossRelativetoOpenPrice = 'LongStopLossRelativetoOpenPrice',
                                    _str_column_name_ShortStopLossRelativetoOpenPrice = 'ShortStopLossRelativetoOpenPrice') 

    df_data.to_csv('Output.csv')
    df_data = df_data.fillna(np.nan)

    #%% Create a plotly plot that shows the fx price together with the volatility

    _obj_fig = make_subplots(rows = 1, cols=1, shared_xaxes=True)


    _obj_fig.add_trace(go.Candlestick(
                                        x = df_data.index,
                                        open = df_data.Open,
                                        high = df_data.High,
                                        low = df_data.Low,
                                        close = df_data.Close
                                        ),
                        row = 1,
                        col=1
                        )


    for _int_row_number in range(df_data.shape[0]):
        

        _str_trade_direction = df_data['TradeDirection'][_int_row_number]
        
        if ( _str_trade_direction == 'Long' or _str_trade_direction == 'Short'):
            
            _date_x_axis_head = df_data['ExitDate'][_int_row_number]
            _int_y_axis_head = df_data['ExitPrice'][_int_row_number]
            _date_x_axis_tail = df_data.index[_int_row_number]
            _int_y_axis_tail = df_data['Open'][_int_row_number]
            
            
            
            print(f"_date_x_axis_head {_date_x_axis_head}")
            print(f"_int_y_axis_head {_int_y_axis_head}")
            print(f"_date_x_axis_tail {_date_x_axis_tail}")
            print(f"_int_y_axis_tail {_int_y_axis_tail}")

            if _int_y_axis_head > 0 and _int_y_axis_tail > 0:
                if _str_trade_direction == 'Long':
                    _obj_fig.add_annotation(
                                            x=_date_x_axis_head,  # arrows' head
                                            y=_int_y_axis_head,  # arrows' head
                                            ax=_date_x_axis_tail,  # arrows' tail
                                            ay=_int_y_axis_tail,  # arrows' tail
                                            xref='x',
                                            yref='y',
                                            axref='x',
                                            ayref='y',
                                            text='',  # if you want only the arrow
                                            showarrow=True,
                                            arrowhead=3,
                                            arrowsize=2,
                                            arrowwidth=1,
                                            arrowcolor=  'green' 
                                            )
                elif _str_trade_direction == 'Short' and _int_y_axis_tail > 0 and _int_y_axis_head != np.nan:
                    _obj_fig.add_annotation(
                                                x=_date_x_axis_head,  # arrows' head
                                                y=_int_y_axis_head,  # arrows' head
                                                ax=_date_x_axis_tail,  # arrows' tail
                                                ay=_int_y_axis_tail,  # arrows' tail
                                                xref='x',
                                                yref='y',
                                                axref='x',
                                                ayref='y',
                                                text='',  # if you want only the arrow
                                                showarrow=True,
                                                arrowhead=3,
                                                arrowsize=2,
                                                arrowwidth=1,
                                                arrowcolor=  'red' 
                                                )
                
    
    df_data['StoplossPrice'] = np.where(df_data['TradeDirection'] == 'Long',
                                         df_data['LongStopLossRelativetoOpenPrice'],
                                         np.where(df_data['TradeDirection'] == 'Short',
                                                  df_data['ShortStopLossRelativetoOpenPrice'],
                                                  np.nan
                                                )
                                        )

    _obj_fig.add_trace(go.Scatter(x=df_data.index, 
                                    y=df_data['StoplossPrice'],
                                    mode='markers',
                                    name='markers')
                        )
    
    _obj_fig.add_trace(go.Scatter(x=df_data.index, 
                                y=df_data['TakeProfitPrice'],
                                mode='markers',
                                name='markers')
                        )

    _obj_fig.update_layout(xaxis_rangeslider_visible=False)

    pio.renderers.default = 'browser'

    pio.show(_obj_fig)


# %%

def PLOT_SINGLE_TRADE_TRAILING_STOPLOSS_AND_TAKEPROFIT(df_data = None):
    
    obj_fig = make_subplots(rows = 1, cols=1, shared_xaxes=True)
    obj_fig.add_trace(go.Candlestick(
                                        x = df_data.FutureDate,
                                        open = df_data.FutureOpenPrice,
                                        high = df_data.FutureHighPrice,
                                        low = df_data.FutureLowPrice,
                                        close = df_data.FutureClosePrice
                                        ),
                        row = 1,
                        col=1
                        )
    
    obj_fig.add_trace(go.Scatter(x=df_data.FutureDate, 
                                y=df_data.TrailingStopLoss,
                                mode='lines+markers',
                                name='TrailingStopLoss')
                    )
    
    obj_fig.add_trace(go.Scatter(x=df_data.FutureDate, 
                                y=df_data.FutureStopLossPrice,
                                mode='lines+markers',
                                name='FutureStopLossPrice')
                    )
    
    obj_fig.update_layout(xaxis_rangeslider_visible=False)

    pio.renderers.default = 'browser'

    return pio.show(obj_fig)


# %%


# %% test if the trailing stop loss are correct

str_date = '2018-11-18'
df_temp = df_data.loc[str_date:str_date,:]

df_temp2 = df_temp.apply(lambda x: x.explode() if x.name in ['TrailingHighLowDirection','FutureStopLossPrice','TrailingStopLoss','FutureOpenPrice','FutureHighPrice','FutureLowPrice','FutureClosePrice','FutureDate'] else x)
df_temp2['FutureDate'] = df_temp2['FutureDate'].astype('datetime64[ns]')

PLOT_SINGLE_TRADE_TRAILING_STOPLOSS_AND_TAKEPROFIT(df_data = df_temp2)

print(df_temp2.head(10))
# %%
