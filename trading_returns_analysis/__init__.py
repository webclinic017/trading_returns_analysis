# -*- coding: utf-8 -*-
__version__ = '3.2.1'
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
import trading_exit_price as tep
import sqlserverconnection as sc
from datetime import datetime
import __main__ as main

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
            try:
                df_data[f'KellyCriterion{int_frequency}DaysRolling'] = df_data[str_SingleTradePercentageChange_column_name].rolling(f'{int_frequency}D').apply(lambda x: KELLY_FORMULA(x) )
            except ValueError:
                df_data[f'KellyCriterion{int_frequency}DaysRolling'] = np.nan
  
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
            try:
                df_data[f'RiskReturn{int_frequency}DaysRolling'] = df_data[str_SingleTradePercentageChange_column_name].rolling(f'{int_frequency}D').apply(lambda x: np.sum(x[x>0]) / abs(np.sum(x[x<0])) )
            except ValueError:
                df_data[f'RiskReturn{int_frequency}DaysRolling'] = np.nan
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
            try:
                df_data[f'WinRate{int_frequency}DaysRolling'] = df_data[str_SingleTradePercentageChange_column_name].rolling(f'{int_frequency}D').apply(lambda x: np.sum(x>0) / np.sum(~np.isnan(x)) )
            except ValueError:
                df_data[f'WinRate{int_frequency}DaysRolling'] = np.nan
                
    return df_data


#%%
def CLOSED_TRADES_PERCENTAGE_CHANGE(df_data = None,
                     str_column_trade_entry_price_column_name: (str) = None,
                     str_column_trade_direction_column_name: (str) = None,
                     str_column_trade_exit_price_column_name: (str) = None,
                     str_column_trade_exit_date_column_name: str = None):
    
    # Get the percentage change between the exit price and the entry price

    
    df_data['SingleTradePercentageChange'] = (df_data[str_column_trade_exit_price_column_name].astype('float64') /
                                           df_data[str_column_trade_entry_price_column_name].astype('float64')
                                           - 1
                                           )
 
        
    df_data['SingleTradePercentageChange'] = np.where(df_data[str_column_trade_direction_column_name] == 'Short',
                                                   df_data['SingleTradePercentageChange'] * -1,
                                                   df_data['SingleTradePercentageChange'])
    
    #df_data['SingleTradePercentageChange'] = df_data['SingleTradePercentageChange'].shift(int_future_closing_lag_number_of_days)
    
    df_data['CumulativeReturn'] = None
    for int_row_number in range(df_data.shape[0]):
        nparray_single_trade_percentage_change = np.where(df_data.index[int_row_number] > df_data[str_column_trade_exit_date_column_name][0:int_row_number],
                                                            df_data['SingleTradePercentageChange'][0:int_row_number],
                                                            0)
        df_data['CumulativeReturn'][int_row_number] = np.prod(1 + nparray_single_trade_percentage_change) - 1

    try:
        df_data['Rolling30DReturn'] = df_data['SingleTradePercentageChange'].rolling('30D').apply(lambda x: np.prod(1+x)-1)
        
        df_data['Rolling3MReturn'] = df_data['SingleTradePercentageChange'].rolling('90D').apply(lambda x: np.prod(1+x)-1)
        
        df_data['Rolling6MReturn'] = df_data['SingleTradePercentageChange'].rolling('180D').apply(lambda x: np.prod(1+x)-1)
        
        df_data['Rolling9MReturn'] = df_data['SingleTradePercentageChange'].rolling('270D').apply(lambda x: np.prod(1+x)-1)
    except ValueError:
        df_data['Rolling30DReturn'] = np.nan
        df_data['Rolling3MReturn'] = np.nan
        df_data['Rolling6MReturn'] = np.nan
        df_data['Rolling9MReturn'] = np.nan
    
    return df_data



#%%


def func_list_int_generate_trade_duration(df_data = None,
                                        str_exit_date_column_name = None,
                                        str_entry_date_column_name = None):
    list_int_generate_trade_duration = (df_data[str_exit_date_column_name] - df_data.index).dt.days
    
    return list_int_generate_trade_duration

