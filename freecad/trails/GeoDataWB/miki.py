# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- miki - my kivy like creation tools
#--
#-- microelly 2016,2018,2019 (py3)
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------
''' kivy like creation tool'''



# pylint: disable=W0331
# pylint: disable=unused-import
# pylint: disable=invalid-name
# xpylint: disable=bare-except
# xpylint: disable=exec-used

import FreeCAD
import FreeCADGui

#from transportationwb.say import sayexc, say
#from transportationwb.say import  *

import sys
if sys.version_info[0] !=2:
	from importlib import reload


from GeoDataWB.say import sayexc, say
from GeoDataWB.say import  *

from PySide import QtGui, QtCore

import re
import pivy
from pivy import coin

#import nurbswb.configuration
#reload (nurbswb.configuration)
#from nurbswb.configuration import getcb


def getMainWindow():
	'''returns the main window'''
	toplevel = QtGui.qApp.topLevelWidgets()
	for i in toplevel:
		if i.metaObject().className() == "Gui::MainWindow":
			return i
	raise Exception("No main window found")


def getComboView(mw):
	'''returns the Combo View widget'''
	dw = mw.findChildren(QtGui.QDockWidget)
	for i in dw:
		if str(i.objectName()) == "Combo View":
			return i.findChild(QtGui.QTabWidget)
		elif str(i.objectName()) == "Python Console":
			return i.findChild(QtGui.QTabWidget)
	raise Exception("No tab widget found")


def ComboViewShowWidget(widget, tabMode=False):
	'''create a tab widget inside the combo view'''

	# stop to default
	if not tabMode:
		widget.show()
		return widget

	mw = getMainWindow()
	tab = getComboView(mw)
	c = tab.count()

	# clear the combo  window
	for i in range(c - 1, 1, -1):
		tab.removeTab(i)

	# start the requested tab
	tab.addTab(widget, widget.tabname)
	tab.setCurrentIndex(2)

	widget.tab = tab
	return widget


def creatorFunction(name):
	'''generates a python code string for the creation of a Qt/Part/So-Object'''

	print ("create object",name)
	if name.startswith('Part.'):
		[_, c] = name.split('.')
		return "App.activeDocument().addObject('Part::" + c + "','test')"

	if name.startswith('So'):
		return "coin." + name + '()'

	if name.startswith('QtGui'):
		return name + "()"

	if name.startswith('MyQtGui'):
		return name + "()"

	if name.startswith('Animation'):
		[_, c] = name.split('.')
		return 'Animation.create' + c + '()'

	if name in ['Plugger', 'Manager']:
		return 'Animation.create' + name + '()'

	# default method
	return name + '()'


# a test method
# YourSpecialCreator=Animation.createManager


def VerticalLayoutTab(title=''):
	''' create as a tab widget for the comboView '''

	t = QtGui.QLabel("my widget")
	w = MikiWidget(t, "Reconstruction WB")

	try:
		FreeCAD.w5.append(w)
	except:
		FreeCAD.w5 = [w]

	if title != '':
		w.setWindowTitle(title)

	w.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
	ComboViewShowWidget(w, True)

	# store it to FC.w5

	return w

def setSpacer():
	'''special command for QSpacerItem'''
	return "__MAGIC__ Spacer"

def run_magic(p,c):
	''' special command wrapper'''
	p.layout.addItem(QtGui.QSpacerItem(
			10, 10, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding))


def DockWidget(title=''):
	'''create a dock widget in a gibes dock container window'''

	t = QtGui.QLabel("my widget")
	w = MikiDockWidget(t, "My Dock")

	# w=QtGui.QWidget()
# w.setStyleSheet("QWidget { font: bold 18px;color:brown;border-style:
# outset;border-width: 3px;border-radius: 10px;border-color: blue;}")

	if title != '':
		w.setWindowTitle(title)

	layout = QtGui.QVBoxLayout()
	layout.setAlignment(QtCore.Qt.AlignTop)
	# w.layout=layout
	# w.setLayout(layout)

	w.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
	w.show()
	# ComboViewShowWidget(w,True)
	try:
		FreeCAD.w5.append(w)
	except:
		FreeCAD.w5 = [w]

	getdockwindowMgr2(w, "FreeCAD")
	return w


def MainWindow(title=''):
	'''create the dialog as a main window (not a dock widget)'''

	w = QtGui.QWidget()
