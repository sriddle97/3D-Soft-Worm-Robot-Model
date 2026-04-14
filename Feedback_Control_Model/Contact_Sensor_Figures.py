#### Plotting Contact Sensor Feedback Signals, Controller Signals, Tuning Curves, and Contact Force Feedback Results
#
# Author: Shane Riddle
#
# Last edited: 04/08/2026
#
# NOTES - Feedback signal is calculated by adding the contact sensors 
#         readings from the right and subtracting readings from the left.
#       - Be sure to change the wave_length, time_tot, and t_end in the 
#         functions below to match your experiment. Each is measured in ms
#         and reflects the peristaltic waveform parameters.
#       - Change the data_filenames, results, cols, and data_mat elements
#         to match your csv file structures and orgnization. 
#########################################################################

########################### Import packages #############################

#### Basic Utility and Plotting Packages
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
from matplotlib.collections import LineCollection

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
viridis_trunc = colors.LinearSegmentedColormap.from_list('viridis_trunc', cm.viridis(np.linspace(0, 1.0, 256))) #decided not to truncate
#####################################

#### Linear regression functions
def lin_func(x, intercept, slope):
    y = intercept + slope * x
    return y
def lin_func0(x, slope):
    y = 0 + slope * x
    return y
#####################################

#### Average Peak Force, Calculation Only
def avg_peak(data_matrix):
    wave_length = 6000
    time_tot = 100000               # 100 second cutoff was implemented
    avg_feedback_sigs = np.zeros(data_matrix.shape[2])
    for j in range(data_matrix.shape[2]):
        max_values = 0
        missed_peaks = 0
        for i in range(int(time_tot/wave_length)):
            if np.max(np.abs(data_matrix[wave_length*i:wave_length*(i+1),45,j])) > 3:
                max_values = max_values + np.max(np.abs(data_matrix[wave_length*i:wave_length*(i+1),45,j]))
            else:
                missed_peaks = missed_peaks+1
        avg_feedback_sigs[j] = max_values/(int(time_tot/wave_length)-missed_peaks)
    return avg_feedback_sigs
#####################################

#### Average Peak Force, Calculation WITH PLOTS (Optional)
def avg_peak_plotted(data_matrix):
    color_mat = cm.viridis(np.linspace(0, 1, data_matrix.shape[2]))
    fig = plt.figure(figsize = (10,4))
    ax = plt.subplot2grid((1, 1), (0, 0))
    # print(data_matrix.shape)

    wave_length = 6000
    time_tot = 100000           # 100 second cutoff was implemented for calculations
    t_end = 100000              # t_end dictates how much to plot (can be <= time_tot)
    avg_feedback_sigs = np.zeros(data_matrix.shape[2])
    for j in range(data_matrix.shape[2]):
        ax.plot(data_matrix[0:t_end,0,j]*1/1000, data_matrix[0:t_end,45,j], color = color_mat[j])

        max_values = 0
        missed_peaks = 0
        for i in range(int(time_tot/wave_length)):
            if np.max(np.abs(data_matrix[wave_length*i:wave_length*(i+1),45,j])) > 3:
                max_values = max_values + np.max(np.abs(data_matrix[wave_length*i:wave_length*(i+1),45,j]))
            else:
                missed_peaks = missed_peaks+1
        avg_feedback_sigs[j] = max_values/(int(time_tot/wave_length)-missed_peaks)

    ax.set_ylim(bottom = -5, top = 20)
    ax.set_xlim(left = 0, right = t_end/1000)
    ax.set_ylabel('Feedback Signal (N)', fontsize = 12, fontname="Arial")
    ax.set_xlabel('Time (s)', fontsize = 12, fontname="Arial")

    norm = plt.Normalize(vmin=0.5, vmax=1.3)
    sm = cm.ScalarMappable(norm=norm, cmap='viridis')
    cbar = fig.colorbar(sm, ax=ax, label='Pipe Bend ROC (m)')
    cbar.ax.invert_yaxis()

    plt.tight_layout()
    # plt.savefig("Feedback_Signals_Raw.png", format="png")
    plt.show()

    rad_vec = np.array([0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3])
    points = np.array([rad_vec, avg_feedback_sigs]).T.reshape(-1, 1, 2)
    segments = np.concatenate([points[:-1], points[1:]], axis=1)
    t = np.linspace(0, 1, len(rad_vec))  # parameter for color
    lc = LineCollection(segments, cmap='viridis', norm=plt.Normalize(0, 0.9))
    lc.set_array(t)        # apply the color values
    lc.set_linewidth(3)


    fig, ax = plt.subplots(figsize = (10,4))
    ax.add_collection(lc)
    ax.set_xlim(rad_vec.min(), rad_vec.max())
    ax.set_ylim(avg_feedback_sigs.min(), avg_feedback_sigs.max())
    # ax.plot(rad_vec, max_feedback_sigs, color = 'k')
    ax.set_ylabel('Average Peak Feedback Signal (N)', fontsize = 12, fontname="Arial")
    ax.set_xlabel('Pipe Bend ROC (m)', fontsize = 12, fontname="Arial")
    plt.tight_layout()
    plt.show()
    return avg_feedback_sigs
