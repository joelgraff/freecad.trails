'''import data in lan lot elevation format'''

# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- geodat import csv
#--
#-- microelly 2016 v 0.1
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------


from GeoDataWB.say import *

import Points

def setNice(flag=True): 
	''' make smooth skins by setting the MeshDeviation to 0.05'''
	p = FreeCAD.ParamGet("User parameter:BaseApp/Preferences/Mod/Part")
	w=p.GetFloat("MeshDeviation")
	if flag:
		p.SetFloat("MeshDeviation",0.05)
	else:
		p.SetFloat("MeshDeviation",0.5)



'''
datenquelle
http://www.bezreg-koeln.nrw.de/brk_internet/geobasis/hoehenmodelle/gelaendemodelle/index.html
siehe auch 
http://www.bezreg-koeln.nrw.de/brk_internet/geobasis/hoehenmodelle/3d_gebaeudemodelle/index.html

http://www.opengeospatial.org/standards/citygml
https://www.youtube.com/watch?v=U0UBNrAr-j0&feature=youtu.be

http://www.cpa-software.de/index.php?do=zei&lang=d
http://www.businesslocationcenter.de/berlin3d-downloadportal/
http://www.3dcitydb.net/3dcitydb/downloads/

'''




'''
example data
32356000.00 5638000.00   50.48
32356000.00 5638001.00   50.47
32356000.00 5638002.00   50.49
32356000.00 5638003.00   50.47
32356000.00 5638004.00   50.46
32356000.00 5638005.00   50.47
32356000.00 5638006.00   50.46
32356000.00 5638007.00   50.46
32356000.00 5638008.00   50.46
'''

## still hard coded


def getShape(pts):
	'''given a point cloud of a rectangle area get the shape of a appropriate array'''
	dists={}
	ls=[]
	for i,p in enumerate(pts):
		if i>0:
			pa=pts[i-1]
			p1=FreeCAD.Vector(p.x,p.y,0)
			p2=FreeCAD.Vector(pa.x,pa.y,0)
			dist=(p1-p2).Length
			dist=round(dist)
			ls.append(dist)
			try:dists[dist] += 1
			except: dists[dist]=1
	say(dists.keys())
	mm=np.mean(list(dists.keys()))

	tts=[]
	ia=-1
	for i,d in enumerate(ls):
			if d>mm:
				tts.append(i-ia)
				ia=i
	say(tts)
	try:
		dx=int(np.mean(tts))
		dy=len(pts)/dx
		say(("getshape shape: ",dx,dy))
		return dx,dy
	except:
		return (len(pts),1)




## reduce the size of a grid 
# by deleting data columns and rows
# on a regular pattern

def reduceGrid(pts,ku=100,kv=50,lu=0,lv=0):
	''' simplify data '''

	wb, eb, sb, nb = 3, 3, 3, 3
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

#	p=Points.Points(pts2)
#	Points.show(p)
	return pts2


def showFrame(pts,u=0,v=0,d=10,lu=None,lv=None):
	'''showFrame(pts,u=0,v=0,d=10,lu=None,lv=None)
	creates a rectangle frame of size u * v  on a rectangle grid point cloud with shape lu * lv
	if lu or lv is not set, the shape of the point cloud is calculated
	'''

	say(("showframe u v to u+d v+d  in lu,lv",u,v,d,lu,lv))
	if lu == None or lv == None:
		lu,lv=getShape(pts)

	say((lu,lv,u,v,d))
	assert(u+d<lu)
	assert(v+d<lv)

	try:
		ff=FreeCAD.ActiveDocument.frame
	except:
		ff=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","frame")
		ViewProvider(ff.ViewObject)

	iix=[u+v*lu,u+v*lu+d,u+v*lu +d*lu +d,u+v*lu +d*lu]
	a,b,c,d = pts[iix[0]], pts[iix[1]],  pts[iix[2]], pts[iix[3]],

	sha=Part.makePolygon([a,b,c,d,a])

	ff.Shape=sha
	ff.ViewObject.show()

