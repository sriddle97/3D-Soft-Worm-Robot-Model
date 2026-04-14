function make_excludes(helix_vecs,xml_path, new_xml_path)
    
    dummy = helix_vecs("left_handed");
    LH_helixes = dummy{1,1};
    dummy = helix_vecs("right_handed");
    RH_helixes = dummy{1,1};
    dummy = helix_vecs("intersection_points");
    intersection_pts = dummy{1,1};

    xml_file = xml2struct(xml_path);

    num_excludes = 1;
    
    for i = 1:length(LH_helixes)
        for ii = 1:length(RH_helixes)
            [~,b,~] = intersect(LH_helixes{i},RH_helixes{ii},'rows');
            for iii = 1:length(b)
                if b(iii) == 1
                    xml_file.mujoco.contact.exclude{1,num_excludes}.Attributes.body1 = append('LH',num2str(i-1),'B_first');
                    xml_file.mujoco.contact.exclude{1,num_excludes}.Attributes.body2 = append('RH',num2str(ii-1),'B_first');
                    num_excludes = num_excludes + 1;
                elseif b(iii) == length(LH_helixes{ii})
                    xml_file.mujoco.contact.exclude{1,num_excludes}.Attributes.body1 = append('LH',num2str(i-1),'B_last');
                    xml_file.mujoco.contact.exclude{1,num_excludes}.Attributes.body2 = append('RH',num2str(ii-1),'B_last');
                    num_excludes = num_excludes + 1;
                else
                    xml_file.mujoco.contact.exclude{1,num_excludes}.Attributes.body1 = append('LH',num2str(i-1),'B_',num2str(b(iii)-2))
                    xml_file.mujoco.contact.exclude{1,num_excludes}.Attributes.body2 = append('RH',num2str(ii-1),'B_',num2str(b(iii)-2))
                    num_excludes = num_excludes + 1;

                    xml_file.mujoco.contact.exclude{1,num_excludes}.Attributes.body1 = append('LH',num2str(i-1),'B_',num2str(b(iii)-2))
                    xml_file.mujoco.contact.exclude{1,num_excludes}.Attributes.body2 = append('RH',num2str(ii-1),'B_',num2str(b(iii)-1))
                    num_excludes = num_excludes + 1;

                    xml_file.mujoco.contact.exclude{1,num_excludes}.Attributes.body1 = append('LH',num2str(i-1),'B_',num2str(b(iii)-1))
                    xml_file.mujoco.contact.exclude{1,num_excludes}.Attributes.body2 = append('RH',num2str(ii-1),'B_',num2str(b(iii)-2))
                    num_excludes = num_excludes + 1;

                    xml_file.mujoco.contact.exclude{1,num_excludes}.Attributes.body1 = append('LH',num2str(i-1),'B_',num2str(b(iii)-1))
                    xml_file.mujoco.contact.exclude{1,num_excludes}.Attributes.body2 = append('RH',num2str(ii-1),'B_',num2str(b(iii)-1))
                    num_excludes = num_excludes + 1;
                end         
            end
        end
    end
    struct2xml(xml_file, new_xml_path)
end