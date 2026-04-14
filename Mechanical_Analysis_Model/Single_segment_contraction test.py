## Single segment contraction for peristaltic model tuning
#
# Author: Shane Riddle
#
# Last edited: 03/13/2025
#########################################################################

# This script can be used to tune the model for a desired radial stiffness.
# It contracts the actuator muscle of a middle segment and records
# the diameter of the segment and tension of the muscle tendon.
# We used this to match Force vs. Diameter data gathered from the Wang robot

# To change the Force vs. Diameter behavior of the model you can tune the
# muscle actuator and/or bend and twist composite body parameters.
# Use in conjunction with the FLV.m file to tune the muscle forces

########################### Import packages #############################

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

# Automatically get work directory
work_dir = os.getcwd()
print("String format :", work_dir)

xml_path = work_dir + r"\worm_modeling\worm_test_connector_mass.xml"
xml_file = ET.parse(xml_path)

# Recomended to have friction set to 0 to mitigate slip effects that could skew the tuning process
##### Control contraction and expansion gradually for hysteresis analysis
# file_paths = [r'\pipes\no_pipe.xml']
# vid_names = ["Seg3_no_pipe_0.0f_20e8_updown.mp4"]
# plot_names = ["Seg3_no_pipe_0.0f_20e8_updown.png"]
# data_filenames = ['Seg3_no_pipe_0.0f_20e8_updown.csv']
# defined_friction = ['0.0']

##### Control contraction gradually and release actuator signal for rapid expansion
file_paths = [r'\pipes\no_pipe.xml']
vid_names = ["Seg3_no_pipe_0.0f_20e8.mp4"]
plot_names = ["Seg3_no_pipe_0.0f_20e8.png"]
data_filenames = ['Seg3_no_pipe_0.0f_20e8.csv']
defined_friction = ['0.0']

######################### Mujoco Simulation Setup ############################

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

    # Simulation Time(ms) Stuff
    Nseg = 6            # number of segments
    dtSim = 1           # millisecond
    tmax = 4000          #4000 for normal contraction, 6000 for hysteresis analysis
    tSim = np.arange(0, tmax, dtSim)
    numSteps = np.size(tSim)

    # Sensor Data
    sensor_data = np.zeros((np.size(tSim), np.size(data_mj.sensordata)))
    sensor_data[0,:] = data_mj.sensordata[:]

    # Initialize actuator and seg diam vectors
    F_app = np.zeros((np.size(tSim)))
    Seg3_diam = np.zeros((np.size(tSim)))
    Seg3_diam[0] = 0.32                         # Set equal to diameter (2*radius) used to generate worm robot xml file

    ############################### Simulation Run ################################
    # for i in range(numSteps):
    for i in tqdm(range(numSteps), miniters=500):
        for j in range(Nseg):
            if i != numSteps-1:

                # Contract just segment 3 gradually
                if i < 2850:
                    data_mj.act[2] = min(i/2900,1)
                # elif i>=2851 and i<3850:              # Uncomment this if ramp & hold is desired, rather than just ramp
                #     data_mj.act[2] = 1
                else:
                    data_mj.act[2] = 0

                # # Contract and re-expand gradually (hysteresis test)
                # if i < 2850:
                #     data_mj.act[2] = min(i/2900,0.99)
                # elif i>=2850 and i<5700:
                #     data_mj.act[2] = max(0.98-(i-2850)/2900,0)          # 2850/2900=0.983, use 0.98 as start for down slope
                # else:
                #     data_mj.act[2] = 0

        # feed data.act back into the mujoco simulation
        mujoco.mj_step(model_mj, data_mj)

        # Add frame to video for each time step
        if len(frames) < data_mj.time * framerate:
            renderer.update_scene(data_mj, camera='fixed')
            # renderer.update_scene(data_mj, camera='top_down')
            pixels = renderer.render().copy()
            frames.append(pixels)

        # read data from mujoco and generate position data and sensor feedback
        for j in range(Nseg):

            if i != numSteps-1:
                # Sensor recordings and motion tracking
                sensor_data[i+1,:] = data_mj.sensordata[:]          # Data from all sensors

                #### The following are used to track Segment 3's actuator muscle tension and diameter for model tuning purposes.
                #### Add the tendon and sensor only AFTER all other tendons/sensors in the xml file then verify ten_length and sensor_data indices

                # Segment 3 contraction force data (requires <force> or <actuatorfrc> sensor in xml file)
                # F_app[i+1] = np.sqrt(data_mj.sensordata[24]**2+data_mj.sensordata[25]**2+data_mj.sensordata[26]**2)   # corrected
                F_app[i+1] = data_mj.sensordata[24]*(-1)     # <actuatorfrc>

                # Segment 3 diameter (requires "diam_meas" <tendon> in xml file)
                Seg3_diam[i+1] = data_mj.ten_length[42]

    media.write_video(vid_names[count], frames, fps=framerate)          # Save video
    renderer.close()

    sim_end[count] = time.time()
    sim_time[count] = sim_end[count]-sim_start[count]
    print("Scenario ", count+1, " took ", sim_time[count], " seconds to simulate", tmax/dtSim, " time steps")


    ########################################################## Plotting ############################################################
    color_mat = cm.rainbow(np.linspace(0, 1, Nseg))

    ax = plt.subplot2grid((2, 1), (0, 0))
    plt.plot(tSim,F_app, color = color_mat[2,:])
    plt.ylabel('Actuator Tension (N)', fontsize = 12, fontname="Arial")
    plt.xlabel('Time (ms)', fontsize = 12, fontname="Arial")
    ax = plt.subplot2grid((2, 1), (1, 0))
    plt.plot(Seg3_diam[1:]-Seg3_diam[1],F_app[1:], color = color_mat[2,:])
    plt.ylabel('Actuator Tension (N)', fontsize = 12, fontname="Arial")
    plt.xlabel('Diam (m)', fontsize = 12, fontname="Arial")
    plt.savefig(plot_names[count], format="png")
    plt.show()

    ######################################## Write all data to an excel file ################################################
    import pandas as pd
    from openpyxl import load_workbook

    df = pd.DataFrame({'Time': tSim, 'Tension in Muscle': F_app, 'Diameter of Seg 3': Seg3_diam})
    df.to_csv(data_filenames[count], index=False)
    

    # Increase count to move on to next scenario in the file_paths array
    count = count+1