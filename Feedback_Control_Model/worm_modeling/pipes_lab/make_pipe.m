function make_pipe(points, xml_filepath, radius)   
    xml = struct();
    num_points = length(points{1});
    num_geoms = 1;
    for i = 1:length(points)-1
        for ii = 1:num_points
            if points{i}(ii,3) >= radius
                size = max([pdist2(points{i}(1,:), points{i}(2,:))/2, pdist2(points{i+1}(1,:), points{i+1}(2,:))/2]);
                xml.mujoco.worldbody.geom{1,num_geoms}.Attributes.type = 'cylinder';
                xml.mujoco.worldbody.geom{1,num_geoms}.Attributes.size = num2str(size);
                xml.mujoco.worldbody.geom{1,num_geoms}.Attributes.fromto = append(num2str(points{i}(ii,:)),'      ',num2str(points{i+1}(ii,:)));
                xml.mujoco.worldbody.geom{1,num_geoms}.Attributes.euler = append(' 0   ',num2str(ii*10),'   0  ');
                xml.mujoco.worldbody.geom{1,num_geoms}.Attributes.rgba = append('1 1 1 0.05');
                num_geoms = num_geoms + 1;
            else
                size = max([pdist2(points{i}(1,:), points{i}(2,:))/2, pdist2(points{i+1}(1,:), points{i+1}(2,:))/2]);
                xml.mujoco.worldbody.geom{1,num_geoms}.Attributes.type = 'cylinder';
                xml.mujoco.worldbody.geom{1,num_geoms}.Attributes.size = num2str(size);
                xml.mujoco.worldbody.geom{1,num_geoms}.Attributes.fromto = append(num2str(points{i}(ii,:)),'      ',num2str(points{i+1}(ii,:)));
                xml.mujoco.worldbody.geom{1,num_geoms}.Attributes.euler = append(' 0   ',num2str(ii*10),'   0  ');
                xml.mujoco.worldbody.geom{1,num_geoms}.Attributes.rgba = append('0.5 0.5 0.5 0.6');       %can make lower half different color
                % xml.mujoco.worldbody.geom{1,num_geoms}.Attributes.rgba = append('1 1 1 0.35');
                num_geoms = num_geoms + 1;
            end

            % size = max([pdist2(points{i}(1,:), points{i}(2,:))/2, pdist2(points{i+1}(1,:), points{i+1}(2,:))/2]);
            % xml.mujoco.worldbody.geom{1,num_geoms}.Attributes.type = 'cylinder';
            % xml.mujoco.worldbody.geom{1,num_geoms}.Attributes.size = num2str(size);
            % xml.mujoco.worldbody.geom{1,num_geoms}.Attributes.fromto = append(num2str(points{i}(ii,:)),'      ',num2str(points{i+1}(ii,:)));
            % xml.mujoco.worldbody.geom{1,num_geoms}.Attributes.euler = append(' 0   ',num2str(ii*10),'   0  ');
            % xml.mujoco.worldbody.geom{1,num_geoms}.Attributes.rgba = append('1 1 1 0.35');
            % num_geoms = num_geoms + 1;
        end
    end
    struct2xml(xml, xml_filepath)
end