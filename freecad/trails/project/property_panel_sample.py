"""gui control panel for parametes of different objects"""

# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- a basic param controller gui
#--
#-- microelly 2017 v 0.1
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------

#\cond
import FreeCAD,FreeCADGui
App=FreeCAD
Gui=FreeCADGui

import PySide
from PySide import  QtGui,QtCore
#\endcond

def createListWidget(obj=None,propname=None):
	"""list Widget for PropertyLinkList, the  Labels are displayed"""

	w=QtGui.QWidget()
	box = QtGui.QVBoxLayout()
	w.setLayout(box)

	listWidget = QtGui.QListWidget() 
	listWidget.setSelectionMode(QtGui.QAbstractItemView.MultiSelection)
	listWidget.sels=[]
	ks={}
	liste=obj.getPropertyByName(propname)
	for l in liste:
		ks[l.Label]=l

	for  k in ks.keys():
		item = QtGui.QListWidgetItem(k)
		listWidget.addItem(item)
		
	def f(*arg):
		print("itemsele cahgned")
		print(arg,listWidget)
		print(listWidget.selectedItems())
		for item in  listWidget.selectedItems():
			print(ks[item.text()])

		listWidget.sels= [ ks[item.text()] for item in  listWidget.selectedItems()]

	listWidget.itemSelectionChanged.connect(f)
	box.addWidget(listWidget)

	def remove():
		"""method to remove selected item form list"""

		ref=obj.getPropertyByName(propname+"Source")

		# remove selected items
		aa=ref.getPropertyByName(propname)
		bb=[]
		for a in aa:
			if not a in listWidget.sels:
				bb.append(a)
			else:
				print("skip ", a.Label)

		# wrte list back to objects
		setattr(ref,propname,bb)
		setattr(obj,propname,bb)

		#refresh dialog
		obj.Proxy.dialog.hide()
		obj.Proxy.dialog=dialog(obj)

		App.activeDocument().recompute()



	def add():
		"""add gui selected objects to list"""

		sels=Gui.Selection.getSelection()
		ref=obj.getPropertyByName(propname+"Source")
		aa=ref.getPropertyByName(propname)

		# add selected objects if not aready on list
		for s in sels:
			if s not in aa:
				print(a.Label +"not in aa")
				aa.append(s)

		#write list back to objects
		setattr(ref,propname,aa)
		setattr(obj,propname,aa)

		#refresh dialog
		obj.Proxy.dialog.hide()
		obj.Proxy.dialog=dialog(obj)

		App.activeDocument().recompute()


	w.r=QtGui.QPushButton("remove selected items")
	box.addWidget(w.r)
	w.r.pressed.connect(remove)

	w.r=QtGui.QPushButton("add Gui selection")
	box.addWidget(w.r)
	w.r.pressed.connect(add)

	return w





def clear(window):
	""" delet the window widget """
	#window.deleteLater()
	# App.ActiveDocument.Spreadsheet.ViewObject.update()
	App.activeDocument().recompute()


def hu():
	mw=FreeCADGui.getMainWindow()
	mdiarea=mw.findChild(QtGui.QMdiArea)

	label="Spreadsheet"
	sws=mdiarea.subWindowList()
	print("windows ...")
	for w2 in sws:
		print(str(w2.windowTitle()))
		if str(w2.windowTitle()).startswith(label):
			sw=w2
			bl=w2.children()[3]
			blcc=bl.children()[2].children()

			w=QtGui.QWidget()
			w.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

			box = QtGui.QVBoxLayout()
			w.setLayout(box)
			ss=blcc[3]
			box.addWidget(ss)
			# ss.setParent(w)
			w.setGeometry(50, 30, 1650, 350)
			w.show()
			sw.close()
			FreeCAD.ss=w
			return w

	FreeCAD.ss.hide()
	FreeCAD.ss.show()


## create a Controler Widget for a property
 

def createPropWidget(obj,propname):
	"""create and retur widget fpr obj.propname"""

	w=QtGui.QWidget()

	box = QtGui.QVBoxLayout()
	box.setAlignment(QtCore.Qt.AlignTop)
	w.setLayout(box)

	ref=obj.getPropertyByName(propname+"Source")
	w.l=QtGui.QLabel(ref.Label+'.'+propname )
	box.addWidget(w.l)

	pt=obj.getTypeIdOfProperty(propname)
	print ("create widget for property ",propname,pt)

	# case LinkList
	if pt=='App::PropertyLinkList':
		w.d=createListWidget(obj,propname)
		box.addWidget(w.d)
		return w

	cellmode=False

	try: 
		obj.getPropertyByName(propname+"Typ")
		cellmode=True
	except:
		pass


	# case float properties
	if obj.getPropertyByName(propname+"Slider"):
		w.d=QtGui.QSlider()
		w.d.setOrientation(QtCore.Qt.Horizontal)
		w.d.setTickPosition(QtGui.QSlider.TicksBelow)
	else:
		w.d=QtGui.QDial()
		w.d.setNotchesVisible(True)

	if cellmode:
		w.d.setMinimum(obj.getPropertyByName(propname+"Min"))
		w.d.setMaximum(obj.getPropertyByName(propname+"Max"))
		w.d.setValue(obj.getPropertyByName(propname))
		#w.d.setValue(obj.getPropertyByName(propname).Value)

	else:
		w.d.setMinimum(obj.getPropertyByName(propname+"Min").Value)
		w.d.setMaximum(obj.getPropertyByName(propname+"Max").Value)
		w.d.setValue(obj.getPropertyByName(propname).Value)

	w.d.setSingleStep(obj.getPropertyByName(propname+"Step"))

	def valueChangedA(val):
		"""update obj and ref with new value""" 
		print("update ----------")
		
		ref=obj.getPropertyByName(propname+"Source")
		print (ref.Label,propname,val)
		if ref.__class__.__name__ == 'Sheet':
			ref.set(propname, str(val))
		else:
			setattr(ref,propname,val)
		setattr(obj,propname,val)
		App.activeDocument().recompute()
		Gui.updateGui()

	w.d.valueChanged.connect(valueChangedA)
	box.addWidget(w.d)

	return w

