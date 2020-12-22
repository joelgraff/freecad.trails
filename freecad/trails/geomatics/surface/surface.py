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
import Mesh
from pivy import coin
from .surface_func import SurfaceFunc
from freecad.trails import ICONPATH, geo_origin
from . import surfaces
import random, copy



def create(name='Surface'):
    group = surfaces.get()
    obj=FreeCAD.ActiveDocument.addObject("App::FeaturePython", "Surface")
    obj.Label = name
    Surface(obj)
    ViewProviderSurface(obj.ViewObject)
    group.addObject(obj)
    FreeCAD.ActiveDocument.recompute()

    return obj


class Surface(SurfaceFunc):
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
            'App::PropertyLinkList', "PointGroups", "Base",
            "List of Point Groups").PointGroups = []

        obj.addProperty(
            "App::PropertyIntegerList", "Delaunay", "Base",
            "Index of Delaunay vertices", 4).Delaunay = []

        obj.addProperty(
            "Mesh::PropertyMeshKernel", "Mesh", "Base",
            "Mesh object of triangulation").Mesh = Mesh.Mesh()

        obj.addProperty(
            "App::PropertyLength", "MaxLength", "Base",
            "Maximum length of triangle edge").MaxLength = 50000

        obj.addProperty(
            "App::PropertyAngle","MaxAngle","Base",
            "Maximum angle of triangle edge").MaxAngle = 170

        # Contour properties.
        obj.addProperty(
            "App::PropertyFloatConstraint", "ContourInterval", "Contour",
            "Size of the point group").ContourInterval = (1.0, 0.0, 100.0, 1.0)

        obj.addProperty(
            "App::PropertyVectorList", "ContourPoints", "Contour",
            "Points of contours", 4).ContourPoints = []

        obj.addProperty(
            "App::PropertyIntegerList", "ContourVertices", "Contour",
            "Vertices of contours.", 4).ContourVertices = []

        obj.Proxy = self

    def onChanged(self, obj, prop):
        '''
        Do something when a data property has changed.
        '''
        points = []
        pgs = obj.getPropertyByName("PointGroups")
        for pg in pgs:
            points.extend(pg.Points)
        if points:
            origin = geo_origin.get(points[0])
        else:
            origin = geo_origin.get()

        if prop =="PointGroups":
            if len(points) > 2:
                obj.Delaunay = self.triangulate(points)
            else:
                obj.Mesh = Mesh.Mesh()

        if prop == "Delaunay" or prop == "MaxLength" or prop == "MaxAngle":
            delaunay = obj.getPropertyByName("Delaunay")
            lmax = obj.getPropertyByName("MaxLength")
            amax = obj.getPropertyByName("MaxAngle")

            if delaunay:
                obj.Mesh = self.test_delaunay(
                    origin.Origin, points, delaunay, lmax, amax)

        if prop == "Mesh" or prop == "ContourInterval":
            deltaH = obj.getPropertyByName("ContourInterval")
            mesh = obj.getPropertyByName("Mesh")

            coords, num_vert = self.contour_points(origin.Origin, mesh, deltaH)

            obj.ContourPoints = coords
            obj.ContourVertices = num_vert

    def execute(self, obj):
        '''
        Do something when doing a recomputation. 
        '''
        pass

class ViewProviderSurface:
    """
    This class is about Surface Object view features.
    """

    def __init__(self, vobj):
        '''
        Set view properties.
        '''
        (r, g, b) = (random.random(), random.random(), random.random())

        vobj.addProperty(
            "App::PropertyColor", "TriangleColor", "Surface Style",
            "Color of the point group").TriangleColor = (r, g, b)

        vobj.Proxy = self

    def attach(self, vobj):
        '''
        Create Object visuals in 3D view.
        '''
        # GeoCoords Node.
        self.geo_coords = coin.SoGeoCoordinate()

        # Surface features.
        self.triangles = coin.SoIndexedFaceSet()
        shape_hints = coin.SoShapeHints()
        shape_hints.vertex_ordering = coin.SoShapeHints.COUNTERCLOCKWISE
        self.mat_color = coin.SoMaterial()
        mat_binding = coin.SoMaterialBinding()
        mat_binding.value = coin.SoMaterialBinding.OVERALL
        edge_color = coin.SoBaseColor()
        edge_color.rgb = (0.5, 0.5, 0.5)
        offset = coin.SoPolygonOffset()

        # Highlight for selection.
        highlight = coin.SoType.fromName('SoFCSelection').createInstance()
        #highlight.documentName.setValue(FreeCAD.ActiveDocument.Name)
        #highlight.objectName.setValue(vobj.Object.Name)
        #highlight.subElementName.setValue("Main")
        highlight.addChild(self.geo_coords)
        highlight.addChild(self.triangles)

        # Line style.
        line_style = coin.SoDrawStyle()
        line_style.style = coin.SoDrawStyle.LINES
        line_style.lineWidth = 2

        # Contour features.
        cont_color = coin.SoBaseColor()
        cont_color.rgb = (1, 1, 0)
        self.cont_coords = coin.SoGeoCoordinate()
        self.cont_lines = coin.SoLineSet()

        # Contour root.
        contours = coin.SoSeparator()
        contours.addChild(cont_color)
        contours.addChild(line_style)
        contours.addChild(self.cont_coords)
        contours.addChild(self.cont_lines)

        # Edge root.
        edges = coin.SoSeparator()
        edges.addChild(edge_color)
        edges.addChild(line_style)
        edges.addChild(highlight)

        # Surface root.
        surface_root = coin.SoSeparator()
        surface_root.addChild(edges)
        surface_root.addChild(offset)
        surface_root.addChild(shape_hints)
        surface_root.addChild(contours)
        surface_root.addChild(self.mat_color)
        surface_root.addChild(mat_binding)
        surface_root.addChild(highlight)
        vobj.addDisplayMode(surface_root,"Surface")

        # Take features from properties.
        self.onChanged(vobj,"TriangleColor")

    def onChanged(self, vobj, prop):
        '''
        Update Object visuals when a view property changed.
        '''
        try:
            if prop == "TriangleColor":
                color = vobj.getPropertyByName("TriangleColor")
                self.mat_color.diffuseColor = (color[0],color[1],color[2])
        except Exception: pass

    def updateData(self, obj, prop):
        '''
        Update Object visuals when a data property changed.
        '''
        if prop == "Mesh":
            mesh = obj.getPropertyByName("Mesh")
            topo_points = mesh.Topology[0]
            topo_tri = mesh.Topology[1]

            # Get GeoOrigin.
            points = []
            triangles = []
            origin = geo_origin.get()
            base = copy.deepcopy(origin.Origin)
            base.z = 0

            for i in topo_points:
                point = copy.deepcopy(i)
                points.append(point.add(base))

            for i in topo_tri:
                triangles.extend(list(i))
                triangles.append(-1)

            # Set GeoCoords.
            geo_system = ["UTM", origin.UtmZone, "FLAT"]
            self.geo_coords.geoSystem.setValues(geo_system)
            self.geo_coords.point.values = points

            #Set contour system.
            self.cont_coords.geoSystem.setValues(geo_system)
            self.triangles.coordIndex.values = triangles

        if prop == "Mesh" or prop == "ContourInterval":
            cont_points = obj.getPropertyByName("ContourPoints")
            cont_vert = obj.getPropertyByName("ContourVertices")

            self.cont_coords.point.values = cont_points
            self.cont_lines.numVertices.values = cont_vert

    def getDisplayModes(self,vobj):
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