import sys
import pygame

from scripts.render import loadImage, loadImages, Animations
from scripts.entities import PhysicsEntity, Player
from scripts.tiles import Tilemap
from scripts.cloudRender import Clouds

class Game:
    def __init__(self):
        pygame.init()

        pygame.display.set_caption('ninja game')
        self.screen = pygame.display.set_mode((640, 480))
        self.display = pygame.Surface((320, 240))

        self.clock = pygame.time.Clock()

        '''
        OLD
        self.image = pygame.image.load('data/images/clouds/cloud_1.png')
        self.image.set_colorkey((0,0,0))
        self.imagepos = [160,260]'''
        
        self.movement = [False, False]
        
        self.assets = {
            'decor': loadImages('tiles/decor'),
            'grass': loadImages('tiles/grass'),
            'large_decor': loadImages('tiles/large_decor'),
            'stone': loadImages('tiles/stone'),
            'player': loadImage('entities/player.png'),
            'background': loadImage('background.png'),
            'clouds': loadImages('clouds'),
            'player/idle': Animations(loadImages('entities/player/idle'), image_duration=6),
            'player/run': Animations(loadImages('entities/player/run'), image_duration=4),
            'player/jump': Animations(loadImages('entities/player/jump')),
            'player/slide': Animations(loadImages('entities/player/slide')),
            'player/wall_slide': Animations(loadImages('entities/player/wall_slide')),
        }
        
        #print(self.assets) (OLD)
        self.clouds = Clouds(self.assets['clouds'], count=16)
        
        self.player = Player(self, (50, 50), (8, 15))
        
        self.tilemap = Tilemap(self, tileSize=16)
        
        self.tilemap.load('map.json')
        #Camera
        self.scroll = [0, 0]
        
    def run(self):
        while True:
            #Used to be filling with a color but upon progress we filled it with the background image
            self.display.blit(self.assets['background'], (0, 0))
            
            '''Moving Camera 
            We cant do self.scroll[0] += 1 as it just moves linearly and doesn't check if player is still on the screen
            If we put it right where player is, player would be situated in top left of screen
            To keep it in the center, we subtract half the screen size so that center of what we see is situated on player
            Long story short, we subtract where we are(THE PART AFTER '/2') from where we want to be (BEFORE '/2')
            Then we divide by 30 so that it takes a 30th of what is remaining to the center and applies that to the scroll
            Further the player, faster it moves
            As it gets closer, it slows down'''
            self.scroll[0] += (self.player.rect().centerx - self.display.get_width() / 2 - self.scroll[0]) / 30
            self.scroll[1] += (self.player.rect().centery - self.display.get_height() / 2 - self.scroll[1]) / 30

            '''
            UPON DOING ALL THIS THERE IS A JITTER IN MOVEMENT 
            THIS IS BECAUSE THE POSITION OF THE PLAYER IS A FLOAT VALUE AND IT CAUSES SUB PIXEL MOVEMENT 
            EVEN THE SCROLL VALUE IS A WHOLE NUMBER
            WE CAN USE int() HERE So AS TO CONTROL THIS AND WE RENDER WITH THIS SCROLL VALUE
            '''
            render_scroll = (int(self.scroll[0]), int(self.scroll[1]))
            
            self.clouds.update()
            self.clouds.render(self.display, offset=render_scroll)
            
            self.tilemap.render(self.display, offset=render_scroll)
            
            self.player.update(self.tilemap, (self.movement[1] - self.movement[0], 0))
            self.player.render(self.display, offset=render_scroll)

             #TESTING FOR TILE COLLISION : print(self.tileMap.physics_rects_around(self.player.pos))
            
            '''
            OLD
            imageRect = pygame.Rect(self.imagepos[0], self.imagepos[1], self.image.get_width(), self.image.get_height())

            if imageRect.colliderect(self.collisionArea):
                pygame.draw.rect(self.screen, (0,100,200), self.collisionArea)
            else:
                pygame.draw.rect(self.screen, (0,100,2), self.collisionArea)
            '''
            #self.imagepos[1] += (self.movement[1] - self.movement[0])*5    
            #self.screen.blit(self.image, self.imagepos)
            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.movement[1] = True
                    if event.key == pygame.K_UP:
                        self.player.velocity[1] = -3
                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.movement[1] = False
            
            #Renders screen onto display and scaling wrt screen itself 
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            
            #FPS
            pygame.display.update()
            self.clock.tick(60)

Game().run()