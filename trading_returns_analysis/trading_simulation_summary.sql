
Select *
From  
(
 SELECT  DISTINCT
       
        InsertDateTime,
        Convert(nvarchar(max), Replace(TradingParametersJSON,'''','"') )  as TradingParametersJSON,
        LAST_VALUE(  CumulativeReturn) over ( Partition by InsertDateTime order by InsertDateTime  ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)  as CumulativeReturn,
        LAST_VALUE(  CumulativeBalanceUSD) over ( Partition by InsertDateTime order by InsertDateTime  ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)  as CumulativeBalanceUSD,
        LAST_VALUE(  WinRateCumulative) over ( Partition by InsertDateTime order by InsertDateTime  ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)  as WinRateCumulative,
        LAST_VALUE(  CumulativeReturnOriginal) over ( Partition by InsertDateTime order by InsertDateTime  ROWS BETWEEN UNBOUNDED PRECEDING AND UNBOUNDED FOLLOWING)  as CumulativeReturnOriginal
    FROM 
        db_oms.dbo.tbl_trading_predictions_performance
)tbl_main
Cross Apply OpenJson
(tbl_main.TradingParametersJSON) tbl_parameter


        


