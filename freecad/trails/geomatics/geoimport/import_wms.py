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

__title__= "GIS2BIM_FreeCAD_import_wms"
__author__ = "Maarten Vroegindeweij"
__url__ = "https://github.com/DutchSailor/GIS2BIM"

# WMS Importer

from PySide2 import QtCore, QtWidgets
from PySide2.QtGui import*
from PIL import Image, ImageOps

import FreeCAD

from PyPackages import GIS2BIM
from PyPackages import GIS2BIM_FreeCAD
from PyPackages import GIS2BIM_GUI

class GISWMS_Dialog(QtWidgets.QDialog):

	def __init__(self):
		super(GISWMS_Dialog, self).__init__()

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
		self.tempFileName = self.tempFolder + "initialWMS.jpg" 
		
		#Set Style
		self.setStyleSheet("QWidget {background-color: rgb(68, 68, 68)} QPushButton { background-color: black } QGroupBox {border: 1px solid grey; }") #margin: 2px;

		#Download list of predefined WMS Requests
		category = "webserverRequests"
		service = "WMS"
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
		
		self.setWindowTitle("Load Raster Data with WMS(Web Map Server)")
		self.resize(920, 910)
		
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

		#Pixel Width
		pixelwidthLab = QtWidgets.QLabel("Pixels(width)", self)
		self.pixelwidth= QtWidgets.QLineEdit(self)		
		self.pixelwidth.setText("3000")
		
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
		grid.addWidget(self.imageName,0,1,1,2)
		grid.addWidget(pixelwidthLab,1,0)
		grid.addWidget(self.pixelwidth,1,1)
		grid.addWidget(cbGrayscaleLab,1,2)
		grid.addWidget(self.cbGrayscale,1,3)
		grid.addWidget(dxLab,2,0)
		grid.addWidget(self.dx,2,1)
		grid.addWidget(dyLab,2,2)
		grid.addWidget(self.dy,2,3)
		groupBox.setLayout(grid)
		return groupBox
	
	def webserverGroup(self):
		groupBox = QtWidgets.QGroupBox("Input Webserver / Request")

		# combobox with WMS-servers
		cboDefWMSLab = QtWidgets.QLabel("Predifined WMS Requests", self)		
		self.cboDefWMS = QtWidgets.QComboBox(self)
		self.cboDefWMS.addItems(self.TitleList)
		self.cboDefWMS.currentIndexChanged.connect(self.selectionchange)
		
		# Webrequest text
		requestLab = QtWidgets.QLabel("Webserver Address & Request", self)
		self.request= QtWidgets.QLineEdit(self)		
		self.request.setText(self.ServerRequestPrefix[self.cboDefWMS.currentIndex()])

		grid = QtWidgets.QGridLayout()
		grid.addWidget(cboDefWMSLab,0,0)
		grid.addWidget(self.cboDefWMS,0,1)
		grid.addWidget(requestLab,1,0)
		grid.addWidget(self.request,1,1)
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

		# note set
		self.labelnote = QtWidgets.QLabel("Note: Use 'Geographic Location' to obtain CRS and coordinates from map", self)
		self.labelnote.move(40, 620)
			
	def onimageName(self): 
		self.filelocation = self.folderName + "/" + self.imageName.text() + ".jpg"

	def selectionchange(self): 
		self.request.clear()		
		self.request.setText(self.ServerRequestPrefix[self.cboDefWMS.currentIndex()])
		self.imageName.clear()
		self.imageName.setText(self.cboDefWMS.currentText())

	def onbboxHeight(self):
		test = "test"

	def onbboxWidth(self):
		test = "test"

	def onTest(self):
		URL = self.request.text()
		width = float(self.bboxWidth.text())
		height = float(self.bboxHeight.text())
		fileLocationWMS = self.tempFolder + self.imageName.text() + '.jpg'
		pixWidth = float(self.pixelwidth.text())
		self.pixHeight = int((pixWidth*height)/width)
		pixHeight = self.pixHeight
		Bbox = GIS2BIM.CreateBoundingBox(float(self.X),float(self.Y),width,height,2)
		GIS2BIM.WMSRequest(URL,Bbox,self.tempFileName,pixWidth,pixHeight)
		if self.cbGrayscale.checkState():
			img = Image.open(fileLocationWMS)
			fileLocationWMS2 = self.tempFolder + self.imageName.text() + '_gray.jpg'
			gray_image = ImageOps.grayscale(img)
			gray_image.save(fileLocationWMS2)
		else: fileLocationWMS2 = fileLocationWMS
		picture = QPixmap(fileLocationWMS2)
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
		pixWidth = float(self.pixelwidth.text())
		self.pixHeight = (pixWidth*height)/width
		pixHeight = self.pixHeight		
		URL = self.request.text()
		X = float(self.X)
		Y = float(self.Y)
		dx = float(self.dx.text())*1000
		dy = float(self.dy.text())*1000
		fileLocationWMS = self.tempFolder + self.imageName.text() + '.jpg'
		Bbox = GIS2BIM.CreateBoundingBox(X,Y,width,height,2)
		result = GIS2BIM.WMSRequest(URL,Bbox,fileLocationWMS,self.pixelwidth.text(),int(self.pixHeight))
		if self.cbGrayscale.checkState():
			img = Image.open(fileLocationWMS)
			fileLocationWMS2 = self.tempFolder + self.imageName.text() + '_gray.jpg'
			gray_image = ImageOps.grayscale(img)
			gray_image.save(fileLocationWMS2)
		else: fileLocationWMS2 = fileLocationWMS
		ImageAerialPhoto = GIS2BIM_FreeCAD.ImportImage(fileLocationWMS2,width,height,1000, str(self.imageName.text()), dx,dy)
		ImageAerialPhoto.addProperty("App::PropertyString","WMSRequestURL")
		ImageAerialPhoto.WMSRequestURL = result[2]
		GIS2BIM_FreeCAD.CreateLayer("GIS_Raster")
		FreeCAD.activeDocument().getObject("GIS_Raster").addObject(FreeCAD.activeDocument().getObject(ImageAerialPhoto.Label))
		FreeCAD.ActiveDocument.recompute()
		self.close()

	def onCancel(self):
		self.close()

#form = GISWMS_Dialog()
#form.exec_()