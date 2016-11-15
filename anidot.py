import pygame
import pickle

# Constants
ANIDOT_DOTBLOCK_OFF = ' '
ANIDOT_DOTBLOCK_ON = 'X'
ANIDOT_ANIMATION_STOP = -1
ANIDOT_ANIMATION_START = 0

class Dot(pygame.sprite.Sprite):

    def __init__(self, spritesheet, patchwidth, numberframes, framerate, position):
        self.spriteSheetImage = spritesheet
        self.patchWidth = patchwidth
        self.numberOfFrames = numberframes
        self.frameRate = framerate
        self.positionInWindow = position
        self.animationFrameCount = 0
        self.animationPatchNumber = 0
        self.activated = 0

    def update(self):
        if self.animationFrameCount > 0 and self.animationPatchNumber != self.numberOfFrames * self.activated:
            self.animationFrameCount = (self.animationFrameCount + 1) % self.frameRate
            if self.activated: # animate from 'on' to 'off'
                self.animationPatchNumber = abs(self.animationFrameCount // self.numberOfFrames)
            else: # animate from 'off' to 'on'
                self.animationPatchNumber = self.numberOfFrames - (self.animationFrameCount // self.numberOfFrames)

    def draw(self, onthissurface):
        patchRect = (self.animationPatchNumber * self.patchWidth, 0,
                       self.patchWidth, self.spriteSheetImage.get_height())
        onthissurface.blit(self.spriteSheetImage,self.positionInWindow,patchRect)

    def flip(self):
        self.animationFrameCount = 1
        self.activated ^= 1

    def turnOn(self):
        self.activated = 1
        self.animationFrameCount = 1

    def turnOff(self):
        self.activated = 0
        self.animationFrameCount = 1


class Board():

    def __init__(self,xdiscs,ydiscs,spritesheetfile,discsize,numberofframes,framerate,sweephoriz,animationdelay):
        self.numDotsX = xdiscs
        self.numDotsY = ydiscs
        self.dotSizeX = discsize
        self.spriteSheetImage = pygame.image.load(spritesheetfile)

        self.majorDimensionIsX = sweephoriz # True = sweep horizontally, False = sweep vertically

        self.timeOfLastStep = 0
        self.lengthOfAnimationStep = animationdelay # milliseconds
        self.currentAnimationStepMajor = ANIDOT_ANIMATION_STOP

        self.dotSizeY = self.spriteSheetImage.get_height()
        self.dotArray = []

        self.windowSizeX = self.dotSizeX * self.numDotsX
        self.windowSizeY = self.dotSizeY * self.numDotsY
        self.window = pygame.display.set_mode((self.windowSizeX,self.windowSizeY))
        self.backgroundSurface = pygame.Surface(self.window.get_size())

        # These two arrays facilitate locating a Dot from window coordinates (e.g. mouse click).
        self.dotTopsides = []
        self.dotLeftsides = []

        for i, topside in enumerate(range(0,self.windowSizeY,self.dotSizeY)):
            self.dotArray.append([])
            self.dotTopsides.append(topside)
            for leftside in range(0,self.windowSizeX,self.dotSizeX):
                if i == 0: self.dotLeftsides.append(leftside)
                self.dotArray[i].append(Dot(self.spriteSheetImage, discsize, numberofframes, framerate, (leftside, topside)))

    def convert(self):
        "Call after __init__ to optimize imagery."
        self.spriteSheetImage.convert()
        self.backgroundSurface = self.backgroundSurface.convert()

    def update(self):
        for i in range(0,self.numDotsY):
            for j in range(0,self.numDotsX):
                self.dotArray[i][j].update()

    def draw(self):
        for i in range(0,self.numDotsY):
            for j in range(0,self.numDotsX):
                self.dotArray[i][j].draw(self.backgroundSurface)

    def blit(self):
        self.window.blit(self.backgroundSurface,(0,0))

    def cycle(self):
        "Display changes made during this frame. Call at end of pygame frame loop."
        self.update()
        self.draw()
        self.blit()
        pygame.display.flip()

    def setBlock(self,xleft,ytop,array):
        for i, charRow in enumerate(array):
            for j, charColumn in enumerate(charRow):
                if charColumn == ANIDOT_DOTBLOCK_OFF:
                    self.dotArray[i][j].turnOff()
                else:
                    self.dotArray[i][j].turnOn()

    def setBlockWithAnimation(self,xleft,ytop,array):
        if not self.animationIsRunning():
            return
        # Do nothing if step is before or after the position of the block--
        #   hence checks of step value before copying block data
        if self.majorDimensionIsX:
            if self.currentAnimationStepMajor < xleft or self.currentAnimationStepMajor >= xleft + len(array[0]):
                return
            for i, charRow in enumerate(array):
                if charRow[self.currentAnimationStepMajor] == ANIDOT_DOTBLOCK_OFF:
                    self.dotArray[i][self.currentAnimationStepMajor].turnOff()
                else:
                    self.dotArray[i][self.currentAnimationStepMajor].turnOn()
        else:
            if self.currentAnimationStepMajor < ytop or self.currentAnimationStepMajor >= ytop + len(array):
                return
            for j, charColumn in enumerate(array[self.currentAnimationStepMajor]):
                if charColumn == ANIDOT_DOTBLOCK_OFF:
                    self.dotArray[self.currentAnimationStepMajor][j].turnOff()
                else:
                    self.dotArray[self.currentAnimationStepMajor][j].turnOn()

    def advanceAnimationStep(self):
        "Move to the next animation step--but only if animation has started, and the specified amount of time has passed since the last frame"
        if pygame.time.get_ticks() - self.timeOfLastStep >= self.lengthOfAnimationStep and self.animationIsRunning():
            self.currentAnimationStepMajor += 1
            # if step is at the end of the dimension, stop animation
            if self.majorDimensionIsX:
                if self.currentAnimationStepMajor >= self.numDotsX:
                    self.currentAnimationStepMajor = ANIDOT_ANIMATION_STOP
            else:
                if self.currentAnimationStepMajor >= self.numDotsY:
                    self.currentAnimationStepMajor = ANIDOT_ANIMATION_STOP
            self.timeOfLastStep = pygame.time.get_ticks()

    def startAnimation(self):
        self.currentAnimationStepMajor = ANIDOT_ANIMATION_START

    def stopAnimation(self):
        self.currentAnimationStepMajor = ANIDOT_ANIMATION_STOP

    def animationIsRunning(self):
        if self.currentAnimationStepMajor >= 0: return True
        return False

    def getDotByWindowCoordinates(self, coords):
        (x, y) = coords
        for i, y_min in enumerate(self.dotTopsides):
            y_max = y_min + self.dotSizeY
            if y >= y_min and y < y_max:
                for j, x_min in enumerate(self.dotLeftsides):
                    x_max = x_min + self.dotSizeX
                    if x >= x_min and x < x_max:
                        return (i, j)
        return None # no dots matched

    def getArea(self, istart, jstart, iend, jend):
        area = []
        for i in range(istart, iend + 1):
            row = []
            for j in range(jstart, jend + 1):
                row.append(self.dotArray[i][j])
            #print map(lambda a: a.activated, row)
            area.append(row)
        return area


class Font():

    kind = 'Font'
    def __init__(self,name,xmax,ymax,baseline=None,gap=1,fromfile=None):
        if fromfile is not None: # TODO some kind of security
            fileObj = pickle.load(open(fromfile,'rb'))
            try:
                if fileObj.kind != 'Font':
                    raise AttributeError # not sure if this is best
            except:
                return
            self.name = fileObj.name
            self.maxDimX = fileObj.maxDimX
            self.maxDimY = fileObj.maxDimY
            self.baselineY = fileObj.baselineY
            self.characters = fileObj.characters
            self.defaultGap = fileObj.defaultGap
        else:
            self.name = name
            self.maxDimX = xmax
            self.maxDimY = ymax
            self.baselineY = baseline
            self.characters = {}
            self.defaultGap = gap

    def setCharacter(self,unichar,dots):
        """
        Given dot arrangement for a Unicode character, (re)define the glyph for
        that character. unichar is the character. dots is either a list of strings,
        or a list of lists of Dot() objects like that returned from Board.getBlock().
        """
        if type(dots) is list:
            height = len(dots)
            if type(dots[0]) is str:
                # List of strings, each string representing a row in the character.
                width = 0
                for rowstring in dots:
                    if len(rowstring) > width:
                        width = len(rowstring)
                self.characters[unichar] = {'dimX': width, 'dimY': height, 'glyph': dots}
            if type(dots[0]) is list:
                if type(dots[0][0]) is Dot:
                    # List of dot objects. Get status of each and assign to the character array.
                    dotsstrings = []
                    width = len(dots[0])
                    height = len(dots)
                    for row in dots:
                        rowstring = ''
                        for col in row:
                            if col.activated == 1:
                                rowstring += ANIDOT_DOTBLOCK_ON
                            else:
                                rowstring += ANIDOT_DOTBLOCK_OFF
                        dotsstrings.append(rowstring)
                    self.characters[unichar] = {'dimX': width, 'dimY': height, 'glyph': dotsstrings}
        else:
            return False

    def sumWidthsOfCharactersInString(self,string):
        totalWidth = 0
        for c in string:
            try:
                totalWidth += self.characters[c]['dimX']
            except KeyError: # character not defined
                totalWidth += self.maxDimX
        return totalWidth

    def makeBlockFromString(self,string):
        stringBlock = []
        if len(string) < 1: return
        block = [[0] * (self.sumWidthsOfCharactersInString(string) + self.defaultGap *
                        (len(string) - 1))] * self.maxDimY
        for row in range(0,self.maxDimY):
            marker = 0
            for character in string:
                for cell in self.characters[character]['glyph'][row]:
                    if cell == ANIDOT_DOTBLOCK_OFF:
                        block[row][marker] = 0
                    else:
                        block[row][marker] = 1
                    marker += 1
                marker += self.defaultGap
            # copy row to output as a string
            stringBlock.append(''.join(map(lambda x: (x and ANIDOT_DOTBLOCK_ON) or ' ', block[row])))
        return stringBlock

    def saveToFile(self,name):
        pickle.dump(self,open(name,'wb'))


class Image():

    kind = 'Image'
    def __init__(self,name,cellArray,fromfile=None):
        if fromfile is not None: # TODO some kind of security
            fileObj = pickle.load(open(fromfile,'rb'))
            try:
                if fileObj.kind != 'Image':
                    raise AttributeError # not sure if this is best
            except:
                return
            self.name = fileObj.name
            self.cellArray = fileObj.cellArray
        else:
            self.name = name
            self.cellArray = cellArray

    def makeFromBoard(self,boardObj):
        self.cellArray = []
        for dotRow in boardObj.dotArray:
            imageRow = []
            for dot in dotRow:
                imageRow.append(dot.activated)
            self.cellArray.append(imageRow)

    def saveToFile(self,name):
        pickle.dump(self,open(name,'wb'))

    def flipCell(self,r,c):
        self.cellArray[r][c] ^= 1
        return self.cellArray[r][c]


class TextField():

    def __init__(self,text,font,xpos,ypos,clear=False):
        self.text = text
        self.font = font # Font instance
        self.xpos = xpos
        self.ypos = ypos
        self.clear = clear # if True, clear board when loaded


class Sequence():
    """
    A predefined series of actions to be played back.
    Actions are:
      LoadImage - supply arg to load from filename or object - otherwise Image obj is saved in sequence
      ShowText - arg to load from filename/object - otherwise Board.getArea() array saved in sequence
      Pause - do nothing for specified number of seconds (arg)
      Restart - go back immediately to first action
    If a Restart is not encountered the sequence will stop after all actions have been executed.
    """

    kind = 'Sequence'
    # actionArgs defines the permissible actions, and types for each's argument.
    actionArgs = {
        'LoadImage': (str, Image),
        'ShowText': (str, Font),
        'Pause': (float),
        'Restart': ()
    }
    def __init__(self,name,fromfile=None):
        if fromfile is not None: # TODO some kind of security
            fileObj = pickle.load(open(fromfile,'rb'))
            try:
                if fileObj.kind != 'Sequence':
                    raise RuntimeError('File does not contain a Sequence object')
            except:
                return
            self.name = fileObj.name
            self.actions = fileObj.actions
        else:
            self.name = name
            self.actions = []

    def addAction(self,action,arg=None,position=None):
        """
        :param action: one of the predefined action names, as string
        :param arg: filename, object, time spec, string, list
        :param position: Where to put the action in the sequence. If None, append.
        :return: None
        """
        if action not in actionArgs:
            raise RuntimeError('Invalid action')
            return
        if action == 'LoadImage':
            if isinstance(arg,str):
                pass
                # load from filename
            elif isinstance(arg,Image):
                self.actions.append(arg)
            else:
                raise RuntimeError('Supplied argument is invalid for LoadImage action')
        if action == 'ShowText':
            if isinstance(arg,str):
                # load from filename
                pass
            elif isinstance(arg,Image):
                pass
                # use image object
            else:
                raise RuntimeError('Supplied argument is invalid for LoadImage action')
        if action == 'Pause':
            if isinstance(arg,float):
                # set value
                pass
            else:
                raise RuntimeError('Supplied argument is invalid for Pause action')
        #self.actions.append or whatever


    def next(self,boardObj,arg=None):
        """
        Perform next action in self.actions on boardObj. arg is used to link action to an existing file or object.
        :param boardObj: An object of class Board on which the action is to be played.
        :param arg: If filename, load appropriate object from file. If object, use Image or Font object for this action.
        :return: None
        """
