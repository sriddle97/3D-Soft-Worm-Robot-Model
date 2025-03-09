## Single segment contraction for peristaltic model tuning
#
# Author: Shane Riddle
#
# Last edited: 02/19/2025
#########################################################################

# The worm robot is simulated in Mujoco using composite cable objects for 
# the structure, circumferential muscles for the actuators, and tendons 
# for the springs. The model can be altered in the xml file. 
# Note: alterations to the xml file will likely require alterations to 
# the rest of this code.

# The muscle activation signal is time-based and pre-determined
# The muscle tension forces are determined using a force-length-velocity curve.
# There is a force sensor and diameter tendon on Segment 3 to measure contraction
# forces and diameter changes.

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

# Tubes used on the robot are made of polyethylene
# Link to tubes on McMaster-Carr:    https://www.mcmaster.com/53385K14/
# Polyethylene flexuaral stiffness is approximately 0.28-1.5 GPa.
# Polyethylene density is ~0.94 g/cm^3 or 940 kg/m^3
# Tube OD is 0.25", ID is 0.17"  ->  cross-sectional area is 0.17 cm^2 
# so length density should be 16g/cm^3 or 0.016 kg/m of tubing

### XML Model Properties
# -  Bend parameter = Young's modulus = 0.8 GPa (corrected from 0.3 GPa via tuning)
# -  Twist parameter = Shear Modulus = 0.2 GPa (polyethylene, uncorrected since little impact)
# -  Mujoco does not have tube shapes but does have cylinders/capsules. Solid capsules of radius 0.00299m were
#    used which gives the same area moment of inertia and therfore similar stiffness to the tube.
# -  Since this produces a different c/s area compared to the hollow tube the density was adjusted to 571.6 kg/m^3.
#    This maintains the correct mass/length ratio and overall mass of the model.
# -  Physical dimensions and stretch readings are in m
# -  Density is in kg/m^3 (default is 1000, ie. water) so mass is in kg
# -  Model timestep is 1 millisecond

# The mujoco data struct is organized such that each object is added to the model in order from the xml file
# This is important for interacting with data_mj


# Automatically get work directory
work_dir = os.getcwd()
print("String format :", work_dir)

# xml_path = work_dir + r"\worm_modeling\worm_xml_test.xml"
# xml_path = work_dir + r"\worm_modeling\worm_fixed_contacts.xml"
# xml_path = work_dir + r"\worm_modeling\worm_fixed_contacts_shear.xml"
xml_path = work_dir + r"\worm_modeling\worm_test_connector_mass.xml"
xml_file = ET.parse(xml_path)


#2e8 and 8e8

##### Flat ground 
# file_paths = [r'\pipes\no_pipe.xml']
# vid_names = ["Seg3_no_pipe_0.0f_mass.mp4"]
# plot_names = ["Seg3_no_pipe_0.0f_mass.png"]
# data_filenames = ['Seg3_no_pipe_0.0f_mass.csv']
# # data_filenames = ['Seg3_no_pipe_0.0f_2e8shear.csv']
# # data_filenames = ['Seg3_no_pipe_0.0f_force.csv']
# defined_friction = ['0.0']

file_paths = [r'\pipes\90_pipe_0.5_thin.xml']
# file_paths = [r'\pipes\guardrails.xml']
# file_paths = [r'\pipes\no_pipe.xml']
vid_names = ["pos_test.mp4"]
plot_names = ["pos_test.png"]
data_filenames = ['pos_test.csv']
defined_friction = ['0.2']

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
    renderer = mujoco.Renderer(model_mj, 400, 900)            # can specify pixel dimensions here (480, 640) ALSO NEED TO CHANGE IN XML FILE
    renderer.update_scene(data_mj, camera='fixed')            # Change camera angle here if needed


    # renderer.update_scene(data_mj, camera='top_down')


    framerate = 100
    frames = []

    # Initialize the mujoco model
    mujoco.mj_forward(model_mj,data_mj)

    # Calculate total mass of all bodies defined in the xml model (for tuning purposes)
    # Warning: This also includes pipes, run with no_pipe for mass of the robot alone
    masses = model_mj.body_mass
    tot_mass = np.sum(masses)
    print("total mass = ", tot_mass)

    # Simulation Time(ms) Stuff
    Nseg = 6            # number of segments
    dtSim = 1           # millisecond
    tmax = 100          #4000
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
                # Contract just segment 3 gradually (trying to replicate instron test)
                if i < 2850:                      #2000 and do i/2700 for 3e8, 2900 and i/2900 for 8e8
                    data_mj.act[2] = min(i/2900,1)
                # elif i>=2851 and i<3850:
                #     data_mj.act[2] = 1
                else:
                    data_mj.act[2] = 0


                # # Contract and Re-expand Gradually (hysteresis test)
                # if i < 2850:
                #     data_mj.act[2] = min(i/2900,0.99)
                # elif i>=2850 and i<5700:
                #     data_mj.act[2] = max(0.98-(i-2850)/2900,0)          # 2850/2900=0.983, use 0.98 as start for down slope
                # else:
                #     data_mj.act[2] = 0

                # if i < 2000:                    # for 3e8
                #     data_mj.act[2] = min(i/2700,0.99)
                # elif i>=2000 and i<4000:
                #     data_mj.act[2] = max(0.74-(i-2000)/2700,0)
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




                # Segment 3 contraction force data (actuator cable tension, used for tuning, requires <force> sensor in xml file)
                # F_app[i+1] = np.sqrt(data_mj.sensordata[24]**2+data_mj.sensordata[25]**2+data_mj.sensordata[26]**2)/np.cos(60*np.pi/180)    # old
                # F_app[i+1] = np.sqrt(data_mj.sensordata[24]**2+data_mj.sensordata[25]**2+data_mj.sensordata[26]**2)   # corrected
                F_app[i+1] = data_mj.sensordata[24]*(-1)     # <actuatorfrc>




                # Segment 3 diameter (used for tuning, requires "diam_meas" <tendon> in xml file)
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