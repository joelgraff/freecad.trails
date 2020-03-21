'''import a image as elevation grid'''
# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- geodat import image to nurbs/pcl
#--
#-- microelly 2016 v 0.2
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------

from GeoDataWB.say import *
import Points

import sys
if sys.version_info[0] !=2:
	from importlib import reload



import matplotlib.pyplot as plt
import matplotlib.image as mpimg
import numpy as np
import os.path

import csv,re

import random

## create the pointcloud, grid or nurbs surface
#
# @param filename image file
# @param n size of a flat border around the area
# @param c color channel (not used)
# @param inverse invert the height
# @param kx scale the size value 1 means 1 pixel is 1 mm
# @param ky
# @param kz
# @param gengrid create a grid of the isocurves
# @param genblock create a solid with the surface as the top face
# @param genpoles create a pointcloud of the poles
# @param pointsonly create only a point cloud of the pixel points
#
# For large images the computation time can be very long, 
# so the option to run  **pointsonly** first is a good way to inspect the image data.
#
# .


def import_image(filename=None,n=10,c=2,inverse=False,kx=10,ky=10,kz=60,gengrid=True,genblock=False,genpoles=False,pointsonly=False):
	'''import_image(filename=None,n=10,c=2,inverse=False,kx=10,ky=10,kz=60,gengrid=True,genblock=False,genpoles=False,pointsonly=False)
	'''

	display_mathplot=False
	dataAsPoles=False

	if filename==None:
		filename='/home/microelly2/Schreibtisch/test_nurbs3.png'
	img = mpimg.imread(filename)

	ojn=os.path.basename(filename)

	# grey scaled image and color channel select
	if len(img.shape) == 2:
		lum_img = img
	else:
		lum_img = img[:,:,c]
		lum_img = 0.33*img[:,:,0]+0.33*img[:,:,1]+0.34*img[:,:,2]

	(lu,lv)=lum_img.shape

	if display_mathplot:
		plt.imshow(lum_img)
		plt.show()

	#create a n points border
	uu2=np.zeros((lu+2*n)*(lv+2*n))
	uu2=uu2.reshape(lu+2*n,lv+2*n)
	uu2[n:lu+n,n:lv+n]=lum_img
	lum_img=uu2

	(lu,lv)=lum_img.shape

	bz=kz+100
	if inverse: kz= -kz

	pts=[]
	uu=[]
	for u in range(lu):
		ul=[]
		for v in range(lv):
			# p=FreeCAD.Vector(ky*v,-kx*u,bz-kz*lum_img[u,v])
			r=0.001
			p=FreeCAD.Vector(ky*v+r*random.random(),-kx*u+r*random.random(),bz-kz*lum_img[u,v] +r*random.random())
			ul.append(p)
			pts.append(p)
		uu.append(ul)

	# show the points
	p=Points.Points(pts)
	Points.show(p)
	App.ActiveDocument.ActiveObject.ViewObject.ShapeColor=(1.0,.0,1.0)
	App.ActiveDocument.ActiveObject.Label="Points " + str(lv) +" " + str(lu) + " _"
	say ((("u, v, points"),u,v,len(pts)))
	Gui.updateGui()

	if pointsonly: return
	
	tt=Part.BSplineSurface()
	
	if dataAsPoles:
		pols=uu
	else:
		tt.interpolate(uu)
		#  flatten the border
		pols=tt.getPoles()


	pols2=np.array(pols)
	lup,lvp,la=pols2.shape
	zz=bz
	bord=n-2
	for u in range(lup):
		for v in range(bord):
			op=pols[u][v]
			nup=FreeCAD.Vector(op.x,op.y,zz)
			pols[u][v]=nup
			op=pols[u][-1-v]
			nup=FreeCAD.Vector(op.x,op.y,zz)
			pols[u][-1-v]=nup

	for u in range(bord):
		for v in range(lvp):
			op=pols[u][v]
			nup=FreeCAD.Vector(op.x,op.y,zz)
			pols[u][v]=nup
			op=pols[-1-u][v]
			nup=FreeCAD.Vector(op.x,op.y,zz)
			pols[-1-u][v]=nup

	bs=Part.BSplineSurface()
	knot_v2=tt.getVKnots()
	knot_u2=tt.getUKnots()
	mult_u=tt.getUMultiplicities()
	mult_v=tt.getVMultiplicities()
	ws=tt.getWeights()

	bs.buildFromPolesMultsKnots(pols,
			mult_u,
			mult_v,
			knot_u2,
			knot_v2,
			False,False,3,3,
			ws
		)

	if 1:
		sha=bs.toShape()

	# show the poles
	if genpoles:
		pols=bs.getPoles()
		ps=[]
		for l in pols:
			for po in l:
				ps.append(po)

		p=Points.Points(ps)
		Points.show(p)
		App.ActiveDocument.ActiveObject.ViewObject.ShapeColor=(1.0,1.0,.0)
		App.ActiveDocument.ActiveObject.Label='Poles '  + str(lv) +" " + str(lu) +" _"
		Gui.updateGui()


	# the nurbs grid
	if gengrid:
		jj=[]

		rr=lv
		for i in range(rr+1):
			v=bs.vIso((0.0+i)/rr).toShape()
			jj.append(v.Edge1)

		rr=lu
		for i in range(rr+1):
			v=bs.uIso((0.0+i)/rr).toShape()
			jj.append(v.Edge1)

		com=Part.makeCompound(jj)
		ttt=App.ActiveDocument.addObject('Part::Feature','Nurbsgrid ' + str(n) + ' ' + ojn)
		ttt.ViewObject.DisplayMode = "Wireframe"
