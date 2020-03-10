function [RmsList, x] = GetRmsList(y)

StartStop = [] ;
N = 5 ;
x = [] ; 
for i=1:N
	a = (i-1)*70+1 ;
	b = i*70 ; 
	StartStop(i,:) = [a, b] ;
	
end
iEnd = size(y,1) ;
StartStop(N+1,:) = [iEnd-70, iEnd] ;


RmsList = [] ;
for i=1:size(StartStop,1)
	ia = StartStop(i,1) ;
	ib = StartStop(i,2) ;
	RmsList(i) = std(y(ia : ib)) ;
x(i) = ia + (ib-ia) * 0.5 ; 
end

end

