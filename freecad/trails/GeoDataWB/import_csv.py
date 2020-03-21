"""
CSV File importer
"""

import FreeCAD, FreeCADGui, Part, Draft
from GeoDataWB.transversmercator import TransverseMercator
from GeoDataWB.say import *
import csv, re


def import_csv(fn, orig, datatext = None):
	# Lat Lon
	yy = orig.split(',')
	origin = (float(yy[0]), float(yy[1]))

	data = []

	if len(datatext) != 0:
		lines = datatext.split('\n')

		for l in lines:
			pp = re.split("( )+", l)

			if len(pp) == 1:
				continue

			if len(pp) < 3:
				raise Exception("Syntax error in 'direct Data input'")

			data.append([str(pp[0]),str(pp[2])])

		print(data)

	else:
		with open(fn, 'r') as csvfile:
			reader = csv.reader(csvfile, delimiter=';')
			print(reader)

			for row in reader:
				data.append(row)

	tm = TransverseMercator()
	tm.lat = origin[0]
	tm.lon = origin[1]
	center = tm.fromGeographic(tm.lat, tm.lon)

	points = []

	for p in data:
		lat, lon = p[0], p[1]
		ll = tm.fromGeographic(float(lat), float(lon))
		points.append(FreeCAD.Vector(ll[0]-center[0], ll[1]-center[1], 0.0))

	points.append(points[0])
	Draft.makeWire(points)

	po = FreeCAD.ActiveDocument.ActiveObject
	po.ViewObject.LineColor = (1.0, 0.0, 0.0)
	po.MakeFace = False

	FreeCAD.activeDocument().recompute()
	FreeCADGui.SendMsgToActiveView("ViewFit")


s6 = '''
MainWindow:
	VerticalLayout:
		id:'main'

		QtGui.QLabel:
			setText:"***   I M P O R T    CSV   GEODATA   ***"
		QtGui.QLabel:

		QtGui.QLabel:
			setText:"Data input filename"

		QtGui.QLineEdit:
			setText:"Select *.csv file"
			id: 'bl'

		QtGui.QPushButton:
			setText: "Get CSV File Name"
			clicked.connect: app.getfn

		QtGui.QLabel:
			setText:"direct Data input  "


		QtGui.QTextEdit:
			setText:""
			id: 'data'

		QtGui.QLabel:
			setText:"Origin (lat,lon) "


		QtGui.QLineEdit:
			setText:"50.3729107,11.1913920"
			id: 'orig'

		QtGui.QPushButton:
			setText: "Run values"
			clicked.connect: app.run

'''


class MyApp(object):

	def run(self):
		filename = self.root.ids['bl'].text()

		try:
			import_csv(
					filename,
					self.root.ids['orig'].text(),
					self.root.ids['data'].toPlainText(),
			)
		except:
			sayexc()

	def getfn(self):
		fileName = QtGui.QFileDialog.getOpenFileName(None, u"Open File", u"/tmp/");
		s = self.root.ids['bl']
		s.setText(fileName[0])


def mydialog():
	app = MyApp()

	import GeoDataWB.miki as miki

	miki = miki.Miki()
	miki.app = app
	app.root = miki

	miki.parse2(s6)
	miki.run(s6)
	return miki


def runtest():
	m = mydialog()
	m.objects[0].hide()
