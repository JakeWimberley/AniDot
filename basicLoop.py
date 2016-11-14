__author__ = 'jcw'
import pygame
import anidot

frameRate = 1200
spriteSheetFile = '/home/jcw/dev/ferranti.png'
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


def main():
    pygame.init()
    clock = pygame.time.Clock()
    discsize = 21
    nframes = 12
    xdiscs = 5
    ydiscs = 7
    sweepHorizontally = True
    delayBetweenSteps = 80
    board = anidot.Board(xdiscs,ydiscs,spriteSheetFile,discsize,nframes,frameRate,sweepHorizontally,delayBetweenSteps)
    board.convert()
    charArray = []
    while True:
        clock.tick(frameRate)
        board.advanceAnimationStep()
        currentEvent = pygame.event.poll()
        if currentEvent.type == pygame.QUIT:
            break
        if currentEvent.type == pygame.KEYDOWN:
            if currentEvent.dict['key'] == 27: # ESC
                pygame.quit()
                break
            keyPressed = currentEvent.dict['unicode']
            if keyPressed in fontDef.keys():
                charArray = fontDef[keyPressed]
                board.startAnimation()
        if currentEvent.type == pygame.MOUSEBUTTONDOWN:
            (clickedi, clickedj) = board.getDotByWindowCoordinates(currentEvent.dict['pos'])
            board.dotArray[clickedi][clickedj].flip()
        board.setBlockWithAnimation(0,0,charArray)
        board.cycle()


if __name__ == '__main__': main()
