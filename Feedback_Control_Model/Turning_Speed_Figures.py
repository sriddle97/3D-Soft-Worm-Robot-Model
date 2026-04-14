#### Plotting Speed vs. Radius of Curvature for Manual and Adaptive Turns
#
# Author: Shane Riddle
#
# Last edited: 04/09/2026
#
# NOTES - For all 90 degree pipe bend tests a 100 second cutoff was 
#         implemented. If a model could not pass fully through the pipe, 
#         its speed was calculated using its maximum achieved distance.
#       - Be sure to change the function and global variables to match 
#         your experimental parameters (l_0, pipe_rad, etc.).
#       - Change the data_filenames, results, cols, and data_mat elements
#         to match your csv file structures and orgnization. 
#########################################################################

########################### Import packages #############################

# Basic Utility and Plotting Packages
import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
import matplotlib.colors as colors
import xml.etree.ElementTree as ET
import time
import os
from scipy.optimize import curve_fit
import seaborn as sns
import matplotlib.image as mpimg
from matplotlib.ticker import FormatStrFormatter

# Movie Making Packages  (Use mediapy for Mujoco)
import matplotlib.animation as animation
import mediapy as media

# Excel file interaction
import pandas as pd
from openpyxl import load_workbook
import csv

############################## Functions ################################

#### Truncated Colormaps (remove very light yellows)
plasma_trunc = colors.LinearSegmentedColormap.from_list('plasma_trunc', cm.plasma(np.linspace(0, 0.85, 256)))
#####################################

#### Linear regression functions
def lin_func(x, intercept, slope):
    y = intercept + slope * x
    return y
def lin_func0(x, slope):
    y = 0 + slope * x
    return y
#####################################

#### Average Speed Through Pipe, Calculation Only
def avg_speed(data_matrix, rad_vecs, l_0s):
    ## Transform x-y cordinates to distance along midline of pipe bend (s)
    # (Will need to change conditional statements if reintroducing progress along l_0)
    speed_vec = np.zeros(data_matrix.shape[2])
    s = np.zeros((data_matrix.shape[0], data_matrix.shape[2]))
    s_end = rad_vecs*np.pi/2
    for j in range(data_matrix.shape[2]):
        start_check = 0
        end_check = 0
        for i in range(data_matrix.shape[0]):
            x_m = data_matrix[i,1,j]
            y_m = data_matrix[i,8,j]
            if x_m <= l_0s:
                s[i,j] = 0
            elif x_m > l_0s:
                phi = np.arctan((x_m-l_0s)/(rad_vecs[j]-y_m))
                s[i,j] = phi*rad_vecs[j]
            if y_m >= rad_vecs[j]:
                s[i,j] = s_end[j]+y_m-rad_vecs[j]

            # Average total speed thru pipe calculations
            if s[i,j] > 0 and start_check == 0:          
                start_t = data_matrix[i,0,j]
                start_s = s[i,j]
                start_check = 1
            if s[i,j] >= s_end[j] and end_check == 0:
                end_t = data_matrix[i,0,j]
                end_s = s[i,j]
                end_check = 1
        if np.max(s[:,j]) <= s_end[j]:
            end_t = data_matrix[-1,0,j]
            end_s = s[-1,j]
        speed_vec[j] = (end_s-start_s)/(end_t-start_t)*1000         # *1000 to convert to ms

    return speed_vec
#####################################

#### Average Speed Through Pipe, Calculation WITH PLOTS (Optional)
def avg_speed_plotted(data_matrix, rad_vecs, l_0s, pipe_rads, color_mat, leg_vec):
    ## Read x-y plane position data
    for j in range(data_matrix.shape[2]):
        # plt.plot(data_matrix[:,7,j], data_matrix[:,14,j])          # COM
        plt.plot(data_matrix[:,1,j], data_matrix[:,8,j], color = color_mat[j,:])          # Segment 1
    for j in range(data_matrix.shape[2]):
        left_edge = l_0s+rad_vecs[j]-pipe_rads
        right_edge = l_0s+rad_vecs[j]+pipe_rads
        plt.plot([left_edge, right_edge],[rad_vecs[j], rad_vecs[j]], color = color_mat[j,:], linestyle='dashed')

    plt.xlabel('Distance Traveled in X (m)', fontsize = 12, fontname="Arial")
    plt.ylabel('Distance Traveled in Y (m)', fontsize = 12, fontname="Arial")
    plt.ylim(top=1.4)
    # plt.legend(['0.5', '0.6', '0.7', '0.8', '0.9', '1.0', '1.1', '1.2', '1.3'])
    plt.legend(leg_vec)
    plt.show()

    ## Transform x-y cordinates to distance along midline of pipe bend (s)
    # (Will need to change conditional statements if reintroducing progress along l_0)
    speed_vec = np.zeros(data_matrix.shape[2])
    s = np.zeros((data_matrix.shape[0], data_matrix.shape[2]))
    s_end = rad_vecs*np.pi/2
    for j in range(data_matrix.shape[2]):
        start_check = 0
        end_check = 0
        for i in range(data_matrix.shape[0]):
            x_m = data_matrix[i,1,j]
            y_m = data_matrix[i,8,j]
            if x_m <= l_0s:
                s[i,j] = 0
            elif x_m > l_0s:
                phi = np.arctan((x_m-l_0s)/(rad_vecs[j]-y_m))
                s[i,j] = phi*rad_vecs[j]
            if y_m >= rad_vecs[j]:
                s[i,j] = s_end[j]+y_m-rad_vecs[j]

            # Average total speed thru pipe calculations
            if s[i,j] > 0 and start_check == 0:          
                start_t = data_matrix[i,0,j]
                start_s = s[i,j]
                start_check = 1
            if s[i,j] >= s_end[j] and end_check == 0:
                end_t = data_matrix[i,0,j]
                end_s = s[i,j]
                end_check = 1
        if np.max(s[:,j]) <= s_end[j]:
            end_t = data_matrix[-1,0,j]
            end_s = s[-1,j]
        speed_vec[j] = (end_s-start_s)/(end_t-start_t)*1000         # *1000 since given in ms
        plt.plot(data_matrix[:,0,j], s[:,j], color = color_mat[j,:])

    for j in range(data_matrix.shape[2]):
        plt.plot([0, len(s[:,j])], [s_end[j], s_end[j]], color = color_mat[j,:], linestyle='dashed')
    plt.xlabel('Time (ms)', fontsize = 12, fontname="Arial")
    plt.ylabel('Distance Along Pipe (m)', fontsize = 12, fontname="Arial")
    plt.legend(leg_vec)
    plt.show()

    #### Speed vs. Radius of curvature plot (Speed = dist/time average)
    plt.plot(rad_vecs, speed_vec)
    plt.xlabel('Pipe Bend Radius of Curvature (m)', fontsize = 12, fontname="Arial")
    plt.ylabel('Average Speed in Pipe (m/s)', fontsize = 12, fontname="Arial")
    plt.show()

    return speed_vec
#########################################################################

################## Read and plot data from excel files ##################

# Automatically get work directory
work_dir = os.getcwd()
print("String format :", work_dir)
# results = r'\Turning Results'
pipe_rad = 0.2                      # pipe cross sectional radius (NOT radius of cruvature)
l_0 = 0.25+0.0935                   # length of straight section + distance of segment 1 from pipe end, WILL BE FURTHER if using COM (+0.374,instead of +0.0935)
count = 0

########## Supplemental Figures Visualizing the Speed Calculation Method
data_filenames = [r'\Time_sens_0.7r_adapt_f0.3.csv']
results = r'\Sens Results\rl0.01_mf15'

cols = [range(8), range(9, 16), range(17, 23), range(24, 30)]
flattened_list = [item for r in cols for item in r]
data_mat= np.loadtxt(work_dir + results + data_filenames[0], delimiter=',', skiprows=1, usecols=flattened_list)

#### Read x-y plane position data
rad = 0.7
left_edge = l_0+rad-pipe_rad
right_edge = l_0+rad+pipe_rad
top_edge = pipe_rad
bottom_edge = -pipe_rad

#### Generate the midline arc
arc_center = (l_0, rad)
arc_rad = rad
arc_theta = np.linspace(-np.pi/2, 0, 100)                       # -90° to 0°
x_arc = arc_center[0]+arc_rad*np.cos(arc_theta)
y_arc = arc_center[1]+arc_rad*np.sin(arc_theta)

fig, ax = plt.subplots()
ax.plot(data_mat[:,1], data_mat[:,8], color = 'Black')          # Segment 1 Path
ax.plot([left_edge, right_edge],[rad, rad], color = 'Red', linestyle='dashed')
ax.plot([l_0, l_0],[bottom_edge, top_edge], color = 'Red', linestyle='dashed')
ax.scatter(arc_center[0], arc_center[1], marker='*', color = 'Red', s=100)
ax.plot(x_arc, y_arc, color = 'Red', linestyle='dashed')
ax.set_aspect('equal')
ax.set_xlim(-0.1, 1.3)
ax.set_ylim(-0.3, 1.1)
plt.xlabel('Distance Traveled in X (m)', fontsize = 12, fontname="Arial")
plt.ylabel('Distance Traveled in Y (m)', fontsize = 12, fontname="Arial")
plt.show()

