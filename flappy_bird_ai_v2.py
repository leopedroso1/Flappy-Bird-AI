# -*- coding: utf-8 -*-
"""
Created on Sun Dec 29 19:51:49 2019

@author: Leonardo
"""

import pygame
import time
import os
import random
import neat
pygame.font.init()

# NEAT - NeuroEvolution of Augmenting Topologies is an evolutionary algorithm that creates artificial neural networks.
# in other words is an genetic algorithm toolkit to make our life easier...

# Artificial intelligence architecture - Genetic Neural Network for flappy bird playing

# Inputs: 3 Nodes: Y bird position, Top pipe position, Bottom pipe position,
# Output: 1 jump?
# Activation function: tanH (we can change for ReLU for testing)
# Population Size: 100 birds per generation
# Fitness function: distance. How far our bird goes is the best fit for our model
# Max. Generations: 30 for testing if the neural network is performing well

# Set the frame size 800 x 600
WIN_WIDTH = 500
WIN_HEIGHT = 800

# Load images: Bird, Pipe, Base, and Background
BIRD_IMAGES = [pygame.transform.scale2x(pygame.image.load(os.path.join("img", "bird1.png"))),
               pygame.transform.scale2x(pygame.image.load(os.path.join("img", "bird2.png"))), 
               pygame.transform.scale2x(pygame.image.load(os.path.join("img", "bird3.png")))]

PIPE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("img", "pipe.png")))

BASE_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("img", "base.png")))

BG_IMG = pygame.transform.scale2x(pygame.image.load(os.path.join("img", "bg.png")))

STAT_FONT = pygame.font.SysFont("comicsans", 60)

class Bird:
    
    IMGS = BIRD_IMAGES
    MAX_ROTATION = 25  # 25 degrees of maximun pitch angle for bird's rotation
    ROT_VEL = 20 # how much we are gonna move the bird
    ANIMATION_TIME = 5 # how much time we will exhibit the bird animation
    
    def __init__(self, x, y):
        
        self.x = x # X coordinate
        self.y = y # Y coordinate
        self.tilt = 0 # how much the image tilt (inclina) on the screen. 0 = flat
        self.tick_count = 0 # Physics of the bird
        self.vel = 0 # velocity (start not moving)
        self.height = self.y # this is the height. We start with the Y of the image
        self.img_count = 0 # What image is currently showing
        self.img = self.IMGS[0] # Initialize with the first bird image
        
    def jump(self):

        self.vel = -10.5 # Remember from (0,0) coordinates in the upper left corner of monitor. if you wanna go down (+ positive velocity) if you wanna go up (- negative velocity)
        self.tick_count = 0  
        self.height = self.y
        
    def move(self):
        self.tick_count += 1 # How many moves we made since the last jump
        
        #Physics equation for displacement (deslocamento)
        displacement = self.vel * self.tick_count + 1.5 * self.tick_count**2 # Calculate how many pixels move up when we change the "Y" position
        # this equation will result progressively: -10.5 + 1.5 = -9...-7...-3...2 (when positive our bird goes down by "gravity") 
        
        if displacement >= 16: # 16 pixels is the maximum
            displacement = 16
            
        if displacement < 0: # 0 pixels - make a smaller correction for the next jump
            displacement -= 2
            
        self.y = self.y + displacement # change the "y" coordinate based on displacement
        
        # handling the tilt of the bird given the displacement, y coordinate and heights
        if displacement < 0 or self.y < self.height + 50:
            if self.tilt < self.MAX_ROTATION:
                self.tilt = self.MAX_ROTATION
        else:
            if self.tilt > -90: # 90º angle
                self.tilt -= self.ROT_VEL # Completely changes the tilt for 90º downwards faster to the ground
     
    def draw(self, win):  # Handle the loading of images given situations
        self.img_count += 1
        
        # Sit 1: Bird going up normally
        if self.img_count < self.ANIMATION_TIME:
            self.img = self.IMGS[0]
        
        elif self.img_count < self.ANIMATION_TIME*2:
            self.img = self.IMGS[1]
        
        elif self.img_count < self.ANIMATION_TIME*3:
            self.img = self.IMGS[2]
            
        elif self.img_count < self.ANIMATION_TIME*4:
            self.img = self.IMGS[1]

        elif self.img_count < self.ANIMATION_TIME*4 + 1:
            self.img = self.IMGS[0]
            self.img_count = 0    
            
        # Sit 2: Bird going down
        if self.tilt <= -80:
            self.img = self.IMGS[1]
            self.img_count = self.ANIMATION_TIME*2 # Recovery if we press up the wings will flap again
            
        # sit 3: Rotation handling
        rotated_image = pygame.transform.rotate(self.img, self.tilt) # rotate the image 
        new_rect = rotated_image.get_rect(center=self.img.get_rect(topleft= (self.x, self.y)).center) # create a centred rectangle to move in the the image in its center
        win.blit(rotated_image, new_rect.topleft)
        
    def get_mask(self): # Used for colisions
        return pygame.mask.from_surface(self.img)
    


