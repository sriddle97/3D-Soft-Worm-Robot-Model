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

# Movie Making Packages  (Use mediapy for Mujoco)
import matplotlib.animation as animation
import mediapy as media

# Excel file interaction
import pandas as pd
from openpyxl import load_workbook
import csv

################################### Read and plot data from excel file ############################################

# Automatically get work directory
work_dir = os.getcwd()
print("String format :", work_dir)


# ########## Recorded time to run sim vs perscribed friction coefficient (90 degree pipe, 60 second sim)
# friction = [0.01, 0.1, 0.2, 0.3, 0.35, 0.4, 0.5, 0.6, 0.7, 0.8]
# sim_time = np.array([8393, 8192, 7349, 7012, 6954, 6581, 6431, 6420, 6341, 6345])     # Divide by 60 to get real_time per 1 second of sim_time
# sim_time = sim_time/60
# plt.plot(friction, sim_time)
# plt.ylabel('Simulation Run Time (s)', fontsize = 12, fontname="Arial")
# plt.xlabel('Coefficient of Friction', fontsize = 12, fontname="Arial")
# plt.savefig("SimTime_vs_Friction.png", format="png")
# plt.show()



# ########## Load-frame and muscle contraction comparison
# # data_filenames = [r'\xml_test_2_8e8.csv', r'\Load_Frame_c.csv', r'\xml_test_2_3e8.csv']
# # data_filenames = [r'\Seg3_no_pipe_0.0f_2e8shear.csv', r'\Load_Frame_c.csv', r'\Seg3_no_pipe_0.0f.csv']
# # data_filenames = [r'\xml_test_2_8e8.csv', r'\Load_Frame_c.csv', r'\Seg3_no_pipe_0.0f.csv']
# data_filenames = [r'\Load_Frame_c.csv', r'\Compiled_Instron_164703.xlsx', r'\xml_test_2_3e8.csv', r'\Seg3_no_pipe_0.0f_mass.csv']
# tune_folder = r'\Tuning Data'

# cols1 = [range(3)]
# flattened_list1 = [item for r in cols1 for item in r]
# data1 = np.loadtxt(work_dir + tune_folder + data_filenames[0], delimiter=',', skiprows=0, usecols=flattened_list1)
# df = pd.read_excel(work_dir + tune_folder + data_filenames[1], sheet_name='Sheet1')
# data2 = df.to_numpy()
# cols3 = [range(8), range(9, 21), range(22, 28), range(29, 35), range(36, 42), range(43,45), range(46,52), range(53,56)]
# flattened_list3 = [item for r in cols3 for item in r]
# data3 = np.loadtxt(work_dir + tune_folder + data_filenames[2], delimiter=',', skiprows=1, usecols=flattened_list3)
# data4 = np.loadtxt(work_dir + data_filenames[3], delimiter=',', skiprows=1, usecols=flattened_list1)
# # data3 = np.loadtxt(work_dir + data_filenames[2], delimiter=',', skiprows=1, usecols=flattened_list1)
# # data1 = np.loadtxt(work_dir + data_filenames[0], delimiter=',', skiprows=1, usecols=flattened_list2)

# x1 = data1[0:3318,0]/(1000*3)        #to get into meters and convert to diameter (using hexagons, should have to divide by 3)
# y1 = data1[0:3318,1]
# x2 = data2[:,4]
# y2 = data2[:,5]
# x3 = data3[0:2001,48]
# x3 = -(x3-x3[0])      
# y3 = data3[0:2001,47]/2              # Test may need re-run, was done prior to tension equation fix ????????????
# x4 = data4[0:2851,2]
# x4 = -(x4-x4[0]) 
# y4 = data4[0:2851,1]
# # x4 = data4[0:3851,2]
# # x4 = -(x4-x4[0]) 
# # y4 = data4[0:3851,1]

# print('Max for Instron Loose: ', np.max(y1))
# print('Max for Instron Tightened: ', np.max(y2))
# print('Max for 3e8: ', np.max(y3))
# print('Max for 20e8: ', np.max(y4))

