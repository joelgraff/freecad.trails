# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- gpx importer
#--
#-- microelly 2016 v 0.0
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------

import FreeCAD
from .transversmercator import TransverseMercator
from .say import say, sayexc
from PySide import QtGui

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

def import_latlon(filename,orig,hi,op):
	# content=trackstring

#	fn='/home/microelly2/FCB/b202_gmx_tracks/im_haus.gpx'
#	filename='/home/microelly2/FCB/b202_gmx_tracks/neufang.gpx'

	f=open(filename,"r")
	c1=f.read()

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

	import numpy as np
	FreeCAD.c=c1
	vals=[]
	for c in c1.split():
		vals.append(float(c))
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
	except Exception:
		pass
	'''

	lats=[]
	lons=[]

	points=[]
	for i in range(0, len(vals), 3):
		print(vals[i],vals[i+1],vals[i+2])
		lats.append(float(vals[i]))
		lons.append(float(vals[i+1]))
		ll=tm.fromGeographic(float(vals[i]),float(vals[i+1]))
		points.append(FreeCAD.Vector(ll[0]-center[0],ll[1]-center[1],1000*(float(vals[i+2]))))

	print (min(lats),max(lats))
	print (min(lons),max(lons))
	print ((max(lats)+min(lats))/2,(max(lons)+min(lons))/2)
	print ((max(lats)-min(lats))/2,(max(lons)-min(lons))/2)

	if op == True:
		# Get or create "Point_Groups".
		try:
			PointGroups = FreeCAD.ActiveDocument.Point_Groups
		except Exception:
			PointGroups = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroup", 'Point_Groups')
			PointGroups.Label = "Point Groups"

		# Get or create "Points".
		try:
			FreeCAD.ActiveDocument.Points
		except Exception:
			Points = FreeCAD.ActiveDocument.addObject('Points::Feature', "Points")
			PointGroups.addObject(Points)

		PointGroup = FreeCAD.ActiveDocument.addObject('Points::Feature', "Point_Group")
		PointGroup.Label = "LatLonH"
		FreeCAD.ActiveDocument.Point_Groups.addObject(PointGroup)
		PointObject = PointGroup.Points.copy()
		PointObject.addPoints(points)
		PointGroup.Points = PointObject
	else:
		import Draft
		Draft.makeWire(points)

	FreeCAD.ActiveDocument.recompute()
	return

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

		QtGui.QRadioButton:
			setText: "Only points"
			id: 'op'


		QtGui.QPushButton:
			setText: "Run values"
			clicked.connect: app.run

'''.format(inn)

class MyApp(object):

	def run(self):
		filename=self.root.ids['bl'].text()
		try:
			rc=import_latlon(
					filename,
					self.root.ids['orig'].text(),
					self.root.ids['h'].text(),
					self.root.ids['op'].isChecked(),
			)
			self.root.ids['orig'].setText(rc),
		except Exception:
				sayexc()

	def getfn(self):
		fileName = QtGui.QFileDialog.getOpenFileName(None,u"Open File",u"/tmp/");
		s=self.root.ids['bl']
		s.setText(fileName[0])


def mydialog():
	app=MyApp()

	from . import miki

	miki=miki.Miki()
	miki.app=app
	app.root=miki

	miki.parse2(s6)
	miki.run(s6)

def importLatLonZ():
	mydialog()
