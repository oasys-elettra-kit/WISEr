%% settings

ResidualFile = 'Residual_Iter07.txt' ;
NowFile = 'proto42.txt' ;

%% Lettura profilo ideale
cd '\\SINCRO-SHARE\Public\PADReS\DATA' ;
t =  readtable('kb_raimondi.csv', 'ReadVariableNames', false, 'Delimiter','\t') ; 
a = tblread('kb_raimondi.csv', '\t') ; 
xIdeal = t.Var1 ; 
yIdeal = t.Var2 ; 




%% Lettura profilo corrente

t =  readtable(NowFile, 'ReadVariableNames', false, 'Delimiter','\t') ; 
xNow = t.Var1 ;
yNow = t.Var2 ;

%% Raddrizzo yIdeal
xx = [xIdeal(1) , xIdeal(end) ] ;
yy = [yIdeal(1) , yIdeal(end)] ;
p = polyfit(xx,yy,1) ;
yLine = polyval(p,xIdeal) ; 

yIdeal = (yIdeal - yLine) ;
yIdeal = yIdeal - min(yIdeal) ; 


%% Raddrizzo yNow
xx = [xNow(1) , xNow(end) ] ;
yy = [yNow(1), yNow(end)] ;
p = polyfit(xx,yy,1) ;
yLine = polyval(p,xNow) ; 

yNow = (yNow - yLine) ;
yNow = yNow - min(yNow) ; 

%% Calcolo residui

yDiff =  yNow - yIdeal ; 

%% scrittura file
xNew = 1:numel(yDiff) ;
t = table(xNow, yDiff) ;
writetable(t,ResidualFile, 'WriteVariableNames',false, 'Delimiter', '\t') ;

%% immagini

figure(1) ;
plot(xNow, yDiff*1e3) ;
title('residuo') ;
ylabel('\mum') ;
