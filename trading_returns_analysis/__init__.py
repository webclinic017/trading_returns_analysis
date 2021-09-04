# -*- coding: utf-8 -*-
__doc__ =  """
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
import plotly.graph_objects as go
import plotly.io as pio
from plotly.subplots import make_subplots

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

def CUMULATIVE_AND_ROLLING_KELLY_CRITERION(df_data = None,
                                            str_SingleTradePercentageChange_column_name: (str) = None,
                                            boolean_apply_rolling_periods_True_or_False: (bool) = True):
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
    
    AssertionError(type(df_data.index) == pd.core.indexes.datetimes.DatetimeIndex,
                   ''''Please set the date as your index. 
                   If your index is already a the date, make sure to set the data type to data.index.astype(datetime64[ns])''')
    

    #Create a cumulative win rate column and formula
    df_data['KellyCriterionCumulative'] = df_data[str_SingleTradePercentageChange_column_name].expanding().apply(lambda x: KELLY_FORMULA(x) )
    
    if boolean_apply_rolling_periods_True_or_False == True:
        #Create a rolling  win rate
        list_int_frequency_days = [7,30,60,90,180,365]
        for int_frequency in list_int_frequency_days:
            df_data[f'KellyCriterion{int_frequency}DaysRolling'] = df_data[str_SingleTradePercentageChange_column_name].rolling(f'{int_frequency}D').apply(lambda x: KELLY_FORMULA(x) )

  
    return df_data

#%% Create new column that will determine the cumulative risk and return and the rolling win rate

def CUMULATIVE_AND_ROLLING_RISK_TO_RETURN_RATIO(df_data = None,
                                                str_SingleTradePercentageChange_column_name: (str) = None,
                                                boolean_apply_rolling_periods_True_or_False: (bool) = True):
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
    
    AssertionError(type(df_data.index) == pd.core.indexes.datetimes.DatetimeIndex,
                   ''''Please set the date as your index. 
                   If your index is already a the date, make sure to set the data type to data.index.astype(datetime64[ns])''')
    
    
    
    #Create a cumulative win rate column and formula
    df_data['RiskReturnCumulative'] = df_data[str_SingleTradePercentageChange_column_name].expanding().apply(lambda x: np.sum(x[x>0]) / abs(np.sum(x[x<0])) )
    
    if boolean_apply_rolling_periods_True_or_False == True:
        #Create a rolling  win rate
        list_int_frequency_days = [7,30,60,90,180,365]
        for int_frequency in list_int_frequency_days:
            df_data[f'RiskReturn{int_frequency}DaysRolling'] = df_data[str_SingleTradePercentageChange_column_name].rolling(f'{int_frequency}D').apply(lambda x: np.sum(x[x>0]) / abs(np.sum(x[x<0])) )

    return df_data


#%% Create new column that will determine the cumulative win rate and the rolling win rate

def CUMULATIVE_AND_ROLLING_WIN_RATE(df_data = None,
                                    str_SingleTradePercentageChange_column_name: (str) = None,
                                     boolean_apply_rolling_periods_True_or_False: (bool) = False):
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
    
    AssertionError(type(df_data.index) == pd.core.indexes.datetimes.DatetimeIndex,
                   ''''Please set the date as your index. 
                   If your index is already a the date, make sure to set the data type to data.index.astype(datetime64[ns])''')
    
    
    
    #Create a cumulative win rate column and formula
    df_data['WinRateCumulative'] = df_data[str_SingleTradePercentageChange_column_name].expanding().apply(lambda x: np.sum(x>0) / np.sum(~np.isnan(x)) )
    
    if boolean_apply_rolling_periods_True_or_False == True:
        #Create a rolling  win rate
        list_int_frequency_days = [7,30,60,90,180,365]
        for int_frequency in list_int_frequency_days:
            df_data[f'WinRate{int_frequency}DaysRolling'] = df_data[str_SingleTradePercentageChange_column_name].rolling(f'{int_frequency}D').apply(lambda x: np.sum(x>0) / np.sum(~np.isnan(x)) )

    return df_data


#%%
def CLOSED_TRADES_PERCENTAGE_CHANGE(df_data = None,
                     str_column_trade_entry_price_column_name: (str) = None,
                     str_column_trade_direction_column_name: (str) = None,
                     str_column_trade_exit_price_column_name: (str) = None):
    
    # Get the percentage change between the exit price and the entry price

    
    df_data['SingleTradePercentageChange'] = (df_data[str_column_trade_exit_price_column_name].astype('float64') /
                                           df_data[str_column_trade_entry_price_column_name].astype('float64')
                                           - 1
                                           )
 
        
    df_data['SingleTradePercentageChange'] = np.where(df_data[str_column_trade_direction_column_name] == 'Short',
                                                   df_data['SingleTradePercentageChange'] * -1,
                                                   df_data['SingleTradePercentageChange'])
    
    # Generate Cumulative Return
    
    df_data['CumulativeReturn'] = df_data['SingleTradePercentageChange'].expanding().apply(lambda x: np.prod(1+x)-1)
    
    df_data['Rolling30DReturn'] = df_data['SingleTradePercentageChange'].rolling('30D').apply(lambda x: np.prod(1+x)-1)
    
    df_data['Rolling3MReturn'] = df_data['SingleTradePercentageChange'].rolling('90D').apply(lambda x: np.prod(1+x)-1)
    
    df_data['Rolling6MReturn'] = df_data['SingleTradePercentageChange'].rolling('180D').apply(lambda x: np.prod(1+x)-1)
    
    df_data['Rolling9MReturn'] = df_data['SingleTradePercentageChange'].rolling('270D').apply(lambda x: np.prod(1+x)-1)
    
    return df_data



#%%


def func_list_int_generate_trade_duration(df_data = None,
                                        str_exit_date_column_name = None,
                                        str_entry_date_column_name = None):
    list_int_generate_trade_duration = (df_data[str_exit_date_column_name] - df_data.index).dt.days
    
    return list_int_generate_trade_duration


        
#%%

def func_df_generate_returns_analysis(df_data = None,
                                str_column_trade_entry_price_column_name = None,
                                str_column_trade_direction_column_name = None,
                                str_column_trade_exit_price_column_name = None,
                                str_column_trade_exit_date_column_name = None
                            ):
    
    df_data = CLOSED_TRADES_PERCENTAGE_CHANGE(df_data = df_data,
                                                str_column_trade_entry_price_column_name = str_column_trade_entry_price_column_name,
                                                str_column_trade_direction_column_name = str_column_trade_direction_column_name,
                                                str_column_trade_exit_price_column_name = str_column_trade_exit_price_column_name)
    
    
    df_data = CUMULATIVE_AND_ROLLING_WIN_RATE(df_data = df_data,
                                            str_SingleTradePercentageChange_column_name = 'SingleTradePercentageChange',
                                            boolean_apply_rolling_periods_True_or_False = True)
    
    df_data = CUMULATIVE_AND_ROLLING_RISK_TO_RETURN_RATIO(df_data = df_data,
                                                        str_SingleTradePercentageChange_column_name = 'SingleTradePercentageChange',
                                                        boolean_apply_rolling_periods_True_or_False = True)
    
    df_data = CUMULATIVE_AND_ROLLING_KELLY_CRITERION(df_data = df_data,
                                                        str_SingleTradePercentageChange_column_name = 'SingleTradePercentageChange',
                                                        boolean_apply_rolling_periods_True_or_False = True)
    
    df_data['TradeDuration'] = func_list_int_generate_trade_duration(df_data = df_data,
                                                                     str_exit_date_column_name = str_column_trade_exit_date_column_name,
                                                                     str_entry_date_column_name = df_data.index.name)
    return df_data


#%%
def func_plotlychart_generate_chart(df_data = None,
                                    str_cumulative_return_column_name = None,
                                    str_cumulative_win_rate_column_name = None,
                                    str_cumulative_risk_return_column_name = None,
                                    str_cumulative_kelly_criterion_column_name = None,
                                    bool_merge_plotly_chart_with_other_chart_True_or_False = False,
                                    class_trading_exit_price = None):

    
    if bool_merge_plotly_chart_with_other_chart_True_or_False == True:
        int_additional_row_plotly_chart  = 1
        obj_fig = class_trading_exit_price.generate_plotly_chart_showing_stoploss_and_takeprofit(bool_merge_plotly_chart_with_other_chart_True_or_False = True)
        
    else:
        int_additional_row_plotly_chart = 0
        obj_fig = make_subplots(rows = 4 , cols=1, shared_xaxes=True)
    
    
    

    obj_fig.add_trace(go.Scatter(x=df_data.index, 
                                y=df_data[str_cumulative_return_column_name],
                                mode='lines',
                                name='Cumulative Return'),
                    row = 1 + int_additional_row_plotly_chart,
                    col = 1
                    )

    obj_fig.add_trace(go.Scatter(x=df_data.index, 
                                y=df_data[str_cumulative_win_rate_column_name],
                                mode='lines',
                                name='WinRateCumulative'),
                    row = 2 + int_additional_row_plotly_chart,
                    col = 1
                    )

    obj_fig.add_trace(go.Scatter(x=df_data.index, 
                                y=df_data[str_cumulative_risk_return_column_name],
                                mode='lines',
                                name='RiskReturnCumulative'),
                    row = 3 + int_additional_row_plotly_chart,
                    col = 1
                    )

    obj_fig.add_trace(go.Scatter(x=df_data.index, 
                                y=df_data[str_cumulative_kelly_criterion_column_name],
                                mode='lines',
                                name='KellyCriterionCumulative'),
                    row = 4 + int_additional_row_plotly_chart,
                    col = 1
                    )
    obj_fig.update_layout(  xaxis_rangeslider_visible=False,
                            autosize=False,
                            width=2000,
                            height=3000)
    pio.renderers.default = 'browser'
    pio.show(obj_fig)
    
    return None

# %%

# %%


if __name__ == '__main__':
    
    from asset_price_etl import etl_fx_histadata_001 as etl
    import trading_exit_price as tep
    from trading_direction import func_list_str_generate_random_trades as td

    
    df_data = etl._function_extract(_str_valuedate_start = '1/1/2018',
                                     _str_valuedate_end = '12/7/2018',
                                     _str_resample_frequency = 'D')
    
    #%% Create a simulated trade based on random number generation between 0 & 2
    df_data['TradeDirection'] = td.func_list_str_generate_random_trades(df_data)
    
    df_data['TakeProfitRate'] = 0.005
    df_data['StoplossRate'] = 0.005
    
    class_tep = tep.trading_exit_price( df_data = df_data,
                                    str_open_price_column_name = 'Open',
                                    str_high_price_column_name = 'High',
                                    str_low_price_column_name = 'Low',
                                    str_close_price_column_name = 'Close',
                                    str_stoploss_rate_column_name = 'StoplossRate',
                                    str_takeprofit_rate_column_name = 'TakeProfitRate',
                                    str_trade_direction_column_name = 'TradeDirection',
                                    str_stoploss_fix_or_variable = 'fix',
                                    bool_exit_price_and_exit_date_only_True_or_False = False)
    
    df_data = class_tep.df_data

    class_tep.generate_plotly_chart_showing_stoploss_and_takeprofit()
    
    class_tep.generate_plot_single_trade_trailing_stoploss_and_takeprofit(str_date = '2018-08-02')

    
    df_data = func_df_generate_returns_analysis(df_data = df_data,
                                                str_column_trade_entry_price_column_name = 'Open',
                                                str_column_trade_direction_column_name = 'TradeDirection',
                                                str_column_trade_exit_price_column_name = 'ExitPrice',
                                                str_column_trade_exit_date_column_name = 'ExitDate'
                                                )
    
    func_plotlychart_generate_chart(df_data = df_data,
                                    str_cumulative_return_column_name = 'CumulativeReturn',
                                    str_cumulative_win_rate_column_name = 'WinRateCumulative',
                                    str_cumulative_risk_return_column_name = 'RiskReturnCumulative',
                                    str_cumulative_kelly_criterion_column_name = 'KellyCriterionCumulative',
                                    bool_merge_plotly_chart_with_other_chart_True_or_False = True,
                                    class_trading_exit_price = class_tep
                                    )
