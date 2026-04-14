#### Calculating and Plotting Cost of Transport
#
# Author: Shane Riddle
#
# Last edited: 04/08/2026
#
# NOTES - We calculated the work component (mass*grav*dist) for Cost of 
#         Transport (COT) by taking the sum for individual segments, 
#         rather than tracking center of mass directly.
#       - Be sure to change the function variables to match your
#         experimental parameters (Nseg, mass, etc.).
#       - Change the data_filenames, results, cols, and data_mat elements
#         to match your csv file structures and orgnization. 
#########################################################################

########################### Import packages #############################

# Basic Utility and Plotting Packages
import numpy as np
import math
import matplotlib.pyplot as plt
from matplotlib.pyplot import cm
from mpl_toolkits.mplot3d import Axes3D
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

#### Cost of Transport Calculation
def Cost_T(data_matrix, styles, rad_vecs):
    # pipe_rad = 0.2                      # pipe cross section radius in m (NOT radius of curvature)
    Nseg = 6                            # number of segments
    mass = 1.981                        # robot mass in kg
    grav = 9.81                         # gravity in m/s^2
    length_0 = 0.25                     # length of straight section at the pipe entrance
    l_0 = np.zeros(Nseg)
    for q in range(Nseg):               # distance from tip to start of curve, adjusted for each segment
        l_0[q] = length_0+0.0935+q*0.1122

    speed_vec = np.zeros(data_matrix.shape[2])
    s = np.zeros((data_matrix.shape[0], Nseg, data_matrix.shape[2]))
    s_end = rad_vecs*np.pi/2

    Work = np.zeros(data_matrix.shape[2])
    Distance = np.zeros(data_matrix.shape[2])
    COT = np.zeros(data_matrix.shape[2])
    cut_time = np.zeros(data_matrix.shape[2])

    for j in range(data_matrix.shape[2]):
        if styles[j] == "bend":
            trig = 0
            x_m = data_matrix[:,1:Nseg+1,j]
            y_m = data_matrix[:,2+Nseg:2+2*Nseg,j]
            #### Mapping to path along centerline of a 90 degree pipe bend    
            for i in range(data_matrix.shape[0]):
                for q in range(Nseg):
                    if x_m[i,q] <= l_0[q]:              # + distance of segment from pipe end, WILL BE DIFFERENT if using COM (+0.374)
                        s[i,q,j] = x_m[i,q]
                    elif x_m[i,q] > l_0[q]:
                        phi = np.arctan((x_m[i,q]-l_0[q])/(rad_vecs[j]-y_m[i,q]))
                        s[i,q,j] = l_0[q]+phi*rad_vecs[j]
                    if y_m[i,q] >= rad_vecs[j]:
                        s[i,q,j] = l_0[q]+s_end[j]+y_m[i,q]-rad_vecs[j]
                if y_m[i,5] >= rad_vecs[j] and trig !=1:         # cut data off if/when last segment leaves pipe bend (?)
                    cut_time[j] = i
                    trig = 1
                elif trig != 1:
                    cut_time[j] = data_matrix.shape[0]-1
            # print(cut_time[j])

            denominator = 0
            for q in range(Nseg):
                # for i in range(1, data_matrix.shape[0]):
                for i in range(1, int(cut_time[j])):
                    # Work[j] = Work[j] + data_matrix[i,3+2*Nseg+q,j]*abs(data_matrix[i,3+4*Nseg+q,j]-data_matrix[i-1,3+4*Nseg+q,j])      # F_i*del_l
                    # Work[j] = Work[j]+0.5*data_matrix[i,3+2*Nseg+q,j]*max(abs(0.48-data_matrix[i-1,3+4*Nseg+q,j]), 0)      # F_i*del_l, del_l is from rest (0.48m), NOT time i-1 to i
                    Work[j] = Work[j]+0.5*data_matrix[i,3+2*Nseg+q,j]*max(abs(0.48-data_matrix[i-1,3+4*Nseg+q,j]), 0)+0.5*data_matrix[i,3+3*Nseg+q,j]*max(abs(0.48-data_matrix[i-1,3+5*Nseg+q,j]), 0)      # F_i*del_l, del_l is from rest (0.48m), NOT time i-1 to i

                denominator = denominator + mass/Nseg*grav*s[int(cut_time[j]),q,j]         # Add contribution of each segment individually since COM path hard to predict
                Distance[j] = Distance[j]+s[int(cut_time[j]),q,j]
                # print(s[int(cut_time[j]),q,j])                        # Distance traveled for each segment
            COT[j] = Work[j]/denominator
            Distance[j] = Distance[j]/Nseg          # Approximated distance traveled of COM using average of individual segments

        else:
            popt, pcov = curve_fit(lin_func, data_matrix[:,0,j], data_matrix[:,7,j])
            speed_vec[j] = popt[1]*1000             # 1000 gets it into units of m/s

            for i in range(1, data_matrix.shape[0]):
                for q in range(Nseg):
                    # Work[j] = Work[j]+data_matrix[i,3+2*Nseg+q,j]*abs(data_matrix[i,3+4*Nseg+q,j]-data_matrix[i-1,3+4*Nseg+q,j])      # F_i*del_l
                    # Work[j] = Work[j]+0.5*data_matrix[i,3+2*Nseg+q,j]*max(abs(0.48-data_matrix[i-1,3+4*Nseg+q,j]), 0)      # F_i*del_l, del_l is from rest (0.48m), NOT time i-1 to i
                    Work[j] = Work[j]+0.5*data_matrix[i,3+2*Nseg+q,j]*max(abs(0.48-data_matrix[i-1,3+4*Nseg+q,j]), 0)+0.5*data_matrix[i,3+3*Nseg+q,j]*max(abs(0.48-data_matrix[i-1,3+5*Nseg+q,j]), 0)      # F_i*del_l, del_l is from rest (0.48m), NOT time i-1 to i

            Distance[j] = data_matrix[data_matrix.shape[0]-1,7,j]-data_matrix[0,7,j]
            COT[j] = Work[j]/(mass*grav*Distance[j])

    print("Work is : ", np.round(Work, 2))
    print("Distance is : ", np.round(Distance, 2))
    print("COT is : ", np.round(COT, 2))
    print("Average speed is : ", np.round(speed_vec, 4))
    print("")
    return COT
