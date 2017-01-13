import pygame
import anidot

frameRate = 240 # set higher than usual for this script
spriteSheetFile = 'megamax-10px.png'

pygame.init()
clock = pygame.time.Clock()
pygame.event.set_allowed(None)
pygame.event.set_allowed((pygame.KEYDOWN,pygame.MOUSEBUTTONDOWN,pygame.MOUSEBUTTONUP,pygame.MOUSEMOTION,pygame.QUIT,pygame.USEREVENT))

discsize = 10
nframes = 6
xdiscs = 112
ydiscs = 16
sweepHorizontally = True
delayBetweenSteps = 50
board = anidot.Board(xdiscs,ydiscs,spriteSheetFile,discsize,nframes,sweepHorizontally,delayBetweenSteps)

toggleDots = False
lastI = -1
lastJ = -1
inc = 0
while True:
    clock.tick(frameRate)
    board.advanceAnimationStep()
    currentEvent = pygame.event.poll()
    if currentEvent.type == pygame.QUIT:
        break
    if currentEvent.type == pygame.USEREVENT:
        # handle change event
        (flipI,flipJ) = currentEvent.dict['ij']
        if currentEvent.dict['button'] == 1:
            board.dotArray[flipI][flipJ].turnOn()
        if currentEvent.dict['button'] == 3:
            board.dotArray[flipI][flipJ].turnOff()
    if currentEvent.type == pygame.KEYDOWN:
        if currentEvent.dict['key'] == pygame.K_ESCAPE:
            pygame.quit()
            break
        if currentEvent.dict['unicode'] == 'p': # Play
            pass
        if currentEvent.dict['unicode'] == 's': # Save
            pass
        if currentEvent.dict['unicode'] == 'n': # New action (exposure)
            pass
    if currentEvent.type == pygame.MOUSEBUTTONDOWN:
        # post change event (MOUSEMOTION won't pick up the dot under BUTTONDOWN)
        # also record start of cursor drag
        toggleDots = True
        (nowI,nowJ) = board.getDotByWindowCoordinates(currentEvent.dict['pos'])
        pygame.event.post(pygame.event.Event(pygame.USEREVENT,{'ij': (nowI,nowJ), 'button': currentEvent.dict['button']}))
        (lastI,lastJ) = (nowI,nowJ)
    if currentEvent.type == pygame.MOUSEBUTTONUP:
        toggleDots = False
    if currentEvent.type == pygame.MOUSEMOTION:
        if toggleDots: # post change event to queue if mouse has moved to new dot
            (nowI,nowJ) = board.getDotByWindowCoordinates(currentEvent.dict['pos'])
            if nowI != lastI or nowJ != lastJ:
                button = None
                if currentEvent.dict['buttons'][0] == 1: button = 1
                elif currentEvent.dict['buttons'][2] == 1: button = 3
                pygame.event.post(pygame.event.Event(pygame.USEREVENT,{'ij': (nowI,nowJ), 'button': button}))
            (lastI,lastJ) = (nowI,nowJ)
    board.cycle()
