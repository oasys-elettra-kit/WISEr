function [a] = fit_ellipse(x,y)
    D1 = [x .^ 2, x .* y, y .^ 2]; % quadratic part of the design matrix
    D2 = [x, y, ones(size(x))]; % linear part of the design matrix
    S1 = D1' * D1; % quadratic part of the scatter matrix
    S2 = D1' * D2; % combined part of the scatter matrix
    S3 = D2' * D2; % linear part of the scatter matrix
    T = - inv(S3) * S2'; % for getting a2 from a1
    M = S1 + S2 * T; % reduced scatter matrix
    M = [M(3, :) ./ 2; - M(2, :); M(1, :) ./ 2]; % premultiply by inv(C1)
    [evec, eval] = eig(M); % solve eigensystem
    cond = 4 * evec(1, :) .* evec(3, :) - evec(2, :) .^ 2; % evaluate a’Ca
    a1 = evec(:, find(cond > 0)); % eigenvector for min. pos. eigenvalue
    a = [a1; T * a1]; % ellipse coefficients
end

