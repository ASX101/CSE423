from OpenGL.GL import *
from OpenGL.GLUT import *
from OpenGL.GLU import *
from OpenGL.GLUT import GLUT_BITMAP_HELVETICA_18

import math
import random
import time


game_over = False
score = 0
life = 5
bullets_missed = 0
MAX_LIFE = 5
MAX_MISSED = 10


camera_pos = [0, 500, 500]
camera_angle = 0
camera_height = 450
camera_distance = 500
first_person_mode = False


player_pos = [0, 0, 30]
player_angle = 0
gun_angle = 0
player_speed = 10
rotation_speed = 5
player_lying = False


cheat_mode = False
cheat_vision = False
last_fire_time = 0
fire_cooldown = 0.1


bullets = []
bullet_speed = 15
BULLET_SIZE = 7


enemies = []
ENEMY_COUNT = 5
enemy_speed = 0.1
enemy_size = 20
enemy_scale = [1.0] * ENEMY_COUNT
enemy_scale_direction = [1] * ENEMY_COUNT


GRID_LENGTH = 600
fovY = 120

def initialize_game():
    global game_over, score, life, bullets_missed, player_pos, gun_angle, bullets, enemies
    global player_lying, enemy_scale, enemy_scale_direction, player_angle
    
    game_over = False
    score = 0
    life = MAX_LIFE
    bullets_missed = 0
    player_lying = False
    
    player_pos = [0, 0, 100]
    gun_angle = 0
    player_angle = 0
    bullets = []
    
    enemies = []
    enemy_scale = [1.0] * ENEMY_COUNT
    enemy_scale_direction = [1] * ENEMY_COUNT
    for i in range(ENEMY_COUNT):
        spawn_enemy()

