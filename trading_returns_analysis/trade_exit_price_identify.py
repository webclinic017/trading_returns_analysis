
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

#%%
def GENERATE_FIX_STOP_LOSS_PRICE(df_data = None,
                                str_stoploss_rate_column_name: (float) = None,
                                str_column_name_trade_direction: str = None,
                                str_open_price_column_name = None):
    """s
    Description
    ----
        This function allows you to set a fix rate relative to the open price as the stoploss

    Args:
        df_data ([type], optional): [description]. Defaults to None.
        str_stoploss_rate_column_name ([type], optional): [description]. Defaults to None.
        str_column_name_tradedirection (str, optional): [description]. Defaults to None.

    Returns:
        [type]: [description]
    """

    
    df_data['StopLossPrice'] = np.nan
    df_data['StopLossPrice'] = np.where(df_data[str_column_name_trade_direction] =='Long',
                                            df_data[str_open_price_column_name] * (1 - df_data[str_stoploss_rate_column_name]),
                                            df_data['StopLossPrice']
                                            )
                                            
    df_data['StopLossPrice'] = np.where(df_data[str_column_name_trade_direction] =='Short',
                                          df_data[str_open_price_column_name] * (1 + df_data[str_stoploss_rate_column_name]),
                                          df_data['StopLossPrice']
                                        )
    
    return pd.Series(df_data['StopLossPrice'])



#%%


