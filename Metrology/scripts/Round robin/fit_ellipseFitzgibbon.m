function a = fit_ellipseFitzgibbon(x, y)
    D = [x.*x x.*y y.*y x y ones(size(x))]; % design matrix
    S = D' * D; % scatter matrix
    C(6, 6) = 0; 
    C(1, 3) = 2; 
    C(2, 2) = -1; 
    C(3, 1) = 2; % constraint matrix
    [gevec, geval] = eig(inv(S) * C); % solve eigensystem
%     [gevec, geval] = eig(S/C);
    [PosR, PosC] = find(geval > 0 & ~isinf(geval)); % find positive eigenvalue
    a = gevec(:, PosC);
end