#########################################################################

################## Read and plot data from excel files ##################

# Automatically get work directory
work_dir = os.getcwd()
print("String format :", work_dir)
# results = r'\Turning Results'
# Nseg = 6
rad_vec = np.array([0.0, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3])
style = ["straight", "bend", "bend", "bend", "bend", "bend", "bend", "bend", "bend", "bend"]
count = 0

########## Straight-line Algorithm Cost of Transport vs. Pipe Radii of Curvature
data_filenames = [r'\Time_sens_straight_pipe_norm.csv', r'\Time_sens_0.5r_norm_f0.3.csv', r'\Time_sens_0.6r_norm_f0.3.csv', r'\Time_sens_0.7r_norm_f0.3.csv', r'\Time_sens_0.8r_norm_f0.3.csv', r'\Time_sens_0.9r_norm_f0.3.csv', r'\Time_sens_1.0r_norm_f0.3.csv', r'\Time_sens_1.1r_norm_f0.3.csv', r'\Time_sens_1.2r_norm_f0.3.csv', r'\Time_sens_1.3r_norm_f0.3.csv']
results = r'\Sens Results'

cols = [range(8), range(9, 16), range(38, 44), range(45, 51), range(52, 58), range(59, 65)]
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
data10 = np.loadtxt(work_dir + results + data_filenames[9], delimiter=',', skiprows=1, usecols=flattened_list)

data_mat = np.dstack((data1, data2, data3, data4, data5, data6, data7, data8, data9, data10))
COT_straight = Cost_T(data_mat, style, rad_vec)
count = count+1




########## Turning Algorithm Cost of Transport vs. Pipe Radii of Curvature: 100% act diff
data_filenames = [r'\Time_sens_straight_pipe_norm.csv', r'\Time_sens_0.5r_manual0.0_f0.3.csv', r'\Time_sens_0.6r_manual0.0_f0.3.csv', r'\Time_sens_0.7r_manual0.0_f0.3.csv', r'\Time_sens_0.8r_manual0.0_f0.3.csv', r'\Time_sens_0.9r_manual0.0_f0.3.csv', r'\Time_sens_1.0r_manual0.0_f0.3.csv', r'\Time_sens_1.1r_manual0.0_f0.3.csv', r'\Time_sens_1.2r_manual0.0_f0.3.csv', r'\Time_sens_1.3r_manual0.0_f0.3.csv']
results = r'\Sens Results\Manual'

cols = [range(8), range(9, 16), range(38, 44), range(45, 51), range(52, 58), range(59, 65)]
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
data10 = np.loadtxt(work_dir + results + data_filenames[9], delimiter=',', skiprows=1, usecols=flattened_list)

data_mat = np.dstack((data1, data2, data3, data4, data5, data6, data7, data8, data9, data10))
COT_turn100 = Cost_T(data_mat, style, rad_vec)
count = count+1




########## Turning Algorithm Cost of Transport vs. Pipe Radii of Curvature: 90% act diff
data_filenames = [r'\Time_sens_straight_pipe_norm.csv', r'\Time_sens_0.5r_manual0.1_f0.3.csv', r'\Time_sens_0.6r_manual0.1_f0.3.csv', r'\Time_sens_0.7r_manual0.1_f0.3.csv', r'\Time_sens_0.8r_manual0.1_f0.3.csv', r'\Time_sens_0.9r_manual0.1_f0.3.csv', r'\Time_sens_1.0r_manual0.1_f0.3.csv', r'\Time_sens_1.1r_manual0.1_f0.3.csv', r'\Time_sens_1.2r_manual0.1_f0.3.csv', r'\Time_sens_1.3r_manual0.1_f0.3.csv']
results = r'\Sens Results\Manual'

