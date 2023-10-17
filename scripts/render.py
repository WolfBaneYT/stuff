import pygame
import os

basePath = 'data/images/'

def loadImage(path):
    #Convert makes it easier to render by converting internal representation in pygame
    image = pygame.image.load(basePath + path).convert()
    image.set_colorkey((0,0,0))
    return image

def loadImages(path):
    images = []
    #Taking all files in a particular path
    for imageName in os.listdir(basePath + path):
        images.append(loadImage(path + '/' + imageName))
    return images

class Animations:
    def __init__(self,images,image_duration = 5, loop=True):
        self.images = images
        self.loop = loop
        self.image_duration = image_duration
        #self.done would be True if we are not looping and it reaches the end
        self.done = False
        #Keeping track of where we are/Game Frame
        self.frame = 0
    
    def copy(self):
        #just copying to prevent performance drop
        return Animations(self.images, self.image_duration, self.loop)
    
    def update(self):
        #
        if self.loop:
            '''
            If it goes past the end of animation we may run into index error since we are trying to access image
            past the animation's end
            So what we do here makes it so that the code is forced to loop once it reaches the end
            Getting remainder is basically creating a loop
            '''
            self.frame = (self.frame+1) % (self.image_duration * len(self.images))

        else:
            self.frame = min(self.frame + 1 , self.image_duration * len(self.images) - 1)

            if self.frame >= self.image_duration * len(self.images) - 1:
                self.done = True

    def image(self):
        #Getting current image of animation to provide flexibility so we can use however we want 
        return self.images[int(self.frame / self.image_duration)]