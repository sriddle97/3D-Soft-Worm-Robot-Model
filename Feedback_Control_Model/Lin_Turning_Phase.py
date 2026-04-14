## Phase Shifted Time-Based Controller for Peristaltic Turning
#
# Author: Shane Riddle
#
# Last edited: 04/13/2025
#########################################################################

# The worm robot is simulated in Mujoco using composite cable objects for 
# the structure, circumferential tendon linear actuators, and passive 
# tendons for the linear springs. Contact and stretch sensors have been
# implemented for proprioceptive feedback and tracking. The model can be 
# altered in the xml file. Alterations to the xml file will likely 
# require alterations to the rest of this code. The order in which the 
# model is built impacts the order of the input and output arrays, as 
# well as data_mj.

# The actuator signals are time-based, 3x1 persitaltic waves with fixed 
# intervals. When performing turns this code runs an open-loop, 
# phase-shifted wave, where the left and right sides have the same 
# actuatiuon pattern but one side lags behind the other by a fixed amount.

## XML Model Properties
# -  Cable composite Bend parameter = Young's modulus = 2 GPa (corrected via tuning)
# -  Cable composite Twist parameter = Shear Modulus = 1.33 GPa (scaled same as Young's)
# -  Physical dimensions and stretch readings are in m
# -  Density is in kg/m^3 (default is 1000, ie. water) so mass is in kg
# -  Model timestep is 1 ms

############################## Import packages ################################

## Mujoco
import mujoco

## Basic Utility and Plotting Packages
import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
import xml.etree.ElementTree as ET
import time
import os
from tqdm import tqdm
import pandas as pd
from openpyxl import load_workbook

## Movie Making Packages  (Use mediapy for Mujoco)
import matplotlib.animation as animation
import mediapy as media

####################### Input/Output File Organization ########################

## Automatically get work directory
work_dir = os.getcwd()
print("String format :", work_dir)

xml_path = work_dir + r"\worm_modeling\worm_extra_sensors.xml"
xml_file = ET.parse(xml_path)

## Change file_paths as needed. These xml objects get added to the "worm_with_pipe.xml" file which is then used to run the sim
## File names for videos, csv data files, and plots also go here, as well as frictions (if none specified, the deafault in the xml file is used)

# file_paths = [r'\pipes\90_pipe_0.5_wide.xml', r'\pipes\90_pipe_0.6_wide.xml', r'\pipes\90_pipe_0.7_wide.xml', r'\pipes\90_pipe_0.8_wide.xml', r'\pipes\90_pipe_0.9_wide.xml', r'\pipes\90_pipe_1.0_wide.xml', r'\pipes\90_pipe_1.1_wide.xml', r'\pipes\90_pipe_1.2_wide.xml', r'\pipes\90_pipe_1.3_wide.xml']
# vid_names = ["Phase_shift_3x1_0.5r.mp4", "Phase_shift_3x1_0.6r.mp4", "Phase_shift_3x1_0.7r.mp4", "Phase_shift_3x1_0.8r.mp4", "Phase_shift_3x1_0.9r.mp4", "Phase_shift_3x1_1.0r.mp4", "Phase_shift_3x1_1.1r.mp4", "Phase_shift_3x1_1.2r.mp4", "Phase_shift_3x1_1.3r.mp4"]
# plot_names = ["Phase_shift_3x1_0.5r.png", "Phase_shift_3x1_0.6r.png", "Phase_shift_3x1_0.7r.png", "Phase_shift_3x1_0.8r.png", "Phase_shift_3x1_0.9r.png", "Phase_shift_3x1_1.0r.png", "Phase_shift_3x1_1.1r.png", "Phase_shift_3x1_1.2r.png", "Phase_shift_3x1_1.3r.png"]
# data_filenames = ['Phase_shift_3x1_0.5r.csv', 'Phase_shift_3x1_0.6r.csv', 'Phase_shift_3x1_0.7r.csv', 'Phase_shift_3x1_0.8r.csv', 'Phase_shift_3x1_0.9r.csv', 'Phase_shift_3x1_1.0r.csv', 'Phase_shift_3x1_1.1r.csv', 'Phase_shift_3x1_1.2r.csv', 'Phase_shift_3x1_1.3r.csv']
# defined_friction = ['0.3', '0.3', '0.3', '0.3', '0.3', '0.3', '0.3', '0.3', '0.3']

