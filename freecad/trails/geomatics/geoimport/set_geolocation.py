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

"""This module contains
"""

__title__= "GIS2BIM_FreeCAD_set_geolocation"
__author__ = "Maarten Vroegindeweij"
__url__ = "https://github.com/DutchSailor/GIS2BIM"

####imports

from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtWebEngineWidgets import QWebEnginePage 
from PySide2 import QtCore, QtWidgets
from PySide2.QtCore import QUrl

from . import GIS2BIM
from . import GIS2BIM_FreeCAD
from . import GIS2BIM_CRS 
import FreeCAD

import os
import time
import re

from freecad.trails import geo_origin

class GISLocation_Dialog(QtWidgets.QDialog):

	def __init__(self):
		super(GISLocation_Dialog, self).__init__()
		self.sitename = "GIS-Sitedata"
		self.tempFolderName = "GIStemp/"
		self.lat = str(GIS2BIM_FreeCAD.ArchSiteCreateCheck(self.sitename).WGS84_Latitude)
		self.lon = str(GIS2BIM_FreeCAD.ArchSiteCreateCheck(self.sitename).WGS84_Longitude)
		self.bboxWidth = str(GIS2BIM_FreeCAD.ArchSiteCreateCheck(self.sitename).BoundingboxWidth)
		self.bboxHeight = str(GIS2BIM_FreeCAD.ArchSiteCreateCheck(self.sitename).BoundingboxHeight)
		#Create temp folders/files
		self.URLmap = GIS2BIM.GetWebServerData("HTMLLocationData", "Other", "URL")
		self.URLSearch = GIS2BIM.GetWebServerData("HTMLLocationDataJSmapfilesearch", "Other", "URL")
		self.URLUpdate = GIS2BIM.GetWebServerData("HTMLLocationDataJSmapbboxupdate", "Other", "URL")
		self.filepathBaseMap = GIS2BIM.DownloadURL(GIS2BIM_FreeCAD.CreateTempFolder(self.tempFolderName),self.URLmap,"basemap.html")
		self.filepathNewMap = GIS2BIM.DownloadURL(GIS2BIM_FreeCAD.CreateTempFolder(self.tempFolderName),self.URLmap,"map.html")
		self.filepathJSSearch = GIS2BIM.DownloadURL(GIS2BIM_FreeCAD.CreateTempFolder(self.tempFolderName),self.URLSearch,"map_filesearch.js")
		self.filepathJSUpdate = GIS2BIM.DownloadURL(GIS2BIM_FreeCAD.CreateTempFolder(self.tempFolderName),self.URLUpdate,"map_bboxupdate.js")
		#self.filepathBaseMap = "C:/Users/mikev/OneDrive/Bureaublad/TEMP/GIStemp/basemap.html"	
		self.tempFolderPath = GIS2BIM_FreeCAD.CreateTempFolder(self.tempFolderName)	
		self.temptxtPath = self.tempFolderPath + "/temp.txt"
		
		for file in os.listdir(self.tempFolderPath): # Cleanup of txt-files
			if file.endswith(".txt"):
				self.filename = self.tempFolderPath + "/" + file
				os.remove(self.filename)
		self.initUI()
		#self.application = QApplication(sys.argv)  #extend this to kill the webengineprocess
	
	def initUI(self):
		self.result = userCancelled
		self.setWindowTitle("Set Geographic Location")
		self.setGeometry(100, 100, 920, 900)
		self.setFixedSize(self.size())
		
		# CrossLines
		self.centralwidget = QtWidgets.QWidget(self)
		self.centralwidget.setObjectName("map")

		self.webView = QWebEngineView(self.centralwidget)
		self.webView.setGeometry(QtCore.QRect(40, 40, 840, 620))
		self.webPage = QWebEnginePage()
		
		#Download map.html from GIS2BIM Repository and set projectlocation
		os.remove(self.filepathNewMap)
		BaseMap = open(self.filepathBaseMap,"r")
		BaseMapstr = BaseMap.read()
		Newstr = BaseMapstr.replace("51LAT",str(self.lat))
		Newstr = Newstr.replace("4LONG", str(self.lon))
		Newstr = Newstr.replace("FOLDERNAME", self.temptxtPath)
		Newstr = Newstr.replace("WBBOX",self.bboxWidth)
		Newstr = Newstr.replace("HBBOX",self.bboxHeight)
		open(self.filepathNewMap, "x")
		f1 = open(self.filepathNewMap, "w")
		f1.write(Newstr)
		f1.close()

		#Load map.html		
		self.webPage.load(QUrl(QtCore.QUrl(self.filepathNewMap)))
		self.webView.setObjectName("webView")
		self.webView.setPage(self.webPage)

		QtCore.QMetaObject.connectSlotsByName(self)
		self.label1 = QtWidgets.QLabel("Click on the map to set the center of the boundingbox" , self)
		self.label1.move(50, 25)

		#Search 
		self.label3 = QtWidgets.QLabel("Search Place/Address", self)
		self.label3.move(40, 675)

		#search line
		self.searchline1 = QtWidgets.QPlainTextEdit(self)
		self.searchline1.insertPlainText("Dordrecht")
		self.searchline1.setFixedWidth(400)
		self.searchline1.setFixedHeight(50)
		self.searchline1.move(195, 670)

		# search button
		searchButton = QtWidgets.QPushButton('Search', self)
		searchButton.clicked.connect(self.onSearch)
		searchButton.setAutoDefault(True)
		searchButton.move(600, 670)

		#list of CRS
		self.dropdownCRSlabel = QtWidgets.QLabel("Coordinate Reference System", self)
		self.dropdownCRSlabel.move(40, 735)
		#
		self.dropdownCRS = QtWidgets.QComboBox(self)
		self.dropdownCRS.addItems(list(map(str.__add__, [i + " " for i in GIS2BIM_CRS.inputChars] , GIS2BIM_CRS.inputNumbers)))
		self.dropdownCRS.setCurrentIndex(5523)
		self.dropdownCRS.setFixedWidth(300)
		self.dropdownCRS.move(200, 730)

		# boundingbox width
		self.bboxWidthLab = QtWidgets.QLineEdit(self)
		self.bboxWidthLab.setInputMask("")
		self.bboxWidthLab.setText(self.bboxWidth)
		self.bboxWidthLab.setFixedWidth(100)
		self.bboxWidthLab.move(200, 760)
		self.bboxWidthLab.editingFinished.connect(self.onbboxWidth)
		self.label1 = QtWidgets.QLabel("Boundingbox Width [m]", self)
		self.label1.move(40, 765)

		# boundingbox height
		self.bboxHeightLab = QtWidgets.QLineEdit(self)
		self.bboxHeightLab.setInputMask("")
		self.bboxHeightLab.setText(self.bboxHeight)
		self.bboxHeightLab.setFixedWidth(100)
		self.bboxHeightLab.move(200, 790)
		self.bboxHeightLab.editingFinished.connect(self.onbboxHeight)
		self.label2 = QtWidgets.QLabel("Boundingbox Height [m]", self)
		self.label2.move(40, 795)
		
		# checkbox update Geo Origin
		self.checkbox1 = QtWidgets.QCheckBox("Create/Update GeoOrigin Object(Trials WB)", self)
		self.checkbox1.toggle()
		self.checkbox1.move(340,760)

		# cancel button
		cancelButton = QtWidgets.QPushButton('Cancel', self)
		cancelButton.clicked.connect(self.onCancel)
		cancelButton.setAutoDefault(True)
		cancelButton.move(120, 840)

		# OK button
		okButton = QtWidgets.QPushButton('OK', self)
		okButton.clicked.connect(self.onOk)
		okButton.move(35, 840)
		self.show()

	def onbboxWidth(self):
		JS2 = open(self.filepathJSUpdate,"r")
		JS2 = JS2.read()
		JS2 = JS2.replace("WBBOX", self.bboxWidthLab.text())
		JS2 = JS2.replace("HBBOX", self.bboxHeightLab.text())
		self.webPage.runJavaScript(JS2) # update bboxWidth in mapview

	def onbboxHeight(self):
		JS3 = open(self.filepathJSUpdate,"r")
		JS3 = JS3.read()
		JS3 = JS3.replace("WBBOX", self.bboxWidthLab.text())
		JS3 = JS3.replace("HBBOX", self.bboxHeightLab.text())
		self.webPage.runJavaScript(JS3) # update bboxHeight in mapview

	def onCancel(self):
		self.result= userCancelled
		self.webView.stop()
		self.close()
		
	def onSearch(self):	
		#self.result= userOK
		searchterm = self.searchline1.toPlainText().split()
		self.lat = (GIS2BIM.NominatimAPI(searchterm))[0] #Use Nominatim for geocoding
		self.lon = (GIS2BIM.NominatimAPI(searchterm))[1]
		if self.lat is None:
			dialog = QtWidgets.QMessageBox()
			dialog.setText("Address not found")
			dialog.setWindowTitle("Warning")
			dialog.exec_() 
		else:
			JS = open(self.filepathJSSearch,"r")
			JS = JS.read()
			JS = JS.replace("51LAT",str(self.lat))
			JS = JS.replace("4LONG", str(self.lon))
			JS = JS.replace("FOLDERNAME", self.temptxtPath)
			self.webPage.runJavaScript(JS) # set view

	def onOk(self):
		# Find latest version of temp.txt which contains the chosen coordinates
		filenames = []
		filestamps = []
		for filename in os.listdir(self.tempFolderPath):
			if filename.endswith(".txt"):
				filenames.append(filename)
				i = os.path.getmtime(self.tempFolderPath + "/" + filename)
				filestamps.append(time.strftime('%Y-%m-%d %H:%M:%S', time.localtime(i)))
		latest = max(filestamps)
		indexof = filestamps.index(latest)
		latestfile = filenames[indexof]
		filepathTempfileLATLONData = self.tempFolderPath + "/" + latestfile #most recent file
		tempFileCoordinates = open(filepathTempfileLATLONData,"r")
		CoordinatesString = tempFileCoordinates.read()
		tempFileCoordinates.close()

		strsplit = re.split("[(, )]", CoordinatesString)
		self.lat = strsplit[1]
		self.lon = strsplit[3]
		SiteObject = GIS2BIM_FreeCAD.ArchSiteCreateCheck(self.sitename)
		CRS_EPSG_SRID = SiteObject.CRS_EPSG_SRID = GIS2BIM_CRS.inputChars[self.dropdownCRS.currentIndex()]
		SiteObject.WGS84_Longitude = self.lon
		SiteObject.WGS84_Latitude = self.lat
		SiteObject.Longitude = float(self.lon)
		SiteObject.Latitude = float(self.lat)
		Transformation = GIS2BIM.TransformCRS_epsg("4326",CRS_EPSG_SRID,self.lon,self.lat)
		SiteObject.CRS_x = float(Transformation[0])
		SiteObject.CRS_y = float(Transformation[1])
		SiteObject.BoundingboxWidth = float(self.bboxWidthLab.text())
		SiteObject.BoundingboxHeight = float(self.bboxHeightLab.text())
		SiteObject.CRS_EPSG_Description = GIS2BIM_CRS.getCRSdata(CRS_EPSG_SRID)
		#Set GeoOrigin
		if self.checkbox1:
			obj = geo_origin.get()	
			obj.Origin = FreeCAD.Vector(float(Transformation[0])*1000, float(Transformation[1])*1000, 0)
		self.result= userOK
		self.close()
			
# Constant definitions
userCancelled		= "Cancelled"
userOK			= "OK"

#form = GISLocation_Dialog()
#form.exec_()