cols = [range(8), range(9, 16), range(38, 44), range(45, 51), range(52, 58), range(59, 65)]
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
data10 = np.loadtxt(work_dir + results + data_filenames[9], delimiter=',', skiprows=1, usecols=flattened_list)

data_mat = np.dstack((data1, data2, data3, data4, data5, data6, data7, data8, data9, data10))
COT_turn90 = Cost_T(data_mat, style, rad_vec)
count = count+1




########## Turning Algorithm Cost of Transport vs. Pipe Radii of Curvature: 80% act diff
data_filenames = [r'\Time_sens_straight_pipe_norm.csv', r'\Time_sens_0.5r_manual0.2_f0.3.csv', r'\Time_sens_0.6r_manual0.2_f0.3.csv', r'\Time_sens_0.7r_manual0.2_f0.3.csv', r'\Time_sens_0.8r_manual0.2_f0.3.csv', r'\Time_sens_0.9r_manual0.2_f0.3.csv', r'\Time_sens_1.0r_manual0.2_f0.3.csv', r'\Time_sens_1.1r_manual0.2_f0.3.csv', r'\Time_sens_1.2r_manual0.2_f0.3.csv', r'\Time_sens_1.3r_manual0.2_f0.3.csv']
results = r'\Sens Results\Manual'

cols = [range(8), range(9, 16), range(38, 44), range(45, 51), range(52, 58), range(59, 65)]
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
data10 = np.loadtxt(work_dir + results + data_filenames[9], delimiter=',', skiprows=1, usecols=flattened_list)

data_mat = np.dstack((data1, data2, data3, data4, data5, data6, data7, data8, data9, data10))
COT_turn80 = Cost_T(data_mat, style, rad_vec)
count = count+1




########## Turning Algorithm Cost of Transport vs. Pipe Radii of Curvature: 70% act diff
data_filenames = [r'\Time_sens_straight_pipe_norm.csv', r'\Time_sens_0.5r_manual0.3_f0.3.csv', r'\Time_sens_0.6r_manual0.3_f0.3.csv', r'\Time_sens_0.7r_manual0.3_f0.3.csv', r'\Time_sens_0.8r_manual0.3_f0.3.csv', r'\Time_sens_0.9r_manual0.3_f0.3.csv', r'\Time_sens_1.0r_manual0.3_f0.3.csv', r'\Time_sens_1.1r_manual0.3_f0.3.csv', r'\Time_sens_1.2r_manual0.3_f0.3.csv', r'\Time_sens_1.3r_manual0.3_f0.3.csv']
results = r'\Sens Results\Manual'

cols = [range(8), range(9, 16), range(38, 44), range(45, 51), range(52, 58), range(59, 65)]
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
data10 = np.loadtxt(work_dir + results + data_filenames[9], delimiter=',', skiprows=1, usecols=flattened_list)

data_mat = np.dstack((data1, data2, data3, data4, data5, data6, data7, data8, data9, data10))
COT_turn70 = Cost_T(data_mat, style, rad_vec)
count = count+1




########## Turning Algorithm Cost of Transport vs. Pipe Radii of Curvature: 60% act diff
data_filenames = [r'\Time_sens_straight_pipe_norm.csv', r'\Time_sens_0.5r_manual0.4_f0.3.csv', r'\Time_sens_0.6r_manual0.4_f0.3.csv', r'\Time_sens_0.7r_manual0.4_f0.3.csv', r'\Time_sens_0.8r_manual0.4_f0.3.csv', r'\Time_sens_0.9r_manual0.4_f0.3.csv', r'\Time_sens_1.0r_manual0.4_f0.3.csv', r'\Time_sens_1.1r_manual0.4_f0.3.csv', r'\Time_sens_1.2r_manual0.4_f0.3.csv', r'\Time_sens_1.3r_manual0.4_f0.3.csv']
results = r'\Sens Results\Manual'

cols = [range(8), range(9, 16), range(38, 44), range(45, 51), range(52, 58), range(59, 65)]
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
data10 = np.loadtxt(work_dir + results + data_filenames[9], delimiter=',', skiprows=1, usecols=flattened_list)

data_mat = np.dstack((data1, data2, data3, data4, data5, data6, data7, data8, data9, data10))
COT_turn60 = Cost_T(data_mat, style, rad_vec)
count = count+1