#%%
def func_pdseries_int_cumulative_balance_usd(df_data = None,
                                                int_initial_balance_in_usd = None,
                                                float_percent_risk_per_trade = None,
                                                str_SingleTradePercentageChange_column_name = None,
                                                str_StoplossRate_column_name = None,
                                                str_KellyCriterionCumulative_column_name = None,
                                                bool_appy_kelly_criterion_True_or_False = None,
                                                float_kelly_criterion_multiplier = None):


    df_data = df_data.copy()
    df_data = df_data[[str_StoplossRate_column_name,str_SingleTradePercentageChange_column_name,str_KellyCriterionCumulative_column_name]]
    
    df_data[str_SingleTradePercentageChange_column_name] = np.where(np.isnan(df_data[str_SingleTradePercentageChange_column_name]),
                                                                    0,
                                                                    df_data[str_SingleTradePercentageChange_column_name]
                                                                    )
    
    df_data[str_KellyCriterionCumulative_column_name] = np.where(np.isinf(df_data[str_KellyCriterionCumulative_column_name]),
                                                                0,
                                                                df_data[str_KellyCriterionCumulative_column_name]
                                                                )
    
    df_data[str_KellyCriterionCumulative_column_name] = np.where(df_data[str_SingleTradePercentageChange_column_name] == 0,
                                                                0,
                                                                df_data[str_KellyCriterionCumulative_column_name]
                                                                )
    df_data['CumulativeBalance'] = np.nan

    for int_row in range(df_data.shape[0]):
        float_stoploss_rate = df_data[str_StoplossRate_column_name][int_row]
        float_exit_rate = df_data[str_SingleTradePercentageChange_column_name][int_row]
        float_kelly_criterion = df_data[str_KellyCriterionCumulative_column_name][int_row]
        
        if float_kelly_criterion < -1:
            float_kelly_criterion = -1
        
        if int_row == 0:
            int_previous_balance = int_initial_balance_in_usd
        else:
            int_previous_balance = df_data.CumulativeBalance[int_row - 1]
        
        if bool_appy_kelly_criterion_True_or_False == True:
            float_kelly_criterion = float_kelly_criterion * float_kelly_criterion_multiplier
            float_kelly_criterion = 1 + float_kelly_criterion
        else:
            float_kelly_criterion = 1
        
        
        df_data.CumulativeBalance[int_row] = ( (int_previous_balance * float_percent_risk_per_trade * float_kelly_criterion) 
                                            / float_stoploss_rate
                                            * float_exit_rate 
                                            ) + int_previous_balance
        
    return pd.Series(df_data.CumulativeBalance)
        
#%%

def func_df_generate_returns_analysis(  df_data = None,
                                        str_column_trade_entry_price_column_name = None,
                                        str_column_trade_direction_column_name = None,
                                        str_column_trade_exit_price_column_name = None,
                                        str_column_trade_exit_date_column_name = None,
                                        int_initial_balance_in_usd = None,
                                        float_percent_risk_per_trade = None,
                                        bool_appy_kelly_criterion_True_or_False = None,
                                        float_kelly_criterion_multiplier = None,
                                        class_trading_exit_price = None,
                                        bool_generate_plotly_chart_True_or_False = None
                                     ):
    
    df_data = CLOSED_TRADES_PERCENTAGE_CHANGE(df_data = df_data,
                                                str_column_trade_entry_price_column_name = str_column_trade_entry_price_column_name,
                                                str_column_trade_direction_column_name = str_column_trade_direction_column_name,
                                                str_column_trade_exit_price_column_name = str_column_trade_exit_price_column_name,
                                                str_column_trade_exit_date_column_name = str_column_trade_exit_date_column_name)
    
    
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
    
    df_data['CumulativeBalanceUSD'] = func_pdseries_int_cumulative_balance_usd( df_data = df_data,
                                                                                int_initial_balance_in_usd = int_initial_balance_in_usd,
                                                                                float_percent_risk_per_trade = float_percent_risk_per_trade,
                                                                                str_SingleTradePercentageChange_column_name = 'SingleTradePercentageChange',
                                                                                str_StoplossRate_column_name = 'StoplossRate',
                                                                                str_KellyCriterionCumulative_column_name = 'KellyCriterionCumulative',
                                                                                bool_appy_kelly_criterion_True_or_False = bool_appy_kelly_criterion_True_or_False,
                                                                                float_kelly_criterion_multiplier = float_kelly_criterion_multiplier)
    
    if bool_generate_plotly_chart_True_or_False != False:

        func_plotlychart_generate_chart(df_data = df_data,
                                    str_cumulative_return_column_name = 'CumulativeReturn',
                                    str_cumulative_win_rate_column_name = 'WinRateCumulative',
                                    str_cumulative_risk_return_column_name = 'RiskReturnCumulative',
                                    str_cumulative_kelly_criterion_column_name = 'KellyCriterionCumulative',
                                    str_CumulativeBalanceUSD_column_name = 'CumulativeBalanceUSD',
                                    bool_merge_plotly_chart_with_other_chart_True_or_False = True,
                                    class_trading_exit_price = class_trading_exit_price
                                    )
        
    return df_data


