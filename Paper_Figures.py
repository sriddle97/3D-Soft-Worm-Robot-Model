########################### Import packages #############################


# Basic Utility and Plotting Packages
import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
import xml.etree.ElementTree as ET
import time
import os
from scipy.optimize import curve_fit
import seaborn as sns
import matplotlib.image as mpimg

# Movie Making Packages  (Use mediapy for Mujoco)
import matplotlib.animation as animation
import mediapy as media

# Excel file interaction
import pandas as pd
from openpyxl import load_workbook
import csv


#### Linear regression functions ####
def lin_func(x, intercept, slope):
    y = intercept + slope * x
    return y
def lin_func0(x, slope):
    y = 0 + slope * x
    return y
#####################################

################################### Read and plot data from excel file ############################################

# Automatically get work directory
work_dir = os.getcwd()
print("String format :", work_dir)
results = r'\Results'



########## Recorded time to run sim vs prescribed friction coefficient (90 degree pipe, 80 second sim)
friction = [0.1, 0.2, 0.3, 0.35, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9]                               # May want to run 0.01 just for this?
sim_time = np.array([8287, 8170, 7588, 6887, 6848, 6666, 6479, 6345, 6374, 6384])
sim_time = sim_time/80      # Divide by 80 to get real_time per 1 second of sim_time
plt.plot(friction, sim_time)
plt.ylabel('Simulation Run Time (s)', fontsize = 12, fontname="Arial")
plt.xlabel('Coefficient of Friction', fontsize = 12, fontname="Arial")
plt.savefig("SimTime_vs_Friction.png", format="png")
plt.show()




########## Load-frame and model segment contraction comparison (using Segment 3 for both)
data_filenames = [r'\Load_Frame_c.csv', r'\Compiled_Instron_164703.xlsx', r'\Seg3_no_pipe_0.0f_3e8.csv', r'\Seg3_no_pipe_0.0f_20e8.csv', r'\Seg3_no_pipe_0.0f_10e8.csv']
tune_folder = r'\Tuning Data'

cols1 = [range(3)]
flattened_list1 = [item for r in cols1 for item in r]
data1 = np.loadtxt(work_dir+ tune_folder + data_filenames[0], delimiter=',', skiprows=0, usecols=flattened_list1)
df = pd.read_excel(work_dir+ tune_folder + data_filenames[1], sheet_name='Sheet1')
data2 = df.to_numpy()
cols3 = [range(8), range(9, 21), range(22, 28), range(29, 35), range(36, 42), range(43,45), range(46,52), range(53,56)]
flattened_list3 = [item for r in cols3 for item in r]
data3 = np.loadtxt(work_dir+ tune_folder + data_filenames[2], delimiter=',', skiprows=1, usecols=flattened_list1)
data4 = np.loadtxt(work_dir + tune_folder + data_filenames[3], delimiter=',', skiprows=1, usecols=flattened_list1)
data5 = np.loadtxt(work_dir + tune_folder + data_filenames[4], delimiter=',', skiprows=1, usecols=flattened_list1)

x1 = data1[0:3318,0]/(1000*3)        #/1000 to get into meters and /3 to convert to diameter (hexagon geomerty says d_diam=2*d_side_length, d_side_length=d_cable_length/6, 2/6 = 1/3)
y1 = data1[0:3318,1]
x2 = data2[:,4]
y2 = data2[:,5]
x3 = data3[0:2851,2]
x3 = -(x3-x3[0])      
y3 = data3[0:2851,1]
x4 = data4[0:2851,2]
x4 = -(x4-x4[0]) 
y4 = data4[0:2851,1]
x5 = data5[0:2851,2]
x5 = -(x5-x5[0]) 
y5 = data5[0:2851,1]

print('Max for Instron Loose: ', np.max(y1))
print('Max for Instron Tightened: ', np.max(y2))
print('Max for 3e8: ', np.max(y3))
print('Max for 20e8: ', np.max(y4))
print('Max for 10e8: ', np.max(y5))

plt.plot(x1,y1, color = "Black")
plt.plot(x2,y2, color = "Black", linestyle='dashed')
plt.plot(x3,y3, color = "Blue")
plt.plot(x4,y4, color = "Red")
plt.plot(x5,y5, color = "Green")

plt.ylabel('Actuator Tension (N)', fontsize = 12, fontname="Arial")
plt.xlabel('Diameter Change (m)', fontsize = 12, fontname="Arial")
plt.legend(['Loose Joints', 'Tight Joints', 'Initial: 3e8', 'Corrected: 20e8', '10e8'])
plt.savefig("Tension_v_Disp.png", format="png")
# plt.savefig("Tension_v_Disp_trialrun.png", format="png")
plt.show()




########## Contraction-Expansion Hysteresis comparison
data_filenames = [r'\Load_Frame_c.csv', r'\Seg3_no_pipe_0.0f_20e8_updown.csv']
tune_folder = r'\Tuning Data'

cols1 = [range(3)]
flattened_list1 = [item for r in cols1 for item in r]
data1 = np.loadtxt(work_dir + tune_folder + data_filenames[0], delimiter=',', skiprows=0, usecols=flattened_list1)
data2 = np.loadtxt(work_dir + tune_folder + data_filenames[1], delimiter=',', skiprows=1, usecols=flattened_list1)

x1 = data1[:,0]/(1000*3)        #to get into meters and convert to diameter (using hexagon math, delta_diam = delta_s/3)
y1 = data1[:,1]
x2 = data2[:,2]
x2 = -(x2-x2[0]) 
y2 = data2[:,1]