# w.setStyleSheet("QWidget { font: bold 18px;color:brown;border-style:
# outset;border-width: 3px;border-radius: 10px;border-color: blue;}")

	if title != '':
		w.setWindowTitle(title)

	layout = QtGui.QVBoxLayout()
	layout.setAlignment(QtCore.Qt.AlignTop)
	w.layout = layout
	w.setLayout(layout)

	w.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
	w.show()

	try:
		FreeCAD.w5.append(w)
	except:
		FreeCAD.w5 = [w]
	return w


def HorizontalLayout(title=''):
	'''create a QHBoxLayout'''

	w = QtGui.QWidget()
	# w.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

# w.setStyleSheet("QWidget { font: bold 18px;color:blue;border-style:
# outset;border-width: 3px;border-radius: 10px;border-color: blue;}")
	layout = QtGui.QHBoxLayout()
	layout.setAlignment(QtCore.Qt.AlignLeft)
	w.setLayout(layout)

	if title != '':
		w.setWindowTitle(title)
	# w.show()
	# ComboViewShowWidget(w,False)
	w.layout = layout
	return w


def VerticalLayout(title=''):
	'''create a QVBoxLayout'''

	w = QtGui.QWidget()
	# w.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)

# w.setStyleSheet("QWidget { font: bold 18px;color:blue;border-style:
# outset;border-width: 3px;border-radius: 10px;border-color: blue;}")
	layout = QtGui.QVBoxLayout()
	layout.setAlignment(QtCore.Qt.AlignLeft)
	w.setLayout(layout)
	if title != '':
		w.setWindowTitle(title)
	w.layout = layout
	return w


def HorizontalGroup(title=''):
	'''create a GroupBox with a QHBoxLayout'''

	w = QtGui.QGroupBox()
	w.setStyleSheet(
		"QGroupBox { border: 2px solid green; border-radius: 5px;"
		"margin: 7px; margin-bottom: 7px; padding: 0px}"
		"QGroupBox::title {top:-7 ex;left: 10px; subcontrol-origin: border}")
	w.setTitle("horizonmmtal layout group")
	layout = QtGui.QHBoxLayout()
	layout.setAlignment(QtCore.Qt.AlignLeft)
	w.setLayout(layout)
	if title != '':
		w.setWindowTitle(title)
	w.layout = layout
	return w


def VerticalGroup(title=''):
	'''create a GroupBox with a QVBoxLayout'''

	w = QtGui.QGroupBox()
	w.setStyleSheet(
	"QGroupBox { border: 3px solid blue; border-radius: "
	"5px; margin: 7px; margin-bottom: 7px; padding: 0px} "
	"QGroupBox::title {top:-7 ex;left: 10px; subcontrol-origin: border}")
	w.setTitle("vertical layout group")
	layout = QtGui.QVBoxLayout()
	layout.setAlignment(QtCore.Qt.AlignLeft)
#	label = QtGui.QLabel("HUWAS2")   
#	layout.addWidget(label)
#	verticalSpacer = QtGui.QSpacerItem(10, 40, QtGui.QSizePolicy.Minimum, QtGui.QSizePolicy.Expanding)
#	layout.addItem(verticalSpacer)
	w.setLayout(layout)
	if title != '':
		w.setWindowTitle(title)
	w.layout = layout
	return w


##\cond
def ftab2(name="horizontal"):

	w = QtGui.QWidget()
	layout = QtGui.QHBoxLayout()
	layout.setAlignment(QtCore.Qt.AlignLeft)
	w.setLayout(layout)
	pB = QtGui.QLabel(name)
	pB.setStyleSheet(
	"QWidget { font: bold 18px;color:red;border-style: outset;"
	"border-width: 3px;border-radius: 10px;border-color: blue;}")
	layout.addWidget(pB)
	# w.show()
	ComboViewShowWidget(w, False)

	w1 = QtGui.QWidget()
# w.setStyleSheet("QWidget { font: bold 18px;color:blue;border-style:
# outset;border-width: 3px;border-radius: 10px;border-color: blue;}")
	layout1 = QtGui.QVBoxLayout()
	layout1.setAlignment(QtCore.Qt.AlignLeft)

	w1.setLayout(layout1)

	pB1 = QtGui.QLabel("name1")
	layout1.addWidget(pB1)
	pB1 = QtGui.QLabel("name1")
	layout1.addWidget(pB1)

	layout.addWidget(w1)

	w2 = QtGui.QWidget()
# w.setStyleSheet("QWidget { font: bold 18px;color:blue;border-style:
# outset;border-width: 3px;border-radius: 10px;border-color: blue;}")
	layout2 = QtGui.QVBoxLayout()
	layout2.setAlignment(QtCore.Qt.AlignLeft)

	w2.setLayout(layout2)

	pB2 = QtGui.QLabel("name2")
	layout2.addWidget(pB2)
	pB1 = QtGui.QLabel("name1")
	layout2.addWidget(pB1)

	layout.addWidget(w2)

	w.layout = layout
	return w
