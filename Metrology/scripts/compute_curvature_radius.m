%%
close all ;
clc ; 
File1 = 'D:\Topics\Metrology\DATA Fermi\HE_WISE.dat' ;
PathOut = 'D:\Topics\Analisi WFS\Doc\Paper\images' ; 
Save = 0 ; 

yv = importdata(File1) ; 
yv = -yv* 1e6 ; 
Offset = 0; 
x = [0:numel(yv)-1]  ;
x = x*1 ; 



Fig1 = figure(1) ;
hold on ; 
%--- plot profilo
pv = plot(x, yv+Offset, 'r' ) ;
pv.LineWidth =2 ;   

grid on ;


%%
Ax = gca ; 
Ax.FontSize  = 14 ; 

xl = xlabel('Longitudinal position (mm)') ;
yl = ylabel('Residual heigth ($nm$)' ) ;
yl.Interpreter = 'latex' ; 
xl.Interpreter = 'latex' ; 
 xlim([0,500])
% ylim([-400, 400])

grid minor ; 


hold on ; 


% Leg = legend([pv,ph], {'V','H'}, 'location', 'northwest') ;
% Leg.Box = 'off' ; 
grid minor
% t1 = text(340,-415, '-460') 
% Ax.XTick = [0,50,100,200,300,350]
hFig = gcf
%  SavePng(hFig,PathOut, 'plot_residuals') ;