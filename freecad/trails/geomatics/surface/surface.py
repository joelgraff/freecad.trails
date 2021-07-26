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
        obj.addProperty("Part::PropertyPartShape", "ContourShapes", "Contour",
            "Contour Shapes").ContourShapes = Part.Shape()

        obj.addProperty(
            "App::PropertyLength", "MajorInterval", "Contour",
            "Major contour interval").MajorInterval = 5000

        obj.addProperty(
            "App::PropertyLength", "MinorInterval", "Contour",
            "Minor contour interval").MinorInterval = 1000

        obj.Proxy = self

    def onChanged(self, obj, prop):
        '''
        Do something when a data property has changed.
        '''
        points = []
        pgs = obj.getPropertyByName("PointGroups")
        for pg in pgs:
            points.extend(pg.Points.Points)

        if prop == "MinorInterval":
            min_int = obj.getPropertyByName(prop)
            obj.MajorInterval = min_int*5

        if prop =="PointGroups":
            pgs = obj.getPropertyByName(prop)

            points = []
            for pg in pgs:
                points.extend(pg.Points.Points)

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

        if prop == "Placement":
            placement = obj.getPropertyByName(prop)
            copy_mesh = obj.Mesh.copy()
            copy_mesh.Placement = placement
            obj.Mesh = copy_mesh

    def execute(self, obj):
        '''
        Do something when doing a recomputation. 
        '''
        major = obj.MajorInterval
        minor = obj.MinorInterval

        obj.ContourShapes = self.get_contours(
            obj.Mesh, major.Value/1000, minor.Value/1000)