#########################################################################

################## Read and plot data from excel files ##################

# Automatically identify work directory
work_dir = os.getcwd()
print("String format :", work_dir)
Nseg = 6                            # Number of segments
Ntouch = 4                          # Number of left-right touch sensors 
count = 0

########## Distributed Contact Sensor Feedback Signals: Organized by Sensor Location (top-left, bottom-right, etc.)
data_filenames = [r'\Time_sens_adapt_75N.csv']
# data_filenames = [r'\Time_sens_75N.csv']
results = r'\Sens Results'

# cols = [range(8), range(9, 16), range(38, 44), range(45, 51), range(52, 58), range(59, 65)]
cols = [range(8), range(9, 16), range(66, 72), range(73, 79), range(80, 86), range(87, 93), range(94,100)]
flattened_list = [item for r in cols for item in r]
data1 = np.loadtxt(work_dir + results + data_filenames[0], delimiter=',', skiprows=1, usecols=flattened_list)

# data_mat = np.dstack((data1))
color_mat = cm.rainbow(np.linspace(0, 1, Nseg))

# fig = plt.figure(figsize = (16,13))
fig = plt.figure(figsize = (10,8))
Sensor = ["Top Left Sensor", "Bottom Left Sensor", "Top Right Sensor", "Bottom Right Sensor"]
for ct in range(1, Ntouch+1):
    ax = plt.subplot2grid((Ntouch, 1), (ct-1, 0))

    for j in range(Nseg):
        ax.plot(data1[:,0], data1[:,15+Nseg*(ct-1)+j], color = color_mat[j,:])
    ax.plot(data1[:,0], data1[:,17+Nseg*(Ntouch)+ct-1], color = 'Black')
    
    ax.set_ylim(bottom = 0, top = 14)
    ax.set_ylabel('Contact Force (N)', fontsize = 12, fontname="Arial")
    ax.set_title(Sensor[ct-1], fontsize = 14, fontname="Arial", fontweight="bold")
ax.set_xlabel('Time (ms)', fontsize = 12, fontname="Arial")
ax.legend(['Segment 1', 'Segment 2', 'Segment 3', 'Segment 4', 'Segment 5', 'Segment 6', 'Front'])

plt.tight_layout()
# plt.savefig("Touch_Sensor_Data_Adapt.png", format="png")
# plt.savefig("Touch_Sensor_Data_Norm.png", format="png")
plt.show()




########## Distributed Contact Sensor Feedback Signals: Organized by Segment
# data_filenames = [r'\Time_sens_adapt_75N.csv', r'\Time_sens_75N.csv']
# data_filenames = [r'\Time_sens_adapt_75N.csv']
# data_filenames = [r'\Time_sens_75N.csv']
# data_filenames = [r'\Time_sens_0.9r_norm_f0.3.csv']
# data_filenames = [r'\Time_sens_0.9r_adapt_f0.3.csv']
# results = r'\Sens Results'
data_filenames = [r'\Time_sens_S_Shape0.8_0.8.csv']
results = r'\Sens Results\S_Shape'

# cols = [range(8), range(9, 16), range(38, 44), range(45, 51), range(52, 58), range(59, 65)]
cols = [range(8), range(9, 16), range(66, 72), range(73, 79), range(80, 86), range(87, 93), range(94,100)]
flattened_list = [item for r in cols for item in r]
data1 = np.loadtxt(work_dir + results + data_filenames[0], delimiter=',', skiprows=1, usecols=flattened_list)
# data2 = np.loadtxt(work_dir + results + data_filenames[1], delimiter=',', skiprows=1, usecols=flattened_list)

# data_mat = np.dstack((data1))
color_mat = cm.rainbow(np.linspace(0, 1, Nseg))

# fig = plt.figure(figsize = (16,13))
fig = plt.figure(figsize = (10,12))
Segment = ["Segment 1", "Segment 2", "Segment 3", "Segment 4", "Segment 5", "Segment 6"]
front_comb = -data1[:,41]-data1[:,42]+data1[:,43]+data1[:,44]
for j in range(Nseg):
    data_comb = 0
    ax = plt.subplot2grid((Nseg, 1), (j, 0))

    for ct in range(1, Ntouch+1):               # Order for sensors is left-left-right-right (left -, right +)
        if ct == 1 or ct == 2:
            data_comb = data_comb - data1[:,15+Nseg*(ct-1)+j]
        elif ct == 3 or ct == 4:
            data_comb = data_comb + data1[:,15+Nseg*(ct-1)+j]
    ax.plot(data1[:,0], data_comb, color = color_mat[j,:])
    # ax.plot(data1[:,0], data1[:,17+Nseg*(Ntouch)+ct-1], color = 'Black')
    ax.plot(data1[:,0], front_comb, color = 'Black')

    ax.set_ylim(bottom = -25, top = 25)
    ax.set_ylabel('Feedback Signal (N)', fontsize = 12, fontname="Arial")
    ax.set_title(Segment[j], fontsize = 14, fontname="Arial", fontweight="bold")