file_paths = [r'\pipes\90_pipe_0.6_wide.xml']
vid_names = ["Phase_shift_test.mp4"]
plot_names = ["Phase_shift_test.png"]
data_filenames = ['Phase_shift_test.csv']
defined_friction = ['0.3']

########################## Define Global Variables ############################

## Define simulation parameters
Nseg = 6                # number of segments
dtSim = 1               # simulation timestep (ms)
tmax = 100000           # simulation runtime (ms)

## Define 3x1 peristaltic wave-form parameters
max_act = 0.31          # linear actuator length corresponding to maximum segment contraction (m)
rest_act = 0.48         # linear actuator length corresponding to minimum segment contraction (m)
up_time = 1000          # time for full contraction (ms)
hold_time = 1000        # time held as bridge segment (ms)
down_time = 1000        # time for full expansion (ms)

########################## Mujoco Simulation Setup ############################

sim_end = np.zeros(np.size(file_paths))
sim_start = np.zeros(np.size(file_paths))
sim_time = np.zeros(np.size(file_paths))

count = 0
for path in file_paths:
    sim_start[count] = time.time()

    # Include pipe xml in worm model xml file
    print("pipe in testing : ", path)
    include_path = work_dir + r"\worm_modeling" + path
    xml_file.findall('include')[0].attrib['file'] = include_path

    # If friction is not defined as a variable, use value from the xml file
    try:
        defined_friction
    except NameError:
        print('Friction not defined. Using default from .xml file.')
    else:
        xml_file.findall('.//geom')[0].attrib['friction'] = defined_friction[count]

    # Write changes to file
    xml_file.write(work_dir+r'\worm_modeling\worm_with_pipe.xml')

    ## Load model in Mujoco
    model_mj = mujoco.MjModel.from_xml_path(work_dir + r"\worm_modeling\worm_with_pipe.xml")
    data_mj = mujoco.MjData(model_mj)

    scene_option = mujoco.MjvOption()
    scene_option.flags[mujoco.mjtVisFlag.mjVIS_CONTACTPOINT] = True
    scene_option.flags[mujoco.mjtVisFlag.mjVIS_CONTACTFORCE] = False        # Set to True if you want to see contact force arrows

    ## Rendering Stuff 
    # Set colors in xml file using <rgba> for the bodies and assets (sky and floor, after the <contacts>)
    # for blue sky rgb1="0.3 0.5 0.7", for black sky rgb1="0 0 0"
    renderer = mujoco.Renderer(model_mj, 400, 900)            # can specify pixel dimensions here (480, 640) ALSO NEED TO CHANGE IN XML FILE
    # scene = mujoco.MjvScene(model_mj, maxgeom=10000)          # (Unused)

    ## Specify camera angle (multiple videos can be recorded at once by declaring and saving to multiple frames)
    ## Must change uncommented line both here and in the simulation loop later
    # renderer.update_scene(data_mj, camera='fixed', scene_option=scene_option)
    renderer.update_scene(data_mj, camera='top_down', scene_option=scene_option)
    # renderer.update_scene(data_mj, camera='top_down_shift', scene_option=scene_option)
    # renderer.update_scene(data_mj, camera='spiral', scene_option=scene_option)
    framerate = 100
    frames = []

    ## Initialize the mujoco model
    mujoco.mj_forward(model_mj,data_mj)

    ## Option to save a starting view of the model
    # mujoco.save(model_mj, 'mid_pipe_state.mjb')
    # viewer = mujoco.MjViewer(model_mj)
    # viewer.render()

    # Calculate total mass of all bodies defined in the xml model (for tuning purposes, will print value in kg)
    # Warning: This also includes pipes, run with no_pipe.xml for mass of the robot alone
    masses = model_mj.body_mass
    tot_mass = np.sum(masses)
    print("total mass = ", tot_mass)

    # Simulation time vectors
    tSim = np.arange(0, tmax, dtSim)
    numSteps = np.size(tSim)

    ## Set up tracking points to record movement
    tracker_sites = model_mj.sensor_objid[0:Nseg]

    site_pos = data_mj.site_xpos                        # records the x-y-z position of each site
    tracker_pos = np.zeros((np.size(tSim),3,Nseg))
    for j in range(Nseg):
        tracker_pos[0,:,j] = site_pos[tracker_sites[j],:]
    COM_pos = np.zeros((np.size(tSim),3))
    COM_pos[0,:] = np.mean(tracker_pos[0,:,:],axis=1)

    # Prepare sensor data vectors
    sensor_data = np.zeros((np.size(tSim), np.size(data_mj.sensordata)))
    sensor_data[0,:] = data_mj.sensordata[:]

    F_app = np.zeros((np.size(tSim), Nseg))
    F_app_l = np.zeros((np.size(tSim), Nseg))
    F_app_r = np.zeros((np.size(tSim), Nseg))
    # Seg3_diam = np.zeros((np.size(tSim)))       # Only used for tuning
    # Seg3_diam[0] = 0.32                         # Set equal to diameter (2*radius) used to generate worm robot xml file

    ## Time-based actuation signal generation: 3x1
    Act_sig = np.ones((np.size(tSim), Nseg))*rest_act
    ramp_time = up_time
    patt_time = up_time+hold_time+down_time
    num_waves = tmax/(ramp_time*Nseg)
    # print('number of waves: ', num_waves)
    num_waves = int(num_waves)

    Act_pattern = np.ones(up_time+hold_time+down_time)*rest_act
    Act_pattern[0:up_time] = np.linspace(rest_act,max_act,up_time)
    Act_pattern[up_time:up_time+hold_time] = np.ones(hold_time)*max_act
    Act_pattern[up_time+hold_time:up_time+hold_time+down_time] = np.linspace(max_act,rest_act,down_time)

    next_start = 0
    for j in range(Nseg):
        for i in range(num_waves+1):
            new_start = int(next_start+ramp_time*Nseg*i)
            if tmax-new_start < patt_time and tmax-new_start > 0:
                Act_sig[new_start:tmax,j] = Act_pattern[0:tmax-new_start]
            elif tmax-new_start <= 0:
                    q=0             #do nothing
            else:
                Act_sig[new_start:new_start+patt_time,j] = Act_pattern
        next_start = next_start+up_time

    ## Uncomment this section only to visualize the actuation pattern before running tests
    ## DO NOT leave uncommented for multi-iteration runs or you will have to close the plot after every iteration
    # color_mat = cm.rainbow(np.linspace(0, 1, Nseg))
    # fig = plt.figure(figsize = (12,4))
    # for j in range(Nseg):
    #     plt.plot(tSim, Act_sig[:,j], color = color_mat[j,:])
    # plt.ylabel('Act Sig', fontsize = 12, fontname="Arial")
    # plt.title('Actuation Signals', fontsize = 14, fontname="Arial", fontweight="bold")
    # plt.xlabel('Time (ms)', fontsize = 12, fontname="Arial")
    # plt.show()

    ############################### Simulation Run ################################
    
    l_bias = np.ones(Nseg)
    r_bias = np.ones(Nseg)
    feedback = np.zeros(np.size(tSim))
    l_feed_sig = np.ones(np.size(tSim))
    r_feed_sig = np.ones(np.size(tSim))
    l_old_feed_sig = 1
    r_old_feed_sig = 1
    l_min_sig = 1
    r_min_sig = 1
    Act_sig_l = np.ones((np.size(tSim), Nseg))*rest_act
    Act_sig_r = np.ones((np.size(tSim), Nseg))*rest_act

    cont_timer = 0
    for i in tqdm(range(numSteps), miniters=500):        
        ## Combined front tip contact sensor feedback signal (N)
        feedback[i] = -sensor_data[i,74]-sensor_data[i,75]+sensor_data[i,76]+sensor_data[i,77]              # -left contact force, +right contact force
        # print(feedback)

        for j in range(Nseg):
            if i != numSteps-1:
                ## Start the phase shifted turn after 1 cycle (so it can enter the pipe)
                if i <= 6000:                                       # Normal operation
                    Act_sig_l[i,j] = Act_sig[i,j]
                    data_mj.ctrl[2*j] = Act_sig_l[i,j]              # Left
                    Act_sig_r[i,j] = Act_sig[i,j]
                    data_mj.ctrl[2*j+1] = Act_sig_r[i,j]            # Right
                elif i > 6000 and i <= 9000:                        # Transition period
                    Act_sig_l[i,j] = Act_sig[i-up_time,j]
                    data_mj.ctrl[2*j] = Act_sig_l[i,j]
                    Act_sig_r[i,j] = Act_sig[i,j]
                    data_mj.ctrl[2*j+1] = Act_sig_r[i,j]
                    if j >= 3:
                        Act_sig_l[i,j] = Act_sig[i,j]
                        data_mj.ctrl[2*j] = Act_sig_l[i,j]
                        Act_sig_r[i,j] = Act_sig[i,j]
                        data_mj.ctrl[2*j+1] = Act_sig_r[i,j]
                else:                                               # Shifted operation
                    Act_sig_l[i,j] = Act_sig[i-up_time,j]           # shift the left side behavior
                    data_mj.ctrl[2*j] = Act_sig_l[i,j]
                    Act_sig_r[i,j] = Act_sig[i,j]
                    data_mj.ctrl[2*j+1] = Act_sig_r[i,j]

        l_old_feed_sig = l_feed_sig[i]
        r_old_feed_sig = r_feed_sig[i]
        cont_timer = cont_timer-1                                   # decay the contact timer

        ## Feed data.act back into mujoco for the next sim timestep
        mujoco.mj_step(model_mj, data_mj)

        ## Add frame to video(s) at intervals designated by the framerate
        if len(frames) < data_mj.time * framerate:
            # renderer.update_scene(data_mj, camera='fixed', scene_option=scene_option)
            renderer.update_scene(data_mj, camera='top_down', scene_option=scene_option)
            # renderer.update_scene(data_mj, camera='top_down_shift', scene_option=scene_option)
            # renderer.update_scene(data_mj, camera='spiral', scene_option=scene_option)
            pixels = renderer.render().copy()
            frames.append(pixels)

        ## Read data from mujoco and generate position data and sensor feedback
        if i != numSteps-1:

            # Sensor recordings
            sensor_data[i+1,:] = data_mj.sensordata[:]              # Data from all sensors
            
            # Motion tracking (top contact sensor is the marker)
            site_pos = data_mj.site_xpos
            for j in range(Nseg):
                tracker_pos[i+1,:,j] = site_pos[tracker_sites[j],:]
            COM_pos[i+1,:] = np.mean(tracker_pos[i+1,:,:],axis=1)
            
            # # Segment 3 diameter (used for tuning, requires "diam_meas" <tendon> in xml file)
            # Seg3_diam[i+1] = data_mj.ten_length[48]                     # [42] if single muscle segments

    media.write_video(vid_names[count], frames, fps=framerate)          # Save video
    renderer.close()

    sim_end[count] = time.time()
    sim_time[count] = sim_end[count]-sim_start[count]
    print("Scenario ", count+1, " took ", sim_time[count], " seconds to simulate", tmax/dtSim, " time steps")

    ################################# Plotting ####################################

    ## Left side
    # Plots 1 and 2: Left-Right position control signals
    # Plots 3-Nseg+2: Segment length recordings (stretch sensors)
    ## Right Side
    # Plots 1 and 2: X and Y axis tracking of each segment
    # Plot 3: Top contact sensor reading (can be replaced with sensor of your choice or the feedback signal)
    
    color_mat = cm.rainbow(np.linspace(0, 1, Nseg))

    fig = plt.figure(figsize = (16,13))
    Segment = "Segment "
    for ct in range(1, Nseg+3):
        ax = plt.subplot2grid((Nseg+2, 2), (ct-1, 0))
        if ct == 1:
            for j in range(Nseg):
                ax.plot(tSim, Act_sig_l[:,j], color = color_mat[j,:])
            ax.set_ylabel('Act Sig Left', fontsize = 12, fontname="Arial")
            ax.set_title('Actuation Signals', fontsize = 14, fontname="Arial", fontweight="bold")
        elif ct == 2:
            for j in range(Nseg):
                ax.plot(tSim, Act_sig_r[:,j], color = color_mat[j,:])
            ax.set_ylabel('Act Sig Right', fontsize = 12, fontname="Arial")
            ax.set_title('Actuation Signals', fontsize = 14, fontname="Arial", fontweight="bold")
        else:
            ax.plot(tSim, sensor_data[:,(ct-3)+Nseg*2], color = color_mat[ct-3,:])                          # Left
            ax.plot(tSim, sensor_data[:,(ct-3)+Nseg*3], color = 'Gray', linestyle='dashed')                 # Right
            ax.set_ylim(bottom = 0.065, top = 0.15)
            ax.set_ylabel('l (m)', fontsize = 12, fontname="Arial")
            ax.set_title(Segment + str(ct-2), fontsize = 14, fontname="Arial", fontweight="bold")
    ax.set_xlabel('Time (ms)', fontsize = 12, fontname="Arial")

    # straightline x-axis distance tracking
    tracker_pos_x = -1*(tracker_pos[:,0,:]-tracker_pos[0,0,:])
    COM_pos_x = -1*(COM_pos[:,0]-COM_pos[0,0])

    # y-axis tracking
    tracker_pos_y = -1*(tracker_pos[:,1,:]-tracker_pos[0,1,:])
    COM_pos_y = -1*(COM_pos[:,1]-COM_pos[0,1])

    # x-axis tracking plot
    ax = plt.subplot2grid((Nseg+2, 2), (0, 1), rowspan = 3)
    for j in range(Nseg):
        ax.plot(tSim, tracker_pos_x[:,j], color = color_mat[j,:])
    ax.plot(tSim, COM_pos_x, color = "Black")
    ax.set_ylabel('Distance Traveled X (m)', fontsize = 12, fontname="Arial")
    ax.set_title('Tracking Markers on Each Segment', fontsize = 14, fontname="Arial", fontweight="bold")
    ax.set_xlabel('Time (ms)', fontsize = 12, fontname="Arial")

    # y-axis tracking plot
    ax = plt.subplot2grid((Nseg+2, 2), (3, 1), rowspan = 3)
    for j in range(Nseg):
        ax.plot(tSim, tracker_pos_y[:,j], color = color_mat[j,:])
    ax.plot(tSim, COM_pos_y, color = "Black")
    ax.set_ylabel('Distance Traveled Y (m)', fontsize = 12, fontname="Arial")
    ax.set_title('Tracking Markers on Each Segment', fontsize = 14, fontname="Arial", fontweight="bold")
    ax.set_xlabel('Time (ms)', fontsize = 12, fontname="Arial")
    
    # Plot touch sensor data
    ax = plt.subplot2grid((Nseg+2, 2), (6, 1), rowspan = 2)
    for j in range(Nseg):
        # ax.plot(tSim, sensor_data[:,(j*4)+1], color = color_mat[j,:])
        ax.plot(tSim, sensor_data[:,j], color = color_mat[j,:])
    ax.set_ylabel('Touch (N)', fontsize = 12, fontname="Arial")
    ax.set_title('Top Touch Sensor', fontsize = 14, fontname="Arial", fontweight="bold")
    ax.set_xlabel('Time (ms)', fontsize = 12, fontname="Arial")

    plt.tight_layout()
    plt.savefig(plot_names[count], format="png")
    # plt.show()

    ###################### Write all data to an excel file ########################

    df = pd.DataFrame({'Time': tSim, 
                    'Seg 1 Pos': tracker_pos_x[:,0], 'Seg 2 Pos': tracker_pos_x[:,1], 'Seg 3 Pos': tracker_pos_x[:,2], 'Seg 4 Pos': tracker_pos_x[:,3], 'Seg 5 Pos': tracker_pos_x[:,4], 'Seg 6 Pos': tracker_pos_x[:,5], 'COM Pos': COM_pos_x,
                    'Seg 1 Y-Pos': tracker_pos_y[:,0], 'Seg 2 Y-Pos': tracker_pos_y[:,1], 'Seg 3 Y-Pos': tracker_pos_y[:,2], 'Seg 4 Y-Pos': tracker_pos_y[:,3], 'Seg 5 Y-Pos': tracker_pos_y[:,4], 'Seg 6 Y-Pos': tracker_pos_y[:,5], 'COM Y-Pos': COM_pos_y,
                    'Seg 1 Len_L': sensor_data[:,12], 'Seg 2 Len_L': sensor_data[:,13], 'Seg 3 Len_L': sensor_data[:,14], 'Seg 4 Len_L': sensor_data[:,15], 'Seg 5 Len_L': sensor_data[:,16], 'Seg 6 Len_L': sensor_data[:,17],
                    'Seg 1 Len_R': sensor_data[:,18], 'Seg 2 Len_R': sensor_data[:,19], 'Seg 3 Len_R': sensor_data[:,20], 'Seg 4 Len_R': sensor_data[:,21], 'Seg 5 Len_R': sensor_data[:,22], 'Seg 6 Len_R': sensor_data[:,23],
                    'Seg 1 Top Touch': sensor_data[:,0], 'Seg 2 Top Touch': sensor_data[:,1], 'Seg 3 Top Touch': sensor_data[:,2], 'Seg 4 Top Touch': sensor_data[:,3], 'Seg 5 Top Touch': sensor_data[:,4], 'Seg 6 Top Touch': sensor_data[:,5],
                    'Seg 1 Left Ten': sensor_data[:,24]*(-1), 'Seg 2 Left Ten': sensor_data[:,25]*(-1), 'Seg 3 Left Ten': sensor_data[:,26]*(-1), 'Seg 4 Left Ten': sensor_data[:,27]*(-1), 'Seg 5 Left Ten': sensor_data[:,28]*(-1), 'Seg 6 Left Ten': sensor_data[:,29]*(-1),
                    'Seg 1 Right Ten': sensor_data[:,30]*(-1), 'Seg 2 Right Ten': sensor_data[:,31]*(-1), 'Seg 3 Right Ten': sensor_data[:,32]*(-1), 'Seg 4 Right Ten': sensor_data[:,33]*(-1), 'Seg 5 Right Ten': sensor_data[:,34]*(-1), 'Seg 6 Right Ten': sensor_data[:,35]*(-1),
                    'Seg 1 Left Musc Len': sensor_data[:,36], 'Seg 2 Left Musc Len': sensor_data[:,37], 'Seg 3 Left Musc Len': sensor_data[:,38], 'Seg 4 Left Musc Len': sensor_data[:,39], 'Seg 5 Left Musc Len': sensor_data[:,40], 'Seg 6 Left Musc Len': sensor_data[:,41],
                    'Seg 1 Right Musc Len': sensor_data[:,42], 'Seg 2 Right Musc Len': sensor_data[:,43], 'Seg 3 Right Musc Len': sensor_data[:,44], 'Seg 4 Right Musc Len': sensor_data[:,45], 'Seg 5 Right Musc Len': sensor_data[:,46], 'Seg 6 Right Musc Len': sensor_data[:,47],
                    'Seg 1 TopL Touch': sensor_data[:,48], 'Seg 2 TopL Touch': sensor_data[:,49], 'Seg 3 TopL Touch': sensor_data[:,50], 'Seg 4 TopL Touch': sensor_data[:,51], 'Seg 5 TopL Touch': sensor_data[:,52], 'Seg 6 TopL Touch': sensor_data[:,53],
                    'Seg 1 BotL Touch': sensor_data[:,54], 'Seg 2 BotL Touch': sensor_data[:,55], 'Seg 3 BotL Touch': sensor_data[:,56], 'Seg 4 BotL Touch': sensor_data[:,57], 'Seg 5 BotL Touch': sensor_data[:,58], 'Seg 6 BotL Touch': sensor_data[:,59],
                    'Seg 1 TopR Touch': sensor_data[:,60], 'Seg 2 TopR Touch': sensor_data[:,61], 'Seg 3 TopR Touch': sensor_data[:,62], 'Seg 4 TopR Touch': sensor_data[:,63], 'Seg 5 TopR Touch': sensor_data[:,64], 'Seg 6 TopR Touch': sensor_data[:,65],
                    'Seg 1 BotR Touch': sensor_data[:,66], 'Seg 2 BotR Touch': sensor_data[:,67], 'Seg 3 BotR Touch': sensor_data[:,68], 'Seg 4 BotR Touch': sensor_data[:,69], 'Seg 5 BotR Touch': sensor_data[:,70], 'Seg 6 BotR Touch': sensor_data[:,71],
                    'Front Top Touch': sensor_data[:,72], 'Front Bot Touch': sensor_data[:,73], 'Front TL Touch': sensor_data[:,74], 'Front BL Touch': sensor_data[:,75], 'Front TR  Touch': sensor_data[:,76], 'Front BR  Touch': sensor_data[:,77],
                    'Seg 1 Act Left': Act_sig_l[:,0], 'Seg 2 Act Left': Act_sig_l[:,1], 'Seg 3 Act Left': Act_sig_l[:,2], 'Seg 4 Act Left': Act_sig_l[:,3], 'Seg 5 Act Left': Act_sig_l[:,4], 'Seg 6 Act Left': Act_sig_l[:,5],
                    'Seg 1 Act Right': Act_sig_r[:,0], 'Seg 2 Act Right': Act_sig_r[:,1], 'Seg 3 Act Right': Act_sig_r[:,2], 'Seg 4 Act Right': Act_sig_r[:,3], 'Seg 5 Act Right': Act_sig_r[:,4], 'Seg 6 Act Right': Act_sig_r[:,5],
                    'Feedback Sensor Reading': feedback, 'Left Feedback Control Signal': l_feed_sig, 'Right Feedback Control Signal': r_feed_sig
                    })
    df.insert(8, '', '', True)
    df.insert(16, '', '', True)
    df.insert(23, '', '', True)
    df.insert(30, '', '', True)
    df.insert(37, '', '', True)
    df.insert(44, '', '', True)
    df.insert(51, '', '', True)
    df.insert(58, '', '', True)
    df.insert(65, '', '', True)
    df.insert(72, '', '', True)
    df.insert(79, '', '', True)
    df.insert(86, '', '', True)
    df.insert(93, '', '', True)
    df.insert(100, '', '', True)
    df.insert(107, '', '', True)
    df.insert(114, '', '', True)
    df.to_csv(data_filenames[count], index=False)

    # Increase count to move on to next scenario in the file_paths array
    count = count+1