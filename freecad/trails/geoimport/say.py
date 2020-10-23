# -*- coding: utf-8 -*-
#-------------------------------------------------
#-- Animation workbench
#--
#-- microelly 2016
#--
#-- GNU Lesser General Public License (LGPL)
#-------------------------------------------------

import FreeCAD, FreeCADGui
App=FreeCAD
Gui=FreeCADGui

from PySide import QtCore, QtGui



#import matplotlib
#import matplotlib.pyplot as plt
#from matplotlib.pyplot import cm 


import sys,traceback

def sayd(s):
	if hasattr(FreeCAD,'animation_debug'):
		FreeCAD.Console.PrintMessage(str(s)+"\n")

def say(*s):
	if len(s)==1:FreeCAD.Console.PrintMessage(str(s[0]))
	elif len(s)==0:FreeCAD.Console.PrintMessage(str(s[0]))
	else:
		for aa in s:
			FreeCAD.Console.PrintMessage(str(aa)+' ')
	FreeCAD.Console.PrintMessage("\n")

def sayErr(s):
	FreeCAD.Console.PrintError(str(s)+"\n")


def sayW(s):
	FreeCAD.Console.PrintWarning(str(s)+"\n")


def errorDialog(msg):
    diag = QtGui.QMessageBox(QtGui.QMessageBox.Critical,u"Error Message",msg )
    diag.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
    diag.exec_()


def sayexc(mess=''):
	exc_type, exc_value, exc_traceback = sys.exc_info()
	ttt=repr(traceback.format_exception(exc_type, exc_value,exc_traceback))
	lls=eval(ttt)
	l=len(lls)
	l2=lls[(l-3):]
	FreeCAD.Console.PrintError(mess + "\n" +"-->  ".join(l2))
