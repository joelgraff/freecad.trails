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



def create(cluster=None):
    obj=FreeCAD.ActiveDocument.addObject("App::FeaturePython", "GuideLines")
    obj.Label = "Guide Lines"
    PointGroup(obj)
    ViewProviderPointGroup(obj.ViewObject)
    cluster.addObject(obj)
    FreeCAD.ActiveDocument.recompute()

    return obj


class PointGroup:
    """
    This class is about Guide Lines object data features.
    """

    def __init__(self, obj):
        '''
        Set data properties.
        '''

        self.Type = 'Trails::GuideLines'

        obj.addProperty(
            "App::PropertyLength", "StartStation", "Base",
            "Guide lines start station").StartStation = 0

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
        vobj.addProperty(
            "App::PropertyColor", "PointColor", "Point Style",
            "Color of the point group").PointColor = (r, g, b)

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