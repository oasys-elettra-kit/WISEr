% Fitta i file dell'LTP con un'ellisse

clear all;
%% Carica dati
[filename, pathname] = uigetfile({'*.SLP'; '*.*'},'Load LTP data');
%[filename,pathname]=uigetfile({'*.hgt';'*.*'},'Load LTP data');


% di default salta le prime 15 righe del file. 
[x,slp] = ImportLTPdata(fullfile(pathname,filename));

%% esegue l'integrazione della slope e fit con ellisse
yy = cumtrapz(x, slp);

%[x,yy] = ImportLTPdata(fullfile(pathname,filename));

%% stabilità
[filename,pathname]=uigetfile({'*.slp';'*.*'},'Load STAB data');
[x,slpstab]=ImportLTPdata(fullfile(pathname,filename));

ystab=cumtrapz(x,slpstab);

y=yy-ystab;

%%
figure;
plot(x,yy,'r',x,y,'g',x,ystab,'k');
legend('measure','meas-stab','stability');

%% Esegue il fit 
%a = fit_ellipse(x,y);            % Halir
a = fit_ellipseFitzgibbon(x,y); % Fitzgibbon



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
slp = gradient(y);

% differenza delle slope
diff_slp = y_fit_slp - slp;

%% Calcolo dell'rms della slope
sqrdiff_slp = diff_slp.^2;
rms_slp = sqrt(sum(sqrdiff_slp)./npnti);

clear npnti i;
clear aa bb cc;

figure('Name',filename);
subplot(2,2,1); plot(x,y,'b.',x,y_fit,'r'); %plot(x,y_fit,'r',x,y,'b.');

title('Fit of heights');
subplot(2,2,2); plot(x,diff_y);
title('\Delta y');
subplot(2,2,3); plot(x,slp);
title('Slope');
subplot(2,2,4); plot(x,diff_slp);
title(sprintf('\\Delta Slope: rms = %s', num2str(rms_slp)));