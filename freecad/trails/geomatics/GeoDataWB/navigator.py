'''navigation in 3D'''

# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- event filter next germ + navigator
#--
#-- microelly 2016
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------

#http://doc.qt.io/qt-5/qt.html#Key-enum
#http://doc.qt.io/qt-5/qevent.html#Type-enum
#http://doc.qt.io/qt-5/qcolor.html#setNamedColor
#http://doc.qt.io/qt-5/richtext-html-subset.html

from .say import sayexc
from PySide import QtGui,QtCore
import FreeCAD,FreeCADGui
from pivy import coin
import os
import time,math



# whenever the module is loaded stop an old eventserver
try:
	stop()
except Exception:
	pass

# the debug window for runtime parameter
def myDebugWidget():
	liste=QtGui.QWidget()
	liste.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
	layout=QtGui.QVBoxLayout()
	liste.setLayout(layout)
	liste.vmap={}
	for k in ['key','xa','ya','za','xr','yr','zr','dxw','dyw','click','clickcount' ]:
		line = QtGui.QLineEdit()
		line.setText("("+k+")")
		layout.addWidget(line)
		liste.vmap[k]=line
	for k in ['windows']:
		line = QtGui.QTextEdit()
		line.setText("("+k+")")
		layout.addWidget(line)
		liste.vmap[k]=line

	bt= QtGui.QPushButton()
	bt.setText("Ende")
	bt.clicked.connect(stop)
	layout.addWidget(bt)

	liste.show()
	return liste

# callback when a key is released
def on_key_release(ef,keystring):
	print("on_key_release:", keystring)
	return True