def removeFrame():
	'''remove frame object'''
	App.ActiveDocument.removeObject("frame")



def import_xyz(mode,filename="/tmp/test.xyz",label='',ku=20, kv=10,lu=0,lv=0):
	'''import_xyz(mode,filename="/tmp/test.xyz",label='',ku=20, kv=10,lu=0,lv=0)
	import the point cloud from the file
	'''

	print("Import mode=",mode)
	if mode:

		if lu>0 and lv>0:
			sayErr("read Points001")

		try:
			App.ActiveDocument.nurbs
		except:
			nurbs=App.ActiveDocument.addObject("App::DocumentObjectGroup","nurbs")
		try:
			App.ActiveDocument.grids
		except:
			grids=App.ActiveDocument.addObject("App::DocumentObjectGroup","grids")

		# Get or create "Point_Groups".
		try:
			PointGroups = FreeCAD.ActiveDocument.Point_Groups
		except:
			PointGroups = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroup", 'Point_Groups')
			PointGroups.Label = "Point Groups"

		# Get or create "Points".
		try:
			FreeCAD.ActiveDocument.Points
		except:
			Points = FreeCAD.ActiveDocument.addObject('Points::Feature', "Points")
			PointGroups.addObject(Points)

		objs=App.ActiveDocument.getObjectsByLabel(label)

		if len(objs)!=1:
			sayexc("no point cloud with this label found: >"+label+"<")

		pts=objs[0].Points.Points
		say(("len pts, lu, lv, lu*lv",len(pts),lu,lv,lu*lv))
		assert(len(pts)==lu*lv)
		return pts



	say("iport")
	try:
		App.ActiveDocument.Points
		say("use existing Points")
		return App.ActiveDocument.Points.Points.Points
	except:
		try:
			App.ActiveDocument.nurbs
		except:
			nurbs=App.ActiveDocument.addObject("App::DocumentObjectGroup","nurbs")
		try:
			App.ActiveDocument.grids
		except:
			grids=App.ActiveDocument.addObject("App::DocumentObjectGroup","grids")

		# Get or create "Point_Groups".
		try:
			PointGroups = FreeCAD.ActiveDocument.Point_Groups
		except:
			PointGroups = FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroup", 'Point_Groups')
			PointGroups.Label = "Point Groups"

		# Get or create "Points".
		try:
			FreeCAD.ActiveDocument.Points
		except:
			Points = FreeCAD.ActiveDocument.addObject('Points::Feature', "Points")
			PointGroups.addObject(Points)


		fn=filename
		if fn.startswith('UserAppData'):
			fn=fn.replace('UserAppData',FreeCAD.ConfigGet("UserAppData"))

		f=open(fn)
		lines=f.readlines()
		say("readlines",len(lines))

		'''
		# utm coords 32356000.00 5638000.00
		# height scale factor
		hfac=3
		'''


		pts=[]
		Gui.updateGui()
		for i,l in enumerate(lines):
			p=l.split()
			hfac=3
			try:
				#pts.append(FreeCAD.Vector(float(p[0])-32356000.00,float(p[1])-5638000.00,hfac*float(p[2])))

				pts.append(FreeCAD.Vector(float(p[0]),float(p[1]),hfac*float(p[2])))
			except: 
				sayErr(("error line ",i,p,l))
			if i % 1000 == 0:
				Gui.updateGui()