# plt.plot(x1,y1, color = "Black")
# plt.plot(x2,y2, color = "Purple", linestyle='dashed')
# plt.plot(x3,y3, color = "Blue")
# plt.plot(x4,y4, color = "Red")

# plt.ylabel('Actuator Tension (N)', fontsize = 12, fontname="Arial")
# plt.xlabel('Diameter Change (m)', fontsize = 12, fontname="Arial")
# # plt.ylim(bottom=-0.05)
# # plt.xlim(left=0)
# plt.legend(['Loose Joints', 'Tight Joints', 'Initial: 3e8', 'Corrected: 20e8'])
# # plt.savefig("Tension_v_Disp.png", format="png")
# # plt.savefig("Tension_v_Disp_trialrun.png", format="png")
# plt.show()




# ########## Contraction-Expansion Hysteresis comparison
# data_filenames = [r'\Load_Frame_c.csv', r'\Seg3_no_pipe_0.0f_updown.csv']
# tune_folder = r'\Tuning Data'

# cols1 = [range(3)]
# flattened_list1 = [item for r in cols1 for item in r]
# data1 = np.loadtxt(work_dir + tune_folder + data_filenames[0], delimiter=',', skiprows=0, usecols=flattened_list1)
# data2 = np.loadtxt(work_dir + tune_folder + data_filenames[1], delimiter=',', skiprows=1, usecols=flattened_list1)

# x1 = data1[:,0]/(1000*3)        #to get into meters and convert to diameter (using hexagon math, delta_diam = delta_s/3)
# y1 = data1[:,1]
# x2 = data2[:,2]
# x2 = -(x2-x2[0]) 
# y2 = data2[:,1]

# plt.plot(x1,y1, color = "Black")
# plt.plot(x2,y2, color = "Red")

# plt.ylabel('Actuator Tension (N)', fontsize = 12, fontname="Arial")
# plt.xlabel('Diameter Change (m)', fontsize = 12, fontname="Arial")
# plt.legend(['Instron', 'Corrected: 20e8'])
# plt.savefig("Tension_v_Disp_Hysteresis.png", format="png")
# plt.show()




# ########## Segment length recordings for Yifan data comparison (used 0.7 friction)
# data_filenames = [r'\Time_no_pipe_0.7.csv', r'\FullFSR.xlsx']
# # data_filenames = [r'\Time_no_pipe_0.7.csv']
# res_folder = r'\Friction Tests on Flat Ground'

# cols = [range(8), range(9, 16), range(17, 23), range(24, 30)]
# flattened_list = [item for r in cols for item in r]
# data1 = np.loadtxt(work_dir + res_folder + data_filenames[0], delimiter=',', skiprows=1, usecols=flattened_list)
# df = pd.read_excel(work_dir + data_filenames[1], sheet_name='Sheet1')
# data2 = df.to_numpy()

# Nseg = 6
# color_mat = cm.rainbow(np.linspace(0, 1, Nseg))
# fig = plt.figure(figsize = (12,7))
# Segment = 'Segment '

# print('Simulated Robot: ')
# x1 = data1[:,0]
# for j in range(1, Nseg+1):
#     len_data = data1[:,14+j]
#     print(Segment+str(j)+ " length change is", np.max(np.max(data1[10000:np.size(data1[:,0])-5000,14+j]))-np.min(np.min(data1[10000:np.size(data1[:,0])-5000,14+j])))

#     ax = plt.subplot2grid((Nseg*2, 2), (2*(j-1), 1), rowspan = 2)
#     ax.plot(x1[:17000], len_data[:17000], color = color_mat[j-1,:])
#     ax.set_ylim(bottom = 0.055, top = 0.17)
#     ax.set_ylabel('l (m)', fontsize = 12, fontname="Arial")
#     ax.set_title(Segment + str(j), fontsize = 14, fontname="Arial", fontweight="bold")
# ax.set_xlabel('Time (ms)', fontsize = 12, fontname="Arial")

