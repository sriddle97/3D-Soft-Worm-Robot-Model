## Time-Based controller for peristaltic locomotion
#
# Author: Shane Riddle
#
# Last edited: 03/13/2025
###############################################################################

# The worm robot is simulated in Mujoco using composite cable objects for 
# the structure, circumferential muscles for the actuators, and tendons 
# for the springs. The model can be altered in the xml file. 
# Note: Alterations to the xml file will likely require alterations to 
# the rest of this code. The order in which things are built impacts the order
# of the input and output arrays.

# Tubes used on the robot are made of polyethylene
# Link to tubes on McMaster-Carr:    https://www.mcmaster.com/53385K14/
# Polyethylene young's modulus = 0.3 GPa, shear modulus = 0.2 GPa
# Polyethylene density is ~0.94 g/cm^3 or 940 kg/m^3
# Tube OD is 0.25", ID is 0.17"  ->  cross-sectional area is 0.17 cm^2 
# so length density should be 16g/cm^3 or 0.016 kg/m of tubing

### XML Model Properties
# -  Bend parameter = Young's modulus (corrected from 0.3 GPa via iterative tuning)
# -  Twist parameter = Shear Modulus  (changed from 0.2 GPa proportional to young's modulus correction)
# -  Mujoco does not have tube shapes but does have cylinders/capsules. Solid capsules of radius 0.00299m were
#    used which gives the same area moment of inertia and therfore similar stiffness to the tube.
# -  Since this produces a different c/s area compared to the hollow tube the density was adjusted to 571.6 kg/m^3.
#    This maintains the correct mass/length ratio and overall mass of the model.
# -  Physical dimensions and stretch readings are in m
# -  Density is in kg/m^3 (default is 1000, ie. water) so mass is in kg
# -  Model timestep is 1 millisecond

# The muscle activation signal is time-based and pre-determined
# The muscle tension forces are determined using a force-length-velocity curve.

# This code runs the mujoco worm model with an open-loop time-based controller 
# for testing the mechanical properties of the worm robot and simulation environment.

############################## Import packages ################################

# Mujoco
import mujoco

# Basic Utility and Plotting Packages
import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
import xml.etree.ElementTree as ET
import time
import os
from tqdm import tqdm

# Movie Making Packages  (Use mediapy for Mujoco)
import matplotlib.animation as animation
import mediapy as media

####################### Input/Output File Organization ########################

# The mujoco data struct is organized such that each object is added to the model in order from the xml file
# This is important for interacting with data_mj

# Automatically determine the work directory
work_dir = os.getcwd()
print("String format :", work_dir)

# Import the worm robot model
xml_path = work_dir + r"\worm_modeling\worm_test_connector_mass.xml"
# xml_path = work_dir + r"\worm_modeling\worm_test_connector_mass_10e8.xml"
# xml_path = work_dir + r"\worm_modeling\worm_test_connector_mass_3e8.xml"
xml_file = ET.parse(xml_path)

# Change file_paths for pipes as needed. These get added to the worm xml in worm_with_pipe which is then used to run sim
# File names for videos, sheets, and plots go here, as well as frictions if varying those too

