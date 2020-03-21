# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- geodat python library
#--
#-- microelly 2016 v 0.1
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------

import FreeCAD
import cv2
import numpy as np
from pivy import coin
import time




def getShape(pts):

	sx=pts[0][0]
	sy=pts[0][1]
	d0=0

	for i,p in enumerate(pts):
		ex=p[0]
		ey=p[1]
		d=abs(sx-ex)+abs(sy-ey)
		if d<d0:
#			print ("found ", i,p)
			break
		d0=d

	assert(len(pts)%i == 0)
	return i,len(pts)//i


def reduceGrid(pts,ku=100,kv=50):
	''' simplify data '''

	wb, eb, sb, nb = 3, 3, 3, 1
	lu,lv=getShape(pts)

	pts2=[]
	for v in range(lv):
		if v<sb or v>lv-nb-1:
			pass
		else:
			if v%kv !=0: continue
		for u in range(lu):
			if u<wb or u>lu-eb-1:
				pass
			else:
				if u%ku !=0: continue 
			pts2.append(pts[v*lu+u])

	p=Points.Points(pts2)
	Points.show(p)
	return pts2


def showFrame(pts,u=0,v=0,d=10,lu=None,lv=None):

	if lu == None or lv == None:
		lu,lv=getShape(pts)

	assert(u+d<lu)
	assert(v+d<lv)

	try:
		ff=FreeCAD.ActiveDocument.frame
	except:
		ff=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","frame")
		ViewProvider(ff.ViewObject)

	a,b,c,d = pts[u+v*lu], pts[u+v*lu+d],  pts[u+v*lu +d*lu +d],pts[u+v*lu +d*lu],
	sha=Part.makePolygon([a,b,c,d,a])

	ff.Shape=sha

def removeFrame():
	App.ActiveDocument.removeObject("frame")

#showFrame(pts)
#showFrame(pts,9,8,5,lu,lv)








def genTestImage(fn="/tmp/100_200.png"):
	''' create a test image '''

	img=np.zeros(100*200*3,np.uint8)
	img=img.reshape(100,200,3)

	img[0:49,0:99]=[0,0,255]
	img[50:100,0:99]=[0,255,0]
	img[0:49,100:200]=[0,255,255]
	img[50:100,100:200]=[255,0,0]

	for i in range(100):
		img[i,2*i]=(255,255,255)
		img[i,199-2*i]=(255,255,255)

	img[1:5,:]=[255,0,255]
	img[-5:-1,:]=[255,0,255]
	img[:,1:5]=[255,0,255]
	img[:,-5:-1]=[255,0,255]

	cv2.imwrite(fn,img)


def genSizeImage(size=32):
	''' create a quadratic test image of given size
	save it to /tmp/
	and return the filepath
	'''

	img=np.zeros(size*size*3,np.uint8)
	img=img.reshape(size,size,3)
	t=size/2-1
	
	img[:,:,:]=255
	img[1:t,1:size-2]=[0,0,255]
	img[t+1:size-2,1:size-2]=[0,255,0]
	img[1:t,t+1:size-2]=[0,255,255]
	img[t+1:size-2,t+1:size-2]=[255,0,0]

	for i in range(size):
		img[i,i]=(255,255,255)
		img[i,size-1-i]=(255,255,255)

	img[1:2,:]=[255,0,255]
	img[-2:-1,:]=[255,0,255]
	img[:,1:2]=[255,0,255]
	img[:,-2:-1]=[255,0,255]

	fn="/tmp/s_"+str(size)+".png"
	cv2.imwrite(fn,img)
	return fn


def addImageTexture(obj,fn,scale=(1,1)):
	'''fuegt dem Viewobjekt von obj eine Image-Texture aus der Imagefile fn bei, Skalierung mit Faktoren Scale
	'''
	
	rootnode = obj.ViewObject.RootNode
	t1=time.time()
	cl=rootnode.getChildren()

	'''
	print ("childeren",cl.getLength())
	for c in cl:
		print(c)
	'''
	try:
		cl[1].scaleFactor.getValue()
		rootnode.removeChild(1) 
	except:
		print("no texture scaler found")



	try:
		cl[1].filename.getValue()
		rootnode.removeChild(1) 
	except:
		print("no texture image found")

	tex =  coin.SoTexture2()
	tex.filename = str(fn)
	#-----------------
	
	rootnode.insertChild(tex,1)

	# texture 5#20mal wiederholen (zoom auf 50%)
	p=coin.SoTexture2Transform()
	p.scaleFactor = scale # (5.0,20.0)
	rootnode.insertChild(p,1)

	t2=time.time()
	print ("insert node", t2-t1)
	FreeCAD.Console.PrintMessage(str(("insert node", t2-t1)) +"\n")