def on_key_press(ef,keystring):

	try:
		camera=FreeCADGui.activeDocument().activeView().getCameraNode()

		if ef.firstCall:
			FreeCADGui.activeDocument().activeView().setCameraType("Perspective")
			ef.firstCall=False

			campos=FreeCAD.Vector( 0, 0, 0)
			camera.position.setValue(campos) 

			nD=100
			fD=12000000
			camera.nearDistance.setValue(nD)
			camera.farDistance.setValue(fD)


		if keystring=='X' or keystring=='Insert':
			ef.campos.x += 10
		if keystring=='Y'or keystring=='Home' :
			ef.campos.y += 10
		if keystring=='Z'or keystring=='PageUp':
			ef.campos.z += 10

		if keystring=='Shift-X'or keystring=='Delete':
			ef.campos.x -= 10
		if keystring=='Shift-Y'or keystring=='End':
			ef.campos.y -= 10
		if keystring=='Shift-Z'or keystring=='PageDown':
			ef.campos.z -= 10

		if keystring=='F12':
			ef.campos = FreeCAD.Vector( 0, 0, 0)
			ef.laenge=0
			ef.breite=0
			ef.roll=0

		if keystring=='Control-Left':
					ef.roll +=  10
		if  keystring=='Control-Right':
					ef.roll -=  10
		if  keystring=='Control-Down':
					ef.roll =  0

		if ef.mode=='turn':
			if keystring=='Up':
				ef.breite += 1.0
			if keystring=='Down':
				ef.breite -= 1.0
			if keystring=='Shift-Up' or keystring=='Shift-Down':
					ef.breite=-ef.breite
					if ef.laenge <=0:
						ef.laenge +=  180
					else:
						ef.laenge -=  180

			if keystring=='Left':
				ef.laenge -= 1.1
			if keystring=='Right':
				ef.laenge += 1.2
			if keystring=='Shift-Left' or  keystring=='Shift-Right':
					if ef.laenge <=0:
						ef.laenge +=  180
					else:
						ef.laenge -=  180

		elif ef.mode=='walk':
			FreeCAD.Console.PrintMessage('walk mode')
			if keystring=='Left':
				ef.direction -= 0.1
				ef.laenge= -90+ef.direction*180/math.pi
			if keystring=='Right':
				ef.direction += 0.1
				ef.laenge= -90+ef.direction*180/math.pi
			if keystring=='Up':
				ef.campos.x -= ef.speed*math.cos(ef.direction)
				ef.campos.y += ef.speed*math.sin(ef.direction)
				ef.campos.z += ef.speed*math.sin(ef.breite/180*math.pi)
			if keystring=='Down':
				ef.campos.x += ef.speed*math.cos(ef.direction)
				ef.campos.y -= ef.speed*math.sin(ef.direction)
				ef.campos.z -= ef.speed*math.sin(ef.breite/180*math.pi)

			if keystring=='Return':
				pass



		elif ef.mode=='xyz':
			FreeCAD.Console.PrintError('xyz mode')
			if keystring=='Up':
				ef.campos.z += ef.speed*math.cos(math.pi*ef.roll/180) 
			if keystring=='Down':
				ef.campos.z -= ef.speed*math.cos(math.pi*ef.roll/180)

			if keystring=='Left':
				ef.campos.y += ef.speed*math.sin(0.0+ef.laenge/180*math.pi)
				ef.campos.x -= ef.speed*math.cos(0.0+ef.laenge/180*math.pi)


			if keystring=='Right':
				ef.campos.y -= ef.speed*math.sin(0.0+ef.laenge/180*math.pi)
				ef.campos.x += ef.speed*math.cos(0.0+ef.laenge/180*math.pi)




		else:
			FreeCAD.Console.PrintError("no known mode -- no action")

		ef.compass.direction(ef.laenge)
		ef.horizon.direction(ef.roll)
		ef.horizon.setnick(ef.breite)


		r=1000
		pos3=FreeCAD.Vector(
				r*math.sin(ef.laenge/180*math.pi)*math.cos(ef.breite/180*math.pi),
				r*math.cos(ef.laenge/180*math.pi)*math.cos(ef.breite/180*math.pi),
				r*math.sin(ef.breite/180*math.pi))

		dir=FreeCAD.Vector(pos3)
		dir.normalize()
		
		print(ef.direction)
		print("ef.campos", ef.campos)
		ef.map.setPos(ef.campos.x,ef.campos.y,ef.campos.z)


		spos=FreeCAD.Vector(ef.campos)
		d=200
		prpos=FreeCAD.Vector(d*dir.x,d*dir.y,d*dir.z)
		ppos=spos.add(prpos)
		
		# kamera position
		camera.position.setValue(ef.campos) 
		camera.pointAt(coin.SbVec3f(ppos),coin.SbVec3f(0,0.0+math.sin(math.pi*ef.roll/180),0.0+math.cos(math.pi*ef.roll/180)))
		print("Roll ", ef.roll)

#		#hud
#		panel.Placement.Base=ppos
#		panel.Placement.Rotation=FreeCAD.Rotation(ef.laenge,-ef.breite,0)
#		#drehung des kompass/horizonts
#		s.Placement.Rotation=FreeCAD.Rotation(-ef.laenge-90,0,ef.breite)


		#
		# kamera einstellungen
		#

		if keystring=='F9':
			a=camera.heightAngle.getValue()
			a += 0.01
			camera.heightAngle.setValue(a)
		if keystring=='F10':
			a=camera.heightAngle.getValue()
			a -= 0.01
			camera.heightAngle.setValue(a)

		if keystring=='F11':
			camera.heightAngle.setValue(0.785398185253)
			
		if keystring=='F5':
			nD=camera.nearDistance.getValue()
			nD *=1.03
			print("near Distance",nD)
			camera.nearDistance.setValue(nD)

		if keystring=='F6':
			nD=camera.nearDistance.getValue()
			nD /=1.03
			if nD >0:
				print("near Distance",nD)
				camera.nearDistance.setValue(nD)

		if keystring=='F2':
			fn=os.path.dirname(__file__) +"/pics//P1170437.JPG"
			ef.tex.filename = fn

		if keystring=='F3':
			fn=os.path.dirname(__file__) +"/pics/P1170039.JPG"
			ef.tex.filename = fn

		if keystring=='F4':
			fn=os.path.dirname(__file__) +"/pics/winter.jpg"
			ef.tex.filename = fn


		#
		# ausgabe daten
		#
		
		if 1 or keystring=='F2':
			t=FreeCAD.Vector(prpos)
			try:
				t.normalize()
			except Exception:
				pass
			
			
			campos2=(round(ef.campos[0]),round(ef.campos[1]),round(ef.campos[2]))
			nD=camera.nearDistance.getValue()
			a=camera.heightAngle.getValue()

			out=''
			out += "camera position " + str(campos2) +"\n"
			out += "camera direction  " + str([round(t.x,2),round(t.y,2),round(t.z,2)]) + "\n"
			
			out += "speed " + str(ef.speed) +"\n"
			out += "dir " + str(round(ef.direction*180/math.pi)) +"\n"
			out += '\n'
			out += "height Angle      " + str(round(a/math.pi*180)) +'\n'
			out += "focal length " + str(round(10/math.tan(a/2)))+"\n"
			out += "near Distance     " + str(round(nD)) + '\n'
			
			print(out)
			
			
			
			ef.navi.output.setText(out)

		FreeCAD.ActiveDocument.recompute()
		FreeCADGui.updateGui() 

		if keystring=='Escape':
			print("stoppe eventserver ...")
			stop()
			sg = FreeCADGui.ActiveDocument.ActiveView.getSceneGraph()
			
			ef.output.deleteLater()
			ef.navi.deleteLater()
			sg.removeChild(ef.background)
	except Exception:
		sayexc()
		stop()
	return True

