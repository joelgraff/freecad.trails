# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- geodat import lidar
#--
#-- microelly 2018 v 0.1
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------


from GeoDataWB.say import *

import Points

import sys
if sys.version_info[0] !=2:
	from importlib import reload


import time
from laspy.file import File
import numpy as np
import Mesh
import random


def import_lidar(fn,obj,createPCL=False,useOrigin=False):

	inFile = File(fn, mode='r')

	I = inFile.Classification == 2

#	I=0
#	FreeCAD.infile=inFile

	pts=inFile.points[I]

	if 10:

		scalez=0.001
		scalez=1.
		ptsa=[(p[0][0],p[0][1],p[0][2]*scalez) for p in pts]

	if 1:
		import Points
		p=Points.Points(ptsa)
		Points.show(p)


	print(pts[0])


	ptsb=np.array(ptsa)
	ptsbxyz=ptsb.swapaxes(0,1)
	
	obj.placementOrigin.Base.x=ptsbxyz[0].min()/1000.
	obj.placementOrigin.Base.y=ptsbxyz[1].min()/1000.
	obj.placementOrigin.Base.z=ptsbxyz[2].min()/1000.

	print (ptsbxyz[0].min(),ptsbxyz[0].max())

	x=ptsbxyz[0]-ptsbxyz[0].min()
	x= x/1000.0

	y=ptsbxyz[1]-ptsbxyz[1].min()
	y= y/1000.0

	z=ptsbxyz[2]-ptsbxyz[2].min()
	z= z/1000.0

	ptscxyz=np.array([x,y,z])

	ptsc=ptscxyz.swapaxes(0,1)
	ptsc=[FreeCAD.Vector(p) for p in ptsc]

	if createPCL:
		p=Points.Points(ptsc)
		Points.show(p)
		am=App.ActiveDocument.ActiveObject
		if useOrigin:
			am.Placement=obj.placementOrigin
		else:
			am.Placement=FreeCAD.Placement()

	obj.xdim=int(round(x.max()))+1
	obj.ydim=int(round(x.max()))+1
	nar=np.zeros(obj.xdim*obj.ydim).reshape(obj.xdim,obj.ydim)

	for p in ptsc:
		xi=int(round(p.x))
		yi=int(round(p.y))
		nar[xi,yi] += p.z

	ptsd=[]
	ptse=[]
	for ix in range(obj.xdim):
			for iy in range(obj.ydim):
				if nar[ix,iy] != 0:
					ptsd += [FreeCAD.Vector(ix,iy,nar[ix,iy])]
				else:
					ptse += [FreeCAD.Vector(ix,iy,0)]

	if 0:
		p=Points.Points(ptsd)
		Points.show(p)
		App.ActiveDocument.ActiveObject.ViewObject.hide()
		App.ActiveDocument.ActiveObject.ViewObject.ShapeColor=(0.,1.0,0.)


	if 0:
		p=Points.Points(ptse)
		Points.show(p)
		App.ActiveDocument.ActiveObject.ViewObject.ShapeColor=(1.,0.0,0)

	obj.nar=list(nar.reshape(obj.xdim*obj.ydim))
	return nar


