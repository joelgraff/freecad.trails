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
from .surface_func import DataFunctions, ViewFunctions
from freecad.trails import ICONPATH, line_patterns, geo_origin
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


class Surface(DataFunctions):
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
            "Maximum length of triangle edge").MaxLength = 500000

        obj.addProperty(
            "App::PropertyAngle","MaxAngle","Triangulation",
            "Maximum angle of triangle edge").MaxAngle = 180

        obj.addProperty("Part::PropertyPartShape", "BoundaryShapes", "Triangulation",
            "Boundary Shapes").BoundaryShapes = Part.Shape()

        # Analysis properties.
        obj.addProperty(
            "App::PropertyEnumeration", "AnalysisType", "Analysis",
            "Set analysis type").AnalysisType = ["Default", "Elevation", "Slope", "Orientation"]

        obj.addProperty(
            "App::PropertyInteger", "Ranges", "Analysis",
            "Ranges").Ranges = 5

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

        obj.BoundaryShapes = self.get_boundary(obj.Mesh)


class ViewProviderSurface(ViewFunctions):
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

        # Boundary properties.
        vobj.addProperty(
            "App::PropertyColor", "BoundaryColor", "Boundary Style",
            "Set boundary contour color").BoundaryColor = (0.0, 0.75, 1.0, 0.0)

        vobj.addProperty(
            "App::PropertyFloatConstraint", "BoundaryWidth", "Boundary Style",
            "Set boundary contour line width").BoundaryWidth = (3.0, 1.0, 20.0, 1.0)

        vobj.addProperty(
            "App::PropertyEnumeration", "BoundaryPattern", "Boundary Style",
            "Set a line pattern for boundary").BoundaryPattern = [*line_patterns]

        vobj.addProperty(
            "App::PropertyIntegerConstraint", "PatternScale", "Boundary Style",
            "Scale the line pattern").PatternScale = (3, 1, 20, 1)

        # Contour properties.
        vobj.addProperty(
            "App::PropertyColor", "MajorColor", "Contour Style",
            "Set major contour color").MajorColor = (1.0, 0.0, 0.0, 0.0)

        vobj.addProperty(
            "App::PropertyFloatConstraint", "MajorWidth", "Contour Style",
            "Set major contour line width").MajorWidth = (3.0, 1.0, 20.0, 1.0)

        vobj.addProperty(
            "App::PropertyColor", "MinorColor", "Contour Style",
            "Set minor contour color").MinorColor = (1.0, 1.0, 0.0, 0.0)

        vobj.addProperty(
            "App::PropertyFloatConstraint", "MinorWidth", "Contour Style",
            "Set major contour line width").MinorWidth = (1.0, 1.0, 20.0, 1.0)

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
        self.edges = coin.SoIndexedFaceSet()
        self.face_material = coin.SoMaterial()
        self.edge_material = coin.SoMaterial()
        self.edge_color = coin.SoBaseColor()
        self.edge_style = coin.SoDrawStyle()
        self.edge_style.style = coin.SoDrawStyle.LINES

        shape_hints = coin.SoShapeHints()
        shape_hints.vertex_ordering = coin.SoShapeHints.COUNTERCLOCKWISE
        mat_binding = coin.SoMaterialBinding()
        mat_binding.value = coin.SoMaterialBinding.PER_FACE
        offset = coin.SoPolygonOffset()

        # Boundary features.
        self.boundary_color = coin.SoBaseColor()
        self.boundary_coords = coin.SoGeoCoordinate()
        self.boundary_lines = coin.SoLineSet()
        self.boundary_style = coin.SoDrawStyle()
        self.boundary_style.style = coin.SoDrawStyle.LINES

        # Boundary root.
        boundaries = coin.SoSeparator()
        boundaries.addChild(self.boundary_color)
        boundaries.addChild(self.boundary_style)
        boundaries.addChild(self.boundary_coords)
        boundaries.addChild(self.boundary_lines)

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

        # Highlight for selection.
        highlight = coin.SoType.fromName('SoFCSelection').createInstance()
        highlight.style = 'EMISSIVE_DIFFUSE'
        highlight.addChild(shape_hints)
        highlight.addChild(mat_binding)
        highlight.addChild(self.geo_coords)
        highlight.addChild(self.triangles)

        # Face root.
        face = coin.SoSeparator()
        face.addChild(self.face_material)
        face.addChild(highlight)

        # Edge root.
        edge = coin.SoSeparator()
        edge.addChild(self.edge_material)
        edge.addChild(self.edge_style)
        edge.addChild(highlight)

        # Surface root.
        surface_root = coin.SoSeparator()
        surface_root.addChild(boundaries)
        surface_root.addChild(offset)
        surface_root.addChild(major_contours)
        surface_root.addChild(minor_contours)
        surface_root.addChild(offset)
        surface_root.addChild(edge)
        surface_root.addChild(offset)
        surface_root.addChild(face)
        vobj.addDisplayMode(surface_root,"Surface")

        # Boundary root.
        boundary_root = coin.SoSeparator()
        boundary_root.addChild(boundaries)
        vobj.addDisplayMode(boundary_root,"Boundary")

        # Elevation/Shaded root.
        shaded_root = coin.SoSeparator()
        shaded_root.addChild(face)
        vobj.addDisplayMode(shaded_root,"Elevation")
        vobj.addDisplayMode(shaded_root,"Slope")
        vobj.addDisplayMode(shaded_root,"Shaded")

        # Flat Lines root.
        flatlines_root = coin.SoSeparator()
        flatlines_root.addChild(edge)
        flatlines_root.addChild(offset)
        flatlines_root.addChild(face)
        vobj.addDisplayMode(flatlines_root,"Flat Lines")

        # Wireframe root.
        wireframe_root = coin.SoSeparator()
        wireframe_root.addChild(major_contours)
        wireframe_root.addChild(minor_contours)
        wireframe_root.addChild(offset)
        wireframe_root.addChild(edge)
        vobj.addDisplayMode(wireframe_root,"Wireframe")

        # Take features from properties.
        self.onChanged(vobj,"ShapeColor")
        self.onChanged(vobj,"LineColor")
        self.onChanged(vobj,"LineWidth")
        self.onChanged(vobj,"BoundaryColor")
        self.onChanged(vobj,"BoundaryWidth")
        self.onChanged(vobj,"BoundaryPattern")
        self.onChanged(vobj,"PatternScale")
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
            if hasattr(vobj, "ShapeMaterial"):
                material = vobj.getPropertyByName("ShapeMaterial")
                self.face_material.diffuseColor.setValue(material.DiffuseColor[:3])
                self.face_material.transparency = material.DiffuseColor[3]

        if prop == "LineColor" or prop == "LineTransparency":
            if hasattr(vobj, "LineColor") and hasattr(vobj, "LineTransparency"):
                color = vobj.getPropertyByName("LineColor")
                transparency = vobj.getPropertyByName("LineTransparency")
                color = (color[0], color[1], color[2], transparency/100)
                vobj.LineMaterial.DiffuseColor = color

        if prop == "LineMaterial":
            material = vobj.getPropertyByName(prop)
            self.edge_material.diffuseColor.setValue(material.DiffuseColor[:3])
            self.edge_material.transparency = material.DiffuseColor[3]

        if prop == "LineWidth":
            width = vobj.getPropertyByName(prop)
            self.edge_style.lineWidth = width

        if prop == "BoundaryColor":
            color = vobj.getPropertyByName(prop)
            self.boundary_color.rgb = color[:3]

        if prop == "BoundaryWidth":
            width = vobj.getPropertyByName(prop)
            self.boundary_style.lineWidth = width

        if prop == "BoundaryPattern":
            if hasattr(vobj, "BoundaryPattern"):
                pattern = vobj.getPropertyByName(prop)
                self.boundary_style.linePattern = line_patterns[pattern]

        if prop == "PatternScale":
            if hasattr(vobj, "PatternScale"):
                scale = vobj.getPropertyByName(prop)
                self.boundary_style.linePatternScaleFactor = scale

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
        # Get GeoOrigin.
        origin = geo_origin.get()
        base = copy.deepcopy(origin.Origin)
        base.z = 0

        # Set geosystem.
        geo_system = ["UTM", origin.UtmZone, "FLAT"]
        self.geo_coords.geoSystem.setValues(geo_system)
        self.boundary_coords.geoSystem.setValues(geo_system)
        self.major_coords.geoSystem.setValues(geo_system)
        self.minor_coords.geoSystem.setValues(geo_system)

        if prop == "Mesh":
            mesh = obj.getPropertyByName("Mesh")
            copy_mesh = mesh.copy()
            copy_mesh.Placement.move(base)

            triangles = []
            for i in copy_mesh.Topology[1]:
                triangles.extend(list(i))
                triangles.append(-1)

            self.geo_coords.point.values = copy_mesh.Topology[0]
            self.triangles.coordIndex.values = triangles

        if prop == "ContourShapes":
            contour_shape = obj.getPropertyByName(prop)

            if contour_shape.SubShapes:
                major_shape = contour_shape.SubShapes[0]
                points, vertices = self.wire_view(major_shape, base)

                self.major_coords.point.values = points
                self.major_lines.numVertices.values = vertices

                minor_shape = contour_shape.SubShapes[1]
                points, vertices = self.wire_view(minor_shape, base)

                self.minor_coords.point.values = points
                self.minor_lines.numVertices.values = vertices

        if prop == "BoundaryShapes":
            boundary_shape = obj.getPropertyByName(prop)
            points, vertices = self.wire_view(boundary_shape, base, True)

            self.boundary_coords.point.values = points
            self.boundary_lines.numVertices.values = vertices

        if prop == "AnalysisType" or prop == "Ranges":
            analysis_type = obj.getPropertyByName("AnalysisType")
            ranges = obj.getPropertyByName("Ranges")

            if analysis_type == "Default":
                if hasattr(obj.ViewObject, "ShapeMaterial"):
                    material = obj.ViewObject.ShapeMaterial
                    self.face_material.diffuseColor = material.DiffuseColor[:3]

            if analysis_type == "Elevation":
                colorlist = self.elevation_analysis(obj.Mesh, ranges)
                self.face_material.diffuseColor.setValues(0,len(colorlist),colorlist)

            elif analysis_type == "Slope":
                colorlist = self.slope_analysis(obj.Mesh, ranges)
                self.face_material.diffuseColor.setValues(0,len(colorlist),colorlist)

    def getDisplayModes(self,vobj):
        '''
        Return a list of display modes.
        '''
        modes = ["Surface", "Boundary", "Flat Lines", "Shaded" "Wireframe"]

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