def on_move(ef,globalVector,localVector):
	return True

def on_move2(ef,globalVector,localVector):
	if ef.mouseMode:
		d=3
		if ef.v:
			if ef.v[0]>globalVector[0]+d:
				ef.on_key_press(ef,"Left")
			elif ef.v[0]<globalVector[0]-d:
				ef.on_key_press(ef,"Right")
			if ef.v[1]>globalVector[1]+d:
				ef.on_key_press(ef,"Up")
			elif ef.v[1]<globalVector[1]-d:
				ef.on_key_press(ef,"Down")
		ef.v=globalVector

	return True

## click callback for debug 
def on_clicks(ef,button,count):
	print("on clicks 3",button)
	print(ef.windowlist)
	try: 
		if ef.windowlist[0][1]=='Testme':
			print("call HUHU")
			return False
	except Exception:
		return True


# The EventFilter controls the Qt mouse and keyboard events
class EventFilter(QtCore.QObject):

	def __init__(self):
		QtCore.QObject.__init__(self)
		self.lastpos=QtCore.QPoint(0,0)
		self.on_key_press=on_key_press
		self.on_key_release=on_key_release
		self.on_move=on_move
		self.on_clicks=on_clicks
		self.on_windowslist=on_windowslist
		self.keyTimeout=0.1
		self.keyset=0
		self.keyPressed2=False
		self.output=myDebugWidget()

		self.compass = Compass()
		self.horizon = Horizon()
		self.map = Map()
		
		self.laenge=0.0
		self.breite=0.0
		self.campos=FreeCAD.Vector( 0, 0, 20000)
		#self.output.hide()

		self.mouseMode=False
		self.firstCall=True

		self.mode="turn"

		self.speed=100
		self.direction=0.5*math.pi
		self.roll=0

		self.keymap={}
		for t in dir(QtCore.Qt):
			if t.startswith( 'Key_' ):
				v=eval('QtCore.Qt.'+t)
				self.keymap[v]=t[4:]

		self.modmap={}
		for t in dir(QtCore.Qt):
			if t.endswith('Modifier'):
				if t!= 'Modifier':
					v=eval('QtCore.Qt.'+t)
					self.modmap[v]=t[:-8]

	## the event handler 
	def eventFilter(self, o, e):

		z=str(e.type())

		# not used events
		if z == 'PySide.QtCore.QEvent.Type.ChildAdded' or \
					z == 'PySide.QtCore.QEvent.Type.ChildRemoved'or \
					z == 'PySide.QtCore.QEvent.Type.User'  or \
					z == 'PySide.QtCore.QEvent.Type.Paint' or \
					z == 'PySide.QtCore.QEvent.Type.LayoutRequest' or\
					z == 'PySide.QtCore.QEvent.Type.UpdateRequest'   :
			return QtGui.QWidget.eventFilter(self, o, e)

		if z == 'PySide.QtCore.QEvent.Type.KeyPress':
			if time.time()-self.keyset<self.keyTimeout:
				return True
			self.keyPressed2=True
			self.keyset=time.time()
			ks=''
			for k in self.modmap:
				if e.modifiers() & k:
					ks += self.modmap[k] + '-'
			if not self.keymap[e.key()] in ['Shift','Meta','Alt','Control','GroupSwitch']:
				ks +=self.keymap[e.key()]
			self.output.vmap['key'].setText(ks)
			return self.on_key_press(self,ks)

		# end of a single key pressed
		if z == 'PySide.QtCore.QEvent.Type.KeyRelease':
			if self.keyPressed2:
				self.keyPressed2=False
				self.keyset=0
			ks=''
			for k in self.modmap:
				if e.modifiers() & k:
					ks += self.modmap[k] + '-'
			ks +=self.keymap[e.key()]
			self.output.vmap['key'].setText(ks)
			return self.on_key_release(self,ks)

		# enter and leave a widget 
		if z == 'PySide.QtCore.QEvent.Type.Enter' or z == 'PySide.QtCore.QEvent.Type.Leave':
			#FreeCAD.Console.PrintMessage("Enter Leave\n")
			return True

		if z == 'PySide.QtCore.QEvent.Type.HoverMove' :
			try: za=int(self.output.vmap['za'].text())
			except Exception: za=0
			za2=za
			self.output.vmap['xa'].setText(str(e.pos().x()))
			self.output.vmap['ya'].setText(str(e.pos().y()))
			#return self.on_move(self,[e.pos().x(),e.pos().y(),za2],[99,99,99])
			return self.on_move(self,[e.pos().x(),e.pos().y(),za2],[e.pos().x(),e.pos().y(),0])

		try:
			if e.type() == QtCore.QEvent.ContextMenu and o.__class__ == QtGui.QWidget:
				return True

			# wheel rotation
			if e.type()== QtCore.QEvent.Type.Wheel:
				# http://doc.qt.io/qt-4.8/qwheelevent.html

				self.output.vmap['xr'].setText(str(e.x()))
				self.output.vmap['yr'].setText(str(e.y()))
				self.output.vmap['zr'].setText(str(e.delta()))

				self.output.vmap['xa'].setText(str(e.globalX()))
				self.output.vmap['ya'].setText(str(e.globalY()))

				try: za=int(self.output.vmap['za'].text())
				except Exception: za=0
				za2=za+int(e.delta())
				self.output.vmap['za'].setText(str(za2))
				return self.on_move(self,[e.globalX(),e.globalY(),za2],[e.x(),e.y(),e.delta()] )

			# mouse clicks
			if e.type() == QtCore.QEvent.MouseButtonPress or \
					e.type() == QtCore.QEvent.MouseButtonRelease or\
					e.type() == QtCore.QEvent.MouseButtonDblClick:

				windowlist=[]
				myclass=o.__class__.__name__ 
				try: 
					mytext=o.text()
				except Exception: 
					mytext="???"
				if myclass=='QTabBar':
					windowlist.append([myclass,str(o.tabText(o.currentIndex())),o.currentIndex()])
				else:
					windowlist.append([myclass,str(mytext)])

				self.output.vmap['dxw'].setText(str(o.width()))
				self.output.vmap['dyw'].setText(str(o.height()))

				widget = QtGui.QApplication.widgetAt(self.lastpos)
				if widget:
					while widget:
						try:
							p=widget
							if p.__class__.__name__ =='QMdiSubWindow':
								widget=None
							label='???'
							try: 
								label2=p.objectName()
								if label2!='': label=label2
							except Exception: pass
							try: 
								label2=p.windowTitle()
								if label2!='': label=label2
							except Exception: pass
							try: 
								label2=p.tabText()
								if label2!='': label=label2
							except Exception: pass
							windowlist.append([p.__class__.__name__ ,str(label)])
							p=widget.parent()
							widget=p
						except Exception:
							widget=None

				stack=''
				for t in windowlist:
					stack += str(t)+"\n"
				self.output.vmap['xr'].setText(str(e.pos().x()))
				self.output.vmap['yr'].setText(str(e.pos().y()))
				self.output.vmap['windows'].setText(stack)
				
				self.windowlist=windowlist
				self.on_windowslist(self,windowlist)

				if e.type() == QtCore.QEvent.MouseButtonRelease:
					self.output.vmap['clickcount'].setText('release')
					return self.on_clicks(self,'Release',0)

				# double clicked
				if e.type() == QtCore.QEvent.MouseButtonDblClick and e.button() == QtCore.Qt.LeftButton:
					self.output.vmap['click'].setText('left')
					self.output.vmap['clickcount'].setText('2')
					return True

				if e.type() == QtCore.QEvent.MouseButtonDblClick and e.button() == QtCore.Qt.RightButton:
					self.output.vmap['click'].setText('right')
					self.output.vmap['clickcount'].setText('2')
					return True

				if e.type() == QtCore.QEvent.MouseButtonDblClick and e.button() == QtCore.Qt.MiddleButton:
					self.output.vmap['click'].setText('middle')
					self.output.vmap['clickcount'].setText('2')
					return True

				# middle
				if e.button() == QtCore.Qt.MidButton or  e.button() == QtCore.Qt.MiddleButton:
					self.output.vmap['click'].setText('middle')
					self.output.vmap['clickcount'].setText('1')
					return True

				if e.button() == QtCore.Qt.LeftButton:
					FreeCAD.Console.PrintMessage('!Mouse one left\n')
					self.output.vmap['click'].setText('left')
					self.output.vmap['clickcount'].setText('1')
					return self.on_clicks(self,'Left',1)

				# right mouse button when context menu deactivated
				elif e.button() == QtCore.Qt.RightButton:
					self.output.vmap['click'].setText('right')
					self.output.vmap['clickcount'].setText('1')
					return self.on_clicks(self,'Right',1)

		except Exception:
			sayexc()
		return False


