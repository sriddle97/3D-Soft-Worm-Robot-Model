function make_connects(helix_vecs, xml_path, new_xml_path)
    
    dummy = helix_vecs("left_handed");
    LH_helixes = dummy{1,1};
    dummy = helix_vecs("right_handed");
    RH_helixes = dummy{1,1};
    dummy = helix_vecs("intersection_points");
    intersection_pts = dummy{1,1};

    xml_file = xml2struct(xml_path);

    num_connects = 1;
    num_welds = 1;

    for i = 1:length(intersection_pts)
        for ii = 1:length(RH_helixes)
            [~,a,b] = intersect(LH_helixes{ii},intersection_pts{i},'rows');
            [~,c,d] = intersect(RH_helixes{ii},intersection_pts{i},'rows');
            
            for iii = 1:length(a)
                if a(iii) == 1
                    body1 = append('ball',num2str(i-1),num2str(b(iii)-1));
                    body2 = append('LH',num2str(ii-1),'B_','first');
                elseif a(iii) == length(LH_helixes{ii})
                    body1 = append('ball',num2str(i-1),num2str(b(iii)-1));
                    body2 = append('LH',num2str(ii-1),'B_','last');
                else
                    body1 = append('ball',num2str(i-1),num2str(b(iii)-1));
                    body2 = append('LH',num2str(ii-1),'B_',num2str(a(iii)-1));      % 'B_',num2str(a(iii)-2)
                end

                xml_file.mujoco.equality.connect{1,num_connects}.Attributes.body1 = body1;
                xml_file.mujoco.equality.connect{1,num_connects}.Attributes.body2 = body2;
                xml_file.mujoco.equality.connect{1,num_connects}.Attributes.anchor = '0 0 0';
                xml_file.mujoco.equality.connect{1,num_connects}.Attributes.solref = '0.001 1';         % solref may change depending on cable thickness
                num_connects = num_connects + 1;

            end
            for iii = 1:length(c)
                if c(iii) == 1
                    body1 = append('ball',num2str(i-1),num2str(d(iii)-1));
                    body2 = append('RH',num2str(ii-1),'B_','first');
                elseif c(iii) == length(LH_helixes{ii})
                    body1 = append('ball',num2str(i-1),num2str(d(iii)-1));
                    body2 = append('RH',num2str(ii-1),'B_','last');
                else
                    body1 = append('ball',num2str(i-1),num2str(d(iii)-1));
                    body2 = append('RH',num2str(ii-1),'B_',num2str(c(iii)-1));      % 'B_',num2str(c(iii)-2)
                end

                xml_file.mujoco.equality.connect{1,num_connects}.Attributes.body1 = body1;
                xml_file.mujoco.equality.connect{1,num_connects}.Attributes.body2 = body2;
                xml_file.mujoco.equality.connect{1,num_connects}.Attributes.anchor = '0 0 0';
                xml_file.mujoco.equality.connect{1,num_connects}.Attributes.solref = '0.001 1';         % solref may change depending on cable thickness
                num_connects = num_connects + 1;

            end
        end
    end
    struct2xml(xml_file, new_xml_path)
end