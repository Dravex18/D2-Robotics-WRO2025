![GIF](D2%20ROBOTICS%20-%20MODEL.gif)


# 🧩 MODEL – Robot Design Overview

### Welcome to the `MODEL` section. Here you will find the complete design of our robot, including various types of mechanical components, all fully designed and developed by our team. This folder showcases the structural and functional elements that make up our robotic system, reflecting our custom engineering approach.

## DESIGN

This robot was engineered entirely from the ground up, featuring four‑wheel drive and four‑wheel steering. All virtual modeling and assembly were performed in Autodesk Fusion 360, enabling interference checks and tolerance verification without the need for physical prototypes.

Over a three‑month period, we conducted exhaustive testing to optimize:
- Gear tolerances: Dimensional adjustments and clearances were refined to ensure precise meshing and minimize frictional losses.

- Powertrain efficiency: Various motor and transmission ratios were evaluated to maximize output torque and system autonomy.

- Mobility and handling: Simulation of traction and steering control algorithms guaranteed stability during tight turns and rapid directional changes.

- Total mass: Materials and additive‑manufacturing parameters were selected to achieve the optimal stiffness‑to‑weight ratio.


The outcome is one of the most efficient and precise integrated drive‑and‑steering systems implemented in a four‑wheel vehicle.

<p align="center">
  <img src="https://github.com/user-attachments/assets/33eb4b2c-921f-4994-8330-f2ba8f8b8fe5" alt="YouTube Badge" />
</p>

> ## **Note 🔔**  
> ### You can download the .step file [here!!!)](https://github.com/Dravex18/D2-Robotics-WRO2025/releases/download/v1.0-step/Final%20version%20v38.step) .





---


## Additive Manufacturing

For 3D printing the Fusion 360–designed components, we employed a dual‑technology approach:

1. Resin printing (Anycubic Photon):

- Reserved for small, complex geometries such as gears, sensor mounts, and enclosures.

- Included UV curing and post‑processing to achieve the required hardness and dimensional stability.

2. FDM printing (Creality Ender 3 V2):
 - Used for larger structural components where print speed and material economy are prioritized (wheels, structural frames).

 - Optimized infill density, layer height, and retraction settings to maintain mechanical strength while minimizing weight.

<p align="center">
  <img 
    src="https://github.com/user-attachments/assets/15b76466-0532-444d-9004-3f135915a97f" 
    width="300" 
    height="300" 
    alt="Resin Printing"
  </p>




---

## PCB as Chassis

From the project’s outset, we planned to design a custom PCB to host all electronics. Spatial constraints led us to integrate the PCB directly into the chassis:

- Material: FR‑4 fiberglass, providing both structural rigidity and electrical insulation.

- Dual functionality: Supports electronic components (motor drivers, microcontroller, power supplies) and serves as the robot’s main frame.

- Benefits: Reduces overall part count and mass, simplifies assembly, and enhances structural integration


<p align="center">
  <img
    src="https://github.com/user-attachments/assets/c2cdef05-dc74-446f-ba78-8e6435c45050"
    width="300"
    height="300"
    alt="PCB Chassis"
  >
</p>





---
# wheels

For the wheels, we drew inspiration from this [pag](https://sites.google.com/view/fridayroboticsdreamproyectos/ruedas-japonesas-robotracer-japanese-robotracer-wheels), then designed the rims, cut a section of specialized foam, and finally wrapped it in a custom rubber tread—each end mitered at 45°—to prevent the tire from tearing during rotation.



<p align="center">
  <img
    src="https://github.com/user-attachments/assets/c62a6825-1d12-4070-be1c-b7644fae9dd3"
    width="300"
    height="300"
    alt="Wheel Foam Core"
    style="margin-right: 20px;"
  />
  <img
    src="https://github.com/user-attachments/assets/197c7603-080b-4dba-9a85-a18217d9288d"
    width="300"
    height="300"
    alt="LLantas"
  />
</p>


---

By combining systematic design, virtual validation, and strategic use of additive manufacturing, we have developed a robust, lightweight, and highly maneuverable robot architecture that fully leverages rapid‑prototyping and engineering best practices.














