import pygame
import anidot
import random

frameRate = 1200
spriteSheetFile = '/home/jcw/dev/megamax-10px.png'
fontFile = 'test.df'

fontDef = {
    'a': ['     ',
          '0000 ',
          '    0',
          '00000',
          '0   0',
          '0   0',
          ' 0000'],
    '1': ['  0  ',
          ' 00  ',
          '  0  ',
          '  0  ',
          '  0  ',
          '  0  ',
          ' 000 '],
    '2': [' 000 ',
          '0   0',
          '    0',
          '   0 ',
          '  0  ',
          ' 0   ',
          '00000'],
    '3': [' 0000',
          '    0',
          '   0 ',
          '  00 ',
          '    0',
          '0   0',
          ' 000 '],
    '4': ['   0 ',
          '  00 ',
          ' 0 0 ',
          '0  0 ',
          '00000',
          '   0 ',
          '   0 '],
    '5': ['00000',
          '0    ',
          '0    ',
          ' 000 ',
          '    0',
          '0   0',
          ' 000 '],
    '6': ['  00 ',
          ' 0   ',
          '0    ',
          '0 00 ',
          '00  0',
          '0   0',
          ' 000 '],
    '7': ['00000',
          '    0',
          '   0 ',
          '  0  ',
          ' 0   ',
          ' 0   ',
          ' 0   '],
    '8': [' 000 ',
          '0   0',
          '0   0',
          ' 000 ',
          '0   0',
          '0   0',
          ' 000 '],
    '9': [' 000 ',
          '0   0',
          '0   0',
          ' 000 ',
          '  0  ',
          ' 0   ',
          '0    '],
    '0': [' 000 ',
          '0   0',
          '0  00',
          '0 0 0',
          '00  0',
          '0   0',
          ' 000 '],
}



pygame.init()
clock = pygame.time.Clock()
discsize = 10
nframes = 6
xdiscs = 25
ydiscs = 7
sweepHorizontally = True
delayBetweenSteps = 50
board = anidot.Board(xdiscs,ydiscs,spriteSheetFile,discsize,nframes,frameRate,sweepHorizontally,delayBetweenSteps)
board.convert()
intBlock = []
font = anidot.Font('Test',xmax=5,ymax=7,baseline=None,gap=1)
fontx = anidot.Font('',1,1,fromfile=fontFile)
for c in fontDef:
    font.setCharacter(c,fontDef[c])
while True:
    clock.tick(frameRate)
    board.advanceAnimationStep()
    currentEvent = pygame.event.poll()
    if currentEvent.type == pygame.QUIT:
        break
    if currentEvent.type == pygame.KEYDOWN:
        if currentEvent.dict['unicode'] == 27:
            pygame.quit()
            break
        if currentEvent.dict['unicode'] == ' ':
            intStr = '{0:04x}'.format(random.randint(0,2**16-1))
            print 'int is {0:s}'.format(intStr)
            intBlock = fontx.makeBlockFromString(intStr)
            board.startAnimation()
    board.setBlockWithAnimation(0,0,intBlock)
    board.cycle()