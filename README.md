# 3D Worm Robot Model

This repository contains a model of an earthworm inspired soft robot built in the physics engine Mujoco as well as a variety of testing environments used to tune the model and study peristaltic locomotion behavior.

### Building the Model
Mujoco compiles models into the simulation environment from an xml file or object. The xml file for this robot can be auto-generated using the master_worm.m file in the worm_modeling folder. Please note that changes to the model will necessitate minor changes to the code (accounting for new sensor length tolerances, more segments, etc.).

### Running the Model
The python script Time_Based_Worm.py runs the simulation using the model specified in the xml_path variable.

### Necessary Packages
To run this model you will need to have mujoco installed. We have verified compatibility up to Mujoco 3.3.0:

https://github.com/deepmind/mujoco/releases

## Code Citations
[1]  Wouter Falkena (2023). xml2struct (https://www.mathworks.com/matlabcentral/fileexchange/28518-xml2struct), MATLAB Central File Exchange. Retrieved May 22, 2023.

[2]  Wouter Falkena (2023). struct2xml (https://www.mathworks.com/matlabcentral/fileexchange/28639-struct2xml), MATLAB Central File Exchange. Retrieved May 22, 2023.