# Nseg_r = 4
# print('Physical Robot: ')
# x2 = data2[:,0]
# x2 = x2-x2[0]
# for j in range(1, Nseg_r+1):
#     len_data_l = data2[:,(2*j)-1]/1000
#     len_data_r = data2[:,(2*j)]/1000
#     # print(Segment+str(j)+ " left length change is", np.max(np.max(len_data_l[13000:np.size(len_data_l)-5000]))-np.min(np.min(len_data_l[13000:np.size(len_data_l)-5000])))
#     # print(Segment+str(j)+ " right length change is", np.max(np.max(len_data_r[13000:np.size(len_data_r)-5000]))-np.min(np.min(len_data_r[13000:np.size(len_data_r)-5000])))
#     left_range = np.max(np.max(len_data_l[13000:np.size(len_data_l)-5000]))-np.min(np.min(len_data_l[13000:np.size(len_data_l)-5000]))
#     right_range = np.max(np.max(len_data_r[13000:np.size(len_data_r)-5000]))-np.min(np.min(len_data_r[13000:np.size(len_data_r)-5000]))
#     print(Segment+str(j)+ " length change is",np.mean([left_range, right_range]))
    
#     ax = plt.subplot2grid((Nseg*2, 2), (3*(j-1), 0), rowspan = 3)
#     ax.plot(x2, len_data_l, color = color_mat[j-1,:])
#     ax.plot(x2, len_data_r, color = color_mat[j-1,:], linestyle='--')
#     ax.set_ylim(bottom = 0.055, top = 0.17)
#     ax.set_ylabel('l (m)', fontsize = 12, fontname="Arial")
#     ax.set_title(Segment + str(j), fontsize = 14, fontname="Arial", fontweight="bold")
# ax.set_xlabel('Time (ms)', fontsize = 12, fontname="Arial")

# fig.tight_layout(pad=0.5) 
# plt.savefig("Segment_Elongation_Comp.png", format="png")
# plt.show()



########## Distance traveled over flat ground for various frictions
data_filenames = [r'\Time_no_pipe_0.0f.csv', r'\Time_no_pipe_0.01f.csv', r'\Time_no_pipe_0.1f.csv', r'\Time_no_pipe_0.2f.csv', r'\Time_no_pipe_0.3f.csv', r'\Time_no_pipe_0.4f.csv', r'\Time_no_pipe_0.5f.csv', r'\Time_no_pipe_0.6f.csv', r'\Time_no_pipe_0.7f.csv', r'\Time_no_pipe_0.8f.csv', r'\Time_no_pipe_0.9f.csv', r'\Time_no_pipe_1.0f.csv']
# res_folder = r'\Friction Tests on Flat Ground'
res_folder = r''

cols = [range(8), range(9, 16), range(17, 23), range(24, 30)]
flattened_list = [item for r in cols for item in r]
# data1 = np.loadtxt(work_dir + res_folder + data_filenames[0], delimiter=',', skiprows=1, usecols=flattened_list)
data2 = np.loadtxt(work_dir + res_folder + data_filenames[1], delimiter=',', skiprows=1, usecols=flattened_list)
data3 = np.loadtxt(work_dir + res_folder + data_filenames[2], delimiter=',', skiprows=1, usecols=flattened_list)
data4 = np.loadtxt(work_dir + res_folder + data_filenames[3], delimiter=',', skiprows=1, usecols=flattened_list)
data5 = np.loadtxt(work_dir + res_folder + data_filenames[4], delimiter=',', skiprows=1, usecols=flattened_list)
data6 = np.loadtxt(work_dir + res_folder + data_filenames[5], delimiter=',', skiprows=1, usecols=flattened_list)
data7 = np.loadtxt(work_dir + res_folder + data_filenames[6], delimiter=',', skiprows=1, usecols=flattened_list)
data8 = np.loadtxt(work_dir + res_folder + data_filenames[7], delimiter=',', skiprows=1, usecols=flattened_list)
data9 = np.loadtxt(work_dir + res_folder + data_filenames[8], delimiter=',', skiprows=1, usecols=flattened_list)
data10 = np.loadtxt(work_dir + res_folder + data_filenames[9], delimiter=',', skiprows=1, usecols=flattened_list)
data11 = np.loadtxt(work_dir + res_folder + data_filenames[10], delimiter=',', skiprows=1, usecols=flattened_list)
data12 = np.loadtxt(work_dir + res_folder + data_filenames[11], delimiter=',', skiprows=1, usecols=flattened_list)