class Pipe:
    
    GAP = 200 #space between pipes
    VEL = 5 # Speed of the scenario 
    
    
    def __init__(self, x):
        
        self.x = x
        self.height = 0 
        self.gap = 100
        
        self.top = 0 # Where will be the top of the Pipe
        self.bottom = 0 # Where will be the bottom of the Pipe
        self.PIPE_TOP = pygame.transform.flip(PIPE_IMG, False, True) #rotate
        self.PIPE_BOTTOM = PIPE_IMG 
        
        self.passed = False # If the bird passed through the pipe. We will use for collisions
        self.set_height() # We will use to set the height of the pipe where will be possible for the bird pass through
    
    def set_height(self):
        self.height = random.randrange(50, 450) # random height for a random pipe
        self.top = self.height - self.PIPE_TOP.get_height() # we will use to calculate the top of the upper pipe, given the height of the normal pipe - the top of the upper pipe
        self.bottom = self.height + self.GAP
        
    def move(self):
        self.x -= self.VEL # we move the background not the bird
        
        
    def draw(self, win):
        win.blit(self.PIPE_TOP, (self.x, self.top)) # Draw in the windows
        win.blit(self.PIPE_BOTTOM, (self.x, self.bottom))
        
        # In order to pursuit a enhanced collision precision, we will use the mask technique. This technique allows us to detect if the inner pixels from a figure are really colliding (or overlaping) some object, in other words, if this first figure is really touching another one
        # to do this we will an array and compare these arrays
        
    def collide(self, bird):
        bird_mask = bird.get_mask()
        top_mask = pygame.mask.from_surface(self.PIPE_TOP)
        bottom_mask = pygame.mask.from_surface(self.PIPE_BOTTOM)
        
        # Calculate offset - how much something is far from something
        # offset 1: Bird x Top
        top_offset = (self.x - bird.x, self.top - round(bird.y))
                                  
        # offset 2: Bird x Bottom
        bottom_offset = (self.x - bird.x, self.bottom - round(bird.y))

        # bottom point of collision. We can detect the collision by using the overlap function from pygame. 
        b_point = bird_mask.overlap(bottom_mask, bottom_offset)
        
        # top point of collision 
        t_point = top_mask.overlap(top_mask, top_offset)
        
        if b_point or t_point:
            return True
        
        return False
        
# Class for ground action programming 
class Base:
    
    VEL = 5 # the same velocity of the pipe to keep cohesion
    WIDTH = BASE_IMG.get_width() # Width from base
    IMG = BASE_IMG # image loading
    
    def __init__(self, y):
        self.y = y
        self.x1 = 0
        self.x2 = self.WIDTH
        
    def move(self): # We will have 2 images and we move the first one backwards meanwhile the second one is moving with the same speed in the same direction.
        self.x1 -= self.VEL
        self.x2 -= self.VEL
        
        if self.x1 + self.WIDTH < 0: # start over again x1 and x2
            self.x1 = self.x2 + self.WIDTH
            
        if self.x2 + self.WIDTH < 0:
            self.x2 = self.x2 + self.WIDTH
            
    def draw(self, win):
        win.blit(self.IMG, (self.x1, self.y))
        win.blit(self.IMG, (self.x2, self.y))
        
        

        


def draw_window(win, birds, pipes, base, score): # function to draw in the window. Here we call all other draw funcions from classes
    
    win.blit(BG_IMG, (0,0)) #draw some image in some position, in this case we will are drawing the background

    for pipe in pipes:
        pipe.draw(win) # Draw pipes

    text = STAT_FONT.render("Score: "+str(score), 1, (255, 255, 255))
    win.blit(text, (WIN_WIDTH - 10 - text.get_width(), 10))
    
    base.draw(win) # draw base
    
    for bird in birds:
        bird.draw(win) #draw our bird
    
    pygame.display.update() 
    
    
