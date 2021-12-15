#%% Import modules

import sqlserverconnection as sc
import os
import pandas as pd

#%%

def generate_trading_simulations_summary():
    str_sqlquery_file = 'trading_simulation_summary.sql'
    str_sql_query = open(fr"{os.path.dirname(__file__)}/{str_sqlquery_file}",'r').read()

    obj_sql_connection  = sc.CONNECT_TO_SQL_SERVER(_str_server = "localhost",
                                                _str_database = 'db_oms',
                                                _str_trusted_connection = 'no',
                                                str_download_or_upload = 'download')

    df_data = pd.read_sql(sql = str_sql_query,
                    con = obj_sql_connection
                    )


    return df_data

#%%
if __name__ == '__main__':
    df_data = generate_trading_simulations_summary()

#%%
