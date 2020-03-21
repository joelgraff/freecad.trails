fn='/home/thomas/Dokumente/freecad_buch/D006_landxml/Survey.xml'
fn='/home/thomas/Dokumente/freecad_buch/D006_landxml/bratton farm-2.0.xml'
# fn='/home/thomas/Dokumente/freecad_buch/D006_landxml/test.xml'
fn='/home/thomas/Dokumente/freecad_buch/D006_landxml/Portsmouth Heights.xml'
fn='/home/thomas/Dokumente/freecad_buch/D006_landxml/FreeCAD_Document.xml'

# demo files 
# http://www.landxml.org/webapps/LandXMLSamples.aspx
# http://landxml.org/schema/LandXML-2.0/samples/Carlson Software/corridor from CD3-2.0.xml


import GeoDataWB
import re
from GeoDataWB.say import say
import PySide
from PySide import QtGui
import FreeCADGui as Gui
import FreeCAD

class node():

	def __init__(self,typ):
#		print("erzuegen node,type ",typ)
		self.typ=typ
		self.params={}
		self.content=[]

	def getParam(self,param):
		return self.params[param]

	def getNodes(self,typ):
		ns=[]
		for c in self.content:
			if c.typ==typ:
				ns += [c]
		return ns
	
	def addContent(self,c):
		self.content += [c]

	def __str__(self):
		return self.typ


	def getiterator(self,typ):
		rc=[]
		for obj in self.content:
			if obj.typ==typ:
				rc += [obj]
			rc += obj.getiterator(typ)
		return rc


def parseParams(string):
	params={}
	s=string
	while s!="":
		res = re.search(r"(\S+)=\"([^\"]*)\"\s+(\S.*)", s)
		if res != None:
			assert len(res.groups())==3
			k,v,s=res.group(1),res.group(2),res.group(3)
			params[k]=v
			continue

		res = re.search(r"(\S+)=\"(.*)\"", s)
		if res != None:
			assert len(res.groups())==2
			k,v,s=res.group(1),res.group(2),""
			params[k]=v
			continue

		else:
			raise Exception("parse Params Fehler:"+ s)
			s=""
	return params




def getData(fn,pb=None):
	
	if pb==None:
		pb=QtGui.QProgressBar()
		pb.show()


	stack=[0,0]*4
	stackpointer=-1

	objs=[]

	say("Read data from cache file ...")
	say(fn)
	f=open(fn,"r", encoding="utf8")
	content=f.readlines()

	c2=[]
	cl=len(content)
	
	# FreeCAD File hack
	if content[2].startswith(" FreeCAD Document, see http://www.freecadweb.org"):
		content=content[4:]

	cl=len(content)
	say(cl)

	i=-1
	pb.setMaximum(cl)
	while i<cl-1:
		pb.setValue(i)
		i += 1

		line=content[i].strip()
		j=0
		while re.search(r">\s*$", line) == None and j<60:
			i += 1
			j += 1
			line += content[i] 

		c2 +=[line]
		line=''


	content=c2
	pb.setMaximum(len(content))

	for lc,line in enumerate(content):

		if "<TextureHexString>" in line:
			say ("break A")
			continue

		pb.setValue(lc)

#		if lc%100 == 0:
#			say(lc)
#			Gui.updateGui()

#		if stackpointer != -1:
#			print (res.groups())
#			print (stackpointer)

#		print ("\n-------------NEXT:")
#		print(line)
#		print ("--- PARSE IT------------------------")

		if re.search(r"^\s*$",line):
			continue

		# ein satz
		res = re.search(r"^\s*<(\S+)\s+([^<]*)/>\s*$", line)
		if res != None:
#			print ("complete! ",res.groups())
			assert len(res.groups())==2
			typ=res.group(1)
			obj=node(typ)
			paramstring=res.group(2)
			obj.params=parseParams(paramstring)
			objs += [obj]
			if stackpointer != -1:
				stack[stackpointer].content += [obj]
	#			print stack[stackpointer]
	#			for c in stack[stackpointer].content:
	#				print c,",",
	#			print 
			continue

		res = re.search(r"^\s*<(\S+)\s+([^<]*)>\s*$", line)
		if res != None:
