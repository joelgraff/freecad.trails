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
Create a GL Cluster group object from FPO.
'''

import FreeCAD
from freecad.trails import ICONPATH, geo_origin
from . import gl_clusters
from .gl_func import GLFunc



def create(name='GL Cluster', alignment):
    """
    Factory method for GL Cluster.
    """
    clusters = gl_clusters.get()
    clusters.Alignment = alignment

    obj = FreeCAD.ActiveDocument.addObject(
        "App::DocumentObjectGroupPython", 'GLCluster')
    obj.Label = name
    clusters.addObject(obj)

    GLCluster(obj)
    ViewProviderGLCluster(obj.ViewObject)
    FreeCAD.ActiveDocument.recompute()

    return obj


class GLCluster(GLFunc):
    """
    This class is about GL Cluster object data features.
    """

    def __init__(self, obj):
        '''
        Set data properties.
        '''
        self.Type = 'Trails::GLCluster'

        obj.addProperty(
            "App::PropertyBool", "AtHorizontalAlignmentPoints", "Base",
            "Show/hide labels").AtHorizontalAlignmentPoints = True

        obj.addProperty(
            "App::PropertyBool", "FromAlignmentStart", "Base",
            "Show/hide labels").FromAlignmentStart = True

        obj.addProperty(
            "App::PropertyBool", "ToAlignmentEnd", "Base",
            "Show/hide labels").ToAlignmentEnd = True

        obj.addProperty(
            "App::PropertyLength", "StartStation", "Station",
            "Guide lines start station").StartStation = 0

        obj.addProperty(
            "App::PropertyLength", "EndStation", "Station",
            "Guide lines end station").EndStation = 0

        obj.addProperty(
            "App::PropertyLength", "RightOffset", "Offset",
            "Length of right offset").RightOffset = 20000

        obj.addProperty(
            "App::PropertyLength", "LeftOffset", "Offset",
            "Length of left offset").LeftOffset = 20000

        obj.addProperty(
            "App::PropertyLength", "IncrementAlongTangents", "Increment",
            "Distance between guide lines along tangents").IncrementAlongTangents = 10000

        obj.addProperty(
            "App::PropertyLength", "IncrementAlongCurves", "Increment",
            "Distance between guide lines along curves").IncrementAlongCurves = 5000

        obj.addProperty(
            "App::PropertyLength", "IncrementAlongSpirals", "Increment",
            "Distance between guide lines along spirals").IncrementAlongSpirals = 5000

        obj.Proxy = self

    def onChanged(self, fp, prop):
        '''
        Do something when a data property has changed.
        '''
        if prop == "FromAlignmentStart":
            from_start = fp.getPropertyByName("FromAlignmentStart")
            if from_start:
                fp.StartStation = fp.InList[0].Start
        
        if prop == "ToAlignmentEnd":
            to_end = fp.getPropertyByName("ToAlignmentEnd")
            if to_end:
                fp.EndStation = fp.InList[0].End

    def execute(self, fp):
        '''
        Do something when doing a recomputation. 
        '''
        alignment = fp.InList[0].Alignment
        if not alignment: return

        horiz_pnts = fp.getPropertyByName("AtHorizontalAlignmentPoints")
        start = fp.getPropertyByName("StartStation")
        end = fp.getPropertyByName("EndStation")
        right_offset = fp.getPropertyByName("RightOffset")
        left_offset = fp.getPropertyByName("LeftOffset")
        tangent = fp.getPropertyByName("IncrementAlongTangents")
        curve = fp.getPropertyByName("IncrementAlongCurves")
        spiral = fp.getPropertyByName("IncrementAlongSpirals")

        increments = [tangent, curve, spiral]
        ofsets = [left_offset, right_offset]
        region = [start, end]

        self.generate(alignment,increments, ofsets, region, horiz_pnts)



class ViewProviderGLCluster:
    """
    This class is about GL Cluster object view features.
    """

    def __init__(self, vobj):
        '''
        Set view properties.
        '''
        self.Object = vobj.Object
        vobj.Proxy = self

    def attach(self, vobj):
        '''
        Create Object visuals in 3D view.
        '''
        self.Object = vobj.Object
        return

    def getIcon(self):
        '''
        Return object treeview icon.
        '''
        return ICONPATH + '/icons/GuideLines.svg'

    def claimChildren(self):
        """
        Provides object grouping
        """
        return self.Object.Group

    def setEdit(self, vobj, mode=0):
        """
        Enable edit
        """
        return True

    def unsetEdit(self, vobj, mode=0):
        """
        Disable edit
        """
        return False

    def doubleClicked(self, vobj):
        """
        Detect double click
        """
        pass

    def setupContextMenu(self, obj, menu):
        """
        Context menu construction
        """
        pass

    def edit(self):
        """
        Edit callback
        """
        pass

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
