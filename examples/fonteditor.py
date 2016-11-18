__author__ = 'jcw'
import pygame
import anidot

frameRate = 1200
spriteSheetFile = 'ferranti20px.png'
fontFileIn = 'test.df'
fontFileOut = 'new.test.df'

pygame.init()
clock = pygame.time.Clock()
discsize = 21
nframes = 12
xdiscs = 5
ydiscs = 7
sweepHorizontally = True
delayBetweenSteps = 80
board = anidot.Board(xdiscs,ydiscs,spriteSheetFile,discsize,nframes,sweepHorizontally,delayBetweenSteps)
board.convert()
charArray = []
editChar = ''
prevEditChar = ''
fontx = anidot.Font('test',xdiscs,ydiscs)
while True:
    clock.tick(frameRate)
    board.advanceAnimationStep()
    currentEvent = pygame.event.poll()
    if currentEvent.type == pygame.QUIT:
        break
    if currentEvent.type == pygame.KEYDOWN:
        keyPressed = currentEvent.dict['unicode']
        prevEditChar = editChar
        editChar = keyPressed
        if currentEvent.dict['key'] == 27: # ESC
            pygame.quit()
            break
        if currentEvent.dict['key'] == 278: # Home
            fontx = anidot.Font(fromfile=fontFileIn)
        if currentEvent.dict['key'] == 279: # End
            fontx.saveToFile(fontFileOut)
        if currentEvent.dict['key'] == 13: # Enter
            fontx.setCharacter(prevEditChar,board.getArea(0,0,board.numDotsY-1,board.numDotsX-1))
        print currentEvent.dict['key']
        if editChar in fontx.characters.keys():
            charArray = fontx.characters[editChar]['glyph']
        else:
            charArray = [[anidot.ANIDOT_DOTBLOCK_OFF] * xdiscs] * ydiscs
        board.startAnimation()
    if currentEvent.type == pygame.MOUSEBUTTONDOWN:
        (clickedi, clickedj) = board.getDotByWindowCoordinates(currentEvent.dict['pos'])
        board.dotArray[clickedi][clickedj].flip()
    board.setBlockWithAnimation(0,0,charArray)
    board.cycle()
