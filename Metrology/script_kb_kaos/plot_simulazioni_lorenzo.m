%%

% FileName  = 'D:\Topics\METROLOGIA KB WLTP\script_kb_kaos\doc\simkaos\kaos_real_1nm.txt' ;

% a = importdata(FileName) ;
% xstr = a.textdata(4:end,1) ;
% ystr = a.textdata(4:end,2) ;
% x = cellfun(@str2num, xstr) ;
% y = cellfun(@str2num, ystr) ;
PathFolder = 'D:\Topics\METROLOGIA KB WLTP\script_kb_kaos\doc\simkaos\' ;
PathOutput = 'D:\Topics\METROLOGIA KB WLTP\script_kb_kaos\output'
cd('D:\Topics\METROLOGIA KB WLTP\script_kb_kaos')
%%
[x,y] = ReadFileSimulazioneRaimondi(FileName)

%% Generazione plot da 1nm a 50nm


LambdaList = {'1','4','10','20','30','40','50'} ;
iMax = numel(1)
for i =1:1
	Lambda = str2num(LambdaList{i}) ; 
	xLim = 2* Lambda ;
	% ideale
	FileName = sprintf('kaos_ideal_%snm.txt', LambdaList{i})
	PathFile = [PathFolder, FileName] ;
	[xa,ya] = ReadFileSimulazioneRaimondi(PathFile) ;
	%-----------------------
	% simulato
	FileName = sprintf('kaos_real_%snm.txt', LambdaList{i})
	PathFile = [PathFolder, FileName] ;
	[xb,yb] = ReadFileSimulazioneRaimondi(PathFile) ;
	%-----------------------
	try ; close(Fig1) ; end ;
	Fig1 = figure(1) ;
	plot(xa,ya,'g','LineWidth', 3) ;
	hold  on ;
	plot(xb,yb) ;
	
	% plot layout
	xlabel('\mu m') ;
	ylabel('PSF (a.u.)') ;  
	grid on ;
	grid minor ;
	Ax = gca ;
	Ax.XLim = [-xLim, xLim]
	
	legend({'Ideal,' 'Real'} ) ;
	title(['\lambda = ', LambdaList{i},' nm']) ;  
	% Salvataggio
	saveas(Fig1,[PathOutput,'\Plot_',LambdaList{i},'nm.png'])
end

%% generazione plot a 1nm
i = 1 ;
LambdaList = {'1'} ;
FileName = sprintf('kaos_ideal_%snm.txt', LambdaList{i}) ; 
 
Lambda = 1 ;  
xLim = 10* Lambda ;
% ideale
FileName = sprintf('kaos_ideal_%snm.txt', LambdaList{i})
PathFile = [PathFolder, FileName] ;
[xa,ya] = ReadFileSimulazioneRaimondi(PathFile) ;
%-----------------------
% simulato
FileName = sprintf('kaos_real_%snm.txt', LambdaList{i})
PathFile = [PathFolder, FileName] ;
[xb,yb] = ReadFileSimulazioneRaimondi(PathFile) ;
%-----------------------
try ; close(Fig1) ; end ;
Fig1 = figure(1) ;
% plot
subplot(2,1,1) ;
plot(xa,ya,'g','LineWidth', 3) ;
% plot layout 
xlabel('\mu m') ;
ylabel('PSF (a.u.)') ;
grid on ;
grid minor ;
Ax = gca ;
Ax.XLim = [-xLim, xLim]
legend({ 'Ideal'} ) ;
title(['\lambda = ', LambdaList{i},' nm']) ;

%plot
subplot(2,1,2) ; 
plot(xb,yb) ;
% plot layout
xlabel('\mu m') ;
ylabel('PSF (a.u.)') ;
grid on ;
grid minor ;
Ax = gca ;
Ax.XLim = [-xLim, xLim]

legend({ 'Real'} ) ;
	% Salvataggio
	saveas(Fig1,[PathOutput,'\Plot_',LambdaList{i},'nm.png'])