def main(genomes, config):
    #bird = Bird(230,350) # place the bird in X Y coordinate
    
    birds = [] # Now we set up an array of birds because we will use AI to play with multiple birds generations. In other words we will play with more than one bird
    ge = [] # tracking for genomes (Each bird one genome)
    nets = [] # tracking for nets (Each bird one neural net)
    
    
    for _, g in genomes: # This loop creates our birds and each neural network for them. A genome has (Id, object) so we need to use _, g
        net = neat.nn.FeedForwardNetwork.create(g, config) # Neural Network is set
        nets.append(net) # append an net for each genome
        birds.append(Bird(230, 350)) # append an bird for each genome
        g.fitness = 0  # set the initial reward as 0 (It looks like a Q Learning)
        ge.append(g) # append this genome
        
    
    base = Base(700) # place the base in the bottom
    pipes = [Pipe(600)]
    win = pygame.display.set_mode((WIN_WIDTH, WIN_HEIGHT))
    clock = pygame.time.Clock() # Use the clock to solve the quick falling movement from bird. Set for 30 for a smooth falling
    score = 0
    run = True
    
    while(run):
        clock.tick(30)
        for event in pygame.event.get():
            if event.type == pygame.QUIT:
                run = False
                pygame.quit()
                quit()
#        bird.move()
                
        # MOVING THE BIRD 
                
        pipe_ind = 0 # we need to check which pipe is going through

        if len(birds) > 0: # if we have birds
            if len(pipes) > 1 and birds[0].x > pipes[0].x + pipes[0].PIPE_TOP.get_width(): # and if the birds passed through the pipes
                pipe_ind = 1 # then pipe ind = 1
        else: # If there's no bird left
            run = False
            break
                
        for x, bird in enumerate(birds): # for each birds in a set of birds
            bird.move() # move the birds through the game
            ge[x].fitness += 0.1 # if our bird stay alive it gains 0.1 points
            
            # output result: actiave with Y coordination - the distance from height and bottom of the pipes
            output = nets[x].activate((bird.y, abs(bird.y - pipes[pipe_ind].height), abs(bird.y - pipes[pipe_ind].bottom)))                    
            
            if output[0] > 0.5: 
                bird.jump()
                
        
        add_pipe = False
        rem = []
        for pipe in pipes:
            for x, bird in enumerate(birds): #this function will add an index for each bird object (0, Bird())
                
                if pipe.collide(bird): # If collides we will set for an endgame
                    ge[x].fitness -= 1 # Every time the bird gets a pipe we decrease 1 in the fitness score
                    birds.pop(x) # if the bird fails we remove them
                    nets.pop(x) # Hence, we pop the nets for this X and also the genome as written below
                    ge.pop(x)
                    
                    
                if not pipe.passed and pipe.x < bird.x: # If the bird pass through
                    pipe.passed = True
                    add_pipe = True
            
            
            if pipe.x + pipe.PIPE_TOP.get_width() < 0: # if the bird pass through
                rem.append(pipe)
                
            
            pipe.move() # move pipe
        
        if add_pipe: # add another pipe in this X coordinate. If it adds a new pipe so we must inscrease our fitness score
            score += 1
            for g in ge: # the genomes in this list belong to the live birds
                g.fitness += 5
            pipes.append(Pipe(600)) # append another pipe
        
        for r in rem:
            pipes.remove(r) # remove the previous pipe

        for x, bird in enumerate(birds):
            if bird.y + bird.img.get_height() >= 730 or bird.y < 0: # if our bird is out of bounds. Delete them
                birds.pop(x)
                nets.pop(x)
                ge.pop(x)
                
        base.move() # move the base
        draw_window(win, birds, pipes, base, score) # draw window while run

        
    

#main()    

# function run: Used to load the NEAT set up (parameters, Neural networks etc)
def run(config_path):
    config = neat.config.Config(neat.DefaultGenome, neat.DefaultReproduction,
                                neat.DefaultSpeciesSet, neat.DefaultStagnation,
                                config_path) # Here we set up the configuration file to our project. These "neat." contains the same headers from our config file

    p = neat.Population(config) # set the population in the configuration file
    
    p.add_reporter(neat.StdOutReporter(True)) # Set the output performance statistics guideline
    stats = neat.StatisticsReporter() 
    p.add_reporter(stats)

    winner = p.run(main,50) # the first is the main function (fitness function). the second argument is the number or generatioms
                            # we will call this funcion 50x 

if __name__ == "__main__":
    
    local_dir = os.path.dirname(__file__) # find the local directory from this file
    config_path = os.path.join(local_dir, "config-feedforward_vOk.txt") # searches for AI config file
    run(config_path)
    