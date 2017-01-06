import pygame
import anidot
import random

frameRate = 1200
spriteSheetFile = 'megamax-10px.png'
# download this font from https://hea-www.harvard.edu/~fine/Tech/x11fonts.html
fontFile = '/home/jcw/fonz/atari-small.bdf'

pygame.init()
clock = pygame.time.Clock()
discsize = 10
nframes = 6
xdiscs = 40
ydiscs = 7
sweepHorizontally = True
delayBetweenSteps = 20
board = anidot.Board(xdiscs,ydiscs,spriteSheetFile,discsize,nframes,sweepHorizontally,delayBetweenSteps)
board.convert()
block = []
baselineRow = None
fontx = anidot.Font(fontFile)
while True:
    clock.tick(frameRate)
    board.advanceAnimationStep()
    currentEvent = pygame.event.poll()
    if currentEvent.type == pygame.QUIT:
        break
    if currentEvent.type == pygame.KEYDOWN:
        if currentEvent.dict['key'] == pygame.K_ESCAPE:
            pygame.quit()
            break
        if currentEvent.dict['unicode'] == ' ':
            text = ''
            for i in xrange(10):
                text = text + chr(random.randint(33,122))
            print 'text is {0:s}'.format(text)
            (baselineRow, block) = fontx.makeBlockFromString(text)
            print '\n'.join(block)
            board.startAnimation()
    board.setBlockWithAnimation(0,6,block,baselineRow)
    board.cycle()