##\endcond

'''
Miki is the parser and executer for miki configuration strings or files
'''

class Miki(object):
	''' Miki is the parser and executer for miki configuration strings or files'''


	def __init__(self):
		## objects of huhu
		self.objects = [] 
		## the widget of the generated Qt sctructure
		self.widget = None
		## the ids of the input/output sub-widgets 
		self.ids = {}
		
		##\cond
		self.anchors = {}
		self.indents = []
		self.olistref = []
		self.indpos = -1
		self.app = None
		self.classes = {}
		self.lines = []
	##\endcond

	def parse2(self, configurationString):
		'''parse the configuration string'''

		ls = configurationString.splitlines()

		# pylint: disable=unused-variable
		app = self.app
		line = 0
		depth = 0
		d = [0]*30
		ln = [0]*30
		refs = {}
		rs = []
		r = None
		r = [-1, 0, 0, '']
		for l in ls:
			ltxt = l

			if r:
				rs.append(r)
				r = [-1, 0, 0, '']
			line += 1

			if l.startswith('#:'):
				res = re.search(r"#:\s*(\S.*)", l)
				r = [l, line, -1, 'cmd', res.group(1)]
				continue

			if re.search(r"^\W*#", l):
				continue

			res = re.search(r"\<(\S.*)\>:", l)
			if res:
					parent = 0
					ln[0] = line
					depth = 0
					r = [l, line, parent, "local class", res.group(1)]
					self.classes[res.group(1)] = line
					continue

			res = re.search(r"(\s*)(\S.*)", l)
			if res:
				l = len(res.group(1))

				if l == 0:
					depth = 0
				if d[depth] < l:
					depth += 1
				elif d[depth] > l:
					depth -= 1
				try:
					d[depth] = l
				except:
					sayexc(str([l, ltxt]))

				parent = ln[l - 1]
				ln[l] = line

				r = [l, line, parent, res.group(2), depth, ln]
				st = res.group(2)

				res = re.search(r"(\S+):\s*\*(\S+)", st)
				if res:
					r = [l, line, parent, 'link',
							res.group(1), res.group(2), refs[res.group(2)]]
					continue

				res = re.search(r"(\S+):\s*&(\S+)\s+(\S.*)", st)
				if res:
					r = [l, line, parent, "anchor attr",
							res.group(1), res.group(2), res.group(3)]
					refs[res.group(2)] = line
					continue

				res = re.search(r"(\S+):\s*&(\S+)", st)
				if res:
					r = [l, line, parent, "anchor", res.group(1), res.group(2)]
					refs[res.group(2)] = line
					continue

				res = re.search(r"(\S+[^:]):\s*([^:]\S.*)", st)
				if res:
					r = [l, line, parent, "att val", res.group(1), eval(res.group(2))]
					if res.group(1) == 'Name':
						rs[parent].append(res.group(2))
					continue

				res = re.search(r"\s*(\S):\s*([^:]\S.*)", st)
				if res:
					r = [l, line, parent, "att val", res.group(1), eval(res.group(2))]
					if res.group(1) == 'Name':
						rs[parent].append(res.group(2))
					continue
				else:
					res = re.search(r"(\S+):", st)
					if res:
						r = [l, line, parent, "obj", res.group(1), 'no anchor']
		##\cond
		self.anchors = refs
		self.lines = rs
		##\endcond

		
		#debug = getcb("mikidebug")
		debug=0
		#debug = 1
		if debug:
			say("lines parsed ...")
			for r in rs:
					say (r)
			if len(self.anchors.keys()) > 0:
				say("Anchors ....")
				say(self.anchors)

	def build(self):
		'''execute the parsed data (expected in self.lines)'''
		##\cond
		self.widget = None
		##\endcond