########## Turning Algorithm Cost of Transport vs. Pipe Radii of Curvature: 50% act diff
data_filenames = [r'\Time_sens_straight_pipe_norm.csv', r'\Time_sens_0.5r_manual0.5_f0.3.csv', r'\Time_sens_0.6r_manual0.5_f0.3.csv', r'\Time_sens_0.7r_manual0.5_f0.3.csv', r'\Time_sens_0.8r_manual0.5_f0.3.csv', r'\Time_sens_0.9r_manual0.5_f0.3.csv', r'\Time_sens_1.0r_manual0.5_f0.3.csv', r'\Time_sens_1.1r_manual0.5_f0.3.csv', r'\Time_sens_1.2r_manual0.5_f0.3.csv', r'\Time_sens_1.3r_manual0.5_f0.3.csv']
results = r'\Sens Results\Manual'

cols = [range(8), range(9, 16), range(38, 44), range(45, 51), range(52, 58), range(59, 65)]
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
data10 = np.loadtxt(work_dir + results + data_filenames[9], delimiter=',', skiprows=1, usecols=flattened_list)

data_mat = np.dstack((data1, data2, data3, data4, data5, data6, data7, data8, data9, data10))
COT_turn50 = Cost_T(data_mat, style, rad_vec)
count = count+1




########## Turning Algorithm Cost of Transport vs. Pipe Radii of Curvature: 40% act diff
data_filenames = [r'\Time_sens_straight_pipe_norm.csv', r'\Time_sens_0.5r_manual0.6_f0.3.csv', r'\Time_sens_0.6r_manual0.6_f0.3.csv', r'\Time_sens_0.7r_manual0.6_f0.3.csv', r'\Time_sens_0.8r_manual0.6_f0.3.csv', r'\Time_sens_0.9r_manual0.6_f0.3.csv', r'\Time_sens_1.0r_manual0.6_f0.3.csv', r'\Time_sens_1.1r_manual0.6_f0.3.csv', r'\Time_sens_1.2r_manual0.6_f0.3.csv', r'\Time_sens_1.3r_manual0.6_f0.3.csv']
results = r'\Sens Results\Manual'

cols = [range(8), range(9, 16), range(38, 44), range(45, 51), range(52, 58), range(59, 65)]
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
data10 = np.loadtxt(work_dir + results + data_filenames[9], delimiter=',', skiprows=1, usecols=flattened_list)

data_mat = np.dstack((data1, data2, data3, data4, data5, data6, data7, data8, data9, data10))
COT_turn40 = Cost_T(data_mat, style, rad_vec)
count = count+1




########## Turning Algorithm Cost of Transport vs. Pipe Radii of Curvature: 30% act diff
data_filenames = [r'\Time_sens_straight_pipe_norm.csv', r'\Time_sens_0.5r_manual0.7_f0.3.csv', r'\Time_sens_0.6r_manual0.7_f0.3.csv', r'\Time_sens_0.7r_manual0.7_f0.3.csv', r'\Time_sens_0.8r_manual0.7_f0.3.csv', r'\Time_sens_0.9r_manual0.7_f0.3.csv', r'\Time_sens_1.0r_manual0.7_f0.3.csv', r'\Time_sens_1.1r_manual0.7_f0.3.csv', r'\Time_sens_1.2r_manual0.7_f0.3.csv', r'\Time_sens_1.3r_manual0.7_f0.3.csv']
results = r'\Sens Results\Manual'

cols = [range(8), range(9, 16), range(38, 44), range(45, 51), range(52, 58), range(59, 65)]
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
data10 = np.loadtxt(work_dir + results + data_filenames[9], delimiter=',', skiprows=1, usecols=flattened_list)

data_mat = np.dstack((data1, data2, data3, data4, data5, data6, data7, data8, data9, data10))
COT_turn30 = Cost_T(data_mat, style, rad_vec)
count = count+1




########## Turning Algorithm Cost of Transport vs. Pipe Radii of Curvature: 20% act diff
data_filenames = [r'\Time_sens_straight_pipe_norm.csv', r'\Time_sens_0.5r_manual0.8_f0.3.csv', r'\Time_sens_0.6r_manual0.8_f0.3.csv', r'\Time_sens_0.7r_manual0.8_f0.3.csv', r'\Time_sens_0.8r_manual0.8_f0.3.csv', r'\Time_sens_0.9r_manual0.8_f0.3.csv', r'\Time_sens_1.0r_manual0.8_f0.3.csv', r'\Time_sens_1.1r_manual0.8_f0.3.csv', r'\Time_sens_1.2r_manual0.8_f0.3.csv', r'\Time_sens_1.3r_manual0.8_f0.3.csv']
results = r'\Sens Results\Manual'

cols = [range(8), range(9, 16), range(38, 44), range(45, 51), range(52, 58), range(59, 65)]
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
data10 = np.loadtxt(work_dir + results + data_filenames[9], delimiter=',', skiprows=1, usecols=flattened_list)

data_mat = np.dstack((data1, data2, data3, data4, data5, data6, data7, data8, data9, data10))
COT_turn20 = Cost_T(data_mat, style, rad_vec)
count = count+1




