function Ellipse = ConstructEllipse(r1,r2,theta,L)
    a = 1/2 *(r1+r2) ;
    b = 0.5 * sqrt(r1^2 + r2^2 - 2*r1*r2*cos(theta*pi/90) ) ; 
    c = sqrt(a^2 - b^2) ;
    d = (r1*r2*sin(theta*pi/90.0)) / (2*b) ; 
    e = a * sqrt(1- d^2/c^2) ;
    
%     x0 = e - 0.5*L;
%     x1 = e + 0.5*L ;
%     
%     npnti = L+1;
    
    x = linspace(e-0.5*L,e+0.5*L,L+1);
    y = c*sqrt(1-x.^2/a^2)-d;
    
    % sottrae retta
    yret = (y(end)-y(1))/(x(end)-x(1)).*(x-x(1))+y(1);
    y = y-yret;
    
    y=y*(-1);
    
    Ellipse = [(x-x(1))' y'];
end