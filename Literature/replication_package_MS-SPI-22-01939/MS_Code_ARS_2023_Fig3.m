

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

