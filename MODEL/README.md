![GIF](D2%20ROBOTICS%20-%20MODEL.gif)


# 🧩 MODEL – Robot Design Overview

### Welcome to the `MODEL` section. Here you will find the complete design of our robot, including various types of mechanical components, all fully designed and developed by our team. This folder showcases the structural and functional elements that make up our robotic system, reflecting our custom engineering approach.


## 🧭 Direction System - Four Wheels Sterring

### For the steering system, our decision was based on the requirements of the **Obstacle Challenge**. We anticipated the need for very tight turns, so we opted for **four-wheel steering**. This configuration allows for a greater turning angle and improved precision when maneuvering.

### We use **SG90 servo motors** due to their low cost and minimal power consumption.  

### We developed an **independent steering system for each axle** (front and rear), which enables tight maneuvers with the designed configuration and significantly reduces time on the track, as shown in the following image:

imagen

### Since both axles are steerable, we needed to ensure that the **front axle turns in the opposite direction to the rear axle**, and vice versa.  
### To achieve this, we implemented a **basic four-gear system**, as shown in the image below.  
### This solution allowed us to complete a fully functional and synchronized steering system for the robot.

iamgen


## 🔧 Traction System – 4WD

### For the traction system, we chose a **4WD configuration** (four-wheel drive), also known as a **4x4 system**. We believe this setup is more effective on the track, providing better grip and higher speed.
### We use **N20 motors** due to their practicality, speed, and lightweight design. To further enhance performance, we implemented **gears** to increase the robot's speed and a **shaft system** that transmits power to both the front and rear wheels.  
#### This shaft is connected to a **custom differential**, which allows smoother and more controlled motion during turns by distributing power appropriately, regardless of the steering angle.

### Below is an image showcasing the full 4WD setup:

#### imagne

### However, having both steering and traction on all four wheels introduced a major challenge:  
### **How to maintain traction while the robot is turning**.

### To solve this, we designed a **custom differential-like mechanism for each wheel** that allows them to receive power **independently of the steering angle**.  
### This system ensures continuous traction even during sharp turns, greatly improving maneuverability and overall stability on the track.

### Below, we present an image of the implemented system:

#### imagne

