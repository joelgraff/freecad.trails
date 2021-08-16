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

import FreeCAD

import GIS2BIM
import GIS2BIM_FreeCAD

class GISWMS_Dialog(QtWidgets.QDialog):

	def __init__(self):
		super(GISWMS_Dialog, self).__init__()
		self.sitename = "GIS-Sitedata"
		self.tempFolderName = "GIStemp/"
		self.X = str(GIS2BIM_FreeCAD.ArchSiteCreateCheck(self.sitename).CRS_x)
		self.Y = str(GIS2BIM_FreeCAD.ArchSiteCreateCheck(self.sitename).CRS_y)
		self.CRS = str(GIS2BIM_FreeCAD.ArchSiteCreateCheck(self.sitename).CRS_EPSG_SRID)
		self.CRSDescription = str(GIS2BIM_FreeCAD.ArchSiteCreateCheck(self.sitename).CRS_EPSG_Description)
		self.bboxWidth = str(GIS2BIM_FreeCAD.ArchSiteCreateCheck(self.sitename).BoundingboxWidth)
		self.bboxHeight = str(GIS2BIM_FreeCAD.ArchSiteCreateCheck(self.sitename).BoundingboxHeight)
		self.tempFolder = GIS2BIM_FreeCAD.CreateTempFolder(self.tempFolderName)
		self.folderName = self.tempFolder
		self.tempFileName = self.tempFolder + "initialWMS.jpg" 
		
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
		self.initUI()
		
	def initUI(self):
		self.result = userCancelled
		self.setWindowTitle("Load Raster Data with WMS(Web Map Server)")
		self.setGeometry(50, 50, 920, 910)
		self.setFixedSize(self.size())
		
		self.centralwidget = QtWidgets.QWidget(self)
		self.centralwidget.setObjectName("WMS")
		self.pictlabel = QtWidgets.QLabel(self)
		
		# note set
		self.labelnote = QtWidgets.QLabel("Note: Use Geographic Location to obtain CRS and coordinates from map", self)
		self.labelnote.move(40, 620)

		#CRS
		self.labelCRS = QtWidgets.QLabel("CRS", self)
		self.labelCRS.move(40, 645)
		self.CRS = QtWidgets.QLabel(self.CRS + " " + self.CRSDescription, self)
		self.CRS.move(200, 645)

		#X-coordinate
		self.numericInput1X = QtWidgets.QLineEdit(self)
		self.numericInput1X.setInputMask("")
		self.numericInput1X.setText(self.X)
		self.numericInput1X.setFixedWidth(100)
		self.numericInput1X.move(200, 670)
		self.label2 = QtWidgets.QLabel("X-coordinate", self)
		self.label2.move(40, 675)
		
		#Y-coordinate		
		self.numericInput2Y = QtWidgets.QLineEdit(self)
		self.numericInput2Y.setInputMask("")
		self.numericInput2Y.setText(self.Y)
		self.numericInput2Y.setFixedWidth(100)
		self.numericInput2Y.move(200, 700)
		self.label3 = QtWidgets.QLabel("Y-coordinate", self)
		self.label3.move(40, 705)
		
		# boundingbox width
		self.bboxWidthLab = QtWidgets.QLineEdit(self)
		self.bboxWidthLab.setInputMask("")
		self.bboxWidthLab.setText(self.bboxWidth)
		self.bboxWidthLab.setFixedWidth(100)
		self.bboxWidthLab.move(200, 730)
		self.label4 = QtWidgets.QLabel("Boundingbox Width [m]", self)
		self.label4.move(40, 735)

		# boundingbox height
		self.bboxHeightLab = QtWidgets.QLineEdit(self)
		self.bboxHeightLab.setInputMask("")
		self.bboxHeightLab.setText(self.bboxHeight)
		self.bboxHeightLab.setFixedWidth(100)
		self.bboxHeightLab.move(200, 760)
		self.label5 = QtWidgets.QLabel("Boundingbox Height [m]", self)
		self.label5.move(40, 765)

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
		self.imageName.move(520, 670)
		self.imageNameLabel = QtWidgets.QLabel("Image Name", self)
		self.imageNameLabel.move(350, 675)
		self.imageName.editingFinished.connect(self.onimageName)

		#Filelocation 
		self.filelocation = self.tempFileName
		def do_file():
			self.fname = QtWidgets.QFileDialog.getExistingDirectory(self, "Open Directory",self.tempFolder,QtWidgets.QFileDialog.ShowDirsOnly | QtWidgets.QFileDialog.DontResolveSymlinks)
			self.foldername = fname	
			self.filelocation = self.foldername + "/" + self.imageName.text() + ".jpg"
		self.button = QtWidgets.QPushButton("Browse",self)
		self.button.clicked.connect(do_file)
		self.button.show()
		self.button.move(515, 695)
		self.label8 = QtWidgets.QLabel("Folder for temporary files", self)
		self.label8.move(350, 705)

		# pixel width
		self.pixelwidth = QtWidgets.QLineEdit(self)
		self.pixelwidth.setInputMask("")
		self.pixelwidth.setText("3000")
		self.pixelwidth.setFixedWidth(70)
		self.pixelwidth.move(520, 730)
		self.labelpixwidth = QtWidgets.QLabel("Pixels in Width", self)
		self.labelpixwidth.move(350, 735)

		# combobox with WMS-servers
		self.cbo = QtWidgets.QComboBox(self)
		self.cbo.autoCompletion()
		self.cbo.move(520,760)
		self.cbo.addItems(self.TitleList)
		self.labelWMS = QtWidgets.QLabel("Predifined WMS Requests", self)
		self.labelWMS.move(350, 765)
		self.cbo.currentIndexChanged.connect(self.selectionchange)
		
		# webservernameAndRequest
		self.webserverName1 = QtWidgets.QPlainTextEdit(self)
		self.webserverName1.insertPlainText(self.ServerRequestPrefix[self.cbo.currentIndex()])
		self.webserverName1.setFixedWidth(300)
		self.webserverName1.setFixedHeight(80)
		self.webserverName1.move(515, 790)
		self.label1 = QtWidgets.QLabel("Webserver Address & Request", self)
		self.label1.move(350, 795)

		# test WMS button
		testWMSButton = QtWidgets.QPushButton('Test WMS-request and show result', self)
		testWMSButton.clicked.connect(self.testWMS)
		testWMSButton.move(280, 870)

		# cancel button
		cancelButton = QtWidgets.QPushButton('Cancel', self)
		cancelButton.clicked.connect(self.onCancel)
		cancelButton.setAutoDefault(True)
		cancelButton.move(190, 870)

		# Ok WMS button
		okButton = QtWidgets.QPushButton('OK and import image', self)
		okButton.clicked.connect(self.onOk)
		okButton.move(35, 870)
		self.show()
		self.testWMS()

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

	def testWMS(self):
		URL = str(self.webserverName1.toPlainText())
		X = float(self.numericInput1X.text())
		Y = float(self.numericInput2Y.text())
		width = float(self.bboxWidthLab.text())
		height = float(self.bboxHeightLab.text())
		fileLocationWMS = str(self.filelocation)
		pixWidth = float(self.pixelwidth.text())
		self.pixHeight = int((pixWidth*height)/width)
		pixHeight = self.pixHeight
		Bbox = GIS2BIM.CreateBoundingBox(X,Y,width,height,2)
		GIS2BIM.WMSRequest(URL,Bbox,self.tempFileName,pixWidth,pixHeight)
		picture = QPixmap(fileLocationWMS)
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
		self.result= userTest

	def onOk(self):
		self.result= userOK
		width = float(self.bboxWidthLab.text())
		height = float(self.bboxHeightLab.text())
		fileLocationWMS = str(self.filelocation)
		pixWidth = float(self.pixelwidth.text())
		self.pixHeight = (pixWidth*height)/width
		pixHeight = self.pixHeight		
		URL = str(self.webserverName1.toPlainText())
		X = float(self.numericInput1X.text())
		Y = float(self.numericInput2Y.text())
		dx = float(self.dx.text())*1000
		dy = float(self.dy.text())*1000
		Bbox = GIS2BIM.CreateBoundingBox(X,Y,width,height,2)
		result = GIS2BIM.WMSRequest(URL,Bbox,fileLocationWMS,self.pixelwidth.text(),int(self.pixHeight))
		ImageAerialPhoto = GIS2BIM_FreeCAD.ImportImage(fileLocationWMS,width,height,1000, str(self.imageName.text()), dx,dy)
		ImageAerialPhoto.addProperty("App::PropertyString","WMSRequestURL")
		ImageAerialPhoto.WMSRequestURL = result[2]
		GIS2BIM_FreeCAD.CreateLayer("GIS_Raster")
		FreeCAD.activeDocument().getObject("GIS_Raster").addObject(FreeCAD.activeDocument().getObject(ImageAerialPhoto.Label))
		FreeCAD.ActiveDocument.recompute()
		self.result= userOK
		self.close()

# Constant definitions
userCancelled = "Cancelled"
userOK = "OK"
userTest = "TestWMS"

#form = GISWMS_Dialog()
#form.exec_()