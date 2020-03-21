# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- gpx importer
#--
#-- microelly 2016 v 0.0
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------

from GeoDataWB.say import *

# test-data from https://en.wikipedia.org/wiki/GPS_Exchange_Format

trackstring='''
<gpx xmlns="http://www.topografix.com/GPX/1/1" xmlns:gpxx="http://www.garmin.com/xmlschemas/GpxExtensions/v3" xmlns:gpxtpx="http://www.garmin.com/xmlschemas/TrackPointExtension/v1" creator="Oregon 400t" version="1.1" xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance" xsi:schemaLocation="http://www.topografix.com/GPX/1/1 http://www.topografix.com/GPX/1/1/gpx.xsd http://www.garmin.com/xmlschemas/GpxExtensions/v3 http://www.garmin.com/xmlschemas/GpxExtensionsv3.xsd http://www.garmin.com/xmlschemas/TrackPointExtension/v1 http://www.garmin.com/xmlschemas/TrackPointExtensionv1.xsd">
  <metadata>
    <link href="http://www.garmin.com">
      <text>Garmin International</text>
    </link>
    <time>2009-10-17T22:58:43Z</time>
  </metadata>
  <trk>
    <name>Example GPX Document</name>
    <trkseg>
      <trkpt lat="47.644548" lon="-122.326897">
        <ele>4.46</ele>
        <time>2009-10-17T18:37:26Z</time>
      </trkpt>
      <trkpt lat="47.644549" lon="-122.326898">
        <ele>4.94</ele>
        <time>2009-10-17T18:37:31Z</time>
      </trkpt>
      <trkpt lat="47.644550" lon="-122.326898">
        <ele>6.87</ele>
        <time>2009-10-17T18:37:34Z</time>
      </trkpt>
    </trkseg>
  </trk>
</gpx>
'''


# https://de.wikipedia.org/wiki/GPS_Exchange_Format
'''
<ele> xsd:decimal </ele>                     <!-- Höhe in m -->
<time> xsd:dateTime </time>                  <!-- Datum und Zeit (UTC/Zulu) in ISO 8601 Format: yyyy-mm-ddThh:mm:ssZ -->
<magvar> degreesType </magvar>               <!-- Deklination / magnetische Missweisung vor Ort in Grad -->
<geoidheight> xsd:decimal </geoidheight>     <!-- Höhe bezogen auf Geoid -->
<name> xsd:string </name>                    <!-- Eigenname des Elements -->
<cmt> xsd:string </cmt>                      <!-- Kommentar -->
<desc> xsd:string </desc>                    <!-- Elementbeschreibung -->
<src> xsd:string </src>                      <!-- Datenquelle/Ursprung -->
<link> linkType </link>                      <!-- Link zu weiterführenden Infos -->
<sym> xsd:string </sym>                      <!-- Darstellungssymbol -->
<type> xsd:string </type>                    <!-- Klassifikation -->
<fix> fixType </fix>                         <!-- Art der Positionsfeststellung: none, 2d, 3d, dgps, pps -->
<sat> xsd:nonNegativeInteger </sat>          <!-- Anzahl der zur Positionsberechnung herangezogenen Satelliten -->
<hdop> xsd:decimal </hdop>                   <!-- HDOP: Horizontale Streuung der Positionsangabe -->
<vdop> xsd:decimal </vdop>                   <!-- VDOP: Vertikale Streuung der Positionsangabe -->
<pdop> xsd:decimal </pdop>                   <!-- PDOP: Streuung der Positionsangabe -->
<ageofdgpsdata> xsd:decimal </ageofdgpsdata> <!-- Sekunden zwischen letztem DGPS-Empfang und Positionsberechnung -->
<dgpsid> dgpsStationType:integer </dgpsid>   <!-- ID der verwendeten DGPS Station -->
<extensions> extensionsType </extensions>    <!-- GPX Erweiterung -->
'''

# translated above in to english
'''
<ele> xsd: decimal </ele>                    <!-- Height in m -->
<time> xsd: dateTime </time>                 <!-- Date and Time (UTC / Zulu) in ISO 8601 Format: yyyy-mm-ddThh: mm: ssZ -->
<magvar> degreesType </magvar>               <!-- Declination / magnetic local miss in degrees -->
<geoidheight> xsd: decimal </geoidheight>    <!-- Height relative to Geoid -->
<name> xsd: string </name>                   <!-- Name of the item -->
<cmt> xsd: string </cmt>                     <!-- Comment -->
<desc> xsd: string </desc>                   <!-- Element Description -->
<src> xsd: string </src>                     <!-- Data Source / Origin -->
<link> linkType </link>                      <!-- Link to further information -->
<sym> xsd: string </sym>                     <!-- Appearance icon -->
<type> xsd: string </type>                   <!-- Classification -->
<fix> fixType </fix>                         <!-- Type of position detection: none, 2d, 3d, dgps, pps -->
<sat> xsd: nonNegativeInteger </sat>         <!-- Number of satellites used for the position calculation -->
<hdop> xsd: decimal </hdop>                  <!-- HDOP: Horizontal distribution of position information -->
<vdop> xsd: decimal </vdop>                  <!-- VDOP: Vertical distribution of position information -->
<pdop> xsd: decimal </pdop>                  <!-- PDOP: Scattering of position information -->
<ageofdgpsdata> xsd:decimal </ageofdgpsdata> <!-- Seconds between last DGPS reception and position calculation -->
<dgpsid> dgpsStationType:integer </dgpsid>   <!-- ID of the used DGPS station -->
<extensions> extensionsType </extensions>    <!-- GPX extension -->
'''

