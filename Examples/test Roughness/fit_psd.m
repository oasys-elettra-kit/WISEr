%%

a = importdata('D:\Topics\WISEr\Repository GIT\Examples\Data\PSD_MS297_par.txt')

%%
x_um = a.data(:,1) ;
y_nm3 = a.data(:,2);


y_mm3 =  y_nm3 * 1e-18 ; 
x_mm =   x_um * 1e-3 ; 


cftool()


%%

b = importdata('D:\Topics\WISEr\Repository GIT\Examples\Data\psd_00settete.txt')
xx = b(:,1) ;
yy = b(:,2);


