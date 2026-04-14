function make_sensors(helix_vecs, xml_path, new_xml_path)

    dummy = helix_vecs("left_handed");
    LH_helixes = dummy{1,1};
    dummy = helix_vecs("right_handed");
    num_helix_each = length(dummy{1})
    RH_helixes = dummy{1,1};
    dummy = helix_vecs("intersection_points");
    intersection_pts = dummy{1,1};
    
    xml_file = xml2struct(xml_path);
    
    % hard code the site locations for the first two sensors on top and
    % bottom
    top_sens_inds{1} = [5,2];
    top_sens_inds{2} = [3,5];
    bottom_sens_inds{1} = [0,5];
    bottom_sens_inds{2} = [2,2];
    
    num_touch_sensors = 0;
    numExcludes = numel(xml_file.mujoco.contact.exclude);
    
    all_touch_sens_sites = {};

    touch_sensor_rgba = '0.5 0.5 0.5 1';
    stretch_sensor_rgba = '0.0   0.6  0.0 1';

    num_welds = 0;
    
    % top touch sensors
    while length(top_sens_inds) > 0
        for i=1:length(top_sens_inds)
            all_touch_sens_sites{end+1} = top_sens_inds{i};
            xml_file.mujoco.sensor.touch{1,num_touch_sensors+1}.Attributes.name = append('Top_', num2str(num_touch_sensors));
            xml_file.mujoco.sensor.touch{1,num_touch_sensors+1}.Attributes.site = append('site', num2str(top_sens_inds{i}(1)), num2str(top_sens_inds{i}(2)));
            

            % make the touch sensors a different color
            ball_name = append('ball', num2str(top_sens_inds{i}(1)), num2str(top_sens_inds{i}(2)));
            find_ball = find(cellfun(@(x) isfield(x, 'Attributes') && isfield(x.Attributes, 'name') && strcmp(x.Attributes.name, ball_name), xml_file.mujoco.worldbody.body)==1);
            xml_file.mujoco.worldbody.body{1,find_ball}.geom.Attributes.rgba = touch_sensor_rgba;
            
            % change properties for touch sensors
            xml_file.mujoco.worldbody.body{1,find_ball}.geom.Attributes.mass = '0.00578';
            xml_file.mujoco.worldbody.body{1,find_ball}.geom.Attributes.size = '0.0224';
            xml_file.mujoco.worldbody.body{1,find_ball}.geom.Attributes.margin = '0';
            xml_file.mujoco.worldbody.body{1,find_ball}.site.Attributes.size = '0.0224';

            % because we change the margin, we need to add excludes
            %find the right helix names and add the excludes
            sensor_pos = str2num(xml_file.mujoco.worldbody.body{1, find_ball}.Attributes.pos);
            [cell_num, row_num] = find_bodies(sensor_pos, RH_helixes);
            body_name = append('RH', num2str(cell_num-1), 'B_', num2str(row_num-1));
            xml_file.mujoco.contact.exclude{1,numExcludes+1}.Attributes.body1 = body_name;
            xml_file.mujoco.contact.exclude{1,numExcludes+1}.Attributes.body2 = ball_name;
            numExcludes = numExcludes + 1;
            
            body_name = append('RH', num2str(cell_num-1), 'B_', num2str(row_num-2));
            xml_file.mujoco.contact.exclude{1,numExcludes+1}.Attributes.body1 = body_name;
            xml_file.mujoco.contact.exclude{1,numExcludes+1}.Attributes.body2 = ball_name;
            numExcludes = numExcludes + 1;

            %same for the left helix
            [cell_num, row_num] = find_bodies(sensor_pos, LH_helixes);
            body_name = append('LH', num2str(cell_num-1), 'B_', num2str(row_num-1));
            xml_file.mujoco.contact.exclude{1,numExcludes+1}.Attributes.body1 = body_name;
            xml_file.mujoco.contact.exclude{1,numExcludes+1}.Attributes.body2 = ball_name;
            numExcludes = numExcludes + 1;
            
            body_name = append('LH', num2str(cell_num-1), 'B_', num2str(row_num-2));
            xml_file.mujoco.contact.exclude{1,numExcludes+1}.Attributes.body1 = body_name;
            xml_file.mujoco.contact.exclude{1,numExcludes+1}.Attributes.body2 = ball_name;
            numExcludes = numExcludes + 1;

            %change one of the connects to a weld
            connect_inds = find(cellfun(@(x) isfield(x, 'Attributes') && isfield(x.Attributes, 'body1') && strcmp(x.Attributes.body1, ball_name), xml_file.mujoco.equality.connect)==1);
            selected_index = connect_inds(1);
            for j = 1:length(connect_inds)
                % Get the 'body2' attribute
                body2 = xml_file.mujoco.equality.connect{1, connect_inds(j)}.Attributes.body2;
                
                % Check if ball is even (connect to R-Helix)
                if mod(top_sens_inds{i}(2), 2) == 0
                    if startsWith(body2, 'LH')
                        selected_index = connect_inds(j);  % Store the selected index
                        break;
                    end
                else  % If ball is odd (connect to L-Helix)
                    if startsWith(body2, 'RH')
                        selected_index = connect_inds(j);  % Store the selected index
                        break;
                    end
                end
            end

            body2 = xml_file.mujoco.equality.connect{1, selected_index}.Attributes.body2;
            solref = xml_file.mujoco.equality.connect{1, selected_index}.Attributes.solref;
            anchor = xml_file.mujoco.equality.connect{1, selected_index}.Attributes.anchor;
            %delete the connect
            xml_file.mujoco.equality.connect = [xml_file.mujoco.equality.connect(1:selected_index-1), xml_file.mujoco.equality.connect(selected_index+1:end)];
            %add a weld
            xml_file.mujoco.equality.weld{1, num_welds+1}.Attributes.body1 = ball_name;
            xml_file.mujoco.equality.weld{1, num_welds+1}.Attributes.body2 = body2;
            xml_file.mujoco.equality.weld{1, num_welds+1}.Attributes.solref = solref;
            xml_file.mujoco.equality.weld{1, num_welds+1}.Attributes.anchor = anchor;

            num_welds = num_welds+1;
    
            num_touch_sensors = num_touch_sensors+1;
    
            top_sens_inds{i}(1) = top_sens_inds{i}(1)-3;
            top_sens_inds{i}(2) = top_sens_inds{i}(2)+6;
            if top_sens_inds{i}(1) < 0
                top_sens_inds{i}(1) = num_helix_each + top_sens_inds{i}(1);
            end
            if top_sens_inds{i}(2) > (length(intersection_pts{1, top_sens_inds{i}(1)+1})-1)
                top_sens_inds{i} = [];
            end
        end
        top_sens_inds = top_sens_inds(~cellfun('isempty', top_sens_inds));
        
    end
    num_top_sens = num_touch_sensors;
    
    % bottom touch sensors
    while length(bottom_sens_inds) > 0
        for i=1:length(bottom_sens_inds)
            all_touch_sens_sites{end+1} = bottom_sens_inds{i};
            xml_file.mujoco.sensor.touch{1,num_touch_sensors+1}.Attributes.name = append('Bottom_', num2str(num_touch_sensors-num_top_sens));
            xml_file.mujoco.sensor.touch{1,num_touch_sensors+1}.Attributes.site = append('site', num2str(bottom_sens_inds{i}(1)), num2str(bottom_sens_inds{i}(2)));

            % make the touch sensors a different color
            ball_name = append('ball', num2str(bottom_sens_inds{i}(1)), num2str(bottom_sens_inds{i}(2)));
            find_ball = find(cellfun(@(x) isfield(x, 'Attributes') && isfield(x.Attributes, 'name') && strcmp(x.Attributes.name, ball_name), xml_file.mujoco.worldbody.body)==1);
            xml_file.mujoco.worldbody.body{1,find_ball}.geom.Attributes.rgba = touch_sensor_rgba;

            % change properties for touch sensors
            % the bottom sensors have the mass of the motors 
            xml_file.mujoco.worldbody.body{1,find_ball}.geom.Attributes.mass = '0.19228';
            xml_file.mujoco.worldbody.body{1,find_ball}.geom.Attributes.size = '0.0224';
            xml_file.mujoco.worldbody.body{1,find_ball}.geom.Attributes.margin = '0';
            xml_file.mujoco.worldbody.body{1,find_ball}.site.Attributes.size = '0.0224';

            % because we change the margin, we need to add excludes
            %find the right helix names and add the excludes
            sensor_pos = str2num(xml_file.mujoco.worldbody.body{1, find_ball}.Attributes.pos)
            [cell_num, row_num] = find_bodies(sensor_pos, RH_helixes)
            body_name = append('RH', num2str(cell_num-1), 'B_', num2str(row_num-1));
            xml_file.mujoco.contact.exclude{1,numExcludes+1}.Attributes.body1 = body_name;
            xml_file.mujoco.contact.exclude{1,numExcludes+1}.Attributes.body2 = ball_name;
            numExcludes = numExcludes + 1;
            
            body_name = append('RH', num2str(cell_num-1), 'B_', num2str(row_num-2));
            xml_file.mujoco.contact.exclude{1,numExcludes+1}.Attributes.body1 = body_name;
            xml_file.mujoco.contact.exclude{1,numExcludes+1}.Attributes.body2 = ball_name;
            numExcludes = numExcludes + 1;

            %same for the left helix
            [cell_num, row_num] = find_bodies(sensor_pos, LH_helixes)
            body_name = append('LH', num2str(cell_num-1), 'B_', num2str(row_num-1))
            xml_file.mujoco.contact.exclude{1,numExcludes+1}.Attributes.body1 = body_name
            xml_file.mujoco.contact.exclude{1,numExcludes+1}.Attributes.body2 = ball_name
            numExcludes = numExcludes + 1;
            
            body_name = append('LH', num2str(cell_num-1), 'B_', num2str(row_num-2));
            xml_file.mujoco.contact.exclude{1,numExcludes+1}.Attributes.body1 = body_name;
            xml_file.mujoco.contact.exclude{1,numExcludes+1}.Attributes.body2 = ball_name;
            numExcludes = numExcludes + 1;

            %change one of the connects to a weld
            connect_inds = find(cellfun(@(x) isfield(x, 'Attributes') && isfield(x.Attributes, 'body1') && strcmp(x.Attributes.body1, ball_name), xml_file.mujoco.equality.connect)==1);
            selected_index = connect_inds(1);
            for j = 1:length(connect_inds)
                % Get the 'body2' attribute
                body2 = xml_file.mujoco.equality.connect{1, connect_inds(j)}.Attributes.body2;
                
                % Check if ball is even (connect to R-Helix)
                if mod(bottom_sens_inds{i}(2), 2) == 0
                    if startsWith(body2, 'RH')
                        selected_index = connect_inds(j);  % Store the selected index
                        break;
                    end
                else  % If ball is odd (connect to L-Helix)
                    if startsWith(body2, 'LH')
                        selected_index = connect_inds(j);  % Store the selected index
                        break;
                    end
                end
            end

            body2 = xml_file.mujoco.equality.connect{1, selected_index}.Attributes.body2;
            solref = xml_file.mujoco.equality.connect{1, selected_index}.Attributes.solref;
            anchor = xml_file.mujoco.equality.connect{1, selected_index}.Attributes.anchor;
            %delete the connect
            xml_file.mujoco.equality.connect = [xml_file.mujoco.equality.connect(1:selected_index-1), xml_file.mujoco.equality.connect(selected_index+1:end)];
            %add a weld
            xml_file.mujoco.equality.weld{1, num_welds+1}.Attributes.body1 = ball_name;
            xml_file.mujoco.equality.weld{1, num_welds+1}.Attributes.body2 = body2;
            xml_file.mujoco.equality.weld{1, num_welds+1}.Attributes.solref = solref;
            xml_file.mujoco.equality.weld{1, num_welds+1}.Attributes.anchor = anchor;

            num_welds = num_welds+1;


            num_touch_sensors = num_touch_sensors+1;
            bottom_sens_inds{i}(1) = bottom_sens_inds{i}(1)-3;
            bottom_sens_inds{i}(2) = bottom_sens_inds{i}(2)+6;
            if bottom_sens_inds{i}(1) < 0
                bottom_sens_inds{i}(1) = num_helix_each + bottom_sens_inds{i}(1);
            end
            if bottom_sens_inds{i}(2) > (length(intersection_pts{1, bottom_sens_inds{i}(1)+1})-1)
                bottom_sens_inds{i} = [];
            end
        end
        bottom_sens_inds = bottom_sens_inds(~cellfun('isempty', bottom_sens_inds));
    end
    
    L_sens_inds{1} = [1,5,0];
    L_sens_inds{2} = [4,3,0];
    
    all_tenpos_sens_tendons = {};
    num_tendpos_sensors = 0;

    % left stretch sensors
    while length(L_sens_inds) > 0
        for i=1:length(L_sens_inds)
            all_tenpos_sens_tendons{end+1} = L_sens_inds{i};
            xml_file.mujoco.sensor.tendonpos{1,num_tendpos_sensors+1}.Attributes.name = append('L_stretch_', num2str(num_tendpos_sensors));
            xml_file.mujoco.sensor.tendonpos{1,num_tendpos_sensors+1}.Attributes.tendon = append('spring', num2str(L_sens_inds{i}(1)), '_', num2str(L_sens_inds{i}(2)), '_', num2str(L_sens_inds{i}(3)));

            % make the tendons with stretch sensors a different color
            tendon_name = append('spring', num2str(L_sens_inds{i}(1)), '_', num2str(L_sens_inds{i}(2)), '_', num2str(L_sens_inds{i}(3)));
            find_tendon = find(cellfun(@(x) isfield(x, 'Attributes') && isfield(x.Attributes, 'name') && strcmp(x.Attributes.name, tendon_name), xml_file.mujoco.tendon.spatial)==1);
            xml_file.mujoco.tendon.spatial{1,find_tendon}.Attributes.rgba = stretch_sensor_rgba;

            num_tendpos_sensors = num_tendpos_sensors+1;
            
            L_sens_inds{i}(3) = L_sens_inds{i}(3)+1;
        
            new_name = append('spring', num2str(L_sens_inds{i}(1)), '_', num2str(L_sens_inds{i}(2)), '_', num2str(L_sens_inds{i}(3)));
            spring_exists = cellfun(@(x) isfield(x, 'Attributes') && isfield(x.Attributes, 'name') && strcmp(x.Attributes.name, new_name), xml_file.mujoco.tendon.spatial);
        
            if sum(spring_exists)<1
                L_sens_inds{i} = [];
            end
        end
        L_sens_inds = L_sens_inds(~cellfun('isempty', L_sens_inds));
    end
    
    num_L_sens = num_tendpos_sensors;
    R_sens_inds{1} = [1,2,0];
    R_sens_inds{2} = [4,6,0];
    
    % right stretch sensors
    while length(R_sens_inds) > 0
        for i=1:length(R_sens_inds)
            all_tenpos_sens_tendons{end+1} = R_sens_inds{i};
            xml_file.mujoco.sensor.tendonpos{1,num_tendpos_sensors+1}.Attributes.name = append('R_stretch_', num2str(num_tendpos_sensors-num_L_sens));
            xml_file.mujoco.sensor.tendonpos{1,num_tendpos_sensors+1}.Attributes.tendon = append('spring', num2str(R_sens_inds{i}(1)), '_', num2str(R_sens_inds{i}(2)), '_', num2str(R_sens_inds{i}(3)));

            % make the tendons with stretch sensors a different color
            tendon_name = append('spring', num2str(R_sens_inds{i}(1)), '_', num2str(R_sens_inds{i}(2)), '_', num2str(R_sens_inds{i}(3)));
            find_tendon = find(cellfun(@(x) isfield(x, 'Attributes') && isfield(x.Attributes, 'name') && strcmp(x.Attributes.name, tendon_name), xml_file.mujoco.tendon.spatial)==1);
            xml_file.mujoco.tendon.spatial{1,find_tendon}.Attributes.rgba = stretch_sensor_rgba;


            num_tendpos_sensors = num_tendpos_sensors+1;
            
            R_sens_inds{i}(3) = R_sens_inds{i}(3)+1;
        
            new_name = append('spring', num2str(R_sens_inds{i}(1)), '_', num2str(R_sens_inds{i}(2)), '_', num2str(R_sens_inds{i}(3)));
            spring_exists = cellfun(@(x) isfield(x, 'Attributes') && isfield(x.Attributes, 'name') && strcmp(x.Attributes.name, new_name), xml_file.mujoco.tendon.spatial);
            
            if sum(spring_exists)<1
                R_sens_inds{i} = [];
            end
        end
        R_sens_inds = R_sens_inds(~cellfun('isempty', R_sens_inds));
    end
    
    struct2xml(xml_file, xml_path)

    % can output the all_touch_sens_sites variable instead of hardcoding
    % all in the main function
    
function [cell_num, row_num] = find_bodies(xyz, Helix)
   [~, row_indices] = cellfun(@(cellPoints)  deal(~isempty(cellPoints) && ismatrix(cellPoints) && size(cellPoints, 2) == 3, find(ismember(round(cellPoints, 4), round(xyz, 4), 'rows'))),Helix, 'UniformOutput', false);
   cell_num = find(~cellfun(@isempty, row_indices)==1);
   row_num = row_indices{cell_num};




