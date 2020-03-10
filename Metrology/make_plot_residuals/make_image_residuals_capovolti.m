%%
close all ;
clc ; 
File1 = 'D:\K\DATA\LTP\kbv.txt' ;
File2 = 'D:\K\DATA\LTP\kbh.txt' ;
PathOut = 'D:\Topics\Analisi WFS\Doc\Paper\images' ; 

foot2 = 'D:\Topics\Analisi WFS\Doc\Paper\images\make_residuals\I_2nm.txt'
foot5 = 'D:\Topics\Analisi WFS\Doc\Paper\images\make_residuals\I_5nm.txt'
foot10 = 'D:\Topics\Analisi WFS\Doc\Paper\images\make_residuals\I_10nm.txt'
foot20 = 'D:\Topics\Analisi WFS\Doc\Paper\images\make_residuals\I_20nm.txt'
foot50 = 'D:\Topics\Analisi WFS\Doc\Paper\images\make_residuals\I_50nm.txt'
foot80 = 'D:\Topics\Analisi WFS\Doc\Paper\images\make_residuals\I_80nm.txt'


%footprint 2
a = importdata(foot2); 
x2 = a(1,:) + max(a(1,:)) ;  
y2 = a(2,:) ;
%footprint 5
a = importdata(foot2); 
x5 = a(1,:) + max(a(1,:)) ;  
y5 = a(2,:) ;
%footprint 10
a = importdata(foot10); 
x10 = a(1,:) + max(a(1,:)) ;  
y10 = a(2,:) ;
%footprint 20
a = importdata(foot20); 
x20 = a(1,:) + max(a(1,:)) ;  
y20 = a(2,:) ;
%footprint 50
a = importdata(foot80); 
x50 = a(1,:) + max(a(1,:)) ;  
y50 = a(2,:) ;
%footprint 80
a = importdata(foot80); 
x80 = a(1,:) + max(a(1,:)) ;  
y80 = a(2,:) ;

% residui
yh = importdata(File2) ; 
yv = importdata(File1) ; 
yh = -yh * 1e6 ; 
yv = -yv* 1e6 ; 
Offset = -200 ; 
x = [0:numel(yh)-1]  ;
x = x*2 ; 



Fig1 = figure(1) ;
hold on ; 
%--- plot verticale
pv = plot(x, yv+Offset, 'r' ) ;
pv.LineWidth =2 ;   
%--- plot orizzontale
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
ylim([-400, 400])

grid minor ; 

% nuovo asse

yyaxis right ;
yl2 = ylabel('Intensity (a.u.) ') ;
yl2.Interpreter = 'latex' ; 
hold on ; 
% p1 = plot(x2,y2,'-o') ;
p2 = plot(x5,y5,':') ;
p3 = plot(x10,y10,'-.') ;
p4 = plot(x20,y20,'-') ;
p5 = plot(x50,y50,':') ;
% p6 = plot(x80,y80,'-.') ;
C = p2.Color ; 
t1 = text(195.5801, 0.09 , '5nm', 'Color', C)  ;
t2 = text(240, 0.09, '10nm', 'Color', C)  ;
t3 = text(294, 0.09, '20nm', 'Color', C)  ;
t4 = text(294, 0.09, '20nm', 'Color', C)  ;
t4 = text(243.6133, 0.9, '60nm', 'Color', C)  ;

Leg = legend([pv,ph], {'V','H'}, 'location', 'northwest') ;
Leg.Box = 'off' ; 
grid minor
% t1 = text(340,-415, '-460') 
% Ax.XTick = [0,50,100,200,300,350]
hFig = gcf
%  SavePng(hFig,PathOut, 'plot_residuals') ;