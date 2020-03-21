# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- Animation workbench
#--
#-- microelly 2016
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------

import FreeCAD

import FreeCADGui
App=FreeCAD
Gui=FreeCADGui

import PySide
from PySide import QtCore, QtGui

import FreeCAD
import Draft, Part

import numpy as np


#import matplotlib
#import matplotlib.pyplot as plt
#from matplotlib.pyplot import cm 


import os,random,time,sys,traceback




def log(s):
	logon = False
	if logon:
		f = open('/tmp/log.txt', 'a')
		f.write(str(s) +'\n')
		f.close()

def sayd(s):
	if hasattr(FreeCAD,'animation_debug'):
		pass
		log(str(s))
		FreeCAD.Console.PrintMessage(str(s)+"\n")

def say(*s):
	log(str(s))
	if len(s)==1:FreeCAD.Console.PrintMessage(str(s[0]))
	elif len(s)==0:FreeCAD.Console.PrintMessage(str(s[0]))
	else:
		for aa in s:
			FreeCAD.Console.PrintMessage(str(aa)+' ')
	FreeCAD.Console.PrintMessage("\n")

def sayErr(s):
	log(str(s))
	FreeCAD.Console.PrintError(str(s)+"\n")


def sayW(s):
	log(str(s))
	FreeCAD.Console.PrintWarning(str(s)+"\n")


def errorDialog(msg):
    diag = QtGui.QMessageBox(QtGui.QMessageBox.Critical,u"Error Message",msg )
    diag.setWindowFlags(PySide.QtCore.Qt.WindowStaysOnTopHint)
    diag.exec_()


def sayexc(mess=''):
	exc_type, exc_value, exc_traceback = sys.exc_info()
	ttt=repr(traceback.format_exception(exc_type, exc_value,exc_traceback))
	lls=eval(ttt)
	l=len(lls)
	l2=lls[(l-3):]
	FreeCAD.Console.PrintError(mess + "\n" +"-->  ".join(l2))