#%%
def func_plotlychart_generate_chart(df_data = None,
                                    str_cumulative_return_column_name = None,
                                    str_cumulative_win_rate_column_name = None,
                                    str_cumulative_risk_return_column_name = None,
                                    str_cumulative_kelly_criterion_column_name = None,
                                    str_CumulativeBalanceUSD_column_name = None,
                                    bool_merge_plotly_chart_with_other_chart_True_or_False = False,
                                    class_trading_exit_price = None):

    
    if bool_merge_plotly_chart_with_other_chart_True_or_False == True:
        int_additional_row_plotly_chart  = 1
        obj_fig = class_trading_exit_price.generate_plotly_chart_showing_stoploss_and_takeprofit(bool_merge_plotly_chart_with_other_chart_True_or_False = True, 
                                                                                                 int_number_of_subplots = 7)
        
    else:
        int_additional_row_plotly_chart = 0
        obj_fig = make_subplots(rows = 6 , cols=1, shared_xaxes=True)
    
    
    


    
    
    try:
        obj_fig.add_trace(go.Scatter(x=df_data.index, 
                                y=df_data['CumulativeReturnReverseIndicatorSMA'],
                                mode='lines',
                                name='Cumulative Return Reverse Indicator SMA'),
                    row = 1 + int_additional_row_plotly_chart,
                    col = 1
                    )
        
        obj_fig.add_trace(go.Scatter(x=df_data.index, 
                                y=df_data['CumulativeReturnOriginal'],
                                mode='lines',
                                name='CumulativeReturn Original'),
                    row = 1 + int_additional_row_plotly_chart,
                    col = 1
                    )
        
    except KeyError:
        pass


    obj_fig.add_trace(go.Scatter(x=df_data.index, 
                                y=df_data[str_cumulative_return_column_name],
                                mode='lines',
                                name='Cumulative Return'),
                    row = 2 + int_additional_row_plotly_chart,
                    col = 1
                    )
    
    obj_fig.add_trace(go.Scatter(x=df_data.index, 
                                y=df_data[str_CumulativeBalanceUSD_column_name],
                                mode='lines',
                                name='Cumulative Balance USD'),
                    row = 3 + int_additional_row_plotly_chart,
                    col = 1
                    )
        
    obj_fig.add_trace(go.Scatter(x=df_data.index, 
                                y=df_data[str_cumulative_win_rate_column_name],
                                mode='lines',
                                name='WinRateCumulative'),
                    row = 4 + int_additional_row_plotly_chart,
                    col = 1
                    )

    obj_fig.add_trace(go.Scatter(x=df_data.index, 
                                y=df_data[str_cumulative_risk_return_column_name],
                                mode='lines',
                                name='RiskReturnCumulative'),
                    row = 5 + int_additional_row_plotly_chart,
                    col = 1
                    )

    obj_fig.add_trace(go.Scatter(x=df_data.index, 
                                y=df_data[str_cumulative_kelly_criterion_column_name],
                                mode='lines',
                                name='KellyCriterionCumulative'),
                    row = 6 + int_additional_row_plotly_chart,
                    col = 1
                    )
    
    obj_fig.update_layout(  xaxis_rangeslider_visible=False,
                            autosize=False,
                            width=2000,
                            height=3000)
    
    pio.renderers.default = 'browser'
    pio.show(obj_fig)
    
    return None