#### Transform x-y cordinates to distance along midline of pipe bend (s)
s = np.zeros((data_mat.shape[0]))
s_end = rad*np.pi/2
start_check = 0
end_check = 0
for i in range(data_mat.shape[0]):
    x_m = data_mat[i,1]
    y_m = data_mat[i,8]
    if x_m <= l_0:
        s[i] = 0
    elif x_m > l_0:
        phi = np.arctan((x_m-l_0)/(rad-y_m))
        s[i] = phi*rad
    if y_m >= rad:
        s[i] = s_end+y_m-rad

plt.plot(data_mat[:,0]/1000, s[:], color = 'Black')
plt.plot([0, len(s[:])/1000], [s_end, s_end], color = 'Red', linestyle='dashed')
plt.xlabel('Time (ms)', fontsize = 12, fontname="Arial")
plt.ylabel('Distance Along Pipe (m)', fontsize = 12, fontname="Arial")
plt.ylim(bottom=-0.05, top=1.4)
plt.xlim(left=0, right=60)
plt.show()




########## % Progress Through Spiral Pipes with Straight-line and Adaptive Locomotion Patterns
data_filenames = [r'\Time_sens_spiral_pipe0.3_norm.csv', r'\Time_sens_spiral_pipe0.3_adapt.csv']
results = r'\Sens Results\Spiral'

cols = [range(8), range(9, 16), range(17, 23), range(24, 30)]
flattened_list = [item for r in cols for item in r]
data1 = np.loadtxt(work_dir + results + data_filenames[0], delimiter=',', skiprows=1, usecols=flattened_list)
data2 = np.loadtxt(work_dir + results + data_filenames[1], delimiter=',', skiprows=1, usecols=flattened_list)
data_mat = np.dstack((data1, data2))
color_mat = ['Black', 'Red']

#### Read x-y plane position data
rad_vec = np.array([0.3, 1.3])
fig = plt.figure(figsize=(8, 7))
for j in range(data_mat.shape[2]):
    # plt.plot(data_mat[:,7,j], data_mat[:,14,j])          # COM
    plt.plot(data_mat[:,1,j], data_mat[:,8,j], color = color_mat[j])          # Segment 1   
plt.plot([l_0, l_0],[-pipe_rad, pipe_rad], color = 'Gray', linestyle='dashed')
plt.plot([l_0, l_0],[rad_vec[1]-rad_vec[0]-pipe_rad, rad_vec[1]-rad_vec[0]+pipe_rad], color = 'Gray', linestyle='dashed')
plt.plot(l_0, rad_vec[1], color = 'Gray', marker = 'X', markersize=10)

plt.xlabel('X Position (m)', fontsize = 12, fontname="Arial")
plt.ylabel('Y Position (m)', fontsize = 12, fontname="Arial")
plt.ylim(-0.5, 2.5)
plt.xlim(-1, 2)
plt.legend(['0 % Act Diff', 'Adaptive Act Diff'])
plt.show()

#### Transform x-y cordinates to progress along midline of spiral pipe (%)
percent_progress = np.zeros((data_mat.shape[0], data_mat.shape[2]))

fig = plt.figure(figsize=(10, 7))
plt.plot([0, np.max(data_mat[:,0,0])/1000], [100, 100], color = 'Gray', linestyle='dashed', label='_nolegend_')
for j in range(data_mat.shape[2]):
    trigger = 0
    phi = 0
    for i in range(data_mat.shape[0]):
        x_m = data_mat[i,1,j]                       # Segment 1
        y_m = data_mat[i,8,j]
        if x_m <= l_0 and i <= 30000:               # Used time as a check since start and end are both in 1st Quadrant
            percent_progress[i,j] = 0
        else:
            phi = (np.arctan2((x_m-l_0), (rad_vec[1]-y_m))) % (2*np.pi)
            percent_progress[i,j] = phi/(2*np.pi)*100

        if phi < np.pi and i >= 130000:
            percent_progress[i,j] = 100
            trigger = 1
        if trigger == 1:
            percent_progress[i,j] = 100

    plt.plot(data_mat[:,0,j]*1/1000, percent_progress[:,j], color = color_mat[j])

plt.xlabel('Time (s)', fontsize = 12, fontname="Arial")
plt.ylabel('Progress Through Spiral Pipe (%)', fontsize = 12, fontname="Arial")
plt.ylim(-5, 105)
plt.xlim(0, np.max(data_mat[:,0,0])/1000)
plt.legend(['0 % Act Diff', 'Adaptive Act Diff'])
plt.show()




########## Average Speed vs. Pipe Radii of Curvature: 100% act diff (0.3 coefficient of friction, Wide diameter tubes)
data_filenames = [r'\Time_sens_0.5r_manual0.0_f0.3.csv', r'\Time_sens_0.6r_manual0.0_f0.3.csv', r'\Time_sens_0.7r_manual0.0_f0.3.csv', r'\Time_sens_0.8r_manual0.0_f0.3.csv', r'\Time_sens_0.9r_manual0.0_f0.3.csv', r'\Time_sens_1.0r_manual0.0_f0.3.csv', r'\Time_sens_1.1r_manual0.0_f0.3.csv', r'\Time_sens_1.2r_manual0.0_f0.3.csv', r'\Time_sens_1.3r_manual0.0_f0.3.csv']
results = r'\Sens Results\Manual'

cols = [range(8), range(9, 16), range(17, 23), range(24, 30)]
flattened_list = [item for r in cols for item in r]
data1 = np.loadtxt(work_dir + results + data_filenames[0], delimiter=',', skiprows=1, usecols=flattened_list)
data2 = np.loadtxt(work_dir + results + data_filenames[1], delimiter=',', skiprows=1, usecols=flattened_list)
data3 = np.loadtxt(work_dir + results + data_filenames[2], delimiter=',', skiprows=1, usecols=flattened_list)
data4 = np.loadtxt(work_dir + results + data_filenames[3], delimiter=',', skiprows=1, usecols=flattened_list)
data5 = np.loadtxt(work_dir + results + data_filenames[4], delimiter=',', skiprows=1, usecols=flattened_list)
data6 = np.loadtxt(work_dir + results + data_filenames[5], delimiter=',', skiprows=1, usecols=flattened_list)
data7 = np.loadtxt(work_dir + results + data_filenames[6], delimiter=',', skiprows=1, usecols=flattened_list)
data8 = np.loadtxt(work_dir + results + data_filenames[7], delimiter=',', skiprows=1, usecols=flattened_list)
data9 = np.loadtxt(work_dir + results + data_filenames[8], delimiter=',', skiprows=1, usecols=flattened_list)

data_mat = np.dstack((data1, data2, data3, data4, data5, data6, data7, data8, data9))
rad_vec_turn100 = np.array([0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3])
speed_vec_turn100 = avg_speed(data_mat, rad_vec_turn100, l_0)
# color_mat = cm.rainbow(np.linspace(0, 1, data_mat.shape[2]))
# leg_vec = ['0.5', '0.6', '0.7', '0.8', '0.9', '1.0', '1.1', '1.2', '1.3']
# speed_vec_turn100 = avg_speed_plotted(data_mat, rad_vec_turn100, l_0, pipe_rad, color_mat, leg_vec)
# print (speed_vec_turn100)
count = count+1




########## Average Speed vs. Pipe Radii of Curvature: 90% act diff (0.3 coefficient of friction, Wide diameter tubes)
data_filenames = [r'\Time_sens_0.5r_manual0.1_f0.3.csv', r'\Time_sens_0.6r_manual0.1_f0.3.csv', r'\Time_sens_0.7r_manual0.1_f0.3.csv', r'\Time_sens_0.8r_manual0.1_f0.3.csv', r'\Time_sens_0.9r_manual0.1_f0.3.csv', r'\Time_sens_1.0r_manual0.1_f0.3.csv', r'\Time_sens_1.1r_manual0.1_f0.3.csv', r'\Time_sens_1.2r_manual0.1_f0.3.csv', r'\Time_sens_1.3r_manual0.1_f0.3.csv']
results = r'\Sens Results\Manual'