#			if i >100: break


		if ku>1 and kv>1:
			pts=reduceGrid(pts,ku,kv)

		head, tail = os.path.split(fn)

		PointGroup = FreeCAD.ActiveDocument.addObject('Points::Feature', "Point_Group")
		PointGroup.Label = tail[:-4]
		FreeCAD.ActiveDocument.Point_Groups.addObject(PointGroup)
		PointObject = PointGroup.Points.copy()
		PointObject.addPoints(pts)
		PointGroup.Points = PointObject

		App.ActiveDocument.ActiveObject.ViewObject.hide()
		PointGroup.ViewObject.ShapeColor=(1.0,.0,0.0)
		PointGroup.ViewObject.PointSize=3.0

		FreeCAD.ActiveDocument.recompute()
		Gui.SendMsgToActiveView("ViewFit")

	return pts


sdialog='''
#VerticalLayoutTab:
MainWindow:
	VerticalLayout:
		id:'main'


		QtGui.QLabel:
			setText:"***   I M P O R T    Data from xyz   ***"

		QtGui.QCheckBox:
			id: 'pclMode' 
			setText: 'Use existing Point Cloud'
			stateChanged.connect: app.pclMode
			setChecked: True


	VerticalLayout:
		id:'img1'
		setVisible:False

		QtGui.QPushButton:
			setText: "Browse for input data filename"
			clicked.connect: app.getfn

		QtGui.QLineEdit:
#			setText:"/home/microelly2/FCB/b202_gmx_tracks/dgm1/dgm1_32356_5638_2_nw.xyz"
			setText:"/home/thomas/Dokumente/freecad_buch/b202_gmx_tracks/dgm1/dgm1_32356_5638_2_nw.xyz"
			setText:"UserAppData/Mod/geodat/testdata/xyz.txt"
			id: 'bl'

		HorizontalLayout:
			QtGui.QLabel:
				setText:"Reduction Factor  "

			QtGui.QLineEdit:
				setText:"10"
				setText:"1"
				id: 'ku'

			QtGui.QLineEdit:
				setText:"10"
				setText:"1"
				id: 'kv'


	VerticalLayout:
		id:'img2'

		QtGui.QLabel:
			setText:"Point Cloud Name"

		QtGui.QLineEdit:
			setText:"Points 110 99"
			setText:"Points"
			id: 'pclLabel'


		HorizontalLayout:
			QtGui.QLabel:
				setText:"Size lu,lv  "

		QtGui.QLineEdit:
			setText:"3"
			#setText:"110"
			id: 'lu'

		QtGui.QLineEdit:
			setText:"3"
			#setText:"99"
			id: 'lv'


	QtGui.QPushButton:
		setText: "initialize values"
		id:'run'
		clicked.connect: app.run



	VerticalLayout:
		id:'post'
		setVisible: False

		QtGui.QLabel:
			setText:"Create Nurbs Surfaces inside a Rectangle"

		HorizontalLayout:

			QtGui.QLabel:
				setText:"Frame position"

			QtGui.QDial:
				setValue: 0
				id: 'ud'
				setMinimum: 0
				setMaximum: 200
				setTickInterval: 1
				valueChanged.connect: app.showFrame


			QtGui.QDial:
				setValue: 0
				id: 'vd'
				setMinimum: 0
				setMaximum: 200
				setTickInterval: 1
				valueChanged.connect: app.showFrame
				valueChanged.connect: app.update2

		HorizontalLayout:

			QtGui.QLabel:
				setText:"Frame size"
				valueChanged.connect: app.showFrame
#				valueChanged.connect: app.update2

			QtGui.QDial:
				setValue: 5
				id: 'dd'
				setMinimum: 1
				setMaximum: 100
				setTickInterval: 1
				valueChanged.connect: app.update2
#				valueChanged.connect: app.showFrame

		HorizontalLayout:
			QtGui.QPushButton:
				setText: "hide Frame"
				clicked.connect: app.hideFrame

			QtGui.QPushButton:
				setText: "create Nurbs"
				clicked.connect: app.createNurbs

			QtGui.QPushButton:
				setText: "create Mesh"
				clicked.connect: app.createMesh


'''




## Gui backend