##### Test 1: Speed vs. Friction over flat ground. Various frictions, same stiffness (bend and twist params matching Wang robot)
##### Recomended to use the guardrails.xml instead of no_pipe.xml to mitigate drifting
# file_paths = [r'\pipes\no_pipe.xml', r'\pipes\no_pipe.xml', r'\pipes\no_pipe.xml', r'\pipes\no_pipe.xml', r'\pipes\no_pipe.xml', r'\pipes\no_pipe.xml', r'\pipes\no_pipe.xml', r'\pipes\no_pipe.xml', r'\pipes\no_pipe.xml', r'\pipes\no_pipe.xml', r'\pipes\no_pipe.xml']         # flat ground alone
# file_paths = [r'\pipes\guardrails.xml', r'\pipes\guardrails.xml', r'\pipes\guardrails.xml', r'\pipes\guardrails.xml', r'\pipes\guardrails.xml', r'\pipes\guardrails.xml', r'\pipes\guardrails.xml', r'\pipes\guardrails.xml', r'\pipes\guardrails.xml', r'\pipes\guardrails.xml', r'\pipes\guardrails.xml']
# vid_names = ["Time_no_pipe_0.01f.mp4", "Time_no_pipe_0.1f.mp4", "Time_no_pipe_0.2f.mp4", "Time_no_pipe_0.3f.mp4", "Time_no_pipe_0.4f.mp4", "Time_no_pipe_0.5f.mp4", "Time_no_pipe_0.6f.mp4", "Time_no_pipe_0.7f.mp4", "Time_no_pipe_0.8f.mp4", "Time_no_pipe_0.9f.mp4", "Time_no_pipe_1.0f.mp4"]
# plot_names = ["Time_no_pipe_0.01f.png", "Time_no_pipe_0.1f.png", "Time_no_pipe_0.2f.png", "Time_no_pipe_0.3f.png", "Time_no_pipe_0.4f.png", "Time_no_pipe_0.5f.png", "Time_no_pipe_0.6f.png", "Time_no_pipe_0.7f.png", "Time_no_pipe_0.8f.png", "Time_no_pipe_0.9f.png", "Time_no_pipe_1.0f.png"]
# data_filenames = ['Time_no_pipe_0.01f.csv', 'Time_no_pipe_0.1f.csv', 'Time_no_pipe_0.2f.csv', 'Time_no_pipe_0.3f.csv', 'Time_no_pipe_0.4f.csv', 'Time_no_pipe_0.5f.csv', 'Time_no_pipe_0.6f.csv', 'Time_no_pipe_0.7f.csv', 'Time_no_pipe_0.8f.csv', 'Time_no_pipe_0.9f.csv', 'Time_no_pipe_1.0f.csv']
# defined_friction = ['0.01', '0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9', '1.0']


##### Test 2: Speed vs. Friction in 0.5m radius of curvature 90 degree pipe. Various frictions, same stiffness (bend and twist params matching Wang robot)
# file_paths = [r'\pipes\90_pipe_0.5_thin.xml', r'\pipes\90_pipe_0.5_thin.xml', r'\pipes\90_pipe_0.5_thin.xml', r'\pipes\90_pipe_0.5_thin.xml', r'\pipes\90_pipe_0.5_thin.xml', r'\pipes\90_pipe_0.5_thin.xml', r'\pipes\90_pipe_0.5_thin.xml', r'\pipes\90_pipe_0.5_thin.xml', r'\pipes\90_pipe_0.5_thin.xml', r'\pipes\90_pipe_0.5_thin.xml']
# vid_names = ["Time_90deg_0.5r_0.1f_thin.mp4", "Time_90deg_0.5r_0.2f_thin.mp4", "Time_90deg_0.5r_0.3f_thin.mp4", "Time_90deg_0.5r_0.35f_thin.mp4", "Time_90deg_0.5r_0.4f_thin.mp4", "Time_90deg_0.5r_0.5f_thin.mp4", "Time_90deg_0.5r_0.6f_thin.mp4", "Time_90deg_0.5r_0.7f_thin.mp4", "Time_90deg_0.5r_0.8f_thin.mp4", "Time_90deg_0.5r_0.9f_thin.mp4"]
# plot_names = ["Time_90deg_0.5r_0.1f_thin.png", "Time_90deg_0.5r_0.2f_thin.png", "Time_90deg_0.5r_0.3f_thin.png", "Time_90deg_0.5r_0.35f_thin.png", "Time_90deg_0.5r_0.4f_thin.png", "Time_90deg_0.5r_0.5f_thin.png", "Time_90deg_0.5r_0.6f_thin.png", "Time_90deg_0.5r_0.7f_thin.png", "Time_90deg_0.5r_0.8f_thin.png", "Time_90deg_0.5r_0.9f_thin.png"]
# data_filenames = ['Time_90deg_0.5r_0.1f_thin.csv', 'Time_90deg_0.5r_0.2f_thin.csv', 'Time_90deg_0.5r_0.3f_thin.csv', 'Time_90deg_0.5r_0.35f_thin.csv', 'Time_90deg_0.5r_0.4f_thin.csv', 'Time_90deg_0.5r_0.5f_thin.csv', 'Time_90deg_0.5r_0.6f_thin.csv', 'Time_90deg_0.5r_0.7f_thin.csv', 'Time_90deg_0.5r_0.8f_thin.csv', 'Time_90deg_0.5r_0.9f_thin.csv']
# defined_friction = ['0.1', '0.2', '0.3', '0.35', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9']