cols = [range(8), range(9, 16), range(17, 23), range(24, 30)]
flattened_list = [item for r in cols for item in r]
data1 = np.loadtxt(work_dir + results + data_filenames[0], delimiter=',', skiprows=1, usecols=flattened_list)
data2 = np.loadtxt(work_dir + results + data_filenames[1], delimiter=',', skiprows=1, usecols=flattened_list)
data3 = np.loadtxt(work_dir + results + data_filenames[2], delimiter=',', skiprows=1, usecols=flattened_list)
data4 = np.loadtxt(work_dir + results + data_filenames[3], delimiter=',', skiprows=1, usecols=flattened_list)
data5 = np.loadtxt(work_dir + results + data_filenames[4], delimiter=',', skiprows=1, usecols=flattened_list)
data6 = np.loadtxt(work_dir + results + data_filenames[5], delimiter=',', skiprows=1, usecols=flattened_list)
data7 = np.loadtxt(work_dir + results + data_filenames[6], delimiter=',', skiprows=1, usecols=flattened_list)
data8 = np.loadtxt(work_dir + results + data_filenames[7], delimiter=',', skiprows=1, usecols=flattened_list)
data9 = np.loadtxt(work_dir + results + data_filenames[8], delimiter=',', skiprows=1, usecols=flattened_list)

data_mat = np.dstack((data1, data2, data3, data4, data5, data6, data7, data8, data9))
rad_vec_turn90 = np.array([0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3])
speed_vec_turn90 = avg_speed(data_mat, rad_vec_turn90, l_0)
# color_mat = cm.rainbow(np.linspace(0, 1, data_mat.shape[2]))
# leg_vec = ['0.5', '0.6', '0.7', '0.8', '0.9', '1.0', '1.1', '1.2', '1.3']
# speed_vec_turn90 = avg_speed_plotted(data_mat, rad_vec_turn90, l_0, pipe_rad, color_mat, leg_vec)
count = count+1




########## Average Speed vs. Pipe Radii of Curvature: 80% act diff (0.3 coefficient of friction, Wide diameter tubes)
data_filenames = [r'\Time_sens_0.5r_manual0.2_f0.3.csv', r'\Time_sens_0.6r_manual0.2_f0.3.csv', r'\Time_sens_0.7r_manual0.2_f0.3.csv', r'\Time_sens_0.8r_manual0.2_f0.3.csv', r'\Time_sens_0.9r_manual0.2_f0.3.csv', r'\Time_sens_1.0r_manual0.2_f0.3.csv', r'\Time_sens_1.1r_manual0.2_f0.3.csv', r'\Time_sens_1.2r_manual0.2_f0.3.csv', r'\Time_sens_1.3r_manual0.2_f0.3.csv']
results = r'\Sens Results\Manual'

cols = [range(8), range(9, 16), range(17, 23), range(24, 30)]
flattened_list = [item for r in cols for item in r]
data1 = np.loadtxt(work_dir + results + data_filenames[0], delimiter=',', skiprows=1, usecols=flattened_list)
data2 = np.loadtxt(work_dir + results + data_filenames[1], delimiter=',', skiprows=1, usecols=flattened_list)
data3 = np.loadtxt(work_dir + results + data_filenames[2], delimiter=',', skiprows=1, usecols=flattened_list)
data4 = np.loadtxt(work_dir + results + data_filenames[3], delimiter=',', skiprows=1, usecols=flattened_list)
data5 = np.loadtxt(work_dir + results + data_filenames[4], delimiter=',', skiprows=1, usecols=flattened_list)
data6 = np.loadtxt(work_dir + results + data_filenames[5], delimiter=',', skiprows=1, usecols=flattened_list)
data7 = np.loadtxt(work_dir + results + data_filenames[6], delimiter=',', skiprows=1, usecols=flattened_list)
data8 = np.loadtxt(work_dir + results + data_filenames[7], delimiter=',', skiprows=1, usecols=flattened_list)
data9 = np.loadtxt(work_dir + results + data_filenames[8], delimiter=',', skiprows=1, usecols=flattened_list)

data_mat = np.dstack((data1, data2, data3, data4, data5, data6, data7, data8, data9))
rad_vec_turn80 = np.array([0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3])
speed_vec_turn80 = avg_speed(data_mat, rad_vec_turn80, l_0)
# color_mat = cm.rainbow(np.linspace(0, 1, data_mat.shape[2]))
# leg_vec = ['0.5', '0.6', '0.7', '0.8', '0.9', '1.0', '1.1', '1.2', '1.3']
# speed_vec_turn80 = avg_speed_plotted(data_mat, rad_vec_turn80, l_0, pipe_rad, color_mat, leg_vec)
count = count+1




########## Average Speed vs. Pipe Radii of Curvature: 70% act diff (0.3 coefficient of friction, Wide diameter tubes)
data_filenames = [r'\Time_sens_0.5r_manual0.3_f0.3.csv', r'\Time_sens_0.6r_manual0.3_f0.3.csv', r'\Time_sens_0.7r_manual0.3_f0.3.csv', r'\Time_sens_0.8r_manual0.3_f0.3.csv', r'\Time_sens_0.9r_manual0.3_f0.3.csv', r'\Time_sens_1.0r_manual0.3_f0.3.csv', r'\Time_sens_1.1r_manual0.3_f0.3.csv', r'\Time_sens_1.2r_manual0.3_f0.3.csv', r'\Time_sens_1.3r_manual0.3_f0.3.csv']
results = r'\Sens Results\Manual'

cols = [range(8), range(9, 16), range(17, 23), range(24, 30)]
flattened_list = [item for r in cols for item in r]
data1 = np.loadtxt(work_dir + results + data_filenames[0], delimiter=',', skiprows=1, usecols=flattened_list)
data2 = np.loadtxt(work_dir + results + data_filenames[1], delimiter=',', skiprows=1, usecols=flattened_list)
data3 = np.loadtxt(work_dir + results + data_filenames[2], delimiter=',', skiprows=1, usecols=flattened_list)
data4 = np.loadtxt(work_dir + results + data_filenames[3], delimiter=',', skiprows=1, usecols=flattened_list)
data5 = np.loadtxt(work_dir + results + data_filenames[4], delimiter=',', skiprows=1, usecols=flattened_list)
data6 = np.loadtxt(work_dir + results + data_filenames[5], delimiter=',', skiprows=1, usecols=flattened_list)
data7 = np.loadtxt(work_dir + results + data_filenames[6], delimiter=',', skiprows=1, usecols=flattened_list)
data8 = np.loadtxt(work_dir + results + data_filenames[7], delimiter=',', skiprows=1, usecols=flattened_list)
data9 = np.loadtxt(work_dir + results + data_filenames[8], delimiter=',', skiprows=1, usecols=flattened_list)

data_mat = np.dstack((data1, data2, data3, data4, data5, data6, data7, data8, data9))
rad_vec_turn70 = np.array([0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3])
speed_vec_turn70 = avg_speed(data_mat, rad_vec_turn70, l_0)
# color_mat = cm.rainbow(np.linspace(0, 1, data_mat.shape[2]))
# leg_vec = ['0.5', '0.6', '0.7', '0.8', '0.9', '1.0', '1.1', '1.2', '1.3']
# speed_vec_turn70 = avg_speed_plotted(data_mat, rad_vec_turn70, l_0, pipe_rad, color_mat, leg_vec)
count = count+1




########## Average Speed vs. Pipe Radii of Curvature: 60% act diff (0.3 coefficient of friction, Wide diameter tubes)
data_filenames = [r'\Time_sens_0.5r_manual0.4_f0.3.csv', r'\Time_sens_0.6r_manual0.4_f0.3.csv', r'\Time_sens_0.7r_manual0.4_f0.3.csv', r'\Time_sens_0.8r_manual0.4_f0.3.csv', r'\Time_sens_0.9r_manual0.4_f0.3.csv', r'\Time_sens_1.0r_manual0.4_f0.3.csv', r'\Time_sens_1.1r_manual0.4_f0.3.csv', r'\Time_sens_1.2r_manual0.4_f0.3.csv', r'\Time_sens_1.3r_manual0.4_f0.3.csv']
results = r'\Sens Results\Manual'

cols = [range(8), range(9, 16), range(17, 23), range(24, 30)]
flattened_list = [item for r in cols for item in r]
# data1 = np.loadtxt(work_dir + results + data_filenames[0], delimiter=',', skiprows=1, usecols=flattened_list)
data2 = np.loadtxt(work_dir + results + data_filenames[1], delimiter=',', skiprows=1, usecols=flattened_list)
data3 = np.loadtxt(work_dir + results + data_filenames[2], delimiter=',', skiprows=1, usecols=flattened_list)
data4 = np.loadtxt(work_dir + results + data_filenames[3], delimiter=',', skiprows=1, usecols=flattened_list)
data5 = np.loadtxt(work_dir + results + data_filenames[4], delimiter=',', skiprows=1, usecols=flattened_list)
data6 = np.loadtxt(work_dir + results + data_filenames[5], delimiter=',', skiprows=1, usecols=flattened_list)
data7 = np.loadtxt(work_dir + results + data_filenames[6], delimiter=',', skiprows=1, usecols=flattened_list)
data8 = np.loadtxt(work_dir + results + data_filenames[7], delimiter=',', skiprows=1, usecols=flattened_list)
data9 = np.loadtxt(work_dir + results + data_filenames[8], delimiter=',', skiprows=1, usecols=flattened_list)

