%% straight pipe
clc;
clear;

points = {};

radius = 0.16;
pipe_length = 0.5;

center_point1 = [0.16,-0.05,radius-0.02];
center_point2 = [0.16,-(pipe_length+0.05),radius-0.02];
% center_point1 = [0,0.16,radius];
% center_point2 = [pipe_length,0.16,radius];
rotation_angle = 0; % only need if you are making a pipe that bends
num_points = 100; % the number of bodies that will make up the pipe

points{1} = make_points(center_point1,rotation_angle, radius, num_points);
points{2} = make_points(center_point2,rotation_angle, radius, num_points);

make_pipe(points, 'straight_pipe.xml');


%% tapered pipe
clc;
clear;

points = {};

radius1 = 0.18;
radius2 = 0.12;
pipe_length = 0.5;
center_point1 = [0.18,-0.05,radius1-0.02];
center_point2 = [0.18,-(pipe_length+0.05),radius1-0.02];
% center_point1 = [0,0,radius1];
% center_point2 = [0,pipe_length,radius1];
rotation_angle = 0;
num_points = 100;

points{1} = make_points(center_point1,rotation_angle, radius1, num_points);
points{2} = make_points(center_point2,rotation_angle, radius2, num_points);

make_pipe(points, 'tapered_pipe.xml');


%% hourglass pipe
clc;
clear;

points = {};

max_radius = 0.18;
min_radius = 0.13;

center_point = [0,0,max_radius];
rotation_angle = 0;
num_points = 100;

pipe_length = 1.0;
num_segments = 11;

y = linspace(0,pipe_length,num_segments);

figure(1)
clf('reset')
hold on

amp = (max_radius - min_radius)/(median(y)^2);

for i=1:length(y)
    center_point(2) = y(i);
    rad = amp*(y(i)-median(y))^2 + min_radius;
    points{i} = make_points(center_point,rotation_angle,rad, num_points);
    scatter3(points{i}(:,1), points{i}(:,2), points{i}(:,3),200,'x');
end

% if you want straight sections on either end
straight_length = 0.2;
if straight_length > 0
    % add to the beginning
    center_point(2) = y(1) - straight_length;
    new_points = make_points(center_point,rotation_angle,max_radius, num_points);
    scatter3(new_points(:,1), new_points(:,2), new_points(:,3),200,'x');
    points = [new_points, points];
    % add to the end
    center_point(2) = y(end) + straight_length;
    points{end+1} = make_points(center_point,rotation_angle,max_radius, num_points);
    scatter3(points{end}(:,1), points{end}(:,2), points{end}(:,3),200,'x');
end
xlabel('X');
ylabel('Y');
zlabel('Z');
grid on;
axis equal

make_pipe(points, 'hourglass_pipe.xml');

%% 90 bend
clc;
clear;

points = {};

pipe_radius = 0.16;               %0.18;
num_points = 100;

num_sections = 20;
theta = linspace(0,pi/2,num_sections);

ubend_radius = 0.9; %0.9 works (-0.74 offset) 1.2 works (-1.04 for offset in xml) 0.7 doesn't work (-0.54 offset)
x_pos = ubend_radius*cos(theta);
y_pos = ubend_radius*sin(theta);

figure(2)
clf('reset')
hold on

for i=1:num_sections
    center_point = [x_pos(i), y_pos(i), pipe_radius];
    points{i} = make_points(center_point,theta(i),pipe_radius, num_points);
    scatter3(points{i}(:,1), points{i}(:,2), points{i}(:,3),200,'x');
end

% if you want straight sections on either end
straight_length = 0.2;
if straight_length > 0
    % add to the beginning
    center_point = [x_pos(1), y_pos(1)-straight_length, pipe_radius];
    new_points = make_points(center_point,theta(1),pipe_radius, num_points);
    scatter3(new_points(:,1), new_points(:,2), new_points(:,3),200,'x');
    points = [new_points, points];
    % add to the end
    center_point = [x_pos(end)-straight_length, y_pos(end), pipe_radius];
    points{end+1} = make_points(center_point,theta(end),pipe_radius, num_points);
    scatter3(points{end}(:,1), points{end}(:,2), points{end}(:,3),200,'x');
end
xlabel('X');
ylabel('Y');
zlabel('Z');
grid on;
axis equal

make_pipe(points, '90_pipe_0.9_thin.xml');

%% U-bend
clc;
clear;

points = {};

pipe_radius = 0.18;
num_points = 100;

num_sections = 10;
theta = linspace(0,pi,num_sections);

ubend_radius = 0.3;
x_pos = ubend_radius*cos(theta);
y_pos = ubend_radius*sin(theta);

figure(3)
clf('reset')
hold on

for i=1:num_sections
    center_point = [x_pos(i), y_pos(i), pipe_radius];
    points{i} = make_points(center_point,theta(i),pipe_radius, num_points);
    scatter3(points{i}(:,1), points{i}(:,2), points{i}(:,3),200,'x');
end

% if you want straight sections on either end
straight_length = 0.2;
if straight_length > 0
    % add to the beginning
    center_point = [x_pos(1), y_pos(1)-straight_length, pipe_radius];
    new_points = make_points(center_point,theta(1),pipe_radius, num_points);
    scatter3(new_points(:,1), new_points(:,2), new_points(:,3),200,'x');
    points = [new_points, points];
    % add to the end
    center_point = [x_pos(end), y_pos(end)-straight_length, pipe_radius];
    points{end+1} = make_points(center_point,theta(end),pipe_radius, num_points);
    scatter3(points{end}(:,1), points{end}(:,2), points{end}(:,3),200,'x');
end
xlabel('X');
ylabel('Y');
zlabel('Z');
grid on;
axis equal

make_pipe(points, 'ubend_pipe.xml');