# stop and delete the EventFilter
def stop():
	mw=QtGui.qApp
	ef=FreeCAD.eventfilter
	mw.removeEventFilter(ef)
	#mw.setOverrideCursor(QtCore.Qt.ArrowCursor)
	sg = FreeCADGui.ActiveDocument.ActiveView.getSceneGraph()
	
	ef.output.deleteLater()
	ef.navi.deleteLater()
	sg.removeChild(ef.background)


## a widget to display the yaw direction inside a circle
class Compass(QtGui.QWidget):
	#\cond
	def __init__(self):
		super(Compass, self).__init__()
		self.rect= (0, 0, 100, 100)
		self.arc=90
		self.resize(150, 150)
		#self.update()
		#self.initUI()
		
	def initUI(self):      
		self.setGeometry(300, 300, 350, 100)
		self.setWindowTitle('Colors')
		#self.show()

	def paintEvent(self, e):

		qp = QtGui.QPainter()
		qp.begin(self)
		self.drawRectangles(qp)
		qp.end()
		
	def drawRectangles(self, qp):
		color = QtGui.QColor(0, 0, 0)
		color.setNamedColor('#d4d4d4')
		qp.setPen(color)
		qp.setBrush(QtGui.QColor(100, 0, 0,50))
		qp.drawEllipse(0, 0, 100, 100);
		qp.save();
		qp.translate(50,50);
		qp.rotate(self.arc);
		qp.setBrush(QtGui.QColor(255, 0, 0, 255))
		qp.drawRect(0, -3, 50, 6);
		qp.restore();

	def direction(self,arc):
		self.arc=arc-90
		self.repaint()
	#\endcond