#		from pivy import coin
#		from pivy.coin import *

		for l in self.lines:

			if l[3] == 'cmd':
				try:
					exec(l[4])
				except:
					sayexc(str(["Error exec:", l[4]]))
				continue
			if l[3] == 'obj' or l[3] == 'anchor' or l[3] == 'local class':
					name = l[4]
					try:
						f = name + "()"
						f2 = name
					except:
						f = creatorFunction(l[4])

					f = creatorFunction(l[4])

					if len(l) < 7:  # no name for object
						l.append('')

					if l[3] == 'local class':
						exec("class " + name + "(object):pass")
						h = eval(f2)
					else:
						h = eval(f)
					if len(l) < 7:
						l.append(None)
					l.append(h)
					self.objects.append(h)
					##\cond
					if self.widget == None:
						self.widget = h
					##\endcond
			if l[2] != 0:
				if l[4] == 'Name':
					continue
				if l[3] == 'obj' or l[3] == 'anchor':
					parent = self.lines[l[2]][7]
					self.addChild(parent, l[7])
				if l[3] == 'link':
					parent = self.lines[l[2]][7]
					try:
						child = self.lines[l[6]][7]
						self.addChild(parent, child)
					except:
						# link eines attribs
						method = l[4]
						v = self.lines[l[6]][6]
						kk = eval("parent." + l[4])
						cnkk = kk.__class__.__name__

						if cnkk.startswith('So'):
							ex = "parent." + method + ".setValue(" + str(v) + ")"
							exec(ex)
							continue
						if cnkk == 'builtin_function_or_method':
							kk(v)
							continue

						cn = v.__class__.__name__
						if cn == 'int' or cn == 'float':
							ex = "parent." + l[4] + "=" + str(v)
						elif cn == 'str':
							ex = "parent." + l[4] + "='" + v + "'"
						else:
							sayW("nicht implementierter typ")
							sayW([v,cn])
							sayW(l)
							ex = ''
						exec(ex)

			if l[3] == 'att val' or l[3] == 'anchor attr':

					method = l[4]
					parent = self.lines[l[2]][7]

					if l[3] == 'att val':
						v = l[5]
					else:
						v = l[6]
					if method == 'id':
						self.ids[v] = parent
						continue

					try:
						kk = eval("parent." + l[4])
					except:

						cn = v.__class__.__name__
						if cn == 'int' or cn == 'float':
							ex = "parent." + l[4] + "=" + str(v)
						elif cn == 'str':
							ex = "parent." + l[4] + "='" + v + "'"
						elif cn=='Vector':
							sayW("nicht implementierter typ  Ax")
							sayW([v,cn])
							sayW(l)
							sayW(parent)
							ex="parent."+l[4]+"(FreeCAD."+str(v)+")"
							sayW("*** "+ex)
						elif l[4]=='setValue':
							parent.setValue(v)
							continue
						else:
							sayW("nicht implementierter typ  Ayy")
							sayW([v,cn])
							sayW(l)
							ex='' 

						exec(ex)
						continue

					kk = eval("parent." + l[4])
					cnkk = kk.__class__.__name__
					if cnkk.startswith('So'):
						if v.__class__.__name__.startswith('Sb'):
							aaa=v
							ex = "parent." + method + ".setValue(aaa)"
						else:
							ex = "parent." + method + ".setValue(" + str(v) + ")"
						exec(ex)
						continue

					if cnkk == 'builtin_function_or_method':
							kk(v)
							continue

					cn = v.__class__.__name__
					if cn == 'int' or cn == 'float':
						ex = "parent." + l[4] + "=" + str(v)
					elif cn == 'str':
						if l[4].startswith("run"):
							ex = "parent." + l[4] + "('" + v + "')"
						else:
							ex = "parent." + l[4] + "='" + v + "'"
					elif cn=='Vector':
							ex="parent."+l[4]+"(FreeCAD."+str(v)+")"
					else:
						sayW("nicht implementierter typ B")
						sayW([v,cn])
						sayW(l)
						aaa=v
						ex="parent."+l[4]+"(aaa)"
					say("//*** " + ex)
					exec(ex)

		return self.widget

	def showSo(self):
		''' add the item as openinventor objects to FreeCADGui.ActiveDocument.ActiveView.getSceneGraph()'''

		for l in self.lines:
			if l[2] == 0 and l[0] != -1:
					if len(l) < 7:
						continue
					r = l[7]
					if r.__class__.__name__.startswith('So'):
						sg = FreeCADGui.ActiveDocument.ActiveView.getSceneGraph()
						sg.addChild(r)

	def showSo2(self, dokname):
		''' add the item as openinventor objects to ActiveView.getSceneGraph() for a given document '''

		for l in self.lines:
			if l[2] == 0 and l[0] != -1:
					r = l[7]
					if r.__class__.__name__.startswith('So'):
						dok = FreeCADGui.getDocument(dokname)
						sg = dok.ActiveView.getSceneGraph()
						sg.addChild(r)

	def addChild(self, parent, child):
		''' add the child to the parent during the build'''

		p=parent
		c=child
		cc = c.__class__.__name__
		if 0:
			say (p)
			say (p.__class__)
			say ('--')
			say (c)
			say (c.__class__)
			say (cc)


