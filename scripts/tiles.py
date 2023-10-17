import pygame
import json

#Rules to autotile
autotileMap = {
    #CHECKING IF NEIGHBOURS AND GIVING APPROPRIATE CONDITIONS
    #RIGHT AND BELOW
    tuple(sorted([(1,0) , (0,1)])) : 0,
    #BELOW RIGHT AND LEFT
    tuple(sorted([(1,0) , (0,1) , (-1,0)])) : 1,
    tuple(sorted([(-1,0) , (0,1)])) : 2,
    tuple(sorted([(-1,0) , (0,-1), (0,1)])) : 3,
    tuple(sorted([(-1,0) , (0,-1)])) : 4,
    tuple(sorted([(-1,0) , (0,-1) , (1,0)])) : 5,
    tuple(sorted([(1,0) , (0,-1)])) : 6,
    tuple(sorted([(1,0) , (0,-1) , (0,1)])) : 7,
    tuple(sorted([(1,0) , (-1,0) , (0,1), (0,-1)])) : 8
}
#Offset for neighbouring tiles (ALL COMBINATIONS OF 0 and 1)
NEIGHBOUR_OFFSETS = [(-1,0), (-1,-1), (0,-1), (1,-1), (1,0), (0,0), (-1,1), (0,1), (1,1)]
#Collection of tile types with physics enabled, as a dictionary
PHYSICS_TILES = {'grass', 'stone'}
#Quick note :  Using dictionaries throughout as they are faster to read
typesAutotile = {'grass', 'stone'}
class Tilemap:
    def __init__(self,game,tileSize = 16):
        self.game = game
        self.tileSize = tileSize
        #Two sets of tiles
        #Tile Map is where all tiles are on a grid
        #Off Grid Tiles are not placed aligned with the tile map
        #We make this so that its easier to implement physics on to the grid called tileMap
        #Tile Map is dict so that we can assign different tile textures to different tiles
        self.tileMap = {}
        self.offGridTiles = []

        '''for i in range(10):
            #We can take tiles as objects now and assign multiple attributes
            #Vertical
            self.tileMap[str(3+i) + ';10'] =  {'type': 'grass', 'variant': 1, 'pos' : (3+i,10)}
            #Horizontal
            self.tileMap[';10' + str(5+i)] =  {'type': 'stone', 'variant': 1, 'pos' : (10,5+i)}'''
    
    def tiles_around(self,pos):
        #Using integer as position could be a float value and the extra zero can cause issues as negative values may exist and use a different method of division. It converts pixel position to grid position
        tiles = []
        tile_loc = (int(pos[0] // self.tileSize), int(pos[1] // self.tileSize))
        for offset in NEIGHBOUR_OFFSETS:
            check_loc = str(tile_loc[0] + offset[0]) + ';' + str(tile_loc[1] + offset[1])
            if check_loc in self.tileMap:
                tiles.append(self.tileMap[check_loc])
        return tiles
    
    #We multiply position of tile with tile size for exact position and size, we use tileSize for scaling
    def physics_rects_around(self, pos):
        rects = []
        for tile in self.tiles_around(pos):
            if tile['type'] in PHYSICS_TILES:
                rects.append(pygame.Rect(tile['pos'][0] * self.tileSize, tile['pos'][1] * self.tileSize, self.tileSize, self.tileSize))
        return rects
    
    def autotile(self):
        for loc in self.tileMap:
            #Location of tile
            tile = self.tileMap[loc]
            #Look for different neighbours
            neighbors = set()
            for shift in [(1,0), (-1,0), (0,-1), (0,1)]:
                #String location of original tile plus shift
                checkLoc = str(tile['pos'][0] + shift[0]) + ';' + str(tile['pos'][1] + shift[1])
                #If pass iterates, neighbour exists
                if checkLoc in self.tileMap:
                    #MAKING SURE NEIGHBOURING TILE IS SAME GROUP OR VARIANT
                    if self.tileMap[checkLoc]['type'] == tile['type']:
                        neighbors.add(shift)
            neighbors = tuple(sorted(neighbors))
            if (tile['type'] in typesAutotile) and (neighbors in autotileMap):
                tile['variant'] = autotileMap[neighbors]
    def render(self, surface, offset=(0,0)):    
        
        '''
        taking range and dividing offset of camera by tilesize to find x position of the tiles in the top left
        offset system is pixels and our tile system here is tile coordinates(pixels/tileSize)
        we take offset[0] and add display width so as to find right edge the screen and divide by tile size again
        we thus get coordinates of right edge of screen with a discrepancy of 1 so we add 1 as well
        '''
        for tile in self.offGridTiles:
            surface.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] - offset[0], tile['pos'][1] - offset[1]))
            
        for x in range(offset[0] // self.tileSize, (offset[0] + surface.get_width()) // self.tileSize + 1):
            for y in range(offset[1] // self.tileSize, (offset[1] + surface.get_height()) // self.tileSize + 1):
                loc = str(x) + ';' + str(y)
                if loc in self.tileMap:
                    tile = self.tileMap[loc]
                    surface.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] * self.tileSize - offset[0], tile['pos'][1] * self.tileSize - offset[1]))

    def save(self, path):
        f = open(path,'w') 
        #Dumping given object into file and convert to json
        json.dump({'tilemap' : self.tileMap, 'tileSize' : self.tileSize, 'offGrid' : self.offGridTiles}, f)
        f.close()
    def load(self,path):
        #WRAPPING
        f = open(path,'r')
        mapData = json.load(f)
        f.close()

        self.tileMap = mapData['tilemap']
        self.tileSize = mapData['tileSize']
        self.offGridTiles = mapData['offGrid']
    '''
        PREVIOUS CODE
        for tile in self.offGridTiles:
        #Tile positioning with offset for camera
        #To apply offset, for example moving right, we move right while background moves left. thus we subtract
        surfaceace.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] - offset[0], tile['pos'][1] - offset[1])) 
        for loc in self.tileMap:
            tile = self.tileMap[loc]
            surfaceace.blit(self.game.assets[tile['type']][tile['variant']], (tile['pos'][0] * self.tileSize - offset[0], tile['pos'][1] * self.tileSize - offset[1]))
        '''