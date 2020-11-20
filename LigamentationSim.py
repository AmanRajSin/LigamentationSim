import tkinter as tk
from tkinter import messagebox
import math
from random import randint, uniform
from time import sleep

depth = 2     # Depth of tree (no of splits)
Levels = [[]] # List storing pointer to nodes at each level

# Binary tree
class Node:
    def __init__(self, size, d, yfac=[0], parent=None):
        self.left = None       # Pointer to left child
        self.right = None      # Pointer to right child
        self.parent = parent   # Pointer to parent
        self.size = size       # Self Radius
        self.yfac = yfac       # stores yVelocity of self and all predecessors (to calculate exact y coordinate)

        # Recursively building the tree
        if(d>0):
            inver = randint(0, 1)             # Whether larger particle is at top
            
            # Random split-ratio
            if inver:
                ratio = uniform(1.0, 2.5)
            else:
                ratio = uniform(0.4, 1.0)
            
            # Left & Right split factors. Used in both Radius and yVelocity
            yl = abs((1+ratio)**-0.5)
            yr = abs((ratio/(1+ratio))**0.5)

            # Build tree
            self.left = Node(self.size*yr, d-1, self.yfac+[yl*size], self)
            self.right = Node(self.size*yl, d-1, self.yfac+[-yr*size], self)

            # Add nodes to levels
            Levels[depth-d].append([self.right, self.left])

    # Inorder Tree Display
    def printTree(self):
        if (self.left):
            self.left.printTree()
        print(self.size, end=' ')
        if (self.right):
            self.right.printTree()

    # Access info
    def getInfo(self):
        return [self.size, self.yfac]

