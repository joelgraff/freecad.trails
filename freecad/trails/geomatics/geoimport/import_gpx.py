"""
GPX File importer
"""

import FreeCAD, FreeCADGui, Draft
from .transversmercator import TransverseMercator
from .xmltodict import parse
from .say import sayexc
import re
from PySide import QtGui

def import_gpx(filename, orig, hi):
	"""
	Import a gpx trackfile
	"""

	f = open(filename, "r")
	c1 = f.read()
	content = re.sub('^\<\?[^\>]+\?\>', '', c1)
	print(content)

	tm = TransverseMercator()

	# outdoor inn ...
	tm.lat, tm.lon = 50.3736049, 11.191643
	
	if orig != 'auto':
		yy = orig.split(',')
		origin = (float(yy[0]), float(yy[1]))
		tm.lat = origin[0]
		tm.lon = origin[1]
	
	sd = parse(content)

	points = []
	points2 = []
	points0 = []
	px = []
	py = []
	pz = []
	pt = []

	starth = None
	FreeCAD.sd = sd
	seg = sd['gpx']['trk']['trkseg']

	try:
		seg['trkpt']
		ss = seg
		seg = [ss]

	except Exception:
		pass

	lats = []
	lons = []

	for s in seg:
		trkpts = s['trkpt']

		for n in trkpts:
			lats.append(float(n['@lat']))
			lons.append(float(n['@lon']))

	print(min(lats), max(lats))
	print(min(lons), max(lons))
	print((max(lats)+min(lats))/2, (max(lons)+min(lons))/2)
	print((max(lats)-min(lats))/2, (max(lons)-min(lons))/2)

	if orig == 'auto':
		tm.lat, tm.lon = (max(lats)+min(lats))/2, (max(lons)+min(lons))/2
		print("origin:")
		print(tm.lat, tm.lon)
		print("----------")

	for s in seg:
		trkpts = s['trkpt']
		n = trkpts[0]
		center = tm.fromGeographic(tm.lat, tm.lon)

		# map all points to xy-plane
		for n in trkpts:
			lats.append(float(n['@lat']))
			lons.append(float(n['@lon']))
			ll = tm.fromGeographic(float(n['@lat']), float(n['@lon']))
			h = n['ele']
			tim = n['time']
			t2 = re.sub('^.*T', '', tim)
			t3 = re.sub('Z', '', t2)
			t4 = t3.split(':')
			timx = int(t4[0])*3600+int(t4[1])*60+int(t4[2])
			pt.append(timx)

			if starth is None:
				starth = float(h)
				starth = 0

			points.append(FreeCAD.Vector(ll[0]-center[0], ll[1]-center[1], 1000*(float(h)-starth)))
			points.append(FreeCAD.Vector(ll[0]-center[0], ll[1]-center[1], 0))
			points.append(FreeCAD.Vector(ll[0]-center[0], ll[1]-center[1], 1000*(float(h)-starth)))
			points2.append(FreeCAD.Vector(ll[0]-center[0], ll[1]-center[1], 1000*(float(h)-starth)+20000))
			points0.append(FreeCAD.Vector(ll[0]-center[0], ll[1]-center[1], 0))
			px.append(ll[0]-center[0])
			py.append(ll[1]-center[1])
			pz.append(1000*(float(h)-starth))

	Draft.makeWire(points0)

	Draft.makeWire(points)

	po = FreeCAD.ActiveDocument.ActiveObject
	po.ViewObject.LineColor = (1.0, 0.0, 0.0)
	po.MakeFace = False

	po.Placement.Base.z = float(hi)*1000
	po.Label = "My Track"

	Draft.makeWire(points2)

	po2 = FreeCAD.ActiveDocument.ActiveObject
	po2.ViewObject.LineColor = (0.0, 0.0, 1.0)
	po2.ViewObject.PointSize = 5
	po2.ViewObject.PointColor = (0.0, 1.0, 1.0)

	po2.Placement.Base.z = float(hi)*1000
	po2.Label = "Track + 20m"

	FreeCAD.activeDocument().recompute()
	FreeCADGui.SendMsgToActiveView("ViewFit")

	return str(tm.lat)+','+str(tm.lon)


# Gui backend
class MyApp(object):
	"""
	The  execution layer of import_gpx
	"""

	def run(self):
		"""
		Calls import_gpx
		"""

		filename = self.root.ids['bl'].text()
		if filename.startswith('UserAppData'):
			filename = filename.replace('UserAppData', FreeCAD.ConfigGet("UserAppData"))

		try:
			rc = import_gpx(
					filename,
					self.root.ids['orig'].text(),
					self.root.ids['h'].text(),
			)
			self.root.ids['orig'].setText(rc),

		except Exception:
			sayexc()

	def getfn(self):
		"""
		Get the filename of the track
		"""

		fileName = QtGui.QFileDialog.getOpenFileName(None, u"Open File", u"/tmp/");
		print(fileName)
		s = self.root.ids['bl']
		s.setText(fileName[0])


# the dialog to import the file
def mydialog():
	"""
	The dialog to import the file
	"""

	from freecad.trails.geomatics.guigeoimport import miki
	from freecad.trails.geomatics.guigeoimport.miki_import_gpx import sdialog

	app = MyApp()
	amiki = miki.Miki()
	amiki.app = app
	app.root = amiki

	amiki.parse2(sdialog)
	amiki.run(sdialog)
	return amiki


# tst open and hide dialog
def runtest():
	m = mydialog()
	m.objects[0].hide()

if __name__ == '__main__':
	runtest()