def createFace(obj):

	nar=np.array(obj.nar).reshape(obj.xdim,obj.ydim)
	a=obj.uPos
	c=obj.vPos
	b=obj.uSize
	d=obj.vSize
	d += 1
	b += 1

	ptsd=[]
	ptse=[]
	for ix in range(a,a+b):
			for iy in range(c,c+d):
				if nar[ix,iy] != 0:
					ptsd += [FreeCAD.Vector(ix,iy,nar[ix,iy])]
				else:
					ptse += [FreeCAD.Vector(ix,iy,0)]

	if obj.createPoints:
		p=Points.Points(ptsd)
		Points.show(p)
		am=App.ActiveDocument.ActiveObject
		App.ActiveDocument.ActiveObject.ViewObject.ShapeColor=(0.,1.0,1.)
		App.ActiveDocument.ActiveObject.Label="lidar points"
		if obj.useOrigin:
			am.Placement=obj.placementOrigin
		else:
			am.Placement=FreeCAD.Placement()

	dat=np.array(ptsd)
	import scipy
	import scipy.interpolate 
	modeB="cubic"

	xy2h = scipy.interpolate.Rbf(dat[:,0],dat[:,1],dat[:,2], function=modeB)

	ptsda=[]

	for ix in range(a,a+b):
			for iy in range(c,c+d):
					ptsda += [FreeCAD.Vector(ix,iy,xy2h(ix,iy))]

	if obj.createPoints:
		p=Points.Points(ptsda)
		Points.show(p)
		am=App.ActiveDocument.ActiveObject
		App.ActiveDocument.ActiveObject.ViewObject.ShapeColor=(0.,1.0,0.)
		App.ActiveDocument.ActiveObject.Label="interpolated points"
		if obj.useOrigin:
			am.Placement=obj.placementOrigin
		else:
			am.Placement=FreeCAD.Placement()


	ptsdarr=np.array(ptsda).reshape(b,d,3)
	ta=time.time()
	if obj.createNurbs:
		bs=Part.BSplineSurface()
		bs.interpolate(ptsdarr)

		fn="face_"+str(a)+"_"+str(b)+"_"+str(c)+'_'+str(d)
		obja=App.ActiveDocument.getObject(fn)
		if obja == None:
			obja = FreeCAD.ActiveDocument.addObject("Part::Feature",fn)
			obja.ViewObject.ShapeColor=(random.random(),random.random(),random.random())
			obja.ViewObject.hide()


		obja.Shape=bs.toShape()
		obj.Shape=bs.toShape()
		if obj.useOrigin:
			obja.Placement=obj.placementOrigin
		else:
			obja.Placement=FreeCAD.Placement()



	Gui.updateGui()
	tb=time.time()


	# def toUVMesh(ptsda,b=50):
	if obj.createMesh:
		topfaces=[]
		for x in range(b-1):
			for y in range(d-1): 
				topfaces.append((d*x+y,(d)*x+y+1,(d)*(x+1)+y))
				topfaces.append(((d)*x+y+1,(d)*(x+1)+y,(d)*(x+1)+y+1))

		t=Mesh.Mesh((ptsda,topfaces))
		#Mesh.show(t)
		fn="mesh_"+str(a)+"_"+str(b)+"_"+str(c)+'_'+str(d)

		if obj.meshName=="":
			obj.meshName="LidarMesh"
		fn=obj.meshName
		mm=App.ActiveDocument.getObject(fn)
		if mm == None:
			mm = FreeCAD.ActiveDocument.addObject("Mesh::FeaturePython",fn)
			mm.ViewObject.ShapeColor=(random.random(),random.random(),random.random())

		mm.Mesh=t
		ViewProvider(mm.ViewObject)
		mm.ViewObject.Lighting="Two side"
		mm.ViewObject.ShapeColor=obj.ViewObject.ShapeColor

		if obj.useOrigin:
			mm.Placement=obj.placementOrigin
		else:
			mm.Placement=FreeCAD.Placement()


	tc=time.time()
	print("nurbs ",tb-ta)
	print("mesh ",tc-tb)


#-----------------------------------



class LIDAR:

	def __init__(self, obj):
		obj.Proxy = self
		self.Object = obj

	def attach(self, vobj):
		self.Object = vobj.Object

	def __getstate__(self):
		return None

	def __setstate__(self, state):
		return None

	def execute(self,obj):
		try: _=obj.nar[0]
		except: return
		bsa=createFace(obj)
		#bsb=createFace(nar,a=620,c=620,b=70)
		#bsc=createFace(nar,a=620,c=690,b=70)
		pass

#	def attach(self,vobj):
#		self.Object = vobj.Object

	def onChanged(self,obj,prop):
		print("prop ",prop)
		if prop=='anim':
			runAnimation(obj)
		if prop=='useOrigin':
			if obj.useOrigin:
				obj.Placement=obj.placementOrigin
			else:
				obj.Placement=FreeCAD.Placement

	def step(self,now):
		self.Object.anim=int(round(now))

	def initialize(self):
		pass

	def onDocumentRestored(self, fp):
		self.Object=fp


class ViewProvider:
	''' basic defs '''

	def __init__(self, obj):
		obj.Proxy = self
		self.Object = obj

	def __getstate__(self):
		return None

	def __setstate__(self, state):
		return None

	def getIcon(self):
		__dir__ = os.path.dirname(__file__)	
		return  __dir__+ '/icons/abroller.png'

#-------------------------------







def createLIDAR():

	obj = FreeCAD.ActiveDocument.addObject("Part::FeaturePython","MyLidar")
	obj.addProperty("App::PropertyLink", "pcl", "_aux", "Point Cloud")