class MyApp(object):
	'''execution layer of the dialog'''

	def pclMode(self):
		'''toogle the mode point cloud from file/point cloud from document'''
		try:
			if self.root.ids['pclMode'].isChecked():
				self.root.ids['img1'].hide()
				self.root.ids['img2'].show()
			else:
				self.root.ids['img1'].show()
				self.root.ids['img2'].hide()
		except:
			pass

	def update(self):
		'''update dialog values'''
#		lu,lv = getShape(self.pts)
		say("update")
		lu=int(self.root.ids['lu'].text())
		lv=float(self.root.ids['lv'].text())
		say("dd,ud,vd",self.root.ids['dd'].value(),self.root.ids['ud'].value(),self.root.ids['vd'].value())

		dmax = min(lu - self.root.ids['ud'].value(), lv - self.root.ids['vd'].value(),101) -1
		self.root.ids['dd'].setMaximum(dmax)
		if self.root.ids['dd'].value() >dmax:
			self.root.ids['dd'].setValue(dmax)
		say("dd,ud,vd",self.root.ids['dd'].value(),self.root.ids['ud'].value(),self.root.ids['vd'].value())
		self.root.ids['vd'].setMaximum(lv-self.root.ids['dd'].value()-1)
		self.root.ids['ud'].setMaximum(lu-self.root.ids['dd'].value()-1)

	def update2(self):
		'''update dialog values and frame'''
		self.update()
		self.showFrame()

	## read the data from file, create a point clound  
	# calculate the shape of an expected rectangle point cloud layout

	def run(self):
		'''load the data'''
		filename=self.root.ids['bl'].text()
		#filename='/home/microelly2/FCB/b202_gmx_tracks/dgm1/dgm1_32356_5638_2_nw.xyz'
		try:
			ts=time.time()
			#\cond
			self.pts=import_xyz(
					self.root.ids['pclMode'].isChecked(),
					filename,
					self.root.ids['pclLabel'].text(),
					int(self.root.ids['ku'].text()),
					int(self.root.ids['kv'].text()),
					int(self.root.ids['lu'].text()),
					int(self.root.ids['lv'].text()),
			)
			#\endcond
			te=time.time()
			say("load points time " + str(round(te-ts,2)))
			say(("points",len(self.pts)))
			lu,lv=getShape(self.pts)
			self.root.ids['lu'].setText(str(lu))
			self.root.ids['lv'].setText(str(lv))

			self.update()
			self.root.ids['post'].show()
			self.root.ids['run'].hide()
			self.root.ids['main'].hide()
			self.root.ids['img1'].hide()
			self.root.ids['img2'].hide()
		except:
				sayexc()





	def getfn(self):
		''' get the filename dialog'''
		ddir=u"/tmp/"
		ddir="/media/thomas/b08575a9-0252-47ca-971e-f94c20b33801/geodat_DATEN/xyz_lee_county"
		fileName = QtGui.QFileDialog.getOpenFileName(None,u"Open File",ddir);
		s=self.root.ids['bl']
		s.setText(fileName[0])

	def hideFrame(self):
		'''remove the frame from model '''
		removeFrame()

	def showFrame(self):
		'''create and display the frame'''
		u=self.root.ids['ud'].value()
		v=self.root.ids['vd'].value()
		d=self.root.ids['dd'].value()
		lu=int(self.root.ids['lu'].text())
		lv=float(self.root.ids['lv'].text())

		showFrame(self.pts,u,v,d,lu,lv)


	def createNurbs(self):
		'''create nurbs surface for selected frame'''
		u=self.root.ids['ud'].value()
		v=self.root.ids['vd'].value()
		d=self.root.ids['dd'].value()
#		lu,lv = getShape(self.pts)
		lu=int(self.root.ids['lu'].text())
		lv=float(self.root.ids['lv'].text())

		say(("create nurbs for subset",u,v,d,lu,lv))
		suv(self,u,v,d,lu,lv)


	def createMesh(self):
		sayW("NOT IMPLEMENTED")
		u=self.root.ids['ud'].value()
		v=self.root.ids['vd'].value()
		d=self.root.ids['dd'].value()
