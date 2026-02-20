/*##############################################################################*/
/*DATA CODE for reproducing main results of article
'The impact of derivatives on spot markets: Evidence from the introduction of bitcoin futures contracts'
© Augustin P., A. Rubtsov, and D. Shin
accepted for publication at Management Science, 2023
################################################################################*/

/*##############################################################################*/
/*PREAMBLE
{
This Stata file provides a code to reproduce all main regression results in the manuscript using the aggregated data set provided in the Excel file "MS_ARS_2023_DATA.xlsx." The raw data in this project are proprietary and subject to non-disclosure agreements, but accessible through paid subscription services. Data Appendix A in the Internet Appendix and related Tables B.1 and B.2, together with sections 3.5 (Measurement of characteristics) and 4.1 (Data) provide detailed and step-by-step information on data sources, data cleaning procedures and steps in the aggregation process. 

This code provides commands for reproducing Table 3 and Tables 5-11 in the main maunscript and the main results illustrated in Figure 3. Table 1, Table 2, and Table 4 are simple summary statistics tables based on information from the raw data (mean, standard deviation, correlation, ...), which are proprietary, and, therefore, not reproduced here. 
}
*/
/*##############################################################################*/

/*##############################################################################*/
/*DIRECTORY
{
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
}
*/

/*##############################################################################*/

/*##############################################################################*/
/*START OF CODE*/

/*Change to local directory*/
*cd "C:\Users\Paugus8\Dropbox\GRI-McGill PROJECT\Journal_Submissions\MS\FINAL-SUBMISSION\CODES"

