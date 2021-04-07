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
Create a Cross Section object from FPO.
'''

import FreeCAD
import Part
from pivy import coin
from freecad.trails import ICONPATH, geo_origin
from .cs_func import CSFunc
import copy, random


def create():
    obj=FreeCAD.ActiveDocument.addObject("App::FeaturePython", "CrossSection")
    obj.Label = "Cross Section"
    cs = CrossSection(obj)
    ViewProviderCrossSection(obj.ViewObject)
    FreeCAD.ActiveDocument.recompute()

    return obj


class CrossSection(CSFunc):
    """
    This class is about Cross Section object data features.
    """

    def __init__(self, obj):
        '''
        Set data properties.
        '''

        self.Type = 'Trails::CrossSection'

        obj.addProperty(
            'App::PropertyLink', "Surface", "Base",
            "Projection surface").Surface = None

        obj.addProperty(
            'App::PropertyFloatList', "MinZ", "Base",
            "Minimum elevations").MinZ = []

        obj.addProperty(
            "Part::PropertyPartShape", "Shape", "Base",
            "Object shape").Shape = Part.Shape()

        obj.Proxy = self

    def onChanged(self, obj, prop):
        '''
        Do something when a data property has changed.
        '''
        if prop == "Surface":
            surface = obj.getPropertyByName("Surface")

            if surface and obj.InList:
                cs = obj.getParentGroup()
                cluster = cs.getParentGroup()

                for item in cluster.Group:
                    if item.Proxy.Type == 'Trails::Guidelines':
                        gl = item
                        break

                pos = cs.Position
                h = cs.Heigth.Value
                w = cs.Width.Value
                ver = cs.Vertical.Value
                hor = cs.Horizontal.Value
                geometry = [h, w]
                gaps = [ver, hor]
                horizons = cs.Horizons

                wires, obj.MinZ = self.draw_2d_sections(pos, gl, surface, geometry, gaps, horizons)


    def execute(self, obj):
        '''
        Do something when doing a recomputation. 
        '''
        surface = obj.getPropertyByName("Surface")

        if surface and obj.InList:
            cs = obj.getParentGroup()
            cluster = cs.getParentGroup()

            for item in cluster.Group:
                if item.Proxy.Type == 'Trails::Guidelines':
                    gl = item
                    break

            pos = cs.Position
            h = cs.Heigth.Value
            w = cs.Width.Value
            ver = cs.Vertical.Value
            hor = cs.Horizontal.Value
            geometry = [h, w]
            gaps = [ver, hor]
            horizons = cs.Horizons

            obj.Shape, elevations = self.draw_2d_sections(pos, gl, surface, geometry, gaps, horizons)



class ViewProviderCrossSection:
    """
    This class is about Point Group Object view features.
    """

    def __init__(self, vobj):
        '''
        Set view properties.
        '''
        self.Object = vobj.Object

        (r, g, b) = (random.random(), random.random(), random.random())

        vobj.addProperty(
            "App::PropertyColor", "SectionColor", "Point Style",
            "Color of the section").SectionColor = (r, g, b)

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
        self.line_color = coin.SoBaseColor()
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
        guidelines_root.addChild(self.line_color)
        guidelines_root.addChild(highlight)
        vobj.addDisplayMode(guidelines_root,"Lines")

        # Take features from properties.
        self.onChanged(vobj,"SectionColor")

    def onChanged(self, vobj, prop):
        '''
        Update Object visuals when a view property changed.
        '''
        if prop == "SectionColor" and hasattr(vobj, prop):
            color = vobj.getPropertyByName(prop)
            self.line_color.rgb = (color[0],color[1],color[2])

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
            for i, wire in enumerate(shape.Wires):
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
