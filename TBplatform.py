import tkinter as tk
import numpy as np

PLATFORM_X0 = 0
PLATFORM_Y0 = 0
ANGLE_X0 = 2.5 # positive means clockwise
ANGLE_Y0 = 2.5 # positive means tail up

Info = """

How to use this:

  **Reset and Center**: When you click the "Reset and Center" button, the four values you set (from left to right: x0, y0, angle_x0, and angle_y0) will be applied as the initial positiono of the platform and orientation of the detector. The calorimeter will always be adjusted to center the beam spot on the central tower.

  **Movement and Rotation**: Use the 8 buttons to move the platform and adjust the calorimeter rotation.

  **Beam Spot Tracking**: As you move or rotate the calorimeter, the beam spot will shift accordingly. The new coordinates of the beam spot, relative to the cross-section of the calorimeter, will be displayed in real-time.
"""

def cosdeg(x):
    return np.cos(np.deg2rad(x))
def sindeg(x):
    return np.sin(np.deg2rad(x))

def getModCoo(x,y,facex,facey,opt='string'):
    print(x,y,facex,facey)
    
    xD = 384 - (facex/2-x) * 384/facex  #coordinate from bottom-left corner
    yD = 338.4 - (facey/2-y) * 338.4/facey  #coordinate from bottom-left corner

    col = int(xD / (384/3))  # from 0
    row = int(yD / (338.4/12)) # from 0

    xm = xD-(col*384/3) - 0.5*(384/3)
    ym = yD-(row*338.4/12) - 0.5*(338.4/12)

    if opt=='string':
        return f"Module ({col+1},{row+1}) position ({round(xm,3)},{round(ym,3)})"
    else:
        return col+1, row+1, xm, ym

    
    


