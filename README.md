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
pip install version pip install git+https://github.com/Iankfc/trading_returns_analysis.git@master --no-deps
```

To use the module in a pythone terminal, import the module just like other python modules such as pandas or numpy.

### Python Terminal
```

from asset_price_etl import etl_fx_histadata_001 as etl
from trading_direction import func_list_str_generate_random_trades as td
import trading_returns_analysis as tra

df_data = etl._function_extract(_str_valuedate_start = '1/1/2020',
                                    _str_valuedate_end = '12/31/2020',
                                    _str_resample_frequency = 'D',
                                    str_currency_pair = 'EURUSD')

#%% Create a simulated trade based on random number generation between 0 & 2
df_data['TradeDirection'] = td.func_list_str_generate_random_trades(df_data)

df_data['TakeProfitRate'] = 0.01
df_data['StoplossRate'] = 0.005



df_data = tra.func_df_plotlychart_generate_returns_analysis(df_data = df_data,
                                                            str_column_trade_entry_price_column_name = 'Open',
                                                        str_column_trade_direction_column_name = 'TradeDirection',
                                                        str_column_trade_exit_price_column_name = 'ExitPrice',
                                                        str_column_trade_exit_date_column_name = 'ExitDate',
                                                        int_initial_balance_in_usd = 10_000,
                                                        float_percent_risk_per_trade = 0.01,
                                                        bool_appy_kelly_criterion_True_or_False = True,
                                                        float_kelly_criterion_multiplier = 0.1,
                                                        int_future_closing_lag_number_of_days = 14,
                                                        str_stoploss_fix_or_variable = 'variable',
                                                        bool_apply_CumulativeReturnReverseIndicatorSMA_True_or_False = True,
                                                        str_rolling_return_sampling_duration_for_trade_hold_or_reverse = '30D')


```


## Usage <a name = "usage"></a>

The module can be use to for extract transform and load (ETL) flow of data science.
