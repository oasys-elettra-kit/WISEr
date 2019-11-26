%%

%%
clc ; 
N = 1000 ;
sigma_N = 300
x = linspace(-N/2, N/2,N) ;
y1 = exp(-0.5 * x.^2/sigma_N^2) ; 
y2 = exp(-0.5 * (x-150).^2/sigma_N^2) *0.5 ;
y22 = exp(-0.5 * (x+150).^2/sigma_N^2) *0.5 ;
y3 = y2+y1+y22 ;
y = y3 ; 
figure(80)
plot(y3) ;

%%
r = exp(1j*2*pi * rand(1,N)) ; 

f = fft((fftshift(y).*r)) ; 
rf = real(f) ;
af = abs(f) ;

figure(1)
plot(rf,'r') ;
hold on ;
plot(af,'b'); 

%%
ac_rf = autocorr(rf,N-1) ; 
figure(2) ;
plot(ac_rf) ; 