# x1 = data1[:,0]
# y1 = data1[:,7]
x2 = data2[:,0]
y2 = data2[:,7]
x3 = data3[:,0]
y3 = data3[:,7]
x4 = data4[:,0]
y4 = data4[:,7]
x5 = data5[:,0]
y5 = data5[:,7]
x6 = data6[:,0]
y6 = data6[:,7]
x7 = data7[:,0]
y7 = data7[:,7]
x8 = data8[:,0]
y8 = data8[:,7]
x9 = data9[:,0]
y9 = data9[:,7]
x10 = data10[:,0]
y10 = data10[:,7]
x11 = data11[:,0]
y11 = data11[:,7]
x12 = data12[:,0]
y12 = data12[:,7]
Nseg = 6

# plt.plot(x1,y1)
plt.plot(x2,y2)
plt.plot(x3,y3)
plt.plot(x4,y4)
plt.plot(x5,y5)
plt.plot(x6,y6)
plt.plot(x7,y7)
plt.plot(x8,y8)
plt.plot(x9,y9)
plt.plot(x10,y10)
plt.plot(x11,y11)
plt.plot(x12,y12)
# plt.plot(x12[0:60000],y12[0:60000])
plt.ylabel('Distance Traveled (m)', fontsize = 12, fontname="Arial")
plt.xlabel('Time (ms)', fontsize = 12, fontname="Arial")
plt.legend(['0.01', '0.1', '0.2', '0.3', '0.4', '0.5', '0.6', '0.7', '0.8', '0.9', '1.0'])
# plt.savefig("Flat_surface_friction_test.png", format="png")
plt.show()

########## Average speed vs friction (TRY SLOPE WITHOUT AN INTERCEPT TOO TO CONSTRAIN IT TO START AT 0,0)??????????????????????????????
def lin_func(x, intercept, slope):
    y = intercept + slope * x
    return y
def lin_func0(x, slope):
    y = 0 + slope * x
    return y
# popt, pcov = curve_fit(lin_func, x1, y1)
# int1 = popt[0]
# slope1 = popt[1]

popt, pcov = curve_fit(lin_func, x2, y2)
int2 = popt[0]
slope2 = popt[1]

popt, pcov = curve_fit(lin_func, x3, y3)
int3 = popt[0]
slope3 = popt[1]
popt, pcov = curve_fit(lin_func, x4, y4)
int4 = popt[0]
slope4 = popt[1]
popt, pcov = curve_fit(lin_func, x5, y5)
int5 = popt[0]
slope5 = popt[1]
popt, pcov = curve_fit(lin_func, x6, y6)
int6 = popt[0]
slope6 = popt[1]
popt, pcov = curve_fit(lin_func, x7, y7)
int7 = popt[0]
slope7 = popt[1]
popt, pcov = curve_fit(lin_func, x8, y8)
int8 = popt[0]
slope8 = popt[1]
popt, pcov = curve_fit(lin_func, x9, y9)
int9 = popt[0]
slope9 = popt[1]
popt, pcov = curve_fit(lin_func, x10, y10)
int10 = popt[0]
slope10 = popt[1]
popt, pcov = curve_fit(lin_func, x11, y11)
int11 = popt[0]
slope11 = popt[1]
popt, pcov = curve_fit(lin_func, x12, y12)
int12 = popt[0]
slope12 = popt[1]

# # Mini plot to show line-fitting used to determine average speed (slope of line)
# plt.plot(x2, y2)
# plt.plot(x2, int2+x2*slope2)
# plt.ylabel('Distance Traveled (m)', fontsize = 12, fontname="Arial")
# plt.xlabel('Time (ms)', fontsize = 12, fontname="Arial")
# plt.show()