##### Test 3: Speed vs. Radius of Curvature. Various 90 degree pipe curvatures, same friction, same stiffness per set of tests
##### Run with each of the model stiffnesses (bend param = 2 GPa, 1 GPa, and 0.3 GPa) and straight pipe for "infinite" radius of curvature
# file_paths = [r'\pipes\90_pipe_0.2_thin.xml', r'\pipes\90_pipe_0.3_thin.xml', r'\pipes\90_pipe_0.4_thin.xml', r'\pipes\90_pipe_0.5_thin.xml', r'\pipes\90_pipe_0.6_thin.xml', r'\pipes\90_pipe_0.7_thin.xml', r'\pipes\90_pipe_0.8_thin.xml', r'\pipes\90_pipe_0.9_thin.xml', r'\pipes\straight_pipe_thin.xml']
# vid_names = ["Time_90deg_0.2r_thin.mp4", "Time_90deg_0.3r_thin.mp4", "Time_90deg_0.4r_thin.mp4", "Time_90deg_0.5r_thin.mp4", "Time_90deg_0.6r_thin.mp4", "Time_90deg_0.7r_thin.mp4", "Time_90deg_0.8r_thin.mp4", "Time_90deg_0.9r_thin.mp4", "Time_straight_pipe_thin_20e8.mp4"]
# plot_names = ["Time_90deg_0.2r_thin.png", "Time_90deg_0.3r_thin.png", "Time_90deg_0.4r_thin.png", "Time_90deg_0.5r_thin.png", "Time_90deg_0.6r_thin.png", "Time_90deg_0.7r_thin.png", "Time_90deg_0.8r_thin.png", "Time_90deg_0.9r_thin.png", "Time_straight_pipe_thin_20e8.png"]
# data_filenames = ['Time_90deg_0.2r_thin.csv', 'Time_90deg_0.3r_thin.csv', 'Time_90deg_0.4r_thin.csv', 'Time_90deg_0.5r_thin.csv', 'Time_90deg_0.6r_thin.csv', 'Time_90deg_0.7r_thin.csv', 'Time_90deg_0.8r_thin.csv', 'Time_90deg_0.9r_thin.csv', 'Time_straight_pipe_thin_20e8.csv']
# defined_friction = ['0.3', '0.3', '0.3', '0.3', '0.3', '0.3', '0.3', '0.3', '0.3']

# file_paths = [r'\pipes\90_pipe_0.2_thin.xml', r'\pipes\90_pipe_0.3_thin.xml', r'\pipes\90_pipe_0.4_thin.xml', r'\pipes\90_pipe_0.5_thin.xml', r'\pipes\90_pipe_0.6_thin.xml', r'\pipes\90_pipe_0.7_thin.xml', r'\pipes\90_pipe_0.8_thin.xml', r'\pipes\90_pipe_0.9_thin.xml', r'\pipes\straight_pipe_thin.xml']
# vid_names = ["Time_90deg_0.2r_thin_10e8.mp4", "Time_90deg_0.3r_thin_10e8.mp4", "Time_90deg_0.4r_thin_10e8.mp4", "Time_90deg_0.5r_thin_10e8.mp4", "Time_90deg_0.6r_thin_10e8.mp4", "Time_90deg_0.7r_thin_10e8.mp4", "Time_90deg_0.8r_thin_10e8.mp4", "Time_90deg_0.9r_thin_10e8.mp4", "Time_straight_pipe_thin_10e8.mp4"]
# plot_names = ["Time_90deg_0.2r_thin_10e8.png", "Time_90deg_0.3r_thin_10e8.png", "Time_90deg_0.4r_thin_10e8.png", "Time_90deg_0.5r_thin_10e8.png", "Time_90deg_0.6r_thin_10e8.png", "Time_90deg_0.7r_thin_10e8.png", "Time_90deg_0.8r_thin_10e8.png", "Time_90deg_0.9r_thin_10e8.png", "Time_straight_pipe_thin_10e8.png"]
# data_filenames = ['Time_90deg_0.2r_thin_10e8.csv', 'Time_90deg_0.3r_thin_10e8.csv', 'Time_90deg_0.4r_thin_10e8.csv', 'Time_90deg_0.5r_thin_10e8.csv', 'Time_90deg_0.6r_thin_10e8.csv', 'Time_90deg_0.7r_thin_10e8.csv', 'Time_90deg_0.8r_thin_10e8.csv', 'Time_90deg_0.9r_thin_10e8.csv', 'Time_straight_pipe_thin_10e8.csv']
# defined_friction = ['0.3', '0.3', '0.3', '0.3', '0.3', '0.3', '0.3', '0.3', '0.3']