########## Turning Algorithm Cost of Transport vs. Pipe Radii of Curvature: 10% act diff
data_filenames = [r'\Time_sens_straight_pipe_norm.csv', r'\Time_sens_0.5r_manual0.9_f0.3.csv', r'\Time_sens_0.6r_manual0.9_f0.3.csv', r'\Time_sens_0.7r_manual0.9_f0.3.csv', r'\Time_sens_0.8r_manual0.9_f0.3.csv', r'\Time_sens_0.9r_manual0.9_f0.3.csv', r'\Time_sens_1.0r_manual0.9_f0.3.csv', r'\Time_sens_1.1r_manual0.9_f0.3.csv', r'\Time_sens_1.2r_manual0.9_f0.3.csv', r'\Time_sens_1.3r_manual0.9_f0.3.csv']
results = r'\Sens Results\Manual'

cols = [range(8), range(9, 16), range(38, 44), range(45, 51), range(52, 58), range(59, 65)]
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
data10 = np.loadtxt(work_dir + results + data_filenames[9], delimiter=',', skiprows=1, usecols=flattened_list)

data_mat = np.dstack((data1, data2, data3, data4, data5, data6, data7, data8, data9, data10))
COT_turn10 = Cost_T(data_mat, style, rad_vec)
count = count+1




########## Adaptive Turning Algorithm Cost of Transport vs. Pipe Radii of Curvature
data_filenames = [r'\Time_sens_straight_pipe_norm.csv', r'\Time_sens_0.5r_adapt_f0.3.csv', r'\Time_sens_0.6r_adapt_f0.3.csv', r'\Time_sens_0.7r_adapt_f0.3.csv', r'\Time_sens_0.8r_adapt_f0.3.csv', r'\Time_sens_0.9r_adapt_f0.3.csv', r'\Time_sens_1.0r_adapt_f0.3.csv', r'\Time_sens_1.1r_adapt_f0.3.csv', r'\Time_sens_1.2r_adapt_f0.3.csv', r'\Time_sens_1.3r_adapt_f0.3.csv']
results = r'\Sens Results\rl0.01_mf15'

cols = [range(8), range(9, 16), range(38, 44), range(45, 51), range(52, 58), range(59, 65)]
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
data10 = np.loadtxt(work_dir + results + data_filenames[9], delimiter=',', skiprows=1, usecols=flattened_list)

data_mat = np.dstack((data1, data2, data3, data4, data5, data6, data7, data8, data9, data10))
COT_adapt = Cost_T(data_mat, style, rad_vec)




########## Combined Results, with Legend (comment out lines to make a subset plot)
# fig = plt.figure(figsize = (12,9))
fig = plt.figure(figsize = (10,4))
# color_mat = cm.plasma(np.linspace(0, 1, count))
color_mat = plasma_trunc(np.linspace(0, 1, count))
lines = []
labels = []

# line, = plt.plot([0.4, 1.35], [COT_straight[0], COT_straight[0]], color = 'Black', linestyle = 'dashed')
# lines.append(line)
line, = plt.plot(rad_vec[3:], COT_straight[3:], color = color_mat[0,:], linestyle='dashdot', markersize=8, label='Norm 0% Act Diff')
lines.append(line)
line, = plt.plot(rad_vec[3:], COT_turn10[3:], color = color_mat[1,:], linestyle='dashdot', markersize=8, label='Turn 10% Act Diff')
lines.append(line)
line, = plt.plot(rad_vec[2:], COT_turn20[2:], color = color_mat[2,:], linestyle='dashdot', markersize=8, label='Turn 20% Act Diff')
lines.append(line)
line, = plt.plot(rad_vec[2:], COT_turn30[2:], color = color_mat[3,:], linestyle='dashdot', markersize=8, label='Turn 30% Act Diff')
lines.append(line)
line, = plt.plot(rad_vec[2:], COT_turn40[2:], color = color_mat[4,:], linestyle='dashdot', markersize=8, label='Turn 40% Act Diff')
lines.append(line)
line, = plt.plot(rad_vec[2:], COT_turn50[2:], color = color_mat[5,:], linestyle='dashdot', markersize=8, label='Turn 50% Act Diff')
lines.append(line)
line, = plt.plot(rad_vec[2:], COT_turn60[2:], color = color_mat[6,:], linestyle='dashdot', markersize=8, label='Turn 60% Act Diff')
lines.append(line)
line, = plt.plot(rad_vec[1:], COT_turn70[1:], color = color_mat[7,:], linestyle='dashdot', markersize=8, label='Turn 70% Act Diff')
lines.append(line)
line, = plt.plot(rad_vec[1:], COT_turn80[1:], color = color_mat[8,:], linestyle='dashdot', markersize=8, label='Turn 80% Act Diff')
lines.append(line)
line, = plt.plot(rad_vec[1:], COT_turn90[1:], color = color_mat[9,:], linestyle='dashdot', markersize=8, label='Turn 90% Act Diff')
lines.append(line)
line, = plt.plot(rad_vec[1:], COT_turn100[1:], color = color_mat[10,:], linestyle='dashdot', markersize=8, label='Turn 100% Act Diff')
lines.append(line)
line, = plt.plot(rad_vec[1:], COT_adapt[1:], color = 'Green', markersize=8, linewidth=2.5, label='Adaptive Act Diff')
lines.append(line)