data_mat = np.dstack((data2, data3, data4, data5, data6, data7, data8, data9))
rad_vec_turn60 = np.array([0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3])
speed_vec_turn60 = avg_speed(data_mat, rad_vec_turn60, l_0)
# color_mat = cm.rainbow(np.linspace(0, 1, data_mat.shape[2]))
# leg_vec = ['0.6', '0.7', '0.8', '0.9', '1.0', '1.1', '1.2', '1.3']
# speed_vec_turn60 = avg_speed_plotted(data_mat, rad_vec_turn60, l_0, pipe_rad, color_mat, leg_vec)
count = count+1




########## Average Speed vs. Pipe Radii of Curvature: 50% act diff (0.3 coefficient of friction, Wide diameter tubes)
data_filenames = [r'\Time_sens_0.5r_manual0.5_f0.3.csv', r'\Time_sens_0.6r_manual0.5_f0.3.csv', r'\Time_sens_0.7r_manual0.5_f0.3.csv', r'\Time_sens_0.8r_manual0.5_f0.3.csv', r'\Time_sens_0.9r_manual0.5_f0.3.csv', r'\Time_sens_1.0r_manual0.5_f0.3.csv', r'\Time_sens_1.1r_manual0.5_f0.3.csv', r'\Time_sens_1.2r_manual0.5_f0.3.csv', r'\Time_sens_1.3r_manual0.5_f0.3.csv']
results = r'\Sens Results\Manual'

cols = [range(8), range(9, 16), range(17, 23), range(24, 30)]
flattened_list = [item for r in cols for item in r]
# data1 = np.loadtxt(work_dir + results + data_filenames[0], delimiter=',', skiprows=1, usecols=flattened_list)
data2 = np.loadtxt(work_dir + results + data_filenames[1], delimiter=',', skiprows=1, usecols=flattened_list)
data3 = np.loadtxt(work_dir + results + data_filenames[2], delimiter=',', skiprows=1, usecols=flattened_list)
data4 = np.loadtxt(work_dir + results + data_filenames[3], delimiter=',', skiprows=1, usecols=flattened_list)
data5 = np.loadtxt(work_dir + results + data_filenames[4], delimiter=',', skiprows=1, usecols=flattened_list)
data6 = np.loadtxt(work_dir + results + data_filenames[5], delimiter=',', skiprows=1, usecols=flattened_list)
data7 = np.loadtxt(work_dir + results + data_filenames[6], delimiter=',', skiprows=1, usecols=flattened_list)
data8 = np.loadtxt(work_dir + results + data_filenames[7], delimiter=',', skiprows=1, usecols=flattened_list)
data9 = np.loadtxt(work_dir + results + data_filenames[8], delimiter=',', skiprows=1, usecols=flattened_list)

data_mat = np.dstack((data2, data3, data4, data5, data6, data7, data8, data9))
rad_vec_turn50 = np.array([0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3])
speed_vec_turn50 = avg_speed(data_mat, rad_vec_turn50, l_0)
# color_mat = cm.rainbow(np.linspace(0, 1, data_mat.shape[2]))
# leg_vec = ['0.6', '0.7', '0.8', '0.9', '1.0', '1.1', '1.2', '1.3']
# speed_vec_turn50 = avg_speed_plotted(data_mat, rad_vec_turn50, l_0, pipe_rad, color_mat, leg_vec)
count = count+1




########## Average Speed vs. Pipe Radii of Curvature: 40% act diff (0.3 coefficient of friction, Wide diameter tubes)
data_filenames = [r'\Time_sens_0.5r_manual0.6_f0.3.csv', r'\Time_sens_0.6r_manual0.6_f0.3.csv', r'\Time_sens_0.7r_manual0.6_f0.3.csv', r'\Time_sens_0.8r_manual0.6_f0.3.csv', r'\Time_sens_0.9r_manual0.6_f0.3.csv', r'\Time_sens_1.0r_manual0.6_f0.3.csv', r'\Time_sens_1.1r_manual0.6_f0.3.csv', r'\Time_sens_1.2r_manual0.6_f0.3.csv', r'\Time_sens_1.3r_manual0.6_f0.3.csv']
results = r'\Sens Results\Manual'

cols = [range(8), range(9, 16), range(17, 23), range(24, 30)]
flattened_list = [item for r in cols for item in r]
# data1 = np.loadtxt(work_dir + results + data_filenames[0], delimiter=',', skiprows=1, usecols=flattened_list)
data2 = np.loadtxt(work_dir + results + data_filenames[1], delimiter=',', skiprows=1, usecols=flattened_list)
data3 = np.loadtxt(work_dir + results + data_filenames[2], delimiter=',', skiprows=1, usecols=flattened_list)
data4 = np.loadtxt(work_dir + results + data_filenames[3], delimiter=',', skiprows=1, usecols=flattened_list)
data5 = np.loadtxt(work_dir + results + data_filenames[4], delimiter=',', skiprows=1, usecols=flattened_list)
data6 = np.loadtxt(work_dir + results + data_filenames[5], delimiter=',', skiprows=1, usecols=flattened_list)
data7 = np.loadtxt(work_dir + results + data_filenames[6], delimiter=',', skiprows=1, usecols=flattened_list)
data8 = np.loadtxt(work_dir + results + data_filenames[7], delimiter=',', skiprows=1, usecols=flattened_list)
data9 = np.loadtxt(work_dir + results + data_filenames[8], delimiter=',', skiprows=1, usecols=flattened_list)

data_mat = np.dstack((data2, data3, data4, data5, data6, data7, data8, data9))
rad_vec_turn40 = np.array([0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3])
speed_vec_turn40 = avg_speed(data_mat, rad_vec_turn40, l_0)
# color_mat = cm.rainbow(np.linspace(0, 1, data_mat.shape[2]))
# leg_vec = ['0.6', '0.7', '0.8', '0.9', '1.0', '1.1', '1.2', '1.3']
# speed_vec_turn40 = avg_speed_plotted(data_mat, rad_vec_turn40, l_0, pipe_rad, color_mat, leg_vec)
count = count+1




########## Average Speed vs. Pipe Radii of Curvature: 30% act diff (0.3 coefficient of friction, Wide diameter tubes)
data_filenames = [r'\Time_sens_0.5r_manual0.7_f0.3.csv', r'\Time_sens_0.6r_manual0.7_f0.3.csv', r'\Time_sens_0.7r_manual0.7_f0.3.csv', r'\Time_sens_0.8r_manual0.7_f0.3.csv', r'\Time_sens_0.9r_manual0.7_f0.3.csv', r'\Time_sens_1.0r_manual0.7_f0.3.csv', r'\Time_sens_1.1r_manual0.7_f0.3.csv', r'\Time_sens_1.2r_manual0.7_f0.3.csv', r'\Time_sens_1.3r_manual0.7_f0.3.csv']
results = r'\Sens Results\Manual'

cols = [range(8), range(9, 16), range(17, 23), range(24, 30)]
flattened_list = [item for r in cols for item in r]
# data1 = np.loadtxt(work_dir + results + data_filenames[0], delimiter=',', skiprows=1, usecols=flattened_list)
data2 = np.loadtxt(work_dir + results + data_filenames[1], delimiter=',', skiprows=1, usecols=flattened_list)
data3 = np.loadtxt(work_dir + results + data_filenames[2], delimiter=',', skiprows=1, usecols=flattened_list)
data4 = np.loadtxt(work_dir + results + data_filenames[3], delimiter=',', skiprows=1, usecols=flattened_list)
data5 = np.loadtxt(work_dir + results + data_filenames[4], delimiter=',', skiprows=1, usecols=flattened_list)
data6 = np.loadtxt(work_dir + results + data_filenames[5], delimiter=',', skiprows=1, usecols=flattened_list)
data7 = np.loadtxt(work_dir + results + data_filenames[6], delimiter=',', skiprows=1, usecols=flattened_list)
data8 = np.loadtxt(work_dir + results + data_filenames[7], delimiter=',', skiprows=1, usecols=flattened_list)
data9 = np.loadtxt(work_dir + results + data_filenames[8], delimiter=',', skiprows=1, usecols=flattened_list)

data_mat = np.dstack((data2, data3, data4, data5, data6, data7, data8, data9))
rad_vec_turn30 = np.array([0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3])
speed_vec_turn30 = avg_speed(data_mat, rad_vec_turn30, l_0)
# color_mat = cm.rainbow(np.linspace(0, 1, data_mat.shape[2]))
# leg_vec = ['0.6', '0.7', '0.8', '0.9', '1.0', '1.1', '1.2', '1.3']
# speed_vec_turn30 = avg_speed_plotted(data_mat, rad_vec_turn30, l_0, pipe_rad, color_mat, leg_vec)
count = count+1




