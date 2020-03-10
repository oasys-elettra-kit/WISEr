%% 
cd('D:\Topics\METROLOGIA KB WLTP\Sulla gravità');

%% Profili dati da claudio
clc ; 
xc = [0 12.5000000000000 25 37.5000000000000 50 87.5000000000000 125 162.500000000000 200 237.500000000000 275 312.500000000000 350 362.500000000000 375 387.500000000000 400];
yc = [0.00808544800000000 0.0117075700000000 0.0481771170000000 0.142380944000000 0.283120404000000 0.861476175000000 1.46905274600000 1.91124028100000 2.07164720600000 1.91146705800000 1.46945263300000 0.862118613000000 0.283547648000000 0.142870282000000 0.0485895400000000 0.0116589300000000 0.00792251600000000] ;


% nuovo campionamento (più fine)
x = 0:1:400 ;
y = spline(xc,yc,x) ;

x = x' ;
y = y' ; 
y2 = y.^2; 

% plot
plot(xc,yc,'o') ;
hold on;
plot(x,y)

%% CROP
xClaude_mm = x ; 
yClaude_um = y; 

xC_mm = xClaude_mm(20:end-21 ) ;
yC_um =-yClaude_um(20:end-21) ; 

%% profilo da WLTP

t = readtable('D:\Topics\METROLOGIA KB WLTP\Sulla gravità\proto80.txt', ...
			'Delimiter', '\t', 'ReadVariableNames', false);

xI_mm = t.Var1 ;  ; 
yXp_um = t.Var2 *1e3 ; 
yXp_um = yXp_um  - max(yXp_um) ; 
%% controllo centri
clc
[a, b]  = min(yC_um) ;
[c, d] = min(yXp_um) ; 
disp(b)
disp(d)

yI_n = yXp_um/min(yXp_um) ;
yC_n = yC_um/min(yC_um) ; 

plot(yI_n,'b') ;
hold on ;
plot(yC_n, 'r') ; 
%% Differenza

ySum_um = -yC_um + yXp_um ; 
ySum_mm = ySum_um*1e-3 ; 
xSum_mm = 1:1:numel(ySum_um-1) ;
xSum_mm = xSum_mm' ; 

t = table(xSum_mm, ySum_mm) ; 
writetable(t,'Proto80MinusGravity.txt', 'Delimiter','\t') ; 