def spawn_enemy():
    min_distance = 500
    
    while True:
        side = random.randint(0, 3)
        if side == 0:
            x = random.uniform(-GRID_LENGTH + 50, GRID_LENGTH - 50)
            y = GRID_LENGTH - 50
        elif side == 1:
            x = random.uniform(-GRID_LENGTH + 50, GRID_LENGTH - 50)
            y = -GRID_LENGTH + 50
        elif side == 2:
            x = -GRID_LENGTH + 50
            y = random.uniform(-GRID_LENGTH + 50, GRID_LENGTH - 50)
        else:
            x = GRID_LENGTH - 50
            y = random.uniform(-GRID_LENGTH + 50, GRID_LENGTH - 50)
        
        dx = x - player_pos[0]
        dy = y - player_pos[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance >= min_distance:
            enemies.append([x, y, 30])
            break

def update_enemies():
    global enemies, life, game_over, score, player_lying
    
    for i, enemy in enumerate(enemies[:]):
        
        enemy_scale[i] += 0.02 * enemy_scale_direction[i]
        if enemy_scale[i] >= 1.3:
            enemy_scale_direction[i] = -1
        elif enemy_scale[i] <= 0.7:
            enemy_scale_direction[i] = 1
        
        
        dx = player_pos[0] - enemy[0]
        dy = player_pos[1] - enemy[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance > 0:
            enemy[0] += (dx / distance) * enemy_speed
            enemy[1] += (dy / distance) * enemy_speed
        
       
        if distance < enemy_size * enemy_scale[i] + 30 and not game_over:
            life -= 1
            print("Remaining Player Life :", life)
            if enemy in enemies:
                idx = enemies.index(enemy)
                enemies.remove(enemy)
                spawn_enemy()
            
            if life <= 0:
                game_over = True
                player_lying = True
            break

def check_bullet_enemy_collision():
    global bullets, enemies, score
    
    for bullet in bullets[:]:
        for i, enemy in enumerate(enemies[:]):
            dx = bullet[0] - enemy[0]
            dy = bullet[1] - enemy[1]
            distance = math.sqrt(dx*dx + dy*dy)
            
            if distance < enemy_size * enemy_scale[i] + BULLET_SIZE:
                
                if bullet in bullets:
                    bullets.remove(bullet)
                if enemy in enemies:
                    enemies.remove(enemy)
                    spawn_enemy()
                score += 1
                break

def update_bullets():
    global bullets, bullets_missed, game_over, player_lying
    
    for bullet in bullets[:]:
        angle_rad = math.radians(bullet[3])
        bullet[0] += bullet_speed * math.cos(angle_rad)
        bullet[1] += bullet_speed * math.sin(angle_rad)
        
        if abs(bullet[0]) > GRID_LENGTH or abs(bullet[1]) > GRID_LENGTH:
            if bullet in bullets:
                bullets.remove(bullet)
            bullets_missed += 1
            print("Bullet missed:", bullets_missed)
            
            if bullets_missed >= MAX_MISSED and not game_over:
                game_over = True
                player_lying = True

def fire_bullet():
    global bullets, last_fire_time

    current_time = time.time()
    if current_time - last_fire_time < fire_cooldown:
        return

    if not game_over:
        angle_rad = math.radians(player_angle)
        offset = 40
        bullet_x = player_pos[0] + offset * math.cos(angle_rad)
        bullet_y = player_pos[1] + offset * math.sin(angle_rad)
        bullets.append([bullet_x, bullet_y, 50, player_angle])
        last_fire_time = current_time
        print("Player Bullet Fired!")

def find_nearest_enemy_in_sight():
    nearest_enemy = None
    min_distance = float('inf')
    
    for enemy in enemies:
        dx = enemy[0] - player_pos[0]
        dy = enemy[1] - player_pos[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        angle_to_enemy = math.degrees(math.atan2(dy, dx))
        angle_diff = abs((angle_to_enemy - gun_angle + 180) % 360 - 180)
        
        if angle_diff < 45 and distance < min_distance:
            min_distance = distance
            nearest_enemy = enemy
    
    return nearest_enemy

def cheat_mode_update():
    global gun_angle, player_angle

    nearest_enemy = None
    min_distance = float('inf')
    
    for enemy in enemies:
        dx = enemy[0] - player_pos[0]
        dy = enemy[1] - player_pos[1]
        distance = math.sqrt(dx*dx + dy*dy)
        
        if distance < min_distance:
            min_distance = distance
            nearest_enemy = enemy
    
    if not nearest_enemy:
        return

    dx = nearest_enemy[0] - player_pos[0]
    dy = nearest_enemy[1] - player_pos[1]
    target_angle = math.degrees(math.atan2(dy, dx))

    angle_diff = (target_angle - gun_angle + 180) % 360 - 180

   
    if abs(angle_diff) > 3:
        turn_speed = min(rotation_speed * 0.8, abs(angle_diff) * 0.1)
        gun_angle += turn_speed * (1 if angle_diff > 0 else -1)
        player_angle = gun_angle
    else:
        gun_angle = target_angle
        player_angle = gun_angle
        fire_bullet()

def draw_text(x, y, text, font=GLUT_BITMAP_HELVETICA_18):
    glColor3f(1, 1, 1)
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluOrtho2D(0, 1000, 0, 800)
    
    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()
    
    glRasterPos2f(x, y)
    for ch in text:
        glutBitmapCharacter(font, ord(ch))
    
    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)

def draw_grid():
    glBegin(GL_QUADS)
    
    tile_size = GRID_LENGTH / 10
    for i in range(20):
        for j in range(20):
            x = -GRID_LENGTH + i * tile_size
            y = -GRID_LENGTH + j * tile_size
            
            if (i + j) % 2 == 0:
                glColor3f(1, 1, 1)
            else:
                glColor3f(0.7, 0.5, 0.95)
            
            glVertex3f(x, y, 0)
            glVertex3f(x + tile_size, y, 0)
            glVertex3f(x + tile_size, y + tile_size, 0)
            glVertex3f(x, y + tile_size, 0)
    
    glEnd()
    
    boundary_height = 150
    
    glBegin(GL_QUADS)
    glColor3f(0, 1, 1)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, boundary_height)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, boundary_height)
    glEnd()
    
    glBegin(GL_QUADS)
    glColor3f(1, 1, 1)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, boundary_height)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, boundary_height)
    glEnd()
    
    glBegin(GL_QUADS)
    glColor3f(0, 1, 0)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, GRID_LENGTH, boundary_height)
    glVertex3f(-GRID_LENGTH, GRID_LENGTH, boundary_height)
    glEnd()
    
    glBegin(GL_QUADS)
    glColor3f(0, 0, 1)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, 0)
    glVertex3f(GRID_LENGTH, -GRID_LENGTH, boundary_height)
    glVertex3f(-GRID_LENGTH, -GRID_LENGTH, boundary_height)
    glEnd()
    
def draw_cylinder(radius, height, slices=20, stacks=15):
    quad = gluNewQuadric()
    gluCylinder(quad, radius, radius, height, slices, stacks)
    gluDeleteQuadric(quad)


