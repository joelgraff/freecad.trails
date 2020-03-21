"""
Import srtm data
"""

import Points
from GeoDataWB.transversmercator import TransverseMercator
import math


# Create a QProgressBar widget for long running process
def createProgressBar(label=None):
	w = QtGui.QWidget()
	hbox = QtGui.QHBoxLayout()
	w.setLayout(hbox)
	pb = QtGui.QProgressBar()
	w.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

	if label != None:
		lab = QtGui.QLabel(label)
		hbox.addWidget(lab)
	hbox.addWidget(pb)
	w.show()
	FreeCAD.w = w
	pb.setValue(0)
	w.pb = pb
	return w


# create contour curve points list
def runfile(fn, xw, xe, ys, yn, ox=0, oy=0):
	f = 100000000

	tm = TransverseMercator()
	tm.lat = 0.5*(yn+ys)
	tm.lon = 0.5*(xw+xe)

	center = tm.fromGeographic(tm.lat, tm.lon)

	xw *= f
	xe *= f
	ys *= f
	yn *= f
	ox *= f
	oy *= f
	pts = []
	poss = {}
	nds = []
	elev = -1

	c = 0


	#Gui.ActiveDocument.ActiveView.setAnimationEnabled(False)
	pb=createProgressBar(label="create Elevations " + os.path.basename(fn) )

	# file = open('/home/microelly2/Downloads/Lat50Lon11Lat51Lon12.osm', 'r')
	file =open(fn)
#	pb.pb.setValue(10)

	for line in file.readlines():

		c += 1
		# if c == 100000: break
		pb.pb.setValue((c/100)%100)

		m = re.match(r'.*<node id="([^"]+)" lat="([^"]+)" lon="([^"]+)".*', line)
		if m:
			y=float(m.group(2))*f
			x=float(m.group(3))*f
			id=m.group(1)
			poss[id]=(x,y)
			continue

		m = re.match(r'.*<nd ref="([^"]+)".*', line)
		if m:
			nds.append(m.group(1))
			continue

		m = re.match(r'.*<tag k="ele" v="([^"]+)".*', line)
		if m:
			elev=float(m.group(1))
			continue

		m = re.match(r'.*/way.*', line)
		if m:

			for nd in nds:
				x=poss[nd][0]
				y=poss[nd][1]
				if xw<x and x<xe and ys<y and y<yn:
					ll=tm.fromGeographic(y/f,x/f)
					pts.append(FreeCAD.Vector(ll[0]-center[0],ll[1]-center[1],elev*1000))

#			if len(pts)>2:
#				d=Draft.makeWire(pts)
#			if len(pts)==1:
#				d=Draft.makePoint(pts[0])

			c +=1

			poss={}
			elev=0
			nds=[]
			continue

	pb.hide()
	return pts


# download the file
import sys, os, zipfile, traceback, time, re, platform
import urllib.request

from GeoDataWB.say import *



## download the data files from /geoweb.hft-stuttgart.de/SRTM

def getdata(directory,dat):

	zipfilename=directory + "/{}.osm.zip".format(dat)
	source="http://geoweb.hft-stuttgart.de/SRTM/srtm_as_osm/{}.osm.zip".format(dat)

	fn=directory+"/"+dat+".osm"
	if not os.path.exists(fn):

		if not os.path.exists(zipfilename):
			say("get "+ source)
			tg=urllib.request.urlretrieve(source,zipfilename)
			targetfile=tg[0]
			say("targetfile:"+targetfile)
			fh = open(targetfile, 'rb')

		else:
			fh = open(zipfilename, 'rb')

		zfile = zipfile.ZipFile(fh)
		zfile.extractall(directory)
		fh.close()


## get the date from files,create a point cloud

def run(mx,my,dx,dy):

	ys=my-dy
	yn=my+dy
	xw=mx-dx
	xe=mx+dx

	dats=[]

	say(xw,ys,xe,yn)
	for ix in range(int(math.floor(xw)),int(math.floor(xe))+1):
		for iy in range(int(math.floor(ys)),int(math.floor(yn))+1):
			dat="Lat"+str(iy)+"Lon"+str(ix)+"Lat"+str(iy+1)+"Lon"+str(ix+1)
			say(dat)
			dats.append(dat)

	directory=FreeCAD.ConfigGet("UserAppData") + "geodat_SRTM/"



	if not os.path.isdir(directory):
		os.makedirs(directory)

	for dat in dats:
		getdata(directory,dat)
		fn=directory+"/"+dat+".osm"
		pts=runfile(fn,xw,xe,ys,yn,mx,my)

		# Get or create "Point_Groups".
		try:
			PointGroups = FreeCAD.ActiveDocument.Point_Groups
		except:
			PointGroups = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroup", 'Point_Groups')
			PointGroups.Label = "Point Groups"

		# Get or create "Points".
		try:
			FreeCAD.ActiveDocument.Points
		except:
			Points = FreeCAD.ActiveDocument.addObject('Points::Feature', "Points")
			PointGroups.addObject(Points)

		PointGroup = FreeCAD.ActiveDocument.addObject('Points::Feature', "Point_Group")
		PointGroup.Label = dat
		FreeCAD.ActiveDocument.Point_Groups.addObject(PointGroup)
		PointObject = PointGroup.Points.copy()
		PointObject.addPoints(pts)
		PointGroup.Points = PointObject

	FreeCAD.ActiveDocument.recompute()
	Gui.SendMsgToActiveView("ViewFit")

	return pts




# test daten

dy=0.09
dx=0.09


