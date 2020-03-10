%%
cd('D:\Topics\METROLOGIA KB WLTP') ;
%% MACRO COPIA DATI

%% Lettura ellisse ideal

FName = 'D:\Topics\METROLOGIA KB WLTP\kb diproi nichel\ideal_mirror_v.txt' ;
a = importdata(FName)
x = a(:,1) ;
y = a(:,2) ;
% sottrazione retta (ideale)
xp = [x(1), x(end) ]  ;
yp = [y(1) , y(end)] ;
p = polyfit(xp,yp,1) ;
yRect = polyval(p,x) ;
yTh = y-yRect ;



yTh = - yTh ;
% plot(y) ;

%%
Path = 'D:\topics\metrologia kb wltp\kb diproi nichel\data\' ;
FileIndexList = [22:23,25,26] ;
FileIndexList = [21,22,44:47] ;

yResList = [] ;
Legend = {} ;

for i=1:numel(FileIndexList)
	FilePath = [Path,sprintf('kbniv%02d.hgt',FileIndexList(i))] ;
	Legend{i} = num2str(FileIndexList(i)) ;
	disp(FilePath) 
	% FName = 'D:\topics\metrologia kb wltp\kb diproi nichel\data\kbniv16.hgt' ;
	[xXp, yXp] = ReadFileHGT(FilePath) ;
	
	
	% sottrazione retta (dati)
	xp = [xXp(1), xXp(end) ]  ;
	yp = [yXp(1) , yXp(end)] ;
	p = polyfit(xp,yp,1) ;
	yRect = polyval(p,xXp) ;
	yXp = yXp-yRect  ;
	yRes = yXp - yTh ;
	yResList = [yResList ; yRes'] ;
end
yResList = yResList' ;
% carico residuo di riferimento
%=========================
if 1==0
	FName = 'B:\KAOSV29.HGT' ; 
	[x yResRef] = ReadFileHGT(FName) ; 
	Legend{end+1} = 'kaos' ;
	yResList = [yResList, yResRef] ; 
end
%=========================


% PLOT
%=========================
close all
plot(yResList *1e3,'linewidth', 2) ;
legend(Legend) ;
grid on ;
ylabel('\mu m') ;
xlabel('x (mm)') ;
title(' (Experiment - theory)') ;
