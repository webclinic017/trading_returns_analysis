
#%% import module 

import pandas as pd
import numpy as np
from asset_price_etl import etl_fx_histadata_001 as etl
import sqlconnection as sc
import random
import warnings
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

#%% Supress warnings

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
    
    _df_data['LongHigherHighHigherLow'] = np.where(_df_data[_str_low_price_column_name].shift(1) > _df_data[_str_low_price_column_name].shift(2),
                                            'HigherLow',
                                            _df_data['LongHigherHighHigherLow'])
    
    _df_data['LongHigherHighHigherLow'] = np.where(_df_data[_str_low_price_column_name].shift(1) < _df_data[_str_low_price_column_name].shift(2),
                                            'LowerLow',
                                            _df_data['LongHigherHighHigherLow'])
    
    
    _df_data['ShortLowerHighLowerLow'] = np.where(_df_data[_str_high_price_column_name ].shift(1) > _df_data[_str_high_price_column_name ].shift(2),
                                            'HigherHigh',
                                            _df_data['ShortLowerHighLowerLow'])
    
    df_fx['ShortLowerHighLowerLow'] = np.where(_df_data[_str_high_price_column_name ].shift(1) < _df_data[_str_high_price_column_name ].shift(2),
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


#%% GET_EXIT_PRICE_BASED_ON_TRAILING_STOP
def GET_EXIT_PRICE_BASED_ON_TRAILING_STOP(_df_data = None,
                                         _str_high_price_column_name : (str) = None,
                                         _str_low_price_column_name : (str) = None,
                                         _str_trade_direction_column_name : (str) = None,
                                         _str_column_name_LongStopLossRelativetoOpenPrice: (str) = None,
                                         _str_column_name_ShortStopLossRelativetoOpenPrice: (str) = None):
        
    
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
    
    _df_data['LongHigherHighHigherLow'] = np.where(_df_data[_str_low_price_column_name].shift(1) > _df_data[_str_low_price_column_name].shift(2),
                                            'HigherLow',
                                            _df_data['LongHigherHighHigherLow'])
    
    _df_data['LongHigherHighHigherLow'] = np.where(_df_data[_str_low_price_column_name].shift(1) < _df_data[_str_low_price_column_name].shift(2),
                                            'LowerLow',
                                            _df_data['LongHigherHighHigherLow'])
    
    
    _df_data['ShortLowerHighLowerLow'] = np.where(_df_data[_str_high_price_column_name].shift(1) > _df_data[_str_low_price_column_name].shift(2),
                                            'HigherHigh',
                                            _df_data['ShortLowerHighLowerLow'])
    
    _df_data['ShortLowerHighLowerLow'] = np.where(_df_data[_str_high_price_column_name].shift(1) < _df_data[_str_high_price_column_name].shift(2),
                                            'LowerHigh',
                                            _df_data['ShortLowerHighLowerLow'])
    
    
    _columns = ['LongHigherHighHigherLow','ShortLowerHighLowerLow']
    
    _df_data[_columns] = _df_data[_columns].mask(_df_data == 'nan', np.nan).ffill()
    
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
    
    return pd.Series(df_fx['TradeDirection'])
    
#%% Main function

def _func_get_exit_price(_df_data = None,
                        _str_open_price_column_name = None,
                        _str_high_price_column_name = None,
                        _str_low_price_column_name = None,
                        _str_close_price_column_name = None,
                        _str_stoploss_rate_column_name = None,
                        _str_takeprofit_rate_column_name = None,
                        _str_trade_direction_column_name = None):

    
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
                                                    _str_high_price_column_name   = 'High',
                                                    _str_low_price_column_name  = 'Low',
                                                    _str_trade_direction_column_name  = 'TradeDirection',
                                                    _str_column_name_LongStopLossRelativetoOpenPrice = 'LongStopLossRelativetoOpenPrice',
                                                    _str_column_name_ShortStopLossRelativetoOpenPrice = 'ShortStopLossRelativetoOpenPrice')
    
    
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

    
    _df_data = _df_data.drop(columns = ['LongHigherHighHigherLow',
                                        'ShortLowerHighLowerLow',
                                        'TrailingHighLowDirection',
                                        'FutureStopLossPrice', 'TrailingStopLoss'], 
                             axis = 1)
    
    return _df_data