# zugspitze
my=47.4210641
mx=10.9678556

# nizza
my=43.6827455
mx=7.255056


# puy de dome  Clermont Ferrand
my=45.7750419
mx=2.902975

# run(mx,my,dx,dy)

# mount everest
my=28.0020784
mx=86.9238805



#  friesener berg
my=50.2714589
mx=11.3614118


# outdoor inn
my=50.3736049
mx=11.1916430




s6='''
MainWindow:
	VerticalLayout:
		id:'main'
#		setFixedHeight: 600
		setFixedWidth: 250
		move:  PySide.QtCore.QPoint(100,100)

		QtGui.QLabel:
			setText:"I m p o r t    S R T M   Elevations"

		QtGui.QLabel:
			setText:"Location:"


		QtGui.QLineEdit:
			setText:"45.7750419,2.902975"
#			setText:"50.3736049,11.191643"
			id: 'bl'

		QtGui.QLabel:
			setText:"Area Interval:"
			
		QtGui.QLineEdit:
			setText:"0.03,0.03"
			id: 'dbl'

		QtGui.QPushButton:
			setText: "Create Elevation Points"
			clicked.connect: app.runbl

		QtGui.QPushButton:
			setText: "Show in OpenStreetMap"
			clicked.connect: app.run_browser

		QtGui.QPushButton:
			setText: "Show in Google Maps"
			clicked.connect: app.run_google

		QtGui.QPushButton:
			setText: "Reit und Wanderkarte"
			clicked.connect: app.run_reitwander


		QtGui.QLabel:
			setText:"Test Case Coords ..."

		QtGui.QPushButton:
			setText: "Nizza"
			clicked.connect: app.run_nizza

		QtGui.QPushButton:
			setText: "Puy de Dome"
			clicked.connect: app.run_puydedome

		QtGui.QPushButton:
			setText: "Mount Everest"
			clicked.connect: app.run_everest

		QtGui.QPushButton:
			setText: "Outdoor Inn"
			clicked.connect: app.run_outdoorinn




'''

import FreeCAD,FreeCADGui

## the gui backend

class MyApp(object):

	#\cond
	def run_nizza(self):
		self.root.ids['bl'].setText("43.6827455,7.255056")

	def run_puydedome(self):
		self.root.ids['bl'].setText("45.7750419,2.902975")

	def run_everest(self):
		self.root.ids['bl'].setText("28.0020784,86.9238805")

	def run_outdoorinn(self):
		self.root.ids['bl'].setText("50.3736049,11.1916430")


# horta azores 38.5346786,-28.6456061
# 0.25,0.25  flores azores 39.4360002,-31.1834447
# pico 0.40,0.40 38.435102,-28.3676582

# rocky mountains 44.188239,-109.8549527
# niagara falls 43.1024171,-79.0903965
# ungarn balaton 46.9101974,17.8516823

# china drei schluchten 30.8243332,111.0184339

# Guayaquil Ecuador-2.1523858,-80.0501215

	def run_browser(self):
		import WebGui
		bl=self.root.ids['bl'].text()
		spli=bl.split(',')
		my=float(spli[0])
		mx=float(spli[1])
		WebGui.openBrowser( "http://www.openstreetmap.org/#map=12/"+str(my)+'/'+str(mx))

	def run_google(self):
		import WebGui
		bl=self.root.ids['bl'].text()
		spli=bl.split(',')
		my=float(spli[0])
		mx=float(spli[1])
		WebGui.openBrowser( "https://www.google.de/maps/@"+str(my)+','+str(mx) +",8000m/data=!3m1!1e3")

	def run_reitwander(self):
		import WebGui
		bl=self.root.ids['bl'].text()
		spli=bl.split(',')
		my=float(spli[0])
		mx=float(spli[1])
		WebGui.openBrowser( "http://www.wanderreitkarte.de/index.php?lon="+str(mx)+"&lat="+str(my)+"&zoom=12")






	def runbl(self):
		bl=self.root.ids['bl'].text()
		spli=bl.split(',')
		my=float(spli[0])
		mx=float(spli[1])

#		dy=0.09
#		dx=0.09

		dbl=self.root.ids['dbl'].text()
		spli=dbl.split(',')
		dy=float(spli[0])
		dx=float(spli[1])

		run(mx,my,dx,dy)


	def runValues(self):
		b=self.root.ids['b'].text()
		l=self.root.ids['l'].text()
		s=self.root.ids['s'].value()
		say([l,b,s])
		import WebGui
#		WebGui.openBrowser( "http://www.openstreetmap.org/#map=19/"+str(b)+'/'+str(l))
		import GeoDataWB.import_osm
		geodat.import_osm.import_osm(float(b),float(l),float(s)/10,self.root.ids['progb'],self.root.ids['status'])


	def showMap(self):
		b=self.root.ids['b'].text()
		l=self.root.ids['l'].text()
		s=self.root.ids['s'].value()
		say([l,b,s])
		import WebGui
		WebGui.openBrowser( "http://www.openstreetmap.org/#map=9/"+str(b)+'/'+str(l))

	#\endcond

##the gui startup

def mydialog():
	app=MyApp()

	import GeoDataWB.miki as miki

	miki=miki.Miki()
	miki.app=app
	app.root=miki


	miki.parse2(s6)

	miki.run(s6)
	m=miki.ids['main']
	return miki


## testcase start and hide the dialog
def runtest():
	m=mydialog()
	m.objects[0].hide()

def importSRTM():
	mydialog()

if __name__ == '__main__':
	runtest()