import FreeCAD,FreeCADGui, Part
App=FreeCAD
Gui=FreeCADGui

from  GeoDataWB.transversmercator import TransverseMercator

debug=0

global sd

def run():
	filename='/home/thomas/.FreeCAD/Mod/geodat/testdata/latlonh.txt'
	orig='102.0793929 13.82877942'
	import_latlon(filename,orig,0)


def import_latlon(filename,orig,hi):
	global sd
	# content=trackstring
	
#	fn='/home/microelly2/FCB/b202_gmx_tracks/im_haus.gpx'
#	filename='/home/microelly2/FCB/b202_gmx_tracks/neufang.gpx'
	
	
	f=open(filename,"r")
	c1=f.read()
	import re
	#content = re.sub('^\<\?[^\>]+\?\>', '', c1)


	tm=TransverseMercator()

	# outdoor inn ...
	tm.lat,tm.lon = 50.3736049,11.191643
	
	if orig != 'auto':
		yy=orig.split(' ')
		say(yy)
		origin=(float(yy[0]),float(yy[1]))
		tm.lat=origin[0]
		tm.lon=origin[1]
	center=tm.fromGeographic(tm.lat,tm.lon)

	FreeCAD.c=c1
	vals=np.array([float(c) for c in c1.split()])
	#vals=vals.reshape(len(vals)/3,3)
	'''
	points=[]
	points2=[]
	points0=[]
	px=[]
	py=[]
	pz=[]
	pt=[]

	startx=None
	starty=None
	starth=None
	FreeCAD.sd=sd
	seg=sd['gpx']['trk']['trkseg']
	try:
		seg['trkpt']
		ss=seg
		seg=[ss]
	except:
		pass
	'''

	lats=[]
	lons=[]

	points=[]
	
	for v in vals:
		lats.append(float(v[0]))
		lons.append(float(v[1]))
		ll=tm.fromGeographic(float(v[0]),float(v[1]))

		points.append(FreeCAD.Vector(ll[0]-center[0],ll[1]-center[1],1000*(float(v[2]))))


	print (min(lats),max(lats))
	print (min(lons),max(lons))
	print ((max(lats)+min(lats))/2,(max(lons)+min(lons))/2)
	print ((max(lats)-min(lats))/2,(max(lons)-min(lons))/2)

	import Draft
	Draft.makeWire(points)


	return


	if orig == 'auto':
		tm.lat, tm.lon = (max(lats)+min(lats))/2,(max(lons)+min(lons))/2
		print ("origin:")
		print(tm.lat,tm.lon)
		print ("----------")



	for s in seg:
		trkpts=s['trkpt']


		n=trkpts[0]

		center=tm.fromGeographic(tm.lat,tm.lon)

#		print(trkpts)
#		for p in  trkpts:
#			print(p)

		# map all points to xy-plane
		for n in trkpts:
#			print(n['@lat'],n['@lon'])
			lats.append(float(n['@lat']))
			lons.append(float(n['@lon']))
			ll=tm.fromGeographic(float(n['@lat']),float(n['@lon']))
			h=n['ele']
#			print(h)
			tim=n['time']
			t2=re.sub('^.*T', '', tim)
			t3=re.sub('Z', '', t2)
			t4=t3.split(':')
			timx=int(t4[0])*3600+int(t4[1])*60+int(t4[2])
			pt.append(timx)
			if starth == None:
				starth=float(h)
				starth=0

			points.append(FreeCAD.Vector(ll[0]-center[0],ll[1]-center[1],1000*(float(h)-starth)))
			points.append(FreeCAD.Vector(ll[0]-center[0],ll[1]-center[1],0))
			points.append(FreeCAD.Vector(ll[0]-center[0],ll[1]-center[1],1000*(float(h)-starth)))
			points2.append(FreeCAD.Vector(ll[0]-center[0],ll[1]-center[1],1000*(float(h)-starth)+20000))
			points0.append(FreeCAD.Vector(ll[0]-center[0],ll[1]-center[1],0))
			px.append(ll[0]-center[0])
			py.append(ll[1]-center[1])
			pz.append(1000*(float(h)-starth))