########## Average Speed vs. Pipe Radii of Curvature: 20% act diff (0.3 coefficient of friction, Wide diameter tubes)
data_filenames = [r'\Time_sens_0.5r_manual0.8_f0.3.csv', r'\Time_sens_0.6r_manual0.8_f0.3.csv', r'\Time_sens_0.7r_manual0.8_f0.3.csv', r'\Time_sens_0.8r_manual0.8_f0.3.csv', r'\Time_sens_0.9r_manual0.8_f0.3.csv', r'\Time_sens_1.0r_manual0.8_f0.3.csv', r'\Time_sens_1.1r_manual0.8_f0.3.csv', r'\Time_sens_1.2r_manual0.8_f0.3.csv', r'\Time_sens_1.3r_manual0.8_f0.3.csv']
results = r'\Sens Results\Manual'

cols = [range(8), range(9, 16), range(17, 23), range(24, 30)]
flattened_list = [item for r in cols for item in r]
# data1 = np.loadtxt(work_dir + results + data_filenames[0], delimiter=',', skiprows=1, usecols=flattened_list)
data2 = np.loadtxt(work_dir + results + data_filenames[1], delimiter=',', skiprows=1, usecols=flattened_list)
data3 = np.loadtxt(work_dir + results + data_filenames[2], delimiter=',', skiprows=1, usecols=flattened_list)
data4 = np.loadtxt(work_dir + results + data_filenames[3], delimiter=',', skiprows=1, usecols=flattened_list)
data5 = np.loadtxt(work_dir + results + data_filenames[4], delimiter=',', skiprows=1, usecols=flattened_list)
data6 = np.loadtxt(work_dir + results + data_filenames[5], delimiter=',', skiprows=1, usecols=flattened_list)
data7 = np.loadtxt(work_dir + results + data_filenames[6], delimiter=',', skiprows=1, usecols=flattened_list)
data8 = np.loadtxt(work_dir + results + data_filenames[7], delimiter=',', skiprows=1, usecols=flattened_list)
data9 = np.loadtxt(work_dir + results + data_filenames[8], delimiter=',', skiprows=1, usecols=flattened_list)

data_mat = np.dstack((data2, data3, data4, data5, data6, data7, data8, data9))
rad_vec_turn20 = np.array([0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3])
speed_vec_turn20 = avg_speed(data_mat, rad_vec_turn20, l_0)
# color_mat = cm.rainbow(np.linspace(0, 1, data_mat.shape[2]))
# leg_vec = ['0.6', '0.7', '0.8', '0.9', '1.0', '1.1', '1.2', '1.3']
# speed_vec_turn20 = avg_speed_plotted(data_mat, rad_vec_turn20, l_0, pipe_rad, color_mat, leg_vec)
count = count+1




########## Average Speed vs. Pipe Radii of Curvature, 10% act diff (0.3 coefficient of friction, Wide diameter tubes)
data_filenames = [r'\Time_sens_0.5r_manual0.9_f0.3.csv', r'\Time_sens_0.6r_manual0.9_f0.3.csv', r'\Time_sens_0.7r_manual0.9_f0.3.csv', r'\Time_sens_0.8r_manual0.9_f0.3.csv', r'\Time_sens_0.9r_manual0.9_f0.3.csv', r'\Time_sens_1.0r_manual0.9_f0.3.csv', r'\Time_sens_1.1r_manual0.9_f0.3.csv', r'\Time_sens_1.2r_manual0.9_f0.3.csv', r'\Time_sens_1.3r_manual0.9_f0.3.csv']
results = r'\Sens Results\Manual'

cols = [range(8), range(9, 16), range(17, 23), range(24, 30)]
flattened_list = [item for r in cols for item in r]
# data1 = np.loadtxt(work_dir + results + data_filenames[0], delimiter=',', skiprows=1, usecols=flattened_list)
# data2 = np.loadtxt(work_dir + results + data_filenames[1], delimiter=',', skiprows=1, usecols=flattened_list)
data3 = np.loadtxt(work_dir + results + data_filenames[2], delimiter=',', skiprows=1, usecols=flattened_list)
data4 = np.loadtxt(work_dir + results + data_filenames[3], delimiter=',', skiprows=1, usecols=flattened_list)
data5 = np.loadtxt(work_dir + results + data_filenames[4], delimiter=',', skiprows=1, usecols=flattened_list)
data6 = np.loadtxt(work_dir + results + data_filenames[5], delimiter=',', skiprows=1, usecols=flattened_list)
data7 = np.loadtxt(work_dir + results + data_filenames[6], delimiter=',', skiprows=1, usecols=flattened_list)
data8 = np.loadtxt(work_dir + results + data_filenames[7], delimiter=',', skiprows=1, usecols=flattened_list)
data9 = np.loadtxt(work_dir + results + data_filenames[8], delimiter=',', skiprows=1, usecols=flattened_list)

data_mat = np.dstack((data3, data4, data5, data6, data7, data8, data9))
rad_vec_turn10 = np.array([0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3])
speed_vec_turn10 = avg_speed(data_mat, rad_vec_turn10, l_0)
# color_mat = cm.rainbow(np.linspace(0, 1, data_mat.shape[2]))
# leg_vec = ['0.7', '0.8', '0.9', '1.0', '1.1', '1.2', '1.3']
# speed_vec_turn10 = avg_speed_plotted(data_mat, rad_vec_turn10, l_0, pipe_rad, color_mat, leg_vec)
count = count+1




########## Average Speed vs. Pipe Radii of Curvature: 0% act dif i.e. straight-line algorithm (0.3 coefficient of friction, Wide diameter tubes)
# data_filenames = [r'\Time_linear_0.45r_norm_f0.3.csv', r'\Time_linear_0.5r_norm_f0.3.csv', r'\Time_linear_0.6r_norm_f0.3.csv', r'\Time_linear_0.7r_norm_f0.3.csv', r'\Time_linear_0.8r_norm_f0.3.csv', r'\Time_linear_0.9r_norm_f0.3.csv', r'\Time_linear_1.0r_norm_f0.3.csv', r'\Time_linear_1.1r_norm_f0.3.csv', r'\Time_linear_1.2r_norm_f0.3.csv', r'\Time_linear_1.3r_norm_f0.3.csv']
# results = r'\Turning Results\Wide Diam Turning\75N Linear Springs'
data_filenames = [r'\Straight\Time_sens_straight_pipe_norm.csv', r'\Time_sens_0.5r_norm_f0.3.csv', r'\Time_sens_0.6r_norm_f0.3.csv', r'\Time_sens_0.7r_norm_f0.3.csv', r'\Time_sens_0.8r_norm_f0.3.csv', r'\Time_sens_0.9r_norm_f0.3.csv', r'\Time_sens_1.0r_norm_f0.3.csv', r'\Time_sens_1.1r_norm_f0.3.csv', r'\Time_sens_1.2r_norm_f0.3.csv', r'\Time_sens_1.3r_norm_f0.3.csv']
results = r'\Sens Results'

cols = [range(8), range(9, 16), range(17, 23), range(24, 30)]
flattened_list = [item for r in cols for item in r]
# data1 = np.loadtxt(work_dir + results + data_filenames[0], delimiter=',', skiprows=1, usecols=flattened_list)
# data2 = np.loadtxt(work_dir + results + data_filenames[1], delimiter=',', skiprows=1, usecols=flattened_list)
# data3 = np.loadtxt(work_dir + results + data_filenames[2], delimiter=',', skiprows=1, usecols=flattened_list)
data4 = np.loadtxt(work_dir + results + data_filenames[3], delimiter=',', skiprows=1, usecols=flattened_list)
data5 = np.loadtxt(work_dir + results + data_filenames[4], delimiter=',', skiprows=1, usecols=flattened_list)
data6 = np.loadtxt(work_dir + results + data_filenames[5], delimiter=',', skiprows=1, usecols=flattened_list)
data7 = np.loadtxt(work_dir + results + data_filenames[6], delimiter=',', skiprows=1, usecols=flattened_list)
data8 = np.loadtxt(work_dir + results + data_filenames[7], delimiter=',', skiprows=1, usecols=flattened_list)
data9 = np.loadtxt(work_dir + results + data_filenames[8], delimiter=',', skiprows=1, usecols=flattened_list)
data10 = np.loadtxt(work_dir + results + data_filenames[9], delimiter=',', skiprows=1, usecols=flattened_list)

data_mat = np.dstack((data4, data5, data6, data7, data8, data9, data10))
rad_vec_norm = np.array([0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3])
speed_vec_norm = avg_speed(data_mat, rad_vec_norm, l_0)
# color_mat = cm.rainbow(np.linspace(0, 1, data_mat.shape[2]))
# leg_vec = ['0.7', '0.8', '0.9', '1.0', '1.1', '1.2', '1.3']
# speed_vec_norm = avg_speed_plotted(data_mat, rad_vec_norm, l_0, pipe_rad, color_mat, leg_vec)
count = count+1




