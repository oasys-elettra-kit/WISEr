%%
clc ; 
FileName = 'K:\DATA (General)\PROTO113.INT';
Thresh = 4000 ; 

Fid = fopen(FileName) ; 


for i=1:7
s  = fgetl(Fid);
switch i
	case 4
		NTracks = str2num(s) ; 
		
	case 7
		tmp = strsplit(s,'=') ;
		tmp = strsplit(tmp{2},'.') ;
		NPoints0 = str2num(tmp{1}) ; 
end
end

Track_tmp = fscanf(Fid,'%f') ;
Sz = size(Track_tmp,1) ;
NPoints = Sz / NTracks ;				%ridefinito
disp(sprintf('NTracks= %d\nNPoints=%d\nNPoints (recomputed)=%d', NTracks, NPoints0, NPoints)) ; 

fclose(Fid) ; 

%%
Tracks = reshape(Track_tmp, [NPoints NTracks]) ; 
% e.g. the fifth track is
% Tracks(:,5)

for i=1:1
	myTrack = Tracks(:,i) ; 
	x = 1:numel(myTrack) ; 
	
	pos = find(myTrack > 4000) ;
	pos1 = pos(1) ;
	pos2 = pos(end) ; 
	
	y = Tracks(pos1:pos2) ; 
	x = x(pos1:pos2) ; 
	[yMin, yMinPos] = min(y) ; 
	
	y = y(yMinPos - 13 : yMinPos+13 ) ;
	x = x(yMinPos - 13 : yMinPos+13 ) ;
	
end
