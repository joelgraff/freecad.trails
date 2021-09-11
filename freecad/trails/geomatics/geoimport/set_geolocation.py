# -*- coding: utf8 -*-
#***************************************************************************
#*   Copyright (c) 2021 Maarten Vroegindeweij <maarten@3bm.co.nl>              *
#*                                                                        						 *
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

import importlib
from PyPackages import GIS2BIM
from PyPackages import GIS2BIM_FreeCAD
from PyPackages import GIS2BIM_CRS 
from PyPackages import GIS2BIM_GUI
import FreeCAD
#importlib.reload(GIS2BIM_GUI)

import os
import time
import re

from freecad.trails import geo_origin

class GISLocation_Dialog(QtWidgets.QDialog):

	def __init__(self):
		super(GISLocation_Dialog, self).__init__()

		self.sitename = "GIS-Sitedata"

		self.tempFolderName = "GIStemp/"
		
		#Get/set parameters for GIS
		self.lat = GIS2BIM_FreeCAD.ArchSiteCreateCheck(self.sitename).WGS84_Latitude
		self.lon = GIS2BIM_FreeCAD.ArchSiteCreateCheck(self.sitename).WGS84_Longitude
		self.bboxWidthStart = str(GIS2BIM_FreeCAD.ArchSiteCreateCheck(self.sitename).BoundingboxWidth)
		self.bboxHeightStart = str(GIS2BIM_FreeCAD.ArchSiteCreateCheck(self.sitename).BoundingboxHeight)
		self.CRS = GIS2BIM_FreeCAD.ArchSiteCreateCheck(self.sitename).CRS_EPSG_SRID

		#Create temp folders/files
		self.URLmap = GIS2BIM.GetWebServerData("HTMLLocationData", "Other", "URL")
		self.URLSearch = GIS2BIM.GetWebServerData("HTMLLocationDataJSmapfilesearch", "Other", "URL")
		self.URLUpdate = GIS2BIM.GetWebServerData("HTMLLocationDataJSmapbboxupdate", "Other", "URL")
		#self.filepathBaseMap = GIS2BIM.DownloadURL(GIS2BIM_FreeCAD.CreateTempFolder(self.tempFolderName),self.URLmap,"basemap.html")
		self.filepathJSSearch = GIS2BIM.DownloadURL(GIS2BIM_FreeCAD.CreateTempFolder(self.tempFolderName),self.URLSearch,"map_filesearch.js")
		self.filepathJSUpdate = GIS2BIM.DownloadURL(GIS2BIM_FreeCAD.CreateTempFolder(self.tempFolderName),self.URLUpdate,"map_bboxupdate.js")
		self.filepathBaseMap = "C:/Users/mikev/OneDrive/Bureaublad/TEMP/GIStemp/basemapNewVersion.html"	
		self.tempFolderPath = GIS2BIM_FreeCAD.CreateTempFolder(self.tempFolderName)	
		self.filepathNewMap = self.tempFolderPath +"/map.html"	
		self.temptxtPath = self.tempFolderPath + "/temp.txt"

		#Set Style
		self.setStyleSheet(GIS2BIM_GUI.StyleSheet) #margin: 2px

		for file in os.listdir(self.tempFolderPath): # Cleanup of txt-files
			if file.endswith(".txt"):
				self.filename = self.tempFolderPath + "/" + file
				os.remove(self.filename)
		#self.application = QApplication(sys.argv)  #extend this to kill the webengineprocess
				
		#Overall Grid
		grid = QtWidgets.QGridLayout()
		grid.addWidget(self.webViewGroup(), 0, 0)
		grid.addWidget(self.locationGroup(), 1, 0, QtCore.Qt.AlignTop)	
		grid.addLayout(self.buttonGroup(),2,0)
		grid.setRowStretch(0,3)
		self.setLayout(grid)
		
		self.setWindowTitle("Set Geographic Location")
		self.resize(920, 900)

		#Download map.html from GIS2BIM Repository and set projectlocation
		os.remove(self.filepathNewMap)
		BaseMap = open(self.filepathBaseMap,"r")
		BaseMapstr = BaseMap.read()
		Newstr = BaseMapstr.replace("51LAT",self.lat)
		Newstr = Newstr.replace("4LONG", self.lon)
		Newstr = Newstr.replace("FOLDERNAME", self.temptxtPath)
		Newstr = Newstr.replace("WBBOX",self.bboxWidthStart)
		Newstr = Newstr.replace("HBBOX",self.bboxHeightStart)
		open(self.filepathNewMap, "x")
		f1 = open(self.filepathNewMap, "w")
		f1.write(Newstr)
		f1.close()

	def webViewGroup(self):
		groupBoxx = GIS2BIM_GUI.webViewGroup(self)

		return groupBoxx

	def locationGroup(self):
		groupBox = QtWidgets.QGroupBox("Location")
		
		#Search Line
		searchLab = QtWidgets.QLabel("Search Place/Address", self)
		self.search= QtWidgets.QLineEdit(self)		
		self.search.setText('Lange geldersekade Dordrecht')
		
		#Search Button
		searchbtn = QtWidgets.QPushButton("Search")
		searchbtn.clicked.connect(self.onSearch)

		#List of CRS
		cboCRSLab = QtWidgets.QLabel("Coordinate Reference System", self)		
		self.cboCRS = QtWidgets.QComboBox(self)
		
		inputCRS = list(map(str.__add__, [i + " " for i in GIS2BIM_CRS.inputChars] , GIS2BIM_CRS.inputNumbers))
		self.cboCRS.addItems(inputCRS)
		#completer = QtWidgets.QCompleter(inputCRS,self)
		#self.cboCRS.setCompleter(completer)
		try:
			self.index = GIS2BIM_CRS.indexOfCRS(self.CRS)
		except: 
			self.index = 5523
		self.cboCRS.setCurrentIndex(self.index)

		
		#bbox Width
		bboxWidthLab = QtWidgets.QLabel("Boundingbox Width [m]")
		self.bboxWidth = QtWidgets.QLineEdit()
		self.bboxWidth.setText(str(self.bboxWidthStart))
		self.bboxWidth.editingFinished.connect(self.onbboxWidth)

		#bbox Height
		bboxHeightLab = QtWidgets.QLabel("Boundingbox Height [m]")
		self.bboxHeight = QtWidgets.QLineEdit()
		self.bboxHeight.setText(str(self.bboxHeightStart))
		self.bboxHeight.editingFinished.connect(self.onbboxHeight)	
	
		# checkbox update Geo Origin
		self.CBGeoOrigin = QtWidgets.QCheckBox("Create/Update GeoOrigin Object", self)
		self.CBGeoOrigin.toggle()

		# checkbox import map
		self.CBAerialphoto = QtWidgets.QCheckBox("Import Aerialphoto", self)
	
		grid = QtWidgets.QGridLayout()
		grid.addWidget(searchLab,0,0)
		grid.addWidget(self.search,0,1)
		grid.addWidget(searchbtn,0,2)
		grid.addWidget(cboCRSLab,1,0)
		grid.addWidget(self.cboCRS,1,1)
		grid.setRowStretch(1,1)
		grid.addWidget(bboxWidthLab,2,0)
		grid.addWidget(self.bboxWidth,2,1)
		grid.addWidget(bboxHeightLab,3,0)
		grid.addWidget(self.bboxHeight,3,1)
		grid.addWidget(self.CBGeoOrigin,4,1)
		grid.addWidget(self.CBAerialphoto,4,2)

		groupBox.setLayout(grid)
		return groupBox

	def buttonGroup(self):
		hbox = GIS2BIM_GUI.buttonGroupOKCancel(self)
		return hbox

	def onbboxWidth(self):
		JS2 = open(self.filepathJSUpdate,"r")
		JS2 = JS2.read()
		JS2 = JS2.replace("WBBOX", self.bboxWidth.text())
		JS2 = JS2.replace("HBBOX", self.bboxHeight.text())
		self.webPage.runJavaScript(JS2) # update bboxWidth in mapview

	def onbboxHeight(self):
		JS3 = open(self.filepathJSUpdate,"r")
		JS3 = JS3.read()
		JS3 = JS3.replace("WBBOX", self.bboxWidth.text())
		JS3 = JS3.replace("HBBOX", self.bboxHeight.text())
		self.webPage.runJavaScript(JS3) # update bboxHeight in mapview

	def onCancel(self):
		self.webView.stop()
		self.close()
		
	def onSearch(self):	
		searchterm = self.search.text().split()
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
		CRS_EPSG_SRID = SiteObject.CRS_EPSG_SRID = GIS2BIM_CRS.inputChars[self.cboCRS.currentIndex()]
		SiteObject.WGS84_Longitude = self.lon
		SiteObject.WGS84_Latitude = self.lat
		SiteObject.Longitude = float(self.lon)
		SiteObject.Latitude = float(self.lat)
		Transformation = GIS2BIM.TransformCRS_epsg("4326",CRS_EPSG_SRID,self.lon,self.lat)
		SiteObject.CRS_x = float(Transformation[0])
		SiteObject.CRS_y = float(Transformation[1])
		SiteObject.BoundingboxWidth = float(self.bboxWidth.text())
		SiteObject.BoundingboxHeight = float(self.bboxHeight.text())
		SiteObject.CRS_EPSG_Description = GIS2BIM_CRS.getCRSdata(CRS_EPSG_SRID)
		#Set GeoOrigin
		if self.CBGeoOrigin.isChecked() is True:
			obj = geo_origin.get()	
			obj.Origin = FreeCAD.Vector(float(Transformation[0])*1000, float(Transformation[1])*1000, 0)
		if self.CBAerialphoto.isChecked() is True:
			fileLocationTMS = self.tempFolderPath + 'ESRI_aerialphoto.jpg'
			TMS = GIS2BIM.TMS_WMTSCombinedMapFromLatLonBbox(float(self.lat),float(self.lon),float(self.bboxWidth.text()),float(self.bboxHeight.text()),17,256,0,"http://server.arcgisonline.com/ArcGIS/rest/services/World_Imagery/MapServer/tile/{z}/{y}/{x}.png")
			TMS[0].save(fileLocationTMS)
			ImageMap = GIS2BIM_FreeCAD.ImportImage(fileLocationTMS,float(self.bboxWidth.text()),float(self.bboxHeight.text()),1000, "ESRI aerialMap", 0,0)
			GIS2BIM_FreeCAD.CreateLayer("GIS_Raster")
			FreeCAD.ActiveDocument.recompute()
			FreeCAD.activeDocument().getObject("GIS_Raster").addObject(FreeCAD.activeDocument().getObject(ImageMap.Label))
		self.close()
			
#form = GISLocation_Dialog()
#form.exec_()