''' geodat import AST (gdal)'''
# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- geodat import AST (gdal)
#--
#-- microelly 2016 v 0.1
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------

#http://geoinformaticstutorial.blogspot.de/2012/09/reading-raster-data-with-python-and-gdal.html
#http://forum.freecadweb.org/viewtopic.php?f=8&t=17647&start=10#p139201

# the ast file is expected in ~/.FreeCAD/geodat/AST
# FreeCAD.ConfigGet("UserAppData") +'/geodat/AST/ASTGTM2_' + ff +'_dem.tif'

'''
ASTER GDEM Policy Agreements
I agree to redistribute the ASTER GDEM *only* to individuals within my organization or project of intended use or in response to disasters in support of the GEO Disaster Theme.
When presenting or publishing ASTER GDEM data, I agree to include "ASTER GDEM is a product of METI and NASA."

Because there are known inaccuracies and artifacts in the data set, please use the product with awareness of its limitations. The data are provided "as is" and neither NASA nor METI/ERSDAC will be responsible for any damages resulting from use of the data.
'''

from GeoDataWB.say import *

from  GeoDataWB.transversmercator import TransverseMercator

import gdal
from gdalconst import * 


import WebGui
import Points



def import_ast(b=50.26,l=11.39):
	'''get the data from a downloaded file
	the file is expected in FreeCAD.ConfigGet("UserAppData") + '/geodat/AST/'
	with the common filename for lan/lot parameters 
	example .../.FreeCAD/geodat/AST/ASTGTM2_N51E010_dem.tif
	'''

	import numpy as np

	bs=np.floor(b)
	ls=np.floor(l)

	# the ast dataset
	ff="N%02dE%03d" % (int(bs),int(ls))
	fn=FreeCAD.ConfigGet("UserAppData") +'geodat/AST/ASTGTM2_' + ff +'_dem.tif'
	print(fn)

	'''
	fn='/home/microelly2/FCB/b217_heightmaps/tandemx_daten/Chile-Chuquicatmata.tif'
	b=-22.3054705
	l=-68.9259643
	bs=np.floor(b)
	ls=np.floor(l)
	print(fn)
	'''


	dataset = gdal.Open(fn, GA_ReadOnly) 
	if dataset == None:
		msg="\nProblem cannot open " + fn + "\n"
		FreeCAD.Console.PrintError(msg)
		errorDialog(msg)
		return

	cols=dataset.RasterXSize
	rows=dataset.RasterYSize

	geotransform = dataset.GetGeoTransform()
	originX = geotransform[0]
	originY = geotransform[3]
	pixelWidth = geotransform[1]
	pixelHeight = geotransform[5]

	band = dataset.GetRasterBand(1)
	data = band.ReadAsArray(0, 0, cols, rows)

	#data.shape -> 3601 x 3601 secs
	# erfurt 51,11
	#data[0,0]
	# zeitz  51,12
	#data[3600,0]
	# windischletten(zapfendorf) 50,11
	#data[0,3600]
	# troestau fichtelgebirge 50,12
	#data[3600,3600]

	px=int(round((bs+1-b)*3600))
	py=int(round((l-ls)*3600))


	pts=[]
	d=70

	d1=20
	d2=50
	d1=d
	d2=d


	tm=TransverseMercator()
	tm.lat=b
	tm.lon=l
	center=tm.fromGeographic(tm.lat,tm.lon)

	z0= data[px,py] # relative height to origin px,py

	for x in range(px-d1,px+d1):
		for y in range(py-d2,py+d2):
			ll=tm.fromGeographic(bs+1-1.0/3600*x,ls+1.0/3600*y)
			pt=FreeCAD.Vector(ll[0]-center[0],ll[1]-center[1], 1000.0* (data[x,y]-z0))
			pts.append(pt)

	# display the point cloud
	p=Points.Points(pts)
	Points.show(p)

	return pts

s6='''
MainWindow:
	VerticalLayout:
		id:'main'
#		setFixedHeight: 600
		setFixedWidth: 600
		move:  PySide.QtCore.QPoint(3000,100)

		QtGui.QLabel:
			setText:"C O N F I G U R A T I O N"
		QtGui.QLabel:


		QtGui.QLineEdit:
			id: 'bl'

			# zeyerner wand **
			#(50.2570152,11.3818337)

			# outdoor inn *
			#(50.3737109,11.1891891)

			# roethen **
			#(50.3902794,11.157629)

			# kreuzung huettengrund nach judenbach ***
			#(50.368209,11.2016135)

			setText:"50.368209,11.2016135"
			# coburg zentrum
			setText:"50.2639926,10.9686946"

		QtGui.QPushButton:
			setText: "Create height models"
			clicked.connect: app.runbl

		QtGui.QPushButton:
			setText: "show Map"
			clicked.connect: app.showMap

'''


## the gui backend
class MyApp(object):

	## create the height model
	def runbl(self):
		bl=self.root.ids['bl'].text()
		spli=bl.split(',')
		b=float(spli[0])
		l=float(spli[1])
		s=15
		import_heights(float(b),float(l),float(s))

	## display the location in openstreeetmap
	def showMap(self):
		bl=self.root.ids['bl'].text()
		spli=bl.split(',')
		b=float(spli[0])
		l=float(spli[1])
		s=15
		WebGui.openBrowser( "http://www.openstreetmap.org/#map=16/"+str(b)+'/'+str(l))


## the dialog to import a gdal file

def mydialog():
	'''the dialog to import a gdal file'''

	app=MyApp()
	import GeoDataWB.miki as gmiki
	miki=gmiki.Miki()

	miki.app=app
	app.root=miki

	miki.run(s6)
	FreeCAD.mm=miki
	return miki


## import heigjs using import_xyz

def import_heights(b,l,s):

	import GeoDataWB.import_xyz

	ts=time.time()

	pcl=import_ast(b,l)
	pts=pcl
	ff="N" + str(b) + " E" + str(l)

	nurbs=GeoDataWB.import_xyz.suv2(ff,pts,u=0,v=0,d=140,la=140,lb=140)
	te=time.time()
	print ("time to create models:",te-ts)

	fn=GeoDataWB.geodat_lib.genSizeImage(size=512)
	# geodat.geodat_lib.addImageTexture(nurbs,fn,scale=(8,3))
	nurbs.ViewObject.Selectable = False



## test start and hide the dialog
def runtest():
	m=mydialog()
	m.objects[0].hide()


if __name__ == '__main__':
	runtest()

def importASTER():
	mydialog()
