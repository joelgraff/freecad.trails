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
Create a Region group object from FPO.
'''

import FreeCAD, Part, copy
from pivy import coin
from freecad.trails import ICONPATH, geo_origin
from .region_func import RegionFunc
from ..section import sections
from ..volume import volumes
from ..table import tables


def create(alignment, name='Region'):
    """
    Factory method for Region object.
    """
    for item in alignment.Group:
        if item.Proxy.Type == 'Trails::Regions':
            regions = item
            break

    obj = FreeCAD.ActiveDocument.addObject(
        "App::DocumentObjectGroupPython", 'Region')
    obj.Label = name
    regions.addObject(obj)

    Region(obj)

    # Add Cross Sections group.
    secs = sections.create()
    obj.addObject(secs)

    # Add Volumes group.
    vol_areas = volumes.create()
    obj.addObject(vol_areas)

    # Add Tables group.
    tabs = tables.create()
    obj.addObject(tabs)

    ViewProviderRegion(obj.ViewObject)
    FreeCAD.ActiveDocument.recompute()

    return obj



class Region(RegionFunc):
    """
    This class is about Region object data features.
    """

    def __init__(self, obj):
        '''
        Set data properties.
        '''
        self.Type = 'Trails::Region'

        obj.addProperty(
            "App::PropertyBool", "AtHorizontalAlignmentPoints", "Base",
            "Show/hide labels").AtHorizontalAlignmentPoints = True

        obj.addProperty(
            "App::PropertyFloatList", "StationList", "Base",
            "List of stations").StationList = []

        obj.addProperty(
            "Part::PropertyPartShape", "Shape", "Base",
            "Object shape").Shape = Part.Shape()

        obj.addProperty(
            "App::PropertyBool", "FromAlignmentStart", "Region",
            "Show/hide labels").FromAlignmentStart = True

        obj.addProperty(
            "App::PropertyBool", "ToAlignmentEnd", "Region",
            "Show/hide labels").ToAlignmentEnd = True

        obj.addProperty(
            "App::PropertyLength", "StartStation", "Station",
            "Guide lines start station").StartStation = 0

        obj.addProperty(
            "App::PropertyLength", "EndStation", "Station",
            "Guide lines end station").EndStation = 0

        obj.addProperty(
            "App::PropertyLength", "IncrementAlongTangents", "Increment",
            "Distance between guide lines along tangents").IncrementAlongTangents = 10000

        obj.addProperty(
            "App::PropertyLength", "IncrementAlongCurves", "Increment",
            "Distance between guide lines along curves").IncrementAlongCurves = 5000

        obj.addProperty(
            "App::PropertyLength", "IncrementAlongSpirals", "Increment",
            "Distance between guide lines along spirals").IncrementAlongSpirals = 5000

        obj.addProperty(
            "App::PropertyLength", "RightOffset", "Offset",
            "Length of right offset").RightOffset = 20000

        obj.addProperty(
            "App::PropertyLength", "LeftOffset", "Offset",
            "Length of left offset").LeftOffset = 20000

        obj.setEditorMode('StartStation', 1)
        obj.setEditorMode('EndStation', 1)

        self.onChanged(obj,'FromAlignmentStart')
        self.onChanged(obj,'ToAlignmentEnd')

        obj.Proxy = self

    def onChanged(self, obj, prop):
        '''
        Do something when a data property has changed.
        '''
        alignment = obj.InList[0].InList[0]
        start, end = self.get_alignment_infos(alignment)

        if prop == "FromAlignmentStart":
            from_start = obj.getPropertyByName("FromAlignmentStart")
            if from_start:
                obj.setEditorMode('StartStation', 1)
                obj.StartStation = start
            else:
                obj.setEditorMode('StartStation', 0)

        if prop == "ToAlignmentEnd":
            to_end = obj.getPropertyByName("ToAlignmentEnd")
            if to_end:
                obj.setEditorMode('EndStation', 1)
                obj.EndStation = end
            else:
                obj.setEditorMode('EndStation', 0)

    def execute(self, obj):
        '''
        Do something when doing a recomputation.
        '''
        alignment = obj.InList[0].InList[0]

        tangent = obj.getPropertyByName("IncrementAlongTangents")
        curve = obj.getPropertyByName("IncrementAlongCurves")
        spiral = obj.getPropertyByName("IncrementAlongSpirals")
        increments = [tangent, curve, spiral]

        start = obj.getPropertyByName("StartStation")
        end = obj.getPropertyByName("EndStation")
        region = [start, end]

        horiz_pnts = obj.getPropertyByName("AtHorizontalAlignmentPoints")

        obj.StationList = self.generate(alignment,increments, region, horiz_pnts)

        left_offset = obj.getPropertyByName("LeftOffset")
        right_offset = obj.getPropertyByName("RightOffset")
        offsets = [left_offset, right_offset]

        # Get GeoOrigin.
        origin = geo_origin.get()
        base = copy.deepcopy(origin.Origin)
        base.z = 0

        obj.Shape = self.get_lines(base, alignment, offsets, obj.StationList)



class ViewProviderRegion:
    """
    This class is about Region object view features.
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

        # Lines root.
        self.line_coords = coin.SoGeoCoordinate()
        self.lines = coin.SoLineSet()
        self.gl_labels = coin.SoSeparator()

        # Line style.
        line_color = coin.SoBaseColor()
        line_color.rgb = (0.0, 1.0, 1.0)
        line_style = coin.SoDrawStyle()
        line_style.style = coin.SoDrawStyle.LINES
        line_style.lineWidth = 2

        # Highlight for selection.
        highlight = coin.SoType.fromName('SoFCSelection').createInstance()
        highlight.style = 'EMISSIVE_DIFFUSE'
        highlight.addChild(line_style)
        highlight.addChild(self.line_coords)
        highlight.addChild(self.lines)

        # Surface root.
        guidelines_root = coin.SoSeparator()
        guidelines_root.addChild(self.gl_labels)
        guidelines_root.addChild(line_color)
        guidelines_root.addChild(highlight)
        vobj.addDisplayMode(guidelines_root,"Lines")

    def onChanged(self, vobj, prop):
        '''
        Update Object visuals when a view property changed.
        '''
        pass

    def updateData(self, obj, prop):
        '''
        Update Object visuals when a data property changed.
        '''
        if prop == "Shape" and obj.StationList:
            self.gl_labels.removeAllChildren()
            shape = obj.getPropertyByName("Shape")

            # Get GeoOrigin.
            origin = geo_origin.get()
            base = copy.deepcopy(origin.Origin)
            base.z = 0

            # Set GeoCoords.
            geo_system = ["UTM", origin.UtmZone, "FLAT"]
            self.line_coords.geoSystem.setValues(geo_system)

            points = []
            line_vert = []
            for i, wire in enumerate(shape.Wires):
                font = coin.SoFont()
                font.size = 3000
                gl_label = coin.SoSeparator()
                location = coin.SoTranslation()
                text = coin.SoAsciiText()

                label = str(round(obj.StationList[i], 2))
                location.translation = wire.Vertexes[-1].Point
                text.string.setValues([label])
                gl_label.addChild(font)
                gl_label.addChild(location)
                gl_label.addChild(text)
                self.gl_labels.addChild(gl_label)

                for vertex in wire.Vertexes:
                    points.append(vertex.Point.add(base))

                line_vert.append(len(wire.Vertexes))

            self.line_coords.point.values = points
            self.lines.numVertices.values = line_vert

    def getDisplayModes(self, vobj):
        '''
        Return a list of display modes.
        '''
        modes=[]
        modes.append("Lines")

        return modes

    def getDefaultDisplayMode(self):
        '''
        Return the name of the default display mode.
        '''
        return "Lines"

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

    def setupContextMenu(self, vobj, menu):
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
