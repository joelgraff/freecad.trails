'''create height map image'''
# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- geodat height map texture
#--
#-- microelly 2016 v 0.1
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------

from importlib import reload
import FreeCAD as App

import numpy as np
from matplotlib import cm
import matplotlib.pyplot as plt
import matplotlib.mlab as ml
from mpl_toolkits.mplot3d.axes3d import *




def gengrid(pcl):
	'''transforms the pointcloud pcl into a rectangle grid
	assume the points are arranged in xy directions
	returns a numpy array
	'''

	xmin=pcl.Points.BoundBox.XMin
	xmax=pcl.Points.BoundBox.XMax
	ymin=pcl.Points.BoundBox.YMin
	ymax=pcl.Points.BoundBox.YMax

	for i,p in enumerate(pcl.Points.Points):
		if p.x== xmin and p.y == ymin: 
			print ("a",i,p)
			a=i
		if p.x== xmax and p.y == ymin: 
			print ("b",i,p)
			b=i
		if p.x== xmin and p.y == ymax: 
			print ("c",i,p)
			c=i
		if p.x== xmax and p.y == ymax: 
			print ("d",i,p)
			d=i

	assert(a-b==c-d)
	assert(a-c==b-d)

	lx=b-a+1
	ly=(a-c)/lx +1 

	assert(lx*ly==len(pcl.Points.Points))

	pts=np.array(pcl.Points.Points)
	grid=pts.reshape(lx,ly,3)
	print ("dim grind ", len(pcl.Points.Points),lx,ly)
	return grid


## create and display a matplotlib plot

def mpl3Dplot(grid):
	'''mpl3Dplot(grid)'''

	xs=grid[0,:,0]
	ys=grid[:,0,1]

	# z-werte als matrix
	zs=grid[:,:,2]
	zs *= -1

	X, Y = np.meshgrid(xs, ys)
	fig = plt.figure()
	ax = Axes3D(fig)
	ax.plot_surface(X, Y, zs, rstride=1, cstride=1, cmap=cm.jet,linewidth=1, antialiased=True)
	plt.show()



import cv2

## create cv2 image file

def cv2plot(grid,fn="/tmp/foo.png",cmap=cv2.COLORMAP_JET):
	''' create cv2 image file 
	returns the cv2 image object
	'''

	zs=np.array(grid[:,:,2], np.uint8)
	x,y=zs.shape
	assert(x==y) # momentan nur quadrate
	xa = x-3
	# mystic swap of the axis #+#
	if (4<=xa and xa<32) or (16<=xa and xa<32) or (64<=xa and xa<128):
		flip=0
	else: 
		flip=1

	zz=np.zeros((x+1)*(y+1), np.uint8)
	zz=zz.reshape(x+1,y+1)
	zz[:-1,:-1]=zs
	zs=zs[2:-2,2:-2]
	print ("x,y,flip",x,y,flip)
	if flip:
		zs=zs.swapaxes(0,1)
		zs1=cv2.flip(zs,1)
		zs2=cv2.flip(zs1,0)
		zs=zs2

	zs = -zs
	zs -= zs.min()
	zs *= 255/zs.max()

#	im_color = cv2.applyColorMap(zs, cv2.COLORMAP_RAINBOW)
#	im_color = cv2.applyColorMap(zs, cv2.COLORMAP_JET)
#	im_color = cv2.applyColorMap(zs, cv2.COLORMAP_HSV)

	im_color = cv2.applyColorMap(zs, cmap)

	s=max(x,y)
	im_color=cv2.resize(im_color,(s,s), interpolation = cv2.INTER_CUBIC)

	cv2.imwrite(fn,im_color)
	return im_color


import geodat.geodat_lib as geodat_lib
reload(geodat_lib)


## test case

def run(testnumber):
	''' run a test '''

	c=testnumber

	if c==1:
		pcl=App.ActiveDocument.Points009
		nurbs=App.ActiveDocument.mynurbs007

	if c == 2:
		pcl=App.ActiveDocument.Points004
		nurbs=App.ActiveDocument.mynurbs003

	if c == 3:
		pcl=App.ActiveDocument.Points003
		nurbs=App.ActiveDocument.mynurbs002

	if c == 4:
		pcl=App.ActiveDocument.Points002
		nurbs=App.ActiveDocument.mynurbs001

	if c == 5:
		pcl=App.ActiveDocument.Points006
		nurbs=App.ActiveDocument.mynurbs004

	if c == 6:
		pcl=App.ActiveDocument.Points007
		nurbs=App.ActiveDocument.mynurbs005

	if c == 7:
		pcl=App.ActiveDocument.Points002
		nurbs=App.ActiveDocument.mynurbs


	grid=gengrid(pcl)

	im=cv2plot(grid, cv2.COLORMAP_RAINBOW)
	# cv2.COLORMAP_HSV
	#im=cv2plot(grid, cv2.COLORMAP_JET)


	geodat_lib.addImageTexture(nurbs,"/tmp/foo.png",scale=(1,1))
	#add(nurbs,"/tmp/100_200.png")

	mpl3Dplot(grid)


## Height map image generator
# generates a height map image and insert it as a soTexture2 node to the part
# 

class gen_heightmap():
	''' create a heightmap texture for a nurbs'''
	
	def test(self):
		''' run test for one face'''
		run(1)

	def testall(self):
		''' run test for all faces'''
		for i in 1,2,3,4,5,6,7:
			run(i)


gen_heightmap().test()