#			print ("!start! ",res.groups())
			assert len(res.groups())==2
			typ=res.group(1)
			obj=node(typ)
			paramstring=res.group(2)
			obj.params=parseParams(paramstring)
			objs += [obj]
			
			if stackpointer != -1:
				stack[stackpointer].content += [obj]
	#			for c in stack[stackpointer].content:
	#				print c,
			stackpointer += 1
			stack[stackpointer]=obj
			continue


		res = re.search(r"^\s*</([^<]*)>\s*$", line)
		if res != None:
#			print ("!ende---------STACKPOINTER down! ",res.groups())
			assert len(res.groups())==1
			stackpointer -= 1
			continue

		res = re.search(r"^\s*<([^<\s]*)>\s*$", line)
		if res != None:
#			print ("!simple start! ",res.groups())
			assert len(res.groups())==1
			typ=res.group(1)
			obj=node(typ)


			if stackpointer != -1:
				stack[stackpointer].content += [obj]


			stackpointer += 1
			stack[stackpointer] = obj

			continue


		#auf und zu
		res = re.search(r"^\s*<(\S+)\s*([^<]*)>(.*)</([^<]+)>\s*$", line)
		if res != None:
#			print ("!alles! ",res.groups())
			assert len(res.groups())==4
			typ=res.group(1)
			obj=node(typ)
			paramstring=res.group(2)
			obj.params=parseParams(paramstring)
			obj.text=res.group(3)
			objs += [obj]
			
			if stackpointer != -1:
				stack[stackpointer].content += [obj]
	#			for c in stack[stackpointer].content:
	#				print c,
	#		stackpointer += 1
	#		stack[stackpointer]=obj


			continue


		raise Exception("unerwartet :" +line +":")
	#	x = re.findall('<([^<]*)>', line)
	#	for xl in x: 
	#		print(xl)

#	say("done getit--------")


	FreeCAD.stackpointer=stackpointer
	FreeCAD.stack=stack
	FreeCAD.objs=objs


	return stack[0]



if 0:
	#----------------------------


	# import landxml

	pb=QtGui.QProgressBar()
	pb.show()