def func_dict_pdseries_hold_or_reverse_trade_direction_based_on_rolling_trade_return(df_data = None,
                                                                                     str_CumulativeReturn_column_name = None,
                                                                                    str_TradeDirection_column_name = None,
                                                                                    str_StoplossRate_column_name = None,
                                                                                    str_TakeProfitRate_column_name = None,
                                                                                    bool_reverse_trade_direction_when_cumulative_return_trend_down_True_or_False = False,
                                                                                    str_rolling_return_sampling_duration = None,
                                                                                    bool_hold_trade_when_cumulative_return_trend_down_True_or_False = None,
                                                                                    bool_interchange_sl_and_tp_when_cumulative_return_trend_down_True_or_False = None,
                                                                                    bool_generate_plotly_chart_True_or_False = None):
        
        df_data = df_data.copy()
        
        df_data['CumulativeReturnOriginal'] = df_data.CumulativeReturn.copy()

        try:
            df_data['CumulativeReturnReverseIndicatorSMA'] = df_data.CumulativeReturn.rolling(str_rolling_return_sampling_duration).mean().fillna(0)
        except ValueError:
            print('In case of an error change the rolling period to either the conventional string or with an integer')
            print("Change the rolling period to any of these: 'D, 2D, 30D, M, 1, 2, 3")

        if bool_hold_trade_when_cumulative_return_trend_down_True_or_False == True:

            df_data[str_TradeDirection_column_name] = np.where( df_data[str_CumulativeReturn_column_name] > df_data.CumulativeReturnReverseIndicatorSMA,
                                                                df_data.TradeDirection,
                                                                'Hold'
                                                                )
            
        elif bool_reverse_trade_direction_when_cumulative_return_trend_down_True_or_False == True:
            df_data[str_TradeDirection_column_name] = np.where(( df_data[str_CumulativeReturn_column_name] > df_data.CumulativeReturnReverseIndicatorSMA),
                                    df_data.TradeDirection,
                                    np.where(df_data.TradeDirection == 'Long',
                                            'Short',
                                            np.where(df_data.TradeDirection == 'Short',
                                                    'Long',
                                                    df_data.TradeDirection)
                                            )
                                    )
            
        if bool_interchange_sl_and_tp_when_cumulative_return_trend_down_True_or_False == True:
            df_data['TakeProfitRateTemp'] = np.where((df_data.CumulativeReturn > 0 ) & ( df_data[str_CumulativeReturn_column_name] > df_data.CumulativeReturnReverseIndicatorSMA),
                                                df_data[str_TakeProfitRate_column_name],  
                                                df_data[str_StoplossRate_column_name]
                                                ) 
            df_data['StoplossRateTemp'] = np.where((df_data.CumulativeReturn > 0 ) & ( df_data[str_CumulativeReturn_column_name] > df_data.CumulativeReturnReverseIndicatorSMA),
                                                df_data[str_StoplossRate_column_name],  
                                                df_data[str_TakeProfitRate_column_name]
                                                ) 
            
            df_data[str_TakeProfitRate_column_name] = df_data['TakeProfitRateTemp'].copy()
            
            df_data[str_StoplossRate_column_name] = df_data['StoplossRateTemp'].copy()

            if bool_generate_plotly_chart_True_or_False != False:
                obj_fig = make_subplots(rows = 1 , cols=1, shared_xaxes=True)
                obj_fig.add_trace(go.Scatter(x=df_data.index, 
                                y=df_data['CumulativeReturn'],
                                mode='lines',
                                name='Cumulative Return'),
                    row = 1 ,
                    col = 1
                    )
                obj_fig.add_trace(go.Scatter(x=df_data.index, 
                                y=df_data['CumulativeReturnReverseIndicatorSMA'],
                                mode='lines',
                                name='Cumulative Return'),
                    row = 1 ,
                    col = 1
                    )
                obj_fig.update_layout(  xaxis_rangeslider_visible=False,
                            autosize=False,
                            width=1000,
                            height=500)
                pio.renderers.default = 'browser'
                pio.show(obj_fig)
    
    
        dict_output = {'TradeDirection':df_data[str_TradeDirection_column_name],
                       'TakeProfitRate': df_data[str_TakeProfitRate_column_name],
                       'StoplossRate': df_data[str_StoplossRate_column_name],
                       'CumulativeReturnReverseIndicatorSMA':df_data['CumulativeReturnReverseIndicatorSMA'],
                       'CumulativeReturnOriginal':df_data['CumulativeReturnOriginal']}
        
        return dict_output