## a widget to display the pitch of the view
class Horizon(QtGui.QWidget):
	#\cond
	def __init__(self):
		super(Horizon, self).__init__()
		self.rect= (0, 0, 100, 100)
		self.arc=0
		self.nick=0
		self.resize(100, 100)

	def initUI(self):
		self.setGeometry(300, 300, 350, 100)
		self.setWindowTitle('Colors')

	def paintEvent(self, e):
		qp = QtGui.QPainter()
		qp.begin(self)
		self.drawRectangles(qp)
		qp.end()

	def drawRectangles(self, qp):
		color = QtGui.QColor(0, 0, 0)
		color.setNamedColor('#d4d4d4')
		qp.setBrush(QtGui.QColor(100, 100, 100, 255))
		qp.drawEllipse(0, 0, 100, 100);
		qp.setPen(color)
		qp.setBrush(QtGui.QColor(220, 220, 255,200))
		rect = QtCore.QRectF(0.0, 0.0, 100.0, 100.0)
		startAngle = (90+self.arc-0.5*self.nick) * 16
		spanAngle = (self.nick) * 16
		qp.drawChord(rect, startAngle, spanAngle)

	def direction(self,arc):
		self.arc=arc
		self.repaint()
	def setnick(self,n):
		self.nick=-n-180
		self.repaint()
	#\endcond


