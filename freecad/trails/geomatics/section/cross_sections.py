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
Create a Cross Sections object from FPO.
'''

import FreeCAD
import Part
from pivy import coin
from freecad.trails import ICONPATH, geo_origin
from .cs_func import CSFunc
import copy


def create():
    obj=FreeCAD.ActiveDocument.addObject("App::DocumentObjectGroupPython", "CrossSections")
    obj.Label = "Cross Sections"
    CrossSections(obj)
    ViewProviderCrossSections(obj.ViewObject)
    FreeCAD.ActiveDocument.recompute()

    return obj


class CrossSections(CSFunc):
    """
    This class is about Cross Section object data features.
    """

    def __init__(self, obj):
        '''
        Set data properties.
        '''

        self.Type = 'Trails::CrossSections'

        obj.addProperty(
            'App::PropertyVector', "Position", "Base",
            "Section creation origin").Position = FreeCAD.Vector()

        obj.addProperty(
            'App::PropertyLink', "Guidelines", "Base",
            "Base guidelines").Guidelines = None

        obj.addProperty(
            "Part::PropertyPartShape", "Shape", "Base",
            "Object shape").Shape = Part.Shape()

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
        position = obj.getPropertyByName("Position")
        gl = obj.getPropertyByName("Guidelines")
        group = obj.getPropertyByName("Group")

        if group and gl:
            obj.Shape = self.draw_2d_sections(position, gl, group)


class ViewProviderCrossSections:
    """
    This class is about Point Group Object view features.
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
        if prop == "Shape":
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
            sta_list = obj.Guidelines.StationList
            for i, wire in enumerate(shape.Wires):
                font = coin.SoFont()
                font.size = 3000
                gl_label = coin.SoSeparator()
                location = coin.SoTranslation()
                text = coin.SoAsciiText()

                label = str(round(sta_list[i % len(sta_list)], 2))
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
        return ICONPATH + '/icons/CreateSections.svg'

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