def draw_player():
    glPushMatrix()
    glTranslatef(player_pos[0], player_pos[1], 0)
    if game_over:
        glTranslatef(0, 0, 10)   
        glRotatef(-90, 0, 1, 0)
    else:
        glRotatef(player_angle, 0, 0, 1)

    glColor3f(0.5, 0.5, 0.0)
    glPushMatrix()
    glTranslatef(0, 0, 70)
    glScalef(20, 40, 40)
    glutSolidCube(1)
    glPopMatrix()

    glColor3f(0, 0, 0)
    glPushMatrix()
    glTranslatef(0, 0, 110)
    glutSolidSphere(15, 15, 16)
    glPopMatrix()

    glColor3f(0.0, 0.0, 1.0)
    for x in [-10, 10]:
        glPushMatrix()
        glTranslatef(0, x, 50)
        glRotatef(180, 1, 0, 0)
        draw_cylinder(10, 50, 5, 10)
        glPopMatrix()

    glColor3f(1.0, 0.8, 0.6)
    for x in [-15, 15]:
        glPushMatrix()
        glTranslatef(10, x, 90)
        glRotatef(90, 0, 1, 0)
        draw_cylinder(5, 35)
        glPopMatrix()

    glColor3f(0.3, 0.3, 0.3)
    glPushMatrix()
    if game_over:
        glTranslatef(0, 0, 90)
        glRotatef(-90, 0, 0, 1)  
        glRotatef(-90, 1, 0, 0)  
    else:
        glTranslatef(0, 0, 90)
        glRotatef(90, 0, 1, 0)  
    draw_cylinder(5, 60)
    glPopMatrix()
    glPopMatrix()
    

def draw_fp_hands():
    glMatrixMode(GL_PROJECTION)
    glPushMatrix()
    glLoadIdentity()
    gluPerspective(60, 1.25, 0.01, 50)

    glMatrixMode(GL_MODELVIEW)
    glPushMatrix()
    glLoadIdentity()

   
    glClear(GL_DEPTH_BUFFER_BIT)

    quad = gluNewQuadric()

    base_z = -10.0
    y_offset = -3.5

    
    glColor3f(0.35, 0.35, 0.35)
    glPushMatrix()
    glTranslatef(0.0, y_offset, base_z)
    gluCylinder(quad, 0.8, 0.8, 18, 20, 20)
    glPopMatrix()

    
    glColor3f(0.95, 0.75, 0.6)

   
    glPushMatrix()
    glTranslatef(-2.4, y_offset, base_z)
    gluCylinder(quad, 0.7, 0.7, 6.0, 20, 20)
    glPopMatrix()

    
    glPushMatrix()
    glTranslatef(2.4, y_offset, base_z)
    gluCylinder(quad, 0.7, 0.7, 6.0, 20, 20)
    glPopMatrix()

    glPopMatrix()
    glMatrixMode(GL_PROJECTION)
    glPopMatrix()
    glMatrixMode(GL_MODELVIEW)


def draw_bullets():
    for bullet in bullets:
        glPushMatrix()
        glColor3f(1, 0, 0)
        glTranslatef(bullet[0], bullet[1], bullet[2])
        glutSolidSphere(BULLET_SIZE, 15, 15)
        glPopMatrix()

def draw_enemies():
    for i, enemy in enumerate(enemies):
        glPushMatrix()
        glTranslatef(enemy[0], enemy[1], enemy[2])
        
        glColor3f(0.8, 0.1, 0.1)
        glPushMatrix()
        glScalef(enemy_scale[i], enemy_scale[i], enemy_scale[i])
        gluSphere(gluNewQuadric(), 17, 10, 10)
        glPopMatrix()
        
        glColor3f(0.0, 0.0, 0.)
        glTranslatef(0, 0, 25)
        glPushMatrix()
        glScalef(enemy_scale[i], enemy_scale[i], enemy_scale[i])
        gluSphere(gluNewQuadric(), 10, 10, 10)
        glPopMatrix()
        
        glPopMatrix()

