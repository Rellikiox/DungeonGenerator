from vec2d import Vec2d

import sys
import random
import math

class Dungeon():
	width = -1
	height = -1
	min_sizes = None
	max_sizes = None
	grid = None
	rooms = None
	
	def __init__(self, width, height, mins, maxs):
		self.width = width
		self.height = height
		self.min_sizes = list(mins)
		self.max_sizes = list(maxs)
		
		self.grid = [ ['.'] * width for i in range(height) ]
		
		self.rooms = []
		
	def placeEntrance(self):
		first_room = self.getNextRoom()
		
		entr_pos = Vec2d(random.randint(1, self.width - 2), random.randint(1, self.height - 2))
		
		entr_pos.x, entr_pos.y, direction = random.choice([
			lambda : (0, entr_pos.y, "w"),
			lambda : (self.width - 1, entr_pos.y, "e"),
			lambda : (entr_pos.x, 0, "n"),
			lambda : (entr_pos.x, self.height - 1, "s")])()
		

		hallway = Hallway(entr_pos, entr_pos)
		self.grid[entr_pos.y][entr_pos.x] = '*'
		first_room.hallways[Room.invertDirection(direction)].append(hallway)

		self.placeRoom(first_room, entr_pos, direction)
		self.printRoom(first_room)

		self.rooms.append(first_room)

	
	def generate(self):
		rooms_left = [ r for r in self.rooms if r.walls != "" ]
		tries = 0
		while len(rooms_left) > 0 and tries < 500:
			tries += 1
			start_room = random.choice( rooms_left )
			start_wall = random.choice( start_room.walls )
			start_room.removeWall(start_wall)
			
			p_out = start_room.getPointInWall(start_wall)
			while self.pointOutside(p_out) and start_room.walls != "":
				start_wall = random.choice( start_room.walls )
				start_room.removeWall(start_wall)
				p_out = start_room.getPointInWall(start_wall)
			
			if self.pointOutside(p_out):
				rooms_left = [ r for r in self.rooms if r.walls != "" ]
				continue	
			
			new_room = self.getNextRoom()
			
			self.placeRoom(new_room, p_out, Room.invertDirection(start_wall))				
			
			if not self.fixRoom(new_room):
				rooms_left = [ r for r in self.rooms if r.walls != "" ]
				continue

			# Check collisions with other rooms
			collides = False
			for r in self.rooms:
				if new_room.collidesWith(r):
					dir_start_r = start_room.getDirection(r)
					if dir_start_r == start_wall and not start_room.connectedTo(r):
						overlap = start_room.getOverlap(r)
						if overlap[0][1] - overlap[0][0] > 2:
							distance = start_room.distance(r)
							if 0 <= distance[1] <= 5:							
								if dir_start_r == "n": 
									h_x_pos = random.randint(overlap[0][0] + 1, overlap[0][1] - 1)
									h_start = Vec2d(overlap[0][0] + 1, r.p.y + r.h) 
									h_end = Vec2d(overlap[0][0] + 1, start_room.p.y - 1)
									hallway = Hallway(h_start, h_end)
									self.createConnection(start_room, dir_start_r, hallway, r)
								elif dir_start_r == "s":
									h_x_pos = random.randint(overlap[0][0] + 1, overlap[0][1] - 1)
									h_start = Vec2d(overlap[0][0] + 1, start_room.p.y + start_room.h)
									h_end = Vec2d(overlap[0][0] + 1, r.p.y - 1)
									hallway = Hallway(h_start, h_end)
									self.createConnection(start_room, dir_start_r, hallway, r)

						elif overlap[1][1] - overlap[1][0] > 2:
							distance = start_room.distance(r)
							if 0 <= distance[0] <= 5:
								if dir_start_r == "e":
									h_y_pos = random.randint(overlap[1][0] + 1, overlap[1][1] - 1)
									h_start = Vec2d(start_room.p.x + start_room.w, h_y_pos)
									h_end = Vec2d(r.p.x - 1 , h_y_pos)
									hallway = Hallway(h_start, h_end)
									self.createConnection(start_room, dir_start_r, hallway, r)
								elif dir_start_r == "w":
									h_y_pos = random.randint(overlap[1][0] + 1, overlap[1][1] - 1)
									h_start = Vec2d(r.p.x + r.w, h_y_pos)
									h_end = Vec2d(start_room.p.x - 1 , h_y_pos)
									hallway = Hallway(h_start, h_end)
									self.createConnection(start_room, dir_start_r, hallway, r)
					collides = True

			if collides:
				rooms_left = [ r for r in self.rooms if r.walls != "" ]
				continue

			self.rooms.append(new_room)
			self.printRoom(new_room)

			hallway = Hallway(p_out, p_out)
			self.createConnection(start_room, start_wall, hallway, new_room)
			
			rooms_left = [ r for r in self.rooms if r.walls != "" ]
			
		self.setRoomLevel(self.rooms[0], 0)
		self.printRoomLevels()
	
	def printRoom(self, room):
		for i in range(0, room.h):
			for j in range(0, room.w):
				self.grid[room.p.y + i][room.p.x + j] = '#'

	def createConnection(self, room_a, d, hallway, room_b):
		room_a.rooms[d].append(room_b)
		room_a.hallways[d].append(hallway)
		room_a.removeWall(d)

		inv_d = Room.invertDirection(d)
		room_b.rooms[inv_d].append(room_a)
		room_b.hallways[inv_d].append(hallway)
		room_b.removeWall(inv_d)
		# Draw the hallway
		for i in range(hallway.start.y, hallway.end.y + 1):
			for j in range(hallway.start.x, hallway.end.x + 1):
				self.grid[i][j] = '*'


	def setRoomLevel(self, room, lvl):
		if room.level != -1 and room.level < lvl:
			return
		room.level = lvl
		for k, v in room.rooms.items():
			for r in v:
				self.setRoomLevel(r, lvl + 1)
	
	def printRoomLevels(self):
		for r in self.rooms:
			if r.level < 10:
				self.grid[r.p.y][r.p.x] = str(r.level)
			else:
				self.grid[r.p.y][r.p.x] = str(r.level)[0]
				if r.p.x < self.width - 1:
					self.grid[r.p.y][r.p.x + 1] = str(r.level)[1]
				else:
					self.grid[r.p.y + 1][r.p.x] = str(r.level)[1]

	def getNextRoom(self):
		kind = random.randint(0,2)
		width = random.randint(self.min_sizes[kind], self.max_sizes[kind])
		height = random.randint(self.min_sizes[kind], self.max_sizes[kind])
		return Room(width, height, kind)
		
	def placeRoom(self, room, pos, d):
		if d == "n":
			room.p.x = pos.x - int(room.w / 2)
			room.p.y = pos.y + 1
		elif d == "s":
			room.p.x = pos.x - int(room.w / 2)
			room.p.y = pos.y - room.h
			
		elif d == "e":
			room.p.x = pos.x - room.w
			room.p.y = pos.y - int(room.h / 2)
			
		elif d == "w":
			room.p.x = pos.x + 1
			room.p.y = pos.y - int(room.h / 2)
			
			
		room.removeWall(d)
	
	def fixRoom(self, room):		
		return not self.pointOutside(room.p) and not self.pointOutside(Vec2d(room.p.x + room.w, room.p.y + room.h))
			
	def pointOutside(self, pos):
		return pos.x < 0 or pos.x >= self.width or pos.y < 0 or pos.y >= self.height	
			
	def __repr__(self):
		return "\n".join([ " ".join(row) for row in self.grid ])
		
		
