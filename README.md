# 28add11's Vector Processor and Normalizer

This project is a simple FSM driven vector processor for use in 3D graphics. It implements matrix-vector postmultiplication and then normalization with a w coordinate, which is the first steps in a 3D graphics pipeline. 
It is not programmable (Though hopefully that'll change in v2) however it is capable of (Insert speed here!).

![the final 3D render of a cube](https://github.com/28add11/diy-GPU/blob/main/renderedCube.png)

This project was submitted for [Hack Club's Summer of Making](https://summer.hackclub.com/), a summer-long program where teenagers can get rewards for making things!
The process of making this was a big learning experience, and although there are many ways it can be improved, I'm still very proud of it. Eventually, I would love to integrate it into a full video game console and share it with the world.

## What does it do?

The core idea of the 3D graphics pipeline is turning a point in 3D space to a point on a 2D screen so that it may be filled in (rasterized). This project handles the former component, translating a 3D point to a 2D one.
To do this, we use matricies from math. If you aren't familiar with them, don't worry, they're just effectively lists of numbers. A seperate compute unit (Likely a CPU) creates what's called a projection matrix, 
which we multiply with our coordinates to "project" them onto a virtual camera plane (think of it like a strip of film or an image sensor). After that, we perform a perspective divide on all our coordinates, dividing them 
by our depth value. This is what really gives the illusion of depth.

## How does it do this?

The core logic is driven by a mealy finite state machine (FSM) which transitions from one state to another based on current inputs. Once we recive the start signal, the FSM transitions from an idle state to loading in the matrix for calculations. 
After that, for every vector (passed in by the workItemCount input) we load it in, multiply it by the matrix, then take the reciprocal of the depth coordinate and multiply the result to all our other vectors. 
This does the same as dividing the coordinates but saves on many cycles, since divisions are much more expensive than multiplications for cycle times. 
All of this is done with fixed point arithmetic, since it is much easier to implement on the constrained timeframe for Summer of Making, not to mention it is already flexible enough for this project.

## Where will this project go in the future?

Though I'm proud of what I've accomplished with this, I would like to make some improvements for the second version, which will hopefully be good enough for real time complex graphics.

1. Make it programmable
   - Currently, the design is not programmable, which locks developers into a specific way of doing things, not to mention makes this harder to optimize.
   - In V2, changing this from an FSM based system to a heavily modified RISC-V alike would greatly improve things, as well as help me practice programmable core design.
2. Rasterization
   - This is only one half of the graphics pipeline, true GPUs still need to draw something to the screen!
   - On the second version, I want to add a seperate rasterization pipeline. I want to make it somewhat programmable, but only to the degree that simple lighting and shading is possible. Beyond that, speed and features should be the biggest concern.
3. Clipping
   - Clipping is the part of the GPU pipeline that makes it impossible to see what's behind you.
   - This will be easily implemented with a programmable pipeline, as long as it is designed well.
4. Bus connection
   - Modern SoCs would control such a device through a bus such as one from Arm's AMBA protocols.
   - Adding control through a bus would also make integration and testing on FPGAs much easier.

I can't wait to get a chance to actually implement these features on a new design, hopefully if you found this interesting you could keep an eye on how it goes!