plt.xlim(left=0.4)
plt.xlim(right=1.35)
# plt.ylim(top=4)
plt.xlabel('Pipe Bend ROC (m)', fontsize = 12, fontname="Arial")
plt.ylabel('Cost of Transport', fontsize = 12, fontname="Arial")
plt.legend(handles=lines[:], labels=labels[:])
# plt.savefig("COT_vs_ROC.png", format="png")
plt.show()




########## Combined Results, with Colorbar
fig = plt.figure(figsize = (10,4))
# color_mat = cm.plasma(np.linspace(0, 1, count))
color_mat = plasma_trunc(np.linspace(0, 1, count))
ax = plt.subplot2grid((1, 1), (0, 0))
ax.plot(rad_vec[3:], COT_straight[3:], color = color_mat[0,:], linestyle='dashdot', markersize=8, label='_nolegend_')
ax.plot(rad_vec[3:], COT_turn10[3:], color = color_mat[1,:], linestyle='dashdot', markersize=8, label='_nolegend_')
ax.plot(rad_vec[2:], COT_turn20[2:], color = color_mat[2,:], linestyle='dashdot', markersize=8, label='_nolegend_')
ax.plot(rad_vec[2:], COT_turn30[2:], color = color_mat[3,:], linestyle='dashdot', markersize=8, label='_nolegend_')
ax.plot(rad_vec[2:], COT_turn40[2:], color = color_mat[4,:], linestyle='dashdot', markersize=8, label='_nolegend_')
ax.plot(rad_vec[2:], COT_turn50[2:], color = color_mat[5,:], linestyle='dashdot', markersize=8, label='_nolegend_')
ax.plot(rad_vec[2:], COT_turn60[2:], color = color_mat[6,:], linestyle='dashdot', markersize=8, label='_nolegend_')
ax.plot(rad_vec[1:], COT_turn70[1:], color = color_mat[7,:], linestyle='dashdot', markersize=8, label='_nolegend_')
ax.plot(rad_vec[1:], COT_turn80[1:], color = color_mat[8,:], linestyle='dashdot', markersize=8, label='_nolegend_')
ax.plot(rad_vec[1:], COT_turn90[1:], color = color_mat[9,:], linestyle='dashdot', markersize=8, label='_nolegend_')
ax.plot(rad_vec[1:], COT_turn100[1:], color = color_mat[10,:], linestyle='dashdot', markersize=8, label='_nolegend_')
ax.plot(rad_vec[1:], COT_adapt[1:], color = 'Green', markersize=8, linewidth=2.5, label='Adaptive Act Diff')

norm = plt.Normalize(vmin=0, vmax=100)      #vmax indicates 100th percentile of the data, not the max color used (don't change to 85)
# sm = cm.ScalarMappable(norm=norm, cmap='plasma')
sm = cm.ScalarMappable(norm=norm, cmap=plasma_trunc)
# im = ax.imshow(speeds, extent=[radii.min(), radii.max(), act_diffs.min(), act_diffs.max()], origin='lower', aspect='auto', cmap='plasma', norm=norm)
cbar = fig.colorbar(sm, ax=ax, label='Activation Difference (%)')       #, shrink=0.8)
cbar.ax.invert_yaxis()

plt.xlim(left=0.4)
plt.xlim(right=1.35)
# plt.ylim(top=4)
plt.xlabel('Pipe Bend ROC (m)', fontsize = 12, fontname="Arial")
plt.ylabel('Cost of Transport', fontsize = 12, fontname="Arial")
# plt.legend(handles=lines[:], labels=labels[:])
plt.legend()
plt.tight_layout()
# plt.savefig("COT_vs_ROC.png", format="png")
plt.show()




