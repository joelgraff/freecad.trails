'''import heights'''
# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- google heights importer
#--
#-- microelly 2016 v 0.3
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------

import FreeCAD, FreeCADGui, Draft
from  GeoDataWB.transversmercator import TransverseMercator
from GeoDataWB.say import *

tm=TransverseMercator()


## get the height of point 
# @param b latitude
# @param l longitude

'''
f='https://maps.googleapis.com/maps/api/elevation/json?locations=50.3377879,11.2104096'
response = urllib2.urlopen(f)
'''

def getheight(b,l):
	source="https://api.open-elevation.com/api/v1/lookup?locations="+str(b)+','+str(l)
	say(source)
	print (source)

	import json
	from urllib import request
	response = request.urlopen(source)
	s = json.loads(response.read())

	res=s['results']
		
	for r in res:
		return round(r['elevation']*1000,2)


## download the heights from open-elevation

def run(b0=50.35,l0=11.17,b=50.35,le=11.17,size=40):

	tm.lat=b0
	tm.lon=l0
	baseheight=getheight(tm.lat,tm.lon)
	center=tm.fromGeographic(tm.lat,tm.lon)

	say("Base height ", baseheight)
	say("center point", center)

	
	for i in range(-size,size):
		source="https://api.open-elevation.com/api/v1/lookup?locations="
		bb=b+i*0.001
		ss=str(bb)+','+str(le)
		source += ss

		import json
		from urllib import request
		response = request.urlopen(source)
		s=json.loads(response.read())

		res = s['results']

		points=[]

		for r in res:
			c=tm.fromGeographic(r['latitude'],r['longitude'])
			v=FreeCAD.Vector(
						round((c[0]-center[0]),2),
						round((c[1]-center[1]),2), 
						round(r['elevation']*1000,2)-baseheight
					)
			points.append(v)

	Draft.makeWire(points,closed=False,face=False,support=None)
	FreeCAD.activeDocument().recompute()
	FreeCADGui.updateGui()
	return FreeCAD.activeDocument().ActiveObject
	

## import the heights of a rectangle area

def import_heights(b,le,size):

	size=int(size)
	size=30

	lines=[]
	for ld in range(-size,size): 
		say("run",ld)
		res=run(b,le,b,le +ld*0.001,size)
		lines.append(res)

	ll=FreeCAD.activeDocument().addObject('Part::Loft','Loft')
	ll.Sections=lines
	for li in lines:
		li.ViewObject.Visibility=False

	inventortools.setcolorlights(ll)
	FreeCAD.activeDocument().recompute()


s6='''
MainWindow:
	VerticalLayout:
		id:'main'
#		setFixedHeight: 600
		setFixedWidth: 300
#		move:  PySide.QtCore.QPoint(3000,100)

		QtGui.QLabel:
			setText:"C O N F I G U R A T I O N"
		QtGui.QLabel:

		QtGui.QLineEdit:
			setText:"50.3377879,11.2104096"
#			setText:"50.3736049,11.191643"
			id: 'bl'

		QtGui.QPushButton:
			setText: "Run values"
			clicked.connect: app.runbl

#
'''


## the gui backend
class MyApp(object):

	## download the heights
	def runbl(self):
		bl=self.root.ids['bl'].text()
		spli=bl.split(',')
		b=float(spli[0])
		l=float(spli[1])

		s=15
		say([l,b,s])
		import_heights(float(b),float(l),float(s))




## the gui startup
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


## test start the gui 
def importHeights():
	app=MyApp()

	import GeoDataWB.miki as miki
	reload(miki)

	miki=miki.Miki()
	miki.app=app
	app.root=miki


	miki.parse2(s6)

	miki.run(s6)
	m=miki.ids['main']


# mytest()


def importHeights():
	say("runit")
	mydialog()
	say("runit-done")
