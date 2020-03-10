clear all
%% CONSTRUCT ELLIPSE
r = 98754;  % distanza sorgente-specchio
r1 = 1750;  % distanza fuoco-specchio
alpha = 2*pi/180;   % angolo di incidenza
L = 400;    % lunghezza dello specchio

a = (r+r1)/2;
c = sqrt(((r+r1)*cos(alpha)).^2 + ((r-r1)*sin(alpha)).^2)/2.0;
b = sqrt(a*a-c*c);

delta = asin((r1*sin(pi-2*alpha))/(2*c));
x0 = 0;
x1 = L*cos(alpha-delta);
y1 = b*sqrt(1-(x1/a).^2);

x=(x0:x1)';

y=-b*sqrt(1-(x./a).^2) + ((y1-b)/x1).*x+b;
%% 

plot(x,y);

data=[x y];

dlmwrite('ellisse.txt',data,'\t');
clear data