#			print(ll)


	if 1:
		import Draft
		if 0: #close path
			points.append(points[0])
		
		
		
		Draft.makeWire(points0)
		
		Draft.makeWire(points)

		po=App.ActiveDocument.ActiveObject
		po.ViewObject.LineColor=(1.0,.0,0.0)
		po.MakeFace = False

		po.Placement.Base.z= float(hi) *1000
		po.Label="My Track" 

		Draft.makeWire(points2)

		po2=App.ActiveDocument.ActiveObject
		po2.ViewObject.LineColor=(.0,.0,1.0)
		po2.ViewObject.PointSize=5
		po2.ViewObject.PointColor=(.0,1.0,1.0)
		
		po2.Placement.Base.z= float(hi)*1000
		po2.Label="Track + 20m"


		App.activeDocument().recompute()
		Gui.SendMsgToActiveView("ViewFit")
		# break

	#------------------------------------------------
	# data for postprocessing

	try:
		import numpyNode
		import mathplotlibNode

		t=mathplotlibNode.createMPL()
		t.Label="My Track raw Data"

		# provide values here
		t.countSources=4
		t.source1Values=px
		t.source2Values=py
		t.source3Values=pz
		t.source4Values=pt

		t.source1Data="px"
		t.source2Data="py"
		t.source3Data="pz"
		t.source4Data="pt"
		
		t.useOut1=True
		t.useOut2=True
		t.useOut3=True
		t.useOut4=True

		# convert values
		t2=numpyNode.createNP()
		t2.Label="My Track data processed"
		t2.sourceObject=t
		t2.expression1="in1/np.max(np.abs(in1))"
		t2.label1 = "x relative"

		t2.expression2="in2/np.max(np.abs(in2))"
		t2.label2 = "y relative"

		t2.expression3="in3/np.max(np.abs(in3))"
		t2.label3 = "z relative"

		t2.expression4="-1+2*(in4-np.min(in4))/(np.max(in4)-np.min(in4))"
		t2.label4 = "time relative"

		# graphing values
		t3=mathplotlibNode.createMPL()
		t3.Label="My Track Data visualization"
		t3.record=False
		t3.useNumpy=True
		t3.sourceNumpy=t2

		t3.useOut1=True
		t3.useOut2=True
		t3.useOut3=True
		t3.useOut4=True

		t4=numpyNode.createNP()
		t4.Label="My Track Data xy"
		t4.sourceObject=t

		t4.expression2="in2"
		t4.label2 = "path xy"
		
		t4.expressionTime="in1"

		t5=mathplotlibNode.createMPL()
		t5.Label="My Track Data xy Map"
		t5.record=False
		t5.useNumpy=True
		t5.sourceNumpy=t4

		t5.useOut2=True
		FreeCAD.ActiveDocument.recompute()
	except:
		sayexc()

	print("!",orig,"!")

	return (str(tm.lat)+','+str(tm.lon))
	return px,py

if 0: 
	px,py=import_gpx()
	count=len(px)
	pp=range(count)
	px2=[]
	py2=[]

	import numpy as np
	xpp=np.array(px)
	np.average(xpp)
	std=np.std(xpp)

	for p in pp:
		if abs(px[p]) <2*std:
			px2.append(px[p])
		else:
			if px[p]>0:
				px2.append(2*std)
			else:
				px2.append(-2*std)

	for p in pp:
		if abs(py[p]) <10000:
			py2.append(py[p])
		else:
			py2.append(10000.0)
			

	import matplotlib.pyplot as plt

	#plt.plot(pp,px,pp,py)
	#plt.show()

	plt.hist(px2)
	# plt.hist(py2)
	#plt.show()


# px,py=import_gpx()

inn=FreeCAD.ConfigGet("UserAppData")



s6='''
MainWindow:
	VerticalLayout:
		id:'main'

		QtGui.QLabel:
			setText:"***   I M P O R T    LAT LON Height     ***"
		QtGui.QLabel:

		QtGui.QLabel:
			setText:"Track input filename"

		QtGui.QLineEdit:
			setText:"UserAppData/Mod/geodat/testdata/latlonh.txt"
			id: 'bl'

		QtGui.QPushButton:
			setText: "Get LatLon Height File Name"
			clicked.connect: app.getfn

		QtGui.QLabel:
			setText:"Origin (lat,lon) "

		QtGui.QLineEdit:
			setText:"50.3736049 11.191643"
#			setText:"auto"
			id: 'orig'

		QtGui.QLabel:
			setText:"relative Height of the Startpoint"

		QtGui.QLineEdit:
#			setText:"-197.55"
			setText:"0"
			id: 'h'

		QtGui.QRadioButton:
			setText: "Generate Data Nodes "
#			clicked.connect: app.run_co2


		QtGui.QPushButton:
			setText: "Run values"
			clicked.connect: app.run

'''.format(inn)

import FreeCAD,FreeCADGui

class MyApp(object):

	def run(self):
		filename=self.root.ids['bl'].text()
		try:
			rc=import_latlon(
					filename,
					self.root.ids['orig'].text(),
					self.root.ids['h'].text(),
			)
			self.root.ids['orig'].setText(rc),
		except:
				sayexc()

	def getfn(self):
		fileName = QtGui.QFileDialog.getOpenFileName(None,u"Open File",u"/tmp/");
		s=self.root.ids['bl']
		s.setText(fileName[0])


def mydialog():
	app=MyApp()

	import GeoDataWB.miki as miki

	miki=miki.Miki()
	miki.app=app
	app.root=miki

	miki.parse2(s6)
	miki.run(s6)

def importLatLonZ():
	mydialog()