#		if str(c.__class__).startswith("<type 'PySide.QtGui.") or  str(c.__class__).startswith("<class 'nurbswb.miki"):
		if str(c.__class__).startswith("<class 'PySide2.QtWidgets.") or \
			str(c.__class__).startswith("<type 'PySide.QtGui.") or  str(c.__class__).startswith("<class 'nurbswb.miki"):

			if p.__class__.__name__ ==  '_MyTabWidget':
				p.addWidget(c)
			else:
				p.layout.addWidget(c)
			return

		if cc.startswith('So'):
			p.addChild(c)
			return

		if	p.__class__.__name__ == 'object' or \
			str(p.__class__).startswith("<class 'geodat.miki."):
			# "Add children to object"
			try:
				p.children.append(c)
			except:
				p.children = [c]
			return
		try:
			if str(p.TypeId) == 'Part::MultiFuse':
				z = p.Shapes
				z.append(c)
				p.Shapes = z
			elif str(p.TypeId) == 'Part::Compound':
				z = p.Links
				z.append(c)
				p.Links = z
			else:
				try:
					p.addObject(c)
				except:
					try:
						if c.startswith('__MAGIC_'):
							run_magic(p,c)
					except:
						FreeCAD.Console.PrintError("\naddObject funktioniert nicht A")
						FreeCAD.Console.PrintError([p, c])
		except:
				try:
					print ("TRy to add",c)
					p.addObject(c)
				except:
					try:
						if c.startswith('__MAGIC_'):
							run_magic(p,c)
					except:
						FreeCAD.Console.PrintError("\naddObject funktioniert nicht BBB")
						FreeCAD.Console.PrintError([p, c])


	def run(self, string, cmd=None):
		''' parse the configuration string and execute the resulting tree'''

		debug = False
		if debug:
			sayW("parse2 ....")
		self.parse2(string)
		if debug:
			sayW("build ...#")
		rca = self.build()

		if debug:
			sayW("showSo ...")
		self.showSo()
		if cmd != None:
			say("CMD ...")
			say(cmd)
			rca = cmd()
			say(("rc run...", rca))
		return rca

	def roots(self):
		'''returns a list of all roots of the configuration tree'''
		rl = []
		for l in self.lines:
			if l[0] == 0:
				rl.append(l)
		return rl

	def report(self, results=None):
		'''some debug information about objects, anchors, roots'''
		say("Results ...")
		if results == None:
			results = []
		for r in results:
			say(r)
			if r.__class__.__name__.startswith('So'):
				sg = FreeCADGui.ActiveDocument.ActiveView.getSceneGraph()
				sg.addChild(r)

		say ("Data ...")
		for ob in self.objects:
			say (ob)

		say (self.anchors)

		for r in self.roots():
			say (r)



class MikiWidget(QtGui.QWidget):
	'''the widget for the mikidialog'''

	def __init__(self, title_widget, objectname):

		QtGui.QWidget.__init__(self)
		## the widget with the title information
		self.title_widget = title_widget
		## the Tabname of the ComboView Tab for the miki widget
		self.tabname = "MikiTab"
		##\cond
		self.setWindowTitle(objectname)
		self.setObjectName(objectname)
		layout = QtGui.QVBoxLayout()
		self.setLayout(layout)
		self.layout = layout
		self.dwl = None
		##\endcond


class MikiDockWidget(QtGui.QDockWidget):

	def __init__(self, title_widget, objectname):

		QtGui.QDockWidget.__init__(self)

		self.title_widget = title_widget
		self.setWindowTitle(objectname)
		self.setObjectName(objectname)

#		self.toggle_title_widget(False)
#		self.toggle_title_widget(True)
#		self.topLevelChanged.connect(self.toggle_title_widget)
		if 1:
			self.setTitleBarWidget(None)
		else:
			self.setTitleBarWidget(self.title_widget)

		self.setMinimumSize(200, 185)

		self.centralWidget = QtGui.QWidget(self)
		self.setWidget(self.centralWidget)
		# self.centralWidget.setMaximumHeight(800)

		layout = QtGui.QVBoxLayout()
		self.layout = layout
		self.centralWidget.setLayout(layout)
		self.scroll = QtGui.QScrollArea()

		self.liste = QtGui.QWidget()
		self.lilayout = QtGui.QVBoxLayout()
		self.liste.setLayout(self.lilayout)

		mygroupbox = QtGui.QGroupBox()
		mygroupbox.setStyleSheet(
		"QWidget { background-color: lightblue;margin:0px;padding:0px;}"
		"QPushButton { margin-right:0px;margin-left:0px;margin:0 px;padding:0px;;"
		"background-color: lightblue;text-align:left;"
		"padding:6px;padding-left:4px;color:brown; }")
		self.mygroupbox = mygroupbox

		myform = QtGui.QFormLayout()
		self.myform = myform
		self.myform.setSpacing(0)
		mygroupbox.setLayout(myform)

		scroll = QtGui.QScrollArea()
		scroll.setWidget(mygroupbox)
		scroll.setWidgetResizable(True)
		self.lilayout.addWidget(scroll)

		# optionaler Top button
		if 0:
			self.pushButton00 = QtGui.QPushButton(
	  QtGui.QIcon('icons:freecad.svg'), objectname)
			layout.addWidget(self.pushButton00)

		self.pushButton01 = QtGui.QPushButton(
			QtGui.QIcon(FreeCAD.ConfigGet('UserAppData') + '/Mod/mylib/icons/mars.png'),
			"Mars")
		# self.pushButton01.clicked.connect(self.start)

