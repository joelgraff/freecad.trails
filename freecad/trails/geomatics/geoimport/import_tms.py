# -*- coding: utf8 -*-
#***************************************************************************
#*   Copyright (c) 2021 Maarten Vroegindeweij <maarten@3bm.co.nl>              *
#*                                                                         *
#*   This program is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU Lesser General Public License (LGPL)    *
#*   as published by the Free Software Foundation; either version 2 of     *
#*   the License, or (at your option) any later version.                   *
#*   for detail see the LICENCE text file.                                 *
#*                                                                         *
#*   This program is distributed in the hope that it will be useful,       *
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of        *
#*   MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
#*   GNU Library General Public License for more details.                  *
#*                                                                         *
#*   You should have received a copy of the GNU Library General Public     *
#*   License along with this program; if not, write to the Free Software   *
#*   Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
#*   USA                                                                   *
#*                                                                         *
#***************************************************************************

"""This module provides tools to load GIS information into FreeCAD
"""

__title__= "GIS2BIM_FreeCAD_import_tms"
__author__ = "Maarten Vroegindeweij"
__url__ = "https://github.com/DutchSailor/GIS2BIM"
# TMS Importer

from PySide2 import QtCore, QtWidgets
from PySide2.QtGui import*

import FreeCAD

import GIS2BIM
import GIS2BIM_FreeCAD