## dialog in vertical Box Layout (old version)

def dialogV(obj):
	"""erzeugen dialog vLayout"""

	w=QtGui.QWidget()
	box = QtGui.QVBoxLayout()
	w.setLayout(box)
	w.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

	for p in obj.props:
		pw=createPropWidget( obj,p)
		box.addWidget(pw)

	w.r=QtGui.QPushButton("close")
	box.addWidget(w.r)
	w.r.pressed.connect(lambda :clear(w))

	w.show()
	return w


##create controller main dialog

def dialog(obj):
	"""erzeuge dialog grid"""

	grid = QtGui.QGridLayout()
	grid.setSpacing(10)

	w=QtGui.QWidget()
	w.setLayout(grid)
	w.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

	bmax=2
	bmax=1
	b=0;l=3
	if hasattr(obj,"props"):
		for i,p in enumerate(obj.props):
			pw=createPropWidget( obj,p)
			grid.addWidget(pw, l, b,)
			b += 1
			if b>bmax: b=0; l+=1

	# common methods ...
	w.r=QtGui.QPushButton("close")
	w.r.pressed.connect(lambda :clear(w))
	grid.addWidget(w.r, 1, 0,1,4)

	w.show()
	return w




#\cond
class PartFeature:
	def __init__(self, obj):
		obj.Proxy = self
		self.Object=obj


	def attach(self,vobj):
		self.Object = vobj.Object

	def claimChildren(self):
		return self.Object.Group

	def __getstate__(self):
		return None

	def __setstate__(self,state):
		return None



class ViewProvider:

	def __init__(self, obj):
		obj.Proxy = self
		self.Object=obj

	def attach(self,vobj):
		self.Object = vobj.Object

	def __getstate__(self):
		return None

	def __setstate__(self,state):
		return None

#-------------------
# contextmenu und double click 

	def setupContextMenu(self, obj, menu):
		self.Object=obj.Object
		action = menu.addAction("Open Editor Dialog ...")
		action.triggered.connect(self.edit)


	def edit(self):
		obj=self.Object
		try: obj.Proxy.dialog.hide()
		except: pass 
		obj.Proxy.dialog=dialog(obj.Object)

	def setEdit(self,vobj,mode=0):
		self.edit()
		return True

	def unsetEdit(self,vobj,mode=0):
		return False

	def doubleClicked(self,vobj):
		print(vobj)
		self.setEdit(vobj,1)

#\endcond


#-------------------


## object to store control panel configuration and data