#		ttt.ViewObject.hide()
		ttt.Shape=com
		ttt.Placement.Base.z=10
		Gui.updateGui()
		return


	#create the solid
	a=FreeCAD.Vector(0,0,-bz)
	b=FreeCAD.Vector(0,-kx*(lu-1),-bz)
	c=FreeCAD.Vector(ky*(lv-1),-kx*(lu-1),-bz)
	d=FreeCAD.Vector(ky*(lv-1),0,-bz)

	ad=FreeCAD.Vector(0,0,bz)
	bd=FreeCAD.Vector(0,-kx*(lu-1),bz)
	cd=FreeCAD.Vector(ky*(lv-1),-kx*(lu-1),bz)
	dd=FreeCAD.Vector(ky*(lv-1),0,bz)


	# for nonlinear borders - experimental
	if 0:
		u0e=bs.uIso(0).toShape()
		p=Part.makePolygon([ad,a,d,dd],True)
		ll=p.Edges+[u0e.Edge1]
		f4=Part.makeFilledFace(Part.__sortEdges__(ll))
		Part.show(f4)

		v0e=bs.vIso(0).toShape()
		p=Part.makePolygon([bd,b,a,ad],True)
		ll=p.Edges+[v0e.Edge1]
		f1=Part.makeFilledFace(Part.__sortEdges__(ll))
		#Part.show(v0e)
		#Part.show(p)
		Part.show(f1)

		u1e=bs.uIso(1).toShape()
		p=Part.makePolygon([bd,b,c,cd],True)
		ll=p.Edges+[u1e.Edge1]
		f2=Part.makeFilledFace(Part.__sortEdges__(ll))
		# f2=Part.Face(Part.__sortEdges__(ll))
		#Part.show(u1e)
		#Part.show(p)
		Part.show(f2)

		v1e=bs.vIso(1).toShape()
		p=Part.makePolygon([dd,d,c,cd],True)
		ll=p.Edges+[v1e.Edge1]
		f3=Part.makeFilledFace(Part.__sortEdges__(ll))
		#Part.show(v1e)
		#Part.show(p)
		Part.show(f3)

		p=Part.makePolygon([a,b,c,d], True)
		f0=Part.makeFilledFace(p.Edges)
		Part.show(f0)

	if 1:
		nb=App.ActiveDocument.addObject('Part::Spline','Nurbs ' + str(n) +   ' ' + ojn)
		nb.Shape=sha.Face1
		

	if genblock:

		fln=sha.Face1

		f0=Part.Face(Part.makePolygon([a,b,c,d], True))
		f1=Part.Face(Part.makePolygon([ad,bd,b,a], True)) 
		f2=Part.Face(Part.makePolygon([b,bd,cd,c], True))
		f3=Part.Face(Part.makePolygon([cd,dd,d,c], True)) 
		f4=Part.Face(Part.makePolygon([ad,a,d,dd], True))

		fls=[f0,f1,f2,f3,f4,fln]
		sh=Part.Shell(fls)
		sol=Part.Solid(sh)

		ttt=App.ActiveDocument.addObject('Part::Feature','Nurbsblock ' + str(n) +   ' ' + ojn)
		ttt.Shape=sol
