function [x,y] = ReadFileRaimondiSimulazione(FileName)
a = importdata(FileName) ; 
xstr = a.textdata(4:end,1) ;
ystr = a.textdata(4:end,2) ; 
x = cellfun(@str2num, xstr) ; 
y = cellfun(@str2num, ystr) ;

end

