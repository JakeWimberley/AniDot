import pygame
import anidot
import random

frameRate = 1200
spriteSheetFile = 'megamax-10px.png'
fontFile = '/home/jcw/fonz/luminator_8.bdf'
# if you want to try unicode,
# use this font from https://hea-www.harvard.edu/~fine/Tech/x11fonts.html
# fontFile = '/home/jcw/fonz/unifont-9.0.04.bdf'

pygame.init()
clock = pygame.time.Clock()
discsize = 10
nframes = 6
xdiscs = 90
ydiscs = 20
sweepHorizontally = True
delayBetweenSteps = 10
board = anidot.Board(xdiscs,ydiscs,spriteSheetFile,discsize,nframes,sweepHorizontally,delayBetweenSteps)
fontx = anidot.Font(fontFile)
while True:
    clock.tick(frameRate)
    board.advanceAnimationStep()
    currentEvent = pygame.event.poll()
    if currentEvent.type == pygame.QUIT:
        break
    if currentEvent.type == pygame.MOUSEBUTTONDOWN:
        (clickedi, clickedj) = board.getDotByWindowCoordinates(currentEvent.dict['pos'])
        text = ''
        for i in xrange(10):
            text = text + chr(random.randint(0x41,0x5A))
            #text = text + chr(random.randint(33,122))
        print 'text is {0:s}, at {1:d},{2:d}'.format(text,clickedi,clickedj)
        (baselineRow, block) = fontx.makeBlockFromString(text)
        print '\n'.join(block)
        board.setBlock(clickedi,clickedj,block,baselineRow)
        board.startAnimation()
    if currentEvent.type == pygame.KEYDOWN:
        if currentEvent.dict['key'] == pygame.K_ESCAPE:
            pygame.quit()
            break
        if currentEvent.dict['unicode'] == 'c':
            # sweeping clear
            board.clear(animate=False)
            board.startAnimation()
        if currentEvent.dict['unicode'] == 'C':
            # clear simultaneously--no sweep
            board.clear()
    board.cycle()