class RectangleMoverApp:
    def __init__(self, root):
        self.root = root
        self.root.title("DRAGO mover")

        # Canvas dimensions
        self.canvas_width = 1000
        self.canvas_height = 700
        
        # Rectangle dimensions
        self.face_width = 384 * cosdeg(PLATFORM_X0)
        self.face_height = 338.4 * cosdeg(PLATFORM_Y0)
        self.face_length = 2500
        
        # Tower matrix dimensions
        self.rows = 12
        self.cols = 3

        # Initial platform position
        self.plat_x = PLATFORM_X0
        self.plat_y = PLATFORM_Y0
        
        # Initial position of the calo face
        self.face_x = self.canvas_width // 2 
        self.face_y = self.canvas_height // 2 + int(self.face_height/(12*2))

        # Angle position
        self.angle_x = ANGLE_X0
        self.angle_y = ANGLE_Y0
        
        # Red dot's initial position (center of the original rectangle)
        self.beam_spot_x = self.canvas_width // 2
        self.beam_spot_y = self.canvas_height // 2
        
        # Create a canvas
        self.canvas = tk.Canvas(root, width=self.canvas_width, height=self.canvas_height, bg='white')
        self.canvas.pack()
        
        # Draw initial rectangle and red dot
        self.draw_rectangle()
        self.draw_beam_spot()
        
        # Display coordinates
        self.plat_label = tk.Label(root, text=f"Platform setting: ({self.plat_x},{self.plat_y}) mm. Angle: ({self.angle_x,self.angle_y}) deg")
        self.spot_label = tk.Label(root, text=f"Resulting in beam hitting at ({-self.beam_spot_x+self.face_x},{-self.beam_spot_y+self.face_y}) mm")
        self.spot_mod_label = tk.Label(root, text=getModCoo(-self.beam_spot_x+self.face_x, -self.beam_spot_y+self.face_y, self.face_width, self.face_height))
        self.plat_label.pack()
        self.spot_label.pack()
        self.spot_mod_label.pack()

        # Variable to track if "20x" is checked
        self.ten_x = tk.BooleanVar(value=False)
        
        
        # Create buttons
        self.create_buttons()
        
    
    def draw_rectangle(self):
        self.canvas.delete("rectangle")
        # Draw the rectangle divided into a matrix of smaller rectangles
        small_rect_width = self.face_width / self.cols
        small_rect_height = self.face_height / self.rows
        
        for i in range(self.rows):
            for j in range(self.cols):
                x1 = self.face_x - self.face_width / 2 + j * small_rect_width
                y1 = self.face_y - self.face_height / 2 + i * small_rect_height
                x2 = x1 + small_rect_width
                y2 = y1 + small_rect_height
                color = "lightyellow" if (i==5 and j==1) else "lightblue"
                self.canvas.create_rectangle(x1, y1, x2, y2, outline="black", fill=color, tags="rectangle")
    
    def draw_beam_spot(self):
        self.canvas.delete("beam_spot")
        # Red dot's position is fixed at the center of the initial rectangle position
        self.canvas.create_oval(
            self.beam_spot_x - 3, self.beam_spot_y - 3,
            self.beam_spot_x + 3, self.beam_spot_y + 3,
            outline="red", fill="red", tags="beam_spot"
        )
    
    def update_position(self):
        self.face_x = self.canvas_width // 2 + (self.plat_x - PLATFORM_X0) - 0.5*self.face_length*sindeg(self.angle_x) + 0.5*self.face_length*sindeg(ANGLE_X0)
        self.face_y = self.canvas_height // 2 + self.face_height // 24 - (self.plat_y - PLATFORM_Y0) + 0.5*self.face_length*sindeg(self.angle_y) - 0.5*self.face_length*sindeg(ANGLE_Y0)
        self.face_width = 384 * cosdeg(self.angle_x)
        self.face_height = 338.4 * cosdeg(self.angle_y)
        self.draw_rectangle()
        self.draw_beam_spot()
        self.plat_label.config(text=f"Platform setting: ({round(self.plat_x,3)},{round(self.plat_y,3)}) mm. Angle: ({round(self.angle_x,3),round(self.angle_y,3)}) deg")
        self.spot_label.config(text=f"Resulting in beam hitting at ({round(self.beam_spot_x-self.face_x,3)},{round(-self.beam_spot_y+self.face_y,3)}) mm")
        self.spot_mod_label.config(text=getModCoo(self.beam_spot_x-self.face_x,-self.beam_spot_y+self.face_y,self.face_width,self.face_height))
       
        
    
    def create_buttons(self):
        button_frame = tk.Frame(self.root)
        button_frame.pack()

        # Entry fields for PLATFORM_X0, PLATFORM_Y0, ANGLE_X0, ANGLE_Y0
        self.entry_plat_x0 = tk.Entry(button_frame, width=10)
        self.entry_plat_y0 = tk.Entry(button_frame, width=10)
        self.entry_angle_x0 = tk.Entry(button_frame, width=10)
        self.entry_angle_y0 = tk.Entry(button_frame, width=10)
        
        self.entry_plat_x0.insert(0, str(PLATFORM_X0))
        self.entry_plat_y0.insert(0, str(PLATFORM_Y0))
        self.entry_angle_x0.insert(0, str(ANGLE_X0))
        self.entry_angle_y0.insert(0, str(ANGLE_Y0))
        
        self.entry_plat_x0.grid(row=0, column=1, padx=5, pady=5)
        self.entry_plat_y0.grid(row=0, column=2, padx=5, pady=5)
        self.entry_angle_x0.grid(row=0, column=3, padx=5, pady=5)
        self.entry_angle_y0.grid(row=0, column=4, padx=5, pady=5)

        # Create "20x" checkbox
        tk.Checkbutton(button_frame, text="20x", variable=self.ten_x).grid(row=2, column=4, padx=5, pady=5)
        
        # Create buttons for moving the rectangle
        tk.Button(button_frame, text="Reset and center", command=self.recenter).grid(row=0, column=0, padx=5, pady=5)
        tk.Button(button_frame, text="Up", command=self.move_up).grid(row=1, column=0, padx=5, pady=5)
        tk.Button(button_frame, text="Down", command=self.move_down).grid(row=1, column=1, padx=5, pady=5)
        tk.Button(button_frame, text="Left", command=self.move_left).grid(row=1, column=2, padx=5, pady=5)
        tk.Button(button_frame, text="Right", command=self.move_right).grid(row=1, column=3, padx=5, pady=5)

        tk.Button(button_frame, text="Clock", command=self.rotate_right).grid(row=2, column=0, padx=5, pady=5)
        tk.Button(button_frame, text="Countclk", command=self.rotate_left).grid(row=2, column=1, padx=5, pady=5)
        tk.Button(button_frame, text="Tail up", command=self.rotate_tailup).grid(row=2, column=2, padx=5, pady=5)
        tk.Button(button_frame, text="Tail down", command=self.rotate_taildown).grid(row=2, column=3, padx=5, pady=5)

        
        
        #tk.Button(button_frame, text="Up", command=self.move_up).pack(side=tk.LEFT)
        #tk.Button(button_frame, text="Down", command=self.move_down).pack(side=tk.LEFT)
        #tk.Button(button_frame, text="Left", command=self.move_left).pack(side=tk.LEFT)
        #tk.Button(button_frame, text="Right", command=self.move_right).pack(side=tk.LEFT)
        
    def recenter(self):
        global PLATFORM_X0, PLATFORM_Y0, ANGLE_X0, ANGLE_Y0

        # Update global variables with the values from the entry fields
        PLATFORM_X0 = float(self.entry_plat_x0.get())
        PLATFORM_Y0 = float(self.entry_plat_y0.get())
        ANGLE_X0 = float(self.entry_angle_x0.get())
        ANGLE_Y0 = float(self.entry_angle_y0.get())
        self.plat_x = PLATFORM_X0
        self.plat_y = PLATFORM_Y0
        self.angle_x = ANGLE_X0
        self.angle_y = ANGLE_Y0
        self.face_width = 384 * cosdeg(self.angle_x)
        self.face_height = 338.4 * cosdeg(self.angle_y)
        self.beam_spot_x = self.canvas_width // 2
        self.beam_spot_y = self.canvas_height // 2
        
        self.update_position()

    def get_20x(self):
        return 20 if self.ten_x.get() else 1
    
    def move_up(self):
        self.plat_y += .1*self.get_20x()
        self.update_position()
    
    def move_down(self):
        self.plat_y -= .1*self.get_20x()
        self.update_position()
    
    def move_left(self):
        self.plat_x -= .2*self.get_20x()
        self.update_position()
    
    def move_right(self):
        self.plat_x += .2*self.get_20x()
        self.update_position()

    def rotate_right(self):
        self.angle_x += .1*self.get_20x()
        self.update_position()

    def rotate_left(self):
        self.angle_x -= .1*self.get_20x()
        self.update_position()

    def rotate_tailup(self):
        self.angle_y += .1*self.get_20x()
        self.update_position()

    def rotate_taildown(self):
        self.angle_y -= .1*self.get_20x()
        self.update_position()


    
        


# Create the main window
print(Info)
print("Press Enter to enjoy")
input()
print("Experiment with larger angles for the rotation. You'll observe the fascinating effect of the calorimeter face gradually shrinking as the angle increases!")
print("Press Enter to enjoy (really)")
input()
root = tk.Tk()
app = RectangleMoverApp(root)
app.update_position()
root.mainloop()
