"""
Import data from OpenStreetMap
"""

import FreeCAD, FreeCADGui, WebGui, Part
from pivy import coin
from . import my_xmlparser
from .transversmercator import TransverseMercator
from . import inventortools as inventortools
from .say import say,sayErr,sayexc,sayW
import json, urllib.request, time

debug = False


def getHeight(b, l):
	"""
	Get height of a single point with latitude b, longitude l
	"""

	anz = 0

	while anz < 4:
		source = "https://maps.googleapis.com/maps/api/elevation/json?locations="+str(b)+','+str(l)
		response = urllib.request.urlopen(source)
		ans = response.read()

		if ans.find("OVER_QUERY_LIMIT"):
			anz += 1
			time.sleep(5)

		else:
			anz=10

	s = json.loads(ans)
	res = s['results']

	for r in res:
		return round(r['elevation']*1000,2)


# Get the heights for a list of points
def getHeights(points):
	"""
	Get heights for a list of points
	"""

	i = 0
	size = len(points)

	while i < size:
		source = "https://maps.googleapis.com/maps/api/elevation/json?locations="
		ii = 0

		if i > 0:
			time.sleep(1)

		while ii < 20 and i < size:
			p = points[i]
			ss = p[1]+','+p[2] + '|'
			source += ss
			i += 1
			ii += 1

		source += "60.0,10.0"
		response = urllib.request.urlopen(source)
		ans = response.read()
		s = json.loads(ans)
		res = s['results']
		heights = {}

		for r in res:
			key = "%0.7f" % (r['location']['lat']) + " " + "%0.7f" % (r['location']['lng'])
			heights[key] = r['elevation']

	return heights


def organize():
	"""
	Create groups for the different object types
	GRP_highways, GRP_building, GRP_landuse
	"""

	highways = FreeCAD.activeDocument().addObject("App::DocumentObjectGroup", "GRP_highways")
	landuse = FreeCAD.activeDocument().addObject("App::DocumentObjectGroup", "GRP_landuse")
	buildings = FreeCAD.activeDocument().addObject("App::DocumentObjectGroup", "GRP_building")
	pathes = FreeCAD.activeDocument().addObject("App::DocumentObjectGroup", "GRP_pathes")

	for oj in FreeCAD.activeDocument().Objects:
		if oj.Label.startswith('building'):
			buildings.addObject(oj)

		if oj.Label.startswith('highway') or oj.Label.startswith('way'):
			highways.addObject(oj)
			oj.ViewObject.Visibility=False

		if oj.Label.startswith('landuse'):
			landuse.addObject(oj)
			oj.ViewObject.Visibility = False

		if oj.Label.startswith('w_'):
			pathes.addObject(oj)
			oj.ViewObject.Visibility = False


