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
            "App::PropertyVectorList",
            "Points",
            "Base",
            "List of group points").Points = ()

        obj.addProperty(
            "App::PropertyEnumeration",
            "Marker",
            "Base",
            "List of point markers").Marker = [*marker_dict]

        obj.Proxy = self

        self.Base = None
        self.Points = None

    def onChanged(self, fp, prop):
        '''
        Do something when a data property has changed.
        '''
        # fp is feature python.
        if prop == "Points":
            points = fp.getPropertyByName("Points")
            if points:
                origin = geo_origin.get(points[0])


    def execute(self, fp):
        '''
        Do something when doing a recomputation. 
        '''
        return


class ViewProviderPointGroup:
    """
    This class is about Point Group Object view features.
    """

    def __init__(self, obj):
        '''
        Set view properties.
        '''
        (r, g, b) = (random.random(),
                     random.random(),
                     random.random())

        obj.addProperty(
            "App::PropertyColor",
            "PointColor",
            "Point Style",
            "Color of the point group").PointColor = (r, g, b)

        obj.addProperty(
            "App::PropertyFloatConstraint",
            "PointSize",
            "Point Style",
            "Size of the point group").PointSize = (3.0)

        obj.Proxy = self

        obj.PointSize = (3.0, 1.0, 20.0, 1.0)

    def attach(self, obj):
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
        #highlight.objectName.setValue(obj.Object.Name)
        #highlight.subElementName.setValue("Main")
        highlight.addChild(self.geo_coords)
        highlight.addChild(points)
        highlight.addChild(self.markers)

        # Point group root.
        point_root = coin.SoSeparator()
        point_root.addChild(self.point_style)
        point_root.addChild(self.point_normal)
        point_root.addChild(self.color_mat)
        point_root.addChild(highlight)
        obj.addDisplayMode(point_root,"Point")

        # Take features from properties.
        self.onChanged(obj,"PointSize")
        self.onChanged(obj,"PointColor")

    def onChanged(self, vp, prop):
        '''
        Update Object visuals when a view property changed.
        '''
        # vp is view provider.
        if prop == "PointSize":
            size = vp.getPropertyByName("PointSize")
            self.point_style.pointSize = size

        if prop == "PointColor":
            color = vp.getPropertyByName("PointColor")
            self.color_mat.diffuseColor = (color[0],color[1],color[2])

    def updateData(self, fp, prop):
        '''
        Update Object visuals when a data property changed.
        '''
        # fp is feature python.
        if prop == "Points":
            points = fp.getPropertyByName("Points")
            if points:
                origin = geo_origin.get(points[0])

                geo_system = ["UTM", origin.UtmZone, "FLAT"]
                self.geo_coords.geoSystem.setValues(geo_system)
                self.geo_coords.point.values = points

        if prop == "Marker":
            marker = fp.getPropertyByName("Marker")
            self.markers.markerIndex = marker_dict[marker]

    def getDisplayModes(self,obj):
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