def func_df_plotlychart_generate_returns_analysis(df_data = None,
                                                    str_column_trade_entry_price_column_name = None,
                                                    str_column_trade_direction_column_name = None,
                                                    int_initial_balance_in_usd = None,
                                                    float_percent_risk_per_trade = None,
                                                    bool_appy_kelly_criterion_True_or_False = None,
                                                    float_kelly_criterion_multiplier = None,
                                                    str_stoploss_fix_or_variable = None,
                                                    bool_apply_CumulativeReturnReverseIndicatorSMA_True_or_False = None,
                                                    str_rolling_return_sampling_duration_for_trade_hold_or_reverse = None,
                                                    bool_reverse_trade_direction_when_cumulative_return_trend_down_True_or_False = None,
                                                    bool_hold_trade_when_cumulative_return_trend_down_True_or_False = None,
                                                    bool_interchange_sl_and_tp_when_cumulative_return_trend_down_True_or_False = None,
                                                    str_other_trading_parameters_json_column_name = None,
                                                    str_timeframe_column_name = None,
                                                    str_broker_column_name = None,
                                                    str_strategy_name_column_name = None,
                                                    bool_generate_plotly_chart_True_or_False = None
                                                    ):
    
    assert(bool_hold_trade_when_cumulative_return_trend_down_True_or_False == bool_reverse_trade_direction_when_cumulative_return_trend_down_True_or_False,
          'The variables bool_reverse_trade_direction_when_cumulative_return_trend_down_True_or_False and bool_reverse_trade_direction_when_cumulative_return_trend_down_True_or_False cannot be the same.')


    df_data['InsertDateTime'] = datetime.today().strftime('%Y-%m-%d-%H:%M:%S')
    df_data['PythonFilePath'] = main.__file__

    list_trading_paramters_column = [str_timeframe_column_name
                                    ,str_broker_column_name
                                    ,str_strategy_name_column_name
                                    ,str_other_trading_parameters_json_column_name
                                    ,'InsertDateTime'
                                    ,'PythonFilePath']

    df_trading_parameters = df_data[list_trading_paramters_column].reset_index()
    df_trading_parameters['TradingParametersJSON'] = df_trading_parameters[str_other_trading_parameters_json_column_name].astype(str)

    df_data = df_data.copy()
    
    class_tep = tep.trading_exit_price( df_data = df_data,
                                str_open_price_column_name = 'Open',
                                str_high_price_column_name = 'High',
                                str_low_price_column_name = 'Low',
                                str_close_price_column_name = 'Close',
                                str_stoploss_rate_column_name = 'StoplossRate',
                                str_takeprofit_rate_column_name = 'TakeProfitRate',
                                str_trade_direction_column_name = 'TradeDirection',
                                str_stoploss_fix_or_variable = str_stoploss_fix_or_variable,
                                bool_exit_price_and_exit_date_only_True_or_False = False)

    df_data = class_tep.df_data
        
    df_data = func_df_generate_returns_analysis(df_data = df_data,
                                                str_column_trade_entry_price_column_name = str_column_trade_entry_price_column_name,
                                                str_column_trade_direction_column_name = str_column_trade_direction_column_name,
                                                str_column_trade_exit_price_column_name = 'ExitPrice',
                                                str_column_trade_exit_date_column_name = 'ExitDate',
                                                int_initial_balance_in_usd = int_initial_balance_in_usd,
                                                float_percent_risk_per_trade = float_percent_risk_per_trade,
                                                bool_appy_kelly_criterion_True_or_False = bool_appy_kelly_criterion_True_or_False,
                                                float_kelly_criterion_multiplier = float_kelly_criterion_multiplier,
                                                class_trading_exit_price = class_tep,
                                                bool_generate_plotly_chart_True_or_False = bool_generate_plotly_chart_True_or_False
                                                )
    

    
    if bool_apply_CumulativeReturnReverseIndicatorSMA_True_or_False == True:
 
        dict_output = func_dict_pdseries_hold_or_reverse_trade_direction_based_on_rolling_trade_return(df_data = df_data,
                                                                                                        str_CumulativeReturn_column_name = 'CumulativeReturn',
                                                                                                        str_TradeDirection_column_name = 'TradeDirection',
                                                                                                        str_StoplossRate_column_name = 'StoplossRate',
                                                                                                        str_TakeProfitRate_column_name = 'TakeProfitRate',
                                                                                                        bool_reverse_trade_direction_when_cumulative_return_trend_down_True_or_False = bool_reverse_trade_direction_when_cumulative_return_trend_down_True_or_False,
                                                                                                        str_rolling_return_sampling_duration = str_rolling_return_sampling_duration_for_trade_hold_or_reverse,
                                                                                                        bool_hold_trade_when_cumulative_return_trend_down_True_or_False = bool_hold_trade_when_cumulative_return_trend_down_True_or_False,
                                                                                                        bool_interchange_sl_and_tp_when_cumulative_return_trend_down_True_or_False = bool_interchange_sl_and_tp_when_cumulative_return_trend_down_True_or_False,
                                                                                                        bool_generate_plotly_chart_True_or_False = bool_generate_plotly_chart_True_or_False)
            
        df_data['TradeDirection'] = dict_output['TradeDirection']
        df_data['CumulativeReturnReverseIndicatorSMA'] = dict_output['CumulativeReturnReverseIndicatorSMA']
        df_data['CumulativeReturnOriginal'] = dict_output['CumulativeReturnOriginal']
                                                                        
        
        class_tep = tep.trading_exit_price( df_data = df_data,
                                        str_open_price_column_name = 'Open',
                                        str_high_price_column_name = 'High',
                                        str_low_price_column_name = 'Low',
                                        str_close_price_column_name = 'Close',
                                        str_stoploss_rate_column_name = 'StoplossRate',
                                        str_takeprofit_rate_column_name = 'TakeProfitRate',
                                        str_trade_direction_column_name = 'TradeDirection',
                                        str_stoploss_fix_or_variable = str_stoploss_fix_or_variable,
                                        bool_exit_price_and_exit_date_only_True_or_False = False)
        
        df_data = class_tep.df_data
        
        df_data = func_df_generate_returns_analysis(df_data = df_data,
                                                    str_column_trade_entry_price_column_name = str_column_trade_entry_price_column_name,
                                                    str_column_trade_direction_column_name = str_column_trade_direction_column_name,
                                                    str_column_trade_exit_price_column_name = 'ExitPrice',
                                                    str_column_trade_exit_date_column_name = 'ExitDate',
                                                    int_initial_balance_in_usd = int_initial_balance_in_usd,
                                                    float_percent_risk_per_trade = float_percent_risk_per_trade,
                                                    bool_appy_kelly_criterion_True_or_False = bool_appy_kelly_criterion_True_or_False,
                                                    float_kelly_criterion_multiplier = float_kelly_criterion_multiplier,
                                                    class_trading_exit_price = class_tep,
                                                    bool_generate_plotly_chart_True_or_False = bool_generate_plotly_chart_True_or_False
                                                    )

    #######################################################

    list_str_columns_to_be_uploaded_in_sql_database = [ 'Open', 
                                                        'High', 
                                                        'Low', 
                                                        'Close', 
                                                        #'Volume', 
                                                        'TradeDirection',
                                                        'TakeProfitRate', 
                                                        'StoplossRate', 
                                                        'TakeProfitPrice', 
                                                        'StopLossPrice',
                                                        'TakeProfitHitDate',
                                                        'ExitPrice', 
                                                        'ExitDate', 
                                                        'SingleTradePercentageChange', 
                                                        'CumulativeReturn', 
                                                        'Rolling30DReturn',
                                                        'Rolling3MReturn', 
                                                        'Rolling6MReturn', 
                                                        'Rolling9MReturn',
                                                        'WinRateCumulative', 
                                                        'WinRate7DaysRolling', 
                                                        'WinRate30DaysRolling',
                                                        'WinRate60DaysRolling', 
                                                        'WinRate90DaysRolling', 
                                                        'WinRate180DaysRolling',
                                                        'WinRate365DaysRolling', 
                                                        #'RiskReturnCumulative',
                                                        #'RiskReturn7DaysRolling', 
                                                        #'RiskReturn30DaysRolling',
                                                        #'RiskReturn60DaysRolling', 
                                                        #'RiskReturn90DaysRolling',
                                                        #'RiskReturn180DaysRolling', 
                                                        #'RiskReturn365DaysRolling',
                                                        #'KellyCriterionCumulative', 
                                                        #'KellyCriterion7DaysRolling',
                                                        #'KellyCriterion30DaysRolling', 
                                                        #'KellyCriterion60DaysRolling',
                                                        #'KellyCriterion90DaysRolling', 
                                                        #'KellyCriterion180DaysRolling',
                                                        #'KellyCriterion365DaysRolling', 
                                                        'TradeDuration', 
                                                        'CumulativeBalanceUSD',
                                                        'CumulativeReturnReverseIndicatorSMA', 
                                                        'CumulativeReturnOriginal'
                                                        ]

    obj_sql_connection = sc.CONNECT_TO_SQL_SERVER(  _str_server = "localhost",
                                                    _str_database = 'db_oms',
                                                    _str_trusted_connection = 'no',
                                                    str_download_or_upload = 'upload')

    df_data_to_be_upload = df_data.replace(np.inf, np.nan)
    df_data_to_be_upload = df_data.replace(-np.inf, np.nan)


    df_data_to_be_upload['CumulativeReturn'] = df_data_to_be_upload['CumulativeReturn'].astype('float64')

    df_data_to_be_upload['CumulativeReturnOriginal'] = df_data_to_be_upload['CumulativeReturnOriginal'].astype('float64')

    df_data_to_be_upload = df_data_to_be_upload[list_str_columns_to_be_uploaded_in_sql_database].reset_index()

    df_data_to_be_upload = pd.merge(df_data_to_be_upload,
                                    df_trading_parameters,
                                    how='left',
                                    left_on='DateTime',
                                    right_on = 'DateTime'
                                    )

    df_data_to_be_upload.to_sql(    'tbl_trading_predictions_performance', 
                                    schema='dbo', 
                                    con = obj_sql_connection, 
                                    if_exists = 'append',
                                    index= False
                                    )
    
    return df_data

