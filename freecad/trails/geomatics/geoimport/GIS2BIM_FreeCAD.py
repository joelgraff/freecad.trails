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

__title__= "GIS2BIM_FreeCAD"
__author__ = "Maarten Vroegindeweij"
__url__ = "https://github.com/DutchSailor/GIS2BIM"

import GIS2BIM
import Draft
import Part
import FreeCAD
import Arch
import os
from PySide2 import QtCore, QtWidgets, QtGui

SiteName = "Geo-Sitedata"
TempFolderName = "GIStemp/"

def CreateTempFolder(Name):
#Create a temporary subfolder in the folder of the projectfile to store temporary GIS-files
	FileName = FreeCAD.ActiveDocument.FileName
	if len(str(FreeCAD.ActiveDocument.FileName)) < 1:
		dialog = QtWidgets.QMessageBox()
		dialog.setText("Please save your project so that FreeCAD-GIS can create a temporary folder for GIS-files")
		dialog.setWindowTitle("Warning")
		dialog.exec_() 
	else:
		NewFolder = os.path.dirname(FileName) + "/" + Name
		if os.path.exists(NewFolder):
			NewFolder
		else:
			os.mkdir(NewFolder)
	return NewFolder

def ImportImage(fileLocation,width,height,scale,name,dx,dy):
#Import image in view
    Img = FreeCAD.activeDocument().addObject('Image::ImagePlane',name)
    Img.ImageFile = fileLocation
    Img.XSize = width*scale
    Img.YSize = height*scale
    Img.Placement = FreeCAD.Placement(FreeCAD.Vector(dx,dy,0.000000),FreeCAD.Rotation(0.000000,0.000000,0.000000,1.000000))
    return Img

def Buildings3D(curves3DBAG,heightData3DBAG):
    solids = []
    for i,j,k in zip(curves3DBAG,heightData3DBAG[1],heightData3DBAG[2]):
        pointlist = []
        for curve in i:
            pointlist.append(FreeCAD.Vector(curve[0], curve[1], float(j)*1000))
        a = Part.makePolygon(pointlist)
        face = Part.Face(a)
        solid = face.extrude(FreeCAD.Vector(0, 0, float(k) * 1000))
        sld = Part.show(solid)
        solids.append(sld)
    return solids

def CurvesFromWFS(serverName,boundingBoxString,xPathString,dx,dy,scale,DecimalNumbers,XYZCountDimensions,closedValue,DrawStyle,LineColor):
    curves = GIS2BIM.PointsFromWFS(serverName,boundingBoxString,xPathString,dx,dy,scale,DecimalNumbers,XYZCountDimensions)
    curvesWFS = []
    for i in curves:
        pointlist = []
        for j in i:
            pointlist.append(FreeCAD.Vector(j[0], j[1], 0))
        a = Draft.makeWire(pointlist, closed=closedValue)
        a.MakeFace = closedValue
        a.ViewObject.DrawStyle = DrawStyle
        a.ViewObject.LineColor = LineColor
        curvesWFS.append(a)
    return curvesWFS

def PlaceText(textData,fontSize, upper):
    Texts = []
    for i, j, k in zip(textData[0], textData[1], textData[2]):
        ZAxis = FreeCAD.Vector(0, 0, 1)
        p1 = FreeCAD.Vector(i[0][0], i[0][1], 0)
        Place1 = FreeCAD.Placement(p1, FreeCAD.Rotation(ZAxis, -float(j)))
        if upper:
           k = k.upper()
        else: k = k
        Text1 = Draft.makeText(k, point=p1)
        Text1.ViewObject.FontSize = fontSize
        Text1.Placement = Place1
        Texts.append(Text1)
    return Texts

def CreateLayer(layerName):
	layerName = layerName.replace(" ","_")
	lstObjects = []
	for obj in FreeCAD.ActiveDocument.Objects: #Check is layername already exists
		lstObjects.append(obj.Label)
	if not layerName in lstObjects:
		layerObj = FreeCAD.activeDocument().addObject("App::DocumentObjectGroup", layerName)
	return layerName

def ArchSiteCreateCheck(SiteName):
#Create an ArchSiteobject which is used to store data nessecary for GIS2BIM. 
	lstObjects = []
	for obj in FreeCAD.ActiveDocument.Objects: #Check is SiteObject already exists and fill parameters
	    lstObjects.append(obj.Label)
	if SiteName in lstObjects: 
		ArchSiteObject = FreeCAD.ActiveDocument.Objects[lstObjects.index(SiteName)]
	else: #Create Siteobject and add parameters
	    ArchSiteObject = Arch.makeSite([],[],SiteName)
	    ArchSiteAddparameters(ArchSiteObject)
		
	return ArchSiteObject

def ArchSiteAddparameters(SiteObject):
	SiteObject.addProperty("App::PropertyString","CRS_EPSG_SRID")
	SiteObject.addProperty("App::PropertyString","CRS_EPSG_Description")
	SiteObject.addProperty("App::PropertyString","WGS84_Longitude")
	SiteObject.addProperty("App::PropertyString","WGS84_Latitude")
	SiteObject.addProperty("App::PropertyFloat","CRS_x")
	SiteObject.addProperty("App::PropertyFloat","CRS_y")
	SiteObject.addProperty("App::PropertyFloat","BoundingboxWidth")
	SiteObject.addProperty("App::PropertyFloat","BoundingboxHeight")
	SiteObject.WGS84_Longitude = "4.659201"
	SiteObject.WGS84_Latitude = "51.814213"
	SiteObject.BoundingboxWidth = 500
	SiteObject.BoundingboxHeight = 500	
	return SiteObject