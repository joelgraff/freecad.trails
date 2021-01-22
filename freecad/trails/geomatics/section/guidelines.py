# /**********************************************************************
# *                                                                     *
# * Copyright (c) 2021 Hakan Seven <hakanseven12@gmail.com>             *
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
Create a Guide Lines object from FPO.
'''

import FreeCAD
from pivy import coin
from freecad.trails import ICONPATH, geo_origin
from .gl_func import GLFunc


def create():
    obj=FreeCAD.ActiveDocument.addObject("App::FeaturePython", "GuideLines")
    obj.Label = "Guide Lines"
    GuideLines(obj)
    ViewProviderGuideLines(obj.ViewObject)
    FreeCAD.ActiveDocument.recompute()

    return obj


class GuideLines(GLFunc):
    """
    This class is about Guide Lines object data features.
    """

    def __init__(self, obj):
        '''
        Set data properties.
        '''

        self.Type = 'Trails::GuideLines'

        obj.addProperty(
            'App::PropertyLink', "Alignment", "Base",
            "Parent alignment").Alignment = None

        obj.addProperty(
            "App::PropertyFloatList", "StationList", "Base",
            "List of stations").StationList = []

        obj.addProperty(
            "App::PropertyLength", "RightOffset", "Offset",
            "Length of right offset").RightOffset = 20000

        obj.addProperty(
            "App::PropertyLength", "LeftOffset", "Offset",
            "Length of left offset").LeftOffset = 20000

        obj.Proxy = self

    def onChanged(self, obj, prop):
        '''
        Do something when a data property has changed.
        '''
        return

    def execute(self, obj):
        '''
        Do something when doing a recomputation. 
        '''
        alignment = obj.getPropertyByName("Alignment")
        stations = obj.getPropertyByName("StationList")
        if alignment and stations:
            left_offset = obj.getPropertyByName("LeftOffset")
            right_offset = obj.getPropertyByName("RightOffset")
            offsets = [left_offset, right_offset]
            lines = self.get_lines(alignment, offsets, stations)


class ViewProviderGuideLines:
    """
    This class is about Point Group Object view features.
    """

    def __init__(self, vobj):
        '''
        Set view properties.
        '''
        vobj.Proxy = self

    def attach(self, vobj):
        '''
        Create Object visuals in 3D view.
        '''
        # GeoCoord Node.
        self.geo_coords = coin.SoGeoCoordinate()

    def onChanged(self, vobj, prop):
        '''
        Update Object visuals when a view property changed.
        '''
        if prop == "PointSize":
            size = vobj.getPropertyByName("PointSize")
            self.point_style.pointSize = size

    def updateData(self, obj, prop):
        '''
        Update Object visuals when a data property changed.
        '''
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
        return ICONPATH + '/icons/GuideLines.svg'

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
