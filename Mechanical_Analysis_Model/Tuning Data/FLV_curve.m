clc;

% Default values for Mujoco FLV curve (cannot be used here since
% lengthrange does not have a default value)
lengthrange = [0, 0];       % Derived at compile time if not defined
lmin = 0.5;
lmax = 1.6;
range = [0.75, 1.05];

% Old model parameters (bend=8e8 worm model with lmin, and range muscles)
% lengthrange = [0.055 1.069];
% lmin = 0.58;
% lmax = 1.6;
% range = [0.62, 1.1];


%% Tune the muscles using the FLV curve

% The goal is to tune the FLV output such that the maximum tension force 
% required to contract a segment is produced at the lower limit of the
% specified lengthrange (ie. when the segment is fully contracted)

% Velocity component of the FLV curve scales forces down a little, so 
% overshooting the max force by ~20% is fine. 
Fmax_20e8_measured = 16.05;   % This one was tuned to match the Wang robot, serves as a baseline
FLV_curve_F_lmin_20e8 = 19.39;
overshoot_proportinality = FLV_curve_F_lmin_20e8/Fmax_20e8_measured;
Fmax_10e8_measured = 9.58;
Fmax_3e8_measured = 4.79;
Goal_Fmax_10e8 = overshoot_proportinality*Fmax_10e8_measured
Goal_Fmax_3e8 = overshoot_proportinality*Fmax_3e8_measured


%% FLV Curve Calculations and Plotting

len = [0.1:0.01:2.0];       % Vector of real lengths for plotting scaled FLV curve

% bend=20e8 worm model with lengthrange muscles (lmin, lmax, range = deafault settings)
lengthrange = [0.62, 0.96];         % Determined by geometry
lmin = 0.5;
lmax = 1.6;
range = [0.75, 1.05];
Fmax = 30;                          % Tuned parameter

FL = calc_FL(len, lengthrange, range, lmin, lmax);
L0 = (lengthrange(2) - lengthrange(1)) / (range(2) - range(1));
L = range(1) + (len - lengthrange(1)) / L0;     % Vector of normalized lengths for plotting normalized FLV curve

figure(1)
clf('reset')
subplot(1,2,1)
title('Normalized')
hold on
plot(L, FL, 'b', 'LineWidth', 1.2)
subplot(1,2,2)
title('Scaled')
hold on
plot(len, Fmax*FL, 'b', 'LineWidth', 1.2)


% bend=3e8 worm model with lengthrange muscles
lengthrange = [0.62, 0.96];
lmin = 0.5;
lmax = 1.6;
range = [0.75, 1.05];
Fmax = 9;

FL = calc_FL(len, lengthrange, range, lmin, lmax);
L0 = (lengthrange(2) - lengthrange(1)) / (range(2) - range(1));
L = range(1) + (len - lengthrange(1)) / L0;

subplot(1,2,1)
hold on
plot(L, FL, 'r-', 'LineWidth', 1.2)
xlabel('Normalized Length')
ylabel('Force')
subplot(1,2,2)
hold on
plot(len, Fmax*FL, 'r-', 'LineWidth', 1.2)
xlabel('Length')
ylabel('Force')


% bend=10e8 worm model with lengthrange muscles
lengthrange = [0.62, 0.96];
lmin = 0.5;
lmax = 1.6;
range = [0.75, 1.05];
Fmax = 18;

FL = calc_FL(len, lengthrange, range, lmin, lmax);
L0 = (lengthrange(2) - lengthrange(1)) / (range(2) - range(1));
L = range(1) + (len - lengthrange(1)) / L0;

subplot(1,2,1)
hold on
plot(L, FL, 'g-', 'LineWidth', 1.2)
xlabel('Normalized Length')
ylabel('Force')
subplot(1,2,2)
hold on
plot(len, Fmax*FL, 'g-', 'LineWidth', 1.2)
xlabel('Length')
ylabel('Force')


%20e8 Testing different lengthrage (to show how it changes the FLV curve)
lengthrange = [0.62, 1.5];
lmin = 0.5;
lmax = 1.6;
range = [0.75, 1.05];
Fmax = 30;

FL = calc_FL(len, lengthrange, range, lmin, lmax);
L0 = (lengthrange(2) - lengthrange(1)) / (range(2) - range(1));
L = range(1) + (len - lengthrange(1)) / L0;

subplot(1,2,1)
hold on
plot(L, FL, 'k-', 'LineWidth', 1.2)
xlabel('Normalized Length')
ylabel('Force')
subplot(1,2,2)
hold on
plot(len, Fmax*FL, 'k-', 'LineWidth', 1.2)
legend('20e8', '3e8', '10e8','20e8 extended range')


% Plot bars for the lengthrange limits
plot([0.62 0.62], [0 30], 'k')
plot([0.96 0.96], [0 30], 'k')

xlabel('Length')
ylabel('Force')



%% Functions
function out = calc_FL(len, lengthrange, range, lmin, lmax)
    L0 = (lengthrange(2) - lengthrange(1)) / (range(2) - range(1));
    L = range(1) + (len - lengthrange(1)) / L0;
    out = Force_length(L, lmin, lmax);
end

function out = Force_length(LL, lmin, lmax)
    FL = zeros(size(LL));
    for i=1:length(LL)
        L = LL(i);
        FL(i) = bump(L, lmin, 1, lmax) + 0.15*bump(L, lmin, 0.5*(lmin+0.95), 0.95);
    end
    out = FL;
end

function y = bump(L, A, mid, B)
% A = lmin
% B = lmax
    left = 0.5*(A+mid);
    right = 0.5*(mid+B);

    if (L<=A) || (L>=B)
        y = 0;
    elseif L<left
        x = (L-A)/(left-A);
        y = 0.5*x*x;
    elseif L<mid
        x = (mid-L)/(mid-left);
        y = 1-0.5*x*x;
    elseif L<right
        x = (L-mid)/(right-mid);
        y = 1-0.5*x*x;
    else
        x = (B-L)/(B-right);
        y = 0.5*x*x;
    end
end