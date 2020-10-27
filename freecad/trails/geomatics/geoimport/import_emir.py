# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- geodat import emir
#--
#-- microelly 2018 v 0.1
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------

from .say import sayexc

import FreeCAD, FreeCADGui
App=FreeCAD
Gui=FreeCADGui

import numpy as np
data='''ncols        5
nrows        6
xllcorner    260.000000000000
yllcorner    120.000000000000
cellsize     10.000000000000
10 10 10 10 10 10 
10 11 12 13 10 10 
10 11 11 8 10 10 
10 11 11 9 10 10 
10 10 10 10 10 10
'''


def parsedata(lines):
	import Draft
	print(lines)
	dat={}
	a=lines[0].decode().split()
	dat[a[0]]=int(a[1])

	a=lines[1].decode().split()
	dat[a[0]]=int(a[1])

	a=lines[2].decode().split()
	dat[a[0]]=float(a[1])

	a=lines[3].decode().split()
	dat[a[0]]=float(a[1])

	a=lines[4].decode().split()
	dat[a[0]]=float(a[1])

	print(dat)

	a=[]
	for i in range(dat['ncols']):
		aa = lines[5+i].split()
		a += [(0,0,float(h)) for h in aa]

#	print(dat)

	a=np.array(a).reshape(dat['ncols'],dat['nrows'],3)
	cellsize=dat['cellsize']
	xllcorner=0
	yllcorner=0

	for i in range(dat['ncols']):
		a[i,:,0]=i*cellsize+xllcorner

	for i in range(dat['nrows']):
		a[:,i,1]=i*cellsize+yllcorner

	for i in range(dat['ncols']):
		Draft.makeBSpline([FreeCAD.Vector(p) for  p in a[i]])

	for i in range(dat['nrows']):
		Draft.makeBSpline([FreeCAD.Vector(p) for  p in a[:,i]])

	FreeCAD.ActiveDocument.recompute()

	return a


def	import_emir(
					filename,
					textdat=None,
					directText=False,
			):

	#lines=data.splitlines()
	if filename.startswith('UserAppData'):
		filename=filename.replace('UserAppData',FreeCAD.ConfigGet("UserAppData"))

	f=open(filename, 'rb')
	lines=f.readlines()
	parsedata(lines)

s6='''
MainWindow:
	VerticalLayout:
		id:'main'

		QtGui.QLabel:
			setText:"***   I M P O R T  EMIR   GEODATA   ***"
		QtGui.QLabel:

		QtGui.QLabel:
			setText:"Data input filename"

		QtGui.QLineEdit:
			setText:"UserAppData/Mod/geodat/testdata/emir.dat"
			id: 'bl'

		QtGui.QPushButton:
			setText: "Get File Name"
			clicked.connect: app.getfn

#		QtGui.QLabel:
#			setText:"direct Data input  "

#		QtGui.QTextEdit:
#			setText:""
#			id: 'data'

		QtGui.QPushButton:
			setText: "Run values"
			clicked.connect: app.run

'''

from PySide import QtGui

class MyApp(object):

	def run(self):
		filename=self.root.ids['bl'].text()
		try:
			import_emir(
					filename,
					#self.root.ids['data'].text(),
					#self.root.ids['data'].toPlainText(),
			)
		except Exception:
				sayexc()

	def getfn(self):
		fileName = QtGui.QFileDialog.getOpenFileName(None,u"Open File",u"/tmp/")
		print(fileName)
		s=self.root.ids['bl']
		s.setText(fileName[0])


def mydialog():
	app=MyApp()

	from . import miki

	miki=miki.Miki()
	miki.app=app
	app.root=miki

	miki.parse2(s6)
	miki.run(s6)
	return miki


# mydialog()



def runtest():
	m=mydialog()
	m.objects[0].hide()



def importEMIR():
	mydialog()
