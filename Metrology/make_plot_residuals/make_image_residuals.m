%%
File1 = 'D:\K\DATA\LTP\kbv.txt' ;
File2 = 'D:\K\DATA\LTP\kbh.txt' ;

yh = importdata(File2) ; 
yv = importdata(File1) ; 
yh = yh * 1e6 ; 
yv = yv* 1e6 ; 
x = [0:numel(yh)-1]  ;
x = x*2 ; 



Fig1 = figure(1) ;
hold on ; 

pv = plot(x, yv+200, 'r' ) ;
pv.LineWidth =2 ;   

ph = plot(x(1:end-1), yh(1:end-1), 'k' ) ;  
ph.LineWidth = 2 ; 
grid on ;

Ax = gca ; 
Ax.FontSize  = 14 ; 

xl = xlabel('Longitudinal position (mm)') ;
yl = ylabel('Residual heigth ($nm$)' ) ;
yl.Interpreter = 'latex' ; 
xl.Interpreter = 'latex' ; 
xlim([0,360])
Leg = legend([pv,ph], {'V','H'}) ;
Leg.Box = 'off' ; 

% t1 = text(340,-415, '-460') 
% Ax.XTick = [0,50,100,200,300,350]