# slopes = [slope1, slope2, slope3, slope4, slope5, slope6]
# frictions = [0.0, 0.01, 0.1, 0.3, 0.6, 1.0]
slopes = np.array([slope2, slope3, slope4, slope5, slope6, slope7, slope8, slope9, slope10, slope11, slope12])*1000      #get the speeds in m/s rather than m/ms
frictions = [0.01, 0.1, 0.2, 0.3, 0.4, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0]
plt.plot(frictions, slopes)
plt.xlabel('Friction Coefficient', fontsize = 12, fontname="Arial")
plt.ylabel('Average Speed (m/s)', fontsize = 12, fontname="Arial")
# plt.savefig("Avg_Speed_vs_Friction.png", format="png")
plt.show()



# ########## Path along pipe in the x-y plane for different frictions (0.6m radius of curvature pipe, Yifan robot stiffness)
# data_filenames = [r'\Time_90deg_0.6r_0.01f.csv', r'\Time_90deg_0.6r_0.1f.csv', r'\Time_90deg_0.6r_0.2f.csv', r'\Time_90deg_0.6r_0.3f.csv', r'\Time_90deg_0.6r_0.35f.csv', r'\Time_90deg_0.6r_0.4f.csv', r'\Time_90deg_0.6r_0.5f.csv', r'\Time_90deg_0.6r_0.6f.csv', r'\Time_90deg_0.6r_0.7f.csv', r'\Time_90deg_0.6r_0.8f.csv']
# res_folder = r'\Friction Tests in 90deg Pipe'

# cols = [range(8), range(9, 16), range(17, 23), range(24, 30)]
# flattened_list = [item for r in cols for item in r]
# data1 = np.loadtxt(work_dir + res_folder + data_filenames[0], delimiter=',', skiprows=1, usecols=flattened_list)
# data2 = np.loadtxt(work_dir + res_folder + data_filenames[1], delimiter=',', skiprows=1, usecols=flattened_list)
# data3 = np.loadtxt(work_dir + res_folder + data_filenames[2], delimiter=',', skiprows=1, usecols=flattened_list)
# data4 = np.loadtxt(work_dir + res_folder + data_filenames[3], delimiter=',', skiprows=1, usecols=flattened_list)
# data5 = np.loadtxt(work_dir + res_folder + data_filenames[4], delimiter=',', skiprows=1, usecols=flattened_list)
# data6 = np.loadtxt(work_dir + res_folder + data_filenames[5], delimiter=',', skiprows=1, usecols=flattened_list)
# data7 = np.loadtxt(work_dir + res_folder + data_filenames[6], delimiter=',', skiprows=1, usecols=flattened_list)
# data8 = np.loadtxt(work_dir + res_folder + data_filenames[7], delimiter=',', skiprows=1, usecols=flattened_list)
# data9 = np.loadtxt(work_dir + res_folder + data_filenames[8], delimiter=',', skiprows=1, usecols=flattened_list)
# data10 = np.loadtxt(work_dir + res_folder + data_filenames[9], delimiter=',', skiprows=1, usecols=flattened_list)

# x1 = data1[:,7]
# y1 = data1[:,14]
# x2 = data2[:,7]
# y2 = data2[:,14]
# x3 = data3[:,7]
# y3 = data3[:,14]
# x4 = data4[:,7]
# y4 = data4[:,14]
# x5 = data5[:,7]
# y5 = data5[:,14]
# x6 = data6[:,7]
# y6 = data6[:,14]
# x7 = data7[:,7]
# y7 = data7[:,14]
# x8 = data8[:,7]
# y8 = data8[:,14]
# x9 = data9[:,7]
# y9 = data9[:,14]
# x10 = data10[:,7]
# y10 = data10[:,14]
# # plt.plot(x1,y1)               # Friction too low, couldn't make it into pipe
# plt.plot(x2,y2)
# plt.plot(x3,y3)
# plt.plot(x4,y4)
# plt.plot(x5,y5)
# plt.plot(x6,y6)
# plt.plot(x7,y7)
# plt.plot(x8,y8)
# plt.plot(x9,y9)
# plt.plot(x10,y10)
# plt.xlabel('Distance Traveled in X (m)', fontsize = 12, fontname="Arial")
# plt.ylabel('Distance Traveled in Y (m)', fontsize = 12, fontname="Arial")
# # plt.legend(['0.01', '0.1', '0.2', '0.3', '0.35', '0.4', '0.5', '0.6', '0.7', '0.8'])
# plt.legend(['0.1', '0.2', '0.3', '0.35', '0.4', '0.5', '0.6', '0.7', '0.8'])
# plt.savefig("90deg_0.6_pipe_friction_test.png", format="png")
# plt.show()







