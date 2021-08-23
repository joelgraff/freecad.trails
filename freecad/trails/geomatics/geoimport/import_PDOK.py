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

# PDOK Importer

#import statements

from PySide import QtGui, QtCore

import FreeCAD

import GIS2BIM
import GIS2BIM_FreeCAD
import GIS2BIM_CRS
import GIS2BIM_NL

# UI Class definitions

class PDOK_Dialog(QtGui.QDialog):
	""""""
	def __init__(self):
		super(PDOK_Dialog, self).__init__()
		self.initUI()

	def initUI(self):
		SiteName = "GIS-Sitedata"
		self.X = str(GIS2BIM_FreeCAD.ArchSiteCreateCheck(SiteName).CRS_x)
		self.Y = str(GIS2BIM_FreeCAD.ArchSiteCreateCheck(SiteName).CRS_y)
		BoundingboxWidth = str(GIS2BIM_FreeCAD.ArchSiteCreateCheck(SiteName).BoundingboxWidth)
		BoundingboxHeight = str(GIS2BIM_FreeCAD.ArchSiteCreateCheck(SiteName).BoundingboxHeight)
		self.TempFolderName = "GIStemp/"
		self.TempFolderPath = GIS2BIM_FreeCAD.CreateTempFolder(self.TempFolderName)
		# create our window
		self.setGeometry(250, 250, 400, 400)
		self.setWindowTitle("Load GIS-data PDOK Netherlands")
		self.setWindowFlags(QtCore.Qt.WindowStaysOnTopHint)
		# create some Labels
		self.label1 = QtGui.QLabel("Rdx(EPSG 28992)", self)
		self.label1.move(20, 20)
		#
		self.numericInput1Rdx = QtGui.QLineEdit(self)
		self.numericInput1Rdx.setText(self.X)
		self.numericInput1Rdx.setFixedWidth(100)
		self.numericInput1Rdx.move(250, 20)
		#
		self.label2 = QtGui.QLabel("Rdy(EPSG 28992)", self)
		self.label2.move(20, 50)
		#
		self.numericInput2Rdy = QtGui.QLineEdit(self)
		self.numericInput2Rdy.setText(self.Y)
		self.numericInput2Rdy.setFixedWidth(100)
		self.numericInput2Rdy.move(250, 50)
		#
		self.label3 = QtGui.QLabel("Boundingbox Width(m)", self)
		self.label3.move(20, 80)
		#
		self.numericInput3Width = QtGui.QLineEdit(self)
		self.numericInput3Width.setInputMask("")
		self.numericInput3Width.setText(BoundingboxWidth)
		self.numericInput3Width.setFixedWidth(100)
		self.numericInput3Width.move(250, 80)
		#
		self.label4 = QtGui.QLabel("Boundingbox Height(m)", self)
		self.label4.move(20, 110)
		#
		self.numericInput4Height = QtGui.QLineEdit(self)
		self.numericInput4Height.setInputMask("")
		self.numericInput4Height.setText(BoundingboxHeight)
		self.numericInput4Height.setFixedWidth(100)
		self.numericInput4Height.move(250, 110)
		# checkboxes
		self.checkbox1 = QtGui.QCheckBox("Cadastral Parcels 2D", self)
		self.checkbox1.move(20,140)
		#
		self.checkbox2 = QtGui.QCheckBox("Building Outline 2D", self)
		self.checkbox2.move(20,170)
		#
		self.checkbox3 = QtGui.QCheckBox("3D Buildings", self)
		self.checkbox3.move(20,200)
		#
		self.checkbox4 = QtGui.QCheckBox("2D Aerialphoto 2020", self)
		self.checkbox4.move(20,230)
		#
		self.checkbox5 = QtGui.QCheckBox("GIS 2D Annotation", self)
		self.checkbox5.move(20,260)
		#
		#self.checkbox6 = QtGui.QCheckBox("2D Bestemmingsplan Bouwvlak Vector", self)
		#self.checkbox6.move(20,290)
		#
		# cancel button
		cancelButton = QtGui.QPushButton('Cancel', self)
		cancelButton.clicked.connect(self.onCancel)
		cancelButton.setAutoDefault(True)
		cancelButton.move(100, 330)
		# OK button
		okButton = QtGui.QPushButton('OK', self)
		okButton.clicked.connect(self.onOk)
		okButton.move(20, 330)
		# now make the window visible
		self.show()
		#
	def onCancel(self):
		self.close()
		
	def onOk(self):
		Rdx = float(self.numericInput1Rdx.text())
		Rdy = float(self.numericInput2Rdy.text())
		width = float(self.numericInput3Width.text())
		height = float(self.numericInput4Height.text())
		CadastralParcels2D = self.checkbox1.isChecked()
		BuildingOutline2D = self.checkbox2.isChecked()
		Buildings3D = self.checkbox3.isChecked()
		Aerialphoto2D = self.checkbox4.isChecked()
		GIS2DAnnotation = self.checkbox5.isChecked()
		#Bestemmingsplan = self.checkbox6.isChecked()

		Bbox = GIS2BIM.CreateBoundingBox(Rdx,Rdy,width,height,2)

		fileLocationWMS = self.TempFolderPath + "wms.jpg"

		#Create Cadastral Parcels 2D
		if CadastralParcels2D is True:
			GIS_2D_Cadastral_Parcel = GIS2BIM_FreeCAD.CreateLayer("GIS_2D_Cadastral_Parcel")	
			CadastralParcelCurves = GIS2BIM_FreeCAD.CurvesFromWFS(GIS2BIM_NL.NLPDOKCadastreCadastralParcels,Bbox,GIS2BIM_NL.NLPDOKxPathOpenGISposList,-Rdx,-Rdy,1000,3,False,False,u"Dashdot",(0.0,0.0,0.0))
			FreeCAD.activeDocument().getObject("GIS_2D_Cadastral_Parcel").addObjects(CadastralParcelCurves)

		#Create Building outline 2D
		if BuildingOutline2D is True:
			GIS_2D_Building_Outline = GIS2BIM_FreeCAD.CreateLayer("GIS_2D_Building_Outline")	
			BAGCurves = GIS2BIM_FreeCAD.CurvesFromWFS(GIS2BIM_NL.NLPDOKBAGBuildingCountour,Bbox,GIS2BIM_NL.NLPDOKxPathOpenGISposList,-Rdx,-Rdy,1000,3,True, True,u"Solid",(0.7,0.0,0.0))
			FreeCAD.activeDocument().getObject("GIS_2D_Building_Outline").addObjects(BAGCurves)

		#Create 3D Building
		if Buildings3D is True:
			GIS_3D = GIS2BIM_FreeCAD.CreateLayer("GIS_3D")	
			curves3DBAG = GIS2BIM.PointsFromWFS(GIS2BIM_NL.NLTUDelftBAG3DV1,Bbox,GIS2BIM_NL.NLPDOKxPathOpenGISPosList2,-Rdx,-Rdy,1000,3)
			heightData3DBAG = GIS2BIM.DataFromWFS(GIS2BIM_NL.NLTUDelftBAG3DV1,Bbox,GIS2BIM_NL.NLPDOKxPathOpenGISPosList2,GIS2BIM_NL.xPathStrings3DBag,-Rdx,-Rdy,1000,3)
			BAG3DSolids = GIS2BIM_FreeCAD.Buildings3D(curves3DBAG,heightData3DBAG)
			FreeCAD.activeDocument().getObject("GIS_3D").addObjects(BAG3DSolids)

		# Import Aerialphoto in view

		if Aerialphoto2D is True:
			GIS_Raster = GIS2BIM_FreeCAD.CreateLayer("GIS_Raster")	
			a = GIS2BIM.WMSRequest(GIS2BIM.GetWebServerData("NL_PDOK_Luchtfoto_2020_28992", "webserverRequests", "serverrequestprefix"),Bbox,fileLocationWMS,3000,3000)
			print(a)
			ImageAerialPhoto = GIS2BIM_FreeCAD.ImportImage(fileLocationWMS,width,height,1000,"luchtfoto2020",0,0)
			ImageAerialPhoto.addProperty("App::PropertyString","WMSRequestURL")
			ImageAerialPhoto.WMSRequestURL = a[2]
			FreeCAD.activeDocument().getObject("GIS_Raster").addObject(App.activeDocument().getObject(ImageAerialPhoto.Label))
			
		#Create Textdata Cadastral Parcels
		if GIS2DAnnotation is True:
			GIS_Annotation = GIS2BIM_FreeCAD.CreateLayer("GIS_Annotation")	
			textDataCadastralParcels = GIS2BIM.DataFromWFS(GIS2BIM_NL.NLPDOKCadastreCadastralParcelsNummeraanduiding,Bbox,GIS2BIM_NL.NLPDOKxPathOpenGISPos,GIS2BIM_NL.xPathStringsCadastreTextAngle,-Rdx,-Rdy,1000,3)
			textDataOpenbareRuimtenaam = GIS2BIM.DataFromWFS(GIS2BIM_NL.NLPDOKCadastreOpenbareruimtenaam,Bbox,GIS2BIM_NL.NLPDOKxPathOpenGISPos,GIS2BIM_NL.xPathStringsCadastreTextAngle,-Rdx,-Rdy,1000,3)
			placeTextFreeCAD1 = GIS2BIM_FreeCAD.PlaceText(textDataCadastralParcels,500,0)
			placeTextFreeCAD2 = GIS2BIM_FreeCAD.PlaceText(textDataOpenbareRuimtenaam,2000,1)
			FreeCAD.activeDocument().getObject("GIS_Annotation").addObjects(placeTextFreeCAD1)
			FreeCAD.activeDocument().getObject("GIS_Annotation").addObjects(placeTextFreeCAD2)

		#Create Ruimtelijke plannen outline 2D
		#if Bestemmingsplan is True:
		#	GIS_2D_Ruimtelijke_Plannen = GIS2BIM_FreeCAD.CreateLayer("GIS_2D_Ruimtelijke_Plannen")	
		#	RuimtelijkePlannenBouwvlakCurves = GIS2BIM_FreeCAD.CurvesFromWFS(GIS2BIM_NL.NLRuimtelijkeplannenBouwvlak,Bbox,GIS2BIM_NL.NLPDOKxPathOpenGISposList,-Rdx,-Rdy,1000,3,False, False,u"Solid",(0.0,0.0,1.0))
		#	App.activeDocument().getObject("GIS_2D_Ruimtelijke_Plannen").addObjects(RuimtelijkePlannenBouwvlakCurves)
			
		FreeCAD.ActiveDocument.recompute()
		self.close()

#form = PDOK_Dialog()
#form.exec_()