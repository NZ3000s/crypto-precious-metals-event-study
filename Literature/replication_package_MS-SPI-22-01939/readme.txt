/*##############################################################################*/
/*DATA CODE for reproducing main results of article
'The impact of derivatives on spot markets: Evidence from the introduction of bitcoin futures contracts'
© Augustin P., A. Rubtsov, and D. Shin
accepted for publication at Management Science, 2023
################################################################################*/

/*##############################################################################*/
/*PREAMBLE
This Stata file provides a code to reproduce all main regression results in the manuscript using the aggregated data set provided in the Excel file "MS_ARS_2023_DATA.xlsx." The raw data in this project are proprietary and subject to non-disclosure agreements, but accessible through paid subscription services. Data Appendix A in the Internet Appendix and related Tables B.1 and B.2, together with sections 3.5 (Measurement of characteristics) and 4.1 (Data) provide detailed and step-by-step information on data sources, data cleaning procedures and steps in the aggregation process. 

This code provides commands for reproducing Table 3 and Tables 5-11 in the main maunscript and the main results illustrated in Figure 3. Table 1, Table 2, and Table 4 are simple summary statistics tables based on information from the raw data (mean, standard deviation, correlation, ...), which are proprietary, and, therefore, not reproduced here. 
/*##############################################################################*/

/*##############################################################################*/
/*DIRECTORY
-Section A: Results for exchange pairs; Table 3 (Correlation, Integration), Table 5, Table 6 (Panel B), Table 10, Figure 3
-Section B: Results for Volume; * Table 6 (Panel A)
-Section C: Results for individual exchanges (i.e., other metrics); Table 7; Table 3 (other metrics);
-Section D: Results using flow data; Table 8
-Section E: Results for ETH; Table 9
-Section F: Results for ETH; Table 11

DATA SHEET: MS_ARS_2023_DATA.xlsx
-WORK SHEET 1: "Exchange-Pairs"
-WORK SHEET 2: "Volume"
-WORK SHEET 3: "Exchange-Individual"
-WORK SHEET 4: "Flow"
-WORK SHEET 5: "Flow-Agg"
-WORK SHEET 6: "ETHUSD"
-WORK SHEET 7: "ETHCCCY"
-WORK SHEET 8: "ETHFUTURES"

SOFTWARE LICENSES
-Regressions generated using STATA
-Figures created using MATLAB

LIST OF VARIABLES
-Date: monthly observation frequency, end-of-month date_string
-Exchanges: Exchange-pair (Exchange1_Exchange2)
-Currency: fiat currency leg of BTC-CCY exchange rate (e.g., BTC-USD) 
-PriceSynchronicity_3m: Price synchronicity measure rho, measured over a 3-month horizon (see table B.3 in the Internet Appendix for alternative trading horizons)
-PriceSyncNumOfNoNaN_3m: Number of missing observations (minimum of 45 non-missing observations required) 
-PriceIntegration_3m: Price integration measure kappa, measured over a 3-month horizon (see table B.3 in the Internet Appendix for alternative trading horizons)
-month: month variable
-Treatment: indicator variable for treatment currency BTC-USD
-Post: Indicator variable for post-event period
-Treatment_Post: Indicator variable for interaction of Treatment and Post
-Exchange 1: Exchnage 1 of Exchange Pair
-Exchange 2: Exchnage 2 of Exchange Pair
-HighAttention1: Indicator variable for high attention for Exchange 1
-HighAttention2: Indicator variable for high attention for Exchange 2
-Short1: Indicator variable for ability to short in Exchange 1
-Short2: Indicator variable for ability to short in Exchange 2
-PriceSynchronicity_3m_w: PriceSynchronicity_3m winsorized
-PriceIntegration_3m_w:PriceIntegration_3m winsorized
-PriceSynchronicity_3m_weekday_w: Price Synchronicity measured using weekday data, winsorized
-PriceSynchronicity_3m_weekend_w: Price Synchronicity measured using week-end data, winsorized
-PriceIntegration_3m_weekday_w: Price Integration measured using weekday data, winsorized
-PriceIntegration_3m_weekend_w: Price Integration measured using week-end data, winsorized
-CleanExchanges: Indicator variable identifying exchanges not subject to manipulation
-model_SS: selection variable for regressions focused on Short Selling
-model_FR: selection variable for regressions focused on Arbitrage Risk
-model_CC: selection variable for regressions focused on Capital Controls
-model_Attention: selection variable for regressions focused on Attention
-PriceSynchronicity_14d_w: Prince Synchronicity measured over 14 days horizons, winsorized
-PriceSyncNumOfNoNaN_14d: Number of days with missing information in 14-day period for Prince Synchronicity
-PriceIntegration_14d_w: Prince Integration measured over 14 days horizons, winsorized
-HighVolume14d: Indicator variable capturing periods with high futures trading volume
-Roll_3m: Roll price impact metric, measured over a 3-month trading horizon 
-CHL_3m: CHL bid-ask spread metric, measured over a 3-month trading horizon
-Amihud_3m: Amihud price impact metric, measured over a 3-month trading horizon
-Q_3m: Market quality metric q, measured over a 3-month trading horizon
-D1_ML4_CL4_3m: Price efficiency metric D1, measured over a 3-month trading horizon
-Volatility_3m: Volatility metric sigma, measured over a 3-month trading horizon
-comb_Liquidity_3m_2: Aggregate illiquidity metric lambda, measured over a 3-month trading horizon  	
-D1_ML4_CL4_3m_w: Price efficiency metric D1, measured over a 3-month trading horizon, winsorized
-Q_3m_w: Market quality metric q, measured over a 3-month trading horizon, winsorized
-Volatility_3m_w: Volatility metric sigma, measured over a 3-month trading horizon, winsorized
-RollNumOfNoNaN_3m: Number of non-missing observations in the computation of the Roll measure
-YEAR: year variables
-MONTH: month variable
-exchange_from: originating exchange for transfer
-exchange_to: receiving exchange for transfer
-transferred_amount: aggregate BTC volume transferred between two exchanges
-mean_USD_frac_from: Indicator capturing whether BTC–USD trading volume accounts for
more than 50% of all trading volume at the originating exchange and zero otherwise
-mean_USD_frac_to: Indicator capturing whether BTC–USD trading volume accounts for
more than 50% of all trading volume at the receiving exchange and zero otherwise
-PriceSynchronicity_3m_hourly_w: Price Synchronicity measured using hourly data over 3-month horizon, winsorized
-PriceIntegration_3m_hourly_w: Price Integration measured using hourly data over 3-month horizon, winsorized
-log_transfer_noise: Logarithm of (1+transfer volume) + noise term. Section D provides details on the construction of this variable.
-Treatment: Indicator equal to 1 if the BTC-USD trading volume shares in exchange_from and exchange_to are over 50% of trading volume, and 0 otherwise
/*##############################################################################*/
