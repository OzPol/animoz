from vpython import *

scene.background = color.white
scene.width = 800
scene.height = 600
scene.camera.pos = vector(0, 0, -5)
scene.camera.axis = vector(0, 0, 5)

# Create a simple 3D object
box_obj = box(pos=vector(0, 0, 0), size=vector(2, 2, 2), color=color.red)

# Rotate it forever (or until stopped)
# This is a simple animation loop that rotates the box object around the y-axis
while True:
    rate(60)
    box_obj.rotate(angle=radians(2), axis=vector(0, 1, 0))
