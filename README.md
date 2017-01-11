# AniDot
by Jake Wimberley
(last name without the y) + j at gmail dot com

## Introduction

I have been fascinated by electromechanical "flip-dot" (or "flip-disc")
displays for a long time. AniDot is a library to visually simulate these types
of displays. It is a work in progress.

Most folks have probably seen flip-dot displays as traffic information signs on
superhighways, as destination signs on some transit buses, and on TV game
shows. (US users may remember the "big board" used in the final round of the
Richard Dawson and Ray Combs versions of *Family Feud*.) The vast improvements
in LED technology during the 1990s led to many displays being replaced with
cheaper, more reliable, and often multi-color LED displays. A compelling
advantage of flip-dots, however, is that they only require power to *change*,
i.e., they retain the display state without power.

I am nostalgic about technology and have an appreciation for "character." To
me, flip-dots, with their relatively low resolution, mechanical flaws and
clacking sounds, have more character than do their LED descendants, and that's
what draws me to them.

AniDot is built on top of Pygame. The simulation runs as a Pygame window, and
the library provides the capability to pickle simulation data so they can be
saved and reloaded. A primary goal is to support both the display of
information as an image (any specific arrangement of dots) as well as arbitrary
text rendered using a font.

As there are a number of possible uses of AniDot, it was implemented as a
library. Some example applications are provided.


## Theory

Flip-dot displays operate using magnetized discs arranged in a regular grid.
Each side of a disc is a different color (typically one black, one yellow), and
each is mounted on a pivot. Electromagnetic coils turn the discs to flip them
between 'off' and 'on' states. A quick search of Google Patents reveals a
number of specific designs, but this is the general idea. At least in some
designs, the discs are changed state one at a time. Often, the electrical state
of one row or column of dots is changed very quickly, but the selected
row/column changes slowly enough that a sweeping effect is seen across the
array as the dots begin to turn at different times. However, modern solid-state
switching circuitry is capable of changing the electrical state of the grid
faster than the discs' inertia would allow them to move, such that all discs
appear to change at the same time.

In AniDot, animation is accomplished using sprite sheets to permit a
high-resolution depiction of a real display. Consult the Pygame documentation
for a complete explanation of sprite sheets. Each frame of the sheet represents
a different position of a turning disc element. Timing is carefully controlled,
and the user can choose to make the status changes occur slowly enough that the
sweeping effect can be replicated.

## Getting started 

Depending on how realistic you want the animation to look, and how powerful
your graphics adapter is, you can choose as many or as few frames as you like.
I created some spritesheets in SVG format, that you can use to make raster
sheets of any size you wish. Of course, you can make your own spritesheets
using another method.

So after fetching the package, the first step is to create raster spritesheets
(PNG, GIF, etc.). Inkscape's *Export PNG Image* or *Export Bitmap* feature does
a great job of this if you choose to use the included SVGs. AniDot assumes that
a sprite sheet is composed of square frames arranged from left to right, in the
order "fully off" to "fully on". You will need to make sure the dimension of
each frame matches the configured disc size in your program. So, following the
convention of square frames, the height of the raster is the disc size.

## Provided examples

- basicLoop.py is an extremely basic AniDot window that loads the digits 0-9,
  plus lowercase "a", to a small board when those keys are pressed. This script
  is configured to use the "20px Ferranti" spritesheet, which mimics the
  appearance of the once common Ferranti-Packard discs.
- showStringWithFont.py renders a random 6-character string using a BDF font.
  Press the spacebar to load a new string. This one uses the "10px MegaMAX"
  spritesheet, which is a rendition of discs from the Luminator GTI MegaMAX
  destination sign.
