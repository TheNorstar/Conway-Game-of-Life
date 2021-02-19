import pygame
import sys
import random
import math
from copy import deepcopy
from time import sleep

WIDTH = 800
HEIGHT = 600

FPS = 60
COLOR_BLACK = (0, 0, 0)
COLOR_RED = (255, 0, 0)

pygame.font.init()

font = pygame.font.SysFont("arial", 20)

def in_circle(p1,p2,r):
    return (p1[0]-p2[0])**2 + (p1[1]-p2[1])**2 <= r**2


class cube:
    height = 12
    width = 12
    def __init__(self,x,y,status):
        self.x = x
        self.y = y
        self.status = status
    def update_status(self,new_status):
        self.status = new_status
    def display_cube(self,background):
        pygame.draw.rect(background, (255,255,255), pygame.Rect(self.x, self.y,self.width,self.height))

class cubes:
    def __init__(self,n,m,density):
        self.m = m
        self.n = n
        self.density = density
        self.matrix = list()
        self.height = n * (cube.width + 2) - 2
        self.width = m * (cube.height + 2) - 2
        self.x = WIDTH // 2 - self.width // 2
        self.y = 100
        for i in range(n):
            self.matrix.append(list())
            for j in range(m):
                self.matrix[i].append(cube(self.x + j*(cube.width+2),self.y+i*(cube.height+2),True if random.uniform(0,1) <= density else False))
    def display(self,background):
        pygame.draw.rect(background,(150,150,150), pygame.Rect(WIDTH // 2 - self.width // 2 - 2, 100 - 2, self.width + 4, self.height + 4))
        pygame.draw.rect(background,COLOR_BLACK, pygame.Rect(WIDTH // 2 - self.width // 2, 100, self.width, self.height))
        for row in self.matrix:
            for cub in row:
                if cub.status == True:
                    cub.display_cube(background)
    def update(self):
        new_matrix = deepcopy(self.matrix)
        for i in range(self.n):
            for j in range(self.m):
                c = 0
                for k in range(i-1,i+2):
                    for l in range(j-1,j+2):
                        if k >= 0 and k < self.n and l >= 0 and l < self.m and not (k == i and l == j):
                            if new_matrix[k][l].status == True:
                                c += 1
                if new_matrix[i][j].status == False and c == 3:
                    self.matrix[i][j].update_status(True)
                elif new_matrix[i][j].status == True and (c == 3 or c == 2):
                    self.matrix[i][j].update_status(True)
                else:
                    self.matrix[i][j].update_status(False)
    def check_click(self,old_x,old_y):
        x = pygame.mouse.get_pos()[0]
        y = pygame.mouse.get_pos()[1]
        if x < self.x or x > self.x + self.width or y < self.y or y > self.y + self.height:
            return 0
        for row in self.matrix:
            for cub in row:
                if y < cub.y or y > cub.y + cub.height:
                    break
                elif not(x < cub.x or x > cub.x + cub.width or y < cub.y or y > cub.y + cub.height):
                    if pygame.mouse.get_pressed()[0]:
                        cub.status = True
                    elif pygame.mouse.get_pressed()[2]:
                        cub.status = False

class button:
    width = 100
    height = 50
    def __init__(self,x,y,id,text):
        self.x = x
        self.y = y
        self.id = id
        self.text = text
        self.img_text = font.render(text, True, COLOR_BLACK)
        self.button_obj = pygame.Rect(self.x,self.y,self.width,self.height)

    def check_click(self):
        mouse_x = pygame.mouse.get_pos()[0]
        mouse_y = pygame.mouse.get_pos()[1]
        if mouse_x > self.x and mouse_x < self.x + self.width and mouse_y > self.y and mouse_y < self.y + self.height:
            return True
        else:
            return False

    def display_button(self,background,screen):
        pygame.draw.rect(background, (255, 255, 255),self.button_obj)
        self.img_text = font.render(self.text, True, COLOR_BLACK)
        screen.blit(self.img_text,(self.button_obj.x + self.button_obj.width // 2 - self.img_text.get_width() // 2,self.button_obj.y + self.button_obj.height // 2 - self.img_text.get_height() // 2))

def main():
    # Initialize imported pygame modules
    pygame.init()

    # Set the window's caption
    pygame.display.set_caption("Conway's Game of Life")

    clock = pygame.time.Clock()

    screen = pygame.display.set_mode((WIDTH, HEIGHT))

    background = pygame.Surface((WIDTH, HEIGHT))
    background = background.convert()
    background.fill(COLOR_BLACK)

    # Blit everything to screen
    screen.blit(background, (0, 0))
    density = 0.5
    speed = 100
    
    while True:
        pygame.display.flip()

        old_x = 0
        old_y = 0
        n = 0
        sem = True
        all_states = list()
        fake_density = str(density)
        cube_matrix = cubes(25,50,density)
        cooldown = -99
        running = 0
        nr_iteration = 0
        fake_speed = str(speed)
        buttons = list()

        # Creating the buttons
        run_button = button(cube_matrix.x,cube_matrix.height // 2 + HEIGHT // 2 ,"RUN","Run")
        stop_button = button(WIDTH//2 - 50,cube_matrix.height // 2 + HEIGHT // 2,"STOP","Stop")
        step_button = button(cube_matrix.x + (stop_button.x - run_button.x) // 2, cube_matrix.height // 2 + HEIGHT // 2,"STEP","Step")
        restart_button = button(stop_button.x + (stop_button.x - run_button.x),cube_matrix.height // 2 + HEIGHT // 2,"RESTART","Restart")
        clear_button = button(cube_matrix.x,cube_matrix.height // 2 + HEIGHT // 2 + run_button.height + 10,"CLEAR","Clear")
        speed_button = button(WIDTH//2 - 50,cube_matrix.height // 2 + HEIGHT // 2 + run_button.height + 10,"SPEED","Speed:"+str(speed))
        density_button = button(stop_button.x + (stop_button.x - run_button.x),cube_matrix.height // 2 + HEIGHT // 2 + run_button.height + 10,"DENSITY","Density:"+str(density))
        undo_button = button(cube_matrix.x + (stop_button.x - run_button.x) // 2, cube_matrix.height // 2 + HEIGHT // 2 + run_button.height + 10,"UNDO","Undo")

        # Adding the buttons to a list
        buttons.append(run_button)
        buttons.append(stop_button)
        buttons.append(step_button)
        buttons.append(restart_button)
        buttons.append(clear_button)
        buttons.append(speed_button)
        buttons.append(density_button)
        buttons.append(undo_button)

        restarted = False
        input_active_speed = False
        input_active_density = False
        while not restarted:
            img_iterations = font.render('Iteration No. ' + str(nr_iteration), True, COLOR_RED)
            clock.tick(FPS)
            screen.blit(img_iterations,(WIDTH // 2 - img_iterations.get_width() // 2,65))
            # Erase everything drawn at last step by filling the background
            # with color black
            background.fill(COLOR_BLACK)

            # Check for Quit event
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                elif event.type == pygame.MOUSEBUTTONUP:
                    old_x = 0
                    old_y = 0
                elif event.type == pygame.MOUSEBUTTONDOWN:
                    mouse_poz = pygame.mouse.get_pos()
                    for button_obj in buttons:
                        if button_obj.check_click():
                            if button_obj.id == "RUN":
                                running = 1
                                sem = True
                            elif button_obj.id == "STOP":
                                running = 0
                            elif button_obj.id == "RESTART":
                                restarted = True
                                break
                            elif button_obj.id == "CLEAR":
                                for row in cube_matrix.matrix:
                                    for cub in row:
                                        cub.status = False
                            elif button_obj.id == "SPEED":
                                input_active_speed = True
                                fake_speed = ""
                                button_obj.text = "Speed:"
                            elif button_obj.id == "DENSITY":
                                input_active_density = True
                                fake_density = ""
                                button_obj.text = "Density:"
                            elif button_obj.id == "STEP":
                                cooldown = speed + 1
                                new_matrix = list()
                                i = 0
                                j = 0
                                for row in cube_matrix.matrix:
                                    new_matrix.append(list())
                                    j = 0
                                    for cub in row:
                                        new_matrix[i].append(row[j].status)
                                        j += 1
                                    i += 1
                                if not (new_matrix in all_states):
                                    all_states.append(new_matrix)

                                if n == len(all_states) and running:
                                    sem = False

                                n = len(all_states)

                                nr_iteration += 1
                                cube_matrix.update()

                            elif button_obj.id == "UNDO":
                                if nr_iteration > 0:
                                    for i in range(len(cube_matrix.matrix)):
                                        for j in range(len(cube_matrix.matrix[i])):
                                            cube_matrix.matrix[i][j].status = all_states[len(all_states)-1][i][j]
                                    nr_iteration -= 1
                                    del all_states[len(all_states)-1]

                elif event.type == pygame.KEYDOWN and input_active_speed:
                    if event.key == pygame.K_RETURN:
                        input_active_speed = False
                        speed = int(fake_speed)
                    elif event.key == pygame.K_BACKSPACE:
                        fake_speed = fake_speed[:-1]
                    else:
                        fake_speed += event.unicode
                elif event.type == pygame.KEYDOWN and input_active_density:
                    if event.key == pygame.K_RETURN:
                        input_active_density = False
                        density = float(fake_density)
                    elif event.key == pygame.K_BACKSPACE:
                        fake_density = fake_density[:-1]
                    else:
                        fake_density += event.unicode

            for button_obj in buttons:
                if button_obj.id == "SPEED" and input_active_speed:
                    button_obj.text = "Speed:" + fake_speed
                elif button_obj.id == "DENSITY" and input_active_density:
                    button_obj.text = "Density:" + fake_density
                button_obj.display_button(background, screen)

            if pygame.mouse.get_pressed()[0]:
                cube_matrix.check_click(old_x,old_y)
                old_x = pygame.mouse.get_pos()[0]
                old_y = pygame.mouse.get_pos()[1]
            elif pygame.mouse.get_pressed()[2]:
                cube_matrix.check_click(old_x,old_y)
                old_x = pygame.mouse.get_pos()[0]
                old_y = pygame.mouse.get_pos()[1]
            if cooldown % speed == 0 and sem and running:
                new_matrix = list()
                i = 0
                j = 0
                for row in cube_matrix.matrix:
                    new_matrix.append(list())
                    j = 0
                    for cub in row:
                        new_matrix[i].append(row[j].status)
                        j += 1
                    i += 1
                if not (new_matrix in all_states):
                    all_states.append(new_matrix)

                if n == len(all_states) and running:
                    sem = False

                n = len(all_states)

                nr_iteration += 1
                cube_matrix.update()

            if running:
                cooldown += 1

            cube_matrix.display(background)

            pygame.display.flip()
            screen.blit(background, (0, 0))


if __name__ == '__main__':
    main()
