# -*- coding: utf8 -*-
#***************************************************************************
#*   Copyright (c) 2021 Maarten Vroegindeweij <maarten@3bm.co.nl>          *
#*                                                                         *
#*   This program is free software; you can redistribute it and/or modify  *
#*   it under the terms of the GNU Lesser General Public License (LGPL)    *
#*   as published by the Free Software Foundation; either version 2 of     *
#*   the License, or (at your option) any later version.                   *
#*   for detail see the LICENCE text file.                                 *
#*                                                                         *
#*   This program is distributed in the hope that it will be useful,       *
#*   but WITHOUT ANY WARRANTY; without even the implied warranty of			*
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
from PIL import Image, ImageOps

import FreeCAD

from PyPackages import GIS2BIM
from PyPackages import GIS2BIM_FreeCAD
from PyPackages import GIS2BIM_GUI

class GIS_TMS_Dialog(QtWidgets.QDialog):

	def __init__(self):
		super(GIS_TMS_Dialog, self).__init__()

		#Get/set parameters for GIS		
		self.sitename = "GIS-Sitedata"
		self.tempFolderName = "GIStemp/"
		self.X = str(GIS2BIM_FreeCAD.ArchSiteCreateCheck(self.sitename).CRS_x)
		self.Y = str(GIS2BIM_FreeCAD.ArchSiteCreateCheck(self.sitename).CRS_y)
		self.lat = str(GIS2BIM_FreeCAD.ArchSiteCreateCheck(self.sitename).WGS84_Latitude)
		self.lon = str(GIS2BIM_FreeCAD.ArchSiteCreateCheck(self.sitename).WGS84_Longitude)
		self.CRS = str(GIS2BIM_FreeCAD.ArchSiteCreateCheck(self.sitename).CRS_EPSG_SRID)
		self.CRSDescription = str(GIS2BIM_FreeCAD.ArchSiteCreateCheck(self.sitename).CRS_EPSG_Description)
		self.bboxWidthStart = str(GIS2BIM_FreeCAD.ArchSiteCreateCheck(self.sitename).BoundingboxWidth)
		self.bboxHeightStart = str(GIS2BIM_FreeCAD.ArchSiteCreateCheck(self.sitename).BoundingboxHeight)
		self.width = float(self.bboxWidthStart)
		self.height = float(self.bboxHeightStart)
		self.tempFolder = GIS2BIM_FreeCAD.CreateTempFolder(self.tempFolderName)
		self.folderName = self.tempFolder
		self.tempFileName = self.tempFolder + "initialTMS.jpg" 

		self.zoomL = 17
		self.pixels = 256
		self.TMS_WMTS = 0

		#Set Style
		self.setStyleSheet("QWidget {background-color: rgb(68, 68, 68)} QPushButton { background-color: black } QGroupBox {border: 1px solid grey; }") #margin: 2px;

		#Download list of predefined TMS Requests
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
		
		#Widget Right Bottom Combined
		gridRB = QtWidgets.QGridLayout()
		gridRB.addWidget(self.webserverGroup(), 0, 0, QtCore.Qt.AlignTop)
		gridRB.addWidget(self.freeCADGroup(), 1, 0, QtCore.Qt.AlignTop)
		
		#Overall Grid
		grid = QtWidgets.QGridLayout()
		grid.addWidget(self.imageGroup(), 0, 0, 1, 2)
		grid.addWidget(self.locationGroup(), 3, 0, QtCore.Qt.AlignTop)	
		grid.addLayout(gridRB, 3, 1)
		grid.addLayout(self.buttonGroup(),4,0,1,2)
		grid.setRowStretch(0,2)
		self.setLayout(grid)
		
		self.setWindowTitle("Load Raster Data with TMS(Tile Map Server)")
		self.resize(920, 910)
		self.onTest()
		
	def locationGroup(self):
		groupBoxx = GIS2BIM_GUI.locationGroup(self)
		return groupBoxx

	def freeCADGroup(self):
		groupBox = QtWidgets.QGroupBox("FreeCAD Import Settings")
		
		#Name of Image
		imageNameLab = QtWidgets.QLabel("Image Name", self)
		self.imageName= QtWidgets.QLineEdit(self)		
		self.imageName.setText(self.TitleList[0])
		self.imageName.editingFinished.connect(self.onimageName)
		
		# checkbox halftone
		cbGrayscaleLab = QtWidgets.QLabel("Image Grayscale")
		self.cbGrayscale = QtWidgets.QCheckBox()
		self.cbGrayscale.setChecked(0)

		#dx
		dxLab = QtWidgets.QLabel("X-Placement from origin[m]", self)
		self.dx= QtWidgets.QLineEdit(self)		
		self.dx.setText("0")

		#dy
		dyLab = QtWidgets.QLabel("Y-Placement from origin[m]", self)
		self.dy= QtWidgets.QLineEdit(self)		
		self.dy.setText("0")

		grid = QtWidgets.QGridLayout()
		grid.addWidget(imageNameLab,0,0)
		grid.addWidget(self.imageName,0,1)
		grid.addWidget(cbGrayscaleLab,0,2)
		grid.addWidget(self.cbGrayscale,0,3)
		grid.addWidget(dxLab,1,0)
		grid.addWidget(self.dx,1,1)
		grid.addWidget(dyLab,1,2)
		grid.addWidget(self.dy,1,3)
		groupBox.setLayout(grid)
		return groupBox
	
	def webserverGroup(self):
		groupBox = QtWidgets.QGroupBox("Input Webserver / Request")

		# combobox with TMS-servers
		cboDefTMSLab = QtWidgets.QLabel("Predifined TMS Requests", self)		
		self.cboDefTMS = QtWidgets.QComboBox(self)
		self.cboDefTMS.addItems(self.TitleList)
		self.cboDefTMS.currentIndexChanged.connect(self.selectionchange)
		
		#Zoom Level 
		zoomLevelLab = QtWidgets.QLabel("Zoomlevel (1-18)", self)
		self.zoomLevel= QtWidgets.QLineEdit(self)		
		self.zoomLevel.setText(str(self.zoomL))

		# Webrequest text
		requestLab = QtWidgets.QLabel("Webserver URL", self)
		self.request= QtWidgets.QLineEdit(self)		
		self.request.setText(self.ServerRequestPrefix[self.cboDefTMS.currentIndex()])

		grid = QtWidgets.QGridLayout()
		grid.addWidget(cboDefTMSLab,0,0)
		grid.addWidget(self.cboDefTMS,0,1)
		grid.addWidget(requestLab,1,0)
		grid.addWidget(self.request,1,1)
		grid.addWidget(zoomLevelLab,2,0)
		grid.addWidget(self.zoomLevel,2,1)
		grid.setRowStretch(1,1)

		groupBox.setLayout(grid)
		
		return groupBox

	def imageGroup(self):
		groupBox = QtWidgets.QGroupBox("Example: Note: Use 'Geographic Location' to obtain CRS and coordinates from map")
		
		self.pictlabel = QtWidgets.QLabel(self)
		grid = QtWidgets.QGridLayout()
		grid.addWidget(self.pictlabel,0,0)

		groupBox.setLayout(grid)
		
		return groupBox

	def buttonGroup(self):
		hbox = GIS2BIM_GUI.buttonGroup(self)
		return hbox
			
	def onimageName(self): 
		self.filelocation = self.folderName + "/" + self.imageName.text() + ".jpg"

	def selectionchange(self): 
		self.request.clear()		
		self.request.setText(self.ServerRequestPrefix[self.cboDefTMS.currentIndex()])
		self.imageName.clear()
		self.imageName.setText(self.cboDefTMS.currentText())

	def onbboxHeight(self):
		test = "test"

	def onbboxWidth(self):
		test = "test"

	def onTest(self):
		self.ServerName = self.request.text()		
		TMS = GIS2BIM.TMS_WMTSCombinedMapFromLatLonBbox(float(self.lat),float(self.lon),float(self.bboxWidth.text()),float(self.bboxHeight.text()),int(self.zoomLevel.text()),self.pixels,self.TMS_WMTS,self.ServerName)
		fileLocationTMS = self.tempFolder + self.imageName.text() + '.jpg'
		TMS[0].save(fileLocationTMS)
		if self.cbGrayscale.checkState():
			img = Image.open(fileLocationTMS)
			fileLocationTMS2 = self.tempFolder + self.imageName.text() + '_gray.jpg'
			gray_image = ImageOps.grayscale(img)
			gray_image.save(fileLocationTMS2)
		else: fileLocationTMS2 = fileLocationTMS
		picture = QPixmap(fileLocationTMS2)
		picture = picture.scaledToWidth(800)
		pictheight = picture.height()
		if pictheight > 600:
			scale = 600/pictheight
			pictheight = 600
			pictwidth = 800*scale
			picture = picture.scaledToWidth(pictwidth)
		else:
			pictwidth = 800			
			picture = picture.scaledToWidth(pictwidth)
		self.pictlabel.setPixmap(picture)
		self.pictlabel.setGeometry(QtCore.QRect(40, 40, pictwidth-40, pictheight-40))
		self.pictlabel.hide()
		self.pictlabel.show()

	def onImport(self):
		width = float(self.bboxWidth.text())
		height = float(self.bboxHeight.text())
		if width > 1000 or height > 1000 and int(self.zoomLevel.text()) >17:
			dialog = QtWidgets.QMessageBox()
			dialog.setText("Boundingbox is larger then 1000 meters. Set zoomlevel lower then 18 to prevent extreem large imagefiles")
			dialog.setWindowTitle("Warning")
			dialog.exec_() 
		else: test = "test"
		dx = float(self.dx.text())*1000
		dy = float(self.dy.text())*1000
		fileLocationTMS = self.tempFolder + self.imageName.text() + '.jpg'
		TMS = GIS2BIM.TMS_WMTSCombinedMapFromLatLonBbox(float(self.lat),float(self.lon),float(self.bboxWidth.text()),float(self.bboxHeight.text()),int(self.zoomLevel.text()),self.pixels,self.TMS_WMTS,self.ServerName)
		TMS[0].save(fileLocationTMS)
		if self.cbGrayscale.checkState():
			img = Image.open(fileLocationTMS)
			fileLocationTMS2 = self.tempFolder + self.imageName.text() + '_gray.jpg'
			gray_image = ImageOps.grayscale(img)
			gray_image.save(fileLocationTMS2)
		else: fileLocationTMS2 = fileLocationTMS
		ImageMap = GIS2BIM_FreeCAD.ImportImage(fileLocationTMS2,float(self.bboxWidth.text()),float(self.bboxHeight.text()),1000, str(self.imageName.text()), dx,dy)
		GIS2BIM_FreeCAD.CreateLayer("GIS_Raster")
		FreeCAD.ActiveDocument.recompute()
		FreeCAD.activeDocument().getObject("GIS_Raster").addObject(FreeCAD.activeDocument().getObject(ImageMap.Label))
		FreeCAD.ActiveDocument.recompute()
		self.close()

	def onCancel(self):
		self.close()

#form = GIS_TMS_Dialog()
#form.exec_()