#		ttt.ViewObject.hide()

	print (lu,lv)
	return bs


# bs=createNurbsblock('/home/microelly2/Schreibtisch/fisch.jpg',5,0,True,1000,1000,10)


#bs=createNurbsblock('/home/microelly2/Bilder/fcsw.png',5,0,True,10,10,40)
#bs=createNurbsblock('/home/microelly2/Schreibtisch/freeka.png',10,0,1,100,100,400)

#jpeg brauch kleiner werte #+#
#bs=createNurbsblock('/home/microelly2/Schreibtisch/quick61.jpg',10,0,True,100,100,3)
#bs=createNurbsblock('/home/microelly2/Schreibtisch/normanc.jpg',10,0,True,100,100,4)



sdialog='''
#VerticalLayoutTab:
MainWindow:
	VerticalLayout:
		id:'main'

		QtGui.QLabel:
			setText:"***   I M A G E   T O    N U R B S    ***"

	VerticalLayout:
		id:'img1'
#		setVisible:False

		QtGui.QPushButton:
			setText: "Browse for input data filename"
			clicked.connect: app.getfn

		QtGui.QLineEdit:
			setText:"UserAppData/Mod/geodat/testdata/freeka.png"
			id: 'bl'

		HorizontalLayout:
			QtGui.QLabel:
				setText:"Scale  "

			QtGui.QLineEdit:
				setText:"10"
				id: 'kx'

			QtGui.QLineEdit:
				setText:"10"
				id: 'ky'

			QtGui.QLineEdit:
				setText:"60"
				id: 'kz'

		QtGui.QCheckBox:
			id: 'inverse' 
			setText: 'Invert Height'
			setChecked: False

		QtGui.QLabel:
			setText:"Border Size "

		QtGui.QLineEdit:
			setText:"5"
			id: 'border'

		QtGui.QLabel:
			setText:"Color Channel RGB 012 3-grey noimp "

		QtGui.QLineEdit:
			setText:"2"
			id: 'color'

		QtGui.QCheckBox:
			id: 'pointsonly' 
			setText: 'create only a Pointcloud'
			setChecked: True


		QtGui.QCheckBox:
			id: 'gengrid' 
			setText: 'create Nurbs Grid'
			setChecked: True

		QtGui.QCheckBox:
			id: 'genblock' 
			setText: 'create Nurbsblock Solid'
			setChecked: False

		QtGui.QCheckBox:
			id: 'genpoles' 
			setText: 'create Pole Cloud'
			setChecked: False


	QtGui.QPushButton:
		setText: "import image"
		id:'run'
		clicked.connect: app.run

'''

## the gui backend


class MyApp(object):


	def run(self):
		'''load the file and create a nurbs surface'''
		try:
			filename=self.root.ids['bl'].text()
			if filename.startswith('UserAppData'):
				filename=filename.replace('UserAppData',FreeCAD.ConfigGet("UserAppData"))

			ts=time.time()
			bs=import_image(
					filename,

					int(self.root.ids['border'].text()),
					int(self.root.ids['color'].text()),
					self.root.ids['inverse'].isChecked(),

					int(self.root.ids['kx'].text()),
					int(self.root.ids['ky'].text()),
					int(self.root.ids['kz'].text()),

					self.root.ids['gengrid'].isChecked(),
					self.root.ids['genblock'].isChecked(),
					self.root.ids['genpoles'].isChecked(),
					self.root.ids['pointsonly'].isChecked(),
				)
			te=time.time()
			say("load image time " + str(round(te-ts,2)))
		except:
			sayexc()

	def getfn(self):
		''' get the filename of the image file'''
		fileName = QtGui.QFileDialog.getOpenFileName(None,u"Open File",u"/tmp/");
		print(fileName)
		self.root.ids['bl'].setText(fileName[0])

## the gui startup

def mydialog(run=True):

	app=MyApp()

	import GeoDataWB.miki as miki
	reload(miki)

	miki=miki.Miki()
	miki.app=app
	app.root=miki

	miki.parse2(sdialog)
	miki.run(sdialog)
	return miki



## start and hide the gui dialog
def runtest():
	m=mydialog()
	m.objects[0].hide()


if __name__ == '__main__':
	runtest()

def importImage():
	mydialog()