ax.set_xlabel('Time (ms)', fontsize = 12, fontname="Arial")

plt.tight_layout()
# plt.savefig("Touch_Sensor_Combined_Adapt.png", format="png")
# plt.savefig("Touch_Sensor_Combined_Norm.png", format="png")
plt.show()




########## Feedback Signal Input and Control Output Overlay (S-Shape)
data_filenames = [r'\Time_sens_S_Shape0.7_0.7.csv']
results = r'\Sens Results\S_Shape'

cols = [range(1), range(115, 118)]
flattened_list = [item for r in cols for item in r]
data1 = np.loadtxt(work_dir + results + data_filenames[0], delimiter=',', skiprows=1, usecols=flattened_list)
# print(data1.shape)

percent_diff = -1*(data1[:,2]-data1[:,3])*100

fig, ax1 = plt.subplots(figsize = (8,3), constrained_layout=True)
ax1.plot(data1[0:100000,0]*0.001, data1[0:100000,1], color = 'Black', alpha = 0.4)          # plot opaque raw feedback signal
ax1.set_ylabel('Feedback Signal (N)', fontsize = 12, fontname="Arial", color = 'Black')
ax1.set_xlabel('Time (s)', fontsize = 12, fontname="Arial")
ax1.tick_params(axis='y', labelcolor='Black')
ax1.set_ylim(top = 15, bottom = -15)

ax2 = ax1.twinx()
ax2.plot(data1[0:100000,0]*0.001, percent_diff[0:100000], color = 'Red')      # plot red controller signal
ax2.set_ylabel('Activation Difference (%)', fontsize = 12, fontname="Arial", color = 'Red')
ax2.tick_params(axis = 'y', labelcolor = 'Red')
ax2.set_ylim(top = 100, bottom = -100)

plt.text(50, -85, 'S-Shape Pipe (0.7-0.7m ROC)', fontsize = 12, fontname="Arial", fontweight='bold', color = 'Black', ha='center', va='bottom')
plt.tight_layout()
# plt.savefig("Feedback_raw_and_filtered_S_Shape.png", format="png")
plt.show()




########## Feedback Signal Input and Control Output Overlay (Spiral)
data_filenames = [r'\Time_sens_spiral_pipe0.3_adapt.csv']
results = r'\Sens Results\Spiral'

cols = [range(1), range(115, 118)]
flattened_list = [item for r in cols for item in r]
data1 = np.loadtxt(work_dir + results + data_filenames[0], delimiter=',', skiprows=1, usecols=flattened_list)

percent_diff = -1*(data1[:,2]-data1[:,3])*100

fig, ax1 = plt.subplots(figsize = (8,3), constrained_layout=True)
ax1.plot(data1[0:190000,0]*0.001, data1[0:190000,1], color = 'Black', alpha = 0.4)          # plot opaque raw feedback signal
ax1.set_ylabel('Feedback Signal (N)', fontsize = 12, fontname="Arial", color = 'Black')
ax1.set_xlabel('Time (s)', fontsize = 12, fontname="Arial")
ax1.tick_params(axis='y', labelcolor='Black')
ax1.set_ylim(top = 15, bottom = -15)

ax2 = ax1.twinx()
ax2.plot(data1[0:190000,0]*0.001, percent_diff[0:190000], color = 'Red')      # plot red controller signal
ax2.set_ylabel('Activation Difference (%)', fontsize = 12, fontname="Arial", color = 'Red')
ax2.tick_params(axis = 'y', labelcolor = 'Red')
ax2.set_ylim(top = 100, bottom = -100)

plt.text(90, -85, 'Spiral Pipe (1.3-0.5m ROC)', fontsize = 12, fontname="Arial", fontweight='bold', color = 'Black', ha='center', va='bottom')
plt.tight_layout()
# plt.savefig("Feedback_raw_and_filtered_Spiral.png", format="png")
plt.show()



########## Feedback Signal Input and Control Output Overlay (90_deg bend)
data_filenames = [r'\Time_sens_0.5r_adapt_f0.3.csv']
results = r'\Sens Results\rl0.01_mf15'

cols = [range(1), range(115, 118)]
flattened_list = [item for r in cols for item in r]
data1 = np.loadtxt(work_dir + results + data_filenames[0], delimiter=',', skiprows=1, usecols=flattened_list)

percent_diff = -1*(data1[:,2]-data1[:,3])*100

fig, ax1 = plt.subplots(figsize = (8,3), constrained_layout=True)
ax1.plot(data1[0:60000,0]*0.001, data1[0:60000,1], color = 'Black', alpha = 0.4)          # plot opaque raw feedback signal
ax1.set_ylabel('Feedback Signal (N)', fontsize = 12, fontname="Arial", color = 'Black')
ax1.set_xlabel('Time (s)', fontsize = 12, fontname="Arial")
ax1.tick_params(axis='y', labelcolor='Black')
ax1.set_ylim(top = 15, bottom = -15)