* Section A: Results for exchange pairs; Table 3 (Correlation, Integration), Table 5, Table 6 (Panel B), Table 10, Figure 3
{
/*Import data*/
import excel "MS_ARS_2023_DATA.xlsx", sheet(Exchange-Pairs) firstrow clear

encode Exchanges, gen(ExchangePair_)
encode Currency, gen(CurrencyPair_)
generate monthstring =string(month)
encode monthstring, gen(monthdummy_)
gen byte constant = 1

/*##############################################################################*/
/*Tables*/

*---------------
* Table 3: Summary Statistics for Market Characteristics: Correlation (rho) and Integration (kappa)
* Statistics for other metrics generated below in Section C.

*BTC-USD
tabstat PriceSynchronicity_3m PriceIntegration_3m if Currency =="USD" , s(N mean sd median p5 p95 )
*OTHER
tabstat PriceSynchronicity_3m PriceIntegration_3m if Currency !="USD" , s(N mean sd median p5 p95 )

*---------------
* Table 5: Difference-in-Differences Results - Price Synchronicity/Correlations
generate model1 = 1 /*Model 1: Benchmark*/
generate model2 = 0 /*Model 2: EUR as single control currency*/
replace model2 = 1 if (Currency == "USD" | Currency=="EUR")
generate model3 = 0 /*Model 3: excluding EUR as control currency*/
replace model3 = 1 if Currency != "EUR"
generate model4 = 0 /*Model 4: excluding exchanges suspected of manipulation*/
replace model4 = 1 if CleanExchanges==1

* Exclude anticipation period  
drop if month>=201707 & month <= 201712
*For robustness to alternative sample periods, see Table B.7 in the Internet Appendix

* Regression Table
foreach var of varlist PriceSynchronicity_3m_w PriceIntegration_3m_w{
		eststo clear
		quietly eststo: reghdfe `var' Treatment Post Treatment_Post if PriceSyncNumOfNoNaN_3m>45 & model1==1 & !(month>=201801 & month <= 201802), absorb(constant) vce(cluster i.ExchangePair_)
		quietly eststo: reghdfe `var' Treatment Post Treatment_Post if PriceSyncNumOfNoNaN_3m>45 & model1==1 & !(month>=201801 & month <= 201802), absorb(Exchanges) vce(cluster i.ExchangePair_)
		quietly eststo: reghdfe `var' Treatment Treatment_Post if PriceSyncNumOfNoNaN_3m>45 & model1==1 & !(month>=201801 & month <= 201802), absorb(i.monthdummy_) vce(cluster i.ExchangePair_)
		quietly eststo: reghdfe `var' Treatment_Post Post if PriceSyncNumOfNoNaN_3m>45 & model1==1 & !(month>=201801 & month <= 201802), absorb(i.CurrencyPair_) vce(cluster i.ExchangePair_)
		quietly eststo: reghdfe `var' Treatment_Post if PriceSyncNumOfNoNaN_3m>45 & model1==1 & !(month>=201801 & month <= 201802), absorb(i.ExchangePair_ i.monthdummy_ i.CurrencyPair_) vce(cluster i.ExchangePair_)
		quietly eststo: reghdfe `var' Treatment_Post if PriceSyncNumOfNoNaN_3m>45 & model1==1 & !(month>=201801 & month <= 201802), absorb(i.ExchangePair_#i.monthdummy_ i.CurrencyPair_) vce(cluster i.ExchangePair_)		
		quietly eststo: reghdfe `var' Treatment_Post if PriceSyncNumOfNoNaN_3m>45 & model2==1 & !(month>=201801 & month <= 201802), absorb(i.ExchangePair_ i.monthdummy_ i.CurrencyPair_) vce(cluster i.ExchangePair_)
		quietly eststo: reghdfe `var' Treatment_Post if PriceSyncNumOfNoNaN_3m>45 & model3==1 & !(month>=201801 & month <= 201802), absorb(i.ExchangePair_ i.monthdummy_ i.CurrencyPair_) vce(cluster i.ExchangePair_)
		quietly eststo: reghdfe `var' Treatment_Post if PriceSyncNumOfNoNaN_3m>45 & model4==1 & !(month>=201801 & month <= 201802), absorb(i.ExchangePair_ i.monthdummy_ i.CurrencyPair_) vce(cluster i.ExchangePair_)
		esttab, keep(Treatment Post Treatment_Post) b(%5.3f) se(%5.3f) scalars(N r2_a)  star(* 0.10 ** 0.05 *** 0.01)
*Note: Since our metrics are computed over 3-month horizons, we excude January and February 2018 to avoid overlapping data in the pre- and post-event periods. See Footnote 6 for details. For robustness to alternative sample periods, see Table B.7 in the Internet Appendix
}

*---------------
*Table 6 (Panel B): The Importance of Bitcoin Futures Volume and Week-day/Week-end effects
eststo clear
quietly eststo: reghdfe PriceSynchronicity_3m_w Treatment_Post if PriceSyncNumOfNoNaN_3m>45 & model1==1 & !(month>=201801 & month <= 201802), absorb(i.ExchangePair_ i.monthdummy_ i.CurrencyPair_) vce(cluster i.ExchangePair_)
quietly eststo: reghdfe PriceSynchronicity_3m_w Treatment_Post if PriceSyncNumOfNoNaN_3m>45 & model1==1 & !(month>=201801 & month <= 201802), absorb(i.ExchangePair_#i.monthdummy_ i.CurrencyPair_) vce(cluster i.ExchangePair_)
quietly eststo: reghdfe PriceSynchronicity_3m_weekday_w Treatment_Post if PriceSyncNumOfNoNaN_3m>45 & model1==1 & !(month>=201801 & month <= 201802), absorb(i.ExchangePair_ i.monthdummy_ i.CurrencyPair_) vce(cluster i.ExchangePair_)
quietly eststo: reghdfe PriceSynchronicity_3m_weekday_w Treatment_Post if PriceSyncNumOfNoNaN_3m>45 & model1==1 & !(month>=201801 & month <= 201802), absorb(i.ExchangePair_#i.monthdummy_ i.CurrencyPair_) vce(cluster i.ExchangePair_)		
quietly eststo: reghdfe PriceSynchronicity_3m_weekend_w Treatment_Post if PriceSyncNumOfNoNaN_3m>45 & model1==1 & !(month>=201801 & month <= 201802), absorb(i.ExchangePair_ i.monthdummy_ i.CurrencyPair_) vce(cluster i.ExchangePair_)
quietly eststo: reghdfe PriceSynchronicity_3m_weekend_w Treatment_Post if PriceSyncNumOfNoNaN_3m>45 & model1==1 & !(month>=201801 & month <= 201802), absorb(i.ExchangePair_#i.monthdummy_ i.CurrencyPair_) vce(cluster i.ExchangePair_)			
quietly eststo: reghdfe PriceIntegration_3m_w Treatment_Post if PriceSyncNumOfNoNaN_3m>45 & model1==1 & !(month>=201801 & month <= 201802), absorb(i.ExchangePair_ i.monthdummy_ i.CurrencyPair_) vce(cluster i.ExchangePair_)
quietly eststo: reghdfe PriceIntegration_3m_w Treatment_Post if PriceSyncNumOfNoNaN_3m>45 & model1==1 & !(month>=201801 & month <= 201802), absorb(i.ExchangePair_#i.monthdummy_ i.CurrencyPair_) vce(cluster i.ExchangePair_)
quietly eststo: reghdfe PriceIntegration_3m_weekday_w Treatment_Post if PriceSyncNumOfNoNaN_3m>45 & model1==1 & !(month>=201801 & month <= 201802), absorb(i.ExchangePair_ i.monthdummy_ i.CurrencyPair_) vce(cluster i.ExchangePair_)
quietly eststo: reghdfe PriceIntegration_3m_weekday_w Treatment_Post if PriceSyncNumOfNoNaN_3m>45 & model1==1 & !(month>=201801 & month <= 201802), absorb(i.ExchangePair_#i.monthdummy_ i.CurrencyPair_) vce(cluster i.ExchangePair_)		
quietly eststo: reghdfe PriceIntegration_3m_weekend_w Treatment_Post if PriceSyncNumOfNoNaN_3m>45 & model1==1 & !(month>=201801 & month <= 201802), absorb(i.ExchangePair_ i.monthdummy_ i.CurrencyPair_) vce(cluster i.ExchangePair_)
quietly eststo: reghdfe PriceIntegration_3m_weekend_w Treatment_Post if PriceSyncNumOfNoNaN_3m>45 & model1==1 & !(month>=201801 & month <= 201802), absorb(i.ExchangePair_#i.monthdummy_ i.CurrencyPair_) vce(cluster i.ExchangePair_)			
esttab, keep(Treatment_Post) b(%5.3f) se(%5.3f) scalars(N r2_a)  star(* 0.10 ** 0.05 *** 0.01)

*---------------
*Table 10: Economic Channels
/*
model_SS: regressions focused on Short Selling
model_FR: regressions focused on Arbitrage Risk
model_CC: regressions focused on Capital Controls
model_Attention: regressions focused on Attention
*/

*Label exchanges subject to whether one of the exchanges from the pair has capital controls classified as either Wall or Gate
generate CC = 0
replace CC =1 if CC1==1 | CC2 == 1
generate Post_CC = Post * CC
generate Treatment_CC = Treatment * CC 
generate ThirdDiff_CC = Treatment * Post * CC 

*Label exchanges subject to short selling restructions, i.e., inability to short sell in one of the exchanges
generate SS = 0 
replace SS = 1 if Short1 == 1 & Short2==1
generate Post_SS = Post * SS
generate Treatment_SS = Treatment * SS 
generate ThirdDiff_SS = Treatment * Post * SS

*Label exchanges subject to high arbitrage frictions
*FR = 1 if arbitrage risk is high, and 0 otherwise.
generate Post_FR = Post * FR
generate Treatment_FR = Treatment * FR 
generate ThirdDiff_FR = Treatment * Post * FR 

*Label exchanges subject to high attention
generate HighAttention = 0
replace HighAttention = 1 if HighAttention1 == 1 & HighAttention2==1
generate Post_HighAttention = Post*HighAttention
generate Treatment_HighAttention = Treatment*HighAttention
generate ThirdDiff_HighAttention = Treatment*Post*HighAttention

*Regression Results
foreach var of varlist PriceSynchronicity_3m_w PriceIntegration_3m_w{
	eststo clear
	quietly eststo: reghdfe `var' Treatment Post SS Treatment_Post Treatment_SS Post_SS ThirdDiff_SS if PriceSyncNumOfNoNaN_3m>45 & model_SS==1 & !(month>=201801 & month <= 201802) , absorb(constant) vce(cluster i.ExchangePair_)
	quietly eststo: reghdfe `var' Treatment Post SS Treatment_Post Treatment_SS Post_SS ThirdDiff_SS if PriceSyncNumOfNoNaN_3m>45 & model_SS==1 & !(month>=201801 & month <= 201802) , absorb(i.ExchangePair_ i.monthdummy_ i.CurrencyPair_) vce(cluster i.ExchangePair_)

	quietly eststo: reghdfe `var' Treatment Post FR Treatment_Post Treatment_FR Post_FR ThirdDiff_FR if PriceSyncNumOfNoNaN_3m>45 & model_FR==1 & !(month>=201801 & month <= 201802) , absorb(constant) vce(cluster i.ExchangePair_)
	quietly eststo: reghdfe `var' Treatment Post FR Treatment_Post Treatment_FR Post_FR ThirdDiff_FR if PriceSyncNumOfNoNaN_3m>45 & model_FR==1 & !(month>=201801 & month <= 201802) , absorb(i.ExchangePair_ i.monthdummy_ i.CurrencyPair_) vce(cluster i.ExchangePair_)
		
	quietly eststo: reghdfe `var' Treatment Post CC Treatment_Post Treatment_CC Post_CC ThirdDiff_CC if PriceSyncNumOfNoNaN_3m>45 & model_CC==1 & !(month>=201801 & month <= 201802) , absorb(constant) vce(cluster i.ExchangePair_)
	quietly eststo: reghdfe `var' Treatment Post CC Treatment_Post Treatment_CC Post_CC ThirdDiff_CC if PriceSyncNumOfNoNaN_3m>45 & model_CC==1 & !(month>=201801 & month <= 201802) , absorb(i.ExchangePair_ i.monthdummy_ i.CurrencyPair_) vce(cluster i.ExchangePair_)

	quietly eststo: reghdfe `var' Treatment Post HighAttention Treatment_Post Treatment_HighAttention Post_HighAttention ThirdDiff_HighAttention if PriceSyncNumOfNoNaN_3m>45 & model1==1 & !(month>=201801 & month <= 201802) & model_Attention==1, absorb(constant) vce(cluster i.ExchangePair_)
	quietly eststo: reghdfe `var' Treatment Post HighAttention Treatment_Post Treatment_HighAttention Post_HighAttention ThirdDiff_HighAttention if PriceSyncNumOfNoNaN_3m>45 & model1==1 & !(month>=201801 & month <= 201802) & model_Attention==1, absorb(i.ExchangePair_ i.monthdummy_ i.CurrencyPair_) vce(cluster i.ExchangePair_)

	esttab, keep(Treatment_Post  ThirdDiff_SS ThirdDiff_FR ThirdDiff_CC ThirdDiff_HighAttention) b(%5.3f) se(%5.3f) scalars(N r2_a)  star(* 0.10 ** 0.05 *** 0.01)
}

/*##############################################################################*/
/*Figures*/

*---------------
*Figure 3 

/*Import data*/
import excel "MS_ARS_2023_DATA.xlsx", sheet(Exchange-Pairs) firstrow clear

encode Exchanges, gen(ExchangePair_)
encode Currency, gen(CurrencyPair_)
generate monthstring =string(month)
encode monthstring, gen(monthdummy_)
gen byte constant = 1

generate Q3_2016 = 0
generate Q4_2016 = 0
generate Q1_2017 = 0
generate Q2_2017 = 0
generate Q3_2017 = 0
generate Q4_2017 = 0
generate Q1_2018 = 0
generate Q2_2018 = 0
generate Q3_2018 = 0
generate Q4_2018 = 0

replace Q3_2016 =1 if month >= 201607 & month <= 201609
replace Q4_2016 =1 if month >= 201610 & month <= 201612
replace Q1_2017 =1 if month >= 201701 & month <= 201703
replace Q2_2017 =1 if month >= 201704 & month <= 201706
replace Q3_2017 =1 if month >= 201707 & month <= 201709
replace Q4_2017 =1 if month >= 201710 & month <= 201712
replace Q1_2018 =1 if month >= 201801 & month <= 201803
replace Q2_2018 =1 if month >= 201804 & month <= 201806
replace Q3_2018 =1 if month >= 201807 & month <= 201809
replace Q4_2018 =1 if month >= 201810 & month <= 201812

generate Treatment_Q3_2016 = Treatment * Q3_2016
generate Treatment_Q4_2016 = Treatment * Q4_2016
generate Treatment_Q1_2017 = Treatment * Q1_2017
generate Treatment_Q2_2017 = Treatment * Q2_2017
generate Treatment_Q3_2017 = Treatment * Q3_2017
generate Treatment_Q4_2017 = Treatment * Q4_2017
generate Treatment_Q1_2018 = Treatment * Q1_2018
generate Treatment_Q2_2018 = Treatment * Q2_2018
generate Treatment_Q3_2018 = Treatment * Q3_2018
generate Treatment_Q4_2018 = Treatment * Q4_2018

*---------------
* Figure 3
eststo clear
quietly eststo: reghdfe PriceSynchronicity_3m_w Treatment_Q3_2016 Treatment_Q4_2016 Treatment_Q1_2017 Treatment_Q2_2017 Treatment_Q4_2017 Treatment_Q1_2018 Treatment_Q2_2018 Treatment_Q3_2018 Treatment_Q4_2018 if PriceSyncNumOfNoNaN_3m>45 & !(month>=201801 & month<=201802), absorb(i.ExchangePair_#i.monthdummy_ i.CurrencyPair_) vce(cluster i.ExchangePair_ i.monthdummy_)
esttab, keep(Treatment_Q3_2016 Treatment_Q4_2016 Treatment_Q1_2017 Treatment_Q2_2017 Treatment_Q4_2017 Treatment_Q1_2018 Treatment_Q2_2018 Treatment_Q3_2018 Treatment_Q4_2018) b(%5.3f) se(%5.3f) scalars(N r2_within r2 r2_a)  star(* 0.10 ** 0.05 *** 0.01)
esttab using "coeff.csv", keep(Treatment_Q3_2016 Treatment_Q4_2016 Treatment_Q1_2017 Treatment_Q2_2017 Treatment_Q4_2017 Treatment_Q1_2018 Treatment_Q2_2018 Treatment_Q3_2018 Treatment_Q4_2018) b(%5.3f) se(%5.3f) star(* 0.10 ** 0.05 *** 0.01)
* Saved this result to Excel file "coeff.csv" and export to Matlab for figure creation. Code follows below.

*---------------
* Figure 3: Matlab code for Figure generation
/*
% coeff.csv is an Excel file that contains the regression output for the main figure: 
% By copying and paste the following code in the matlab, Figure 3 in the paper can be replicated.

%%%%%
% read coeff.csv in Matlab
%%%%%
tab = readtable("coeff.csv");

%%%%
% preprocessing for converting the text results into numeric format
%%%% 
tab = tab(:,[2;3]);
Coeff = tab([1;3;5;7;9;11;13;15;17],2);
SE = tab([2;4;6;8;10;12;13;16;18],2);
Coeff.Properties.VariableNames{1} = 'Coeff';
SE.Properties.VariableNames{1} = 'SE';

% cell to string format
Coeff.Coeff = string(Coeff.Coeff);
SE.SE = string(SE.SE);

% make a table, Coeff_SE, that has two columns
Coeff.Coeff = replace(Coeff.Coeff,"*","");
Coeff.Coeff = double(Coeff.Coeff);

SE.SE = replace(SE.SE,"(","");
SE.SE = replace(SE.SE,")","");
SE.SE = double(SE.SE);

Coeff_SE = table(Coeff.Coeff,SE.SE);
Coeff_SE.Properties.VariableNames = {'Coeff','SE'};

% adding 2017Q4 obs. 
added_obs = table(0, NaN);
added_obs.Properties.VariableNames = {'Coeff','SE'};
Coeff_SE = [Coeff_SE(1:4,:); added_obs; Coeff_SE(5:9,:)];
%%%%%%%% Done with preprocessing

%%%%%%%%%%%%%%%%%%
% Draw figure
%%%%%%%%%%%%%%%%%%
figure;
hold on;
errorbar(Coeff_SE.Coeff,1.96*Coeff_SE.SE, 'LineWidth',1,'Color',[0, 0.4470, 0.7410]);
plot(Coeff_SE.Coeff,'LineWidth',2,'Color',[0.8500, 0.3250, 0.0980]);             

plot([5+(71/92) 5+(71/92)],[-0.05 0.25],'r','LineStyle','--');
plot([0 30.5],[0 0],'k','LineStyle','--');
ylabel('$\hat{\alpha}$','Interpreter','latex');
set(gca, 'xtick', [1:10]);
        set(gca, 'xtick', [1:10]);
        set(gca, 'xlim', [0.5 10.5]);
        set(gca,'xticklabel',{'2016Q3','2016Q4','2017Q1','2017Q2','2017Q3', '2017Q4','2018Q1','2018Q2','2018Q3','2018Q4'});
ylim([-0.05; 0.25]);
xtickangle(90)
*/
/*##############################################################################*/

/*##############################################################################*/
}
/*##############################################################################*/
* Section B: Results for Volume; * Table 6 (Panel A)
{
*---------------
*Table 6 (Panel A): The Importance of Bitcoin Futures Volume and Week-day/Week-end effects

/*Import data*/
set excelxlsxlargefile on
import excel "MS_ARS_2023_DATA.xlsx", sheet(Volume) firstrow clear

*Prepare the data and label
encode Exchanges, gen(ExchangePair_)
encode Currency, gen(CurrencyPair_)
generate Datestring= string(Date)
encode Datestring, gen(daydummy_)
gen byte constant = 1

generate Treatment_Post_HighVolume14d = Treatment_Post*HighVolume14d
generate Post_HighVolume14d = Post * HighVolume14d

*Regression Table: Table 6 (Panel A)
eststo clear
quietly eststo: reghdfe PriceSynchronicity_14d_w Treatment Post HighVolume14d Treatment_Post Treatment_Post_HighVolume14d if PriceSyncNumOfNoNaN_14d>7, absorb(constant) vce(cluster i.ExchangePair_)
quietly eststo: reghdfe PriceSynchronicity_14d_w Treatment Post HighVolume14d Treatment_Post Treatment_Post_HighVolume14d if PriceSyncNumOfNoNaN_14d>7, absorb(i.ExchangePair_) vce(cluster i.ExchangePair_)
quietly eststo: reghdfe PriceSynchronicity_14d_w Treatment Treatment_Post Treatment_Post_HighVolume14d if PriceSyncNumOfNoNaN_14d>7, absorb(i.daydummy_) vce(cluster i.ExchangePair_)
quietly eststo: reghdfe PriceSynchronicity_14d_w HighVolume14d Treatment_Post Post Treatment_Post_HighVolume14d if PriceSyncNumOfNoNaN_14d>7, absorb(i.CurrencyPair_) vce(cluster i.ExchangePair_)
quietly eststo: reghdfe PriceSynchronicity_14d_w Treatment_Post Treatment_Post_HighVolume14d if PriceSyncNumOfNoNaN_14d>7, absorb(i.ExchangePair_ i.daydummy_ i.CurrencyPair_) vce(cluster i.ExchangePair_)
quietly eststo: reghdfe PriceSynchronicity_14d_w Treatment_Post Treatment_Post_HighVolume14d if PriceSyncNumOfNoNaN_14d>7, absorb(i.ExchangePair_#i.daydummy_ i.CurrencyPair_) vce(cluster i.ExchangePair_)	
quietly eststo: reghdfe PriceIntegration_14d_w Treatment Post HighVolume14d Treatment_Post Treatment_Post_HighVolume14d if PriceSyncNumOfNoNaN_14d>7, absorb(constant) vce(cluster i.ExchangePair_)
quietly eststo: reghdfe PriceIntegration_14d_w Treatment Post HighVolume14d Treatment_Post Treatment_Post_HighVolume14d if PriceSyncNumOfNoNaN_14d>7, absorb(i.ExchangePair_) vce(cluster i.ExchangePair_)
quietly eststo: reghdfe PriceIntegration_14d_w Treatment Treatment_Post Treatment_Post_HighVolume14d if PriceSyncNumOfNoNaN_14d>7, absorb(i.daydummy_) vce(cluster i.ExchangePair_)
quietly eststo: reghdfe PriceIntegration_14d_w HighVolume14d Treatment_Post Post Treatment_Post_HighVolume14d if PriceSyncNumOfNoNaN_14d>7, absorb(i.CurrencyPair_) vce(cluster i.ExchangePair_)
quietly eststo: reghdfe PriceIntegration_14d_w Treatment_Post Treatment_Post_HighVolume14d if PriceSyncNumOfNoNaN_14d>7, absorb(i.ExchangePair_ i.daydummy_ i.CurrencyPair_) vce(cluster i.ExchangePair_)
quietly eststo: reghdfe PriceIntegration_14d_w Treatment_Post Treatment_Post_HighVolume14d if PriceSyncNumOfNoNaN_14d>7, absorb(i.ExchangePair_#i.daydummy_ i.CurrencyPair_) vce(cluster i.ExchangePair_)	
esttab, keep(Treatment_Post Treatment_Post_HighVolume14d) b(%5.3f) se(%5.3f) scalars(N r2_a)  star(* 0.10 ** 0.05 *** 0.01)
}

/*##############################################################################*/
* Section C: Results for individual exchanges (i.e., other metrics); Table 7; Table 3 (other metrics);
{
/*Import data*/
import excel "MS_ARS_2023_DATA.xlsx", sheet(Exchange-Individual) firstrow clear

*Prepare the data and label 
encode ExchangeName, gen(ExchangeName_)
encode Fiat, gen(Fiat_)
generate date_string = string(Date)
encode date_string, gen(daydummy_)
generate monthstring=string(month)
encode monthstring, gen(monthdummy_)
generate Treatment_Post = Treatment * Post

*---------------
*Table 3: Summary Statistics for Market Characteristics: D1, q, Roll, CHL, Amihud, Volume, Volatility
* Statistics for correlation and integration generated in Section A above.

*BTC-USD
tabstat D1_ML4_CL4_3m Q_3m Roll_3m CHL_3m Amihud_3m Volatility_3m  if Fiat =="USD" , s(N mean sd median p5 p95 )
*OTHER
tabstat D1_ML4_CL4_3m Q_3m Roll_3m CHL_3m Amihud_3m Volatility_3m  if Fiat !="USD" , s(N mean sd median p5 p95 )

*---------------
*Table 7: Main Results for Market Quality, Price Efficiency, Liquidity, Volatility

generate model1 = 1
generate model2 = 0 
replace model2 = 1 if (Fiat == "USD" | Fiat=="EUR")

* Exclude anticipation period 
drop if month>=201707 & month <= 201712
*For robustness to alternative sample periods, see Table B.7 in the Internet Appendix

*Regression Table
eststo clear
quietly eststo: reghdfe Q_3m_w Treatment Post Treatment_Post if RollNumOfNoNaN_3m>45  & !(month>=201801 & month <= 201802) & model1 ==1, absorb(i.ExchangeName_ i.monthdummy_ i.Fiat_) vce(cluster i.ExchangeName_#i.Fiat_)
quietly eststo: reghdfe Q_3m_w Treatment Post Treatment_Post if RollNumOfNoNaN_3m>45  & !(month>=201801 & month <= 201802) & model1 ==1, absorb(i.ExchangeName_#i.monthdummy_ i.Fiat_) vce(cluster i.ExchangeName_#i.Fiat_)
quietly eststo: reghdfe D1_ML4_CL4_3m_w Treatment Post Treatment_Post if RollNumOfNoNaN_3m>45  & !(month>=201801 & month <= 201802) & model2==1 , absorb(i.ExchangeName_ i.monthdummy_ i.Fiat_) vce(cluster i.ExchangeName_#i.Fiat_)
quietly eststo: reghdfe D1_ML4_CL4_3m_w Treatment Post Treatment_Post if RollNumOfNoNaN_3m>45  & !(month>=201801 & month <= 201802) & model2==1 , absorb(i.ExchangeName_#i.monthdummy_ i.Fiat_) vce(cluster i.ExchangeName_#i.Fiat_)
quietly eststo: reghdfe comb_Liquidity_3m_2 Treatment Post Treatment_Post if RollNumOfNoNaN_3m>45  & !(month>=201801 & month <= 201802) & model1 ==1, absorb(i.ExchangeName_#i.Fiat_ i.monthdummy_ ) vce(cluster i.ExchangeName_#i.Fiat_)
quietly eststo: reghdfe comb_Liquidity_3m_2 Treatment Post Treatment_Post if RollNumOfNoNaN_3m>45  & !(month>=201801 & month <= 201802) & model1 ==1, absorb(i.ExchangeName_#i.monthdummy_ i.ExchangeName_#i.Fiat_) vce(cluster i.ExchangeName_#i.Fiat_)
quietly eststo: reghdfe Volatility_3m_w Treatment Post Treatment_Post if RollNumOfNoNaN_3m>45  & !(month>=201801 & month <= 201802) & model1 ==1, absorb(i.ExchangeName_ i.monthdummy_ i.Fiat_) vce(cluster i.ExchangeName_#i.Fiat_)
quietly eststo: reghdfe Volatility_3m_w Treatment Post Treatment_Post if RollNumOfNoNaN_3m>45  & !(month>=201801 & month <= 201802) & model1 ==1, absorb(i.ExchangeName_#i.monthdummy_ i.Fiat_) vce(cluster i.ExchangeName_#i.Fiat_)
esttab, keep(Treatment_Post) b(%5.3f) se(%5.3f) scalars(N r2_a)  star(* 0.10 ** 0.05 *** 0.01)	
}

/*##############################################################################*/
* Section D: Results using flow data; Table 8
{
	
*---------------
/*NOTE: Cross-exchange flow data are from Crystal Blockchain, a commercial data provider specialized in cryptocurrency transaction
analysis and blockchain monitoring. These data are proprietary, and cannot be shared. 
For that reason, we provide information on alterated flow data by adding noise to the variable "log_transfer", 
creating a new variable called "log_transfer_noise." Specifically, we use the following equation to generate "log_transfer_noise."
log_transfer_noise = log_transfer + sigma * epsilon, where sigma is the standard deviation of log_transfer and epsilon is a random variable drawn from a standard normal distribution. The empirical results are qualitatively the same as in Table 8, but the magnitude of the coefficients is slightly different
because the data are adjusted with a noise term.
*/

/*Import data*/
import excel "MS_ARS_2023_DATA.xlsx", sheet(Flow) firstrow clear

*---------------
*Table 8: Flow Patterns Around Futures Introduction
generate from_to = exchange_from + "_" + exchange_to
generate Post = 0
replace Post = 1 if month>=201801
generate Treatment_Post = Treatment*Post

*Regression Table: Columns (1) and (2)
eststo clear
quietly eststo: reghdfe log_transfer Post Treatment_Post, absorb(from_to) vce(cluster from_to)
quietly eststo: reghdfe log_transfer Treatment_Post, absorb(from_to month) vce(cluster from_to)
esttab, keep( Post Treatment_Post) b(%5.3f) se(%5.3f) scalars(N r2_a) star(* 0.10 ** 0.05 *** 0.01)

/*Import data*/
import excel "MS_ARS_2023_DATA.xlsx", sheet(Flow-Agg) firstrow clear

generate from_to = exchange_from + "_" + exchange_to
generate Treatment_Post = Treatment*Post


*Regression Table: Column (3)
eststo clear
quietly eststo: reghdfe log_transfer Post Treatment_Post, absorb(from_to) vce(cluster from_to)
esttab, keep(Post Treatment_Post) b(%5.3f) se(%5.3f) scalars(N r2_a) star(* 0.10 ** 0.05 *** 0.01)
}

/*##############################################################################*/
* Section E: Results for ETH; Table 9
{
/*Import data*/
import excel "MS_ARS_2023_DATA.xlsx", sheet(ETHUSD) firstrow clear

*---------------
*Table 9: Difference-in-Differences Results - ETH pairs

*Manipulate data
encode Exchanges, gen(ExchangePair_)
encode Currency, gen(CurrencyPair_)
generate monthstring =string(month)
encode monthstring, gen(monthdummy_)

*Regression Table Output: Table 9, columns (1) to (4)
eststo clear
foreach var of varlist PriceSynchronicity_3m_w PriceIntegration_3m_w {
		quietly eststo: reghdfe `var' Treatment_Post if PriceSyncNumOfNoNaN_3m>60 & !(month>=201801 & month <= 201802), absorb(i.ExchangePair_ i.monthdummy_ Treatment) vce(cluster i.ExchangePair_)
		quietly eststo: reghdfe `var' Treatment_Post if PriceSyncNumOfNoNaN_3m>60 & !(month>=201801 & month <= 201802), absorb(i.ExchangePair_#i.monthdummy_ Treatment) vce(cluster i.ExchangePair_)
}
esttab, keep(Treatment_Post) b(%5.3f) se(%5.3f) scalars(N r2_a) se star(* 0.10 ** 0.05 *** 0.01)


/*Import data*/
import excel "MS_ARS_2023_DATA.xlsx", sheet(ETHCCY) firstrow clear

*Manipulate data
encode Exchanges, gen(ExchangePair_)
encode Currency, gen(CurrencyPair_)
generate monthstring =string(month)
encode monthstring, gen(monthdummy_)

*Regression Table Output: Table 9, columns (5) to (8)
eststo clear
foreach var of varlist PriceSynchronicity_3m_w PriceIntegration_3m_w {
		quietly eststo: reghdfe `var' Treatment_Post if PriceSyncNumOfNoNaN_3m>45 & !(month>=201801 & month <= 201802), absorb(i.ExchangePair_ i.monthdummy_ i.CurrencyPair_) vce(cluster i.ExchangePair_)
		quietly eststo: reghdfe `var' Treatment_Post if PriceSyncNumOfNoNaN_3m>45 & !(month>=201801 & month <= 201802), absorb(i.ExchangePair_#i.monthdummy_ i.CurrencyPair_) vce(cluster i.ExchangePair_)
}
esttab, keep(Treatment_Post) b(%5.3f) se(%5.3f) scalars(N r2_a) se star(* 0.10 ** 0.05 *** 0.01)
}

/*##############################################################################*/
* Section F: Results for ETH; Table 11
{
/*Import data*/
import excel "MS_ARS_2023_DATA.xlsx", sheet(ETHFUTURES) firstrow clear

*---------------
*Table 11: Ethereum Futures Introduction

*Manipulate data
encode Exchanges, gen(ExchangePair_)
encode Currency, gen(CurrencyPair_)
generate monthstring = string(month)
encode monthstring, gen(monthdummy_)
generate Treatment_Post = Treatment * Post

*Identify exchanges that allow for triangular arbitrage within the exchange
generate Treatment_NTA = Treatment * NTA
generate Treatment_Post_NTA = Treatment * Post * NTA
generate Post_NTA = Post * NTA


*Regression Table Output: Table 11, Panel A, columns (2)-(4) + columns (6) to (8)
eststo clear
quietly eststo: reghdfe PriceSynchronicity_3m_w Treatment Post Treatment_Post if !(month>=202103 & month<=202104), absorb(i.monthdummy_ i.CurrencyPair_ i.ExchangePair_) vce(cluster  i.ExchangePair_)
quietly eststo: reghdfe PriceSynchronicity_3m_w Treatment Post NTA Treatment_NTA Post_NTA Treatment_Post Treatment_Post_NTA  if !(month>=202103 & month<=202104), absorb(i.monthdummy_ i.CurrencyPair_ i.ExchangePair_) vce(cluster  i.ExchangePair_)
quietly eststo: reghdfe PriceSynchronicity_3m_hourly_w Treatment Post NTA Treatment_NTA Post_NTA Treatment_Post Treatment_Post_NTA  if !(month>=202103 & month<=202104), absorb(i.monthdummy_ i.CurrencyPair_ i.ExchangePair_) vce(cluster  i.ExchangePair_)
quietly eststo: reghdfe PriceSynchronicity_3m_w Treatment Post Treatment_Post if !(month>=202103 & month<=202104) , absorb(i.CurrencyPair_ i.ExchangePair_#i.monthdummy_) vce(cluster  i.ExchangePair_)
quietly eststo: reghdfe PriceSynchronicity_3m_w Treatment Post NTA Treatment_NTA Post_NTA Treatment_Post Treatment_Post_NTA  if !(month>=202103 & month<=202104), absorb(i.CurrencyPair_ i.ExchangePair_#i.monthdummy_) vce(cluster  i.ExchangePair_)
quietly eststo: reghdfe PriceSynchronicity_3m_hourly_w Treatment Post NTA Treatment_NTA Post_NTA Treatment_Post Treatment_Post_NTA  if !(month>=202103 & month<=202104), absorb(i.CurrencyPair_ i.ExchangePair_#i.monthdummy_ ) vce(cluster  i.ExchangePair_)
esttab, keep(Treatment_Post Treatment_Post_NTA) b(%5.3f) se(%5.3f) scalars(N r2_a)  star(* 0.10 ** 0.05 *** 0.01)

*Regression Table Output: Table 11, Panel B, columns (2)-(4) + columns (6) to (8)
eststo clear
quietly eststo: reghdfe PriceIntegration_3m_w Treatment Post Treatment_Post if  !(month>=202103 & month<=202104), absorb(i.monthdummy_ i.CurrencyPair_ i.ExchangePair_) vce(cluster  i.ExchangePair_)
quietly eststo: reghdfe PriceIntegration_3m_w Treatment Post NTA Treatment_NTA Post_NTA Treatment_Post Treatment_Post_NTA  if !(month>=202103 & month<=202104), absorb(i.monthdummy_ i.CurrencyPair_ i.ExchangePair_) vce(cluster  i.ExchangePair_)
quietly eststo: reghdfe PriceIntegration_3m_hourly_w Treatment Post NTA Treatment_NTA Post_NTA Treatment_Post Treatment_Post_NTA  if !(month>=202103 & month<=202104), absorb(i.monthdummy_ i.CurrencyPair_ i.ExchangePair_) vce(cluster  i.ExchangePair_)
quietly eststo: reghdfe PriceIntegration_3m_w Treatment Post Treatment_Post if !(month>=202103 & month<=202104) , absorb(i.CurrencyPair_ i.ExchangePair_#i.monthdummy_) vce(cluster  i.ExchangePair_)
quietly eststo: reghdfe PriceIntegration_3m_w Treatment Post NTA Treatment_NTA Post_NTA Treatment_Post Treatment_Post_NTA  if !(month>=202103 & month<=202104), absorb(i.CurrencyPair_ i.ExchangePair_#i.monthdummy_) vce(cluster  i.ExchangePair_)
quietly eststo: reghdfe PriceIntegration_3m_hourly_w Treatment Post NTA Treatment_NTA Post_NTA Treatment_Post Treatment_Post_NTA  if !(month>=202103 & month<=202104), absorb(i.CurrencyPair_ i.ExchangePair_#i.monthdummy_ ) vce(cluster  i.ExchangePair_)
esttab, keep(Treatment_Post Treatment_Post_NTA) b(%5.3f) se(%5.3f) scalars(N r2_a)  star(* 0.10 ** 0.05 *** 0.01)
* In the regression, we drop March 2021 and April 2021 so that the post-period variables do not use any pre-period observations.
}
/*##############################################################################*/
/*END*/