# file_paths = [r'\pipes\90_pipe_0.2_thin.xml', r'\pipes\90_pipe_0.3_thin.xml', r'\pipes\90_pipe_0.4_thin.xml', r'\pipes\90_pipe_0.5_thin.xml', r'\pipes\90_pipe_0.6_thin.xml', r'\pipes\90_pipe_0.7_thin.xml', r'\pipes\90_pipe_0.8_thin.xml', r'\pipes\90_pipe_0.9_thin.xml', r'\pipes\straight_pipe_thin.xml']
# vid_names = ["Time_90deg_0.2r_thin_3e8.mp4", "Time_90deg_0.3r_thin_3e8.mp4", "Time_90deg_0.4r_thin_3e8.mp4", "Time_90deg_0.5r_thin_3e8.mp4", "Time_90deg_0.6r_thin_3e8.mp4", "Time_90deg_0.7r_thin_3e8.mp4", "Time_90deg_0.8r_thin_3e8.mp4", "Time_90deg_0.9r_thin_3e8.mp4", "Time_straight_pipe_thin_3e8.mp4"]
# plot_names = ["Time_90deg_0.2r_thin_3e8.png", "Time_90deg_0.3r_thin_3e8.png", "Time_90deg_0.4r_thin_3e8.png", "Time_90deg_0.5r_thin_3e8.png", "Time_90deg_0.6r_thin_3e8.png", "Time_90deg_0.7r_thin_3e8.png", "Time_90deg_0.8r_thin_3e8.png", "Time_90deg_0.9r_thin_3e8.png", "Time_straight_pipe_thin_3e8.png"]
# data_filenames = ['Time_90deg_0.2r_thin_3e8.csv', 'Time_90deg_0.3r_thin_3e8.csv', 'Time_90deg_0.4r_thin_3e8.csv', 'Time_90deg_0.5r_thin_3e8.csv', 'Time_90deg_0.6r_thin_3e8.csv', 'Time_90deg_0.7r_thin_3e8.csv', 'Time_90deg_0.8r_thin_3e8.csv', 'Time_90deg_0.9r_thin_3e8.csv', 'Time_straight_pipe_thin_3e8.csv']
# defined_friction = ['0.3', '0.3', '0.3', '0.3', '0.3', '0.3', '0.3', '0.3', '0.3']


##### Single Iterations of the above tests
# file_paths = [r'\pipes\no_pipe.xml']
# vid_names = ["Time_no_pipe_0.3f.mp4"]
# plot_names = ["Time_no_pipe_0.3f.png"]
# data_filenames = ['Time_no_pipe_0.3f.csv']
# defined_friction = ['0.3']

# file_paths = [r'\pipes\90_pipe_0.5_thin.xml']
# vid_names = ["Time_90deg_0.5r_thin_0.3f.mp4"]
# plot_names = ["Time_90deg_0.5r_thin_0.3f.png"]
# data_filenames = ['Time_90deg_0.5r_thin_0.3f.csv']
# defined_friction = ['0.3']

# file_paths = [r'\pipes\90_pipe_0.4_thin.xml']
# vid_names = ["Time_90deg_0.4r_thin.mp4"]
# plot_names = ["Time_90deg_0.4r_thin.png"]
# data_filenames = ['Time_90deg_0.4r_thin.csv']
# defined_friction = ['0.3']


