import pygame

#Entities with physics
class PhysicsEntity:
    def __init__(self, game, entityType, pos, size):
        self.game = game
        self.type = entityType

        
        #List helps as it provides a common reference for the rendered entity and one update 
        #updates the entire list of renders of that entity. Tuple isnt good here as you will
        #have to update the entire tuple
        self.pos = list(pos)

        self.size = size

        #derivative of posion = velocity. it shows rate of change of posion. it updates posion based on frame
        self.velocity = [0, 0]

        #Keeping track of collisions in a dictionary
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}

        #To account for action of player
        self.action = ''

        #Rendering images with offset to account for padding
        self.animationOffset = (-3, -3)

        #To account for direction we are facing
        self.flip = False

        #Idle at the start
        self.setAction('idle')
    
    #Giving each PhysicsEntity a collision rectangle
    def rect(self):

        #Position here is the top left of the entity rather than the center
        return pygame.Rect(self.pos[0], self.pos[1], self.size[0], self.size[1])
    
    def setAction(self, action):
        #In case action has changed from idle
        if action != self.action:
            self.action = action
            self.animation = self.game.assets[self.type + '/' + self.action].copy()
        
    def update(self, tileMap, movement=(0, 0)):
        self.collisions = {'up': False, 'down': False, 'right': False, 'left': False}
        
        #Vector quantity to represent how much movement in the frame based on force of frame and velocity
        frame_movement = (movement[0] + self.velocity[0], movement[1] + self.velocity[1])
        
        #Updating posion wrt frame movement VERY IMPORTANT TO KEEP X AND Y SEPARATE

         #X Position
        self.pos[0] += frame_movement[0]
        entity_rect = self.rect()
        #Collision
        for rect in tileMap.physics_rects_around(self.pos):
            #We use movoements in both X and Y axis and we resolve further from there

            if entity_rect.colliderect(rect):

                #Right edge of entity is gonna snap to the left edge of tile
                if frame_movement[0] > 0:
                    entity_rect.right = rect.left
                    self.collisions['right'] = True
                #Left side of entity is gonna snap to the right side of tile
                if frame_movement[0] < 0:
                    entity_rect.left = rect.right
                    self.collisions['left'] = True

                #If we can move around rectangles as we did, why cant we use rect to represent entity position?
                #Its because rects can only accept integer values and thus sub-pixel movements cant happen
                self.pos[0] = entity_rect.x
        
        #Y Position. Same drill as we did for X Position
        self.pos[1] += frame_movement[1]
        entity_rect = self.rect()
        for rect in tileMap.physics_rects_around(self.pos):
            
            if entity_rect.colliderect(rect):

                #Downwards
                if frame_movement[1] > 0:
                    entity_rect.bottom = rect.top
                    self.collisions['down'] = True

                #Upwards
                if frame_movement[1] < 0:
                    entity_rect.top = rect.bottom
                    self.collisions['up'] = True
                self.pos[1] = entity_rect.y
                
        if movement[0] > 0:
            self.flip = False
        if movement[0] < 0:
            self.flip = True
        
        #To apply acceleration we use velocity
        self.velocity[1] = min(5, self.velocity[1] + 0.1)
        
        if self.collisions['down'] or self.collisions['up']:
            self.velocity[1] = 0
            
        self.animation.update()
        
    def render(self, surface, offset=(0, 0)):
        surface.blit(pygame.transform.flip(self.animation.image(), self.flip, False), (self.pos[0] - offset[0] + self.animationOffset[0], self.pos[1] - offset[1] + self.animationOffset[1]))

class Player(PhysicsEntity):
    def __init__(self, game, pos, size):
        #Accessing methods of PhysicsEntity and initializing attributes
        super().__init__(game, 'player', pos, size)
        self.airTime = 0
    
    def update(self, tileMap, movement=(0, 0)):
        super().update(tileMap, movement=movement)
        
        self.airTime += 1
        if self.collisions['down']:
            self.airTime = 0
            
        if self.airTime > 4:
            self.setAction('jump')

        #If we are not moving horizontally, we are not running
        elif movement[0] != 0:
            self.setAction('run')
        else:
            self.setAction('idle')