plt.plot(x1,y1, color = "Black")
plt.plot(x2,y2, color = "Red")
# plt.ylim(bottom=-0.05)
# plt.xlim(left=0)
plt.ylabel('Actuator Tension (N)', fontsize = 12, fontname="Arial")
plt.xlabel('Diameter Change (m)', fontsize = 12, fontname="Arial")
plt.legend(['Instron', 'Model: 20e8'])
plt.savefig("Tension_v_Disp_Hysteresis.png", format="png")
plt.show()




########## Segment length recordings for Wang robot data comparison (used 0.7 friction, best guess for Wang robot testing surface)
data_filenames = [r'\Time_no_pipe_0.7f.csv', r'\FullFSR.xlsx']
res_folder = r'\Friction Tests on Flat Ground 20e8'

cols = [range(8), range(9, 16), range(17, 23), range(24, 30)]
flattened_list = [item for r in cols for item in r]
data1 = np.loadtxt(work_dir + results + res_folder + data_filenames[0], delimiter=',', skiprows=1, usecols=flattened_list)
df = pd.read_excel(work_dir + data_filenames[1], sheet_name='Sheet1')
data2 = df.to_numpy()

Nseg = 6
color_mat = cm.rainbow(np.linspace(0, 1, Nseg))
fig = plt.figure(figsize = (12,7))
Segment = 'Segment '
print('Simulated Robot: ')
x1 = data1[:,0]
for j in range(1, Nseg+1):
    len_data = data1[:,14+j]
    print(Segment+str(j)+ " length change is", np.max(np.max(data1[10000:np.size(data1[:,0])-5000,14+j]))-np.min(np.min(data1[10000:np.size(data1[:,0])-5000,14+j])))
    ax = plt.subplot2grid((Nseg*2, 2), (2*(j-1), 1), rowspan = 2)
    ax.plot(x1[:17000], len_data[:17000], color = color_mat[j-1,:])
    ax.set_ylim(bottom = 0.055, top = 0.17)
    ax.set_ylabel('l (m)', fontsize = 12, fontname="Arial")
    ax.set_title(Segment + str(j), fontsize = 14, fontname="Arial", fontweight="bold")
ax.set_xlabel('Time (ms)', fontsize = 12, fontname="Arial")

Nseg_r = 4
print('Physical Robot: ')
x2 = data2[:,0]
x2 = x2-x2[0]
for j in range(1, Nseg_r+1):
    len_data_l = data2[:,(2*j)-1]/1000
    len_data_r = data2[:,(2*j)]/1000
    # print(Segment+str(j)+ " left length change is", np.max(np.max(len_data_l[13000:np.size(len_data_l)-5000]))-np.min(np.min(len_data_l[13000:np.size(len_data_l)-5000])))
    # print(Segment+str(j)+ " right length change is", np.max(np.max(len_data_r[13000:np.size(len_data_r)-5000]))-np.min(np.min(len_data_r[13000:np.size(len_data_r)-5000])))
    left_range = np.max(np.max(len_data_l[13000:np.size(len_data_l)-5000]))-np.min(np.min(len_data_l[13000:np.size(len_data_l)-5000]))
    right_range = np.max(np.max(len_data_r[13000:np.size(len_data_r)-5000]))-np.min(np.min(len_data_r[13000:np.size(len_data_r)-5000]))
    print(Segment+str(j)+ " length change is",np.mean([left_range, right_range]))
    
    ax = plt.subplot2grid((Nseg*2, 2), (2*(j-1), 0), rowspan = 2)
    ax.plot(x2, len_data_l, color = color_mat[j-1,:])
    ax.plot(x2, len_data_r, color = color_mat[j-1,:], linestyle='--')
    ax.set_ylim(bottom = 0.055, top = 0.17)
    ax.set_ylabel('l (m)', fontsize = 12, fontname="Arial")
    ax.set_title(Segment + str(j), fontsize = 14, fontname="Arial", fontweight="bold")
ax.set_xlabel('Time (ms)', fontsize = 12, fontname="Arial")

#Include image of the robot in the bottom left
image = mpimg.imread(work_dir + results + r"\Contraction_image.png")
ax = plt.subplot2grid((Nseg*2, 2), (8, 0), rowspan = 4)
ax.imshow(image)
ax.axis('off')

fig.tight_layout(pad=0.5) 
plt.savefig("Segment_Elongation_Comp.png", format="png")
plt.show()




########## Average Speed vs. Friction test over flat ground (20e8 stiffness)
data_filenames = [r'\Time_no_pipe_0.0f.csv', r'\Time_no_pipe_0.01f.csv', r'\Time_no_pipe_0.1f.csv', r'\Time_no_pipe_0.2f.csv', r'\Time_no_pipe_0.3f.csv', r'\Time_no_pipe_0.4f.csv', r'\Time_no_pipe_0.5f.csv', r'\Time_no_pipe_0.6f.csv', r'\Time_no_pipe_0.7f.csv', r'\Time_no_pipe_0.8f.csv', r'\Time_no_pipe_0.9f.csv', r'\Time_no_pipe_1.0f.csv']
res_folder = r'\Friction Tests on Flat Ground 20e8'