class GIS_TMS_Dialog(QtWidgets.QDialog):

	def __init__(self):
		super(GIS_TMS_Dialog, self).__init__()
		self.sitename = "GIS-Sitedata"
		self.tempFolderName = "GIStemp/"
		self.lat = float(GIS2BIM_FreeCAD.ArchSiteCreateCheck(self.sitename).WGS84_Latitude)
		self.lon = float(GIS2BIM_FreeCAD.ArchSiteCreateCheck(self.sitename).WGS84_Longitude)
		self.bboxWidth = float(GIS2BIM_FreeCAD.ArchSiteCreateCheck(self.sitename).BoundingboxWidth)
		self.bboxHeight = float(GIS2BIM_FreeCAD.ArchSiteCreateCheck(self.sitename).BoundingboxHeight)
		self.tempFolder = GIS2BIM_FreeCAD.CreateTempFolder(self.tempFolderName)
		self.tempFileName = self.tempFolder + "initialTMS.jpg" 
		
		self.zoomL = 17
		self.pixels = 256
		self.TMS_WMTS = 0
		
		#Download list of predefined WMTS/TMS Requests
		category = "webserverRequests"
		service = "WMTS_TMS"
		data = GIS2BIM.GetWebServerDataService(category,service)
		
		TitleList  = []
		for i in data:
			TitleList.append(i["title"])
		
		ServerRequestPrefix  = []
		for i in data:
			ServerRequestPrefix.append(i["serverrequestprefix"])
		yx = sorted(zip(TitleList,ServerRequestPrefix))
		self.TitleList = [x[0] for x in yx]
		self.ServerRequestPrefix = [x[1] for x in yx]		
		self.initUI()
		
	def initUI(self):
		self.result = userCancelled
		self.setWindowTitle("Load Raster Data with TMS(Tile Map Service)")
		self.setGeometry(50, 50, 920, 910)
		self.setFixedSize(self.size())
		
		self.centralwidget = QtWidgets.QWidget(self)
		self.centralwidget.setObjectName("WMTS")
		self.pictlabel = QtWidgets.QLabel(self)
		self.zoomLevel = self.zoomL

		# dx 
		self.dx = QtWidgets.QLineEdit(self)
		self.dx.setInputMask("")
		self.dx.setText("0")
		self.dx.setFixedWidth(100)
		self.dx.move(200, 790)
		self.label6 = QtWidgets.QLabel("X-Placement from origin[m]", self)
		self.label6.move(40, 795)

		# dy 
		self.dy = QtWidgets.QLineEdit(self)
		self.dy.setInputMask("")
		self.dy.setText("0")
		self.dy.setFixedWidth(100)
		self.dy.move(200, 820)
		self.label7 = QtWidgets.QLabel("Y-Placement from origin[m]", self)
		self.label7.move(40, 825)

		#Name of Image
		self.imageName = QtWidgets.QLineEdit(self)
		self.imageName.setInputMask("")
		self.imageName.setText(self.TitleList[0])
		self.imageName.setFixedWidth(100)
		self.imageName.move(200, 730)
		self.imageNameLabel = QtWidgets.QLabel("Image Name", self)
		self.imageNameLabel.move(40, 735)
		self.imageName.editingFinished.connect(self.onimageName)

		#Zoomlevel
		self.zoomLevel = QtWidgets.QLineEdit(self)
		self.zoomLevel.setText("18")
		self.zoomLevel.setFixedWidth(100)
		self.zoomLevel.move(520, 730)
		self.zoomLevelLab = QtWidgets.QLabel("Zoom Level(1-18)", self)
		self.zoomLevelLab.move(350, 735)

		#Filelocation 
		self.filelocation = self.tempFileName
		self.foldername = self.tempFolder
		def do_file():
			self.fname = QtWidgets.QFileDialog.getExistingDirectory(self, "Open Directory",self.tempFolder,QtWidgets.QFileDialog.ShowDirsOnly | QtWidgets.QFileDialog.DontResolveSymlinks)
			self.foldername = fname	
			self.filelocation = self.foldername + "/" + self.imageName.text() + ".jpg"
		self.button = QtWidgets.QPushButton("Browse",self)
		self.button.clicked.connect(do_file)
		self.button.show()
		self.button.move(195, 755)
		self.label8 = QtWidgets.QLabel("Folder for temporary files", self)
		self.label8.move(40, 765)

		# combobox with WMTS-servers
		self.cbo = QtWidgets.QComboBox(self)
		self.cbo.autoCompletion()
		self.cbo.move(520,760)
		self.cbo.addItems(self.TitleList)
		self.labelWMS = QtWidgets.QLabel("Predifined TMS Requests", self)
		self.labelWMS.move(350, 765)
		self.cbo.currentIndexChanged.connect(self.selectionchange)
		
		# webservernameAndRequest
		self.webserverName1 = QtWidgets.QPlainTextEdit(self)
		self.webserverName1.insertPlainText(self.ServerRequestPrefix[0])
		self.webserverName1.setFixedWidth(300)
		self.webserverName1.setFixedHeight(80)
		self.webserverName1.move(515, 790)
		self.label1 = QtWidgets.QLabel("TMS Webserver ", self)
		self.label1.move(350, 795)

		# test TMS button
		testTMSButton = QtWidgets.QPushButton('Test TMS-request and show result', self)
		testTMSButton.clicked.connect(self.test_TMS)
		testTMSButton.move(280, 870)

		# cancel button
		cancelButton = QtWidgets.QPushButton('Cancel', self)
		cancelButton.clicked.connect(self.onCancel)
		cancelButton.setAutoDefault(True)
		cancelButton.move(190, 870)

		# Ok TMS button
		okButton = QtWidgets.QPushButton('OK and import image', self)
		okButton.clicked.connect(self.onOk)
		okButton.move(35, 870)
		self.show()
		if self.bboxWidth > 1000 or self.bboxHeight > 1000:
			dialog = QtWidgets.QMessageBox()
			dialog.setText("Boundingbox is larger then 1000 meters. Set zoomlevel far lower then 18 to prevent extreem large imagefiles")
			dialog.setWindowTitle("Warning")
			dialog.exec_() 
		else: self.test_TMS()

	def onCancel(self):
		self.result= userCancelled
		self.close()
	
	def onimageName(self): 
		self.filelocation = self.foldername + "/" + self.imageName.text() + ".jpg"

	def selectionchange(self): 
		self.webserverName1.clear()		
		self.webserverName1.insertPlainText(self.ServerRequestPrefix[self.cbo.currentIndex()])
		self.imageName.clear()
		self.imageName.setText(self.cbo.currentText())

	def test_TMS(self):
		self.ServerName = self.webserverName1.toPlainText()
		TMS = GIS2BIM.TMS_WMTSCombinedMapFromLatLonBbox(self.lat,self.lon,self.bboxWidth,self.bboxHeight,int(self.zoomLevel.text()),self.pixels,self.TMS_WMTS,self.ServerName)
		self.filelocation = self.foldername + "/" + self.imageName.text() + ".jpg"		
		TMS[0].save(self.filelocation)		
		picture = QPixmap(self.filelocation)
		picture = picture.scaledToWidth(800)
		pictheight = picture.height()
		if pictheight > 700:
			scale = 700/pictheight
			pictheight = 700
			pictwidth = 800*scale
			picture = picture.scaledToWidth(pictwidth)
		else:
			pictwidth = 800			
			picture = picture.scaledToWidth(pictwidth)
		self.pictlabel.setPixmap(picture)
		self.pictlabel.setGeometry(QtCore.QRect(40, 40, pictwidth-40, pictheight-40))
		self.pictlabel.hide()
		self.pictlabel.show()
		self.result= userTest

	def onOk(self):
		self.result= userOK
		dx = float(self.dx.text())*1000
		dy = float(self.dy.text())*1000
		fileLocationTMS = str(self.filelocation)
		TMS = GIS2BIM.TMS_WMTSCombinedMapFromLatLonBbox(self.lat,self.lon,self.bboxWidth,self.bboxHeight,int(self.zoomLevel.text()),self.pixels,self.TMS_WMTS,self.ServerName)
		TMS[0].save(fileLocationTMS)		
		ImageMap = GIS2BIM_FreeCAD.ImportImage(fileLocationTMS,self.bboxWidth,self.bboxHeight,1000, str(self.imageName.text()), dx,dy)
		GIS2BIM_FreeCAD.CreateLayer("GIS_Raster")
		FreeCAD.ActiveDocument.recompute()
		FreeCAD.activeDocument().getObject("GIS_Raster").addObject(FreeCAD.activeDocument().getObject(ImageMap.Label))
		FreeCAD.ActiveDocument.recompute()
		self.result= userOK
		self.close()

# Constant definitions
userCancelled = "Cancelled"
userOK = "OK"
userTest = "test_TMS"

#form = GIS_TMS_Dialog()
#form.exec_()