########## Average Speed vs. Pipe Radii of Curvature: Adaptive Turning Algorithm (0.3 coefficient of friction, Wide diameter tubes)
data_filenames = [r'\Time_sens_0.5r_adapt_f0.3.csv', r'\Time_sens_0.6r_adapt_f0.3.csv', r'\Time_sens_0.7r_adapt_f0.3.csv', r'\Time_sens_0.8r_adapt_f0.3.csv', r'\Time_sens_0.9r_adapt_f0.3.csv', r'\Time_sens_1.0r_adapt_f0.3.csv', r'\Time_sens_1.1r_adapt_f0.3.csv', r'\Time_sens_1.2r_adapt_f0.3.csv', r'\Time_sens_1.3r_adapt_f0.3.csv']
results = r'\Sens Results\rl0.01_mf15'
# data_filenames = [r'\Time_sens_0.5r_adapt_rl0.005_mf10_f0.3.csv', r'\Time_sens_0.6r_adapt_rl0.005_mf10_f0.3.csv', r'\Time_sens_0.7r_adapt_rl0.005_mf10_f0.3.csv', r'\Time_sens_0.8r_adapt_rl0.005_mf10_f0.3.csv', r'\Time_sens_0.9r_adapt_rl0.005_mf10_f0.3.csv', r'\Time_sens_1.0r_adapt_rl0.005_mf10_f0.3.csv', r'\Time_sens_1.1r_adapt_rl0.005_mf10_f0.3.csv', r'\Time_sens_1.2r_adapt_rl0.005_mf10_f0.3.csv', r'\Time_sens_1.3r_adapt_rl0.005_mf10_f0.3.csv']
# results = r'\Sens Results\rl0.005_mf10'
# data_filenames = [r'\Time_sens_0.5r_adapt_rl0.005_mf12_f0.3.csv', r'\Time_sens_0.6r_adapt_rl0.005_mf12_f0.3.csv', r'\Time_sens_0.7r_adapt_rl0.005_mf12_f0.3.csv', r'\Time_sens_0.8r_adapt_rl0.005_mf12_f0.3.csv', r'\Time_sens_0.9r_adapt_rl0.005_mf12_f0.3.csv', r'\Time_sens_1.0r_adapt_rl0.005_mf12_f0.3.csv', r'\Time_sens_1.1r_adapt_rl0.005_mf12_f0.3.csv', r'\Time_sens_1.2r_adapt_rl0.005_mf12_f0.3.csv', r'\Time_sens_1.3r_adapt_rl0.005_mf12_f0.3.csv']
# results = r'\Sens Results\rl0.005_mf12'
# data_filenames = [r'\Time_sens_0.5r_adapt_rl0.005_mf17_f0.3.csv', r'\Time_sens_0.6r_adapt_rl0.005_mf17_f0.3.csv', r'\Time_sens_0.7r_adapt_rl0.005_mf17_f0.3.csv', r'\Time_sens_0.8r_adapt_rl0.005_mf17_f0.3.csv', r'\Time_sens_0.9r_adapt_rl0.005_mf17_f0.3.csv', r'\Time_sens_1.0r_adapt_rl0.005_mf17_f0.3.csv', r'\Time_sens_1.1r_adapt_rl0.005_mf17_f0.3.csv', r'\Time_sens_1.2r_adapt_rl0.005_mf17_f0.3.csv', r'\Time_sens_1.3r_adapt_rl0.005_mf17_f0.3.csv']
# results = r'\Sens Results\rl0.005_mf17'

cols = [range(8), range(9, 16), range(17, 23), range(24, 30)]
flattened_list = [item for r in cols for item in r]
data1 = np.loadtxt(work_dir + results + data_filenames[0], delimiter=',', skiprows=1, usecols=flattened_list)
data2 = np.loadtxt(work_dir + results + data_filenames[1], delimiter=',', skiprows=1, usecols=flattened_list)
data3 = np.loadtxt(work_dir + results + data_filenames[2], delimiter=',', skiprows=1, usecols=flattened_list)
data4 = np.loadtxt(work_dir + results + data_filenames[3], delimiter=',', skiprows=1, usecols=flattened_list)
data5 = np.loadtxt(work_dir + results + data_filenames[4], delimiter=',', skiprows=1, usecols=flattened_list)
data6 = np.loadtxt(work_dir + results + data_filenames[5], delimiter=',', skiprows=1, usecols=flattened_list)
data7 = np.loadtxt(work_dir + results + data_filenames[6], delimiter=',', skiprows=1, usecols=flattened_list)
data8 = np.loadtxt(work_dir + results + data_filenames[7], delimiter=',', skiprows=1, usecols=flattened_list)
data9 = np.loadtxt(work_dir + results + data_filenames[8], delimiter=',', skiprows=1, usecols=flattened_list)

data_mat = np.dstack((data1, data2, data3, data4, data5, data6, data7, data8, data9))
rad_vec_adapt = np.array([0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3])
speed_vec_adapt = avg_speed(data_mat, rad_vec_adapt, l_0)
# color_mat = cm.rainbow(np.linspace(0, 1, data_mat.shape[2]))
# leg_vec = ['0.5', '0.6', '0.7', '0.8', '0.9', '1.0', '1.1', '1.2', '1.3']
# speed_vec_adapt = avg_speed_plotted(data_mat, rad_vec_adapt, l_0, pipe_rad, color_mat, leg_vec)

## Additional % act diff calculations for the green line in 3D plot
cols = [range(1), range(115, 118)]
flattened_list = [item for r in cols for item in r]
data1 = np.loadtxt(work_dir + results + data_filenames[0], delimiter=',', skiprows=1, usecols=flattened_list)
data2 = np.loadtxt(work_dir + results + data_filenames[1], delimiter=',', skiprows=1, usecols=flattened_list)
data3 = np.loadtxt(work_dir + results + data_filenames[2], delimiter=',', skiprows=1, usecols=flattened_list)
data4 = np.loadtxt(work_dir + results + data_filenames[3], delimiter=',', skiprows=1, usecols=flattened_list)
data5 = np.loadtxt(work_dir + results + data_filenames[4], delimiter=',', skiprows=1, usecols=flattened_list)
data6 = np.loadtxt(work_dir + results + data_filenames[5], delimiter=',', skiprows=1, usecols=flattened_list)
data7 = np.loadtxt(work_dir + results + data_filenames[6], delimiter=',', skiprows=1, usecols=flattened_list)
data8 = np.loadtxt(work_dir + results + data_filenames[7], delimiter=',', skiprows=1, usecols=flattened_list)
data9 = np.loadtxt(work_dir + results + data_filenames[8], delimiter=',', skiprows=1, usecols=flattened_list)

data_mat = np.dstack((data1, data2, data3, data4, data5, data6, data7, data8, data9))
percent_diffs = np.zeros(data_mat.shape[2])
for j in range(data_mat.shape[2]):
    p_diffs = -1*(data_mat[:,2,j]-data_mat[:,3,j])*100
    percent_diffs[j] = np.max(p_diffs)




########## Speed vs. Pipe Radii of Curvature Combined Results 2D
## First find straightline asymptote
data_filenames = [r'\Straight\Time_sens_straight_pipe_norm.csv']
results = r'\Sens Results'

cols = [range(8), range(9, 16), range(17, 23), range(24, 30)]
flattened_list = [item for r in cols for item in r]
data1 = np.loadtxt(work_dir + results + data_filenames[0], delimiter=',', skiprows=1, usecols=flattened_list)

int_vec = np.zeros(data1.shape[1])
slope_vec = np.zeros(data1.shape[1])
x_m = data1[:,1]
t_m = data1[:,0]

start_check = 0
for i in range(data1.shape[0]):
    if x_m[i] > l_0 and start_check == 0:       # Find the start point, use same initial length as curved pipes before starting calculations
        start_index = i
        start_check = 1
end_index = np.argmax(x_m[:])
popt, pcov = curve_fit(lin_func, t_m[start_index:end_index], x_m[start_index:end_index])
int_vec = popt[0]
slope_vec = popt[1]
slope_vec = slope_vec*1000                      # *1000 to convert to ms