cols = [range(8), range(9, 16), range(17, 23), range(24, 30)]
flattened_list = [item for r in cols for item in r]
# data1 = np.loadtxt(work_dir + results + res_folder + data_filenames[0], delimiter=',', skiprows=1, usecols=flattened_list)
data2 = np.loadtxt(work_dir + results + res_folder + data_filenames[1], delimiter=',', skiprows=1, usecols=flattened_list)
data3 = np.loadtxt(work_dir + results + res_folder + data_filenames[2], delimiter=',', skiprows=1, usecols=flattened_list)
data4 = np.loadtxt(work_dir + results + res_folder + data_filenames[3], delimiter=',', skiprows=1, usecols=flattened_list)
data5 = np.loadtxt(work_dir + results + res_folder + data_filenames[4], delimiter=',', skiprows=1, usecols=flattened_list)
data6 = np.loadtxt(work_dir + results + res_folder + data_filenames[5], delimiter=',', skiprows=1, usecols=flattened_list)
data7 = np.loadtxt(work_dir + results + res_folder + data_filenames[6], delimiter=',', skiprows=1, usecols=flattened_list)
data8 = np.loadtxt(work_dir + results + res_folder + data_filenames[7], delimiter=',', skiprows=1, usecols=flattened_list)
data9 = np.loadtxt(work_dir + results + res_folder + data_filenames[8], delimiter=',', skiprows=1, usecols=flattened_list)
data10 = np.loadtxt(work_dir + results + res_folder + data_filenames[9], delimiter=',', skiprows=1, usecols=flattened_list)
data11 = np.loadtxt(work_dir + results + res_folder + data_filenames[10], delimiter=',', skiprows=1, usecols=flattened_list)
data12 = np.loadtxt(work_dir + results + res_folder + data_filenames[11], delimiter=',', skiprows=1, usecols=flattened_list)

data_mat = np.dstack((data2, data3, data4, data5, data6, data7, data8, data9, data10, data11, data12))

color_mat = cm.rainbow(np.linspace(0, 1, data_mat.shape[2]))

int_vec = np.zeros(data_mat.shape[2])
slope_vec = np.zeros(data_mat.shape[2])
for j in range(data_mat.shape[2]):
    # Plot distance traveled vs. time over flat ground for various frictions
    # plt.plot(data_mat[:,0,j], data_mat[:,7,j])          # COM
    plt.plot(data_mat[:,0,j], data_mat[:,1,j], color = color_mat[j,:])          # Segment 1

    # Average speed calculations (ignoring stoppage at the end)
    if data_mat[data_mat.shape[0]-1,1,j] < 0:
        end_index = np.argmin(data_mat[:,1,j])
    else:
        end_index = np.argmax(data_mat[:,1,j])

    popt, pcov = curve_fit(lin_func, data_mat[:end_index,0,j], data_mat[:end_index,1,j])
    int_vec[j] = popt[0]
    slope_vec[j] = popt[1]

plt.ylabel('Distance Traveled (m)', fontsize = 12, fontname="Arial")
plt.xlabel('Time (ms)', fontsize = 12, fontname="Arial")
plt.legend(['0.01', '0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9', '1.0'])
# plt.savefig("Flat_surface_friction_test.png", format="png")
plt.show()

