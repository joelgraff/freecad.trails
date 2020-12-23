# /**********************************************************************
# *                                                                     *
# * Copyright (c) 2020 Hakan Seven <hakanseven12@gmail.com>             *
# *                                                                     *
# * This program is free software; you can redistribute it and/or modify*
# * it under the terms of the GNU Lesser General Public License (LGPL)  *
# * as published by the Free Software Foundation; either version 2 of   *
# * the License, or (at your option) any later version.                 *
# * for detail see the LICENCE text file.                               *
# *                                                                     *
# * This program is distributed in the hope that it will be useful,     *
# * but WITHOUT ANY WARRANTY; without even the implied warranty of      *
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the       *
# * GNU Library General Public License for more details.                *
# *                                                                     *
# * You should have received a copy of the GNU Library General Public   *
# * License along with this program; if not, write to the Free Software *
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307*
# * USA                                                                 *
# *                                                                     *
# ***********************************************************************

'''
Create a Point Group Object from FPO.
'''

import FreeCAD, FreeCADGui
from pivy import coin
from freecad.trails import ICONPATH, geo_origin, marker_dict
from . import  point_groups
import random



def get_points():
    """
    Find the existing Point Groups object
    """
    # Return an existing instance of the same name, if found.
    obj = FreeCAD.ActiveDocument.getObject('PointGroup')

    if obj:
        return obj

    obj = create(name="Points")

    return obj

def create(points=[], name='Point Group'):
    group = point_groups.get()
    obj=FreeCAD.ActiveDocument.addObject("App::FeaturePython", "PointGroup")
    obj.Label = name
    PointGroup(obj)
    obj.Points = points
    ViewProviderPointGroup(obj.ViewObject)
    group.addObject(obj)
    FreeCAD.ActiveDocument.recompute()

    return obj


class PointGroup:
    """
    This class is about Point Group Object data features.
    """

    def __init__(self, obj):
        '''
        Set data properties.
        '''

        self.Type = 'Trails::PointGroup'

        obj.addProperty(
            "App::PropertyStringList", "PointNames", "Base",
            "List of group points").PointNames = []

        obj.addProperty(
            "App::PropertyVectorList", "Points", "Base",
            "List of group points").Points = []

        obj.addProperty(
            "App::PropertyStringList", "Descriptions", "Base",
            "List of group points").Descriptions = []

        obj.addProperty(
            "App::PropertyEnumeration", "Marker", "Base",
            "List of point markers").Marker = [*marker_dict]

        obj.Proxy = self

    def onChanged(self, obj, prop):
        '''
        Do something when a data property has changed.
        '''
        if prop == "Points":
            points = obj.getPropertyByName("Points")
            if points:
                origin = geo_origin.get(points[0])

    def execute(self, obj):
        '''
        Do something when doing a recomputation. 
        '''
        return