# color_mat = cm.plasma(np.linspace(0, 1, count))
color_mat = plasma_trunc(np.linspace(0, 1, count))
fig = plt.figure(figsize = (12,9))
lines = []
labels = []
line, = plt.plot([0.4, 1.35], [slope_vec*100, slope_vec*100], color = 'Gray', linestyle = 'dashed')
lines.append(line)
line, = plt.plot(rad_vec_norm, speed_vec_norm*100, '-o', color = color_mat[0,:], markersize=8, label='Norm 0% Act Diff')
lines.append(line)
line, = plt.plot(rad_vec_turn10, speed_vec_turn10*100, '-s', color = color_mat[1,:], markersize=8, label='Turn 10% Act Diff')
lines.append(line)
line, = plt.plot(rad_vec_turn20, speed_vec_turn20*100, '-s', color = color_mat[2,:], markersize=8, label='Turn 20% Act Diff')
lines.append(line)
line, = plt.plot(rad_vec_turn30, speed_vec_turn30*100, '-s', color = color_mat[3,:], markersize=8, label='Turn 30% Act Diff')
lines.append(line)
line, = plt.plot(rad_vec_turn40, speed_vec_turn40*100, '-s', color = color_mat[4,:], markersize=8, label='Turn 40% Act Diff')
lines.append(line)
line, = plt.plot(rad_vec_turn50, speed_vec_turn50*100, '-s', color = color_mat[5,:], markersize=8, label='Turn 50% Act Diff')
lines.append(line)
line, = plt.plot(rad_vec_turn60, speed_vec_turn60*100, '-s', color = color_mat[6,:], markersize=8, label='Turn 60% Act Diff')
lines.append(line)
line, = plt.plot(rad_vec_turn70, speed_vec_turn70*100, '-s', color = color_mat[7,:], markersize=8, label='Turn 70% Act Diff')
lines.append(line)
line, = plt.plot(rad_vec_turn80, speed_vec_turn80*100, '-s', color = color_mat[8,:], markersize=8, label='Turn 80% Act Diff')
lines.append(line)
line, = plt.plot(rad_vec_turn90, speed_vec_turn90*100, '-s', color = color_mat[9,:], markersize=8, label='Turn 90% Act Diff')
lines.append(line)
line, = plt.plot(rad_vec_turn100, speed_vec_turn100*100, '-s', color = color_mat[10,:], markersize=8, label='Turn 100% Act Diff')
lines.append(line)
line, = plt.plot(rad_vec_adapt, speed_vec_adapt*100, '-*', color = 'Green', markersize=8, linewidth=2.5, label='Adaptive Act Diff')
lines.append(line)

plt.xlim(left=0.4)
plt.xlim(right=1.35)
plt.ylim(top=4.4)
plt.ylim(bottom=2.0)
plt.xlabel('Pipe Bend Radius of Curvature (m)', fontsize = 12, fontname="Arial")
plt.ylabel('Average Speed in Pipe (cm/s)', fontsize = 12, fontname="Arial")
plt.legend(handles=lines[:], labels=labels[:])
plt.text(0.45, 4.15, 'Straight Pipe', fontsize = 9, fontname="Arial", color = 'Black', ha='left', va='bottom')
# plt.savefig("Speed_vs_ROC_Wide_Pipes_Turning_Bias.png", format="png")
plt.show()




########## Speed vs. Pipe Radii of Curvature Combined Results 3D
bias_vec_base = np.ones(10)
markers = ['o', 's', '^', 'D', 'v', 'X', 'P', '*', 'h']
radii = np.array([0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3])
speeds = np.array([[np.append([0, 0], speed_vec_norm*100)],
                   [np.append([0, 0], speed_vec_turn10*100)],
                   [np.append(0, speed_vec_turn20*100)],
                   [np.append(0, speed_vec_turn30*100)],
                   [np.append(0, speed_vec_turn40*100)],
                   [np.append(0, speed_vec_turn50*100)],
                   [np.append(0, speed_vec_turn60*100)],
                   [speed_vec_turn70*100],
                   [speed_vec_turn80*100],
                   [speed_vec_turn90*100],
                   [speed_vec_turn100*100]])
speeds = np.squeeze(speeds)

fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.plot(rad_vec_norm, 0*bias_vec_base[0:np.size(rad_vec_norm)], speed_vec_norm*100, color = color_mat[0,:], markersize=8, label='Norm 0% Act Diff')
ax.plot(rad_vec_turn10, 10*bias_vec_base[0:np.size(rad_vec_turn10)], speed_vec_turn10*100, color = color_mat[1,:], markersize=8, label='Turn 10% Act Diff')
ax.plot(rad_vec_turn20, 20*bias_vec_base[0:np.size(rad_vec_turn20)], speed_vec_turn20*100, color = color_mat[2,:], markersize=8, label='Turn 20% Act Diff')
ax.plot(rad_vec_turn30, 30*bias_vec_base[0:np.size(rad_vec_turn30)], speed_vec_turn30*100, color = color_mat[3,:], markersize=8, label='Turn 30% Act Diff')
ax.plot(rad_vec_turn40, 40*bias_vec_base[0:np.size(rad_vec_turn40)], speed_vec_turn40*100, color = color_mat[4,:], markersize=8, label='Turn 40% Act Diff')
ax.plot(rad_vec_turn50, 50*bias_vec_base[0:np.size(rad_vec_turn50)], speed_vec_turn50*100, color = color_mat[5,:], markersize=8, label='Turn 50% Act Diff')
ax.plot(rad_vec_turn60, 60*bias_vec_base[0:np.size(rad_vec_turn60)], speed_vec_turn60*100, color = color_mat[6,:], markersize=8, label='Turn 60% Act Diff')
ax.plot(rad_vec_turn70, 70*bias_vec_base[0:np.size(rad_vec_turn70)], speed_vec_turn70*100, color = color_mat[7,:], markersize=8, label='Turn 70% Act Diff')
ax.plot(rad_vec_turn80, 80*bias_vec_base[0:np.size(rad_vec_turn80)], speed_vec_turn80*100, color = color_mat[8,:], markersize=8, label='Turn 80% Act Diff')
ax.plot(rad_vec_turn90, 90*bias_vec_base[0:np.size(rad_vec_turn90)], speed_vec_turn90*100, color = color_mat[9,:], markersize=8, label='Turn 90% Act Diff')
ax.plot(rad_vec_turn100, 100*bias_vec_base[0:np.size(rad_vec_turn100)], speed_vec_turn100*100, color = color_mat[10,:], markersize=8, label='Turn 100% Act Diff')
# ax.plot(rad_vec_adapt, -20*bias_vec_base[0:np.size(rad_vec_adapt)], speed_vec_adapt*100, '-*', color = 'Green', markersize=8, label='Adaptive Act Diff')

# Plot the line markers to indicate pipe ROC
for j in range(speeds.shape[0]):
    array1 = speeds[j,:]
    for i in range(array1.shape[0]):
        if array1[i] != 0:
            ax.plot(radii[i], (10*j), array1[i], marker = markers[i], color = color_mat[j,:], markersize=10, label='_nolegend_')

norm = plt.Normalize(vmin=0, vmax=100)
# sm = cm.ScalarMappable(norm=norm, cmap='plasma')
sm = cm.ScalarMappable(norm=norm, cmap=plasma_trunc)
# im = ax.imshow(speeds, extent=[radii.min(), radii.max(), act_diffs.min(), act_diffs.max()], origin='lower', aspect='auto', cmap='plasma', norm=norm)
cbar = fig.colorbar(sm, ax=ax, label='Activation Difference (%)', shrink=0.6, orientation='horizontal')
cbar.ax.invert_xaxis()
ax.set_xlabel('Pipe Bend Radius of Curvature (m)', fontsize = 12, fontname="Arial")
ax.set_ylabel('Activation Difference (%)', fontsize = 12, fontname="Arial")
ax.set_zlabel('Average Speed in Pipe (cm/s)', fontsize = 12, fontname="Arial")
# ax.legend()
plt.show()




########## Speed vs. Pipe Radii of Curvature Combined Results 3D Gray
bias_vec_base = np.ones(10)
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.plot(rad_vec_norm, 0*bias_vec_base[0:np.size(rad_vec_norm)], speed_vec_norm*100, color = '0.6', label='_nolegend_')
ax.plot(rad_vec_turn10, 10*bias_vec_base[0:np.size(rad_vec_turn10)], speed_vec_turn10*100, color = '0.6', label='_nolegend_')
ax.plot(rad_vec_turn20, 20*bias_vec_base[0:np.size(rad_vec_turn20)], speed_vec_turn20*100, color = '0.6', label='_nolegend_')
ax.plot(rad_vec_turn30, 30*bias_vec_base[0:np.size(rad_vec_turn30)], speed_vec_turn30*100, color = '0.6', label='_nolegend_')
ax.plot(rad_vec_turn40, 40*bias_vec_base[0:np.size(rad_vec_turn40)], speed_vec_turn40*100, color = '0.6', label='_nolegend_')
ax.plot(rad_vec_turn50, 50*bias_vec_base[0:np.size(rad_vec_turn50)], speed_vec_turn50*100, color = '0.6', label='_nolegend_')
ax.plot(rad_vec_turn60, 60*bias_vec_base[0:np.size(rad_vec_turn60)], speed_vec_turn60*100, color = '0.6', label='_nolegend_')
ax.plot(rad_vec_turn70, 70*bias_vec_base[0:np.size(rad_vec_turn70)], speed_vec_turn70*100, color = '0.6', label='_nolegend_')
ax.plot(rad_vec_turn80, 80*bias_vec_base[0:np.size(rad_vec_turn80)], speed_vec_turn80*100, color = '0.6', label='_nolegend_')
ax.plot(rad_vec_turn90, 90*bias_vec_base[0:np.size(rad_vec_turn90)], speed_vec_turn90*100, color = '0.6', label='_nolegend_')
ax.plot(rad_vec_turn100, 100*bias_vec_base[0:np.size(rad_vec_turn100)], speed_vec_turn100*100, color = '0.6', label='_nolegend_')
ax.plot(rad_vec_adapt, percent_diffs, speed_vec_adapt*100, '-*', color = 'Green', label='Adaptive Act Diff')