#%% Testing

if __name__ == '__main__':
    #%% Download data
    _df_data = etl._function_extract(_str_valuedate_start = '1/1/2010',
                                     _str_valuedate_end = '12/31/2010',
                                     _str_resample_frequency = 'D')
    
    
    #%% Create a simulated trade based on random number generation between 0 & 2
    _df_data['TradeDirection'] = GENERATE_RANDOM_TRADE_DIRECTION(_df_data = _df_data)
    
    
    #%% Set the take profit and stoploss rate
    _df_data['TakeProfitRate'] = 0.02
    _df_data['StoplossRate'] = 0.01
    

    #%% Generate exit price
    _df_data = _func_get_exit_price(_df_data = _df_data,
                                    _str_open_price_column_name = 'Open',
                                    _str_high_price_column_name = 'High',
                                    _str_low_price_column_name = 'Low',
                                    _str_close_price_column_name = 'Close',
                                    _str_stoploss_rate_column_name = 'StoplossRate',
                                    _str_takeprofit_rate_column_name = 'TakeProfitRate',
                                    _str_trade_direction_column_name = 'TradeDirection') 

    
    _df_data.to_csv('Output.csv')

    #%% Create a plotly plot that shows the fx price together with the volatility

    _obj_fig = make_subplots(rows = 1, cols=1, shared_xaxes=True)


    _obj_fig.add_trace(go.Candlestick(
                                        x = _df_data.index,
                                        open = _df_data.Open,
                                        high = _df_data.High,
                                        low = _df_data.Low,
                                        close = _df_data.Close
                                        ),
                        row = 1,
                        col=1
                        )


    for _int_row_number in range(_df_data.shape[0]):
        

        _str_trade_direction = _df_data['TradeDirection'][_int_row_number]
        
        if ( _str_trade_direction == 'Long' or _str_trade_direction == 'Short'):
            
            _date_x_axis_head = _df_data['ExitDate'][_int_row_number]
            _int_y_axis_head = _df_data['ExitPrice'][_int_row_number]
            _date_x_axis_tail = _df_data.index[_int_row_number]
            _int_y_axis_tail = _df_data['Open'][_int_row_number]
            
            
            
            print(f"_date_x_axis_head {_date_x_axis_head}")
            print(f"_int_y_axis_head {_int_y_axis_head}")
            print(f"_date_x_axis_tail {_date_x_axis_tail}")
            print(f"_int_y_axis_tail {_int_y_axis_tail}")

            if _str_trade_direction == 'Long' and _int_y_axis_tail > 0  and _int_y_axis_head != np.nan:
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
                
    
    _df_data['StoplossPrice'] = np.where(_df_data['TradeDirection'] == 'Long',
                                         _df_data['LongStopLossRelativetoOpenPrice'],
                                         np.where(_df_data['TradeDirection'] == 'Short',
                                                  _df_data['ShortStopLossRelativetoOpenPrice'],
                                                  np.nan
                                                )
                                        )

    _obj_fig.add_trace(go.Scatter(x=_df_data.index, 
                                    y=_df_data['StoplossPrice'],
                                    mode='markers',
                                    name='markers')
                        )
    
    _obj_fig.add_trace(go.Scatter(x=_df_data.index, 
                                y=_df_data['TakeProfitPrice'],
                                mode='markers',
                                name='markers')
                        )

    _obj_fig.update_layout(xaxis_rangeslider_visible=False)

    pio.renderers.default = 'browser'

    pio.show(_obj_fig)


# %%