#		lu,lv = getShape(self.pts)
		lu=int(self.root.ids['lu'].text())
		lv=float(self.root.ids['lv'].text())

		muv(self,u,v,d+1,lu,lv)



def mydialog(run=True):
	'''the gui startup'''

	import GeoDataWB.miki as miki

	app=MyApp()

	miki=miki.Miki()
	miki.app=app
	app.root=miki

	miki.parse2(sdialog)
	miki.run(sdialog)
	return miki



'''
# test scheibe und lesen np array file
def run(app):

	#from tempfile import TemporaryFile
	#outfile = TemporaryFile()

	fn="/tmp/npexport"
	outfile=open(fn,"w")
	x = np.array(app.pts).reshape(200,200,3)
	np.save(outfile, x)
	outfile.close()

	outfile=open(fn)
	t=np.load(outfile)
	say(t.shape)
	return t
'''


## create a grid of BSplineSurface bs with ct lines and rows
#


def create_grid(pu,du,dv, wb, eb, sb, nb, color=(1.0,0.0,0.0)):
	'''create_grid(pu,du,dv, wb, eb, sb, nb, color=(1.0,0.0,0.0)'''

	ts=time.time()
	sss=[]

	# u direction curves
	for iu in range(sb,dv-nb):
		pps=[]
		for iv in range(wb,du-eb):
			pps.append(pu[iu*du+iv])
		tt=Part.BSplineCurve()
		tt.interpolate(pps)
		ss=tt.toShape()
		sss.append(ss)

	# v direction curves
	for iv in range(wb,du-eb):
		pps=[]
		for iu in range(sb,dv-nb):
			pps.append(pu[iu*du+iv])
		tt=Part.BSplineCurve()
		tt.interpolate(pps)
		ss=tt.toShape()
		sss.append(ss)

	comp=Part.Compound(sss)

	Part.show(comp)
	App.ActiveDocument.ActiveObject.ViewObject.LineColor=color
	App.ActiveDocument.grids.addObject(App.ActiveDocument.ActiveObject)
	te=time.time()
	say(["create grid time ",round(te-ts,5) ])
	return App.ActiveDocument.ActiveObject



def create_mgrid(pu,du,dv, wb, eb, sb, nb, color=(1.0,0.0,0.0)):
	'''create_grid(pu,du,dv, wb, eb, sb, nb, color=(1.0,0.0,0.0)'''

	ts=time.time()
	sss=[]

	# mesh generieren #+#
	#alles 0,0 bis 2000, 2000

	# u direction curves
	for iu in range(sb,dv-nb):
		pps=[]
		for iv in range(wb,du-eb):
			pps.append(pu[iu*du+iv])
		ss=Part.makePolygon(pps)
		sss.append(ss)

	# v direction curves
	for iv in range(wb,du-eb):
		pps=[]
		for iu in range(sb,dv-nb):
			pps.append(pu[iu*du+iv])
		ss=Part.makePolygon(pps)
		sss.append(ss)

	comp=Part.Compound(sss)

	Part.show(comp)
	App.ActiveDocument.ActiveObject.ViewObject.LineColor=color
	App.ActiveDocument.grids.addObject(App.ActiveDocument.ActiveObject)
	te=time.time()
	say(["create grid time ",round(te-ts,5) ])
	return App.ActiveDocument.ActiveObject


## create a point cloud
#

def create_pcl(pu,color=(1.0,0.0,0.0)):
	'''create_pcl(pu,color=(1.0,0.0,0.0))'''

	say(len(pu))
	p=Points.Points(pu)
	Points.show(p)
	App.ActiveDocument.ActiveObject.ViewObject.ShapeColor=color
	App.ActiveDocument.ActiveObject.ViewObject.PointSize=3
	try:
		App.ActiveDocument.points
	except:
		points=App.ActiveDocument.addObject("App::DocumentObjectGroup","points")

	App.ActiveDocument.points.addObject(App.ActiveDocument.ActiveObject)
	Gui.updateGui()