class ViewProviderPointGroup:
    """
    This class is about Point Group Object view features.
    """

    def __init__(self, vobj):
        '''
        Set view properties.
        '''
        (r, g, b) = (random.random(), random.random(), random.random())

        vobj.addProperty(
            "App::PropertyBool", "Labels", "Base",
            "Show/hide labels").Labels = False

        vobj.addProperty(
            "App::PropertyBool", "Name", "Labels",
            "Show point name labels").Name = False

        vobj.addProperty(
            "App::PropertyBool", "NortingEasting", "Labels",
            "Show norting easting labels").NortingEasting = False

        vobj.addProperty(
            "App::PropertyBool", "Elevation", "Labels",
            "Show elevation labels").Elevation = False

        vobj.addProperty(
            "App::PropertyBool", "Description", "Labels",
            "Show description labels").Description = False

        vobj.addProperty(
            "App::PropertyColor", "PointColor", "Point Style",
            "Color of the point group").PointColor = (r, g, b)

        vobj.addProperty(
            "App::PropertyFloatConstraint", "PointSize", "Point Style",
            "Size of the point group").PointSize = (3.0, 1.0, 20.0, 1.0)

        vobj.Proxy = self

    def attach(self, vobj):
        '''
        Create Object visuals in 3D view.
        '''
        # GeoCoord Node.
        self.geo_coords = coin.SoGeoCoordinate()

        # Point group features.
        points = coin.SoPointSet()
        self.markers = coin.SoMarkerSet()
        self.color_mat = coin.SoMaterial()
        self.point_normal = coin.SoNormal()
        self.point_style = coin.SoDrawStyle()
        self.point_style.style = coin.SoDrawStyle.POINTS

        # Highlight for selection.
        highlight = coin.SoType.fromName('SoFCSelection').createInstance()
        #highlight.documentName.setValue(FreeCAD.ActiveDocument.Name)
        #highlight.objectName.setValue(vobj.Object.Name)
        #highlight.subElementName.setValue("Main")
        highlight.addChild(self.geo_coords)
        highlight.addChild(points)
        highlight.addChild(self.markers)

        # Point labels features.
        color =coin.SoBaseColor()
        self.point_labels = coin.SoSeparator()
        self.point_labels.addChild(color)

        # Point group root.
        point_root = coin.SoSeparator()
        point_root.addChild(self.point_labels)
        point_root.addChild(self.point_style)
        point_root.addChild(self.point_normal)
        point_root.addChild(self.color_mat)
        point_root.addChild(highlight)
        vobj.addDisplayMode(point_root,"Point")

        # Take features from properties.
        if vobj.Object.Points: self.onChanged(vobj,"Elevation")
        self.onChanged(vobj,"PointSize")
        self.onChanged(vobj,"PointColor")

    def onChanged(self, vobj, prop):
        '''
        Update Object visuals when a view property changed.
        '''
        labels = vobj.getPropertyByName("Labels")
        if labels:
            if prop == "Name" or prop == "NortingEasting" or prop == "Elevation" or prop == "Description":
                self.point_labels.removeAllChildren()
                origin = geo_origin.get(vobj.Object.Points[0])

                show_name = vobj.getPropertyByName("Name")
                show_ne = vobj.getPropertyByName("NortingEasting")
                show_z = vobj.getPropertyByName("Elevation")
                show_des = vobj.getPropertyByName("Description")

                for vector in vobj.Object.Points:
                    font = coin.SoFont()
                    font.size = 1000
                    point_label = coin.SoSeparator()
                    location = coin.SoTranslation()
                    text = coin.SoAsciiText()
                    index = vobj.Object.Points.index(vector)
                    labels =[]

                    if show_name: labels.append(vobj.Object.PointNames[index])
                    if show_ne: labels.extend([str(vector.x/1000), str(vector.y/1000)])
                    if show_z: labels.append(str(vector.z/1000))
                    if show_des and vobj.Object.Descriptions: labels.append(vobj.Object.Descriptions[index])

                    location.translation = vector.sub(FreeCAD.Vector(origin.Origin.x, origin.Origin.y, 0))
                    text.string.setValues(labels)
                    point_label.addChild(font)
                    point_label.addChild(location)
                    point_label.addChild(text)
                    self.point_labels.addChild(point_label)

        if prop == "PointSize":
            size = vobj.getPropertyByName("PointSize")
            self.point_style.pointSize = size

        if prop == "PointColor":
            color = vobj.getPropertyByName("PointColor")
            self.color_mat.diffuseColor = (color[0],color[1],color[2])

    def updateData(self, obj, prop):
        '''
        Update Object visuals when a data property changed.
        '''
        if prop == "Points":
            points = obj.getPropertyByName("Points")
            if points:
                origin = geo_origin.get(points[0])

                geo_system = ["UTM", origin.UtmZone, "FLAT"]
                self.geo_coords.geoSystem.setValues(geo_system)
                self.geo_coords.point.values = points

        if prop == "Marker":
            marker = obj.getPropertyByName("Marker")
            self.markers.markerIndex = marker_dict[marker]

    def getDisplayModes(self, vobj):
        '''
        Return a list of display modes.
        '''
        modes=[]
        modes.append("Point")

        return modes

    def getDefaultDisplayMode(self):
        '''
        Return the name of the default display mode.
        '''
        return "Point"

    def setDisplayMode(self,mode):
        '''
        Map the display mode defined in attach with 
        those defined in getDisplayModes.
        '''
        return mode

    def getIcon(self):
        '''
        Return object treeview icon.
        '''
        return ICONPATH + '/icons/PointGroup.svg'

    def __getstate__(self):
        """
        Save variables to file.
        """
        return None
 
    def __setstate__(self,state):
        """
        Get variables from file.
        """
        return None