#%%

if __name__ == '__main__':
    
    from asset_price_etl.Download_Scripts import etl_fx_histadata_001 as etl
    import trading_exit_price as tep
    from trading_direction import func_list_str_generate_random_trades as td

    
    df_data = etl._function_extract(_str_valuedate_start = '1/1/2011',
                                     _str_valuedate_end = '12/31/2011',
                                     _str_resample_frequency = 'D',
                                     str_currency_pair = 'EURUSD')
    
    #%% Create a simulated trade based on random number generation between 0 & 2
    df_data['TradeDirection'] = td.func_list_str_generate_random_trades(df_data)
    
    df_data['TakeProfitRate'] = 0.01
    df_data['StoplossRate'] = 0.005
    
    df_data['TimeFrame'] = pd.NA
    df_data['Broker'] = pd.NA
    df_data['StrategyName'] = pd.NA
    df_data['TradingParametersJSON'] = np.array({},dtype = object)


    df_data = func_df_plotlychart_generate_returns_analysis(df_data = df_data,
                                                            str_column_trade_entry_price_column_name = 'Open',
                                                            str_column_trade_direction_column_name = 'TradeDirection',
                                                            int_initial_balance_in_usd = 10_000,
                                                            float_percent_risk_per_trade = 0.01,
                                                            bool_appy_kelly_criterion_True_or_False = True,
                                                            float_kelly_criterion_multiplier = 0.1,
                                                            str_stoploss_fix_or_variable = 'variable',
                                                            bool_apply_CumulativeReturnReverseIndicatorSMA_True_or_False = True,
                                                            str_rolling_return_sampling_duration_for_trade_hold_or_reverse = '30D',
                                                            bool_reverse_trade_direction_when_cumulative_return_trend_down_True_or_False = False,
                                                            bool_hold_trade_when_cumulative_return_trend_down_True_or_False = True,
                                                            bool_interchange_sl_and_tp_when_cumulative_return_trend_down_True_or_False = True,
                                                            str_other_trading_parameters_json_column_name = 'TradingParametersJSON',
                                                            str_timeframe_column_name = 'TimeFrame',
                                                            str_broker_column_name = 'Broker',
                                                            str_strategy_name_column_name = 'StrategyName',
                                                            bool_generate_plotly_chart_True_or_False = False)
                



# %%



