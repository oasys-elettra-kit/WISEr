function [ yMean, yStd, RmsMean, RmsStd, RmsListX] = MediaProfiliSLP(FileIndex, FileNameToken, PathFolder)

% FileIndex = [1:5] ;
% clc

yList = [] ; % 2 x m
RmsList = [] ;

yBuf  = [] ;
RmsBuf = [] ; 
NBuf = numel(FileIndex) ;
for iFile=1:NBuf
	nFile = FileIndex(iFile) ;
	FileName = sprintf('%s_%02d', FileNameToken, nFile) ;
	PathFile= [PathFolder, FileName,'.slp'] ;
	disp(PathFile)
	[x,y] = ReadFileSLP(PathFile) ;
	yBuf = [yBuf; y'] ;
	[RmsList, RmsListX]  = GetRmsList(y) ; 
	RmsBuf = [RmsBuf;  RmsList] ;
end
yMean = mean(yBuf) ;
yStd = std(yBuf) ; 
RmsMean = mean(RmsBuf) ;
RmsStd = std(RmsBuf) ;



end

