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

__title__= "GIS2BIM_FreeCAD"
__author__ = "Maarten Vroegindeweij"
__url__ = "https://github.com/DutchSailor/GIS2BIM"

from . import GIS2BIM
import importlib
importlib.reload(GIS2BIM)

import Draft
import Part
import Arch
import os
import re
import json

import FreeCAD
import Mesh

from PySide2 import QtWidgets

SiteName = "GIS-Sitedata"
TempFolderName = "GIStemp/"

def getFreeCADGISData(self):
	self.sitename = SiteName

	#Get/set parameters for GIS
	self.tempFolderName = "GIStemp/"
	self.X = GIS2BIM_FreeCAD.ArchSiteCreateCheck(self.sitename).CRS_x
	self.Y = GIS2BIM_FreeCAD.ArchSiteCreateCheck(self.sitename).CRS_y
	self.lat = str(GIS2BIM_FreeCAD.ArchSiteCreateCheck(self.sitename).WGS84_Latitude)
	self.lon = str(GIS2BIM_FreeCAD.ArchSiteCreateCheck(self.sitename).WGS84_Longitude)
	self.bboxWidthStart = GIS2BIM_FreeCAD.ArchSiteCreateCheck(self.sitename).BoundingboxWidth
	self.bboxHeightStart = GIS2BIM_FreeCAD.ArchSiteCreateCheck(self.sitename).BoundingboxHeight
	self.CRS = str(GIS2BIM_FreeCAD.ArchSiteCreateCheck(self.sitename).CRS_EPSG_SRID)
	self.CRSDescription = str(GIS2BIM_FreeCAD.ArchSiteCreateCheck(self.sitename).CRS_EPSG_Description)
	self.bboxString = GIS2BIM.CreateBoundingBox(GIS2BIM_FreeCAD.ArchSiteCreateCheck(self.sitename).CRS_x,GIS2BIM_FreeCAD.ArchSiteCreateCheck(self.sitename).CRS_y,self.bboxWidthStart,self.bboxHeightStart,0)
	

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

def CurvesFromWFS(serverName,boundingBoxString,xPathString,dx,dy,scale,DecimalNumbers,closedValue,Face,DrawStyle,LineColor):
    curves = GIS2BIM.PointsFromWFS(serverName,boundingBoxString,xPathString,dx,dy,scale,DecimalNumbers)
    FCcurves = []
    for i in curves:
        pointlist = []
        for j in i:
            pointlist.append(FreeCAD.Vector(j[0], j[1], 0))
        a = Draft.makeWire(pointlist, closed=closedValue)
        a.MakeFace = Face
        a.ViewObject.DrawStyle = DrawStyle
        a.ViewObject.LineColor = LineColor
        FCcurves.append(a)
    return FCcurves

def checkIfCoordIsInsideBoundingBox(coord, min_x, min_y, max_x, max_y):
	if re.match(r'^-?\d+(?:\.\d+)$', coord[0]) is None or re.match(r'^-?\d+(?:\.\d+)$', coord[1]) is None:
		return False
	else:
		if min_x <= float(coord[0]) <= max_x and min_y <= float(coord[1]) <= max_y:
			return True
		else:
		    return False
			
