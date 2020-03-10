%% Profili dati da claudio
clc ; 
xc = [0 12.5000000000000 25 37.5000000000000 50 87.5000000000000 125 162.500000000000 200 237.500000000000 275 312.500000000000 350 362.500000000000 375 387.500000000000 400];
yc = [0.00808544800000000 0.0117075700000000 0.0481771170000000 0.142380944000000 0.283120404000000 0.861476175000000 1.46905274600000 1.91124028100000 2.07164720600000 1.91146705800000 1.46945263300000 0.862118613000000 0.283547648000000 0.142870282000000 0.0485895400000000 0.0116589300000000 0.00792251600000000] ;


%% nuovo campionamento (più fine)
x = 0:1:400 ;
y = spline(xc,yc,x) ;

x = x' ;
y = y' ; 
y2 = y.^2; 

% plot
plot(xc,yc,'o') ;
hold on;
plot(x,y)

%% cazzo prova fit parabole di merda
clc ; 
xx = 0:0.1:10 ;
yy = xx.^2 ;
yy = yy + 0.3*rand(1, numel(xx)).*yy ; 

xx = xx' ;
yy = yy' ; 

Ft = fittype(@(a,b,c,x) (a*x.^2 + b*x + c)) ;
FitOptions  = fitoptions('Method', 'NonLinearLeastSquares', ...
	'TolFun', 1e-8, 'StartPoint', [1 0 0]) ;
FitAns1 = fit(xx,yy, Ft, FitOptions) ;

%% fit con ellisse

% equazione
% x^2/a^2 + y^2/b^2 = 1 ;

clc
FitType = fittype(@(a,b,C, x,y) (sqrt(b*(1-x.^2/a)))) ;

% FitType = fittype(@(a,b,C, x,y) (x.^2/a^2 + y.^2/b^2 - C) , ...
% 	'independent', {'x'}, 'dependent', {'y'} ) ;

% FitType = fittype(@(a,b,C, x,y) (x.^2/a^2 + y.^2/b^2 - C)) ;

FitOptions  = fitoptions('Method', 'NonLinearLeastSquares', ...
	'TolFun', 1e-8, 'StartPoint', [1 1 1]) ;

FitAns1 = fit(x,y, FitType, FitOptions) ;
			