DungeonGenerator
================

A procedural dungeon generator made with Python and a really simple 2D representation in Löve. The algo works like this (if I recall correctly):

* The first thing is to feed it the minimum and maximum sizes (width and height) for the small, medium and alrge rooms.
* Selects a starting wall, and palces a random room there. The walls of this room are added to the pool of free walls.
* A random wall is selected, and a room is placed connected to that wall. If the new room collides with another room it gets discarded, and instead it tries to place hallway connecting the room from which we brached off of and the room with which we collided.
* The previous step is repeated until there are no more available walls or there are enough rooms.

I got it working as I intended, but I didn't develop it further. A code cleanup is much needed.