## a widget to display the xy position of the camera in the scene
class Map(QtGui.QWidget):

	def __init__(self):
		super(Map, self).__init__()
		self.rect= (0, 0, 100, 100)
		self.x=50
		self.y=50
		self.z=50
		self.resize(150, 140)
		#self.update()
		#self.initUI()
		
	def initUI(self):      
		self.setGeometry(300, 300, 350, 105)
		self.setWindowTitle('Colors')
		#self.show()

	def paintEvent(self, e):

		qp = QtGui.QPainter()
		qp.begin(self)
		self.drawRectangles(qp)
		qp.end()
		
	def drawRectangles(self, qp):
		color = QtGui.QColor(0, 0, 0)
		color.setNamedColor('#d4d4d4')
		qp.setPen(color)
		qp.setBrush(QtGui.QColor(100, 0, 0,50))
		qp.drawRect(0, 0, 105, 105);
		qp.save();
		qp.translate(self.x,self.y);
		qp.setBrush(QtGui.QColor(255, 0, 0, 255))
		qp.drawRect(0, 0, 5, 5);
#		qp.save();
		
		qp.translate(-self.x,-self.y+self.z);
		qp.setBrush(QtGui.QColor(255, 255, 0, 255))
		qp.drawRect(0, 0, 10, 5);
		qp.restore();
#		qp.restore();

	def setPos(self,x,y,z):
		fak=50.0
		self.z=-z/fak+50
		self.x=x/fak+50
		self.y=-y/fak+50
		print("setpos",x,y)
		self.repaint()
  
  

##creates and returns the navigator display widget


def myNavigatorWidget(ef):
	liste=QtGui.QWidget()
	liste.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
	layout=QtGui.QVBoxLayout()
	liste.setLayout(layout)
	liste.vmap={}

	liste2=QtGui.QWidget()
	layout2=QtGui.QHBoxLayout()
	liste2.setLayout(layout2)
	layout.addWidget(liste2)
	liste2.setMinimumHeight(130)
	liste2.setMinimumWidth(360)

	# compass
	layout2.addWidget(ef.compass)
	ef.compass.direction(-50)

	# horizon
	layout2.addWidget(ef.horizon)
	ef.horizon.setnick(100)
	ef.horizon.direction(20)

	# map
	layout2.addWidget(ef.map)
	ef.map.setPos(20,40,20)

	ll= QtGui.QLabel()
	ll.setText("Turn")
	layout.addWidget(ll)
	liste.modelabel=ll

	bt= QtGui.QPushButton()
	bt.setText("Walk Mode")
	layout.addWidget(bt)

	bt= QtGui.QPushButton()
	bt.setText("Frontal Mode")
	layout.addWidget(bt)

	bt= QtGui.QPushButton()
	bt.setText("Turn Mode")
	layout.addWidget(bt)

	line = QtGui.QTextEdit()
	line.setText("yyy")
	layout.addWidget(line)
	liste.output=line

	bt= QtGui.QPushButton()
	bt.setText("Stop Navigation")
	layout.addWidget(bt)

	bt= QtGui.QPushButton()
	bt.setText("Background 1 Snowland")
	layout.addWidget(bt)
	bt.clicked.connect(lambda:background1(ef)) 

	bt= QtGui.QPushButton()
	bt.setText("Background 2 Duneland")
	layout.addWidget(bt)
	bt.clicked.connect(lambda:background2(ef)) 


	bt= QtGui.QPushButton()
	bt.setText("Background 3 Cologne")
	layout.addWidget(bt)
	bt.clicked.connect(lambda:background3(ef)) 

	bt= QtGui.QPushButton()
	bt.setText("Background 4 Transparence")
	layout.addWidget(bt)
	bt.clicked.connect(lambda:background4(ef)) 

	liste.ef=ef
	liste.show()
	return liste