#		layout.addWidget(self.liste)
#		layout.addWidget(self.pushButton01)

		self.createToplevelButtons()

	def createToplevelButtons(self):
		'''create a row of top level buttons (experimental)'''

		dw = QtGui.QWidget()
		dwl = QtGui.QHBoxLayout()
		dw.setLayout(dwl)
		# pylint: disable=attribute-defined-outside-init
		self.dwl = dwl

		if 0:  # Top level Icon leiste optional sichtbar machen
			self.layout.addWidget(dw)
		# self.setTitleBarWidget(dw)

		l = QtGui.QLabel('Label')
		# dwl.addWidget(l)
		self.add_top(l)

		b = QtGui.QPushButton('Butto')
		# dwl.addWidget(b)
		self.add_top(b)

		b = QtGui.QPushButton(QtGui.QIcon('icons:freecad.svg'), 'Icon+Button')
		# dwl.addWidget(b)
		self.add_top(b)

		b = QtGui.QPushButton(QtGui.QIcon('icons:view-refresh.svg'), '')
		self.add_top(b)

		b = QtGui.QPushButton(QtGui.QIcon(
		'/home/microelly2/.FreeCAD/Mod/reconstruction/icons/std_viewscreenshot.svg'), 'Foto Image')
		self.add_top(b)

		b = QtGui.QPushButton(QtGui.QIcon(
		'/home/microelly2/.FreeCAD/Mod/reconstruction/icons/web-home.svg'), 'Foto 3D')
		self.add_top(b)

		self.layout.setSpacing(0)
#		self.layout = layout

	def add_top(self, widget):
		'''add a widget to the top level row'''
		self.dwl.addWidget(widget)

	def toggle_title_widget(self, off):
		''' toggle the display of the TitleBar Widget'''
		off=False
		if off:
			self.setTitleBarWidget(None)
		else:
			self.setTitleBarWidget(self.title_widget)


def getMainWindowByName(name):
	'''returns a main window of a given Title, 
	if there is no such main window an new main window is created'''

	if name == 'FreeCAD':
		return FreeCADGui.getMainWindow()

	toplevel2 = QtGui.qApp.topLevelWidgets()
	for i in toplevel2:

		if name == i.windowTitle():
			i.show()
			return i

	r = QtGui.QMainWindow()

	FreeCAD.r = r
	r.setWindowTitle(name)
	r.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
	r.show()
	return r

class _MyTabWidget(QtGui.QTabWidget):

	def __init__(self,):
		QtGui.QTabWidget.__init__(self)
		self.setMinimumSize(500, 800)

	def addWidget(self,w):
		self.addTab(w,self.tabname)
		self.show()


class MyWidget(QtGui.QLabel):

	def __init__(self,):
		QtGui.QLabel.__init__(self)

	def setTabname(self,name):
		self.tabname=nae

def MyTabWidget(title=''):
	
	'''create the dialog as a main window (not a dock widget)'''

	w = _MyTabWidget()

#	layout = QtGui.QVBoxLayout()
#	layout.setAlignment(QtCore.Qt.AlignTop)
#	w.layout = layout
#	w.setLayout(layout)
#
	w.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
#	w.show()

	try:
		FreeCAD.w5.append(w)
	except:
		FreeCAD.w5 = [w]
	return w






