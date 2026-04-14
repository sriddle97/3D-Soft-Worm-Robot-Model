function make_muscles_and_tendons(helix_vecs, xml_path, new_xml_path)

    dummy = helix_vecs("left_handed");
    LH_helixes = dummy{1,1};
    dummy = helix_vecs("right_handed");
    RH_helixes = dummy{1,1};
    dummy = helix_vecs("intersection_points");
    intersection_pts = dummy{1,1};

    xml_file = xml2struct(xml_path);
    
    %% make the ring muscles
    % counter. starts at 1
    num_tendons = 1;
    
    % the number of intersections between muscles 
    % each segment is 2 intersections. so skip_between=3 has 1.5 segments
    % between muscles.
    skip_between = 3; 

    % how much space on either end before muscles
    skip_ends = 2;

    muscle_row_vec = [skip_ends]; 

    while (muscle_row_vec(end) + skip_between) <= (length(intersection_pts{1}) - (skip_ends+1))
        muscle_row_vec(end+1) = muscle_row_vec(end) + skip_between;
    end
    
    num_muscles = length(muscle_row_vec)

    for i = 1:num_muscles
        xml_file.mujoco.tendon.spatial{1,num_tendons}.Attributes.name = append('ring', num2str(i-1));
        for ii = 1:length(LH_helixes)+1
            if ii == length(LH_helixes)+1
                % need to loop back so the fisrt and last site are the same
                site_num = 1;
                xml_file.mujoco.tendon.spatial{1,num_tendons}.site{1,ii}.Attributes.site = append('site',num2str(site_num-1), num2str(muscle_row_vec(i)));
            else
                xml_file.mujoco.tendon.spatial{1,num_tendons}.site{1,ii}.Attributes.site = append('site',num2str(ii-1), num2str(muscle_row_vec(i)));
            end
            xml_file.mujoco.tendon.spatial{1,num_tendons}.Attributes.width = '0.003';
        end
        num_tendons = num_tendons+1;
    end

    for i = 1:num_muscles 
        xml_file.mujoco.actuator.muscle{1,i}.Attributes.name = append('ring',num2str(i-1),'_muscle');
        xml_file.mujoco.actuator.muscle{1,i}.Attributes.tendon = append('ring',num2str(i-1));
        xml_file.mujoco.actuator.muscle{1,i}.Attributes.class = 'muscle';
        % % range and lmin tuning
        % xml_file.mujoco.actuator.muscle{1,i}.Attributes.lmin = '0.58';
        % xml_file.mujoco.actuator.muscle{1,i}.Attributes.range = '0.62 1.1';

        % lengthrange tuning
        xml_file.mujoco.actuator.muscle{1,i}.Attributes.lengthrange = '0.62 1.1';

        
        % % Scale Tuning
        % xml_file.mujoco.actuator.muscle{1,i}.Attributes.scale = '4500';
        % % Force Tuning (when bend = 3e8)
        % if i == 1
        %     xml_file.mujoco.actuator.muscle{1,i}.Attributes.force = '5';
        % elseif i == num_muscles
        %     xml_file.mujoco.actuator.muscle{1,i}.Attributes.force = '5';
        % else
        %     xml_file.mujoco.actuator.muscle{1,i}.Attributes.force = '10';
        % end

        % Force Tuning (when bend = 20e8)
        if i == 1
            xml_file.mujoco.actuator.muscle{1,i}.Attributes.force = '16';
        elseif i == num_muscles
            xml_file.mujoco.actuator.muscle{1,i}.Attributes.force = '16';
        else
            xml_file.mujoco.actuator.muscle{1,i}.Attributes.force = '31';
        end
    end

    %% make the spring tendons
    
    % the row of the balls to start the tendons. starts at 0
    start_springs = 1;

    for ii = start_springs:3:start_springs+3
        for i = 1:length(LH_helixes)
            index1 = i;
            index2 = ii;
    
            flag = false;
            spring_num = 0;
            while ~flag
    
                xml_file.mujoco.tendon.spatial{1,num_tendons}.Attributes.name = append('spring',num2str(ii),'_',num2str(i),'_',num2str(spring_num));
                xml_file.mujoco.tendon.spatial{1,num_tendons}.Attributes.stiffness = '24.5';
                xml_file.mujoco.tendon.spatial{1,num_tendons}.Attributes.springlength = '0.065';
    
                xml_file.mujoco.tendon.spatial{1,num_tendons}.Attributes.width = '0.0025';
%                 xml_file.mujoco.tendon.spatial{1,num_tendons}.site{1,ii}.Attributes.rgba = '0.0951    0.9950    0.0317 1';


                xml_file.mujoco.tendon.spatial{1,num_tendons}.site{1,1}.Attributes.site = append('site', num2str(index1-1), num2str(index2)); 
                index1 = index1-1;
                index2 = index2 + 2;
    
                if index1 < 1 
                    index1 = length(LH_helixes);
                end
    
                xml_file.mujoco.tendon.spatial{1,num_tendons}.site{1,2}.Attributes.site = append('site', num2str(index1-1), num2str(index2));
                spring_num = spring_num+1;
                num_tendons = num_tendons+1;
    
                index1 = index1-2;
                index2 = index2 + 4;
    
                if index1 < 1 
                    index1 = length(LH_helixes)+index1;
                end
    
                if index2+2 >= length(intersection_pts{1})
                    flag = true;
                end
            end
    
            struct2xml(xml_file, new_xml_path);
        end
    end