class ControlPanel(PartFeature):

	def __init__(self, obj):

		PartFeature.__init__(self, obj)

		obj.addProperty("App::PropertyStringList","props","ZZConfig")
		obj.addProperty("App::PropertyBool","noExecute" ,"ZZConfig")

		ViewProvider(obj.ViewObject)
		
		## widget for main dialog
		self.dialog=None


	## create a new dialog when noExecute has changed
	def onChanged(proxy,obj, prop):
		if prop in ["noExecute"]: 
			print ("onChanged",prop)
			proxy.dialog=dialog(obj)

	## lock to prevent recursion
	def execute(proxy,obj):
		if obj.noExecute: return
		try: 
			if proxy.lock: return
		except:
			print("except proxy lock")
		proxy.lock=True
		proxy.myexecute(obj)
		proxy.lock=False


	## open the dialog 
	def myexecute(proxy,obj):
		try: 
			proxy.dialog
		except: 
			proxy.dialog=dialog(obj)

	## read the propertyx values from the source objects into the local property holder 
	def refresh(proxy):
		print("aktualisiere attribute")
		obj=proxy.Object
		for propname in obj.props:
			print(obj)
			# ref holen
			pp=obj.getPropertyByName(propname)
			ref=obj.getPropertyByName(propname+"Source")
			print("Source",ref.Label)
			aa=ref.getPropertyByName(propname)
			print("value",aa)
			setattr(obj,propname,aa)


	##add a object property to controller,
	# set some gui configruation values
	# \param obj object
	# \param propname name of the property
	# \param maxV maximum value for dialer
	# \param minV minimum value for dialer

	def addTarget(self,obj,propname,maxV=None,minV=None):
		gn=obj.Label +"." + propname
		pp=obj.getPropertyByName(propname)

		self.Object.props= self.Object.props +[propname]

		if obj.__class__.__name__ == 'Sheet':
			pt="App::PropertyFloat"
			self.Object.addProperty(pt,propname,gn,)
			self.Object.addProperty("App::PropertyLink",propname+"Source",gn)
			self.Object.addProperty("App::PropertyString",propname+"Typ","Cell")
			setattr(self.Object,propname+"Source",obj)
			setattr(self.Object,propname,float(pp))
			pp=float(pp)
			self.Object.addProperty(pt,propname+"Min",gn)
			self.Object.addProperty(pt,propname+"Max",gn)
			self.Object.addProperty("App::PropertyFloat",propname+"Step",gn)
			#self.Object.addProperty("App::PropertyLink",propname+"Source",gn)
			self.Object.addProperty("App::PropertyBool",propname+"Slider",gn)
			st=1

			if maxV==None: maxV=pp.Value+20
			setattr(self.Object,propname+"Max",maxV)
			#m=pp.Value-20*st
			
			if minV==None: minV=max(0,pp.Value-20)
			setattr(self.Object,propname+"Min",minV)
			setattr(self.Object,propname+"Step",st)
			return


		pt=obj.getTypeIdOfProperty(propname)
		print(pt)



		# App::PropertyAngle
		# App::PropertyLength
		if pt=='App::PropertyLinkList':
			self.Object.addProperty(pt,propname,gn,)
			self.Object.addProperty("App::PropertyLink",propname+"Source",gn)
			setattr(self.Object,propname+"Source",obj)
			setattr(self.Object,propname,pp)
			return

		self.Object.addProperty(pt,propname,gn,"Commnetar")
		self.Object.addProperty(pt,propname+"Min",gn)
		self.Object.addProperty(pt,propname+"Max",gn)
		self.Object.addProperty("App::PropertyFloat",propname+"Step",gn)
		self.Object.addProperty("App::PropertyLink",propname+"Source",gn)
		self.Object.addProperty("App::PropertyBool",propname+"Slider",gn)


		setattr(self.Object,propname+"Source",obj)
		try:
			setattr(self.Object,propname,pp.Value)
			#st=0.01*pp.Value
			st=1

			if maxV==None: maxV=pp.Value+20
			setattr(self.Object,propname+"Max",maxV)
			#m=pp.Value-20*st
			
			if minV==None: minV=max(0,pp.Value-20)
			setattr(self.Object,propname+"Min",minV)
			setattr(self.Object,propname+"Step",st)
		except:
			pass

		try: self.dialog.hide()
		except: print("no dialog to hide")
		try: self.dialog=dialog(obj);print("dialog created")
		except: print("cannot create dialog")

##create generic panel without data,
#
# this is still not a useful method 

def run():
	"""create a generic panel without data"""

	a=FreeCAD.activeDocument().addObject("Part::FeaturePython","MyMonitor")
	ControlPanel(a)




#\cond
def start_here():
#if __name__ == '__main__':

	#-- create test infrastructure
	b=App.ActiveDocument.addObject("Part::Box","Box")
	c=App.ActiveDocument.addObject("Part::Cylinder","Cylinder")
	co=App.ActiveDocument.addObject("Part::Cone","Cone")

	ss=App.activeDocument().addObject('Spreadsheet::Sheet','Spreadsheet')
	ss.set('A1', '45')
	ss.set('B4','123')
	#ss.setAlias('A1','ali')

	cp=App.activeDocument().addObject("Part::Compound","Compound")
	cp.Links = [c,co]

#	fu=App.activeDocument().addObject("Part::MultiFuse","Fusion")
#	fu.Shapes = [b,co]

	cm=App.activeDocument().addObject("Part::MultiCommon","Common")
	cm.Shapes = [b,co]


	for k in  [b,c,co,cp]:
		k.ViewObject.Transparency=70

	App.ActiveDocument.recompute()

	#-------------------------------
	a=FreeCAD.activeDocument().addObject("Part::FeaturePython","MyControlPanel")
	m=ControlPanel(a)
	#-----------------------------

	#-- add some parameters to control
	m.addTarget(c,"Angle",maxV=360,minV=10)
	m.addTarget(ss,"A1",maxV=360,minV=0)
#	m.addTarget(ss,"B4",maxV=360,minV=0)

	if 10:
		m.addTarget(c,"Radius")
#		m.addTarget(co,"Radius1")
		m.addTarget(co,"Radius2")
		

		m.addTarget(co,"Height")
		m.addTarget(b,'Length')

		m.addTarget(cp,'Links')
		m.addTarget(cm,'Shapes')

		m.Object.Radius2Slider = True

	App.activeDocument().recompute()

	#start the dialog
	m.Object.ViewObject.Proxy.edit()

#\endcond