## background image winter
def background1(ef):
	fn=os.path.dirname(__file__) +"/pics/winter.jpg"
	ef.tex.filename = fn

## background image dune
def background2(ef):
	fn=os.path.dirname(__file__) +"/pics//P1170437.JPG"
	ef.tex.filename = fn

## background image city
def background3(ef):
	fn=os.path.dirname(__file__) +"/pics/P1170039.JPG"
	ef.tex.filename = fn


## background partially transparent
def background4(ef):
	fn=os.path.dirname(__file__) +"/pics/transpa.png"
	ef.tex.filename = fn

## callback to set the mode or to do some other useful things
def on_windowslist(ef,windowslist):
	for t in windowslist:
		if  t==['QPushButton','Stop Navigation']:
			stop()
			ef.output.deleteLater()
			ef.navi.deleteLater()
		if  t==['QPushButton','Walk Mode']:
			print("Walk mode")
			ef.mode="walk"
			ef.navi.modelabel.setText("Walk")
		if  t==['QPushButton','Frontal Mode']:
			print("Frontal mode")
			ef.mode="xyz"
			ef.navi.modelabel.setText("Frontal")
		if  t==['QPushButton','Turn Mode']:
			print("Turn mode")
			ef.mode="turn"
			ef.navi.modelabel.setText("Turn")
		return


## initialize and start the Eventfilter

def navi():
	'''navigator startup'''


	mw=QtGui.qApp
	#mw.setOverrideCursor(QtCore.Qt.PointingHandCursor)
	ef=EventFilter()
	ef.navi=myNavigatorWidget(ef)

	# get a jpg filename
	fn=os.path.dirname(__file__) +"/pics/transpa.jpg"

	sg = FreeCADGui.ActiveDocument.ActiveView.getSceneGraph()

	trans = coin.SoTranslation()
	trans.translation.setValue([0,0,0])
	myCustomNode = coin.SoSeparator()

	cub = coin.SoSphere()
	cub.radius.setValue(10000000)

	i=coin.SoRotationXYZ()
	i.angle.setValue(1.5708)
	i.axis.setValue(0)
	myCustomNode.addChild(i)

	s=coin.SoRotationXYZ()
	s.angle.setValue(math.pi)
	s.axis.setValue(1)
	myCustomNode.addChild(s)

	#myCustomNode.addChild(trans)
	myCustomNode.addChild(cub)
	sg.addChild(myCustomNode)

	tex =  coin.SoTexture2()
	tex.filename = fn
	myCustomNode.insertChild(tex,0)

	ef.background=myCustomNode
	ef.tex=tex

	FreeCAD.eventfilter=ef
	mw.installEventFilter(ef)

	on_key_press(FreeCAD.eventfilter,'O')

	view=FreeCADGui.activeDocument().activeView()

	FreeCADGui.ActiveDocument.ActiveView.setAnimationEnabled(False)
	mgr=view.getViewer().getSoRenderManager()
	mgr.setAutoClipping(0)
	FreeCAD.ActiveDocument.recompute()
	FreeCADGui.updateGui() 

	return ef

def runtest():
	navi()
	ef=navi()
	ef.navi.hide()
	ef.output.hide()

def Navigator():
	runtest()