# ########## STILL NEED TO FIGURE OUT HOW TO CALCULATE SPEED THROUGH THE CURVED PIPE







# ########## Path along pipe in the x-y plane for different pipe radii (0.35 coefficient of friction, Yifan robot stiffness: 8e8)
# data_filenames = [r'\Time_90deg_0.4r.csv', r'\Time_90deg_0.5r.csv', r'\Time_90deg_0.6r.csv', r'\Time_90deg_0.7r.csv', r'\Time_90deg_0.8r.csv', r'\Time_90deg_0.9r.csv']
# res_folder = r'\Radius of Curvature Tests 0.35f'

# cols = [range(8), range(9, 16), range(17, 23), range(24, 30)]
# flattened_list = [item for r in cols for item in r]
# data1 = np.loadtxt(work_dir + res_folder + data_filenames[0], delimiter=',', skiprows=1, usecols=flattened_list)
# data2 = np.loadtxt(work_dir + res_folder + data_filenames[1], delimiter=',', skiprows=1, usecols=flattened_list)
# data3 = np.loadtxt(work_dir + res_folder + data_filenames[2], delimiter=',', skiprows=1, usecols=flattened_list)
# data4 = np.loadtxt(work_dir + res_folder + data_filenames[3], delimiter=',', skiprows=1, usecols=flattened_list)
# data5 = np.loadtxt(work_dir + res_folder + data_filenames[4], delimiter=',', skiprows=1, usecols=flattened_list)
# data6 = np.loadtxt(work_dir + res_folder + data_filenames[5], delimiter=',', skiprows=1, usecols=flattened_list)

# x1 = data1[:,7]
# y1 = data1[:,14]
# x2 = data2[:,7]
# y2 = data2[:,14]
# x3 = data3[:,7]
# y3 = data3[:,14]
# x4 = data4[:,7]
# y4 = data4[:,14]
# x5 = data5[:,7]
# y5 = data5[:,14]
# x6 = data6[:,7]
# y6 = data6[:,14]

# # Datasets truncated to 100s simulated time
# plt.plot(x1,y1)
# plt.plot(x2,y2)

# plt.plot(x3[0:np.size(x4)],y3[0:np.size(x4)])
# plt.plot(x4,y4)
# # plt.plot(x5,y5)
# # plt.plot(x6,y6)
# plt.plot(x5[0:np.size(x1)],y5[0:np.size(x1)])
# plt.plot(x6[0:np.size(x1)],y6[0:np.size(x1)])
# plt.xlabel('Distance Traveled in X (m)', fontsize = 12, fontname="Arial")
# plt.ylabel('Distance Traveled in Y (m)', fontsize = 12, fontname="Arial")
# plt.legend(['0.4', '0.5', '0.6', '0.7', '0.8', '0.9'])
# plt.savefig("90deg_pipe_radius_test_0.35f.png", format="png")
# plt.show()



# ########## Path along pipe in the x-y plane for different pipe radii (0.35 coefficient of friction, 8e7 stiffness)
# data_filenames = [r'\Time_90deg_0.4r_LowStiff.csv', r'\Time_90deg_0.5r_LowStiff.csv', r'\Time_90deg_0.6r_LowStiff.csv', r'\Time_90deg_0.7r_LowStiff.csv']
# res_folder = r'\Radius of Curvature Tests 0.35f 8e7 stiff'

# cols = [range(8), range(9, 16), range(17, 23), range(24, 30)]
# flattened_list = [item for r in cols for item in r]
# data1 = np.loadtxt(work_dir + res_folder + data_filenames[0], delimiter=',', skiprows=1, usecols=flattened_list)
# data2 = np.loadtxt(work_dir + res_folder + data_filenames[1], delimiter=',', skiprows=1, usecols=flattened_list)
# data3 = np.loadtxt(work_dir + res_folder + data_filenames[2], delimiter=',', skiprows=1, usecols=flattened_list)
# data4 = np.loadtxt(work_dir + res_folder + data_filenames[3], delimiter=',', skiprows=1, usecols=flattened_list)