def import_osm2(b, l, bk, progressbar, status, elevation):
	if progressbar:
		progressbar.setValue(0)

	if status:
		status.setText("get data from openstreetmap.org ...")
		FreeCADGui.updateGui()

	content = ''

	bk = 0.5*bk
	dn = FreeCAD.ConfigGet("UserAppData") + "geodat3/"
	fn = dn+str(b)+'-'+str(l)+'-'+str(bk)
	import os

	if not os.path.isdir(dn):
		os.makedirs(dn)

	try:
		say("I try to read data from cache file ... ")
		say(fn)
		f = open(fn, "r")
		content = f.read()

	except Exception:
		sayW("no cache file, so I connect to  openstreetmap.org...")
		lk = bk
		b1 = b-bk/1113*10
		l1 = l-lk/713*10
		b2 = b+bk/1113*10
		l2 = l+lk/713*10
		source = 'http://api.openstreetmap.org/api/0.6/map?bbox='+str(l1)+','+str(b1)+','+str(l2)+','+str(b2)
		say(source)

		response = urllib.request.urlopen(source)
		FreeCAD.t = response

		f = open(fn, "w")
		f.write(response.read().decode('utf8'))
		f.close()

	if elevation:
		baseheight = getHeight(b, l)

	else:
		baseheight = 0

	if debug:
		say("-------Data---------")
		say(content)

	if status:
		status.setText("parse data ...")
		FreeCADGui.updateGui()

	say("------------------------------")
	say(fn)

	tree = my_xmlparser.getData(fn)

	if debug:
		say(json.dumps(sd, indent=4))

	if status:
		status.setText("transform data ...")
		FreeCADGui.updateGui()

	nodes = tree.getiterator('node')
	ways = tree.getiterator('way')
	bounds = tree.getiterator('bounds')[0]

	# center of the scene
	minlat = float(bounds.params['minlat'])
	minlon = float(bounds.params['minlon'])
	maxlat = float(bounds.params['maxlat'])
	maxlon = float(bounds.params['maxlon'])

	tm = TransverseMercator()
	tm.lat = 0.5*(minlat+maxlat)
	tm.lon = 0.5*(minlon+maxlon)

	center = tm.fromGeographic(tm.lat, tm.lon)
	corner = tm.fromGeographic(minlat, minlon)
	size = [center[0]-corner[0], center[1]-corner[1]]

	# map all points to xy-plane
	points = {}
	nodesbyid = {}

	for n in nodes:
		nodesbyid[n.params['id']] = n
		ll = tm.fromGeographic(float(n.params['lat']), float(n.params['lon']))
		points[str(n.params['id'])] = FreeCAD.Vector(ll[0]-center[0], ll[1]-center[1], 0.0)

	if status:
		status.setText("create visualizations  ...")
		FreeCADGui.updateGui()

	FreeCAD.newDocument("OSM Map")
	say("Datei erzeugt")
	area = FreeCAD.ActiveDocument.addObject("Part::Plane", "area")
	obj = FreeCAD.ActiveDocument.ActiveObject
	say("grundflaeche erzeugt")

	try:
		viewprovider = obj.ViewObject
		root = viewprovider.RootNode
		myLight = coin.SoDirectionalLight()
		myLight.color.setValue(coin.SbColor(0,1,0))
		root.insertChild(myLight, 0)
		say("beleuchtung auf grundobjekt eingeschaltet")

	except Exception:
		sayexc("Beleuchtung 272")

	cam = '''#Inventor V2.1 ascii
	OrthographicCamera {
	viewportMapping ADJUST_CAMERA
	orientation 0 0 -1.0001  0.001
	nearDistance 0
	farDistance 10000000000
	aspectRatio 100
	focalDistance 1
	'''
	x = 0
	y = 0
	height = 200*bk*10000/0.6
	cam += '\nposition ' +str(x) + ' ' + str(y) + ' 999\n '
	cam += '\nheight ' + str(height) + '\n}\n\n'
	FreeCADGui.activeDocument().activeView().setCamera(cam)
	FreeCADGui.activeDocument().activeView().viewAxonometric()
	say("Kamera gesetzt")

	area.Length = size[0]*2
	area.Width = size[1]*2
	area.Placement = FreeCAD.Placement(FreeCAD.Vector(-size[0], -size[1], 0.00), FreeCAD.Rotation(0.00, 0.00, 0.00, 1.00))
	say("Area skaliert")
	wn = -1
	coways = len(ways)
	starttime = time.time()
	refresh = 1000

	for w in ways:
		wid = w.params['id']
		building = False
		landuse = False
		highway = False
		wn += 1

		nowtime = time.time()

		if wn != 0 and (nowtime-starttime)/wn > 0.5:
			say(("way ---- # " + str(wn) + "/" + str(coways) + " time per house: " + str(round((nowtime-starttime)/wn, 2))))

		if progressbar:
			progressbar.setValue(int(0+100.0*wn/coways))

		st = ""
		st2 = ""
		nr = ""
		h = 0
		ci = ""

		for t in w.getiterator('tag'):
			try:
				if str(t.params['k']) == 'building':
					building = True

					if st == '':
						st = 'building'

				if str(t.params['k']) == 'landuse':
					landuse = True
					st = t.params['k']
					nr = t.params['v']

				if str(t.params['k']) == 'highway':
					highway = True
					st = t.params['k']

				if str(t.params['k']) == 'addr:city':
					ci = t.params['v']

				if str(t.params['k']) == 'name':
					nr = t.params['v']

				if str(t.params['k']) == 'ref':
					nr = t.params['v']+" /"

				if str(t.params['k']) == 'addr:street':
					st2 = " "+t.params['v']

				if str(t.params['k']) == 'addr:housenumber':
					nr = str(t.params['v'])

				if str(t.params['k']) == 'building:levels':
					if h == 0:
						h = int(str(t.params['v']))*1000*3

				if str(t.params['k']) == 'building:height':
					h = int(str(t.params['v']))*1000

			except Exception:
				sayErr("unexpected error ######################################################")

		name = str(st) + st2 + " " + str(nr)

		if name == ' ':
			name = 'landuse xyz'

		if debug:
			say(("name ", name))

		# Generate pointlist of the way
		polis = []
		height = None
		llpoints = []

		for n in w.getiterator('nd'):
			m = nodesbyid[n.params['ref']]
			llpoints.append([n.params['ref'], m.params['lat'], m.params['lon']])

		if elevation:
			say("get heights for " + str(len(llpoints)))
			heights = getHeights(llpoints)

		for n in w.getiterator('nd'):
			p = points[str(n.params['ref'])]

			if building and elevation:
				if not height:
					try:
						height = heights[m.params['lat']+' '+m.params['lon']]*1000 - baseheight

					except Exception:
						sayErr("---no height available for " + m.params['lat']+' '+m.params['lon'])
						height = 0

				p.z = height

			polis.append(p)

		# Create 2D map
		pp = Part.makePolygon(polis)
		Part.show(pp)
		z = FreeCAD.ActiveDocument.ActiveObject
		z.Label = "w_"+wid

		if name == ' ':
			g = FreeCAD.ActiveDocument.addObject("Part::Extrusion", name)
			g.Base = z
			g.ViewObject.ShapeColor = (1.00, 1.00, 0.00)
			g.Dir = (0, 0, 10)
			g.Solid = True
			g.Label = 'way ex '

		if building:
			g = FreeCAD.ActiveDocument.addObject("Part::Extrusion", name)
			g.Base = z
			g.ViewObject.ShapeColor = (1.00, 1.00, 1.00)

			if h == 0:
				h = 10000
			g.Dir = (0, 0, h)
			g.Solid = True
			g.Label = name

			obj = FreeCAD.ActiveDocument.ActiveObject
			inventortools.setcolors2(obj)

		if landuse:
			g = FreeCAD.ActiveDocument.addObject("Part::Extrusion", name)
			g.Base = z

			if nr == 'residential':
				g.ViewObject.ShapeColor = (1.00, 0.60, 0.60)

			elif nr == 'meadow':
				g.ViewObject.ShapeColor = (0.00, 1.00, 0.00)

			elif nr == 'farmland':
				g.ViewObject.ShapeColor = (0.80, 0.80, 0.00)

			elif nr == 'forest':
				g.ViewObject.ShapeColor = (1.0, 0.40, 0.40)

			g.Dir = (0, 0, 0.1)
			g.Label = name
			g.Solid = True

		if highway:
			g = FreeCAD.ActiveDocument.addObject("Part::Extrusion", "highway")
			g.Base = z
			g.ViewObject.LineColor = (0.00, 0.00, 1.00)
			g.ViewObject.LineWidth = 10
			g.Dir = (0, 0, 0.2)
			g.Label = name
		refresh += 1

		if os.path.exists("/tmp/stop"):
			sayErr("notbremse gezogen")
			FreeCAD.w = w
			raise Exception("Notbremse Manager main loop")

		if refresh > 3:
			FreeCADGui.updateGui()
			refresh = 0

	FreeCADGui.updateGui()
	FreeCAD.activeDocument().recompute()

	if status:
		status.setText("import finished.")

	if progressbar:
		progressbar.setValue(100)

	organize()

	endtime = time.time()
	say(("running time ", int(endtime-starttime),  " count ways ", coways))

	return True
