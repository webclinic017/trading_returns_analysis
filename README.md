# trading_returns_analysis

## Table of Contents

- [About](#about)
- [Getting Started](#getting_started)
- [Usage](#usage)
- [Contributing](../CONTRIBUTING.md)

## About <a name = "about"></a>

trading_returns _analysis modules contains function to analyze a timeseries of trading returns. Such as, cumulative returns monthly returns, etc.


## Getting Started <a name = "getting_started"></a>

These instructions will get you a copy of the project up and running on your local machine for development and testing purposes. See [deployment](#deployment) for notes on how to deploy the project on a live system.

### Prerequisites

First, you need to create a conda virtual environment together with python version 3.9.5 and at the same time install the dependencies in the requirements.txt file.

### Windows CMD Terminal
```
conda create --name TypeYourVirtualEnvironmentHere python=3.9.5 --file requirements.txt

```
Next, activate the virtual environment that you just created now. In the windows terminal, type the following commands.

### Windows CMD Terminal
```
conda activate TypeYourVirtualEnvironmentHere

```
### Installing

Next, after you have created a conda virtual environment with python version 3.9.5 together with the dependencies in the requirements.txt, you need to pip install sqlconnection (the "Module"). In the windows terminal, type the following codes below.

### Windows CMD Terminal
```
pip install version pip install git+https://github.com/Iankfc/trading_returns_analysis.git@master
```

To use the module in a pythone terminal, import the module just like other python modules such as pandas or numpy.

### Python Terminal
```
from asset_price_etl import etl_fx_histadata_001 as etl
import trading_returns_analysis as tra
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


df_data = tra.func_df_generate_returns_analysis(df_data = df_data,
                                            str_column_trade_entry_price_column_name = 'Open',
                                            str_column_trade_direction_column_name = 'TradeDirection',
                                            str_column_trade_exit_price_column_name = 'ExitPrice',
                                            str_column_trade_exit_date_column_name = 'ExitDate'
                                            )

tra.func_plotlychart_generate_chart(df_data = df_data,
                                str_cumulative_return_column_name = 'CumulativeReturn',
                                str_cumulative_win_rate_column_name = 'WinRateCumulative',
                                str_cumulative_risk_return_column_name = 'RiskReturnCumulative',
                                str_cumulative_kelly_criterion_column_name = 'KellyCriterionCumulative',
                                bool_merge_plotly_chart_with_other_chart_True_or_False = True,
                                class_trading_exit_price = class_tep
                                )
```


## Usage <a name = "usage"></a>

The module can be use to for extract transform and load (ETL) flow of data science.
