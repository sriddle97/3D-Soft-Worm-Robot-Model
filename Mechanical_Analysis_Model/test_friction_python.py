########################### Import packages #############################

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

#########################################################################

work_dir = os.getcwd()
xml_path = work_dir + r"\worm_modeling\worm_friction_test.xml"
# xml_path = work_dir + r"\worm_modeling\friction_platform.xml"
model = mujoco.MjModel.from_xml_path(xml_path)
data = mujoco.MjData(model)


vid_names = ["Angled_Friction_0.6.mp4"]


mujoco.mj_forward(model, data)
renderer = mujoco.Renderer(model, 400, 900)
renderer.update_scene(data, camera='fixed')

tmax = 15
dt = 1/1000                     #milliseconds
t = np.arange(0, tmax, dt)

model.opt.timestep = dt

frames = [] 
framerate = 60

# max_act = -1.0
# ctrl_ramp = np.ones(len(t))*max_act
# ctrl_ramp[0:int(len(t)*0.8)] = np.linspace(0,max_act,int(len(t)*0.8))
max_act = -0.6
ctrl_ramp = np.ones(len(t))*max_act
ctrl_ramp[0:int(len(t)*0.5)] = np.linspace(0,max_act,int(len(t)*0.5))


platform_angle = np.zeros(np.size(t))
actuator_id = mujoco.mj_name2id(model,mujoco.mjtObj.mjOBJ_ACTUATOR,"plat_motor")
joint_id = mujoco.mj_name2id(model,mujoco.mjtObj.mjOBJ_JOINT,"angler")

count = 0
# for i in range(len(t)):
for i in tqdm(range(len(t)), miniters=500):

    data.ctrl[actuator_id] = ctrl_ramp[i]  # Set the control signal
    mujoco.mj_step(model, data)
    platform_angle[i] = data.qpos[joint_id]
    
    if len(frames) < data.time*framerate:
        renderer.update_scene(data, camera='fixed')
        frames.append(renderer.render().copy())

media.write_video(vid_names[count], frames, fps=framerate)          # Save video
renderer.close()