for i in range(speed_vec_adapt.shape[0]):
    if speed_vec_adapt[i] != 0:
        ax.plot(radii[i], percent_diffs[i], speed_vec_adapt[i]*100, marker = markers[i], color = 'Green', markersize=10, label='_nolegend_')

ax.set_xlabel('Pipe Bend Radius of Curvature (m)', fontsize = 12, fontname="Arial")
ax.set_ylabel('Activation Difference (%)', fontsize = 12, fontname="Arial")
ax.set_zlabel('Average Speed in Pipe (cm/s)', fontsize = 12, fontname="Arial")
ax.legend()
plt.show()

## % performance loss from fastest turn to adaptive turn (for each ROC)
max_manual_speeds = np.max(speeds, axis=0)
print("Max Speed per ROC :", max_manual_speeds)
print("Adaptive Speeds :", speed_vec_adapt*100)
p_loss = (max_manual_speeds-speed_vec_adapt*100)/max_manual_speeds*100
print("Percent Performance Loss at Each ROC :", p_loss)
print("Average Percent Loss : ", np.mean(p_loss))




########## Supplemental Figure Comparing Phase Lag Method to Straight-line
data_filenames = [r'\Phase_shift_3x1_0.5r.csv', r'\Phase_shift_3x1_0.6r.csv', r'\Phase_shift_3x1_0.7r.csv', r'\Phase_shift_3x1_0.8r.csv', r'\Phase_shift_3x1_0.9r.csv', r'\Phase_shift_3x1_1.0r.csv', r'\Phase_shift_3x1_1.1r.csv', r'\Phase_shift_3x1_1.2r.csv', r'\Phase_shift_3x1_1.3r.csv']
results = r'\Phase Shift'

cols = [range(8), range(9, 16), range(17, 23), range(24, 30)]
flattened_list = [item for r in cols for item in r]
# data1 = np.loadtxt(work_dir + results + data_filenames[0], delimiter=',', skiprows=1, usecols=flattened_list)
# data2 = np.loadtxt(work_dir + results + data_filenames[1], delimiter=',', skiprows=1, usecols=flattened_list)
data3 = np.loadtxt(work_dir + results + data_filenames[2], delimiter=',', skiprows=1, usecols=flattened_list)
data4 = np.loadtxt(work_dir + results + data_filenames[3], delimiter=',', skiprows=1, usecols=flattened_list)
data5 = np.loadtxt(work_dir + results + data_filenames[4], delimiter=',', skiprows=1, usecols=flattened_list)
data6 = np.loadtxt(work_dir + results + data_filenames[5], delimiter=',', skiprows=1, usecols=flattened_list)
data7 = np.loadtxt(work_dir + results + data_filenames[6], delimiter=',', skiprows=1, usecols=flattened_list)
data8 = np.loadtxt(work_dir + results + data_filenames[7], delimiter=',', skiprows=1, usecols=flattened_list)
data9 = np.loadtxt(work_dir + results + data_filenames[8], delimiter=',', skiprows=1, usecols=flattened_list)

data_mat = np.dstack((data3, data4, data5, data6, data7, data8, data9))
rad_vec_phase = np.array([0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3])
speed_vec_phase = avg_speed(data_mat, rad_vec_phase, l_0)
# color_mat = cm.rainbow(np.linspace(0, 1, data_mat.shape[2]))
# leg_vec = ['0.7', '0.8', '0.9', '1.0', '1.1', '1.2', '1.3']
# speed_vec_phase = avg_speed_plotted(data_mat, rad_vec_phase, l_0, pipe_rad, color_mat, leg_vec)

fig = plt.figure(figsize = (10,7))
lines = []
labels = []
line, = plt.plot(rad_vec_norm, speed_vec_norm*100, color = 'Red', markersize=8, label='Straight-line')
lines.append(line)
line, = plt.plot(rad_vec_phase, speed_vec_phase*100, color = 'Black', markersize=8, label='Phase Lag Turn')
lines.append(line)
plt.xlim(left=0.4)
plt.xlim(right=1.35)
plt.ylim(top=4.2)
plt.xlabel('Pipe Bend Radius of Curvature (m)', fontsize = 12, fontname="Arial")
plt.ylabel('Average Speed in Pipe (cm/s)', fontsize = 12, fontname="Arial")
plt.legend(handles=lines[:], labels=labels[:])
plt.show()




# ########## Height Map (different visualization of the 3D data) (Unused)
# from matplotlib.colors import Normalize
# radii = np.array([0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3])
# act_diffs = np.array([0, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100])
# speeds = np.array([[np.append([0, 0], speed_vec_norm*100)],
#                    [np.append([0, 0], speed_vec_turn10*100)],
#                    [np.append(0, speed_vec_turn20*100)],
#                    [np.append(0, speed_vec_turn30*100)],
#                    [np.append(0, speed_vec_turn40*100)],
#                    [np.append(0, speed_vec_turn50*100)],
#                    [np.append(0, speed_vec_turn60*100)],
#                    [speed_vec_turn70*100],
#                    [speed_vec_turn80*100],
#                    [speed_vec_turn90*100],
#                    [speed_vec_turn100*100]])
# speeds_adapt = speed_vec_adapt*100
# speeds = np.squeeze(speeds)
# print(speeds.shape)
# print(speeds_adapt.shape)

# R, A = np.meshgrid(radii, act_diffs)
# # norm = Normalize(vmin=np.nanmin(Z_fine), vmax=np.nanmax(Z_fine))
# norm = Normalize(vmin=2, vmax=np.nanmax(speeds_adapt))

# fig, axs = plt.subplots(2, 1, figsize=(7, 7), constrained_layout=True)
# axs[0] = plt.subplot2grid((10,1), (1,0), rowspan=9)
# axs[1] = plt.subplot2grid((10,1), (0,0), rowspan=1)

# im = axs[0].imshow(speeds, extent=[radii.min(), radii.max(), act_diffs.min(), act_diffs.max()], origin='lower', aspect='auto', cmap='plasma', norm=norm)
# axs[0].set_xlabel("Pipe Bend Radius of Curvature (m)")
# axs[0].set_ylabel("% Activation Difference")
# cbar = fig.colorbar(im, ax=axs[0], label='Average Speed in Pipe (cm/s)')

# axs[1].imshow(speeds_adapt[np.newaxis, :], extent=[radii.min(), radii.max(), 0, 1], aspect='auto', cmap='plasma', norm=norm)
# axs[1].set_xticklabels([])
# axs[1].set_yticklabels([])
# axs[1].set_ylabel("Adaptive")
# plt.show()




########## Interpolated
# from scipy.interpolate import griddata

# # Flatten data for interpolation
# X, Y = np.meshgrid(radii, act_diffs)
# points = np.column_stack((X.ravel(), Y.ravel()))
# values = speeds.ravel()

# # New finer grid
# radii_fine = np.linspace(radii.min(), radii.max(), 100)
# act_diffs_fine = np.linspace(act_diffs.min(), act_diffs.max(), 100)
# X_fine, Y_fine = np.meshgrid(radii_fine, act_diffs_fine)

# # Interpolate
# Z_fine = griddata(points, values, (X_fine, Y_fine), method='cubic')

# # Plot smooth heatmap
# plt.imshow(
#     Z_fine,
#     extent=[radii.min(), radii.max(), act_diffs.min(), act_diffs.max()],
#     origin='lower',
#     aspect='auto',
#     cmap='viridis'
# )
# plt.colorbar(label='Speeds')
# plt.xlabel('Radii')
# plt.ylabel('Act Diffs')
# plt.title('Interpolated Heatmap of Speeds')
# plt.show()




# ########## Interpolated and Normalized
# from matplotlib.colors import Normalize
# from scipy.interpolate import griddata
# # Flatten data for interpolation
# X, Y = np.meshgrid(radii, act_diffs)
# points = np.column_stack((X.ravel(), Y.ravel()))
# values = speeds.ravel()

# # Create finer grid for smooth interpolation
# radii_fine = np.linspace(radii.min(), radii.max(), 200)
# act_diffs_fine = np.linspace(act_diffs.min(), act_diffs.max(), 200)
# X_fine, Y_fine = np.meshgrid(radii_fine, act_diffs_fine)

# # Interpolate to finer grid
# Z_fine = griddata(points, values, (X_fine, Y_fine), method='cubic')

# # Normalize colors between min and max
# norm = Normalize(vmin=np.nanmin(Z_fine), vmax=np.nanmax(Z_fine))

# # Plot heatmap
# plt.imshow(
#     Z_fine,
#     extent=[radii.min(), radii.max(), act_diffs.min(), act_diffs.max()],
#     origin='lower',
#     aspect='auto',
#     cmap='viridis',
#     norm=norm
# )
# plt.colorbar(label='Speeds (normalized)')
# plt.xlabel('Radii')
# plt.ylabel('Act Diffs')
# plt.title('Normalized Heatmap of Speeds')
# plt.show()