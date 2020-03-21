'''create a house lod2 a'''

## Haus
# @todo : make the house parametric
#
#

class house():
	pass


import FreeCAD,FreeCADGui
import Part
import math



#\cond
def viereck(le,wi,he,inlea=0,inleb=0,inwia=0,inwib=0):
	'''gugu'''
	liste=[
		(0+inlea,inwia,he),
		(le-inleb,inwia,he),
		(le-inleb,wi-inwib,he),
		(inlea,wi-inwib,he),
		(inlea,inwia,he)
		]
	return liste


#\endcond


#\cond
def gen_haus0(le,wi,hiall,hi,midx,wx,midy,wy):


	he=hiall
	he3=hi

	inle=8
	inwi=2
	if wx==0: wx=0.0001
	if wy==0: wy=0.0001

	if midx<0.5:
		bix=le*midx
	else:
		bix=le*(1-midx)

	if midy<0.5:
		biy=wi*midy
	else:
		biy=wi*(1-midy)

	list1=viereck(le,wi,0)
	list2=viereck(le,wi,he)
	list3=viereck(le,wi,he3,
		le*midx-bix*wx,le-(le*midx+bix*wx),
		wi*midy-biy*wy,wi-(wi*midy+biy*wy),
	)

	poly1 = Part.makePolygon( list1)
	poly3 = Part.makePolygon( list3)
	face1 = Part.Face(poly1)
	face3 = Part.Face(poly3)
	faceListe=[face1,face3]

	for i in range(len(list1)-1):
		liste3=[list1[i],list1[i+1],list2[i+1],list2[i],list1[i]]
		poly=Part.makePolygon(liste3)
		face = Part.Face(poly)
		faceListe.append(face)

	for i in range(len(list2)-1):
		liste3=[list2[i],list2[i+1],list3[i+1],list3[i],list2[i]]
		poly=Part.makePolygon(liste3)
		face = Part.Face(poly)
		faceListe.append(face)

	myShell = Part.makeShell(faceListe)   
	mySolid = Part.makeSolid(myShell)
	return mySolid
#\endcond


## create a house as part
 
def gen_haus(le,wi,hiall,hi,ang,midx=0.7,wx=0.5,midy=0.5,wy=0):
	h=gen_haus0(le,wi,hiall,hi,midx,wx,midy,wy)
	Part.show(h)
	p=FreeCAD.ActiveDocument.ActiveObject
	p.Placement.Rotation.Angle=ang*math.pi/180
	return p



s6='''
MainWindow:
	VerticalLayout:
		id:'main'
		setFixedHeight: 800
		setFixedWidth: 600
		move:  PySide.QtCore.QPoint(3000,100)

		QtGui.QLabel:
			setText:"B U I L D I N G LoD2 -- C O N F I G U R A T I O N"

		QtGui.QLabel:
		QtGui.QLabel:
			setText:"D I M E N S I O N S   O F   T H E    H O U S E"
		QtGui.QLabel:


		QtGui.QLabel:
			setText:"x-dim"
		QtGui.QLineEdit:
			setText:"10000"
			id: 'le'

		QtGui.QLabel:
			setText:"y-dim"
		QtGui.QLineEdit:
			setText:"12000"
			id: 'wi'

		QtGui.QLabel:
			setText:"height block"
		QtGui.QLineEdit:
			setText:"6000"
			id: 'hiall'


		QtGui.QLabel:
			setText:"height all (block + roof)"
		QtGui.QLineEdit:
			setText:"9000"
			id: 'hi'


#		QtGui.QLabel:
#		QtGui.QLineEdit:
#			setText:"50.3736049,11.191643"
#			id: 'bl'

		QtGui.QLabel:
		QtGui.QLabel:
			setText:"F O R M    O F   T H E    R O O F"
		QtGui.QLabel:



		QtGui.QLabel:
			setText:"midx"
		QtGui.QSlider:
			id:'midx'
			setOrientation: PySide.QtCore.Qt.Orientation.Horizontal
			setMinimum: 0
			setMaximum: 100
			setTickInterval: 10
			setValue: 50
			setTickPosition: QtGui.QSlider.TicksBothSides

		QtGui.QLabel:
			setText:"wx"
		QtGui.QSlider:
			id:'wx'
			setOrientation: PySide.QtCore.Qt.Orientation.Horizontal
			setMinimum: 0
			setMaximum: 100
			setTickInterval: 10
			setValue: 50
			setTickPosition: QtGui.QSlider.TicksBothSides

		QtGui.QLabel:
			setText:"midy"
		QtGui.QSlider:
			id:'midy'
			setOrientation: PySide.QtCore.Qt.Orientation.Horizontal
			setMinimum: 0
			setMaximum: 100
			setTickInterval: 10
			setValue: 50
			setTickPosition: QtGui.QSlider.TicksBothSides

		QtGui.QLabel:
			setText:"wy"
		QtGui.QSlider:
			id:'wy'
			setOrientation: PySide.QtCore.Qt.Orientation.Horizontal
			setMinimum: 0
			setMaximum: 100
			setTickInterval: 10
			setValue: 100
			setTickPosition: QtGui.QSlider.TicksBothSides

		QtGui.QLabel:
		QtGui.QLabel:
		QtGui.QPushButton:
			setText: "Build the house"
			clicked.connect: app.gen_house

		QtGui.QLabel:
		QtGui.QLabel:

		QtGui.QLabel:
			setText:'Position'
		QtGui.QLineEdit:
			setText:"50.3736049,11.191643"
			id: 'bl'

		QtGui.QLabel:
			setText:'Orientation'
		QtGui.QLineEdit:
			setText:"90"
			id: 'bl'


'''

## Gui backend

class MyApp(object):

	## create a house
	def gen_house(self):
		le=float(self.root.ids['le'].text())
		wi=float(self.root.ids['wi'].text())
		hiall=float(self.root.ids['hiall'].text())
		hi=float(self.root.ids['hi'].text())
		midy=1-float(self.root.ids['midx'].value())/100
		midx=float(self.root.ids['midy'].value())/100
		wy=float(self.root.ids['wx'].value())/100
		wx=float(self.root.ids['wy'].value())/100

		s= gen_haus(le,wi,hiall,hi,90,midx,wx,midy,wy)
		s.ViewObject.ShapeColor=(1.0,0.0,0.0)


## the dialog to create a house

import sys
if sys.version_info[0] !=2:
		from importlib import reload


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

## test start and hide the dialog
def runtest():
	m=mydialog()
	m.objects[0].hide()



def createHouse():
	mydialog()