# x1 = data1[:,7]
# y1 = data1[:,14]
# x2 = data2[:,7]
# y2 = data2[:,14]
# x3 = data3[:,7]
# y3 = data3[:,14]
# x4 = data4[:,7]
# y4 = data4[:,14]

# # Datasets truncated to 100s simulated time
# plt.plot(x1,y1)
# plt.plot(x2,y2)
# plt.plot(x3[0:np.size(x1)],y3[0:np.size(x1)])
# plt.plot(x4,y4)

# plt.xlabel('Distance Traveled in X (m)', fontsize = 12, fontname="Arial")
# plt.ylabel('Distance Traveled in Y (m)', fontsize = 12, fontname="Arial")
# plt.legend(['0.4', '0.5', '0.6', '0.7'])
# plt.savefig("90deg_pipe_radius_test_0.35f_LowStiff.png", format="png")
# plt.show()



# ########## Path along pipe in the x-y plane for different pipe radii (0.35 coefficient of friction, 4e9 stiffness)
# data_filenames = [r'\Time_90deg_0.8r_HighStiff.csv', r'\Time_90deg_0.9r_HighStiff.csv', r'\Time_90deg_1.0r_HighStiff.csv']
# res_folder = r'\Radius of Curvature Tests 0.35f 4e9 stiff'

# cols = [range(8), range(9, 16), range(17, 23), range(24, 30)]
# flattened_list = [item for r in cols for item in r]
# data1 = np.loadtxt(work_dir + res_folder + data_filenames[0], delimiter=',', skiprows=1, usecols=flattened_list)
# data2 = np.loadtxt(work_dir + res_folder + data_filenames[1], delimiter=',', skiprows=1, usecols=flattened_list)
# data3 = np.loadtxt(work_dir + res_folder + data_filenames[2], delimiter=',', skiprows=1, usecols=flattened_list)

# x1 = data1[:,7]
# y1 = data1[:,14]
# x2 = data2[:,7]
# y2 = data2[:,14]
# x3 = data3[:,7]
# y3 = data3[:,14]

# plt.plot(x1,y1)
# plt.plot(x2,y2)
# plt.plot(x3,y3)

# plt.xlabel('Distance Traveled in X (m)', fontsize = 12, fontname="Arial")
# plt.ylabel('Distance Traveled in Y (m)', fontsize = 12, fontname="Arial")
# plt.legend(['0.8', '0.9', '1.0'])
# plt.savefig("90deg_pipe_radius_test_0.35f_HighStiff.png", format="png")
# plt.show()



# ########## Heatmap showing which stiffness configurations succeeded and failed for 90_deg pipe stiffness tests
# data = {'0.4': [1, 0, 0],
#         '0.5': [1, 0, 0],
#         '0.6': [1, 1, 0],
#         '0.7': [1, 1, 0],
#         '0.8': [1, 1, 0],
#         '0.9': [1, 1, 1],
#         '1.0': [1, 1, 1],}
# cats = ['Low Stiff', 'Norm Stiff', 'High Stiff']

# df = pd.DataFrame(data, index=cats)
# print(df)
# plt.figure(figsize = (10,2.5))
# sns.heatmap(df, annot=False, cmap='cool_r', cbar=False)
# plt.savefig("Pipe_Traversal_Heatmap.png", format="png")
# plt.show()



# ########## Frictioless test on flat ground for elongation comparison EXTRA MATERIAL NOT A FIGURE
# data_filenames = [r'\Time_no_pipe_0.0.csv']
# res_folder = r'\Friction Tests on Flat Ground'

# cols = [range(8), range(9, 16), range(17, 23), range(24, 30)]
# flattened_list = [item for r in cols for item in r]
# data1 = np.loadtxt(work_dir + res_folder + data_filenames[0], delimiter=',', skiprows=1, usecols=flattened_list)

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