class Hallway():
	start = None
	end = None
	rooms = None
	
	def __init__(self, start, end):
		self.start = start
		self.end = end
		self.rooms = []
		
		
class Room():
	p = None
	w = -1
	h = -1
	t = -1
	walls = None
	rooms = None
	hallways = None
	level = -1
	
	def __init__(self, width, height, kind):
		self.p = Vec2d(-1, -1)
		self.w = width
		self.h = height
		self.t = kind
		self.walls = "nesw"
		self.rooms = { l: [] for l in "nesw" }
		self.hallways = { l: [] for l in "nesw" } 
		
	def removeWall(self, wall):
		self.walls = self.walls.replace(wall, "", 1)
		
	def getPointInWall(self, wall):
		p = Vec2d(-1, -1)
		if wall == "n" and self.w > 2:
			p.x = self.p.x + random.randint( 1, self.w - 2 )
			p.y = self.p.y - 1
		elif wall == "e" and self.h > 2:
			p.x = self.p.x + self.w
			p.y = self.p.y + random.randint( 1, self.h - 2 )
		elif wall == "s" and self.w > 2:
			p.x = self.p.x + random.randint( 1, self.w - 2 )
			p.y = self.p.y + self.h
		elif wall == "w" and self.h > 2:
			p.x = self.p.x - 1
			p.y = self.p.y + random.randint( 1, self.h - 2 )
		
		return p
	
	def connectedTo(self, room):
		for k, v in room.rooms.items():
			for r in v:
				if r == room:
					print "askdjalskdj"
					return True
		return False

	def collidesWith(self, room):
		return not( self.p.x + self.w < room.p.x or self.p.y + self.h < room.p.y or room.p.x + room.w < self.p.x or room.p.y + room.h < self.p.y )
	
	def getOverlap(self, room):
		# Determine X diff
		room_a, room_b = self, room
		if self.p.x > room.p.x:
			room_a = room
			room_b = self
		
		diff_x = (1, 0)
		if room_b.p.x + room_b.w <= room_a.p.x + room_a.w:
			diff_x = (room_b.p.x, room_b.p.x + room_b.w - 1)
		else:
			diff_x = (room_b.p.x, room_a.p.x + room_a.w - 1)
			
		# Determine Y diff
		room_a, room_b = self, room
		if self.p.y > room.p.y:
			room_a = room
			room_b = self
		
		diff_y = (1, 0)
		if room_b.p.y + room_b.h <= room_a.p.y + room_a.h:
			diff_y = (room_b.p.y, room_b.p.y + room_b.h - 1)
		else:
			diff_y = (room_b.p.y, room_a.p.y + room_a.h - 1)

		return (diff_x, diff_y)

	def distance(self, room):	
		room_a, room_b = self, room
		if self.p.x > room.p.x:
			room_a = room
			room_b = self
		dist_x = room_b.p.x - (room_a.p.x + room_a.w)
			
		# Determine Y dist
		room_a, room_b = self, room
		if self.p.y > room.p.y:
			room_a = room
			room_b = self		
		dist_y = room_b.p.y - (room_a.p.y + room_a.h)

		return (dist_x, dist_y)

	def getDirection(self, room):
		if self.p.x + self.w < room.p.x:
			return "e"
		if self.p.y + self.h < room.p.y:
			return "s"
		if self.p.x > room.p.x + room.w:
			return "w"
		if self.p.y > room.p.y + room.h:
			return "n"
		return ""


	def __repr__(self):
		return "Room(p= (" + str(self.p.x) + "," + str(self.p.y) + "), w= " + str(self.w) + ", h= " + str(self.h) + ")"

	@staticmethod
	def invertDirection(d):
		if d == "n":
			return "s"
		if d == "e":
			return "w"
		if d == "s":
			return "n"
		return "e"

	

if not 9 <= len(sys.argv) <= 10:
	sys.exit()

if len(sys.argv) == 10:
	seed = sys.argv[9]
	random.seed(seed)
else:
	seed = str(random.randint(0,999999))
	random.seed(seed)
print "Seed: ", seed	

mins = map(int, [ sys.argv[3],sys.argv[5], sys.argv[7] ])
maxs = map(int, [ sys.argv[4],sys.argv[6], sys.argv[8] ])

try:
	dunGen = Dungeon(int(sys.argv[1]), int(sys.argv[2]), mins= mins, maxs= maxs)

	dunGen.placeEntrance()
	
	dunGen.generate()
	
	print(dunGen)
except:
	raise	
	

