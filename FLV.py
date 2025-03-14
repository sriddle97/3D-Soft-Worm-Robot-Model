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


############ Functions ##############

def bump(L, A, mid, B):
    # A = lmin
    # B = lmax
    left = 0.5*(A+mid)
    right = 0.5*(mid+B)
    if L <=A or L >= B:
        y = 0
    elif L < left:
        x = (L-A)/(left-A)
        y = 0.5*x*x
    elif L < mid:
        x = (mid-L)/(mid-left)
        y = 1-0.5*x*x
    elif L < right:
        x = (L-mid)/(right-mid)
        y = 1-0.5*x*x
    else:
        x = (B-L)/(B-right)
        y = 0.5*x*x
    return y

def Force_length(LL, lmin, lmax):
    FL = np.zeros(len(LL))
    for i in range(len(LL)):
        L = LL[i]
        FL[i] = bump(L, lmin, 1, lmax) + 0.15*bump(L, lmin, 0.5*(lmin+0.95), 0.95)
    return FL

def calc_FL(length, lengthrange, mj_range, lmin, lmax):
    L0 = (lengthrange[1] - lengthrange[0]) / (mj_range[1] - mj_range[0])
    L = np.array(mj_range[0] + (length - lengthrange[0]) / L0)
    out = Force_length(L, lmin, lmax)
    return out

#####################################

################################### Define FLV parameters and plot curve ############################################

# # Default values for Mujoco FLV curve (cannot be used here since lengthrange does not have a default value)
# lengthrange = [0, 0]        # Derived at compile time if not defined
# lmin = 0.5
# lmax = 1.6
# range = [0.75, 1.05]

# #Old model parameters (bend=8e8 worm model with lmin, and range muscles)
# lengthrange = [0.055 1.069]
# lmin = 0.58
# lmax = 1.6
# range = [0.62, 1.1]

# Automatically get work directory
work_dir = os.getcwd()
print("String format :", work_dir)


###### Tune the muscles using the FLV curve. 
# The goal is to tune the FLV output such that the maximum tension force required to contract a segment
# is produced at the lower limit of the specified lengthrange (ie. when the segment is fully contracted)

# Velocity component of the FLV curve scales forces down a little, so overshooting the max force by ~20% is fine. 
Fmax_20e8_measured = 16.05      # This one was tuned to match the Wang robot, serves as a baseline
FLV_curve_F_lmin_20e8 = 19.39
overshoot_proportinality = FLV_curve_F_lmin_20e8/Fmax_20e8_measured
Fmax_10e8_measured = 9.58
Fmax_3e8_measured = 4.79
Goal_Fmax_10e8 = overshoot_proportinality*Fmax_10e8_measured
Goal_Fmax_3e8 = overshoot_proportinality*Fmax_3e8_measured
print('Peak force recorded for 20e8 model is: ', Fmax_20e8_measured)
print('Tuned FLV force at full contraction for 20e8 model is ', (overshoot_proportinality-1)*100, '% over meaasured')
print('Full contraction goal for 10e8 model is: ', Goal_Fmax_10e8)
print('Full contraction goal for 3e8 model is: ', Goal_Fmax_3e8)


###### FLV Curve Calculations and Plotting
# length =np.arange(0.1, 2.0, 0.01)      # Vector of real lengths for plotting scaled FLV curve
length =np.arange(0.1, 1.8, 0.01)      # Vector of real lengths for plotting scaled FLV curve
color_mat = ['Red', 'Green', 'Blue']

# bend=20e8 worm model with lengthrange muscles (lmin, lmax, range = deafault settings)
lengthrange = [0.62, 0.96]          # Determined by geometry
lmin = 0.5
lmax = 1.6
mj_range = [0.75, 1.05]
Fmax = 30                           # Tuned parameter
FL = calc_FL(length, lengthrange, mj_range, lmin, lmax)
plt.plot(length, Fmax*FL, color = color_mat[0], label='20e8')
plt.plot(length[52], Fmax*FL[52], '*', color  = color_mat[0], markersize=12)
plt.text(length[52], Fmax*FL[52], '19.39 N   ', fontsize=12, fontname="Arial", ha='right', va='bottom')

# bend=10e8 worm model with lengthrange muscles
lengthrange = [0.62, 0.96]
lmin = 0.5
lmax = 1.6
mj_range = [0.75, 1.05]
Fmax = 18
FL = calc_FL(length, lengthrange, mj_range, lmin, lmax)
plt.plot(length, Fmax*FL, color = color_mat[1], label='10e8')
plt.plot(length[52], Fmax*FL[52], '*', color  = color_mat[1], markersize=12)
plt.text(length[52], Fmax*FL[52], '11.63 N      ', fontsize=12, fontname="Arial", ha='right', va='bottom')

# bend=3e8 worm model with lengthrange muscles
lengthrange = [0.62, 0.96]
lmin = 0.5
lmax = 1.6
mj_range = [0.75, 1.05]
Fmax = 9
FL = calc_FL(length, lengthrange, mj_range, lmin, lmax)
plt.plot(length, Fmax*FL, color = color_mat[2], label='3e8')
plt.plot(length[52], Fmax*FL[52], '*', color  = color_mat[2], markersize=12)
plt.text(length[52], Fmax*FL[52], '5.82 N          ', fontsize=12, fontname="Arial", ha='right', va='bottom')

# # 20e8 Testing different lengthrage (to show how it changes the FLV curve)
# lengthrange = [0.62, 1.5]
# lmin = 0.5
# lmax = 1.6
# range = [0.75, 1.05]
# Fmax = 30
# FL = calc_FL(len, lengthrange, range, lmin, lmax)
# plt.plot(len, Fmax*FL, color = 'Gray')

# Plot bars for the lengthrange limits
plt.plot([0.62, 0.62], [0, 30], color = 'Black', ls='--')
plt.plot([0.96, 0.96], [0, 30], color = 'Black', ls='--')
plt.xlabel('Length (m)', fontsize = 12, fontname="Arial")
plt.ylabel('Force (N)', fontsize = 12, fontname="Arial")
plt.legend()
plt.savefig("FLV_curves.png", format="png")
plt.show()