##### Dummy setup for not overwriting other results when testing new configurations
file_paths = [r'\pipes\no_pipe.xml']
vid_names = ["Time_dummy.mp4"]
plot_names = ["Time_dummy.png"]
data_filenames = ['Time_dummy.csv']
defined_friction = ['0.3']

# # file_paths = [r'\pipes\guardrails.xml']
# # file_paths = [r'\pipes\no_pipe.xml']
# file_paths = [r'\pipes\straight_pipe_thin.xml']
# vid_names = ["pos_test.mp4"]
# plot_names = ["pos_test.png"]
# data_filenames = ['pos_test.csv']
# defined_friction = ['0.3']

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

    # Load model in Mujoco
    model_mj = mujoco.MjModel.from_xml_path(work_dir + r"\worm_modeling\worm_with_pipe.xml")
    data_mj = mujoco.MjData(model_mj)

    # Rendering Stuff 
    # Set colors in xml file using <rgba> for the bodies and assets (sky and floor, after the <contacts>)
    # for blue sky rgb1="0.3 0.5 0.7", for black sky rgb1="0 0 0"
    renderer = mujoco.Renderer(model_mj, 400, 900)              # can specify pixel dimensions here (480, 640) ALSO NEED TO CHANGE IN XML FILE
    renderer.update_scene(data_mj, camera='fixed')              # Change camera angle here if needed
    # renderer.update_scene(data_mj, camera='top_down')
    framerate = 100
    frames = []
    mujoco.mj_forward(model_mj,data_mj)                         # Initialize the mujoco model

    # Calculate total mass of all bodies defined in the xml model (for tuning purposes)
    # Warning: This also includes pipes, run with no_pipe for mass of the robot alone
    masses = model_mj.body_mass
    tot_mass = np.sum(masses)
    print("total mass = ", tot_mass)


    # Simulation Time (all in ms)
    Nseg = 6            # number of segments
    dtSim = 1           # millisecond
    tmax = 10000
    tSim = np.arange(0, tmax, dtSim)
    numSteps = np.size(tSim)


    # Set up tracking points to record movement
    x_positions = data_mj.site_xpos
    pos_1 = np.zeros((np.size(tSim),3))
    pos_2 = np.zeros((np.size(tSim),3))
    pos_3 = np.zeros((np.size(tSim),3))
    pos_4 = np.zeros((np.size(tSim),3))
    pos_5 = np.zeros((np.size(tSim),3))
    pos_6 = np.zeros((np.size(tSim),3))
    pos_1[0,:] = x_positions[126,:]
    pos_2[0,:] = x_positions[89,:]
    pos_3[0,:] = x_positions[72,:]
    pos_4[0,:] = x_positions[35,:]
    pos_5[0,:] = x_positions[138,:]
    pos_6[0,:] = x_positions[101,:]
    COM_pos = np.zeros((np.size(tSim),3))
    COM_pos[0,:] = np.mean([[pos_1[0,:]], [pos_2[0,:]], [pos_3[0,:]], [pos_4[0,:]], [pos_5[0,:]], [pos_6[0,:]]],axis=0)

    # Sensor Data
    sensor_data = np.zeros((np.size(tSim), np.size(data_mj.sensordata)))
    sensor_data[0,:] = data_mj.sensordata[:]

    # Initialize actuator and seg diam vectors
    F_app = np.zeros((np.size(tSim)))
    Seg3_diam = np.zeros((np.size(tSim)))
    Seg3_diam[0] = 0.32                         # Set equal to diameter (2*radius) used to generate worm robot xml file


    # #### Time-based actuation signal vector generation (2x2 waveform)
    # Act_sig = np.zeros((np.size(tSim), Nseg))
    # max_act = 1
    # up_time = 1000              #500
    # hold_time = 1000
    # down_time = 1000            #500
    # ramp_time = up_time+hold_time
    # patt_time = up_time+hold_time+down_time

    # # num_waves = tmax/(ramp_time*Nseg/2+down_time)
    # num_waves = tmax/(ramp_time*Nseg/2)
    # # print('number of waves: ', num_waves)
    # num_waves = int(num_waves)

    # Act_pattern = np.zeros(up_time+hold_time+down_time)
    # Act_pattern[0:up_time] = np.linspace(0,max_act,up_time)
    # Act_pattern[up_time:up_time+hold_time] = np.ones(hold_time)
    # Act_pattern[up_time+hold_time:up_time+hold_time+down_time] = np.linspace(max_act,0,down_time)

    # next_start = 0
    # for j in range(Nseg):
    #     for i in range(num_waves+1):
    #         new_start = int(next_start+ramp_time*Nseg/2*i)
    #         if tmax-new_start < patt_time and tmax-new_start > 0:
    #             Act_sig[new_start:tmax,j] = Act_pattern[0:tmax-new_start]
    #         elif tmax-new_start <= 0:
    #                 q=0             #do nothing
    #         else:
    #             Act_sig[new_start:new_start+patt_time,j] = Act_pattern
    #     next_start = next_start+up_time+hold_time


    #### Time-based actuation signal vector generation (3x1 waveform, with bridge segment)
    Act_sig = np.zeros((np.size(tSim), Nseg))
    max_act = 1
    up_time = 1000
    hold_time = 1000
    down_time = 1000
    ramp_time = up_time
    patt_time = up_time+hold_time+down_time

    # num_waves = tmax/(ramp_time*Nseg+hold_time+down_time)
    num_waves = tmax/(ramp_time*Nseg)
    # print('number of waves: ', num_waves)
    num_waves = int(num_waves)

    Act_pattern = np.zeros(up_time+hold_time+down_time)
    Act_pattern[0:up_time] = np.linspace(0,max_act,up_time)
    Act_pattern[up_time:up_time+hold_time] = np.ones(hold_time)
    Act_pattern[up_time+hold_time:up_time+hold_time+down_time] = np.linspace(max_act,0,down_time)

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

    # Uncomment this section only to visualize the actuation pattern before running tests
    # color_mat = cm.rainbow(np.linspace(0, 1, Nseg))
    # fig = plt.figure(figsize = (12,4))
    # for j in range(Nseg):
    #     plt.plot(tSim, Act_sig[:,j], color = color_mat[j,:])
    # plt.ylabel('Act Sig', fontsize = 12, fontname="Arial")
    # plt.title('Actuation Signals', fontsize = 14, fontname="Arial", fontweight="bold")
    # plt.xlabel('Time (ms)', fontsize = 12, fontname="Arial")
    # plt.show()


    ############################### Simulation Run ################################

    num_sens = 4                                        # 4 sensors per segment, Nseg of each: touch_top, touch_bot, stretch_left, stretch_right
    for i in tqdm(range(numSteps), miniters=500):
        for j in range(Nseg):
            if i != numSteps-1:
                # Send actuation signals to each muscle
                data_mj.act[j] = Act_sig[i,j]

        # Feed data.act back into the mujoco simulation
        mujoco.mj_step(model_mj, data_mj)

        # Add frame to video for each time step
        if len(frames) < data_mj.time * framerate:
            renderer.update_scene(data_mj, camera='fixed')
            # renderer.update_scene(data_mj, camera='top_down')
            pixels = renderer.render().copy()
            frames.append(pixels)

        # Read data from mujoco and generate position data and sensor feedback
        for j in range(Nseg):

            if i != numSteps-1:
                # Sensor recordings and motion tracking
                sensor_data[i+1,:] = data_mj.sensordata[:]          # Data from all sensors

                # Tendonpos (in sensordata) is the same as ten_length, copy-pasted
                # l[i+1,j] = data_mj.ten_length[2*j+Nseg+1]           # Tendon lengths, calculated by Mujoco (noise must be added manually if desired)
                
                # Temporary until I figure out algorithm for site spacing (COM estimated using all segment positions)
                x_positions = data_mj.site_xpos                     # Cartesian coordinates for all sites, array of size [n x 3] where n = number of sites
                pos_1[i+1,:] = x_positions[126,:]
                pos_2[i+1,:] = x_positions[89,:]
                pos_3[i+1,:] = x_positions[72,:]
                pos_4[i+1,:] = x_positions[35,:]
                pos_5[i+1,:] = x_positions[138,:]
                pos_6[i+1,:] = x_positions[101,:]
                COM_pos[i+1,:] = np.mean([[pos_1[i+1,:]], [pos_2[i+1,:]], [pos_3[i+1,:]], [pos_4[i+1,:]], [pos_5[i+1,:]], [pos_6[i+1,:]]],axis=0)

                #### The following are used to track Segment 3's actuator muscle tension and diameter for model tuning purposes.
                #### Add the tendon and sensor only AFTER all other tendons/sensors in the xml file then verify ten_length and sensor_data indices

                # Segment 3 contraction force data (requires <force> or <actuatorfrc> sensor in xml file)
                # F_app[i+1] = np.sqrt(data_mj.sensordata[24]**2+data_mj.sensordata[25]**2+data_mj.sensordata[26]**2)                         # <force>
                F_app[i+1] = data_mj.sensordata[24]*(-1)                                                                                    # <actuatorfrc>

                # Segment 3 diameter (requires "diam_meas" <tendon> in xml file)
                Seg3_diam[i+1] = data_mj.ten_length[42]

    media.write_video(vid_names[count], frames, fps=framerate)          # Save video
    renderer.close()

    sim_end[count] = time.time()
    sim_time[count] = sim_end[count]-sim_start[count]
    print("Scenario ", count+1, " took ", sim_time[count], " seconds to simulate", tmax/dtSim, " time steps")


    ########################################################## Plotting ############################################################
    # Plot 1: Control signals for each time step
    # Plots 2-Nseg: Segment lengths over time           (sensor noise must be added manually if desired)
    
    color_mat = cm.rainbow(np.linspace(0, 1, Nseg))

    fig = plt.figure(figsize = (16,13))
    
    Segment = "Segment "
    for ct in range(1, Nseg+2):
        ax = plt.subplot2grid((Nseg+1, 2), (ct-1, 0))
        if ct == 1:
            for j in range(Nseg):
                ax.plot(tSim, Act_sig[:,j], color = color_mat[j,:])
            ax.set_ylabel('Act Sig', fontsize = 12, fontname="Arial")
            ax.set_title('Actuation Signals', fontsize = 14, fontname="Arial", fontweight="bold")
        else:
            ax.plot(tSim, sensor_data[:,(ct-2)+Nseg*2], color = color_mat[ct-2,:])
            ax.set_ylim(bottom = 0.065, top = 0.15)
            ax.set_ylabel('l (m)', fontsize = 12, fontname="Arial")
            ax.set_title(Segment + str(ct-1), fontsize = 14, fontname="Arial", fontweight="bold")
    ax.set_xlabel('Time (ms)', fontsize = 12, fontname="Arial")


    # use this if you want straightline (x-axis) distance tracking
    pos_1p = -1*(pos_1[:,0]-pos_1[0,0])
    pos_2p = -1*(pos_2[:,0]-pos_2[0,0])
    pos_3p = -1*(pos_3[:,0]-pos_3[0,0])
    pos_4p = -1*(pos_4[:,0]-pos_4[0,0])
    pos_5p = -1*(pos_5[:,0]-pos_5[0,0])
    pos_6p = -1*(pos_6[:,0]-pos_6[0,0])
    COM_posp = -1*(COM_pos[:,0]-COM_pos[0,0])

    # y-axis tracking
    pos_1p_y = -1*(pos_1[:,1]-pos_1[0,1])
    pos_2p_y = -1*(pos_2[:,1]-pos_2[0,1])
    pos_3p_y = -1*(pos_3[:,1]-pos_3[0,1])
    pos_4p_y = -1*(pos_4[:,1]-pos_4[0,1])
    pos_5p_y = -1*(pos_5[:,1]-pos_5[0,1])
    pos_6p_y = -1*(pos_6[:,1]-pos_6[0,1])
    COM_posp_y = -1*(COM_pos[:,1]-COM_pos[0,1])

    # x-axis tracking plot
    ax = plt.subplot2grid((Nseg+1, 2), (0, 1), rowspan = 3)
    ax.plot(tSim, pos_1p, color = color_mat[0,:])
    ax.plot(tSim, pos_2p, color = color_mat[1,:])
    ax.plot(tSim, pos_3p, color = color_mat[2,:])
    ax.plot(tSim, pos_4p, color = color_mat[3,:])
    ax.plot(tSim, pos_5p, color = color_mat[4,:])
    ax.plot(tSim, pos_6p, color = color_mat[5,:])
    ax.plot(tSim, COM_posp, color = "Black")
    ax.set_ylabel('Distance Traveled X (m)', fontsize = 12, fontname="Arial")
    ax.set_title('Tracking Markers on Each Segment', fontsize = 14, fontname="Arial", fontweight="bold")
    ax.set_xlabel('Time (ms)', fontsize = 12, fontname="Arial")

    # y-axis tracking plot
    ax = plt.subplot2grid((Nseg+1, 2), (3, 1), rowspan = 3)
    ax.plot(tSim, pos_1p_y, color = color_mat[0,:])
    ax.plot(tSim, pos_2p_y, color = color_mat[1,:])
    ax.plot(tSim, pos_3p_y, color = color_mat[2,:])
    ax.plot(tSim, pos_4p_y, color = color_mat[3,:])
    ax.plot(tSim, pos_5p_y, color = color_mat[4,:])
    ax.plot(tSim, pos_6p_y, color = color_mat[5,:])
    ax.plot(tSim, COM_posp_y, color = "Black")
    ax.set_ylabel('Distance Traveled Y (m)', fontsize = 12, fontname="Arial")
    ax.set_title('Tracking Markers on Each Segment', fontsize = 14, fontname="Arial", fontweight="bold")
    ax.set_xlabel('Time (ms)', fontsize = 12, fontname="Arial")
    
    # Plot touch sensor data
    ax = plt.subplot2grid((Nseg+1, 2), (6, 1), rowspan = 1)
    for j in range(Nseg):
        ax.plot(tSim, sensor_data[:,j], color = color_mat[j,:])
    ax.set_ylabel('Touch (N)', fontsize = 12, fontname="Arial")
    ax.set_title('Touch Data', fontsize = 14, fontname="Arial", fontweight="bold")
    ax.set_xlabel('Time (ms)', fontsize = 12, fontname="Arial")

    plt.tight_layout()
    plt.savefig(plot_names[count], format="png")
    # plt.show()


    ###################### Write all data to an excel file ########################
    import pandas as pd
    from openpyxl import load_workbook

    df = pd.DataFrame({'Time': tSim, 
                    'Seg 1 Pos': pos_1p, 'Seg 2 Pos': pos_2p, 'Seg 3 Pos': pos_3p, 'Seg 4 Pos': pos_4p, 'Seg 5 Pos': pos_5p, 'Seg 6 Pos': pos_6p, 'COM Pos': COM_posp,
                    'Seg 1 Y-Pos': pos_1p_y, 'Seg 2 Y-Pos': pos_2p_y, 'Seg 3 Y-Pos': pos_3p_y, 'Seg 4 Y-Pos': pos_4p_y, 'Seg 5 Y-Pos': pos_5p_y, 'Seg 6 Y-Pos': pos_6p_y, 'COM Y-Pos': COM_posp_y,
                    'Seg 1 Len': sensor_data[:,12], 'Seg 2 Len': sensor_data[:,13], 'Seg 3 Len': sensor_data[:,14], 'Seg 4 Len': sensor_data[:,15], 'Seg 5 Len': sensor_data[:,16], 'Seg 6 Len': sensor_data[:,17],
                    'Seg 1 Touch': sensor_data[:,0], 'Seg 2 Touch': sensor_data[:,1], 'Seg 3 Touch': sensor_data[:,2], 'Seg 4 Touch': sensor_data[:,3], 'Seg 5 Touch': sensor_data[:,4], 'Seg 6 Touch': sensor_data[:,5],
                    'Tension in Muscle': F_app, 'Diameter of Seg 3': Seg3_diam
                    })
    df.insert(8, '', '', True)
    df.insert(16, '', '', True)
    df.insert(23, '', '', True)
    df.insert(30, '', '', True)
    df.to_csv(data_filenames[count], index=False)

    # Increase count to move on to next scenario in the file_paths array
    count = count+1