# ########## Optional 3D Plot
# bias_vec_base = np.ones(np.size(rad_vec[1:]))
# fig = plt.figure()
# ax = fig.add_subplot(111, projection='3d')
# ax.plot(rad_vec[3:], 0*bias_vec_base[2:], COT_straight[3:], '-o', color = color_mat[0,:], markersize=8, label='Norm 0% Act Diff')
# ax.plot(rad_vec[3:], 10*bias_vec_base[2:], COT_turn10[3:], '-s', color = color_mat[1,:], markersize=8, label='Turn 10% Act Diff')
# ax.plot(rad_vec[2:], 20*bias_vec_base[1:], COT_turn20[2:], '-s', color = color_mat[2,:], markersize=8, label='Turn 20% Act Diff')
# ax.plot(rad_vec[2:], 30*bias_vec_base[1:], COT_turn30[2:], '-s', color = color_mat[3,:], markersize=8, label='Turn 30% Act Diff')
# ax.plot(rad_vec[2:], 40*bias_vec_base[1:], COT_turn40[2:], '-s', color = color_mat[4,:], markersize=8, label='Turn 40% Act Diff')
# ax.plot(rad_vec[2:], 50*bias_vec_base[1:], COT_turn50[2:], '-s', color = color_mat[5,:], markersize=8, label='Turn 50% Act Diff')
# ax.plot(rad_vec[2:], 60*bias_vec_base[1:], COT_turn60[2:], '-s', color = color_mat[6,:], markersize=8, label='Turn 60% Act Diff')
# ax.plot(rad_vec[1:], 70*bias_vec_base, COT_turn70[1:], '-s', color = color_mat[7,:], markersize=8, label='Turn 70% Act Diff')
# ax.plot(rad_vec[1:], 80*bias_vec_base, COT_turn80[1:], '-s', color = color_mat[8,:], markersize=8, label='Turn 80% Act Diff')
# ax.plot(rad_vec[1:], 90*bias_vec_base, COT_turn90[1:], '-s', color = color_mat[9,:], markersize=8, label='Turn 90% Act Diff')
# ax.plot(rad_vec[1:], 100*bias_vec_base, COT_turn100[1:], '-s', color = color_mat[10,:], markersize=8, label='Turn 100% Act Diff')

# ax.plot(rad_vec[1:], 120*bias_vec_base, COT_adapt[1:], '-*', color = 'Green', markersize=8, label='Adaptive Act Diff')

# ax.set_xlabel('Pipe Bend Radius of Curvature (m)', fontsize = 12, fontname="Arial")
# ax.set_ylabel('Activation Difference (%)', fontsize = 12, fontname="Arial")
# ax.set_zlabel('Cost of Transport', fontsize = 12, fontname="Arial")

# ax.legend()
# plt.show()




# Working version of COT calculation before turning it into a function
# data_filenames = [r'\Time_sens_straight_pipe_norm.csv', r'\Time_sens_0.5r_manual0.6_f0.3.csv', r'\Time_sens_0.6r_manual0.6_f0.3.csv', r'\Time_sens_0.7r_manual0.6_f0.3.csv', r'\Time_sens_0.8r_manual0.6_f0.3.csv', r'\Time_sens_0.9r_manual0.6_f0.3.csv', r'\Time_sens_1.0r_manual0.6_f0.3.csv', r'\Time_sens_1.1r_manual0.6_f0.3.csv', r'\Time_sens_1.2r_manual0.6_f0.3.csv', r'\Time_sens_1.3r_manual0.6_f0.3.csv']
# results = r'\Sens Results\Manual'

# cols = [range(8), range(9, 16), range(38, 44), range(45, 51), range(52, 58), range(59, 65)]
# flattened_list = [item for r in cols for item in r]
# data1 = np.loadtxt(work_dir + results + data_filenames[0], delimiter=',', skiprows=1, usecols=flattened_list)
# data2 = np.loadtxt(work_dir + results + data_filenames[1], delimiter=',', skiprows=1, usecols=flattened_list)
# data3 = np.loadtxt(work_dir + results + data_filenames[2], delimiter=',', skiprows=1, usecols=flattened_list)
# data4 = np.loadtxt(work_dir + results + data_filenames[3], delimiter=',', skiprows=1, usecols=flattened_list)
# data5 = np.loadtxt(work_dir + results + data_filenames[4], delimiter=',', skiprows=1, usecols=flattened_list)
# data6 = np.loadtxt(work_dir + results + data_filenames[5], delimiter=',', skiprows=1, usecols=flattened_list)
# data7 = np.loadtxt(work_dir + results + data_filenames[6], delimiter=',', skiprows=1, usecols=flattened_list)
# data8 = np.loadtxt(work_dir + results + data_filenames[7], delimiter=',', skiprows=1, usecols=flattened_list)
# data9 = np.loadtxt(work_dir + results + data_filenames[8], delimiter=',', skiprows=1, usecols=flattened_list)
# data10 = np.loadtxt(work_dir + results + data_filenames[9], delimiter=',', skiprows=1, usecols=flattened_list)

# data_mat = np.dstack((data1, data2, data3, data4, data5, data6, data7, data8, data9, data10))
# color_mat = cm.rainbow(np.linspace(0, 1, data_mat.shape[2]))
# style = ["straight", "bend", "bend", "bend", "bend", "bend", "bend", "bend", "bend", "bend"]

# pipe_rad = 0.2
# rad_vec = np.array([0.0, 0.5, 0.6, 0.7, 0.8, 0.9, 1.0, 1.1, 1.2, 1.3])
# mass = 1.981                        # robot mass in kg
# grav = 9.81                         # gravity in m/s^2
# length_0 = 0.25                     # Length of straight section
# l_0 = np.zeros(Nseg)
# for q in range(Nseg):
#     l_0[q] = length_0+0.0935+q*0.1122


