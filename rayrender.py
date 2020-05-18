# Modules used
import pygame as pg
import math
import random

# Main loop set to true
loop = True

# Initalize pygame
pg.init()

# Set field of view
fov = 60

# Set width of world for Eyeball to move around
worldWidth = 500

# Set width and height of entire window, will be used up in rendering
winWidth = worldWidth
winHeight = 1000
# Adjust winWidth according to field of view to avoid gaps in walls
while winWidth % fov > 0:
    if fov % 10 == 0:
        winWidth += 10
    elif fov % 5 == 0:
        winWidth += 5
    else:
        winWidth = worldWidth
        break

# Create game screen with dimensions
win = pg.display.set_mode((winWidth, winHeight))

# Location of render area
scenex = 0
sceney = winHeight // 2

# List of all walls that can be seen
walls = []

# Create pygame clock to manage frame rate
clock = pg.time.Clock()

# Scene list used to list wall chunk locations
scene = []

# Function to map one range of values to another
def mapping(value, oldMin, oldMax, newMin, newMax):
    oldScaled = oldMax - oldMin
    newScaled = newMax - newMin
    valueScaled = float(value-oldMin) / float(oldScaled)
    return newMin + (valueScaled * newScaled)

# Get distance between two points
def distance(p1, p2):
    deltx = p2[0] - p1[0]
    delty = p2[1] - p1[1]
    return math.sqrt(deltx**2 + delty**2)

# Update the screen
def update():
    global scene
    pg.display.update()
    scene = []
    win.fill((0,0,0))

# Class for creating walls to be rendered on screen
class Wall:
    def __init__(self, sx, sy, ex, ey):
        self.sx = sx
        self.sy = sy
        self.ex = ex
        self.ey = ey
    def draw(self):
        pg.draw.line(win, pg.Color("Red"), (self.sx, self.sy), (self.ex, self.ey), 3)

# Class for rays to be traced on screen
class Ray:
    # Constructor
    def __init__(self, n, origin):
        # Set degree of angle
        self.n = n
        # Convert angle to radians
        self.angle = math.radians(self.n)
        # Keep starting point of rays at the center of the Eyeball
        self.sx = origin.x
        self.sy = origin.y
        # Use angle to point ray in the correct direction
        self.x = math.cos(self.angle)
        self.y = math.sin(self.angle)
        # Calculate end point of the ray
        self.ex = self.sx + self.x
        self.ey = self.sy - self.y

    # Draw the ray
    def draw(self):
        # Restate angle variable in case degree has changed
        self.angle = math.radians(self.n)
        self.x = math.cos(self.angle)
        self.y = math.sin(self.angle)
        # Render the ray
        pg.draw.line(win, (pg.Color("White")), (self.sx, self.sy), (int(self.ex), int(self.ey)), 1)

    # Check for an intersection between the ray and the walls
    def check(self):
        # Points list used to determine the closest wall
        points = []
        x3 = self.sx
        y3 = self.sy
        x4 = self.sx + self.x
        y4 = self.sy - self.y
        # Check each wall
        for i in walls:
            x1 = i.sx
            y1 = i.sy
            x2 = i.ex
            y2 = i.ey

            den = (x1-x2) * (y3 - y4) - (y1-y2) * (x3-x4)
            # Continue to other walls if lines are parallel
            if den == 0:
                continue

            t = float(((x1 - x3) * (y3-y4) - (y1 - y3) * (x3 - x4)) / den)
            u = 0 - float(((x1 - x2) * (y1-y3) - (y1 - y2) * (x1 - x3)) / den)

            # Find point of intersection and append to the list of points
            if t > 0 and t < 1 and u > 0:
                ptx = x1 + t * (x2 - x1)
                pty = y1 + t * (y2 - y1)
                points.append((ptx, pty))
            # Continue to other walls if there is no intersection
            else:
                continue
        # Ignore walls if there is no points of intersection
        if len(points) <= 0:
            return False
        # Return the points list for determining closest wall
        else:
            return points

