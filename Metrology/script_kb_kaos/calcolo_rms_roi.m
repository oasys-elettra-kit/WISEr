%%
cd('D:\Topics\METROLOGIA KB WLTP')
addpath('D:\Topics\METROLOGIA KB WLTP')
addpath('D:\Topics\METROLOGIA KB WLTP\script_kb_kaos')
PathWorking = 'D:\Topics\METROLOGIA KB WLTP\script_kb_kaos\'
FileName = '\\sincro-share\public\PADReS\KB_KAOS\KBHT_01.SLP'
PathFolder = '\\sincro-share\public\PADReS\KB_KAOS\' ;
PathOutput = [PathWorking,'output'] ; 

%%

% RmsList = GetRmsList(y)



%% KB ORIZZONTALE
FileNameToken = 'KBHT'
Indexes = [1:5; 6:10] ;
NRow = size(Indexes,1) ;
try ; close(Fig1) ; end
try ; close(Fig2) ; end

Fig1 =figure(1) ; 
Fig2 = figure(2) ; 

Legend = {} ; 
for iRow = 1:NRow
	FileIndex = Indexes(iRow,:) 
	[y, ySd , Rms, RmsSd, RmsX] = MediaProfiliSLP(FileIndex, FileNameToken, PathFolder) ;
	y = y *1e6 ; 
	ySd = y *1e6 ;
	Rms = Rms * 1e6 ;
	RmsSd = RmsSd * 1e6 ; 
	
	x = 1:numel(y) ; 
	
	Legend{iRow} = sprintf('Region %d', iRow) ; 
	% PROFILI
	set(0,'currentfigure', Fig1) ; 
	plot(x,y) ; hold on ;
	grid on ;
	title('Horizontal KB -  average profile') ; 
	xlabel('mm') ;
	ylabel('\mu rad') ; 

	% RMS
	set(0,'currentfigure', Fig2) ; 
	errorbar(RmsX, Rms, RmsSd, 'o') ; 
	title('Horizontal KB - RMS') ;
	xlabel('mm') ;
	ylabel('\mu rad') ; 
	grid on ; 
	hold on ; 
	
end

set(0,'currentfigure', Fig1) ; 
legend(Legend) ; 

set(0,'currentfigure', Fig2) ; 
legend(Legend) ; 
ax = gca ;

saveas(Fig1,[PathOutput,'\KBH_Profiles.png'])
saveas(Fig2,[PathOutput,'\KBH_Rms.png'])

%%
try ; close(Fig3) ; end
try ; close(Fig4) ; end
FileNameToken = 'KBVT'
Indexes = [1:5; 6:10] ;
NRow = size(Indexes,1) ;
Fig3 =figure(3) ; 
Fig4 = figure(4) ; 

Legend = {} ; 
for iRow = 1:NRow
	FileIndex = Indexes(iRow,:) 
	[y, ySd , Rms, RmsSd, RmsX] = MediaProfiliSLP(FileIndex, FileNameToken, PathFolder) ;
	x = 1:numel(y) ; 
		y = y *1e6 ; 
	ySd = y *1e6 ;
	Rms = Rms * 1e6 ;
	RmsSd = RmsSd * 1e6 ; 
	
	Legend{iRow} = sprintf('Region %d', iRow) ; 
	% PROFILI
	set(0,'currentfigure', Fig3) ; 
	plot(x,y) ; hold on ;
	grid on ;
	title('Vertical KB -  average profile') ; 
	xlabel('mm') ;
	ylabel('\mu rad') ; 

	% RMS
	set(0,'currentfigure', Fig4) ; 
	errorbar(RmsX, Rms, RmsSd, '*') ; 
	
	title('Vertical KB -  RMS') ;
	xlabel('mm') ;
	ylabel('\mu rad') ; 
	grid on ; 
	hold on ; 
	
end

set(0,'currentfigure', Fig3) ; 
legend(Legend) ; 

set(0,'currentfigure', Fig4) ; 
legend(Legend) ; 

saveas(Fig3,[PathOutput,'\KBV_Profiles.png'])
saveas(Fig4,[PathOutput,'\KBV_Rms.png'])