class ViewProviderSurface:
    """
    This class is about Surface Object view features.
    """

    def __init__(self, vobj):
        '''
        Set view properties.
        '''
        (r, g, b) = (random.random(), random.random(), random.random())

        # Triangulation properties.
        vobj.addProperty(
            "App::PropertyIntegerConstraint", "Transparency", "Surface Style",
            "Set triangle face transparency").Transparency = (50, 0, 100, 1)

        vobj.addProperty(
            "App::PropertyColor", "ShapeColor", "Surface Style",
            "Set triangle face color").ShapeColor = (r, g, b, vobj.Transparency/100)

        vobj.addProperty(
            "App::PropertyMaterial", "ShapeMaterial", "Surface Style",
            "Triangle face material").ShapeMaterial = FreeCAD.Material()

        vobj.addProperty(
            "App::PropertyIntegerConstraint", "LineTransparency", "Surface Style",
            "Set triangle edge transparency").LineTransparency = (50, 0, 100, 1)

        vobj.addProperty(
            "App::PropertyColor", "LineColor", "Surface Style",
            "Set triangle face color").LineColor = (0.5, 0.5, 0.5, vobj.LineTransparency/100)

        vobj.addProperty(
            "App::PropertyMaterial", "LineMaterial", "Surface Style",
            "Triangle face material").LineMaterial = FreeCAD.Material()

        vobj.addProperty(
            "App::PropertyFloatConstraint", "LineWidth", "Surface Style",
            "Set triangle edge line width").LineWidth = (0.0, 1.0, 20.0, 1.0)

        # Contour properties.
        vobj.addProperty(
            "App::PropertyColor", "MajorColor", "Contour Style",
            "Set major contour color").MajorColor = (1.0, 0.0, 0.0, 0.0)

        vobj.addProperty(
            "App::PropertyFloatConstraint", "MajorWidth", "Contour Style",
            "Set major contour line width").MajorWidth = (5.0, 1.0, 20.0, 1.0)

        vobj.addProperty(
            "App::PropertyColor", "MinorColor", "Contour Style",
            "Set minor contour color").MinorColor = (1.0, 1.0, 0.0, 0.0)

        vobj.addProperty(
            "App::PropertyFloatConstraint", "MinorWidth", "Contour Style",
            "Set major contour line width").MinorWidth = (2.0, 1.0, 20.0, 1.0)

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
        self.face_material = coin.SoMaterial()
        self.edge_material = coin.SoMaterial()
        self.edge_color = coin.SoBaseColor()
        self.edge_style = coin.SoDrawStyle()
        self.edge_style.style = coin.SoDrawStyle.LINES

        shape_hints = coin.SoShapeHints()
        shape_hints.vertex_ordering = coin.SoShapeHints.COUNTERCLOCKWISE
        mat_binding = coin.SoMaterialBinding()
        mat_binding.value = coin.SoMaterialBinding.OVERALL
        offset = coin.SoPolygonOffset()

        # Major Contour features.
        self.major_color = coin.SoBaseColor()
        self.major_coords = coin.SoGeoCoordinate()
        self.major_lines = coin.SoLineSet()
        self.major_style = coin.SoDrawStyle()
        self.major_style.style = coin.SoDrawStyle.LINES

        # Major Contour root.
        major_contours = coin.SoSeparator()
        major_contours.addChild(self.major_color)
        major_contours.addChild(self.major_style)
        major_contours.addChild(self.major_coords)
        major_contours.addChild(self.major_lines)

        # Minor Contour features.
        self.minor_color = coin.SoBaseColor()
        self.minor_coords = coin.SoGeoCoordinate()
        self.minor_lines = coin.SoLineSet()
        self.minor_style = coin.SoDrawStyle()
        self.minor_style.style = coin.SoDrawStyle.LINES

        # Minor Contour root.
        minor_contours = coin.SoSeparator()
        minor_contours.addChild(self.minor_color)
        minor_contours.addChild(self.minor_style)
        minor_contours.addChild(self.minor_coords)
        minor_contours.addChild(self.minor_lines)

        # Face root.
        faces = coin.SoSeparator()
        faces.addChild(shape_hints)
        faces.addChild(self.face_material)
        faces.addChild(mat_binding)
        faces.addChild(self.geo_coords)
        faces.addChild(self.triangles)

        # Highlight for selection.
        highlight = coin.SoType.fromName('SoFCSelection').createInstance()
        highlight.style = 'EMISSIVE_DIFFUSE'
        faces.addChild(shape_hints)
        highlight.addChild(self.edge_material)
        highlight.addChild(mat_binding)
        highlight.addChild(self.edge_style)
        highlight.addChild(self.geo_coords)
        highlight.addChild(self.triangles)

        # Surface root.
        surface_root = coin.SoSeparator()
        surface_root.addChild(major_contours)
        surface_root.addChild(minor_contours)
        surface_root.addChild(offset)
        surface_root.addChild(faces)
        surface_root.addChild(offset)
        surface_root.addChild(highlight)
        vobj.addDisplayMode(surface_root,"Surface")

        # Take features from properties.
        self.onChanged(vobj,"ShapeColor")
        self.onChanged(vobj,"LineColor")
        self.onChanged(vobj,"LineWidth")
        self.onChanged(vobj,"MajorColor")
        self.onChanged(vobj,"MajorWidth")
        self.onChanged(vobj,"MinorColor")
        self.onChanged(vobj,"MinorWidth")

    def onChanged(self, vobj, prop):
        '''
        Update Object visuals when a view property changed.
        '''
        if prop == "ShapeColor" or prop == "Transparency":
            if hasattr(vobj, "ShapeColor") and hasattr(vobj, "Transparency"):
                color = vobj.getPropertyByName("ShapeColor")
                transparency = vobj.getPropertyByName("Transparency")
                color = (color[0], color[1], color[2], transparency/100)
                vobj.ShapeMaterial.DiffuseColor = color

        if prop == "ShapeMaterial":
            material = vobj.getPropertyByName(prop)
            self.face_material.diffuseColor = material.DiffuseColor[:3]
            self.face_material.transparency = material.DiffuseColor[3]

        if prop == "LineColor" or prop == "LineTransparency":
            if hasattr(vobj, "LineColor") and hasattr(vobj, "LineTransparency"):
                color = vobj.getPropertyByName("LineColor")
                transparency = vobj.getPropertyByName("LineTransparency")
                color = (color[0], color[1], color[2], transparency/100)
                vobj.LineMaterial.DiffuseColor = color

        if prop == "LineMaterial":
            material = vobj.getPropertyByName(prop)
            self.edge_material.diffuseColor = material.DiffuseColor[:3]
            self.edge_material.transparency = material.DiffuseColor[3]

        if prop == "LineColor":
            color = vobj.getPropertyByName(prop)
            self.edge_color.rgb = color[:3]

        if prop == "LineWidth":
            width = vobj.getPropertyByName(prop)
            self.edge_style.lineWidth = width

        if prop == "MajorColor":
            color = vobj.getPropertyByName(prop)
            self.major_color.rgb = color[:3]

        if prop == "MajorWidth":
            width = vobj.getPropertyByName(prop)
            self.major_style.lineWidth = width

        if prop == "MinorColor":
            color = vobj.getPropertyByName(prop)
            self.minor_color.rgb = color[:3]

        if prop == "MinorWidth":
            width = vobj.getPropertyByName(prop)
            self.minor_style.lineWidth = width

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
            self.major_coords.geoSystem.setValues(geo_system)
            self.minor_coords.geoSystem.setValues(geo_system)
            self.triangles.coordIndex.values = triangles

        if prop == "ContourShapes":
            contour_shape = obj.getPropertyByName(prop)

            if contour_shape.SubShapes:
                major_pnts = []
                major_vert = []
                major_shape = contour_shape.SubShapes[0]
                for i in major_shape.Wires:
                    points = []
                    for vertex in i.Vertexes:
                        pnt = vertex.Point.add(base)
                        points.append((pnt[0], pnt[1], pnt[2]))

                    major_pnts.extend(points)
                    major_vert.append(len(points))

                self.major_coords.point.values = major_pnts
                self.major_lines.numVertices.values = major_vert

                minor_pnts = []
                minor_vert = []
                minor_shape = contour_shape.SubShapes[1]
                for i in minor_shape.Wires:
                    points = []
                    for vertex in i.Vertexes:
                        pnt = vertex.Point.add(base)
                        points.append((pnt[0], pnt[1], pnt[2]))

                    minor_pnts.extend(points)
                    minor_vert.append(len(points))

                self.minor_coords.point.values = minor_pnts
                self.minor_lines.numVertices.values = minor_vert

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
