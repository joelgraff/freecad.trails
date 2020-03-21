'''textures on nurbs use cases heights and sun intensity'''
# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- textures on nurbs use cases heights and sun intensity
#--
#-- microelly 2016 v 0.3
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------

#\cond
import Draft
import FreeCADGui,FreeCAD
App=FreeCAD
Gui=FreeCADGui

from importlib import reload

import numpy as np
import geodat
import time
import cv2
import matplotlib
#\endcond


def getHeights(nsf,size=16,scale=0.001,normalized=True):
	'''arr = getHeights(nsf,size=16,,scale=0.001,normalized=True) 
	calculates an array with the shape 16 * 16 
	the values are the heights of the bsplinesurface nsf at the grid points'''

	kzs=np.zeros((size+1,size+1),np.float)
	for ux in range(size+1):
		for vx in range(size+1):
			u=float(ux)/size
			v=float(vx)/size
			p=nsf.value(u,v)
			kzs[ux,vx]=p[2]

	kzs *= scale

	if normalized:
		kzs -= kzs.min()
		kzs /= kzs.max()

	return kzs

## @return array shape size x size x 3 (grid of vectors)

def getNormals(nsf,size=16,direction=FreeCAD.Vector(0,0,1)):
	'''arr = getNormals(nsf,size=16,direction=FreeCAD.Vector(0,0,1))
	calculate the difference of the normal vector on a size *size grid for the grid points on the surface nsf'''

	direction.normalize()
	kzs=np.zeros((size+1,size+1),np.float)
	for ux in range(size+1):
		for vx in range(size+1):
			u=float(ux)/size
			v=float(vx)/size
			(t1,t2)=nsf.tangent(u,v)
			# calculate the normal vector and how it differs from the given direction
			n=t1.cross(t2)
			kzs[ux,vx]=n*direction

	return kzs


## @return filename of the colormap image


def createColor(kzs,size,mode):
	'''filename=createColor(kzs,size,mode)
	creates a colormap for the values of the array
	mode 1 cmap(1-t)
	mode 2 cmap(t)
	the colormap is stored as a temp file and the filepath is returned
	'''

	img= np.zeros((size+1,size+1,3), np.uint8)

	#cmap = matplotlib.cm.get_cmap('jet')
	cmap = matplotlib.cm.get_cmap('hsv')

	for ux in range(size+1):
		for vx in range(size+1):
			t=kzs[ux,vx]
			
			if mode == 1: (r,g,b,a)=cmap(1-t)
			if mode == 2: (r,g,b,a)=cmap(t)
			img[size-vx,size-ux]=(255*r,255*g,255*b)

#	cv2.applyColorMap(img, cv2.COLORMAP_JET)

	#cv2.imshow('image2',img)
	import tempfile
	fn=tempfile.mkdtemp()
	fn +='_image_'+str(size)+'.png'
	cv2.imwrite(fn,img)
	return fn


def createColor2(kzs,size,mode):
	''' fuer elevationgrid '''

	img= np.zeros((size+1,size+1,3), np.uint8)

	#cmap = matplotlib.cm.get_cmap('jet')
	cmap = matplotlib.cm.get_cmap('hsv')

	for ux in range(size+1):
		for vx in range(size+1):
			t=kzs[ux,vx]
			
			if mode == 1: (r,g,b,a)=cmap(1-t)
			if mode == 2: (r,g,b,a)=cmap(t)
			#img[size-vx,size-ux]=(255*r,255*g,255*b)
			#img[size-vx,size-ux]=(255*r,255*g,255*b)
			img[size-vx,ux]=(255*r,255*g,255*b)

#	cv2.applyColorMap(img, cv2.COLORMAP_JET)

	#cv2.imshow('image2',img)
	import tempfile
	fn=tempfile.mkdtemp()
	fn +='_image_'+str(size)+'.png'
	cv2.imwrite(fn,img)
	return fn

#
#
# use cases
#





'''
#
# Height map
#

s=64

kzs=getHeights(nurbs.Shape.Surface,s)
fn=createColor(kzs,s,1)
geodat.geodat_lib.addImageTexture(nurbs,fn,scale=(1,1))
Gui.updateGui()
App.ActiveDocument.Text.LabelText=["Height Map","colormap HSV",str(s**2) + " color pixel"]

'''

'''
#
#  Height map animation with different solutions
#

for s in 4,8,16,32:
	kzs=getHeights(nurbs.Shape.Surface,s)
	fn=createColor(kzs,s,1)
	geodat.geodat_lib.addImageTexture(nurbs,fn,scale=(1,1))
	Gui.updateGui()
	time.sleep(0.4)
'''

'''
#
# How planar is the surface - normals
#

for s in 4,8,16,32,64,256:
	kzs=getNormals(nurbs.Shape.Surface,s)
	fn=createColor(kzs,s,1)
	geodat.geodat_lib.addImageTexture(nurbs,fn,scale=(1,1))
	Gui.updateGui()
	time.sleep(0.4)
'''

'''
nurbs=App.ActiveDocument.QuadNurbs


#
# flow of the sun from 6:00 a.m. until 6:00 p.m. in 60 steps
#

for h in range(61):
	s=100

	App.ActiveDocument.Text.LabelText=["Simulation Sun, Day time",str(6.0+ 12.0*h/60),str(s**2) + " color pixel"]

	kzs=getNormals(nurbs.Shape.Surface,s,FreeCAD.Vector(np.cos(np.pi*h/60),-np.sin(np.pi*h/60),np.sin(np.pi*h/60)))

	# evening sun
	# kzs=getNormals(nurbs.Shape.Surface,s,FreeCAD.Vector(-1,-1,2-0.05*h))

	# from axo view
	# kzs=getNormals(nurbs.Shape.Surface,s,FreeCAD.Vector(1,-1,2-0.05*h))

	fn=createColor(kzs,s,2)
	geodat.geodat_lib.addImageTexture(nurbs,fn,scale=(1,1))
	Gui.updateGui()

'''






## test create a surface and add a elevation image testure 
def runtest():
	import geodat.testdata
	reload(geodat.testdata)

	nurbs=geodat.testdata.bspline()
	pcl=geodat.testdata.pcl()

	import geodat.geodat_lib
	fn=geodat.testdata.image(mirroru=True)

	geodat.geodat_lib.addImageTexture(nurbs,fn,scale=(1,2))
	Gui.updateGui()


	fn=geodat.testdata.image(mirroru=True)
	geodat.geodat_lib.addImageTexture(nurbs,fn,scale=(1,1))
	App.ActiveDocument.recompute()
	Gui.updateGui()


if __name__ == '__main__':
	runtest()