# Plot average spped vs. friction over flat ground
frictions = [0.01, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
plt.plot(frictions, slope_vec*1000)
plt.xlabel('Friction Coefficient', fontsize = 12, fontname="Arial")
plt.ylabel('Average Speed (m/s)', fontsize = 12, fontname="Arial")
# plt.savefig("Avg_Speed_vs_Friction_20e8.png", format="png")
plt.show()

# Example plot to show line-fitting used to determine average speed (slope of line)
test_num = 2
plt.plot(data_mat[:,0,test_num], data_mat[:,1,test_num])
plt.plot(data_mat[:,0,test_num], int_vec[test_num]+data_mat[:,0,test_num]*slope_vec[test_num])
plt.ylabel('Distance Traveled (m)', fontsize = 12, fontname="Arial")
plt.xlabel('Time (ms)', fontsize = 12, fontname="Arial")
plt.show()




########## Speed vs. Friction test in a 90 degree pipe (0.5m radius of curvature pipe, 20e8 stiffness)
data_filenames = [r'\Time_90deg_0.5r_0.1f_thin.csv', r'\Time_90deg_0.5r_0.2f_thin.csv', r'\Time_90deg_0.5r_0.3f_thin.csv', r'\Time_90deg_0.5r_0.35f_thin.csv', r'\Time_90deg_0.5r_0.4f_thin.csv', r'\Time_90deg_0.5r_0.5f_thin.csv', r'\Time_90deg_0.5r_0.6f_thin.csv', r'\Time_90deg_0.5r_0.7f_thin.csv', r'\Time_90deg_0.5r_0.8f_thin.csv', r'\Time_90deg_0.5r_0.9f_thin.csv']
res_folder = r'\Friction Tests in 90deg Pipe'

cols = [range(8), range(9, 16), range(17, 23), range(24, 30)]
flattened_list = [item for r in cols for item in r]
data1 = np.loadtxt(work_dir + results + res_folder + data_filenames[0], delimiter=',', skiprows=1, usecols=flattened_list)
data2 = np.loadtxt(work_dir + results + res_folder + data_filenames[1], delimiter=',', skiprows=1, usecols=flattened_list)
data3 = np.loadtxt(work_dir + results + res_folder + data_filenames[2], delimiter=',', skiprows=1, usecols=flattened_list)
data4 = np.loadtxt(work_dir + results + res_folder + data_filenames[3], delimiter=',', skiprows=1, usecols=flattened_list)
data5 = np.loadtxt(work_dir + results + res_folder + data_filenames[4], delimiter=',', skiprows=1, usecols=flattened_list)
data6 = np.loadtxt(work_dir + results + res_folder + data_filenames[5], delimiter=',', skiprows=1, usecols=flattened_list)
data7 = np.loadtxt(work_dir + results + res_folder + data_filenames[6], delimiter=',', skiprows=1, usecols=flattened_list)
data8 = np.loadtxt(work_dir + results + res_folder + data_filenames[7], delimiter=',', skiprows=1, usecols=flattened_list)
data9 = np.loadtxt(work_dir + results + res_folder + data_filenames[8], delimiter=',', skiprows=1, usecols=flattened_list)
data10 = np.loadtxt(work_dir + results + res_folder + data_filenames[9], delimiter=',', skiprows=1, usecols=flattened_list)

data_mat = np.dstack((data1, data2, data3, data4, data5, data6, data7, data8, data9, data10))

color_mat = cm.rainbow(np.linspace(0, 1, data_mat.shape[2]))

#### Path along pipe in the x-y plane for different frictions
for j in range(data_mat.shape[2]):
    # plt.plot(data_mat[:,7,j], data_mat[:,14,j])          # COM
    plt.plot(data_mat[:,1,j], data_mat[:,8,j], color = color_mat[j,:])          # Segment 1

plt.plot([0.59+0.0935, 0.91+0.0935],[0.5, 0.5], color = 'Gray', linestyle='dashed')       # add a line to show end of pipe (OR superimpose pipe on the plot)
plt.xlabel('Distance Traveled in X (m)', fontsize = 12, fontname="Arial")
plt.ylabel('Distance Traveled in Y (m)', fontsize = 12, fontname="Arial")
plt.legend(['0.1', '0.2', '0.3', '0.35', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9'])
# plt.savefig("90deg_0.5_pipe_friction_test.png", format="png")
plt.show()

#### Path along centerline of a 90 degree pipe bend
# (Will need to change conditional statements if reintroducing progress along l_0)
l_0 = 0.25+0.0935              # Length of straight section + distance of segment 1 from pipe end, WILL BE FURTHER if using COM (+0.374,instead of +0.0935)
rad_curv = 0.5
# s_end = l_0+rad_curv*np.pi/2          # 90 degree bend => phi = pi/2
s_end = rad_curv*np.pi/2

speed_vec = np.zeros(data_mat.shape[2])
for j in range(data_mat.shape[2]):
    start_check = 0
    end_check = 0
    s = np.zeros(data_mat.shape[0])
    for i in range(len(s)):
        x_m = data_mat[i,1,j]
        y_m = data_mat[i,8,j]
        if x_m <= l_0:
            # s[i] = x_m
            s[i] = 0
        elif x_m > l_0:
            phi = np.atan((x_m-l_0)/(rad_curv-y_m))
            # s[i] = l_0+phi*rad_curv
            s[i] = phi*rad_curv
        if y_m >= rad_curv:
            # s[i] = s_end+y_m-rad_curv
            s[i] = s_end+y_m-rad_curv

        # Average total speed thru pipe calculations
        if s[i] > 0 and start_check == 0:          
            start_t = data_mat[i,0,j]
            start_s = s[i]
            start_check = 1
        if s[i] >= s_end and end_check == 0:
            end_t = data_mat[i,0,j]
            end_s = s[i]
            end_check = 1
    if np.max(s) <= s_end:
        end_t = data_mat[np.argmax(s),0,j]
        end_s = s[np.argmax(s)]
    speed_vec[j] = (end_s-start_s)/(end_t-start_t)*1000         # *1000 since given in ms
    plt.plot(data_mat[:,0,j], s, color = color_mat[j,:])

plt.plot([0, np.size(s)], [s_end, s_end], color = "Gray", linestyle='dashed')
plt.xlabel('Time (ms)', fontsize = 12, fontname="Arial")
plt.ylabel('Distance Along Pipe (m)', fontsize = 12, fontname="Arial")
plt.legend(['0.1', '0.2', '0.3', '0.35', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9'])
plt.show()

#### Speed vs. Friction plot (Speed = dist/time average,  do a linear regression instead??????)
fric_vec = np.array([0.1, 0.2, 0.3, 0.35, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])
plt.plot(fric_vec, speed_vec)
plt.xlabel('Friction Coefficient', fontsize = 12, fontname="Arial")
plt.ylabel('Average Speed in Pipe (m/s)', fontsize = 12, fontname="Arial")
# plt.savefig("90deg_0.5r_20e8_speed_vs_friction.png", format="png")
plt.show()




########## Combined friction tests on flat ground and in 0.5m radius of curvature pipe
fig, ax1 = plt.subplots()
line1, = ax1.plot(frictions, slope_vec*1000, color = "Black", label="Flat Ground")
ax1.set_xlabel('Friction Coefficient', fontsize = 12, fontname="Arial")
ax1.set_ylabel('Average Speed on Ground (m/s)', fontsize = 12, fontname="Arial")
ax1.tick_params(axis='y', labelcolor="Black")
ax2 = ax1.twinx()
line2, = ax2.plot(fric_vec, speed_vec, color = "Red", label="0.5m curvature Pipe")
ax2.set_ylabel('Average Speed in Pipe (m/s)', fontsize = 12, fontname="Arial", color = "Red")
ax2.tick_params(axis='y', labelcolor="Red")
plt.legend([line1, line2],['Flat Ground', '0.5m curvature Pipe'], loc="lower right")
plt.savefig("Speed_vs_friction_combined.png", format="png", bbox_inches='tight')
plt.show()




########## Speed vs. Pipe Radii of Curvature (0.3 coefficient of friction, 20e8 stiffness)
# 100 second cutoff was implemented, any models that did not pass fully through the pipe had their speeds calculated using their maximum achieved distance
# data_filenames = [r'\Time_90deg_0.4r.csv', r'\Time_90deg_0.5r.csv', r'\Time_90deg_0.6r.csv', r'\Time_90deg_0.7r.csv', r'\Time_90deg_0.8r.csv', r'\Time_90deg_0.9r.csv']
data_filenames = [r'\Time_90deg_0.2r_thin.csv', r'\Time_90deg_0.3r_thin.csv', r'\Time_90deg_0.4r_thin.csv', r'\Time_90deg_0.5r_thin.csv', r'\Time_90deg_0.6r_thin.csv', r'\Time_90deg_0.7r_thin.csv', r'\Time_90deg_0.8r_thin.csv', r'\Time_90deg_0.9r_thin.csv']
res_folder = r'\Radius of Curvature Tests 0.3f'

cols = [range(8), range(9, 16), range(17, 23), range(24, 30)]
flattened_list = [item for r in cols for item in r]
data1 = np.loadtxt(work_dir + results + res_folder + data_filenames[0], delimiter=',', skiprows=1, usecols=flattened_list)
data2 = np.loadtxt(work_dir + results + res_folder + data_filenames[1], delimiter=',', skiprows=1, usecols=flattened_list)
data3 = np.loadtxt(work_dir + results + res_folder + data_filenames[2], delimiter=',', skiprows=1, usecols=flattened_list)
data4 = np.loadtxt(work_dir + results + res_folder + data_filenames[3], delimiter=',', skiprows=1, usecols=flattened_list)
data5 = np.loadtxt(work_dir + results + res_folder + data_filenames[4], delimiter=',', skiprows=1, usecols=flattened_list)
data6 = np.loadtxt(work_dir + results + res_folder + data_filenames[5], delimiter=',', skiprows=1, usecols=flattened_list)
data7 = np.loadtxt(work_dir + results + res_folder + data_filenames[6], delimiter=',', skiprows=1, usecols=flattened_list)
data8 = np.loadtxt(work_dir + results + res_folder + data_filenames[7], delimiter=',', skiprows=1, usecols=flattened_list)

data_mat = np.dstack((data1, data2, data3, data4, data5, data6, data7, data8))

color_mat = cm.rainbow(np.linspace(0, 1, data_mat.shape[2]))

#### Path along pipe in the x-y plane for different radii of curvature
pipe_rad = 0.16
rad_vec = np.array([0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])
l_0 = 0.25+0.0935              # Length of straight section + distance of segment 1 from pipe end, WILL BE FURTHER if using COM (+0.374,instead of +0.0935)
for j in range(data_mat.shape[2]):
    # plt.plot(data_mat[:,7,j], data_mat[:,14,j])          # COM
    plt.plot(data_mat[:,1,j], data_mat[:,8,j], color = color_mat[j,:])          # Segment 1
for j in range(data_mat.shape[2]):
    left_edge = l_0+rad_vec[j]-pipe_rad
    right_edge = l_0+rad_vec[j]+pipe_rad
    plt.plot([left_edge, right_edge],[rad_vec[j], rad_vec[j]], color = color_mat[j,:], linestyle='dashed')

plt.xlabel('Distance Traveled in X (m)', fontsize = 12, fontname="Arial")
plt.ylabel('Distance Traveled in Y (m)', fontsize = 12, fontname="Arial")
plt.legend(['0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9'])
# plt.savefig("90deg_pipe_radii_20e8_test.png", format="png")
plt.show()

#### Path along centerline of a 90 degree pipe bend
# (Will need to change conditional statements if reintroducing progress along l_0)
speed_vec = np.zeros(data_mat.shape[2])
s = np.zeros((data_mat.shape[0], data_mat.shape[2]))
s_end = rad_vec*np.pi/2
for j in range(data_mat.shape[2]):
    start_check = 0
    end_check = 0
    for i in range(data_mat.shape[0]):
        x_m = data_mat[i,1,j]
        y_m = data_mat[i,8,j]
        if x_m <= l_0:
            s[i,j] = 0
        elif x_m > l_0:
            phi = np.atan((x_m-l_0)/(rad_vec[j]-y_m))
            s[i,j] = phi*rad_vec[j]
        if y_m >= rad_vec[j]:
            s[i,j] = s_end[j]+y_m-rad_vec[j]

        # Average total speed thru pipe calculations
        if s[i,j] > 0 and start_check == 0:          
            start_t = data_mat[i,0,j]
            start_s = s[i,j]
            start_check = 1
        if s[i,j] >= s_end[j] and end_check == 0:
            end_t = data_mat[i,0,j]
            end_s = s[i,j]
            end_check = 1
    if np.max(s[:,j]) <= s_end[j]:
        end_t = data_mat[np.argmax(s[:,j]),0,j]
        end_s = s[np.argmax(s[:,j]),j]
    speed_vec[j] = (end_s-start_s)/(end_t-start_t)*1000         # *1000 since given in ms
    plt.plot(data_mat[:,0,j], s[:,j], color = color_mat[j,:])

for j in range(data_mat.shape[2]):
    plt.plot([0, len(s[:,j])], [s_end[j], s_end[j]], color = color_mat[j,:], linestyle='dashed')
plt.xlabel('Time (ms)', fontsize = 12, fontname="Arial")
plt.ylabel('Distance Along Pipe (m)', fontsize = 12, fontname="Arial")
plt.legend(['0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9'])
plt.show()

#### Speed vs. Radius of curvature plot (Speed = dist/time average,  do a linear regression instead??????)
plt.plot(rad_vec, speed_vec)
plt.xlabel('90 Degree Pipe Radius of Curvature (m)', fontsize = 12, fontname="Arial")
plt.ylabel('Average Speed in Pipe (m/s)', fontsize = 12, fontname="Arial")
# plt.savefig("90deg_0.3f_20e8_speed_vs_radii.png", format="png")
plt.show()

rad_vec_20e8 = rad_vec
speed_vec_20e8 = speed_vec




########## Speed vs. Pipe Radii of Curvature (0.3 coefficient of friction, 10e8 stiffness)
# 100 second cutoff was implemented, any models that did not pass fully through the pipe had their speeds calculated using their maximum achieved distance
data_filenames = [r'\Time_90deg_0.2r_thin_10e8.csv', r'\Time_90deg_0.3r_thin_10e8.csv', r'\Time_90deg_0.4r_thin_10e8.csv', r'\Time_90deg_0.5r_thin_10e8.csv', r'\Time_90deg_0.6r_thin_10e8.csv', r'\Time_90deg_0.7r_thin_10e8.csv', r'\Time_90deg_0.8r_thin_10e8.csv', r'\Time_90deg_0.9r_thin_10e8.csv']
res_folder = r'\Radius of Curvature Tests 0.3f 10e8'

cols = [range(8), range(9, 16), range(17, 23), range(24, 30)]
flattened_list = [item for r in cols for item in r]
data1 = np.loadtxt(work_dir + results + res_folder + data_filenames[0], delimiter=',', skiprows=1, usecols=flattened_list)
data2 = np.loadtxt(work_dir + results + res_folder + data_filenames[1], delimiter=',', skiprows=1, usecols=flattened_list)
data3 = np.loadtxt(work_dir + results + res_folder + data_filenames[2], delimiter=',', skiprows=1, usecols=flattened_list)
data4 = np.loadtxt(work_dir + results + res_folder + data_filenames[3], delimiter=',', skiprows=1, usecols=flattened_list)
data5 = np.loadtxt(work_dir + results + res_folder + data_filenames[4], delimiter=',', skiprows=1, usecols=flattened_list)
data6 = np.loadtxt(work_dir + results + res_folder + data_filenames[5], delimiter=',', skiprows=1, usecols=flattened_list)
data7 = np.loadtxt(work_dir + results + res_folder + data_filenames[6], delimiter=',', skiprows=1, usecols=flattened_list)
data8 = np.loadtxt(work_dir + results + res_folder + data_filenames[7], delimiter=',', skiprows=1, usecols=flattened_list)

data_mat = np.dstack((data1, data2, data3, data4, data5, data6, data7, data8))

color_mat = cm.rainbow(np.linspace(0, 1, data_mat.shape[2]))

#### Path along pipe in the x-y plane for different radii of curvature
pipe_rad = 0.16
rad_vec = np.array([0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])
l_0 = 0.25+0.0935              # Length of straight section + distance of segment 1 from pipe end, WILL BE FURTHER if using COM (+0.374,instead of +0.0935)
for j in range(data_mat.shape[2]):
    # plt.plot(data_mat[:,7,j], data_mat[:,14,j])          # COM
    plt.plot(data_mat[:,1,j], data_mat[:,8,j], color = color_mat[j,:])          # Segment 1
for j in range(data_mat.shape[2]):
    left_edge = l_0+rad_vec[j]-pipe_rad
    right_edge = l_0+rad_vec[j]+pipe_rad
    plt.plot([left_edge, right_edge],[rad_vec[j], rad_vec[j]], color = color_mat[j,:], linestyle='dashed')

plt.xlabel('Distance Traveled in X (m)', fontsize = 12, fontname="Arial")
plt.ylabel('Distance Traveled in Y (m)', fontsize = 12, fontname="Arial")
plt.legend(['0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9'])
# plt.savefig("90deg_pipe_radii_20e8_test.png", format="png")
plt.show()

#### Path along centerline of a 90 degree pipe bend
# (Will need to change conditional statements if reintroducing progress along l_0)
speed_vec = np.zeros(data_mat.shape[2])
s = np.zeros((data_mat.shape[0], data_mat.shape[2]))
s_end = rad_vec*np.pi/2
for j in range(data_mat.shape[2]):
    start_check = 0
    end_check = 0
    for i in range(data_mat.shape[0]):
        x_m = data_mat[i,1,j]
        y_m = data_mat[i,8,j]
        if x_m <= l_0:
            s[i,j] = 0
        elif x_m > l_0:
            phi = np.atan((x_m-l_0)/(rad_vec[j]-y_m))
            s[i,j] = phi*rad_vec[j]
        if y_m >= rad_vec[j]:
            s[i,j] = s_end[j]+y_m-rad_vec[j]

        # Average total speed thru pipe calculations
        if s[i,j] > 0 and start_check == 0:          
            start_t = data_mat[i,0,j]
            start_s = s[i,j]
            start_check = 1
        if s[i,j] >= s_end[j] and end_check == 0:
            end_t = data_mat[i,0,j]
            end_s = s[i,j]
            end_check = 1
    if np.max(s[:,j]) <= s_end[j]:
        end_t = data_mat[np.argmax(s[:,j]),0,j]
        end_s = s[np.argmax(s[:,j]),j]
    speed_vec[j] = (end_s-start_s)/(end_t-start_t)*1000         # *1000 since given in ms
    plt.plot(data_mat[:,0,j], s[:,j], color = color_mat[j,:])

for j in range(data_mat.shape[2]):
    plt.plot([0, len(s[:,j])], [s_end[j], s_end[j]], color = color_mat[j,:], linestyle='dashed')
plt.xlabel('Time (ms)', fontsize = 12, fontname="Arial")
plt.ylabel('Distance Along Pipe (m)', fontsize = 12, fontname="Arial")
plt.legend(['0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9'])
plt.show()

#### Speed vs. Radius of curvature plot (Speed = dist/time average,  do a linear regression instead??????)
plt.plot(rad_vec, speed_vec)
plt.xlabel('90 Degree Pipe Radius of Curvature (m)', fontsize = 12, fontname="Arial")
plt.ylabel('Average Speed in Pipe (m/s)', fontsize = 12, fontname="Arial")
# plt.savefig("90deg_0.3f_10e8_speed_vs_radii.png", format="png")
plt.show()

rad_vec_10e8 = rad_vec
speed_vec_10e8 = speed_vec    




########## Speed vs. Pipe Radii of Curvature (0.3 coefficient of friction, 3e8 stiffness)
# 100 second cutoff was implemented, any models that did not pass fully through the pipe had their speeds calculated using their maximum achieved distance
data_filenames = [r'\Time_90deg_0.2r_thin_3e8.csv', r'\Time_90deg_0.3r_thin_3e8.csv', r'\Time_90deg_0.4r_thin_3e8.csv', r'\Time_90deg_0.5r_thin_3e8.csv', r'\Time_90deg_0.6r_thin_3e8.csv', r'\Time_90deg_0.7r_thin_3e8.csv', r'\Time_90deg_0.8r_thin_3e8.csv', r'\Time_90deg_0.9r_thin_3e8.csv']
res_folder = r'\Radius of Curvature Tests 0.3f 3e8'

cols = [range(8), range(9, 16), range(17, 23), range(24, 30)]
flattened_list = [item for r in cols for item in r]
data1 = np.loadtxt(work_dir + results + res_folder + data_filenames[0], delimiter=',', skiprows=1, usecols=flattened_list)
data2 = np.loadtxt(work_dir + results + res_folder + data_filenames[1], delimiter=',', skiprows=1, usecols=flattened_list)
data3 = np.loadtxt(work_dir + results + res_folder + data_filenames[2], delimiter=',', skiprows=1, usecols=flattened_list)
data4 = np.loadtxt(work_dir + results + res_folder + data_filenames[3], delimiter=',', skiprows=1, usecols=flattened_list)
data5 = np.loadtxt(work_dir + results + res_folder + data_filenames[4], delimiter=',', skiprows=1, usecols=flattened_list)
data6 = np.loadtxt(work_dir + results + res_folder + data_filenames[5], delimiter=',', skiprows=1, usecols=flattened_list)
data7 = np.loadtxt(work_dir + results + res_folder + data_filenames[6], delimiter=',', skiprows=1, usecols=flattened_list)
data8 = np.loadtxt(work_dir + results + res_folder + data_filenames[7], delimiter=',', skiprows=1, usecols=flattened_list)

data_mat = np.dstack((data1, data2, data3, data4, data5, data6, data7, data8))

color_mat = cm.rainbow(np.linspace(0, 1, data_mat.shape[2]))

#### Path along pipe in the x-y plane for different radii of curvature
pipe_rad = 0.16
rad_vec = np.array([0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9])
l_0 = 0.25+0.0935              # Length of straight section + distance of segment 1 from pipe end, WILL BE FURTHER if using COM (+0.374,instead of +0.0935)
for j in range(data_mat.shape[2]):
    # plt.plot(data_mat[:,7,j], data_mat[:,14,j])          # COM
    plt.plot(data_mat[:,1,j], data_mat[:,8,j], color = color_mat[j,:])          # Segment 1
for j in range(data_mat.shape[2]):
    left_edge = l_0+rad_vec[j]-pipe_rad
    right_edge = l_0+rad_vec[j]+pipe_rad
    plt.plot([left_edge, right_edge],[rad_vec[j], rad_vec[j]], color = color_mat[j,:], linestyle='dashed')

plt.xlabel('Distance Traveled in X (m)', fontsize = 12, fontname="Arial")
plt.ylabel('Distance Traveled in Y (m)', fontsize = 12, fontname="Arial")
plt.legend(['0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9'])
# plt.savefig("90deg_pipe_radii_3e8_test.png", format="png")
plt.show()

#### Path along centerline of a 90 degree pipe bend
# (Will need to change conditional statements if reintroducing progress along l_0)
speed_vec = np.zeros(data_mat.shape[2])
s = np.zeros((data_mat.shape[0], data_mat.shape[2]))
s_end = rad_vec*np.pi/2
for j in range(data_mat.shape[2]):
    start_check = 0
    end_check = 0
    for i in range(data_mat.shape[0]):
        x_m = data_mat[i,1,j]
        y_m = data_mat[i,8,j]
        if x_m <= l_0:
            s[i,j] = 0
        elif x_m > l_0:
            phi = np.atan((x_m-l_0)/(rad_vec[j]-y_m))
            s[i,j] = phi*rad_vec[j]
        if y_m >= rad_vec[j]:
            s[i,j] = s_end[j]+y_m-rad_vec[j]

        # Average total speed thru pipe calculations
        if s[i,j] > 0 and start_check == 0:          
            start_t = data_mat[i,0,j]
            start_s = s[i,j]
            start_check = 1
        if s[i,j] >= s_end[j] and end_check == 0:
            end_t = data_mat[i,0,j]
            end_s = s[i,j]
            end_check = 1
    if np.max(s[:,j]) <= s_end[j]:
        end_t = data_mat[np.argmax(s[:,j]),0,j]
        end_s = s[np.argmax(s[:,j]),j]
    speed_vec[j] = (end_s-start_s)/(end_t-start_t)*1000         # *1000 since given in ms
    plt.plot(data_mat[:,0,j], s[:,j], color = color_mat[j,:])

for j in range(data_mat.shape[2]):
    plt.plot([0, len(s[:,j])], [s_end[j], s_end[j]], color = color_mat[j,:], linestyle='dashed')
plt.xlabel('Time (ms)', fontsize = 12, fontname="Arial")
plt.ylabel('Distance Along Pipe (m)', fontsize = 12, fontname="Arial")
plt.legend(['0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9'])
plt.show()

#### Speed vs. Radius of curvature plot (Speed = dist/time average,  do a linear regression instead??????)
plt.plot(rad_vec, speed_vec)
plt.xlabel('90 Degree Pipe Radius of Curvature (m)', fontsize = 12, fontname="Arial")
plt.ylabel('Average Speed in Pipe (m/s)', fontsize = 12, fontname="Arial")
# plt.savefig("90deg_0.3f_3e8_speed_vs_radii.png", format="png")
plt.show()

rad_vec_3e8 = rad_vec
speed_vec_3e8 = speed_vec 




########## Speed vs. Pipe Radii of Curvature Combined
data_filenames = [r'\Time_straight_pipe_thin_20e8.csv', r'\Time_straight_pipe_thin_10e8.csv', r'\Time_straight_pipe_thin_3e8.csv']

cols = [range(8), range(9, 16), range(17, 23), range(24, 30)]
flattened_list = [item for r in cols for item in r]
res_folder = r'\Radius of Curvature Tests 0.3f'
data1 = np.loadtxt(work_dir + results + res_folder + data_filenames[0], delimiter=',', skiprows=1, usecols=flattened_list)
res_folder = r'\Radius of Curvature Tests 0.3f 10e8'
data2 = np.loadtxt(work_dir + results + res_folder + data_filenames[1], delimiter=',', skiprows=1, usecols=flattened_list)
res_folder = r'\Radius of Curvature Tests 0.3f 3e8'
data3 = np.loadtxt(work_dir + results + res_folder + data_filenames[2], delimiter=',', skiprows=1, usecols=flattened_list)

data_mat = np.dstack((data1, data2, data3))

color_mat = ['Red', 'Green', 'Blue']

l_0 = 0.25+0.0935              # Using sane initial length as curved pipes before starting calculations -> Length of straight section + distance of segment 1 from pipe end, WILL BE FURTHER if using COM (+0.374,instead of +0.0935)
int_vec = np.zeros(data_mat.shape[2])
slope_vec = np.zeros(data_mat.shape[2])
x_m = np.column_stack((data_mat[:,1,0], data_mat[:,1,1], data_mat[:,1,2]))
t_m = np.column_stack((data_mat[:,0,0], data_mat[:,0,1], data_mat[:,0,2]))
for j in range(data_mat.shape[2]):
    start_check = 0
    # end_check = 0
    for i in range(data_mat.shape[0]):
        # find the start point
        if x_m[i,j] > l_0 and start_check == 0:
            # start_t = t_m[i,j]
            # start_x = x_m[i,j]
            start_index = i
            start_check = 1
    end_index = np.argmax(x_m[:,j])
    print(t_m[end_index,j])
    popt, pcov = curve_fit(lin_func, t_m[start_index:end_index,j], x_m[start_index:end_index,j])
    int_vec[j] = popt[0]
    slope_vec[j] = popt[1]

    # speed_vec[j] = (end_s-start_s)/(end_t-start_t)*1000
    plt.plot(t_m, x_m[:,j], color = color_mat[j])
    plt.plot(t_m, int_vec[j]+t_m*slope_vec[j], color = color_mat[j], linestyle = 'dashed')
plt.ylabel('Distance Traveled (m)', fontsize = 12, fontname="Arial")
plt.xlabel('Time (ms)', fontsize = 12, fontname="Arial")
plt.show()

slope_vec = slope_vec*1000

plt.plot(rad_vec_20e8, speed_vec_20e8, color = 'Red')
plt.plot(rad_vec_10e8, speed_vec_10e8, color = 'Green')
plt.plot(rad_vec_3e8, speed_vec_3e8, color = 'Blue')
for j in range(data_mat.shape[2]):
    plt.plot([0, 1], [slope_vec[j], slope_vec[j]], color = color_mat[j], linestyle = 'dashed')
plt.xlim(left=0.2)
plt.xlim(right=0.9)
plt.xlabel('90 Degree Pipe Radius of Curvature (m)', fontsize = 12, fontname="Arial")
plt.ylabel('Average Speed in Pipe (m/s)', fontsize = 12, fontname="Arial")
plt.legend(['20e8', '10e8', '3e8'])
plt.savefig("90deg_speed_vs_radii_combined.png", format="png")
plt.show()


















# # ########## Heatmap showing which stiffness configurations succeeded and failed for 90_deg pipe stiffness tests
# # data = {'0.4': [1, 0, 0],
# #         '0.5': [1, 0, 0],
# #         '0.6': [1, 1, 0],
# #         '0.7': [1, 1, 0],
# #         '0.8': [1, 1, 0],
# #         '0.9': [1, 1, 1],
# #         '1.0': [1, 1, 1],}
# # cats = ['Low Stiff', 'Norm Stiff', 'High Stiff']

# # df = pd.DataFrame(data, index=cats)
# # print(df)
# # plt.figure(figsize = (10,2.5))
# # sns.heatmap(df, annot=False, cmap='cool_r', cbar=False)
# # plt.savefig("Pipe_Traversal_Heatmap.png", format="png")
# # plt.show()



# ########## Frictionless test on flat ground for elongation comparison EXTRA MATERIAL NOT A FIGURE
# data_filenames = [r'\Time_no_pipe_0.0.csv']
# res_folder = r'\Friction Tests on Flat Ground'

# cols = [range(8), range(9, 16), range(17, 23), range(24, 30)]
# flattened_list = [item for r in cols for item in r]
# data1 = np.loadtxt(work_dir + results + res_folder + data_filenames[0], delimiter=',', skiprows=1, usecols=flattened_list)

# Nseg = 6
# color_mat = cm.rainbow(np.linspace(0, 1, Nseg))
# fig = plt.figure(figsize = (6,7))
# Segment = 'Segment '

# print('Simulated Robot: ')
# x1 = data1[:,0]
# for j in range(1, Nseg+1):
#     len_data = data1[:,14+j]
#     print(Segment+str(j)+ " length change is", np.max(np.max(data1[10000:np.size(data1[:,0])-5000,14+j]))-np.min(np.min(data1[10000:np.size(data1[:,0])-5000,14+j])))

#     ax = plt.subplot2grid((Nseg*2, 1), (2*(j-1), 0), rowspan = 2)
#     ax.plot(x1[:17000], len_data[:17000], color = color_mat[j-1,:])
#     ax.set_ylim(bottom = 0.055, top = 0.17)
#     ax.set_ylabel('l (m)', fontsize = 12, fontname="Arial")
#     ax.set_title(Segment + str(j), fontsize = 14, fontname="Arial", fontweight="bold")
# ax.set_xlabel('Time (ms)', fontsize = 12, fontname="Arial")

# fig.tight_layout(pad=0.5) 

# plt.savefig("Segment_Elongation_0.0.png", format="png")
# plt.show()