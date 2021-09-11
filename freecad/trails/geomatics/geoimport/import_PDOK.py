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

"""This module provides tools to load GIS information into FreeCAD
"""

__title__= "GIS2BIM_FreeCAD_import_pdok"
__author__ = "Maarten Vroegindeweij"
__url__ = "https://github.com/DutchSailor/GIS2BIM"

# WFS Importer

from PySide2 import QtCore, QtWidgets
from PySide2.QtWidgets import *
from PySide2.QtWebEngineWidgets import QWebEngineView
from PySide2.QtWebEngineWidgets import QWebEnginePage 
from PySide2.QtCore import QUrl

import os
import FreeCAD

import xml.etree.ElementTree as ET

from PyPackages import GIS2BIM
from PyPackages import GIS2BIM_FreeCAD
from PyPackages import GIS2BIM_CRS
from PyPackages import GIS2BIM_NL 
from PyPackages import GIS2BIM_GUI

#import importlib
#importlib.reload(GIS2BIM_GUI)
#importlib.reload(GIS2BIM_FreeCAD)

class GIS_NL_Dialog(QtWidgets.QDialog):
	def __init__(self, parent=None):
		super(GIS_NL_Dialog, self).__init__(parent)
		
		self.sitename = "GIS-Sitedata"
		
		#Get/set parameters for GIS
		self.tempFolderName = "GIStemp/"
		self.X = str(GIS2BIM_FreeCAD.ArchSiteCreateCheck(self.sitename).CRS_x)
		self.Y = str(GIS2BIM_FreeCAD.ArchSiteCreateCheck(self.sitename).CRS_y)	
		self.lat = str(GIS2BIM_FreeCAD.ArchSiteCreateCheck(self.sitename).WGS84_Latitude)
		self.lon = str(GIS2BIM_FreeCAD.ArchSiteCreateCheck(self.sitename).WGS84_Longitude)
		self.bboxWidthStart = str(GIS2BIM_FreeCAD.ArchSiteCreateCheck(self.sitename).BoundingboxWidth)
		self.bboxHeightStart = str(GIS2BIM_FreeCAD.ArchSiteCreateCheck(self.sitename).BoundingboxHeight)
		self.CRS = str(GIS2BIM_FreeCAD.ArchSiteCreateCheck(self.sitename).CRS_EPSG_SRID)
		self.CRSDescription = str(GIS2BIM_FreeCAD.ArchSiteCreateCheck(self.sitename).CRS_EPSG_Description)
		self.bboxString = GIS2BIM.CreateBoundingBox(float(GIS2BIM_FreeCAD.ArchSiteCreateCheck(self.sitename).CRS_x),float(GIS2BIM_FreeCAD.ArchSiteCreateCheck(self.sitename).CRS_y),float(self.bboxWidthStart),float(self.bboxHeightStart),0)

		#Set Style
		self.setStyleSheet("QWidget {background-color: rgb(68, 68, 68)} QPushButton { background-color: black } QGroupBox {border: 1px solid grey; }") #margin: 2px;
		
		#Download files
		self.URLUpdate = GIS2BIM.GetWebServerData("HTMLLocationDataJSmapbboxupdate", "Other", "URL")	#Javascript-URL for update boundingbox
		self.URLmap = GIS2BIM.GetWebServerData("HTMLwfs", "Other", "URL")
		self.filepathJSUpdate = GIS2BIM.DownloadURL(GIS2BIM_FreeCAD.CreateTempFolder(self.tempFolderName),self.URLUpdate,"map_bboxupdate.js") #Javascript-file for update boundingbox
		self.filepathBaseMap = GIS2BIM.DownloadURL(GIS2BIM_FreeCAD.CreateTempFolder(self.tempFolderName),self.URLmap,"basemapWFS.html") #Basemap from GIS2BIM Repository for preview
		self.filepathNewMap = GIS2BIM.DownloadURL(GIS2BIM_FreeCAD.CreateTempFolder(self.tempFolderName),self.URLmap,"mapWFS.html") #Edited Basemap with location and bbox
		#self.filepathBaseMap = "C:/Users/mikev/OneDrive/Bureaublad/TEMP/GIStemp/basemapWFS.html"	
		#self.filepathNewMap = "C:/Users/mikev/OneDrive/Bureaublad/TEMP/GIStemp/mapWFS.html"	
		self.tempFolderPath = GIS2BIM_FreeCAD.CreateTempFolder(self.tempFolderName)	

		os.remove(self.filepathNewMap)
		BaseMap = open(self.filepathBaseMap,"r")
		BaseMapstr = BaseMap.read()
		Newstr = BaseMapstr.replace("51LAT",str(self.lat))
		Newstr = Newstr.replace("4LONG", str(self.lon))
		Newstr = Newstr.replace("WBBOX",self.bboxWidthStart)
		Newstr = Newstr.replace("HBBOX",self.bboxHeightStart)
		open(self.filepathNewMap, "x")
		f1 = open(self.filepathNewMap, "w")
		f1.write(Newstr)
		f1.close()

		#Overall Grid
		grid = QtWidgets.QGridLayout()
		grid.addWidget(self.webViewGroup(), 0, 0, 1, 2)
		grid.addWidget(self.locationGroup(), 3, 0)	
		grid.addWidget(self.pdokGroup(), 3, 1)
		grid.addLayout(self.buttonGroup(),4,0,1,2)
		grid.setRowStretch(0,2)
		self.setLayout(grid)
		
		self.setWindowTitle("PDOK: Load GIS-data in the Netherlands")
		self.resize(920, 910)

	def webViewGroup(self):
		groupBoxx = GIS2BIM_GUI.webViewGroup(self)
		return groupBoxx

	def locationGroup(self):
		groupBoxx = GIS2BIM_GUI.locationGroup(self)
		return groupBoxx

	def pdokGroup(self):
		groupBox = QtWidgets.QGroupBox("GIS-data only available in the Netherlands. Source: PDOK, TU Delft, ")

		clsCadLab = QtWidgets.QLabel("Cadastral Parcels 2D(Vector")
		self.clsCad = QtWidgets.QCheckBox()
		self.clsCad.setChecked(1)

		clsBldLab = QtWidgets.QLabel("Building Outline 2D")
		self.clsBld = QtWidgets.QCheckBox()
		self.clsBld.setChecked(1)

		clsBAG3DLab = QtWidgets.QLabel("BAG 3D V2")
		self.clsBAG3D = QtWidgets.QCheckBox()
		self.clsBAG3D.setChecked(1)

		clsAerialLab = QtWidgets.QLabel("Aerialphoto 2020(Raster)")
		self.clsAerial = QtWidgets.QCheckBox()
		self.clsAerial.setChecked(1)

		clsAnnotationLab = QtWidgets.QLabel("GIS 2D Annotation")
		self.clsAnnotation = QtWidgets.QCheckBox()
		self.clsAnnotation.setChecked(1)

		clsBouwvlakLab = QtWidgets.QLabel("Bestemmingsplan Bouwvlak 2D(Vector)")
		self.clsBouwvlak = QtWidgets.QCheckBox()
		self.clsBouwvlak.setChecked(1)

		clsBGTLab = QtWidgets.QLabel("BGT 2D(Vector)")
		self.clsBGT = QtWidgets.QCheckBox()
		self.clsBGT.setChecked(1)

		clsBestemmingsplanLab = QtWidgets.QLabel("Bestemmingsplan(Raster)")
		self.clsBestemmingsplan = QtWidgets.QCheckBox()
		self.clsBestemmingsplan.setChecked(1)

		grid = QtWidgets.QGridLayout()

		grid.addWidget(clsCadLab,0,0)
		grid.addWidget(self.clsCad,0,1)

		grid.addWidget(clsBldLab,1,0)
		grid.addWidget(self.clsBld,1,1)

		grid.addWidget(clsBAG3DLab,2,0)
		grid.addWidget(self.clsBAG3D,2,1)

		grid.addWidget(clsAerialLab,3,0)
		grid.addWidget(self.clsAerial,3,1)

		grid.addWidget(clsAnnotationLab,4,0)
		grid.addWidget(self.clsAnnotation,4,1)

		grid.addWidget(clsBouwvlakLab,5,0)
		grid.addWidget(self.clsBouwvlak,5,1)

		grid.addWidget(clsBGTLab,6,0)
		grid.addWidget(self.clsBGT,6,1)

		grid.addWidget(clsBestemmingsplanLab,7,0)
		grid.addWidget(self.clsBestemmingsplan,7,1)

		groupBox.setLayout(grid)
		
		return groupBox

	def buttonGroup(self):
		importbtn = QtWidgets.QPushButton("Import")
		importbtn.clicked.connect(self.onImport)
		cancelbtn = QtWidgets.QPushButton("Cancel")	
		cancelbtn.clicked.connect(self.onCancel)
		hbox = QtWidgets.QHBoxLayout()
		hbox.addWidget(importbtn)
		hbox.addWidget(cancelbtn)
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
	
	def onImport(self):
		Bbox = GIS2BIM.CreateBoundingBox(float(self.X),float(self.Y),float(self.bboxWidth.text()),float(self.bboxHeight.text()),2)
		width = float(self.bboxWidth.text())
		height = float(self.bboxHeight.text())
		GIS2BIM_FreeCAD.CreateLayer("PDOK")
		fileLocationWMS = self.tempFolderPath + "wms.jpg"

		#Create Cadastral Parcels 2D
		if self.clsCad.isChecked() is True:
			GIS_2D_Cadastral_Parcel = GIS2BIM_FreeCAD.CreateLayer("GIS_2D_Cadastral_Parcel")	
			CadastralParcelCurves = GIS2BIM_FreeCAD.CurvesFromWFS(GIS2BIM_NL.NLPDOKCadastreCadastralParcels,Bbox,GIS2BIM_NL.NLPDOKxPathOpenGISposList,-float(self.X),-float(self.Y),1000,3,False,False,u"Dashdot",(0.0,0.0,0.0))
			FreeCAD.activeDocument().getObject("GIS_2D_Cadastral_Parcel").addObjects(CadastralParcelCurves)
			FreeCAD.activeDocument().getObject("PDOK").addObject(FreeCAD.activeDocument().getObject("GIS_2D_Cadastral_Parcel"))

		#Create Building outline 2D
		if self.clsBld.isChecked() is True:
			GIS_2D_Building_Outline = GIS2BIM_FreeCAD.CreateLayer("GIS_2D_Building_Outline")	
			BAGCurves = GIS2BIM_FreeCAD.CurvesFromWFS(GIS2BIM_NL.NLPDOKBAGBuildingCountour,Bbox,GIS2BIM_NL.NLPDOKxPathOpenGISposList,-float(self.X),-float(self.Y),1000,3,True, True,u"Solid",(0.7,0.0,0.0))
			FreeCAD.activeDocument().getObject("GIS_2D_Building_Outline").addObjects(BAGCurves)
			FreeCAD.activeDocument().getObject("PDOK").addObject(FreeCAD.activeDocument().getObject("GIS_2D_Building_Outline"))

		#Create 3D Building BAG 3D V2
		if self.clsBAG3D.isChecked() is True:
			dx = -float(self.X) * 1000
			dy = -float(self.Y) * 1000		
			bboxString = GIS2BIM.CreateBoundingBox(float(GIS2BIM_FreeCAD.ArchSiteCreateCheck(self.sitename).CRS_x),float(GIS2BIM_FreeCAD.ArchSiteCreateCheck(self.sitename).CRS_y),float(self.bboxWidth.text()),float(self.bboxHeight.text()),0)
			jsonFileNames = GIS2BIM_NL.BAG3DDownload(Bbox,self.tempFolderPath)
				
			#Import JSON
			for jsonFile in jsonFileNames:
				meshes = GIS2BIM_FreeCAD.CityJSONImport(jsonFile,self.X,self.Y,2,float(self.bboxWidth.text()),float(self.bboxHeight.text()))

			FreeCAD.activeDocument().getObject("PDOK").addObject(FreeCAD.activeDocument().getObject("CityJSON"))

		# Import Aerialphoto in view
		if self.clsAerial.isChecked() is True:
			GIS_Raster = GIS2BIM_FreeCAD.CreateLayer("GIS_Raster")	
			a = GIS2BIM.WMSRequest(GIS2BIM.GetWebServerData("NL_PDOK_Luchtfoto_2020_28992", "webserverRequests", "serverrequestprefix"),Bbox,fileLocationWMS,3000,3000)
			ImageAerialPhoto = GIS2BIM_FreeCAD.ImportImage(fileLocationWMS,width,height,1000,"luchtfoto2020",0,0)
			ImageAerialPhoto.addProperty("App::PropertyString","WMSRequestURL")
			ImageAerialPhoto.WMSRequestURL = a[2]
			FreeCAD.activeDocument().getObject("GIS_Raster").addObject(FreeCAD.activeDocument().getObject(ImageAerialPhoto.Label))
			FreeCAD.activeDocument().getObject("PDOK").addObject(FreeCAD.activeDocument().getObject("GIS_Raster"))
			
		#Create Textdata Cadastral Parcels
		if self.clsAnnotation.isChecked() is True:
			GIS_Annotation = GIS2BIM_FreeCAD.CreateLayer("GIS_Annotation")	
			textDataCadastralParcels = GIS2BIM.DataFromWFS(GIS2BIM_NL.NLPDOKCadastreCadastralParcelsNummeraanduiding,Bbox,GIS2BIM_NL.NLPDOKxPathOpenGISPos,GIS2BIM_NL.xPathStringsCadastreTextAngle,-float(self.X),-float(self.Y),1000,3)
			textDataOpenbareRuimtenaam = GIS2BIM.DataFromWFS(GIS2BIM_NL.NLPDOKCadastreOpenbareruimtenaam,Bbox,GIS2BIM_NL.NLPDOKxPathOpenGISPos,GIS2BIM_NL.xPathStringsCadastreTextAngle,-float(self.X),-float(self.Y),1000,3)
			placeTextFreeCAD1 = GIS2BIM_FreeCAD.PlaceText(textDataCadastralParcels,500,0)
			placeTextFreeCAD2 = GIS2BIM_FreeCAD.PlaceText(textDataOpenbareRuimtenaam,2000,1)
			FreeCAD.activeDocument().getObject("GIS_Annotation").addObjects(placeTextFreeCAD1)
			FreeCAD.activeDocument().getObject("GIS_Annotation").addObjects(placeTextFreeCAD2)
			FreeCAD.activeDocument().getObject("PDOK").addObject(FreeCAD.activeDocument().getObject("GIS_Annotation"))

		#Create Ruimtelijke plannen outline 2D
		if self.clsBouwvlak.isChecked() is True:
			GIS_2D_Ruimtelijke_Plannen = GIS2BIM_FreeCAD.CreateLayer("GIS_2D_Ruimtelijke_Plannen")	
			RuimtelijkePlannenBouwvlakCurves = GIS2BIM_FreeCAD.CurvesFromWFS(GIS2BIM_NL.NLRuimtelijkeplannenBouwvlak,Bbox,".//{http://www.opengis.net/gml}posList",-float(self.X),-float(self.Y),1000,3,False, False,u"Solid",(0.0,0.0,1.0))
			FreeCAD.activeDocument().getObject("GIS_2D_Ruimtelijke_Plannen").addObjects(RuimtelijkePlannenBouwvlakCurves)
			FreeCAD.activeDocument().getObject("PDOK").addObject(FreeCAD.activeDocument().getObject("GIS_2D_Ruimtelijke_Plannen"))

		#Create BGT 2D
		if self.clsBGT.isChecked() is True:
			timeout = 150
			folderBGT = GIS2BIM_FreeCAD.CreateTempFolder(self.tempFolderName+ '/BGT')	
			filepathZIP = folderBGT + '.zip'
			
			#Download BGT
			URL = GIS2BIM_NL.bgtDownloadURL(float(self.X),float(self.Y),float(self.bboxWidth.text()),float(self.bboxHeight.text()),timeout)
			GIS2BIM.downloadUnzip(URL,filepathZIP,folderBGT)
			
			#Create Curves
			
			bgt_curves_faces = ["bgt_begroeidterreindeel",
			"bgt_onbegroeidterreindeel",
			"bgt_ondersteunendwaterdeel",
			"bgt_ondersteunendwegdeel",
			"bgt_overbruggingsdeel",
			"bgt_overigbouwwerk",
			"bgt_waterdeel",
			"bgt_wegdeel"]
			
			bgt_curves_faces_color = [(223/255,230/255,208/255),
			(223/255,230/255,208/255),
			(205/255,230/255,237/255),
			(226/255,226/255,226/255),
			(234/255,234/255,234/255),
			(220/255,155/255,140/255),
			(205/255,230/255,237/255),
			(234/255,234/255,234/255)]
			
			bgt_curves_lines = ["bgt_functioneelgebied",
			"bgt_gebouwinstallatie",
			"bgt_kunstwerkdeel",
			"bgt_overbruggingsdeel",
			"bgt_overigbouwwerk",
			"bgt_overigescheiding",
			"bgt_scheiding",
			"bgt_spoor",
			"bgt_tunneldeel"]

			xpath = './/{http://www.opengis.net/gml}posList'

			GIS2BIM_FreeCAD.CreateLayer("BGT")

			#Draw bgt_curves_lines
			for i in bgt_curves_lines:
				path = folderBGT + '/' + i + '.gml'
				tree = ET.parse(path)
				Curves = GIS2BIM_FreeCAD.CurvesFromGML(tree,xpath,-float(self.X),-float(self.Y),float(self.bboxWidth.text()),float(self.bboxHeight.text()),1000,0,0,0,"Solid",(0.7,0.0,0.0),(0.0,0.0,0.0))
				GIS2BIM_FreeCAD.CreateLayer(i)
				FreeCAD.activeDocument().getObject(i).addObjects(Curves)
				FreeCAD.activeDocument().getObject("BGT").addObject(FreeCAD.activeDocument().getObject(i))
				FreeCAD.ActiveDocument.recompute()

			for i,j in zip(bgt_curves_faces,bgt_curves_faces_color):
				path = folderBGT + '/' + i + '.gml'
				tree = ET.parse(path)
				Curves = GIS2BIM_FreeCAD.CurvesFromGML(tree,xpath,-float(self.X),-float(self.Y),float(self.bboxWidth.text()),float(self.bboxHeight.text()),1000,2,1,1,"Solid",(0.7,0.0,0.0),j)
				GIS2BIM_FreeCAD.CreateLayer(i)
				FreeCAD.activeDocument().getObject(i).addObjects(Curves)
				FreeCAD.activeDocument().getObject("BGT").addObject(FreeCAD.activeDocument().getObject(i))
				FreeCAD.ActiveDocument.recompute()

			FreeCAD.activeDocument().getObject("PDOK").addObject(FreeCAD.activeDocument().getObject("BGT"))

		# Import bestemmingsplankaart
		if self.clsBestemmingsplan.isChecked() is True:
			GIS_Raster = GIS2BIM_FreeCAD.CreateLayer("GIS_Raster")	
			a = GIS2BIM.WMSRequest(GIS2BIM.GetWebServerData("NL_INSPIRE_Ruimtelijke_Plannen_Totaal_28992", "webserverRequests", "serverrequestprefix"),Bbox,fileLocationWMS,3000,3000)
			ImageAerialPhoto = GIS2BIM_FreeCAD.ImportImage(fileLocationWMS,width,height,1000,"Ruimtelijke Plannen",0,0)
			ImageAerialPhoto.addProperty("App::PropertyString","WMSRequestURL")
			ImageAerialPhoto.WMSRequestURL = a[2]
			FreeCAD.activeDocument().getObject("GIS_Raster").addObject(FreeCAD.activeDocument().getObject(ImageAerialPhoto.Label))
			FreeCAD.activeDocument().getObject("PDOK").addObject(FreeCAD.activeDocument().getObject("GIS_Raster"))

		FreeCAD.ActiveDocument.recompute()
		self.close()
		
	def onCancel(self):
		self.close()

#form = GIS_NL_Dialog()
#form.exec_()