#\cond
class ViewProvider:
	def __init__(self, obj):
		obj.Proxy = self
		self.Object=obj
#\endcond

def muv(app,u=3,v=5,d=10,la=100,lb=100):
	'''generate a quadratic mesh on startposition u,v with size d)'''
	st=time.time()
	tt=Part.BSplineSurface()
	wb, eb, sb, nb = 0, 0, 0, 0
	if u>=2: wb=2
	if u<la-2-d: eb=2
	if v>=2: sb=2
	if v<la-2-d: nb=2
	uu=[]
	du=d+wb+eb+1
	dv=d+nb+sb+1
	u=u-wb
	v=v-sb
	pu=[]
	say([ "(wb,eb,sb,nb,du,dv)", (wb,eb,sb,nb,du,dv)])
	try: pts=app.pts
	except: pts=app

	for k in range(dv):
		pu += pts[u+v*la+la*k:u+v*la+du+la*k]
		uu.append(pts[u+v*la+la*k:u+v*la+du+la*k])

	color=(1-0.5*random.random(),1-0.5*random.random(),1-0.5*random.random())

	App.ActiveDocument.ActiveObject.ViewObject.hide()


	App.ActiveDocument.ActiveObject.ViewObject.hide()

	#create bspline grid
	create_mgrid(pu,du,dv, wb, eb, sb, nb, color)
	Gui.updateGui()
	



def suv(app,u=3,v=5,d=10,la=100,lb=100):
	'''generate a quadratic bspline surface on startposition u,v with size d)'''

	st=time.time()
	tt=Part.BSplineSurface()
	wb, eb, sb, nb = 0, 0, 0, 0
	if u>=2: wb=2
	if u<la-2-d: eb=2
	if v>=2: sb=2
	if v<la-2-d: nb=2
	uu=[]
	du=d+wb+eb+1
	dv=d+nb+sb+1
	u=u-wb
	v=v-sb
	pu=[]
	say([ "(wb,eb,sb,nb,du,dv)", (wb,eb,sb,nb,du,dv)])
	say('u,v',u,v)
	try: pts=app.pts
	except: pts=app
	for k in range(dv):
		pu += pts[u+v*la+la*k:u+v*la+du+la*k]
		uu.append(pts[u+v*la+la*k:u+v*la+du+la*k])
		
		say(k,u+v*la+la*k,u+v*la+du+la*k)
	
	say("uu")
	say(uu)


	color=(1-0.5*random.random(),1-0.5*random.random(),1-0.5*random.random())

	App.ActiveDocument.ActiveObject.ViewObject.hide()

	# create point cloud
	create_pcl(pu,color)
	Gui.updateGui()

	App.ActiveDocument.ActiveObject.ViewObject.hide()

	#create bspline grid
	create_grid(pu,du,dv, wb, eb, sb, nb, color)
	Gui.updateGui()

	tt.interpolate(uu)
	uk=tt.getUKnots()
	vk=tt.getVKnots()
	tt.segment(uk[sb],uk[-1-nb],vk[wb],vk[-1-eb])
	sha=tt.toShape()
	se=time.time()
	say(["running time for one shape ", round(se-st,5)])
	App.ActiveDocument.ActiveObject.ViewObject.hide()

	a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","mynurbs")
	ViewProvider(a.ViewObject)
	a.Shape=sha
	se=time.time()
	say([ "running time for show the shape ", round(se-st,5)])
	App.ActiveDocument.ActiveObject.ViewObject.ShapeColor=color
	App.ActiveDocument.nurbs.addObject(App.ActiveDocument.ActiveObject)
	Gui.ActiveDocument.update()

	# return the BSpline geometry
	return tt