ax2 = ax1.twinx()
ax2.plot(data1[0:60000,0]*0.001, percent_diff[0:60000], color = 'Red')      # plot red controller signal
ax2.set_ylabel('Activation Difference (%)', fontsize = 12, fontname="Arial", color = 'Red')
ax2.tick_params(axis = 'y', labelcolor = 'Red')
ax2.set_ylim(top = 100, bottom = -100)

plt.text(30, -85, '90$\degree$ Pipe Bend (0.5m ROC)', fontsize = 12, fontname="Arial", fontweight='bold', color = 'Black', ha='center', va='bottom')
plt.tight_layout()
# plt.savefig("Feedback_raw_and_filtered_90deg_0.5r.png", format="png")
plt.show()




########## Straight-line Algorithm Average Feedback Signal Peak vs. Pipe Radii of Curvature (Raw Data & Tuning Curve Plotted)
data_filenames = [r'\Time_sens_0.5r_norm_f0.3.csv', r'\Time_sens_0.6r_norm_f0.3.csv', r'\Time_sens_0.7r_norm_f0.3.csv', r'\Time_sens_0.8r_norm_f0.3.csv', r'\Time_sens_0.9r_norm_f0.3.csv', r'\Time_sens_1.0r_norm_f0.3.csv', r'\Time_sens_1.1r_norm_f0.3.csv', r'\Time_sens_1.2r_norm_f0.3.csv', r'\Time_sens_1.3r_norm_f0.3.csv']
results = r'\Sens Results'

# cols = [range(8), range(9, 16), range(38, 44), range(45, 51), range(52, 58), range(59, 65)]
cols = [range(8), range(9, 16), range(66, 72), range(73, 79), range(80, 86), range(87, 93), range(94,100)]
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
# color_mat = [str(j) for j in np.linspace(0, 0.8, data_mat.shape[2])]        # For grayscale
# color_mat = cm.viridis(np.linspace(0, 1, data_mat.shape[2]))                # For un-truncated viridis (lighter yellows)
color_mat = viridis_trunc(np.linspace(0, 1, data_mat.shape[2]))

## Raw Data
fig = plt.figure(figsize = (10,4))
max_feedback_sigs = np.zeros(data_mat.shape[2])
ax = plt.subplot2grid((1, 1), (0, 0))
front_comb = np.zeros((data_mat.shape[0], data_mat.shape[2]))
wave_length = 6000
time_tot = 100000
t_end = 60000
for j in range(data_mat.shape[2]):
    front_comb[:,j] = -data_mat[:,41,j]-data_mat[:,42,j]+data_mat[:,43,j]+data_mat[:,44,j]
    ax.plot(data_mat[0:t_end,0,j]*1/1000, front_comb[0:t_end,j], color = color_mat[j])

    max_values = 0
    missed_peaks = 0
    for i in range(int(time_tot/wave_length)):
        if np.max(np.abs(front_comb[wave_length*i:wave_length*(i+1),j])) > 3:
            max_values = max_values + np.max(np.abs(front_comb[wave_length*i:wave_length*(i+1),j]))
        else:
            missed_peaks = missed_peaks+1
    
    max_feedback_sigs[j] = max_values/(int(time_tot/wave_length)-missed_peaks)

ax.set_ylim(bottom = -5, top = 20)
ax.set_xlim(left = 0, right = t_end/1000)
# ax.set_ylabel('Combined Contact Force at Tip (N)', fontsize = 12, fontname="Arial")
ax.set_ylabel('Feedback Signal (N)', fontsize = 12, fontname="Arial")
ax.set_xlabel('Time (s)', fontsize = 12, fontname="Arial")
# ax.legend(['0.5', '0.6', '0.7', '0.8', '0.9', '1.0', '1.1', '1.2', '1.3'])

norm = plt.Normalize(vmin=0.5, vmax=1.3)
# sm = cm.ScalarMappable(norm=norm, cmap='viridis')
sm = cm.ScalarMappable(norm=norm, cmap=viridis_trunc)
cbar = fig.colorbar(sm, ax=ax, label='Pipe Bend ROC (m)')
cbar.ax.invert_yaxis()

plt.tight_layout()
# plt.savefig("Feedback_Signals_Raw.png", format="png")
plt.show()


## Tuning Curve
rad_vec = np.array([0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3])

# line color gradient
points = np.array([rad_vec, max_feedback_sigs]).T.reshape(-1, 1, 2)
segments = np.concatenate([points[:-1], points[1:]], axis=1)
t = np.linspace(0, 1, len(rad_vec))  # parameter for color
lc = LineCollection(segments, cmap=viridis_trunc)                               # Normalize needed with new truncated map?
lc.set_array(t)        # apply the color values
lc.set_linewidth(3)

fig, ax = plt.subplots(figsize = (10,4))
ax.add_collection(lc)
ax.set_xlim(rad_vec.min(), rad_vec.max())
ax.set_ylim(max_feedback_sigs.min(), max_feedback_sigs.max())
ax.set_ylabel('Average Peak Feedback Signal (N)', fontsize = 12, fontname="Arial")
ax.set_xlabel('Pipe Bend ROC (m)', fontsize = 12, fontname="Arial")
plt.tight_layout()
plt.show()