def getdockwindowMgr2(dockwindow, winname="FreeCAD"):
	'''add the dock window to the dockwindowManager(main window) winname'''

	d3=dockwindow
	if 1:
		winname = "OTTO"
		winname = "FreeCAD"
		w = getMainWindowByName(winname)

		w.addDockWidget(QtCore.Qt.LeftDockWidgetArea, d3)
		d3.setAllowedAreas(QtCore.Qt.LeftDockWidgetArea|QtCore.Qt.RightDockWidgetArea)

		if 0:
			t = QtGui.QLabel('Title 1')
			d = MikiDockWidget(t, "huhu")
			w.addDockWidget(QtCore.Qt.LeftDockWidgetArea, d)
			t = QtGui.QLabel('Title 2')
			d2 = MikiDockWidget(t, "haha")
			w.addDockWidget(QtCore.Qt.LeftDockWidgetArea, d2)

			w.tabifyDockWidget(d3, d2)
			w.tabifyDockWidget(d2, d)

		d3.raise_()
		w.show()

		return w



class Miki_Contextmenu(Miki):
	'''the miki as contextmenu entry'''

	def __init__(self, App, layoutstring, obj):
		Miki.__init__(self)
		## the Application with the logic behind the Gui
		self.app = App()
		self.app.root = self
		self.app.obj = obj
		obj.ViewObject.Proxy.cmenu.append(["Dialog", lambda: self.run(layoutstring)])
		obj.ViewObject.Proxy.edit = lambda: self.run(layoutstring)


class MikiApp(object):
	'''example for the execution layer of the Gui'''

	def __init__(self):
		## reference to the miki Gui object
		self.root = None

	def run(self):
		'''example button clicked method'''
		say ("Button clicked")
		say (self.root)
		say (self.root.widget)

	def close2(self):
		'''close the combo view tab'''
		mw = getMainWindow()
		tab = getComboView(mw)
		c = tab.count()

		# clear the combo windows #2 and more
		for i in range(c - 1, 1, -1):
			tab.removeTab(i)

	def itemClicked(self, item):
		'''example for item clicked'''
		say (item)
		say (item.text())

	def close(self):
		'''delete the widget'''
		self.root.widget.deleteLater()
		self.close2()


# https://stackoverflow.com/questions/28282434/how-to-combine-opencv-with-pyqt-to-create-a-simple-gui

class PicWidget(QtGui.QLabel):
	'''the widget for the mikidialog'''

	def __init__(self):

		QtGui.QLabel.__init__(self)
		self.sizeX=0
		self.sizeY=0
		self.label=None


	def run_display(frame,pn):


		import cv2
		if frame.label == None:
			label_Image = QtGui.QLabel(frame)
			frame.label =label_Image
		else:
			label_Image = frame.label

		label_Image.setAlignment(QtCore.Qt.AlignCenter)

	#	size=250
	#	im= np.zeros((size,size,3), np.uint8)
	#	im = cv2.imread(pn,0)

		im = cv2.imread(pn)

		cc = im.shape[1]*im.shape[2]
		im[10:20,10:20]=[140,240,140]
		image_profile = QtGui.QImage(im.data, im.shape[1], im.shape[0], cc, QtGui.QImage.Format_RGB888)
	#	image_profile = QtGui.QImage(image_path) #QImage object
		if frame.sizeX!=0 and frame.sizeY!=0:
			image_profile = image_profile.scaled(frame.sizeX,frame.sizeY, aspectRatioMode=QtCore.Qt.KeepAspectRatio, transformMode=QtCore.Qt.SmoothTransformation) # To scale image for example and keep its Aspect Ration    
		label_Image.setPixmap(QtGui.QPixmap.fromImage(image_profile))
		frame.setMinimumSize(PySide.QtCore.QSize( im.shape[1], im.shape[0]))
		if frame.sizeX!=0 and frame.sizeY!=0:
			frame.setMinimumSize(PySide.QtCore.QSize(frame.sizeX,frame.sizeY))
		label_Image.setAlignment(QtCore.Qt.AlignCenter)
		
		return frame

##use case
#pn='/home/thomas/Bilder/bp_841.png'
#frame= PicWidget()
#frame.show_frame_in_display(pn)
#frame.show()




class Controller(MikiApp):
	pass


def createMikiGui(layout, app):
	'''creates a miki Gui object (widget and logic)
	for the view layout string and the controller app'''

	miki = Miki()
	appi = app()

	miki.app = appi
	appi.root = miki

	rca = miki.run(layout)
	
	return rca




def createMikiGui2(layout, app):
	'''creates a miki Gui object (widget and logic)
	for the view layout string and the controller app'''

	miki = Miki()
	appi = app()

	miki.app = appi
	appi.root = miki

	rca = miki.run(layout)
	#return rca,miki
	return appi





