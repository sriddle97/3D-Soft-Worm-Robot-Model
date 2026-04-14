clc;
clear;

skeleton_filepath = 'worm_skeleton.xml';
new_filepath = 'worm_test.xml';

% first we run this to make the points for the composites and sites
% make_helix_vec(num_helix, num_segs_bt_intersections, worm_length, worm_radius,freq)
% the freq as in sin(freq*x)  
% just how tight the spiral is
%                           (num_helix, num_segs_bt_intersections,worm_length, worm_radius,freq)
helix_vecs = make_helix_vecs(12,3,0.75,0.16,14);
% helix_vecs = make_helix_vecs(12,6,0.75,0.16,14);

% this is in a bit of a weird format so lets fix that
%       LH - left handed (counterclockwise)
%       RH - right handed (clockwise)
%       This seemed better then having CW and CCW everywhere. A little more distinctive when youre looking at it
dummy = helix_vecs("left_handed");
LH_helixes = dummy{1,1};
dummy = helix_vecs("right_handed");
RH_helixes = dummy{1,1};
dummy = helix_vecs("intersection_points");
intersection_pts = dummy{1,1};



% Define sites for contact sensors
% turn into an algorithm later (basically just need to calc Nseg from helix 
% dimensions)
% strands = [2, 5, 0, 3, 5, 2, 3, 0, 2, 5, 0, 3];
% points = [2, 2, 5, 5, 8, 8, 11, 11, 14, 14, 17, 17]+1;

% arr1 = strands;
% arr2 = points;
% n = length(strands);
% 
% % NOTE: This is not foolproof, it relies on points vector being entered in
% % numerically ascending order. NEEDS ALTERED TO BE UNIVERSAL
% for i = 1:n
%     for j = 1:n-i
%         if arr1(j) > arr1(j+1)
%             % Swap elements in the array to sort in ascending order
%             temp = arr1(j);
%             arr1(j) = arr1(j+1);
%             arr1(j+1) = temp;
% 
%             temp2 = arr2(j);
%             arr2(j) = arr2(j+1);
%             arr2(j+1) = temp2;
%         else
%         end
%     end
% end
% fprintf('Sorted Arrays: \n')
% disp(arr1)
% disp(arr2)


%% Now lets put these into an xml file
%       worm_skeleton.xml just has two bodies
%             1 composite
%             1 ball
%       just uses these as a framework for the worm_new.xml

% make_bodies(helix_vecs,skeleton_filepath,new_filepath,strands,points)
make_bodies(helix_vecs,skeleton_filepath,new_filepath)

%% Making the excludes and connects

make_excludes(helix_vecs, new_filepath, new_filepath)
make_connects(helix_vecs, new_filepath, new_filepath)

%% Make the tendons and muscles

make_muscles_and_tendons(helix_vecs, new_filepath, new_filepath)

%% make the touch and tendon position sensors

make_sensors(helix_vecs, new_filepath, new_filepath)
%% Plot the worm and connection points
%   just in case you want to see it in here


% strand length for doing mass/length calc (tuning model params)
strand_length = 0;
for i = 2:length(LH_helixes{1,1})
    point_diffs = LH_helixes{1,1}(i,:)-LH_helixes{1,1}(i-1,:);
    part_length = sqrt(sum(point_diffs.^2));
    strand_length = strand_length+part_length;
end
disp(strand_length)
disp(strand_length*12)      %full length of tubing in robot (12 strands)


figure(1)
clf('reset') 
hold on

for i = 1: length(LH_helixes)
    plot3(LH_helixes{1,i}(:,1),LH_helixes{1,i}(:,2),LH_helixes{1,i}(:,3),'b','Linewidth',1.2)
    plot3(RH_helixes{1,i}(:,1),RH_helixes{1,i}(:,2),RH_helixes{1,i}(:,3),'b','Linewidth',1.2)
    plot3(intersection_pts{1,i}(:,1),intersection_pts{1,i}(:,2),intersection_pts{1,i}(:,3),'rx','MarkerSize',10,'LineWidth',1.5)
end

axis equal