def keyboardListener(key, x, y):
    global player_pos, gun_angle, cheat_mode, cheat_vision, game_over, player_angle
    
    if game_over and key == b'r':
        initialize_game()
        return
    
    if game_over:
        return
    
    if key == b'w':
        new_x = player_pos[0] + player_speed * math.cos(math.radians(player_angle))
        new_y = player_pos[1] + player_speed * math.sin(math.radians(player_angle))
        
        if abs(new_x) < GRID_LENGTH - 30 and abs(new_y) < GRID_LENGTH - 30:
            player_pos[0] = new_x
            player_pos[1] = new_y
    
    if key == b's':
        new_x = player_pos[0] - player_speed * math.cos(math.radians(player_angle))
        new_y = player_pos[1] - player_speed * math.sin(math.radians(player_angle))
        
        if abs(new_x) < GRID_LENGTH - 30 and abs(new_y) < GRID_LENGTH - 30:
            player_pos[0] = new_x
            player_pos[1] = new_y
    
    if key == b'a' and not cheat_mode:
        player_angle += rotation_speed
        gun_angle += rotation_speed
    
    if key == b'd' and not cheat_mode:
        player_angle -= rotation_speed
        gun_angle -= rotation_speed
    
    if key == b'c':
        cheat_mode = not cheat_mode
    
    if key == b'v':
        cheat_vision = not cheat_vision

def specialKeyListener(key, x, y):
    global camera_angle, camera_height
    
    if key == GLUT_KEY_UP:
        camera_height += 20
        if camera_height > 1000:
            camera_height = 1000
    
    if key == GLUT_KEY_DOWN:
        camera_height -= 20
        if camera_height < 100:
            camera_height = 100
    
    if key == GLUT_KEY_LEFT:
        camera_angle += 5
    
    if key == GLUT_KEY_RIGHT:
        camera_angle -= 5

def mouseListener(button, state, x, y):
    global first_person_mode
    
    if game_over:
        return
    
    if button == GLUT_LEFT_BUTTON and state == GLUT_DOWN:
        fire_bullet()
    
    if button == GLUT_RIGHT_BUTTON and state == GLUT_DOWN:
        first_person_mode = not first_person_mode

def setupCamera():
    global first_person_mode, cheat_vision, cheat_mode
    
    glMatrixMode(GL_PROJECTION)
    glLoadIdentity()
    gluPerspective(fovY, 1.25, 0.1, 2000)
    glMatrixMode(GL_MODELVIEW)
    glLoadIdentity()
    
    if first_person_mode:
        cam_x = player_pos[0]
        cam_y = player_pos[1]
        cam_z = 90
        
        look_distance = 500
        look_x = player_pos[0] + look_distance * math.cos(math.radians(gun_angle))
        look_y = player_pos[1] + look_distance * math.sin(math.radians(gun_angle))
        look_z = 90
        
        gluLookAt(cam_x, cam_y, cam_z, look_x, look_y, look_z, 0, 0, 1)
    else:
        angle_rad = math.radians(camera_angle)
        cam_x = camera_distance * math.cos(angle_rad)
        cam_y = camera_distance * math.sin(angle_rad)
        cam_z = camera_height
        
        gluLookAt(cam_x, cam_y, cam_z, 0, 0, 0, 0, 0, 1)

def idle():
    if not game_over:
        update_bullets()
        check_bullet_enemy_collision()
        update_enemies()
        
        if cheat_mode:
            cheat_mode_update()
    
    glutPostRedisplay()

def showScreen():
    glClear(GL_COLOR_BUFFER_BIT | GL_DEPTH_BUFFER_BIT)
    glLoadIdentity()
    glViewport(0, 0, 1000, 800)
    
    setupCamera()
    
    draw_grid()
    if not first_person_mode:
        draw_player()

    draw_bullets()
    draw_enemies()
    
    
    if first_person_mode:
        draw_fp_hands()
    
    draw_text(10, 770, f"Player Life Remaining: {life}")
    draw_text(10, 740, f"Game Score: {score}")
    draw_text(10, 710, f"Player Bullet Missed: {bullets_missed}")
    
    if game_over:
        draw_text(355, 600, "GAME OVER! Press R to Restart", GLUT_BITMAP_HELVETICA_18)
    
    glutSwapBuffers()



def main():
    initialize_game()
    
    glutInit()
    glutInitDisplayMode(GLUT_DOUBLE | GLUT_RGB | GLUT_DEPTH)
    glutInitWindowSize(1000, 800)
    glutInitWindowPosition(0, 0)
    wind = glutCreateWindow(b"21301634_Asrar Azim - Bullet Frenzy - 3D Game")
    
    glEnable(GL_DEPTH_TEST)
    glClearColor(0, 0, 0, 1)
    
    glutDisplayFunc(showScreen)
    glutKeyboardFunc(keyboardListener)
    glutSpecialFunc(specialKeyListener)
    glutMouseFunc(mouseListener)
    glutIdleFunc(idle)
    
    glutMainLoop()

if __name__ == "__main__":
    main()