#	obj.addProperty("App::PropertyLink", "ipcl", "_aux", "interpolated Point Cloud")

	obj.addProperty("App::PropertyInteger", "uPos", "_aux", "start Area").uPos=0
	obj.addProperty("App::PropertyInteger", "vPos", "_aux", "start Area").vPos=0
	obj.addProperty("App::PropertyInteger", "uSize", "_aux", "size Area").uSize=40
	obj.addProperty("App::PropertyInteger", "vSize", "_aux", "size Area").vSize=40
	obj.addProperty("App::PropertyFloatList", "nar", "_aux", "elevation array")

	obj.addProperty("App::PropertyBool", "createMesh", "_aux", "create a Mesh")
	obj.addProperty("App::PropertyBool", "createNurbs", "_aux", "create a Mesh")
	obj.addProperty("App::PropertyBool", "createPoints", "_aux", "create a Mesh")
	obj.addProperty("App::PropertyString", "meshName", "_aux", "Mesh").meshName="MyMesh"

	obj.addProperty("App::PropertyInteger", "xdim")
	obj.addProperty("App::PropertyInteger", "ydim")
	obj.addProperty("App::PropertyPlacement", "placementOrigin","location of the data")
	obj.addProperty("App::PropertyBool", "useOrigin", "location of the data", "place dat")


	LIDAR(obj)
	obj.Shape=Part.Shape()

	ViewProvider(obj.ViewObject)
	for prop in ["nar"]:
		obj.setEditorMode(prop, 2) 

	App.activeDocument().recompute()
	Gui.SendMsgToActiveView("ViewFit")
	return obj







#--------------



sdialog='''
MainWindow:
	VerticalLayout:
		id:'main'


		QtGui.QLabel:
			setText:"***   I M P O R T    L I D A R   ***"

		QtGui.QCheckBox:
			id: 'createPCL' 
			setText: 'create Point Cloud'
#			stateChanged.connect: app.pclMode
			setChecked: True

		QtGui.QCheckBox:
			id: 'useOrigin' 
			setText: 'use Origin of Data'
#			stateChanged.connect: app.pclMode
#			setChecked: True

		QtGui.QPushButton:
			setText: "Browse for input data filename."
			clicked.connect: app.getfn

		QtGui.QLineEdit:
			setText:"/media/thomas/b08575a9-0252-47ca-971e-f94c20b33801/geodat_DATEN/las_lee_county/24561900.las"
			id: 'bl'

	QtGui.QPushButton:
		setText: "initialize values"
		id:'run'
		clicked.connect: app.run

'''




## Gui backend

class MyApp(object):
	'''execution layer of the dialog'''


	def update(self):
		'''update dialog values'''
#		lu,lv = getShape(self.pts)
		lu=int(self.root.ids['lu'].text())
		lv=int(self.root.ids['lv'].text())

		dmax = min(lu - self.root.ids['ud'].value(), lv - self.root.ids['vd'].value(),101) -1
		self.root.ids['dd'].setMaximum(dmax)
		if self.root.ids['dd'].value() >dmax:
			self.root.ids['dd'].setValue(dmax)
		self.root.ids['vd'].setMaximum(lv-self.root.ids['dd'].value())
		self.root.ids['ud'].setMaximum(lu-self.root.ids['dd'].value())


	def run(self):
		'''load the data'''
		fn=self.root.ids['bl'].text()
		try:
			obj=createLIDAR()
			nar=import_lidar(fn,obj,self.root.ids['createPCL'].isChecked(),self.root.ids['useOrigin'].isChecked())


#			for bs in [bsa,bsb,bsc]:
#				sh=bsc.toShape()
#				psh=sh.makeParallelProjection(App.ActiveDocument.BSpline.Shape,FreeCAD.Vector(0,0,1))
#				Part.show(psh)

		except:
				sayexc()


	def getfn(self):
		''' get the filename dialog'''
		ddir=u"/tmp/"
		ddir="/media/thomas/b08575a9-0252-47ca-971e-f94c20b33801/geodat_DATEN/las_lee_county"
		fileName = QtGui.QFileDialog.getOpenFileName(None,u"Open File",ddir);
		print(fileName)
		s=self.root.ids['bl']
		s.setText(fileName[0])



def mydialog(run=True):
	'''the gui startup'''

	import GeoDataWB.miki as miki
	reload(miki)

	app=MyApp()

	miki=miki.Miki()
	miki.app=app
	app.root=miki

	miki.parse2(sdialog)
	miki.run(sdialog)
	return miki


def importLIDAR():
	mydialog()