avg_feedback_00 = max_feedback_sigs
count = count+1


# ## Optional 3D plot
# fig = plt.figure()
# ax = fig.add_subplot(111, projection='3d')
# rad_vec_base = np.ones(data_mat.shape[0])
# for j in range(data_mat.shape[2]):
#     ax.plot(rad_vec[j]*rad_vec_base[0:t_end], data_mat[0:t_end,0,j], front_comb[0:t_end,j], color = color_mat[j])           # add label = '' to get a legend

# # # Draw markers ON the x-axis (y=0, z=0)
# # markers = ['o', 's', '^', 'D', 'v', 'X', 'P', '*', 'h']
# # for xi, m in zip(rad_vec, markers):
# #     ax.scatter(xi, 0, 0, marker=m, s=80, color='black')

# norm = plt.Normalize(vmin=0.5, vmax=1.3)
# # sm = cm.ScalarMappable(norm=norm, cmap='viridis')
# sm = cm.ScalarMappable(norm=norm, cmap=viridis_trunc)
# cbar = fig.colorbar(sm, ax=ax, label='Pipe ROC (m)', shrink=0.7)

# ax.set_box_aspect([1, 2, 1])
# ax.set_xlabel('Pipe Bend ROC (m)', fontsize = 12, fontname="Arial")
# ax.set_ylabel('Time (ms)', fontsize = 12, fontname="Arial")
# ax.set_zlabel('Feedback Signal (N)', fontsize = 12, fontname="Arial")
# plt.tight_layout()
# # plt.savefig("Feedback_Signals_Raw_3D.png", format="png")
# plt.show()




########## Average Feedback Signal Peak vs. Pipe Radii of Curvature: 100% act diff
data_filenames = [r'\Time_sens_0.5r_manual0.0_f0.3.csv', r'\Time_sens_0.6r_manual0.0_f0.3.csv', r'\Time_sens_0.7r_manual0.0_f0.3.csv', r'\Time_sens_0.8r_manual0.0_f0.3.csv', r'\Time_sens_0.9r_manual0.0_f0.3.csv', r'\Time_sens_1.0r_manual0.0_f0.3.csv', r'\Time_sens_1.1r_manual0.0_f0.3.csv', r'\Time_sens_1.2r_manual0.0_f0.3.csv', r'\Time_sens_1.3r_manual0.0_f0.3.csv']
results = r'\Sens Results\Manual'

cols = [range(8), range(9, 16), range(66, 72), range(73, 79), range(80, 86), range(87, 93), range(94,100), range(115, 118)]
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
avg_feedback_100 = avg_peak(data_mat)
# avg_feedback_100 = avg_peak_plotted(data_mat)
count = count+1




########## Average Feedback Signal Peak vs. Pipe Radii of Curvature: 90% act diff
data_filenames = [r'\Time_sens_0.5r_manual0.1_f0.3.csv', r'\Time_sens_0.6r_manual0.1_f0.3.csv', r'\Time_sens_0.7r_manual0.1_f0.3.csv', r'\Time_sens_0.8r_manual0.1_f0.3.csv', r'\Time_sens_0.9r_manual0.1_f0.3.csv', r'\Time_sens_1.0r_manual0.1_f0.3.csv', r'\Time_sens_1.1r_manual0.1_f0.3.csv', r'\Time_sens_1.2r_manual0.1_f0.3.csv', r'\Time_sens_1.3r_manual0.1_f0.3.csv']
results = r'\Sens Results\Manual'

cols = [range(8), range(9, 16), range(66, 72), range(73, 79), range(80, 86), range(87, 93), range(94,100), range(115, 118)]
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
avg_feedback_90 = avg_peak(data_mat)
# avg_feedback_90 = avg_peak_plotted(data_mat)
count = count+1




########## Average Feedback Signal Peak vs. Pipe Radii of Curvature: 80% act diff
data_filenames = [r'\Time_sens_0.5r_manual0.2_f0.3.csv', r'\Time_sens_0.6r_manual0.2_f0.3.csv', r'\Time_sens_0.7r_manual0.2_f0.3.csv', r'\Time_sens_0.8r_manual0.2_f0.3.csv', r'\Time_sens_0.9r_manual0.2_f0.3.csv', r'\Time_sens_1.0r_manual0.2_f0.3.csv', r'\Time_sens_1.1r_manual0.2_f0.3.csv', r'\Time_sens_1.2r_manual0.2_f0.3.csv', r'\Time_sens_1.3r_manual0.2_f0.3.csv']
results = r'\Sens Results\Manual'

cols = [range(8), range(9, 16), range(66, 72), range(73, 79), range(80, 86), range(87, 93), range(94,100), range(115, 118)]
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
avg_feedback_80 = avg_peak(data_mat)
# avg_feedback_80 = avg_peak_plotted(data_mat)
count = count+1