def testme(mode=''):
	'''miki Qt example
	modes: VerticalLayoutTab MainWindow DockWidget

	'''

	layout = '''
#VerticalLayoutTab:
MainWindow:
#DockWidget:

#	id:'main'
	QtGui.QLabel:
		setText:"***   N U R B S     E D I T O R   ***"
	VerticalLayout:
		HorizontalGroup:
			QtGui.QLabel:
				setText: "My Label"
			QtGui.QPushButton:
				setText: "My Button"
			QtGui.QLabel:
				setText: "My Label 2"
		VerticalGroup:
			QtGui.QLabel:
				setText:"Action "

			QtGui.QPushButton:
				setText: "Run Action"
				clicked.connect: app.run
				setIcon: QtGui.QIcon('/home/thomas/.FreeCAD/Mod/freecad-transportation-wb/icons/one_center_curve.svg')
				setIconSize: QtCore.QSize(40,40)

			QtGui.QPushButton:
				setText: "close Tab"
				clicked.connect: app.close

			HorizontalGroup:
				VerticalLayout:
					QtGui.QLineEdit:
						setText:"edit Axample"
					QtGui.QLineEdit:
						setText:"edit B"
				VerticalGroup:
					QtGui.QLineEdit:
						setText:"edit B"
					QtGui.QLabel:
						setText: "My Label"


		#	QtGui.QLineEdit:
	#			setText:"horizel "
	QtGui.QListWidget:
		addItem: "HUHU"
		addItem: "HADA"
		addItem: "Hooo"
		addItem: "Hiii"
		itemClicked.connect: app.itemClicked
	HorizontalLayout:
		QtGui.QLabel:
			#setGeometry:  PySide.QtCore.QRect(0,0,100,300)
			setPixmap: QtGui.QPixmap('/home/thomas/Bilder/freeka.png')
		VerticalLayout:
			QtGui.QLineEdit:
				setText:"AA"
			QtGui.QLineEdit:
				setText:"BB"
		VerticalGroup:
			setTitle: "Slider"
			HorizontalLayout:
				# https://srinikom.github.io/pyside-docs/PySide/QtGui/QSlider.html
				# https://github.com/pyside/Examples/blob/master/examples/widgets/sliders.py
				QtGui.QSlider:
				QtGui.QSlider:


		VerticalLayout:
			QtGui.QDial:
				setFocusPolicy: QtCore.Qt.StrongFocus
			QtGui.QDial:
			QtGui.QSlider:
				setOrientation: PySide.QtCore.Qt.Orientation.Horizontal

	HorizontalGroup:
		QtGui.QComboBox:
			id: 'actionmode'
			addItem: "change Height relative"
			addItem: "set absolute Height and Weight"
			addItem: "Add VLine"
			addItem: "Add ULine"
#				addItem: "Elevate VLine"
#				addItem: "Elevate ULine"
#				addItem: "Elevate Rectangle"
#				addItem: "Elevate Circle"
#			currentIndexChanged.connect: app.setActionMode

		QtGui.QCheckBox:
			id: 'relativemode'
			setText: 'Height relative'
#			stateChanged.connect: app.relativeMode
			setChecked: True



	'''


	layoutVT = '''
VerticalLayoutTab:
	setAlignment:QtCore.Qt.AlignTop
	VerticalGroup:
		QtGui.QPushButton:
		QtGui.QPushButton:
		QtGui.QLabel:
			setText:"***   Tab    D E M O   ***"
	VerticalGroup:
		setAlignment:QtCore.Qt.AlignTop
		HorizontalGroup:
			QtGui.QPushButton:
				setText: "close"
				clicked.connect: app.close
			QtGui.QPushButton:
		QtGui.QPushButton:
	VerticalGroup:
	setSpacer: 
	'''


	layoutMW = '''
MainWindow:
	QtGui.QLabel:
		setText:"***   Main Window    D E M O   ***"
	VerticalLayout:
		HorizontalGroup:
			QtGui.QPushButton:
				setText: "close"
				clicked.connect: app.close
	'''


	layoutDW = '''
DockWidget:
	QtGui.QLabel:
		setText:"***   Dock Widget    D E M O   ***"
	VerticalLayout:
		HorizontalGroup:
			QtGui.QPushButton:
				setText: "close"
				clicked.connect: app.close
	setSpacer:
	'''


	if mode == 'VerticalLayoutTab':
		layout = layoutVT
	elif mode == 'MainWindow':
		layout = layoutMW
	elif mode == 'DockWidget':
		layout = layoutDW

	mikigui = createMikiGui(layout, MikiApp)
	return mikigui


if __name__ == '__main__':
	say("miki transport ...")
	testme()

def testDialogMainWindow():
	return testme("MainWindow")

def testDialogTab():
	return testme('VerticalLayoutTab')

def testDialogDockWidget():
	return testme("DockWidget")

def testDialog():
	rc = testme()

	return rc
