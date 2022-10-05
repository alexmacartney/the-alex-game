import os
import tmx
import math
import pygame
from pygame import Rect
from pygame.math import Vector2

os.environ["SDL_VIDEO_CENTERED"] = "1"

###############################################################################
#                               Game State                                    #
###############################################################################

class GameItem():
    def __init__(self, state, position, tile):
        self.state = state
        self.status = "alive"
        self.position = position
        self.tile = tile
        self.orientation = 0

class Unit(GameItem):
    def __init__(self, state, position, tile):
        super().__init__(state, position, tile)

class GameState():
    def __init__(self):
        self.worldSize = Vector2(16, 10)
        self.ground = [ [ Vector2(5, 1) ] * 16 ] * 10
        self.units = [ Unit(self, Vector2(8, 9), Vector2(1, 0)) ]
        self.observers = [ ]
    
    @property
    def worldWidth(self):
        """
        Returns the world width as an integer
        """
        return int(self.worldSize.x)
    
    @property
    def worldHeight(self):
        """
        Returns the world height as an integer
        """
        return int(self.worldSize.y)        

    def isInside(self, position):
        """
        Returns true is position is inside the world
        """
        return position.x >= 0 and position.x < self.worldWidth \
           and position.y >= 0 and position.y < self.worldHeight

    def findUnit(self, position):
        """
        Returns the index of the first unit at position, otherwise None.
        """
        for unit in self.units:
            if  int(unit.position.x) == int(position.x) \
            and int(unit.position.y) == int(position.y):
                return unit
        return None
    
    def findLiveUnit(self, position):
        """
        Returns the index of the first live unit at position, otherwise None
        """
        unit = self.findUnit(position)
        if unit is None or unit.status != "alive":
            return None
        return unit
    
    def addObserver(self, observer):
        """
        Add a game state observer 
        All observer is notified when something happens (see GameStateObserver class)
        """
        self.observers.append(observer)
        
    def notifyUnitDestroyed(self, unit):
        for observer in self.observers:
            observer.unitDestroyed(unit)

class GameStateObserver():
    def unitDestroyed(self, unit):
        pass
    
###############################################################################
#                                Commands                                     #
###############################################################################

class Command():
    def run(self):
        raise NotImplementedError()
        
###############################################################################
#                                Rendering                                    #
###############################################################################
        
class Layer(GameStateObserver):
    def __init__(self, cellSize, imageFile):
        self.cellSize = cellSize
        self.texture = pygame.image.load(imageFile)
        
    def setTileset(self, cellSize, imageFile):
        self.cellSize = cellSize
        self.texture = pygame.image.load(imageFile)
        
    @property
    def cellWidth(self):
        return int(self.cellSize.x)

    @property
    def cellHeight(self):
        return int(self.cellSize.y)
        
    def renderTile(self, surface, position, tile, angle = None):
        # Location on screen
        spritePoint = position.elementwise() * self.cellSize
        
        # Texture
        texturePoint = tile.elementwise() * self.cellSize
        textureRect = Rect(int(texturePoint.x), int(texturePoint.y), self.cellWidth, self.cellHeight)
        
        # Draw
        if angle is None:
            surface.blit(self.texture, spritePoint, textureRect)
        else:
            # Extract the tile in a surface
            textureTile = pygame.Surface((self.cellWidth, self.cellHeight), pygame.SRCALPHA)
            textureTile.blit(self.texture, (0, 0), textureRect)
            # Rotate the surface with the tile
            rotatedTile = pygame.transform.rotate(textureTile, angle)
            # Compute the new coordinate on the screen, knowing that we rotate around the center of the tile
            spritePoint.x -= (rotatedTile.get_width() - textureTile.get_width()) // 2
            spritePoint.y -= (rotatedTile.get_height() - textureTile.get_height()) // 2
            # Render the rotatedTile
            surface.blit(rotatedTile, spritePoint)

    def render(self, surface):
        raise NotImplementedError() 
    
class ArrayLayer(Layer):
    def __init__(self, cellSize, imageFile, gameState, array, surfaceFlags = pygame.SRCALPHA):
        super().__init__(cellSize, imageFile)
        self.gameState = gameState
        self.array = array
        self.surface = None
        self.surfaceFlags = surfaceFlags
        
    def setTileset(self, cellSize, imageFile):
        super().setTileset(cellSize, imageFile)
        self.surface = None
        
    def render(self, surface):
        if self.surface is None:
            self.surface = pygame.Surface(surface.get_size(), flags = self.surfaceFlags)
            for y in range(self.gameState.worldHeight):
                for x in range(self.gameState.worldWidth):
                    tile = self.array[y][x]
                    if not tile is None:
                        self.renderTile(self.surface, Vector2(x, y), tile)
        surface.blit(self.surface,(0, 0))

class UnitsLayer(Layer):
    def __init__(self, cellSize, imageFile, gameState, units):
        super().__init__(cellSize, imageFile)
        self.gameState = gameState
        self.units = units
        
    def render(self, surface):
        for unit in self.units:
            self.renderTile(surface, unit.position, unit.tile, unit.orientation)

###############################################################################
#                                Game Modes                                   #
###############################################################################


        
###############################################################################
#                             User Interface                                  #
###############################################################################

class UserInterface(GameModeObserver):
    def __init__(self):
        # Window
        pygame.init()
        self.window = pygame.display.set_mode((1280, 720))
        pygame.display.set_caption("THE ALEX GAME")
        pygame.display.set_icon(pygame.image.load("assets/Alex.jpeg"))
        
        # Loop properties
        self.clock = pygame.time.Clock()
        self.running = True

    def worldSizeChanged(self, worldSize):
        self.window = pygame.display.set_mode((int(worldSize.x), int(worldSize.y)))
        
    def quitRequested(self):
        self.running = False
       
    def run(self):
        while self.running:
                
            # Update display
            pygame.display.update()    
            self.clock.tick(60)
            
            
userInterface = UserInterface()
userInterface.run()
            
pygame.quit()