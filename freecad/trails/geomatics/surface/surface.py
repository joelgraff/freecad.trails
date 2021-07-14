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

import FreeCAD
import Mesh, Part
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

        obj.addProperty(
            'App::PropertyPlacement', "Placement", "Base",
            "Placement").Placement = FreeCAD.Placement()

        # Triangulation properties.
        obj.addProperty(
            'App::PropertyLinkList', "PointGroups", "Triangulation",
            "List of Point Groups").PointGroups = []

        obj.addProperty(
            "App::PropertyIntegerList", "Delaunay", "Triangulation",
            "Index of Delaunay vertices", 4).Delaunay = []

        obj.addProperty(
            "Mesh::PropertyMeshKernel", "Mesh", "Triangulation",
            "Mesh object of triangulation").Mesh = Mesh.Mesh()

        obj.addProperty(
            "App::PropertyLength", "MaxLength", "Triangulation",
            "Maximum length of triangle edge").MaxLength = 50000

        obj.addProperty(
            "App::PropertyAngle","MaxAngle","Triangulation",
            "Maximum angle of triangle edge").MaxAngle = 170

        # Contour properties.
        obj.addProperty(
            "App::PropertyFloatConstraint", "ContourInterval", "Contour",
            "Size of the point group").ContourInterval = (1.0, 0.0, 100.0, 1.0)

        obj.addProperty("Part::PropertyPartShape", "ContourShapes", "Base",
            "Contour Shapes").ContourShapes = Part.Shape()

        obj.Proxy = self

    def onChanged(self, obj, prop):
        '''
        Do something when a data property has changed.
        '''
        points = []
        pgs = obj.getPropertyByName("PointGroups")
        for pg in pgs:
            points.extend(pg.Points.Points)

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
                    points, delaunay, lmax, amax)

        if prop == "Mesh" or prop == "ContourInterval":
            deltaH = obj.getPropertyByName("ContourInterval")
            mesh = obj.getPropertyByName("Mesh")

            obj.ContourShapes = self.get_contours(mesh, deltaH)

        if prop == "Placement":
            placement = obj.getPropertyByName(prop)
            copy_mesh = obj.Mesh.copy()
            copy_mesh.Placement = placement
            obj.Mesh = copy_mesh

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
            "App::PropertyIntegerConstraint", "Transparency", "Surface Style",
            "Set triangle face transparency").Transparency = (80,0,100,1)

        vobj.addProperty(
            "App::PropertyColor", "ShapeColor", "Surface Style",
            "Set triangle face color").ShapeColor = (r, g, b, vobj.Transparency/100)

        vobj.addProperty(
            "App::PropertyMaterial", "ShapeMaterial", "Surface Style",
            "Triangle face material").ShapeMaterial = FreeCAD.Material()

        vobj.Proxy = self

        vobj.ShapeMaterial.DiffuseColor = vobj.ShapeColor

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

        # Face root.
        faces = coin.SoSeparator()
        faces.addChild(shape_hints)
        faces.addChild(self.mat_color)
        faces.addChild(mat_binding)
        faces.addChild(self.geo_coords)
        faces.addChild(self.triangles)

        # Highlight for selection.
        highlight = coin.SoType.fromName('SoFCSelection').createInstance()
        highlight.style = 'EMISSIVE_DIFFUSE'
        highlight.addChild(edge_color)
        highlight.addChild(line_style)
        highlight.addChild(self.geo_coords)
        highlight.addChild(self.triangles)

        # Surface root.
        surface_root = coin.SoSeparator()
        surface_root.addChild(contours)
        surface_root.addChild(offset)
        surface_root.addChild(faces)
        surface_root.addChild(offset)
        surface_root.addChild(highlight)
        vobj.addDisplayMode(surface_root,"Surface")

        # Take features from properties.
        self.onChanged(vobj,"ShapeColor")

    def onChanged(self, vobj, prop):
        '''
        Update Object visuals when a view property changed.
        '''
        if prop == "ShapeColor" or prop == "Transparency":
            color = vobj.getPropertyByName("ShapeColor")
            transparency = vobj.getPropertyByName("Transparency")
            color = (color[0], color[1], color[2], transparency/100)
            vobj.ShapeMaterial.DiffuseColor = color

        if prop == "ShapeMaterial":
            color = vobj.getPropertyByName(prop)
            try:
                self.mat_color.diffuseColor = color.DiffuseColor[:3]
                self.mat_color.transparency = color.DiffuseColor[3]
            except Exception: pass

    def updateData(self, obj, prop):
        '''
        Update Object visuals when a data property changed.
        '''
        origin = geo_origin.get()
        base = copy.deepcopy(origin.Origin)
        base.z = 0

        if prop == "Mesh":
            mesh = obj.getPropertyByName("Mesh")
            topo_points = mesh.Topology[0]
            topo_tri = mesh.Topology[1]

            # Get GeoOrigin.
            points = []
            triangles = []

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

        if prop == "ContourShapes":
            cont_shps = obj.getPropertyByName(prop)
            cont_pnts = []
            cont_vert = []

            for i in cont_shps.Wires:
                points = []
                for vertex in i.Vertexes:
                    pnt = vertex.Point.add(base)
                    points.append((pnt[0], pnt[1], pnt[2]))

                cont_pnts.extend(points)
                cont_vert.append(len(points))

            self.cont_coords.point.values = cont_pnts
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
