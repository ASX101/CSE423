from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import time

class point:
    def __init__(self):
        self.x=0
        self.y=0
        self.z=0
        
Width_window, Height_window = 500, 500
ball_x , ball_y = 0, 0
speed = 0.005
ball_size = 5

ball_property = []
ball_movement = [(-1, 1), (-1, -1), (1, 1), (1, -1)]
ball_color = []

freeze = False
freeze_counter = 1
is_blinking = False  
blink_start_time = 0  
blink_duration = 0.45  

def convert_coordinate(x, y):
    global Width_window, Height_window
    a = x - (Width_window / 2)
    b = (Height_window / 2) - y
    return a, b

def draw_points(arr, s):
    glPointSize(s)
    for x2, y2, r, g, b, x, y in arr:
        glBegin(GL_POINTS)
        glColor3f(r, g, b)
        glVertex2f(x2, y2)
        
        glEnd()

def rgb():
    r = random.random()
    g = random.random()
    b = random.random()
    return r, g, b
        
def keyboardListener(key, x, y):
    global freeze, freeze_counter
    if not freeze:
        
        if key == b' ':
            freeze = True
            print("Balls Freeze")
            freeze_counter += 1
    else:
        if key == b' ':
            freeze = False
            print("Balls Resume")
            freeze_counter += 1
    glutPostRedisplay()
    
def specialKeyListener(key, x, y):
    global speed, freeze
    if not freeze:
        if key == GLUT_KEY_UP:
            speed *= 2
            print("Speed Increased")
        if key == GLUT_KEY_DOWN:
            speed /= 2
            print("Speed Decreased")
    glutPostRedisplay()
    
def mouseListener(button, state, x, y):
    global ball_x, ball_y, ball_property, ball_color, ball_movement, is_blinking, blink_start_time
    if not freeze:
        if button == GLUT_RIGHT_BUTTON:
            if state == GLUT_DOWN:
                ball_x, ball_y = convert_coordinate(x, y)
                x1, y1 = random.choice(ball_movement)
                r, g, b = rgb()
                ball_property.append([ball_x, ball_y, x1, y1, r, g, b])
                ball_color.append([r, g, b])
                print('spawned')
        if button == GLUT_LEFT_BUTTON:
            if state == GLUT_DOWN:
                is_blinking = True
                blink_start_time = time.time()
                print("Blinking started")

    glutPostRedisplay()
    

def animate():
    global ball_property, speed, freeze, is_blinking, blink_start_time, blink_duration

    if not freeze:
        current_time = time.time()

        for i in range(len(ball_property)):
            x, y, r, g, b, x1, y1 = ball_property[i]
            x += x1 * speed
            y += y1 * speed

            
            if x < (-Width_window / 2) or x > (Width_window / 2):
                x1 = -x1
            if y < (-Height_window / 2) or y > (Height_window / 2):
                y1 = -y1

            
            if is_blinking and current_time - blink_start_time <= blink_duration:
                r, g, b = 0, 0, 0  
            else:
                is_blinking = False  
                r, g, b = ball_color[i]  

            ball_property[i] = [x, y, r, g, b, x1, y1]
    glutPostRedisplay()
    
def display():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glClearColor(0, 0, 0, 0) 
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    gluLookAt(0, 0, 200, 0, 0, 0, 0, 1, 0)
    global ball_x, ball_y, ball_size, ball_property
    draw_points(ball_property, ball_size)
    glutSwapBuffers()

def init():
    glClearColor(0, 0, 0, 0)
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(104, 1, 1, 1000.0)

def main():
    glutInit()
    glutInitDisplayMode(GLUT_RGBA)
    glutInitWindowSize(500, 500)
    glutInitWindowPosition(250, 0)
    glutInitDisplayMode(GLUT_DEPTH | GLUT_DOUBLE | GLUT_RGB)
    glutCreateWindow(b"AmazingBox_task-2")
    init()
    glutDisplayFunc(display)
    glutIdleFunc(animate)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutMainLoop()

if __name__ == "__main__":
    main()