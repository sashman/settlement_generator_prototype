import random, json, os, math, sys
from operator import itemgetter
from PIL import Image, ImageDraw
 
class House(object):
	"""House is a class to hold to render them on the screen"""
	pos = (0,0)
	size = (1,1)
	attraction = 1
	def __init__(self, (x,y), size = (4,4), attraction = 1):
		super(House, self).__init__()
		self.pos = (x,y)
		self.attraction = attraction

		w,h = size
		self.render_pos = (x - w/2, y - h/2)
		self.size = size
		self.offset_size = (x+w,y+h)

	def render(self, draw):
		draw.rectangle([self.render_pos, self.offset_size], outline="#FFFFFF" , fill="#3B1D09")

class HouseGroup(object):

	def __init__(self):
		self.pos = (0,0)
		self.houses = []
		pass

	def add_house(self, house):
		self.house.append(house)
		
		

total_x = None
total_y = None
total_detail = []

terrain_rating = []

house_rating = []
max_house_rating = 0

group_house_points = []

last_placed_house = None
houses = []

candidates = []


#read maps in

def read_map_files():

	global total_x
	global total_y
	global total_detail

	for filename in os.listdir("map"):
		if(os.path.splitext(filename)[1] == ".map"):
			
			m = json.load(open("map/"+filename, "r"))

			if total_x == None and total_y == None:
				total_x = int(m["map"]["total_x"]) *32
				total_y = int(m["map"]["total_y"]) *32

			detail = m["map"]["content"]["detail"]
			total_detail.extend(detail)

#set terrain_rating for an object and its surrounding area
def terrain_rating_circle(object, size = 10):


	x = int(object["x"])
	y = int(object["y"])

	terrain_rating[y][x] = 0.0

	for yi in xrange(y-size/2, y+size/2):
		if yi < 0 or yi >= len(terrain_rating): continue
		for xi in xrange(x-size/2, x+size/2):
			if xi < 0 or xi >= len(terrain_rating): continue

			dist = math.hypot(x - xi, y - yi)
			if dist != 0 and dist < size:
				value = float(dist)/float(size)
				terrain_rating[yi][xi] = min(terrain_rating[yi][xi], value)

def recalculate_terrain_rating(size):

	global total_detail
	for cliff in total_detail:

		terrain_rating_circle(cliff, size=size)

def place_first_house():
	global candidates
	global houses
	if len(candidates) == 0:
		for y in xrange(0, len(terrain_rating)):
			for x in xrange(0, len(terrain_rating)):
				if terrain_rating[y][x]>=1:
					candidates.append((x,y))

	i = random.randint(0,len(candidates))
	picked_coords = candidates[i]

	# picked_coords = (int(total_x/2), int(total_y/2))

	candidates.remove(picked_coords)
	h = House(picked_coords)
	houses.append(h)
	return h

def place_house(size = (4,4), attraction = 1):

	#if called before first house by accident
	global candidates
	global houses
	if len(houses) == 0:
		place_first_house()
		return

	#actual method
	#recalculate candidates with respect to house rating
	#needs to recalculated everytime
	candidates = []
	for y in xrange(0, len(house_rating)):
		for x in xrange(0, len(house_rating)):
			if house_rating[y][x]>0:
				candidates.append((x,y, house_rating[y][x]))

	if len(candidates) <= 0:
		print "No more space"
		return None
	candidates = sorted(candidates, key=itemgetter(2),  reverse=True)
	x,y,_ = candidates[0]
	h = House((x,y), size = size, attraction = attraction)
	houses.append(h)
	return h


def house_rating_circle(house, size = 80):
	if house == None: return

	global max_house_rating
	global house_rating

	actual_max = 0

	x,y = house.pos
	print "Rating house at ", x, y, " range ", x-size/2, y-size/2, "by", x+size/2, y+size/2
	t_too_close, _ = house.size
	t_too_close  = int(t_too_close * 2) + 1
	t_too_far = t_too_close + 10*house.attraction
	max_house_rating = (t_too_close + t_too_far)/2

	
	for yi in xrange(y-size/2, y+size/2):
		if yi < 0 or yi >= len(house_rating): continue
		for xi in xrange(x-size/2, x+size/2):
			if xi < 0 or xi >= len(house_rating): continue
			
			dist = math.hypot(x - xi, y - yi)

			

			k = 1
			steepness = house.attraction

			v = -k * (dist**(steepness) - t_too_close) * (dist - t_too_far)

			
			# v = max(-1,v)
			if dist < t_too_close:
				v = 0
			elif dist > t_too_far:
				# v = -1
				continue


			# if v > 0:
			# 	print t_too_close, t_too_far, dist, v

			# if house_rating[yi][xi] > -1.0:
			# 	house_rating[yi][xi] = min(house_rating[yi][xi], v)
			# else:
			
			if terrain_rating[yi][xi] >= 1:
				
				if house_rating[yi][xi] >= 0:
					# house_rating[yi][xi] = min(house_rating[yi][xi], v)
					house_rating[yi][xi] = (house_rating[yi][xi] * v)
				else:
					house_rating[yi][xi] = v

			if actual_max < house_rating[yi][xi]: actual_max = house_rating[yi][xi]

	max_house_rating = actual_max

	



read_map_files()
print len(total_detail)

screen_height = int(total_y)
screen_width = int(total_x)

terrain_rating = [[1.0 for x in xrange(total_y)] for x in xrange(total_x)] 
house_rating = [[-1.0 for x in xrange(total_y)] for x in xrange(total_x)] 

img_filename = "out.png"
img = Image.new('RGBA', (screen_width, screen_height), "black")

draw = ImageDraw.Draw(img)
 
for cliff in total_detail:

	x = int(cliff["x"])
	y = int(cliff["y"])

	draw.point((x,y), "white")
	#screen.fill((255,255,255), ((x,y), (1,1)))

	terrain_rating_circle(cliff)

for y in xrange(0, len(terrain_rating)):
	for x in xrange(0, len(terrain_rating)):

		if terrain_rating[y][x]>0:
			draw.point((x,y), (0, int(terrain_rating[y][x] * 255),0))
			#screen.fill(((1-terrain_rating[y][x]) * 255,0,0), ((x,y), (1,1)))
			#screen.fill((0, (terrain_rating[y][x]) * 255,0), ((x,y), (1,1)))





house_rating_circle(place_first_house())

house_size = 4
for x in range(int(sys.argv[1])):
	# if x % 10 == 0:
	# 	house_rating_circle(place_house(attraction = 4))
	# else:
	if x % 10 == 0:
		house_size = 8
	else:
		house_size = 4

	if last_placed_house:
		sx, sy = last_placed_house.size
		last_s = max(sx,sy)

		if last_s != house_size:
			recalculate_terrain_rating(house_size)
	else:
		recalculate_terrain_rating(house_size)


	last_placed_house = place_house(size = (house_size,house_size))
	house_rating_circle(last_placed_house)


for h in houses:
	h.render(draw)
	





for y in xrange(0, len(house_rating)):
	for x in xrange(0, len(house_rating)):

		# if house_rating[y][x]>0:

		blue = house_rating[y][x] / max_house_rating
		if blue > 0:
			
			# blue = house_rating[y][x]			
			draw.point((x,y), (0, 0, int(blue * 255)))
		# else:
		# 	draw.point((x,y), (255, 0, 0))

img_filename = "out" + str(sys.argv[1]) + ".png"
img.save(img_filename )