########## Average Feedback Signal Peak vs. Pipe Radii of Curvature: 70% act diff
data_filenames = [r'\Time_sens_0.5r_manual0.3_f0.3.csv', r'\Time_sens_0.6r_manual0.3_f0.3.csv', r'\Time_sens_0.7r_manual0.3_f0.3.csv', r'\Time_sens_0.8r_manual0.3_f0.3.csv', r'\Time_sens_0.9r_manual0.3_f0.3.csv', r'\Time_sens_1.0r_manual0.3_f0.3.csv', r'\Time_sens_1.1r_manual0.3_f0.3.csv', r'\Time_sens_1.2r_manual0.3_f0.3.csv', r'\Time_sens_1.3r_manual0.3_f0.3.csv']
results = r'\Sens Results\Manual'

cols = [range(8), range(9, 16), range(66, 72), range(73, 79), range(80, 86), range(87, 93), range(94,100), range(115, 118)]
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
avg_feedback_70 = avg_peak(data_mat)
# avg_feedback_70 = avg_peak_plotted(data_mat)
count = count+1




########## Average Feedback Signal Peak vs. Pipe Radii of Curvature: 60% act diff
data_filenames = [r'\Time_sens_0.5r_manual0.4_f0.3.csv', r'\Time_sens_0.6r_manual0.4_f0.3.csv', r'\Time_sens_0.7r_manual0.4_f0.3.csv', r'\Time_sens_0.8r_manual0.4_f0.3.csv', r'\Time_sens_0.9r_manual0.4_f0.3.csv', r'\Time_sens_1.0r_manual0.4_f0.3.csv', r'\Time_sens_1.1r_manual0.4_f0.3.csv', r'\Time_sens_1.2r_manual0.4_f0.3.csv', r'\Time_sens_1.3r_manual0.4_f0.3.csv']
results = r'\Sens Results\Manual'

cols = [range(8), range(9, 16), range(66, 72), range(73, 79), range(80, 86), range(87, 93), range(94,100), range(115, 118)]
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
avg_feedback_60 = avg_peak(data_mat)
# avg_feedback_60 = avg_peak_plotted(data_mat)
count = count+1




########## Average Feedback Signal Peak vs. Pipe Radii of Curvature: 50% act diff
data_filenames = [r'\Time_sens_0.5r_manual0.5_f0.3.csv', r'\Time_sens_0.6r_manual0.5_f0.3.csv', r'\Time_sens_0.7r_manual0.5_f0.3.csv', r'\Time_sens_0.8r_manual0.5_f0.3.csv', r'\Time_sens_0.9r_manual0.5_f0.3.csv', r'\Time_sens_1.0r_manual0.5_f0.3.csv', r'\Time_sens_1.1r_manual0.5_f0.3.csv', r'\Time_sens_1.2r_manual0.5_f0.3.csv', r'\Time_sens_1.3r_manual0.5_f0.3.csv']
results = r'\Sens Results\Manual'

cols = [range(8), range(9, 16), range(66, 72), range(73, 79), range(80, 86), range(87, 93), range(94,100), range(115, 118)]
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
avg_feedback_50 = avg_peak(data_mat)
# avg_feedback_50 = avg_peak_plotted(data_mat)
count = count+1




########## Average Feedback Signal Peak vs. Pipe Radii of Curvature: 40% act diff
data_filenames = [r'\Time_sens_0.5r_manual0.6_f0.3.csv', r'\Time_sens_0.6r_manual0.6_f0.3.csv', r'\Time_sens_0.7r_manual0.6_f0.3.csv', r'\Time_sens_0.8r_manual0.6_f0.3.csv', r'\Time_sens_0.9r_manual0.6_f0.3.csv', r'\Time_sens_1.0r_manual0.6_f0.3.csv', r'\Time_sens_1.1r_manual0.6_f0.3.csv', r'\Time_sens_1.2r_manual0.6_f0.3.csv', r'\Time_sens_1.3r_manual0.6_f0.3.csv']
results = r'\Sens Results\Manual'

cols = [range(8), range(9, 16), range(66, 72), range(73, 79), range(80, 86), range(87, 93), range(94,100), range(115, 118)]
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
avg_feedback_40 = avg_peak(data_mat)
# avg_feedback_40 = avg_peak_plotted(data_mat)
count = count+1




########## Average Feedback Signal Peak vs. Pipe Radii of Curvature: 30% act diff
data_filenames = [r'\Time_sens_0.5r_manual0.7_f0.3.csv', r'\Time_sens_0.6r_manual0.7_f0.3.csv', r'\Time_sens_0.7r_manual0.7_f0.3.csv', r'\Time_sens_0.8r_manual0.7_f0.3.csv', r'\Time_sens_0.9r_manual0.7_f0.3.csv', r'\Time_sens_1.0r_manual0.7_f0.3.csv', r'\Time_sens_1.1r_manual0.7_f0.3.csv', r'\Time_sens_1.2r_manual0.7_f0.3.csv', r'\Time_sens_1.3r_manual0.7_f0.3.csv']
results = r'\Sens Results\Manual'

cols = [range(8), range(9, 16), range(66, 72), range(73, 79), range(80, 86), range(87, 93), range(94,100), range(115, 118)]
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
avg_feedback_30 = avg_peak(data_mat)
# avg_feedback_30 = avg_peak_plotted(data_mat)
count = count+1




