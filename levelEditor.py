import sys
import pygame

from scripts.render import loadImages
from scripts.tiles import Tilemap

renderScale = 2.0

class Edit:
    def __init__(self):
        pygame.init()

        #SAME FPS SETTING CODE
        pygame.display.set_caption('LVL EDITOR')
        self.screen = pygame.display.set_mode((640, 480))
        self.display = pygame.Surface((320, 240))

        self.clock = pygame.time.Clock()
        
        self.assets = {
            'decor': loadImages('tiles/decor'),
            'grass': loadImages('tiles/grass'),
            'large_decor': loadImages('tiles/large_decor'),
            'stone': loadImages('tiles/stone')
        }

        #MOVING CAMERA IN ALL DIRECTIONS
        self.movement = [False,False,False,False]
        
        #NEED TILEMAP FOR DESIGN
        self.tilemap = Tilemap(self, tileSize=16)
        
        #Passing map only if it exists
        try:
            self.tilemap.load('map.json')
        except FileNotFoundError:
            pass

        self.scroll = [0, 0]
        
        #Converts our assets into lists
        self.tilesList = list(self.assets)
        #Group
        self.tileGroup = 0
        #Variant
        self.tileVariant = 0

        #Movement Booleans
        self.click = False
        self.rightclick = False
        self.shift = False
        self.onGrid = True
    def run(self):
        while True:
            #Filing black
            self.display.fill((0,0,0))

            #Moving camera
            self.scroll[0] += (self.movement[1] - self.movement[0]) * 2
            self.scroll[1] += (self.movement[3] - self.movement[2]) * 2
            renderScroll = (
                int(self.scroll[0]) ,
                int(self.scroll[1])
                )
            
            self.tilemap.render(self.display, offset=renderScroll)
            '''from tile list, using index of group. from assets, we select the group of the tile such as grass and
            the variant'''
            presentTileImage = self.assets[self.tilesList[self.tileGroup]][self.tileVariant].copy()
            #PARTIAL TRANSPARENCY
            presentTileImage.set_alpha(100)

            mousePos = pygame.mouse.get_pos()
            #Doing this as we have scaling at the bottom of the code and it could create problems
            mousePos = (mousePos[0]/renderScale , mousePos[1]/renderScale)

            #Coordinates of mouse
            tilePos = (
                int((mousePos[0] + self.scroll[0]) // self.tilemap.tileSize),
                int((mousePos[1] + self.scroll[1]) // self.tilemap.tileSize)
                    )
            if self.onGrid:
            #Converting back into coordinates by multiplying with tile size and adjusting position wrt camera
            #Scaling back to snap to grid
                self.display.blit(
                    presentTileImage,
                    (tilePos[0] * self.tilemap.tileSize - self.scroll[0],
                    tilePos[1] * self.tilemap.tileSize - self.scroll[1])
                    )
            else:
                self.display.blit(presentTileImage, mousePos)

            #Dont need for every tile, just some
            if self.click and self.onGrid:
                self.tilemap.tileMap[str(tilePos[0]) + ';' + str(tilePos[1])] = {'type': self.tilesList[self.tileGroup], 'variant': self.tileVariant, 'pos' : tilePos}
            
            if self.rightclick:
                tileLocation = str(tilePos[0]) + ';' + str(tilePos[1])
                #If location exists
                if tileLocation in self.tilemap.tileMap:
                    del self.tilemap.tileMap[tileLocation]
                #Copying because we are gonna delete if touching mouse and prevent iteration problem
                for tile in self.tilemap.offGridTiles.copy():
                    #Hitbox of offgrid tile
                    tileImage = self.assets[tile['type']][tile['variant']]
                    tileR = pygame.Rect(
                        tile['pos'][0] - self.scroll[0],
                        tile['pos'][1] - self.scroll[1],
                        tileImage.get_width(),
                        tileImage.get_height())
                    #Checkin if tile position collides with mouse
                    if tileR.collidepoint(mousePos):
                        self.tilemap.offGridTiles.remove(tile)
            self.display.blit(presentTileImage,(5,5))
            

            for event in pygame.event.get():
                if event.type == pygame.QUIT:
                    pygame.quit()
                    sys.exit()
            #KEYS
                #MOUSE
                if event.type == pygame.MOUSEBUTTONDOWN:
                    #LEFT CLICK
                    if event.button == 1:
                        self.click = True
                        if not self.onGrid:
                            #Adding scroll
                            #From camera perspective, top left is 0,0
                            #If camera is for example a bit to the right, and is placed at 0,0 in window,
                            #the coordinates in world for 0,0 become coordinates of camera were
                            #Thus we add into the world space from display space
                            #Inverse of tile rendering where we convert world space to window space
                            self.tilemap.offGridTiles.append(
                                {'type' : self.tilesList[self.tileGroup],
                                 'variant' : self.tileVariant,
                                 'pos' : (mousePos[0] + self.scroll[0], mousePos[1] + self.scroll[1])
                                 })
                    #RIGHT CLICK
                    if event.button == 3:
                        self.rightclick = True
                    #TILE VARIANT
                    if self.shift == True:
                        #SCROLL UP
                        if event.button == 4:
                            #LOOPING VIA MODULUS
                            self.tileVariant = (self.tileVariant-1) % (len(self.assets[self.tilesList[self.tileGroup]]))
                        #SCROLL DOWN
                        if event.button == 5:
                            #SAME DRILL
                            self.tileVariant = (self.tileVariant+1) % (len(self.assets[self.tilesList[self.tileGroup]]))
                    #TILE GROUP
                    #SET TILE VARIANT TO 0 TO MINIMIZE ERRORS
                    else:
                        if event.button == 4:
                            self.tileGroup = (self.tileGroup-1) % (len(self.tilesList))
                            self.tileVariant = 0
                        if event.button == 5:
                            self.tileGroup = (self.tileGroup + 1) % (len(self.tilesList))
                            self.tileVariant = 0

                if event.type == pygame.MOUSEBUTTONUP:
                    if event.button == 1:
                        self.clicking = False
                    if event.button == 3:
                        self.rightclick = False 
                #KEYBOARD
                if event.type == pygame.KEYDOWN:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.movement[0] = True
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.movement[1] = True
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.movement[2] = True
                    if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.movement[3] = True
                    #Switching whether or not adding
                    if event.key == pygame.K_g:
                        self.onGrid = not self.onGrid
                    if event.key == pygame.K_t:
                        self.tilemap.autotile()
                    if event.key == pygame.K_o:
                        self.tilemap.save('map.json')
                    if event.key == pygame.K_LSHIFT:
                        self.shift = True

                if event.type == pygame.KEYUP:
                    if event.key == pygame.K_LEFT or event.key == pygame.K_a:
                        self.movement[0] = False
                    if event.key == pygame.K_RIGHT or event.key == pygame.K_d:
                        self.movement[1] = False
                    if event.key == pygame.K_UP or event.key == pygame.K_w:
                        self.movement[2] = False
                    if event.key == pygame.K_DOWN or event.key == pygame.K_s:
                        self.movement[3] = False
            
            self.screen.blit(pygame.transform.scale(self.display, self.screen.get_size()), (0, 0))
            
            pygame.display.update()
            self.clock.tick(60)

Edit().run()