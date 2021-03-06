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
import Part
from pivy import coin
from freecad.trails import ICONPATH, geo_origin
from .gl_func import GLFunc
import copy


def create():
    obj=FreeCAD.ActiveDocument.addObject("App::FeaturePython", "Guidelines")
    obj.Label = "Guidelines"
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

        self.Type = 'Trails::Guidelines'

        obj.addProperty(
            'App::PropertyLink', "Alignment", "Base",
            "Parent alignment").Alignment = None

        obj.addProperty(
            "App::PropertyFloatList", "StationList", "Base",
            "List of stations").StationList = []

        obj.addProperty(
            "Part::PropertyPartShape", "Shape", "Base",
            "Object shape").Shape = Part.Shape()

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

            # Get GeoOrigin.
            origin = geo_origin.get()
            base = copy.deepcopy(origin.Origin)
            base.z = 0

            obj.Shape = self.get_lines(base, alignment, offsets, stations)


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
        if prop == "Shape":
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
            counter = 0
            for wire in shape.Wires:
                font = coin.SoFont()
                font.size = 1000
                gl_label = coin.SoSeparator()
                location = coin.SoTranslation()
                text = coin.SoAsciiText()

                for vertex in wire.Vertexes:
                    points.append(vertex.Point.add(base))
                    label = str(round(obj.StationList[counter], 2))
                    location.translation = wire.Vertexes[-1].Point
                    text.string.setValues([label])
                    gl_label.addChild(font)
                    gl_label.addChild(location)
                    gl_label.addChild(text)
                    self.gl_labels.addChild(gl_label)

                counter += 1
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