########## Average Feedback Signal Peak vs. Pipe Radii of Curvature: 20% act diff
data_filenames = [r'\Time_sens_0.5r_manual0.8_f0.3.csv', r'\Time_sens_0.6r_manual0.8_f0.3.csv', r'\Time_sens_0.7r_manual0.8_f0.3.csv', r'\Time_sens_0.8r_manual0.8_f0.3.csv', r'\Time_sens_0.9r_manual0.8_f0.3.csv', r'\Time_sens_1.0r_manual0.8_f0.3.csv', r'\Time_sens_1.1r_manual0.8_f0.3.csv', r'\Time_sens_1.2r_manual0.8_f0.3.csv', r'\Time_sens_1.3r_manual0.8_f0.3.csv']
results = r'\Sens Results\Manual'

cols = [range(8), range(9, 16), range(66, 72), range(73, 79), range(80, 86), range(87, 93), range(94,100), range(115, 118)]
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
avg_feedback_20 = avg_peak(data_mat)
# avg_feedback_20 = avg_peak_plotted(data_mat)
count = count+1




########## Average Feedback Signal Peak vs. Pipe Radii of Curvature: 10% act diff
data_filenames = [r'\Time_sens_0.5r_manual0.9_f0.3.csv', r'\Time_sens_0.6r_manual0.9_f0.3.csv', r'\Time_sens_0.7r_manual0.9_f0.3.csv', r'\Time_sens_0.8r_manual0.9_f0.3.csv', r'\Time_sens_0.9r_manual0.9_f0.3.csv', r'\Time_sens_1.0r_manual0.9_f0.3.csv', r'\Time_sens_1.1r_manual0.9_f0.3.csv', r'\Time_sens_1.2r_manual0.9_f0.3.csv', r'\Time_sens_1.3r_manual0.9_f0.3.csv']
results = r'\Sens Results\Manual'

cols = [range(8), range(9, 16), range(66, 72), range(73, 79), range(80, 86), range(87, 93), range(94,100), range(115, 118)]
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
avg_feedback_10 = avg_peak(data_mat)
# avg_feedback_10 = avg_peak_plotted(data_mat)
count = count+1




########## Average Feedback Signal Peak vs. Pipe Radii of Curvature: Adaptive
data_filenames = [r'\Time_sens_0.5r_adapt_f0.3.csv', r'\Time_sens_0.6r_adapt_f0.3.csv', r'\Time_sens_0.7r_adapt_f0.3.csv', r'\Time_sens_0.8r_adapt_f0.3.csv', r'\Time_sens_0.9r_adapt_f0.3.csv', r'\Time_sens_1.0r_adapt_f0.3.csv', r'\Time_sens_1.1r_adapt_f0.3.csv', r'\Time_sens_1.2r_adapt_f0.3.csv', r'\Time_sens_1.3r_adapt_f0.3.csv']
results = r'\Sens Results\rl0.01_mf15'
# data_filenames = [r'\Time_sens_0.5r_adapt_rl0.005_mf10_f0.3.csv', r'\Time_sens_0.6r_adapt_rl0.005_mf10_f0.3.csv', r'\Time_sens_0.7r_adapt_rl0.005_mf10_f0.3.csv', r'\Time_sens_0.8r_adapt_rl0.005_mf10_f0.3.csv', r'\Time_sens_0.9r_adapt_rl0.005_mf10_f0.3.csv', r'\Time_sens_1.0r_adapt_rl0.005_mf10_f0.3.csv', r'\Time_sens_1.1r_adapt_rl0.005_mf10_f0.3.csv', r'\Time_sens_1.2r_adapt_rl0.005_mf10_f0.3.csv', r'\Time_sens_1.3r_adapt_rl0.005_mf10_f0.3.csv']
# results = r'\Sens Results\rl0.005_mf10'
# data_filenames = [r'\Time_sens_0.5r_adapt_rl0.005_mf12_f0.3.csv', r'\Time_sens_0.6r_adapt_rl0.005_mf12_f0.3.csv', r'\Time_sens_0.7r_adapt_rl0.005_mf12_f0.3.csv', r'\Time_sens_0.8r_adapt_rl0.005_mf12_f0.3.csv', r'\Time_sens_0.9r_adapt_rl0.005_mf12_f0.3.csv', r'\Time_sens_1.0r_adapt_rl0.005_mf12_f0.3.csv', r'\Time_sens_1.1r_adapt_rl0.005_mf12_f0.3.csv', r'\Time_sens_1.2r_adapt_rl0.005_mf12_f0.3.csv', r'\Time_sens_1.3r_adapt_rl0.005_mf12_f0.3.csv']
# results = r'\Sens Results\rl0.005_mf12'
# data_filenames = [r'\Time_sens_0.5r_adapt_rl0.005_mf17_f0.3.csv', r'\Time_sens_0.6r_adapt_rl0.005_mf17_f0.3.csv', r'\Time_sens_0.7r_adapt_rl0.005_mf17_f0.3.csv', r'\Time_sens_0.8r_adapt_rl0.005_mf17_f0.3.csv', r'\Time_sens_0.9r_adapt_rl0.005_mf17_f0.3.csv', r'\Time_sens_1.0r_adapt_rl0.005_mf17_f0.3.csv', r'\Time_sens_1.1r_adapt_rl0.005_mf17_f0.3.csv', r'\Time_sens_1.2r_adapt_rl0.005_mf17_f0.3.csv', r'\Time_sens_1.3r_adapt_rl0.005_mf17_f0.3.csv']
# results = r'\Sens Results\rl0.005_mf17'