#	progressbar.setValue(0)




	#import geodat.my_xmlparser
	#reload (geodat.my_xmlparser)

	from say import *


	# tree=geodat.my_xmlparser.getData(fn)

	tree=getData(fn)
	# tree=FreeCAD.stack[0]


	say("import done")


	Gui.updateGui()
	Ps={}
	pnodes=tree.getiterator('P')
	pb.setMaximum(len(pnodes))



	for i,element in enumerate(pnodes):
			pb.setValue(i)
	#		say((element.params,element.text))
			_coords=element.text.split(' ')
			Ps[element.params['id']]=FreeCAD.Vector(float(_coords[0]),float(_coords[1]),float(_coords[2]))

	import Points
	ptsa=Ps.values()
	Points.show(Points.Points(ptsa))


	App.activeDocument().recompute()
	Gui.SendMsgToActiveView("ViewFit")
	Gui.updateGui()

	if 0:
		for element in tree.getiterator('PntList3D')[:4]:
				say((element.params,element.text))

		say("Some Faces")
		for element in tree.getiterator('F')[:4]:
				say((element.params,element.text))

		say("BREAKLINES")
		for element in tree.getiterator('Breakline')[:3]:
		#		say((element.typ,element.params))
		#		say(element.content[0].text)
				_coords=element.content[0].text.split(' ')
				coords=np.array([float(a) for a in _coords])
				coords=coords.reshape(len(_coords)/3,3)
				pts=[FreeCAD.Vector(p) for p in coords]
				Part.show(Part.makePolygon(pts))
				App.ActiveDocument.ActiveObject.Label=element.params['desc']
				Gui.updateGui()


		for element in tree.getiterator('Boundary')[:10]:
				say((element.typ,element.params))


		#	say("relations")
		#	for element in tree.getiterator('relation'):
		#		say(element.params)

		1/0


		col=[]
		for element in tree.getiterator('F'):
				say((element.params,element.text))
				ixs=element.text.split(' ')
				ptsf=[Ps[ix] for ix in ixs]
				ptsf += [ptsf[0]]
				col +=[Part.makePolygon(ptsf)]

		Part.show(Part.Compound(col))



	def showFace(rbf,rbf2,x,y,gridsize,shapeColor,bound):

		import Draft
		makeLoft=False
		
		grids=gridsize

		ws=[]

		pts2=[]
		xi, yi = np.linspace(np.min(x), np.max(x), grids), np.linspace(np.min(y), np.max(y), grids)

		for ix in xi:
			points=[]
			for iy in yi:
				iz=float(rbf(ix,iy))

	#---------------------- special hacks #+#
				if bound>0:
					if iz > bound: iz = bound
					if iz < -bound: iz = -bound

				points.append(FreeCAD.Vector(iy,ix,iz))

			if makeLoft:
				w=Draft.makeWire(points,closed=False,face=False,support=None)
				ws.append(w)

			pts2.append(points)


		if makeLoft:
			ll=FreeCAD.activeDocument().addObject('Part::Loft','elevation')
			ll.Sections=ws
			ll.Ruled = True
			ll.ViewObject.ShapeColor = shapeColor
			ll.ViewObject.LineColor = (0.00,0.67,0.00)

			for w in ws:
				w.ViewObject.Visibility=False


			ll.Label="Interpolation Gitter " + str(grids)

		bs=Part.BSplineSurface()
		bs.interpolate(pts2)
		Part.show(bs.toShape())



	import scipy.interpolate



	def interpolate(x,y,z, gridsize,mode='thin_plate',rbfmode=True,shape=None):

		mode=str(mode)
		grids=gridsize


		dx=np.max(x)-np.min(x)
		dy=np.max(y)-np.min(y)

		if dx>dy:
			gridx=grids
			gridy=int(round(dy/dx*grids))
		else:
			gridy=grids
			gridx=int(round(dx/dy*grids))

		if shape != None:
			(gridy,gridx)=shape

		xi, yi = np.linspace(np.min(x), np.max(x), gridx), np.linspace(np.min(y), np.max(y), gridy)
		xi, yi = np.meshgrid(xi, yi)


		if rbfmode:
			rbf = scipy.interpolate.Rbf(x, y, z, function=mode)
			rbf2 = scipy.interpolate.Rbf( y,x, z, function=mode)
		else:
			sayErr("interp2d nicht implementiert")
			x=np.array(x)
			y=np.array(y)
			z=np.array(z)
			xi, yi = np.linspace(np.min(x), np.max(x), gridx), np.linspace(np.min(y), np.max(y), gridy)

			rbf = scipy.interpolate.interp2d(x, y, z, kind=mode)
			rbf2 = scipy.interpolate.interp2d(y, x, z, kind=mode)

		zi=rbf2(yi,xi)
		return [rbf,xi,yi,zi]


	def createsurface(pts,mode='thin_plate',rbfmode=True,gridCount=20,zfactor=1,bound=10**5,matplot=False):

		modeColor={
		'linear' : ( 1.0, 0.3, 0.0),
		'thin_plate' : (0.0, 1.0, 0.0),
		'cubic' : (0.0, 1.0, 1.0),
		'inverse' : (1.0, 1.0, 0.0),
		'multiquadric' : (1.0, .0, 1.0),
		'gaussian' : (1.0, 1.0, 1.0),
		'quintic' :(0.5,1.0, 0.0)
		}


		x=[v[1] for v in pts]
		y=[v[0] for v in pts]
		z=[zfactor*v[2] for v in pts]

		x=np.array(x)
		y=np.array(y)
		z=np.array(z)

		gridsize=gridCount

		rbf,xi,yi,zi1 = interpolate(x,y,z, gridsize,mode,rbfmode)

		# hilfsebene
		xe=[100,-100,100,-100]
		ye=[100,100,-100,-100]
		ze=[20,10,20,5]

		rbf2,xi2,yi2,zi2 = interpolate(xe,ye,ze, gridsize,mode,rbfmode,zi1.shape)
		zi=zi1

		color=(1.0,0.0,0.0)
		showFace(rbf,rbf2,x,y,gridsize,color,bound)
	 
		App.ActiveDocument.ActiveObject.Label=mode + " ZFaktor " + str(zfactor) + " #"
		rc=App.ActiveDocument.ActiveObject

	if 0: 
		createsurface(ptsa,mode='linear')


	if 0:
		pn=ptsa[000:2000]
		Points.show(Points.Points(pn))
		createsurface(pn,mode='linear')
