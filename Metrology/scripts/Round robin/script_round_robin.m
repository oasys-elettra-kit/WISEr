%%
cd 'D:\Topics\Metrology\scripts\Round robin'
a = importdata('scan_motor5_5.dat')
%%
x = a(:,1) ;
slp =  a(:,2) ; 

y = cumtrapz(x,slp) ;
plot(x,y) 

%% sottraggo la retta che unisce il primo e l'ultimo punto
y_r = (y(end) - y(1)) / (x(end) - x(1)) * (x - x(1)) + y(1) ; 

y = y- y_r ;
xEll = x ; 

plot(x, y) ; 
% a = fit_ellipseFitzgibbon(x,y); % Fitzgibbon
b = fit_ellipse(x,y);            % Halir
% c = fitellipse(x,y);

%% ricostruzione dell'ellisse fittata
npnti = size(x,1);
y_fit = zeros(npnti,1);

for i=1:npnti
    aa = a(3);
    bb = a(2)*x(i)+a(5);
    cc = a(1)*x(i)^2+a(4)*x(i)+a(6);
    y_fit(i)= (-bb+sqrt(bb^2-4*cc*aa))/(2.0*aa);
end

%% Confronti
% Differenza tra ellisse fittata ed ellisse misurata
diff_y = y_fit - y;

% slope dell'ellisse fittata
y_fit_slp = gradient(y_fit);

% differenza delle slope
diff_slp = y_fit_slp - slp;

%% Calcolo dell'rms della slope
sqrdiff_slp = diff_slp.^2;
rms_slp = sqrt(sum(sqrdiff_slp)./npnti);

% clear npnti i;
% clear aa bb cc;

figure();
subplot(2,2,1); plot(x,y_fit,'r',x,y,'b.');
title('Fit of heights');
subplot(2,2,2); plot(x,diff_y);
ylabel('mm') 
title('\Delta y');
subplot(2,2,3); plot(x,slp);

title('Slope');
subplot(2,2,4); plot(x,diff_slp);
title(sprintf('\\Delta Slope: rms = %s', num2str(rms_slp)));

SavePng(gcf,'D:\Topics\Metrology\scripts\Round robin\OUT','Halir')