def suv2(label,pts,u=3,v=5,d=10,la=100,lb=100):

	try:
		App.ActiveDocument.nurbs
	except:
		nurbs=App.ActiveDocument.addObject("App::DocumentObjectGroup","nurbs")
	try:
		App.ActiveDocument.grids
	except:
		grids=App.ActiveDocument.addObject("App::DocumentObjectGroup","grids")
	try:
		App.ActiveDocument.points
	except:
		points=nurbs=App.ActiveDocument.addObject("App::DocumentObjectGroup","points")


	st=time.time()
	tt=Part.BSplineSurface()
	wb, eb, sb, nb = 0, 0, 0, 0
	if u>=2: wb=2
	if u<la-2-d: eb=2
	if v>=2: sb=2
	if v<la-2-d: nb=2
	uu=[]
	du=d+wb+eb
	dv=d+nb+sb
	u=u-wb
	v=v-sb
	pu=[]
	say([ "(wb,eb,sb,nb,du,dv)", (wb,eb,sb,nb,du,dv)])
	for k in range(dv):
		pu.append(pts[u+v*la+la*k:u+v*la+du+la*k])
		uu.append(pts[u+v*la+la*k:u+v*la+du+la*k])

	color=(1-0.5*random.random(),1-0.5*random.random(),1-0.5*random.random())

	try:
		App.ActiveDocument.ActiveObject.ViewObject.hide()
	except: pass

	# create point cloud
	create_pcl(pu,color)
	Gui.updateGui()
	try:
		App.ActiveDocument.ActiveObject.ViewObject.hide()
	except:
		pass

	#create bspline grid
	create_grid(pu,du,dv, wb, eb, sb, nb, color)
	Gui.updateGui()

	tt.interpolate(uu)
	uk=tt.getUKnots()
	vk=tt.getVKnots()
	tt.segment(uk[sb],uk[-1-nb],vk[wb],vk[-1-eb])
	sha=tt.toShape()
	se=time.time()
	say(["running time for one shape ", round(se-st,5)])

	# alternative
	# Part.show(sha)

	App.ActiveDocument.ActiveObject.ViewObject.hide()

	a=FreeCAD.ActiveDocument.addObject("Part::FeaturePython","QuadNurbs")
	a.Label=label
	ViewProvider(a.ViewObject)
	a.Shape=sha


	se=time.time()
	say([ "running time for show the shape ", round(se-st,5)])

	App.ActiveDocument.ActiveObject.ViewObject.ShapeColor=color
	App.ActiveDocument.nurbs.addObject(App.ActiveDocument.ActiveObject)

	# return tt
	return a



# generate 100 quads with each 100 interpolation points

'''
st=time.time()
for vx in range(10):
	for ux in range(10):
		tt=suv(2+9*ux,2+18*vx)

se=time.time()

print("running time for 100 quads")
print(round(se-st,1))
'''

'''
# range 22,10
st=time.time()
for vx in range(22):
	for ux in range(11):
		tt=suv(0+9*ux,0+9*vx)

se=time.time()
print("running time all")
print(round(se-st,1))
'''

'''
Kreuz Koeln Sued
50.8869691,6.9658102


32356_5638

'''


'''
suv(140,40,20,2000,2000)

#mitte kreuzung
suv(1000,1000,80,2000,2000)

#abfahrt
suv(1100,920,50,2000,2000)

# unten
suv(800,40,50,2000,2000)

# see
suv(300,500,60,2000,2000)
'''

'''
# lasttest
for i in range(10,110,10):
	say("\n")
	say(i)
	suv(1000,1000,i,2000,2000)
'''



## test start and hide the dialog
def runtest():
	m=mydialog()
	m.objects[0].hide()


if __name__ == '__main__':
	runtest()

def importXYZ():
	mydialog()