# speed_vec = np.zeros(data_mat.shape[2])
# s = np.zeros((data_mat.shape[0], Nseg, data_mat.shape[2]))
# s_end = rad_vec*np.pi/2

# Work = np.zeros(data_mat.shape[2])
# Distance = np.zeros(data_mat.shape[2])
# COT = np.zeros(data_mat.shape[2])
# cut_time = np.zeros(data_mat.shape[2])

# for j in range(data_mat.shape[2]):
#     if style[j] == "bend":
#         trig = 0
#         x_m = data_mat[:,1:Nseg+1,j]
#         y_m = data_mat[:,2+Nseg:2+2*Nseg,j]
#         #### Mapping to path along centerline of a 90 degree pipe bend    
#         for i in range(data_mat.shape[0]):
#             for q in range(Nseg):
#                 if x_m[i,q] <= l_0[q]:              # + distance of segment from pipe end, WILL BE DIFFERENT if using COM (+0.374)
#                     s[i,q,j] = x_m[i,q]
#                 elif x_m[i,q] > l_0[q]:
#                     phi = np.arctan((x_m[i,q]-l_0[q])/(rad_vec[j]-y_m[i,q]))
#                     s[i,q,j] = l_0[q]+phi*rad_vec[j]
#                 if y_m[i,q] >= rad_vec[j]:
#                     s[i,q,j] = l_0[q]+s_end[j]+y_m[i,q]-rad_vec[j]
#             if y_m[i,5] >= rad_vec[j] and trig !=1:         # cut data off if/when last segment leaves pipe bend (?)
#                 cut_time[j] = i
#                 trig = 1
#             elif trig != 1:
#                 cut_time[j] = data_mat.shape[0]-1
#         # print(cut_time[j])

#         denominator = 0
#         for q in range(Nseg):
#             # for i in range(1, data_mat.shape[0]):
#             for i in range(1, int(cut_time[j])):
#                 # Work[j] = Work[j] + data_mat[i,3+2*Nseg+q,j]*abs(data_mat[i,3+4*Nseg+q,j]-data_mat[i-1,3+4*Nseg+q,j])      # F_i*del_l
#                 # Work[j] = Work[j]+0.5*data_mat[i,3+2*Nseg+q,j]*max(abs(0.48-data_mat[i-1,3+4*Nseg+q,j]), 0)      # F_i*del_l, del_l is from rest (0.48m), NOT time i-1 to i
#                 Work[j] = Work[j]+0.5*data_mat[i,3+2*Nseg+q,j]*max(abs(0.48-data_mat[i-1,3+4*Nseg+q,j]), 0)+0.5*data_mat[i,3+3*Nseg+q,j]*max(abs(0.48-data_mat[i-1,3+5*Nseg+q,j]), 0)      # F_i*del_l, del_l is from rest (0.48m), NOT time i-1 to i

#             denominator = denominator + mass/Nseg*grav*s[int(cut_time[j]),q,j]         # Add contribution of each segment individually since COM path hard to predict
#             Distance[j] = Distance[j]+s[int(cut_time[j]),q,j]
#             # print(s[int(cut_time[j]),q,j])                        # Distance traveled for each segment
#         COT[j] = Work[j]/denominator
#         Distance[j] = Distance[j]/Nseg          # Approximated distance traveled of COM using average of individual segments
        
#     else:
#         popt, pcov = curve_fit(lin_func, data_mat[:,0,j], data_mat[:,7,j])
#         speed_vec[j] = popt[1]*1000             # 1000 gets it into units of m/s

#         for i in range(1, data_mat.shape[0]):
#             for q in range(Nseg):
#                 # Work[j] = Work[j]+data_mat[i,3+2*Nseg+q,j]*abs(data_mat[i,3+4*Nseg+q,j]-data_mat[i-1,3+4*Nseg+q,j])      # F_i*del_l
#                 # Work[j] = Work[j]+0.5*data_mat[i,3+2*Nseg+q,j]*max(abs(0.48-data_mat[i-1,3+4*Nseg+q,j]), 0)      # F_i*del_l, del_l is from rest (0.48m), NOT time i-1 to i
#                 Work[j] = Work[j]+0.5*data_mat[i,3+2*Nseg+q,j]*max(abs(0.48-data_mat[i-1,3+4*Nseg+q,j]), 0)+0.5*data_mat[i,3+3*Nseg+q,j]*max(abs(0.48-data_mat[i-1,3+5*Nseg+q,j]), 0)      # F_i*del_l, del_l is from rest (0.48m), NOT time i-1 to i

#         Distance[j] = data_mat[data_mat.shape[0]-1,7,j]-data_mat[0,7,j]
#         COT[j] = Work[j]/(mass*grav*Distance[j])

# print("Work is : ", np.round(Work, 2))
# print("Distance is : ", np.round(Distance, 2))
# print("COT is : ", np.round(COT, 2))
# print("Average speed is : ", np.round(speed_vec, 4))
# print("")

# COT_straight = COT