# Class for the eyeball object
class Glow:
    # Constructor
    def __init__(self, x, y):
        self.x = x
        self.y = y
        # Set the amount of rays to the fov
        self.rayCount = fov
        # Create a list of all rays attached to Eyeball
        self.rays = []
        # Create ray objects and pass their fov number as their angle
        for i in range(self.rayCount):
            self.rays.append(Ray(i-1, self))

    # Check for ray collisions and draw them
    def draw(self):
        for i in self.rays:
            # Get points of intersection
            points = i.check()
            # If no walls are found, each ray will have a length of their angle
            if not points:
                i.ex = i.sx + i.x
                i.ey = i.sy - i.y
            # Check for closest wall
            elif points:
                score = 10000
                for j in points:
                    dis = distance((i.sx, i.sy), j)
                    score = min(dis, score)
                for j in points:
                    if distance((i.sx, i.sy), j) == score:
                        i.ex, i.ey = j
                        scene.append(score)
                        break
            i.draw()

    # Move the eyeball
    def move(self, x, y):
        self.x = x
        self.y = y
        for i in self.rays:
            i.sx = x
            i.sy = y
    # Check for keyboard input to move and rotate the eyeball
    def checkInput(self):
        if keys[pg.K_LEFT]:
            for i in self.rays:
                i.n += 1
        if keys[pg.K_RIGHT]:
            for i in self.rays:
                i.n -= 1
        if keys[pg.K_w] and self.y >= 1:
            self.y -= 1
        if keys[pg.K_s] and self.y <= winHeight//2 - 1:
            self.y += 1
        if keys[pg.K_a] and self.x >= 1:
            self.x -= 1
        if keys[pg.K_d] and self.x <= worldWidth - 1:
            self.x += 1
        self.move(self.x, self.y)

        # Use the eyeball to render a 3D environment at the bottom of the screen
    def render(self):
        # Create width of each wall chunk
        width = winWidth / len(scene)
        # Find center of window
        center = sceney + (sceney/2)

        for i in range(len(scene)):
            # Create a color that darkens with distance
            j = mapping(scene[i]**2, 0, winWidth**2, 255, 0)
            # Make sure color fits within range
            if j < 0:
                j = 0
            # Make sure distance fits within range
            if scene[i] <= winWidth:
                distance = scene[i]
            else:
                distance = winWidth
            # Calculate height that fits within render window
            height = mapping(distance, 0, winWidth, sceney, 0)
            # Render the rectangles to make 3D environment
            pg.draw.rect(win, ((j, j, j)), (winWidth-i*width, center, width, height/2))
            pg.draw.rect(win, ((j, j, j)), (winWidth-i*width, center-height/2 +1, width, height/2))

# Create eyeball object
eyeball = Glow(250, 250)

# Create border walls
walls.append(Wall(0, 0, 0, winHeight//2))
walls.append(Wall(0, 0, worldWidth, 0))
walls.append(Wall(worldWidth, 0, worldWidth, winHeight//2))
walls.append(Wall(0, winHeight//2, worldWidth, winHeight//2))

# Create 4 random walls
for i in range(4):
    sx = random.choice(range(50, worldWidth-50))
    sy = random.choice(range(50, winHeight//2-50))
    ex = random.choice(range(50, worldWidth-50))
    ey = random.choice(range(50, winHeight//2-50))
    walls.append(Wall(sx, sy, ex, ey))

# Main loop
while loop:
    # Get key strokes
    keys = pg.key.get_pressed()

    # Check for exit
    for event in pg.event.get():
        if event.type == pg.QUIT:
            loop = False

        # Check for mouse input
        elif event.type == pg.MOUSEMOTION:
            pos = pg.mouse.get_pos()
            if pos[1] <= winHeight//2 and pos[0] <= worldWidth:
                eyeball.move(pos[0], pos[1])

    # Call appropriate functions
    eyeball.checkInput()
    eyeball.draw()
    eyeball.render()

    # Set framerate
    clock.tick(60)

    # Draw walls
    for i in walls:
        i.draw()

    # Update the screen
    update()
