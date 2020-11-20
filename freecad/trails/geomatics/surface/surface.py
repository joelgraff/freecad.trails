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
Create a Surface Object from FPO.
'''

import FreeCAD, FreeCADGui
from pivy import coin
from .surface_func import SurfaceFunc
from freecad.trails import ICONPATH, geo_origin
from . import surfaces
import random



def create(points=[], index=[], name='Surface'):
    group = surfaces.get()
    obj=FreeCAD.ActiveDocument.addObject("App::FeaturePython", "Surface")
    obj.Label = name
    Surface(obj)
    obj.Points = points
    obj.Index = index
    ViewProviderSurface(obj.ViewObject)
    group.addObject(obj)
    FreeCAD.ActiveDocument.recompute()

    return obj


class Surface:
    """
    This class is about Surface Object data features.
    """

    def __init__(self, obj):
        '''
        Set data properties.
        '''
        self.Type = 'Trails::Surface'

        # Triangulation properties.
        obj.addProperty(
            "App::PropertyVectorList",
            "Points",
            "Base",
            "List of group points").Points = ()

        obj.addProperty(
            "App::PropertyIntegerList",
            "Index",
            "Base",
            "Index of points").Index = ()

        # Contour properties.
        obj.addProperty(
            "App::PropertyFloatConstraint",
            "ContourInterval",
            "Point Style",
            "Size of the point group").ContourInterval = (1.0)

        obj.addProperty(
            "App::PropertyVectorList",
            "ContourPoints",
            "Surface Style",
            "Points of contours", 4).ContourPoints = ()

        obj.addProperty(
            "App::PropertyIntegerList",
            "ContourVertices",
            "Surface Style",
            "Vertices of contours.", 4).ContourVertices = ()

        obj.Proxy = self

        self.Points = None
        self.Index = None
        obj.ContourInterval = (1.0, 0.0, 100.0, 1.0)
        self.ContourPoints = None
        self.ContourVertices = None

    def onChanged(self, fp, prop):
        '''
        Do something when a data property has changed.
        '''
        # fp is feature python.
        if prop == "Points" or prop == "Index" or prop == "ContourInterval":
            # Get Surface properties.
            points = fp.getPropertyByName("Points")
            index = fp.getPropertyByName("Index")
            deltaH = fp.getPropertyByName("ContourInterval")

            if points:
                origin = geo_origin.get(points[0])

                mesh = SurfaceFunc.create_mesh(points, index)
                coords, num_vert = SurfaceFunc.contour_points(
                    points[0], mesh, deltaH)

                fp.ContourPoints = coords
                fp.ContourVertices = num_vert

    def execute(self, fp):
        '''
        Do something when doing a recomputation. 
        '''
        return

class ViewProviderSurface:
    """
    This class is about Surface Object view features.
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
            "TriangleColor",
            "Surface Style",
            "Color of the point group").TriangleColor = (r, g, b)

        obj.Proxy = self

    def attach(self, obj):
        '''
        Create Object visuals in 3D view.
        '''
        # Geo Nodes.
        self.geo_coords = coin.SoGeoCoordinate()
        self.geo_separator = coin.SoGeoSeparator()

        # Surface features.
        self.triangles = coin.SoIndexedFaceSet()
        shape_hints = coin.SoShapeHints()
        shape_hints.vertex_ordering = coin.SoShapeHints.COUNTERCLOCKWISE
        self.mat_color = coin.SoMaterial()
        mat_binding = coin.SoMaterialBinding
        mat_binding.value = coin.SoMaterialBinding.OVERALL

        # Highlight for selection.
        highlight = coin.SoType.fromName('SoFCSelection').createInstance()
        #highlight.documentName.setValue(FreeCAD.ActiveDocument.Name)
        #highlight.objectName.setValue(obj.Object.Name)
        #highlight.subElementName.setValue("Main")
        highlight.addChild(self.mat_color)
        highlight.addChild(self.geo_coords)
        highlight.addChild(self.triangles)

        # Contour features.
        cont_color = coin.SoBaseColor()
        cont_color.rgb = (60, 255, 255)
        self.cont_coords = coin.SoGeoCoordinate()
        self.cont_lines = coin.SoLineSet()
        cont_style = coin.SoDrawStyle()
        cont_style.style = coin.SoDrawStyle.LINES
        cont_style.lineWidth = 2

        # Contour root.
        contours = coin.SoSeparator()
        contours.addChild(cont_color)
        contours.addChild(cont_style)
        contours.addChild(self.cont_coords)
        contours.addChild(self.cont_lines)

        # Surface root.
        surface_root = self.geo_separator
        surface_root.addChild(shape_hints)
        #surface_root.addChild(mat_binding)
        surface_root.addChild(contours)
        surface_root.addChild(highlight)
        obj.addDisplayMode(surface_root,"Surface")

        # Take features from properties.
        self.onChanged(obj,"TriangleColor")

    def onChanged(self, vp, prop):
        '''
        Update Object visuals when a view property changed.
        '''
        # vp is view provider.
        if prop == "TriangleColor":
            color = vp.getPropertyByName("TriangleColor")
            self.mat_color.diffuseColor = (color[0],color[1],color[2])

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

                self.geo_separator.geoSystem.setValues(geo_system)
                self.geo_separator.geoCoords.setValue(
                    points[0].x, points[0].y, points[0].z)

                self.cont_coords.geoSystem.setValues(geo_system)

        if prop == "Index":
            index = fp.getPropertyByName("Index")
            for i in range(0, len(index)):
                self.triangles.coordIndex.set1Value(i,index[i])

        if prop == "Points" or prop == "Index" or prop == "ContourInterval":
            cont_points = fp.getPropertyByName("ContourPoints")
            cont_vert = fp.getPropertyByName("ContourVertices")
            self.cont_coords.point.values = cont_points
            self.cont_lines.numVertices.values = cont_vert

    def getDisplayModes(self,obj):
        '''
        Return a list of display modes.
        '''
        modes=[]
        modes.append("Surface")

        return modes

    def getDefaultDisplayMode(self):
        '''
        Return the name of the default display mode.
        '''
        return "Surface"

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
        return ICONPATH + '/icons/Surface.svg'

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