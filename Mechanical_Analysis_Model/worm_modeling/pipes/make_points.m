function points3D = make_points(center_point,rotation_angle, radius, num_points)
x = center_point(1);
y = center_point(2);
z = center_point(3);

% Generate angles for the points evenly spaced around the circle
theta = linspace(0, 2*pi, num_points+1);
theta = theta(1:end-1);

% Calculate the X and Z coordinates using the parametric equations for a circle
x_pos = radius * cos(theta);
z_pos = radius * sin(theta);

% Create the 3D points by combining X, Y, and Z
points3D = [x_pos; zeros(1,num_points); z_pos+z];

% Transpose the points to have each point as a column
% points3D = points3D';

% Apply the rotation around the z-axis
Rz = [cos(rotation_angle), -sin(rotation_angle), 0;
      sin(rotation_angle), cos(rotation_angle), 0;
      0, 0, 1];
  
points3D = (Rz * points3D)';

points3D(:,1) = points3D(:,1) + x;
points3D(:,2) = points3D(:,2) + y;

end



% function points3D = make_points(center_point,rotation_angle, radius, num_points)
% y = center_point(1);
% x = center_point(2);
% z = center_point(3);
% 
% % Generate angles for the points evenly spaced around the circle
% theta = linspace(0, 2*pi, num_points+1);
% theta = theta(1:end-1);
% 
% % Calculate the X and Z coordinates using the parametric equations for a circle
% x_pos = radius * cos(theta);
% z_pos = radius * sin(theta);
% 
% % Create the 3D points by combining X, Y, and Z
% points3D = [zeros(1,num_points); x_pos; z_pos+z];
% 
% % Transpose the points to have each point as a column
% % points3D = points3D';
% 
% % Apply the rotation around the z-axis
% Rz = [cos(rotation_angle), -sin(rotation_angle), 0;
%       sin(rotation_angle), cos(rotation_angle), 0;
%       0, 0, 1];
%   
% points3D = (Rz * points3D)';
% 
% points3D(:,1) = points3D(:,1) + x;
% points3D(:,2) = points3D(:,2) + y;
% 
% end