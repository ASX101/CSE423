from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
import random
import math
import time
import sys

window_width = 500
window_height = 650
catcher_width = 80
catcher_height = 15
catcher_Y = 8
diamond_size = 18
initial_diamond_speed = 100  
catcher_x = window_width // 2-20 - catcher_width // 2
catcher_color = (1.0, 1.0, 1.0)
diamond_x = random.randint(0, window_width - diamond_size)
diamond_y = window_height
diamond_color = (1.0, 0.0, 0.0)
score = 0
game_over = False
paused = False
cheat_mode = False
last_time = time.time()
diamond_speed = initial_diamond_speed


BUTTON_HEIGHT = 40 
BUTTON_WIDTH = 40
BUTTON_Y = window_height - 50
restart_button = (50, BUTTON_Y)
pause_button = (window_width // 2, BUTTON_Y)
exit_button = (window_width - 90, BUTTON_Y)


def line_drawing(x0, y0, x1, y1): 
    glBegin(GL_POINTS)

    dx = x1 - x0
    dy = y1 - y0

    
    if abs(dy) <= abs(dx):  
        if x0 > x1:
            x0, y0, x1, y1 = x1, y1, x0, y0
        dx = x1 - x0
        dy = y1 - y0
        d = 2 * abs(dy) - abs(dx)
        y_step = 1 if dy >= 0 else -1
        y = y0
        for x in range(x0, x1 + 1):
            glVertex2f(x, y)
            if d > 0:
                y += y_step
                d -= 2 * abs(dx)
            d += 2 * abs(dy)
    else:  
        if y0 > y1:
            x0, y0, x1, y1 = x1, y1, x0, y0
        dx = x1 - x0
        dy = y1 - y0
        d = 2 * abs(dx) - abs(dy)
        x_step = 1 if dx >= 0 else -1
        x = x0
        for y in range(y0, y1 + 1):
            glVertex2f(x, y)
            if d > 0:
                x += x_step
                d -= 2 * abs(dy)
            d += 2 * abs(dx)

    glEnd()


def draw_polygon_outline(vertices):
    for i in range(len(vertices)):
        x1, y1 = vertices[i]
        x2, y2 = vertices[(i + 1) % len(vertices)]
        line_drawing(x1, y1, x2, y2)


def draw_diamond(x, y):
    half_size = diamond_size // 2
    
    
    vertices = [
        (x, y + half_size+4), 
        (x + half_size, y),  
        (x, y - half_size-8),  
        (x - half_size, y)   
    ]
    
    
    draw_polygon_outline(vertices)


def draw_catcher():
    glColor3f(*catcher_color)
    x = catcher_x
    y = catcher_Y
    
    
    vertices = [
        (x, y),  
        (x + catcher_width, y),  
        (x + catcher_width + 20, y + catcher_height), 
        (x - 20, y + catcher_height)  
    ]
    
    
    draw_polygon_outline(vertices)


def draw_buttons():
    glColor3f(0.0, 1.0, 1.0)  
    
    x = restart_button[0] + 10
    y = restart_button[1] + BUTTON_HEIGHT//2
    
    
    line_drawing(x, y, x + 20, y)  
    line_drawing(x, y, x + 10, y + 10) 
    line_drawing(x, y, x + 10, y - 10)  
    
   
    glColor3f(0.7, 0.6, 0.0)  
    
    if paused:
       
        line_drawing(pause_button[0] + 12, pause_button[1] + 10, 
                    pause_button[0] + 12, pause_button[1] + 30) 
        line_drawing(pause_button[0] + 12, pause_button[1] + 30, 
                    pause_button[0] + 28, pause_button[1] + 20)  
        line_drawing(pause_button[0] + 28, pause_button[1] + 20, 
                    pause_button[0] + 12, pause_button[1] + 10) 
    else:
        
        left_bar = [
            (pause_button[0] + 10, pause_button[1] + 10),
            (pause_button[0] + 18, pause_button[1] + 10),
            (pause_button[0] + 18, pause_button[1] + 30),
            (pause_button[0] + 10, pause_button[1] + 30)
        ]
        draw_polygon_outline(left_bar)
        
        right_bar = [
            (pause_button[0] + 22, pause_button[1] + 10),
            (pause_button[0] + 30, pause_button[1] + 10),
            (pause_button[0] + 30, pause_button[1] + 30),
            (pause_button[0] + 22, pause_button[1] + 30)
        ]
        draw_polygon_outline(right_bar)
    
    
    glColor3f(0.8, 0.0, 0.0)
    line_drawing(exit_button[0] + 10, exit_button[1] + 10, 
                exit_button[0] + 30, exit_button[1] + 30)
    line_drawing(exit_button[0] + 30, exit_button[1] + 10, 
                exit_button[0] + 10, exit_button[1] + 30)


def has_collided(ax, ay, aw, ah, bx, by, bw, bh): 
    return ax < bx + bw and ax + aw > bx and ay < by + bh and ay + ah > by

def update(value):
    global diamond_y, diamond_x, score, game_over, catcher_color
    global last_time, diamond_speed

    if game_over or paused:
        glutTimerFunc(16, update, 0)
        return
    
    move_catcher_to_diamond()
    current_time = time.time()
    delta = current_time - last_time
    last_time = current_time

    diamond_y -= diamond_speed * delta

    if has_collided(diamond_x, diamond_y, diamond_size, diamond_size, 
                   catcher_x, catcher_Y, catcher_width, catcher_height):
        score += 1
        print(f"Score: {score}")
        diamond_speed += 15
        generate_new_diamond()
    
    elif diamond_y < 0: 
        print(f"Game Over! Final Score: {score}")
        game_over = True
        catcher_color = (1.0, 0.0, 0.0)

    glutPostRedisplay()
    glutTimerFunc(16, update, 0)

def generate_new_diamond():
    global diamond_x, diamond_y, diamond_color
    diamond_x = random.randint(0, window_width - diamond_size)
    diamond_y = window_height
    
    while True:
        r = random.uniform(0.3, 1.0)  
        g = random.uniform(0.3, 1.0)
        b = random.uniform(0.3, 1.0)
        
       
        if (r + g + b) > 1.8:  
            diamond_color = (r, g, b)
            break

def draw_text(text, x, y):
    glColor3f(1.0, 1.0, 1.0)
    glRasterPos2f(x, y)
    for character in text:
        glutBitmapCharacter(GLUT_BITMAP_9_BY_15, ord(character))

def display():
    glClear(GL_COLOR_BUFFER_BIT)
    
    draw_buttons()
    
    if not game_over:
        glColor3f(*diamond_color)
        draw_diamond(diamond_x + diamond_size // 2, int(diamond_y))
    
    draw_catcher()
    
    
    if paused:
        draw_text("PAUSED", window_width // 2 - 30, window_height // 2)
    
    glutSwapBuffers()

def special_keys(key, x, y):
    global catcher_x
    if game_over or paused:
        return
    
    if key == GLUT_KEY_LEFT:
        catcher_x = max(10, catcher_x-20)
    elif key == GLUT_KEY_RIGHT:
        catcher_x = min(window_width - catcher_width-10, catcher_x+20)
    
    glutPostRedisplay()

def move_catcher_to_diamond():
    global catcher_x
    
    if not cheat_mode or game_over or paused:
        return
    
    diamond_center = diamond_x + diamond_size // 2
    
    
    catcher_center = catcher_x + catcher_width // 2
    
    
    move_speed = 5  
    
    if abs(diamond_center - catcher_center) > move_speed:
        if diamond_center > catcher_center:
            catcher_x = min(window_width - catcher_width, catcher_x + move_speed)
        else:
            catcher_x = max(0, catcher_x - move_speed)
    else:
       
        target_x = diamond_center - catcher_width // 2
        catcher_x = max(0, min(window_width - catcher_width, target_x))

def keyboard(key, x, y):
    global cheat_mode
    
    if key == b'c' or key == b'C':
        cheat_mode = not cheat_mode
        if cheat_mode:
            print("Cheat Mode Activated!")
        else:
            print("Cheat Mode Deactivated!")
        glutPostRedisplay()

def mouse_click(button, state, x, y):
    global game_over, catcher_color, paused, score, diamond_speed, last_time
    
    if button != GLUT_LEFT_BUTTON or state != GLUT_DOWN:
        return
    
  
    y = window_height - y
    
   
    if (restart_button[0] <= x <= restart_button[0] + BUTTON_WIDTH and  
        restart_button[1] <= y <= restart_button[1] + BUTTON_HEIGHT):
        
        print("Starting Over: Game Restarted")
        score = 0
        diamond_speed = initial_diamond_speed
        catcher_color = (1.0, 1.0, 1.0)
        game_over = False
        generate_new_diamond()
        last_time = time.time()
        glutPostRedisplay()
    
    
    elif (pause_button[0] <= x <= pause_button[0] + BUTTON_WIDTH and 
          pause_button[1] <= y <= pause_button[1] + BUTTON_HEIGHT):
        paused = not paused
        print("Game " + ("Paused" if paused else "Resumed"))
        if not paused:
            last_time = time.time()  
        glutPostRedisplay()
    
   
    elif (exit_button[0] <= x <= exit_button[0] + BUTTON_WIDTH and   
          exit_button[1] <= y <= exit_button[1] + BUTTON_HEIGHT):
        print(f"Goodbye! Final Score: {score}")
        glutLeaveMainLoop() if hasattr(GLUT, 'glutLeaveMainLoop') else sys.exit()

def init():
    glClearColor(0.0, 0.0, 0.0, 1.0)  
    gluOrtho2D(0, window_width, 0, window_height)
    glPointSize(1.5) 

def main():
    glutInit(sys.argv)
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB)
    glutInitWindowSize(window_width, window_height)
    glutInitWindowPosition(100, 100)
    glutCreateWindow(b"Let's play Catch the Diamonds")
    
    init()
    generate_new_diamond()
    
    glutDisplayFunc(display)
    glutSpecialFunc(special_keys)
    glutMouseFunc(mouse_click)
    glutKeyboardFunc(keyboard)
    last_time = time.time()
    glutTimerFunc(16, update, 0)
    
    glutMainLoop()

if __name__ == "__main__":
    main()