import pygame, pickle, sys

sys.path.append('bdflib')
from bdflib import reader as bdflibReader, model as bdflibModel

# Constants
ANIDOT_DOTBLOCK_OFF = ' '
ANIDOT_DOTBLOCK_ON = 'X'
ANIDOT_ANIMATION_STOP = -1
ANIDOT_ANIMATION_START = 0
ANIDOT_ACTION_LOADIMAGE = pygame.USEREVENT + 100
ANIDOT_ACTION_SHOWTEXT = ANIDOT_ACTION_LOADIMAGE + 1
ANIDOT_ACTION_PAUSE = ANIDOT_ACTION_LOADIMAGE + 2
ANIDOT_ACTION_RESTART = ANIDOT_ACTION_LOADIMAGE + 3
ANIDOT_ACTIONS = (ANIDOT_ACTION_LOADIMAGE,ANIDOT_ACTION_SHOWTEXT,ANIDOT_ACTION_PAUSE,ANIDOT_ACTION_RESTART)


class Dot(pygame.sprite.Sprite):

    def __init__(self, spritesheet, patchwidth, numberframes, position):
        self.spriteSheetImage = spritesheet
        self.patchWidth = patchwidth
        self.numberOfFrames = numberframes # TODO should probably be called numberOfPatches
        self.positionInWindow = position
        self.animationFrameCount = 0
        self.animationPatchNumber = 0
        self.activated = 0 # corresponds to the electrical state of the dot element
        self.initialized = False

    def update(self):
        """
        Calculate the patch that represents the current angle of the disc.
        If self.animationFrameCount is positive, animation is in progress.
        Otherwise, nothing about the dot has changed since last update.
        This will be called once per dot per pygame frame loop.
        """
        if self.animationFrameCount > 0 and self.animationPatchNumber != self.numberOfFrames * self.activated:
            self.animationFrameCount = self.animationFrameCount + 1 # originally I had (aFC) % self.frameRate, but can't remember why
            if self.activated: # animate from 'off' to 'on' (remember patch 0 is supposed to be 'fully off')
                self.animationPatchNumber = abs(self.animationFrameCount // self.numberOfFrames)
            else: # animate from 'on' to 'off'
                self.animationPatchNumber = self.numberOfFrames - (self.animationFrameCount // self.numberOfFrames)
        else:
            self.animationFrameCount = 0 # this resets animation, prevents self.draw() from being called unnecessarily

    def draw(self, onthissurface):
        """
        Blit the patch from the spritesheet that corresponds to the current value of self.animationPatchNumber.
        The patch number should have been set by self.update().
        Don't do anything if animationFrameCount is zero (no animation in progress), except when the element is first drawn.
        """
        if self.animationFrameCount != 0 or self.initialized == False:
            patchRect = (self.animationPatchNumber * self.patchWidth, 0,
                           self.patchWidth, self.spriteSheetImage.get_height())
            onthissurface.blit(self.spriteSheetImage,self.positionInWindow,patchRect)
            self.initialized = True

    def flip(self,animate=True):
        self.animationFrameCount = 1
        if animate: self.activated ^= 1

    def flipNow(self): #TODO
        self.animationFrameCount = self.numberOfFrames - 2
        self.activated ^= 1

    def turnOn(self,animate=True):
        self.activated = 1
        if animate: self.animationFrameCount = 1

    def turnOff(self,animate=True):
        self.activated = 0
        if animate: self.animationFrameCount = 1


class Board():

    def __init__(self,xdiscs,ydiscs,spritesheetfile,discsize,numberofframes,sweephoriz,animationdelay):
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
                self.dotArray[i].append(Dot(self.spriteSheetImage, discsize, numberofframes, (leftside, topside)))
        
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
        "Blit the background surface (onto which dots have been blitted) into the window."
        self.window.blit(self.backgroundSurface,(0,0))

    def cycle(self):
        "Display changes made during this frame. Call at end of pygame frame loop."
        self.animate()
        self.update()
        self.draw()
        self.blit()
        pygame.display.flip()

    def setBlock(self,ytop,xleft,array,baseline=0):
        arrayYDim = len(array)
        for i, charRow in enumerate(array):
            if baseline != 0:
                iDot = i + ytop - baseline + 1
            else:
                iDot = i + ytop
            if iDot < 0: continue
            for j, charColumn in enumerate(charRow):
                jDot = j + xleft
                if jDot < 0: continue
                try:
                    if charColumn == ANIDOT_DOTBLOCK_OFF:
                        self.dotArray[iDot][jDot].turnOff(animate=False)
                    else:
                        self.dotArray[iDot][jDot].turnOn(animate=False)
                except IndexError:
                    pass # outside the Board edge

    def animate(self):
        "Manage the animation: change the dots at the current animation step."
        if not self.animationIsRunning():
            return
        if self.majorDimensionIsX:
            for i in xrange(self.numDotsY):
                if self.dotArray[i][self.currentAnimationStepMajor].activated == 0:
                    self.dotArray[i][self.currentAnimationStepMajor].turnOff()
                else:
                    self.dotArray[i][self.currentAnimationStepMajor].turnOn()
        else:
            for j in xrange(self.numDotsX):
                if self.dotArray[self.currentAnimationStepMajor][j].activated == 0:
                    self.dotArray[self.currentAnimationStepMajor][j].turnOff()
                else:
                    self.dotArray[self.currentAnimationStepMajor][j].turnOn()

    def advanceAnimationStep(self):
        "Move to the next animation step--but only if animation has started, and the specified amount of time has passed since the last frame. This should be called at the beginning of the pygame frame loop, preferably after clock.tick()."
        if self.animationIsRunning() and pygame.time.get_ticks() - self.timeOfLastStep >= self.lengthOfAnimationStep:
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

    def clear(self,animate=True):
        for i in xrange(self.numDotsY):
            for j in xrange(self.numDotsX):
                self.dotArray[i][j].turnOff(animate)


class Font():

    def __init__(self,bdfFileName):
        with open(bdfFileName,'r') as bdfFileObj:
            self.bdf = bdflibReader.read_bdf(bdfFileObj)

    def sumWidthsOfCharactersInString(self,string):
        # TODO bdf-ify
        totalWidth = 0
        for c in string:
            try:
                totalWidth += self.characters[c]['dimX']
            except KeyError: # character not defined
                totalWidth += self.maxDimX
        return totalWidth

    def makeBlockFromString(self,string,tracking=0,rightToLeft=False):
        '''
        Using bdflib's glyph-combination capability, make a new glyph
        to display all the characters in a string. Return value is a tuple:
          (baselineRow, block)
        baselineRow is the index of the row that is the text baseline
        block is an AniDot block for use with Board.setBlock()
        '''
        stringBlock = []
        if len(string) < 1: return (None,[[]])
        combinedGlyph = bdflibModel.Glyph('combined')
        firstChar = True
        for c in string:
            nextChar = self.bdf.glyphs_by_codepoint[ord(c)]
            if firstChar == True: atX = combinedGlyph.bbW
            else: atX = combinedGlyph.bbW + tracking
            atY = 0
            # TODO rightToLeft capability
            combinedGlyph.merge_glyph(nextChar,atX,atY)
            firstChar = False
        # describe length of each row of decoded data (padded to multiple of 8)
        decodedFormatStr = '{0:0' + str(combinedGlyph.bbW - (combinedGlyph.bbW % 8)) + 'b}'
        #decodedFormatStr = '{0:0' + str(combinedGlyph.bbW + (combinedGlyph.bbW % 8)) + 'b}'
        for encodedRow in combinedGlyph.get_data():
            # each character in the encoded string represents 4 dots
            decodedRow = ''
            for char in encodedRow: decodedRow += '{0:04b}'.format(int(char,16))
            # reformat string of digits per AniDot spec
            stringBlock.append(''.join(map(lambda c: (int(c) and ANIDOT_DOTBLOCK_ON) or ' ', decodedRow)))
        return (combinedGlyph.bbH + combinedGlyph.bbY, stringBlock)


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
      ShowText - args are font filename, string to display, (x,y)
      Pause - do nothing for specified number of seconds (arg)
      Restart - go back immediately to first action
    If a Restart is not encountered the sequence will stop after all actions have been executed.
    """

    kind = 'Sequence'
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
        :param action: one of the predefined ANIDOT_ACTION_* constants
        :param arg: filename, object, time spec, string, list
        :param position: Where to put the action in the sequence. If None, append.
        :return: None
        """
        if action not in ANIDOT_ACTIONS:
            raise RuntimeError('Invalid action')
            return
        if action == ANIDOT_ACTION_LOADIMAGE:
            if isinstance(arg,str):
                pass
                # load from filename
            elif isinstance(arg,Image):
                actionArgs = {'imageObject':arg}
            else:
                raise RuntimeError('Supplied argument is invalid for LoadImage action')
        if action == ANIDOT_ACTION_SHOWTEXT:
            # Put opened Font instances in a dictionary - reuse
            if isinstance(arg[0],str) and isinstance(arg[1],str) and isinstance(arg[2],tuple):
                actionArgs = {
                    'fontFile': arg[0],
                    'string': arg[1],
                    'xy': arg[2]
                }
            else:
                raise RuntimeError('Supplied argument(s) invalid for ShowText action')
        if action == ANIDOT_ACTION_PAUSE:
            if isinstance(arg,float):
                actionArgs = {'length':arg}
            else:
                raise RuntimeError('Supplied argument is invalid for Pause action')
        if action == ANIDOT_ACTION_RESTART:
            actionArgs = {}
        if position is not None:
            self.actions.insert(position,pygame.event.Event(action,actionArgs))
        else:
            self.actions.append(pygame.event.Event(action,actionArgs))


    def next(self,boardObj,arg=None):
        """
        Perform next action in self.actions on boardObj. arg is used to link action to an existing file or object.
        :param boardObj: An object of class Board on which the action is to be played.
        :param arg: If filename, load appropriate object from file. If object, use Image or Font object for this action.
        :return: None
        """