def TRAILING_STOPLOSS(pdSeries_future_high_price = None,
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

#%% GET_EXIT_PRICE_BASED_ON_TRAILING_STOP
def GET_EXIT_PRICE_BASED_ON_TRAILING_STOP(df_data = None,
                                         str_high_price_column_name : (str) = None,
                                         str_low_price_column_name : (str) = None,
                                         str_trade_direction_column_name : (str) = None,
                                         str_future_stoploss_column: (str) = None):
    
    
    
    df_data['TrailingStoplossExitPrice'] = np.nan
    df_data['TrailingExitStopLossDate'] = pd.NaT
    df_data['TrailingHighLowDirection'] = pd.NA
    df_data['TrailingStopLoss'] = pd.NA
    
    df_data['Boolean_Condition'] = pd.NA
    bool_condition = []
    
    int_row_lenght = df_data.shape[0]
    
    for int_row_num in range(int_row_lenght):
        
        str_trade_direction = df_data[str_trade_direction_column_name][int_row_num]
        
        if str_trade_direction in ['Long','Short']:
            
            nparray_future_stoploss = df_data[str_future_stoploss_column][int_row_num]
            pdseries_future_low = df_data[str_low_price_column_name].ffill()[int_row_num : int_row_lenght]
            pdseries_future_high = df_data[str_high_price_column_name].ffill()[int_row_num : int_row_lenght]

            
        
            
            pdseries_trailing_stoploss = TRAILING_STOPLOSS(pdSeries_future_high_price = pdseries_future_high,
                                                            pdSeries_future_low_price = pdseries_future_low,
                                                            pdSeries_future_stoploss = nparray_future_stoploss,
                                                            str_trade_direction = str_trade_direction )                                          
            
            nparray_future_low = np.array(pdseries_future_low, dtype = float)
            nparray_future_high = np.array(pdseries_future_high, dtype = float)
            nparray_trailing_stoploss = np.array(pdseries_trailing_stoploss, dtype = float)
            
            if str_trade_direction == 'Long':
                bool_condition = np.where( list(pdseries_future_low  <= pdseries_trailing_stoploss),
                                            True,
                                            False)
                
            elif str_trade_direction == 'Short':
                bool_condition = np.where(  list(pdseries_future_high >= pdseries_trailing_stoploss) ,
                                            True,
                                            False)
            
            try: 
                float_trailing_exit_price = np.array(pdseries_trailing_stoploss)[bool_condition][0]
                datetime_trailing_exit_date = pdseries_future_high.index[bool_condition][0]
                
            except:
                float_trailing_exit_price = np.nan
                datetime_trailing_exit_date = np.nan
            

            df_data['TrailingStopLoss'][int_row_num] = np.array(pdseries_trailing_stoploss).astype(object)
            
            df_data['TrailingStoplossExitPrice'][int_row_num] = float_trailing_exit_price
            df_data['TrailingExitStopLossDate'][int_row_num] = datetime_trailing_exit_date
            
            df_data['Boolean_Condition'][int_row_num] = np.array(bool_condition,dtype = bool)
    
    return df_data


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

#%% Generate future stop loss based on the stop loss rate for a specific period

def func_generate_future_stoploss(df_data = None,
                                  str_open_price_column_name = None,
                                  str_stoploss_rate_column_name = None,
                                  str_trade_direction_column_name = None):
    
    int_number_of_rows = df_data.shape[0]
    
    
    list_output = []
    for int_index in range(int_number_of_rows):
        float_stoploss_rate = df_data[str_stoploss_rate_column_name][int_index]
        str_trade_direction = df_data[str_trade_direction_column_name][int_index]
        list_future_open_price = df_data[str_open_price_column_name][int_index:int_number_of_rows]
        
        if str_trade_direction == 'Long':
            list_future_stoploss = (1 - float_stoploss_rate) * list_future_open_price
        elif str_trade_direction == 'Short':
            list_future_stoploss = (1 + float_stoploss_rate) * list_future_open_price
        else:
            list_future_stoploss = []
            
        list_output.append(np.array(list_future_stoploss,dtype=object))
        
    return list_output

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


#%% Main function

def _func_get_exit_price(df_data = None,
                        str_open_price_column_name = None,
                        str_high_price_column_name = None,
                        str_low_price_column_name = None,
                        str_close_price_column_name = None,
                        str_stoploss_rate_column_name = None,
                        str_takeprofit_rate_column_name = None,
                        str_trade_direction_column_name = None):

    
    df_data['TakeProfitPrice'] = GENERATE_FIX_TAKE_PROFIT_PRICE(  _df_data = df_data,
                                                                _str_takeprofit_rate_column_name =  str_takeprofit_rate_column_name,
                                                                _str_column_name_trade_direction = str_trade_direction_column_name,
                                                                _str_open_price_column_name = str_open_price_column_name )
    
    
    df_data['StopLossPrice'] = GENERATE_FIX_STOP_LOSS_PRICE(df_data = df_data,
                                                                str_stoploss_rate_column_name  = str_stoploss_rate_column_name,
                                                                str_column_name_trade_direction = str_trade_direction_column_name,
                                                                str_open_price_column_name = str_open_price_column_name)
    
    df_data['FutureStoploss'] = func_generate_future_stoploss(df_data = df_data,
                                                                str_open_price_column_name = str_open_price_column_name,
                                                                str_stoploss_rate_column_name = str_stoploss_rate_column_name,
                                                                str_trade_direction_column_name = str_trade_direction_column_name)
    

    #%% Get exit price based on trailing stop

    df_data = GET_EXIT_PRICE_BASED_ON_TRAILING_STOP(df_data = df_data,
                                                    str_high_price_column_name   = str_high_price_column_name,
                                                    str_low_price_column_name  = str_low_price_column_name,
                                                    str_trade_direction_column_name  = str_trade_direction_column_name,
                                                    str_future_stoploss_column = 'FutureStoploss')
    
    
   
    #%% Identify Static Take Profit Hit Date

    df_data = GET_TAKE_PROFIT_AND_DATE(_df_data = df_data,
                                        _str_high_price_column_name = str_high_price_column_name,
                                        _str_low_price_column_name = str_low_price_column_name,
                                        _str_column_name_TakeProfitPrice = 'TakeProfitPrice',
                                        _str_column_name_TradeDirection = str_trade_direction_column_name)

    
    #%% Generate an exit price based on which was triggered first, is it the stoploss or the take profit

    df_data = GENERATE_FINAL_EXIT_PRICE(_df_data = df_data,
                                        _str_column_name_TakeProfitHitDate = 'TakeProfitHitDate',
                                        _str_column_name_TakeProfitPrice = 'TakeProfitPrice',
                                        _str_column_name_TrailingExitStopLossDate = 'TrailingExitStopLossDate',
                                        _str_column_name_TrailingStoplossExitPrice = 'TrailingStoplossExitPrice')

    
    df_data = GENERATE_FUTURE_OPEN_HIGH_LOW_CLOSE_DATE_COLUMN(df_data = df_data.reset_index(),
                                                                str_open_price_column_name = str_open_price_column_name,
                                                                str_high_price_column_name = str_high_price_column_name,
                                                                str_low_price_column_name = str_low_price_column_name,
                                                                str_close_price_column_name = str_close_price_column_name,
                                                                str_date_column_name = 'DateTime')
    
    df_data['DateTime'] = df_data['DateTime'].astype('datetime64[ns]')
    df_data = df_data.set_index('DateTime')
    
    
    
    return df_data



#%%#%% Testing

if __name__ == '__main__':
    #%% Download data
    df_data = etl._function_extract(_str_valuedate_start = '1/1/2018',
                                     _str_valuedate_end = '12/31/2018',
                                     _str_resample_frequency = 'D')
    
    
    #%% Create a simulated trade based on random number generation between 0 & 2
    df_data['TradeDirection'] = GENERATE_RANDOM_TRADE_DIRECTION(_df_data = df_data)
    
    
    #%% Set the take profit and stoploss rate
    df_data['TakeProfitRate'] = 0.02
    df_data['StoplossRate'] = 0.01
    

    #%% Generate exit price
    df_data = _func_get_exit_price(df_data = df_data,
                                    str_open_price_column_name = 'Open',
                                    str_high_price_column_name = 'High',
                                    str_low_price_column_name = 'Low',
                                    str_close_price_column_name = 'Close',
                                    str_stoploss_rate_column_name = 'StoplossRate',
                                    str_takeprofit_rate_column_name = 'TakeProfitRate',
                                    str_trade_direction_column_name = 'TradeDirection') 

#%%
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
                
    


    _obj_fig.add_trace(go.Scatter(x=df_data.index, 
                                    y=df_data['StopLossPrice'],
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
                                y=df_data.FutureStoploss,
                                mode='lines+markers',
                                name='FutureStoploss')
                    )
    
    obj_fig.update_layout(xaxis_rangeslider_visible=False)

    pio.renderers.default = 'browser'

    return pio.show(obj_fig)



# %% test if the trailing stop loss are correct

str_date = '2018-09-24'
df_temp = df_data.loc[str_date:str_date,:]

df_temp2 = df_temp.apply(lambda x: x.explode() if x.name in ['TrailingHighLowDirection','FutureStoploss','TrailingStopLoss','FutureOpenPrice','FutureHighPrice','FutureLowPrice','FutureClosePrice','FutureDate'] else x)
df_temp2['FutureDate'] = df_temp2['FutureDate'].astype('datetime64[ns]')

PLOT_SINGLE_TRADE_TRAILING_STOPLOSS_AND_TAKEPROFIT(df_data = df_temp2)

print(df_temp2.head(10))
# %%