def CurvesFromGML(tree,xPathString,dx,dy,BoxWidth,BoxHeight,scale,DecimalNumbers,closedValue,Face,DrawStyle,LineColor,ShapeColor):
    bbx = -dx
    bby = -dy
	
    # Bounding box definition
    bounding_box = [bbx, bby, BoxWidth,BoxHeight]
    min_x = bounding_box[0] - (bounding_box[2]/2)
    min_y = bounding_box[1] - (bounding_box[3]/2)
    max_x = bounding_box[0] + (bounding_box[2]/2)
    max_y = bounding_box[1] + (bounding_box[3]/2)

    # get data from xml
    root = tree.getroot()

    # for loop to get each element in an array
    XMLelements = []
    for elem in root.iter():
        XMLelements.append(elem)

    xpathfound = root.findall(xPathString)

    # for loop to get all polygons in an array
    FCcurves = []
    for x in xpathfound:
        if x.text:
            try:
                newPolygon = x.text.split(" ")
                polygon_is_inside_bounding_box = False
                x = 0
                xyPolygon = []
                for i in range(0, int(len(newPolygon) / 2)):
                    xy_coord = [newPolygon[x], newPolygon[x + 1]]
                    xy_coord_trans = [round((float(newPolygon[x])-bbx)*scale), round((float(newPolygon[x + 1])-bby)*scale)]
                    xyPolygon.append(xy_coord_trans)
                    x += 2
                    if checkIfCoordIsInsideBoundingBox(xy_coord, min_x, min_y, max_x, max_y):
                        polygon_is_inside_bounding_box = True
                if polygon_is_inside_bounding_box:
                   # xyPolygons.append(xyPolygon)
                    pointlist = []
                    for j in xyPolygon:
                        pointlist.append(FreeCAD.Vector(j[0], j[1], 0))
                    a = Draft.makeWire(pointlist, closed=closedValue)
                    a.MakeFace = Face
                    a.ViewObject.DrawStyle = DrawStyle
                    a.ViewObject.LineColor = LineColor
                    a.ViewObject.ShapeColor = ShapeColor
                    FCcurves.append(a)
            except:
                FCcurves.append("_none_")
        else:
            FCcurves.append("_none_")
    return FCcurves

def PlaceText(textData,fontSize, upper):
    Texts = []
    for i, j, k in zip(textData[0], textData[1], textData[2]):
        ZAxis = FreeCAD.Vector(0, 0, 1)
        p1 = FreeCAD.Vector(i[0][0], i[0][1], 0)
        Place1 = FreeCAD.Placement(p1, FreeCAD.Rotation(ZAxis, -float(j)))
        if upper:
           k = k.upper()
        else: k
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
		FreeCAD.activeDocument().addObject("App::DocumentObjectGroupPython", layerName)
	obj2 = FreeCAD.activeDocument().getObject(layerName)
	return obj2

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

def CityJSONImport(jsonFile,dX,dY,LODnumber,bboxWidth,bboxHeight):
	#Import CityJSON File, jsonfilename, dx and dy in string/meters. Proof of Concept, very buggy and incomplete.
	layer = CreateLayer("CityJSON")	
	data = json.load(open(jsonFile,))
	vert = data['vertices']
	cityobj = data['CityObjects']
	translate = data['transform']['translate']
	scaleX = data['transform']['scale'][0]
	scaleY = data['transform']['scale'][1]
	scaleZ = data['transform']['scale'][2]
	translatex = (translate[0] -float(dX))/scaleX
	translatey = (translate[1] -float(dY))/scaleY
	translatez = -translate[2]/scaleZ
	
	meshes = []
	for i in cityobj:
		objName = i
		for j in data['CityObjects'][objName]['geometry'][2]['boundaries']:	
			facets = []
			for k in j:
				coord = (str(vert[k[0][0]][0]+translatex), str(vert[k[0][0]][1]+translatey))					
				if checkIfCoordIsInsideBoundingBox(coord,-500*float(bboxWidth),-500*float(bboxHeight),500*float(bboxWidth),500*float(bboxHeight)):				
					facets.append(((vert[k[0][0]][0]+translatex, vert[k[0][0]][1]+translatey, vert[k[0][0]][2]+translatez),(vert[k[0][1]][0]+translatex, vert[k[0][1]][1]+translatey, vert[k[0][1]][2]+translatez),(vert[k[0][2]][0]+translatex, vert[k[0][2]][1]+translatey, vert[k[0][2]][2]+translatez)))
				else: pass
			m = Mesh.Mesh(facets)
			f = FreeCAD.activeDocument().addObject("Mesh::Feature", objName)
			f.Mesh = m
			meshes.append(f)
			FreeCAD.activeDocument().getObject("CityJSON").addObject(f)
	return meshes
	
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