# Animation function
def animate(window, canvas, radius=50, vel=50, d=2, scale=1, slow=1, colour = '#ffa500'):
    # Update global variables
    global depth, Levels
    depth = d
    Levels = [[] for i in range(0, depth+1)]

    root = Node(radius, depth) # Create Tree with initial radius and depth
    root.printTree()           # Inorder Tree Display

    # Initial single particle animation
    for frame in range(1, 30):
        canvas.delete('all')                                                                                            # Clear canvas
        x = (radius*scale) + (frame*scale*vel/20)                                                                       # x Coordinate
        canvas.create_oval(x-radius*scale, 250-radius*scale, x+radius*scale, 250+radius*scale, fill=colour, outline='') # Draw particle
        canvas.update()                                                                                                 # Update canvas
        sleep(1/(30*slow))                                                                                              # Frame duration pause

    # Particle pair animation
    for frame in range(1, depth*60):
        canvas.delete('all')                 # Clear canvas
        for shape in Levels[frame//60]:      # For each shape-pair in current level
            # Getting info for both particles
            [r1, yfac1] = shape[0].getInfo()
            [r2, yfac2] = shape[1].getInfo()
            R = shape[0].parent.getInfo()[0]

            # Calculating x & y coordinates
            x = (radius+ 3*vel/2 + frame*vel/20)*scale
            y1 = 250+sum([(frame-(60*i))*yfac1[i+1]/30 for i in range(math.ceil(frame/60))])*scale
            y2 = 250+sum([(frame-(60*i))*yfac2[i+1]/30 for i in range(math.ceil(frame/60))])*scale

            # Display single particle on first frame from start of split
            if frame%60==0:
                canvas.create_oval(x-R*scale, y1-R*scale, x+R*scale, y1+R*scale, fill=colour, outline='')

            # Display splitting particles on 1-29 frames from start of split
            elif frame%60<30:
                # Calculate radius of particles on the particular frame
                r1_fr = (R-((R-r1)*(frame%60)/30))*scale # Radius of Particle 1
                r2_fr = (R-((R-r2)*(frame%60)/30))*scale # Radius of Particle 2
                r3_fr = (2*R-(2*R*(frame%60)/30))*scale  # Radius of joint curvature

                # Coordinates (a, b) of centre of joint curvature arc 
                b = (y1+y2+(((2*r3_fr+r1_fr+r2_fr)*(r1_fr-r2_fr))/(y2-y1)))/2
                a = x + (((r3_fr+r1_fr)**2+(r3_fr+r2_fr)**2-(b-y1)**2-(b-y2)**2)/2)**0.5

                # Angles substended by centre of curvature arc on centres of particles
                theta1 = (180/math.pi)*(math.atan((b-y1)/(a-x)))
                theta2 = (180/math.pi)*(math.atan((y2-b)/(a-x)))

                # Components of particle radii on vertical and horizontal axes (c is for cos and s is for sin)
                r1c = r1_fr*math.cos(theta1*math.pi/180)
                r1s = r1_fr*math.sin(theta1*math.pi/180)
                r2c = r2_fr*math.cos(theta2*math.pi/180)
                r2s = r2_fr*math.sin(theta2*math.pi/180)

                # Draw particles
                canvas.create_oval(x-r1_fr, y1-r1_fr, x+r1_fr, y1+r1_fr, fill=colour, outline='')
                canvas.create_oval(x-r2_fr, y2-r2_fr, x+r2_fr, y2+r2_fr, fill=colour, outline='')

                # Draw joint as polygon
                canvas.create_polygon(x+r1c, y1+r1s, x-r1c, y1+r1s, x-r2c, y2-r2s, x+r2c, y2-r2s, fill=colour, outline='')

                # Draw arcs of background colour to make concave curvature in the joint
                canvas.create_arc(a-r3_fr, b-r3_fr, a+r3_fr, b+r3_fr, start=(180-theta1), extent = theta1+theta2, fill='#ffffff', style=tk.CHORD, outline='')
                canvas.create_arc(a-2*(a-x)-r3_fr, b-r3_fr, a-2*(a-x)+r3_fr, b+r3_fr, start=(-theta2), extent = theta1+theta2, fill='#ffffff', style=tk.CHORD, outline='')

            # Display separate particles on 30-59 frames from start of split
            else:
                canvas.create_oval(x-r1*scale, y1-r1*scale, x+r1*scale, y1+r1*scale, fill=colour, outline='')
                canvas.create_oval(x-r2*scale, y2-r2*scale, x+r2*scale, y2+r2*scale, fill=colour, outline='')

        canvas.update()    # Update canvas
        sleep(1/(30*slow)) # Frame duration pause

# Tkinter window
window = tk.Tk()
window.geometry('1000x560')
window.title('Ligamentation in Gas Atomization')

# Tkinter canvas
canvas = tk.Canvas(window, height=500, width=1000, bg='#ffffff')
canvas.pack(side=tk.TOP)

# Frames for organizing different widgets of the window
fr1 = tk.Frame(window, height=25, width=1000)
fr1.pack(side=tk.TOP, pady=2)
fr2 = tk.Frame(window, height=25, width=1000)
fr2.pack(side=tk.TOP, pady=2)

# Labels & Textboxes
lb1 = tk.Label(fr1, text='Radius:')
in1 = tk.Entry(fr1, width=20)
in1.insert(tk.END, '65')
lb1.pack(side=tk.LEFT)
in1.pack(side=tk.LEFT, padx=(0, 15))

lb2 = tk.Label(fr1, text='xVelocity:')
in2 = tk.Entry(fr1, width=20)
in2.insert(tk.END, '150')
lb2.pack(side=tk.LEFT)
in2.pack(side=tk.LEFT, padx=(0, 15))

lb3 = tk.Label(fr1, text='No. of Split:')
in3 = tk.Entry(fr1, width=20)
in3.insert(tk.END, '3')
lb3.pack(side=tk.LEFT)
in3.pack(side=tk.LEFT, padx=(0, 15))

lb4 = tk.Label(fr1, text='Frame Scale:')
in4 = tk.Entry(fr1, width=20)
in4.insert(tk.END, '0.5')
lb4.pack(side=tk.LEFT)
in4.pack(side=tk.LEFT, padx=(0, 15))

lb5 = tk.Label(fr1, text='Time Scale:')
in5 = tk.Entry(fr1, width=20)
in5.insert(tk.END, '1')
lb5.pack(side=tk.LEFT)
in5.pack(side=tk.LEFT, padx=(0, 0))

# Run onClick function
def onClick():
    animate(window=window, canvas=canvas, radius=float(in1.get()), vel=float(in2.get()), d=int(in3.get()), scale=float(in4.get()), slow=float(in5.get()))

# Info onClick function
def infoCl():
    messagebox.showinfo('Details', 'Radius(float) - Initial Radius of the particle\nxVelocity(float) - x velocity of particle\nNo. of Split(int) - No of times particle will split\nFrame Scale(float) - Scale of coordinate axes\nTime Scale(float) - Scale of animation speed\n\nOptimal values are entered by default.')

# Run Button
run = tk.Button(fr2, width=7,text='Run', command=onClick)
run.pack(side=tk.LEFT, padx=2)

# Info Button
info = tk.Button(fr2, width=7, text='Info', command=infoCl)
info.pack(side=tk.LEFT, padx=2)

window.mainloop()