cols = [range(8), range(9, 16), range(66, 72), range(73, 79), range(80, 86), range(87, 93), range(94,100), range(115, 118)]
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
avg_feedback_adapt = avg_peak(data_mat)
# avg_feedback_adapt = avg_peak_plotted(data_mat)




########## All Experimental Results Combined
# color_mat = cm.plasma(np.linspace(0, 1, count))
color_mat = plasma_trunc(np.linspace(0, 1, count))

rad_vec = np.array([0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3])
fig = plt.figure(figsize = (10,4))
ax = plt.subplot2grid((1, 1), (0, 0))
ax.plot(rad_vec, avg_feedback_00, color = color_mat[0,:], linestyle='dashed', label='_nolegend_')
ax.plot(rad_vec, avg_feedback_10, color = color_mat[1,:], linestyle='dashed', label='_nolegend_')
ax.plot(rad_vec, avg_feedback_20, color = color_mat[2,:], linestyle='dashed', label='_nolegend_')
ax.plot(rad_vec, avg_feedback_30, color = color_mat[3,:], linestyle='dashed', label='_nolegend_')
ax.plot(rad_vec, avg_feedback_40, color = color_mat[4,:], linestyle='dashed', label='_nolegend_')
ax.plot(rad_vec, avg_feedback_50, color = color_mat[5,:], linestyle='dashed', label='_nolegend_')
ax.plot(rad_vec, avg_feedback_60, color = color_mat[6,:], linestyle='dashed', label='_nolegend_')
ax.plot(rad_vec, avg_feedback_70, color = color_mat[7,:], linestyle='dashed', label='_nolegend_')
ax.plot(rad_vec, avg_feedback_80, color = color_mat[8,:], linestyle='dashed', label='_nolegend_')
ax.plot(rad_vec, avg_feedback_90, color = color_mat[9,:], linestyle='dashed', label='_nolegend_')
ax.plot(rad_vec, avg_feedback_100, color = color_mat[10,:], linestyle='dashed', label='_nolegend_')
ax.plot(rad_vec, avg_feedback_adapt, color = 'Green', linewidth=4.0, label='Adaptive Act Diff')

norm = plt.Normalize(vmin=0, vmax=100)      #vmax indicates 100th percentile of the data, not the max color used (don't change to 85)
# sm = cm.ScalarMappable(norm=norm, cmap='plasma')
sm = cm.ScalarMappable(norm=norm, cmap=plasma_trunc)
# im = ax.imshow(speeds, extent=[radii.min(), radii.max(), act_diffs.min(), act_diffs.max()], origin='lower', aspect='auto', cmap='plasma', norm=norm)
cbar = fig.colorbar(sm, ax=ax, label='Activation Difference (%)')       #, shrink=0.8)
cbar.ax.invert_yaxis()

ax.set_ylabel('Average Peak Feedback Signal (N)', fontsize = 12, fontname="Arial")
ax.set_xlabel('Pipe Bend ROC (m)', fontsize = 12, fontname="Arial")
ax.legend()
plt.tight_layout()
# plt.savefig("Average_Peak_Feedback_Signal_vs_ROC.png", format="png")
plt.show()




########## Combined Results, Subset For Easier Visualization
# color_mat = cm.plasma(np.linspace(0, 1, count))
color_mat = plasma_trunc(np.linspace(0, 1, count))

rad_vec = np.array([0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3])
fig = plt.figure(figsize = (10,4))
ax = plt.subplot2grid((1, 1), (0, 0))
ax.plot(rad_vec, avg_feedback_00, color = color_mat[0,:], linestyle='dashed', label='Norm 0% Act Diff')
ax.plot(rad_vec, avg_feedback_50, color = color_mat[5,:], linestyle='dashed', label='Turn 50% Act Diff')
ax.plot(rad_vec, avg_feedback_70, color = color_mat[7,:], linestyle='dashed', label='Turn 70% Act Diff')
ax.plot(rad_vec, avg_feedback_100, color = color_mat[10,:], linestyle='dashed', label='Turn 100% Act Diff')
ax.plot(rad_vec, avg_feedback_adapt, color = 'Green', linewidth=4.0, label='Adaptive Act Diff')

ax.set_ylabel('Average Peak Feedback Signal (N)', fontsize = 12, fontname="Arial")
ax.set_xlabel('Pipe Bend ROC (m)', fontsize = 12, fontname="Arial")
ax.legend()
# plt.tight_layout()
# plt.savefig("Average_Peak_Feedback_Signal_vs_ROC.png", format="png")
plt.show()