%%

function [x,y] = ReadFileSLP(FileName);
%FileName = 'D:\Topics\METROLOGIA KB WLTP\kb diproi nichel\data\KBNIV09.HGT'


Fid = fopen(FileName) ;

NSkipLines = 40 ;
for i=1:NSkipLines
	s  = fgetl(Fid);
end
T = [] ;

while not (feof(Fid))
	s = fgetl(Fid) ;
	ss = sscanf(s,'%e') ;
	T = [T;ss'] ;
end

fclose(Fid) ;

x = T(:,1) ;
y = T(:,2) ; 