# -*- coding: utf-8 -*-
# **************************************************************************
# *                                                                        *
# *  Copyright (c) 2018 Joel Graff <monograff76@gmail.com>                 *
# *                                                                        *
# *  This program is free software; you can redistribute it and/or modify  *
# *  it under the terms of the GNU Lesser General Public License (LGPL)    *
# *  as published by the Free Software Foundation; either version 2 of     *
# *  the License, or (at your option) any later version.                   *
# *  for detail see the LICENCE text file.                                 *
# *                                                                        *
# *  This program is distributed in the hope that it will be useful,       *
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *  GNU Library General Public License for more details.                  *
# *                                                                        *
# *  You should have received a copy of the GNU Library General Public     *
# *  License along with this program; if not, write to the Free Software   *
# *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *  USA                                                                   *
# *                                                                        *
# **************************************************************************

"""
Cell feature generates a 3D cell, consisting of a sketch swept along a baseline
"""
__title__ = "CellPath.py"
__author__ = "Joel Graff"
__url__ = "https://www.freecadweb.org"

import FreeCAD as App
import Draft
import Part
import transportationwb

OBJECT_TYPE = "CellPath"

if App.Gui:
    import FreeCADGui as Gui
    from DraftTools import translate
    from PySide.QtCore import QT_TRANSLATE_NOOP

def createCellPath(body_geometry, sweep_template, sweep_path):
    """
    Creates a cell path object and adds to it the objects in the list
    """

    if sweep_path is None:
        print("Missing base feature")
        return

    if sweep_path is None:
        print("Missing body object")

    obj = App.ActiveDocument.addObject("PartDesign::FeaturePython", OBJECT_TYPE)

    #obj.Label = translate("Transportation", OBJECT_TYPE)

    cellpath = _CellPath(obj)

    body_geometry.addObject(obj)

    _ViewProviderCell(obj.ViewObject)

    cellpath.Object.SweepPath = sweep_path
    cellpath.Object.SweepTemplate = sweep_template

    App.ActiveDocument.recompute()

    return cellpath

class _CellPath():

    ft_mm = staticmethod(lambda _x: (_x / 12.0) / 25.4)
    round_sta = staticmethod(lambda _x: round(_x / (25.4 * 12),3) * 25.4 * 12)

    def __init__(self, obj):
        """
        Default Constructor
        """
        obj.Proxy = self
        self.Type = OBJECT_TYPE
        self.Object = obj

        self.add_property("App::PropertyLength", "StartStation", "Starting station for the cell").StartStation = 0.00
        self.add_property("App::PropertyLength", "EndStation", "Ending station for the cell").EndStation = 0.00
        self.add_property("App::PropertyLength", "Length", "Length of baseline").Length = 0.00
        obj.setEditorMode("Length", 1)

        self.add_property("App::PropertyLink", "SweepPath", "Sketch containing sweep path").SweepPath = None
        self.add_property("Part::PropertyGeometryList", "PathGeometry", "Path geometry shape").PathGeometry = []
        self.add_property("App::PropertyLink", "SweepTemplate", "Sketch containing sweep template").SweepTemplate = None

        self.init = True

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state

    def add_property(self, prop_type, prop_name, prop_desc):

        return self.Object.addProperty(prop_type, prop_name, OBJECT_TYPE, QT_TRANSLATE_NOOP("App::Property", prop_desc))

    def set_path_length(self):
        """
        Sets the length of the cell path based on the starting and ending station properties
        """

        new_length = self.Object.EndStation - self.Object.StartStation

        if new_length < 0.0:
            new_length = 0.0

        if self.Object.Length == new_length:
            return False

        if self.Object.Length < 0.0:
            self.Object.Length = 0.0

        self.Object.Length = new_length

        return True

    @staticmethod
    def _discretize_edge(edge, start_pt = 0.0, end_pt = 0.0):
        """
        Discretizes an edge, returning two points for a line and three points for an arc
        """

        segmentize = start_pt <= 0.0 and end_pt <= 0.0
        points = []

        if not segmentize:

            if start_pt <= 0.0:
                start_pt = 0.0

            if end_pt <= 0.0:
                end_pt = edge.Length

        if isinstance(edge.Curve, Part.Circle):

            if segmentize:
                points = edge.discretize(3)

            else:
                start_prm = edge.Curve.parameterAtDistance(start_pt, edge.FirstParameter)
                end_prm = edge.Curve.parameterAtDistance(end_pt, edge.FirstParameter)

                print ("\nstart: ", start_pt, ", ", start_prm)
                print ("\nend: ", end_pt, ", ", end_prm, "\n")

                points.extend(edge.discretize(Number = 3, First = start_prm, Last = end_prm))

        elif isinstance(edge.Curve, Part.Line):

            if segmentize:
                points = [edge.Vertexes[0].Point, edge.Vertexes[1].Point]

            else:
                tmp = edge.discretize(Distance = end_pt - start_pt)
                points = [tmp[0], tmp[1]]

        else:
            print ("Invalid edge type for discretization")

        return points

    @staticmethod
    def _get_edge_points(stations, geometry):
        """
        Returns a list of point sublists which describe the final sweep path
        stations - list of starting and ending stations
        geometry - list of geometry elements which form a continuous path and
                   whose list order and vertices are sorted from beginning to end
        """

        path_edges = []
        tot_len = 0.0

        #iterate the geometry list to get the edges on which the new path
        #begins and ends
        for _e in geometry:

            tot_len += _e.Length

            #skip if we're not to the start yet
            if tot_len < stations[0]:
                continue

            start_pt = _e.Length - (tot_len - stations[0])
            end_pt = _e.Length - (tot_len - stations[1])

            if end_pt > _e.Length:
                end_pt = -1.0

            print ("discretizing [", start_pt, "] to [", end_pt, "]")
            path_edges.append(_CellPath._discretize_edge(edge=_e, start_pt = start_pt, end_pt = end_pt))

            if end_pt >= 0.0:
                break

        if path_edges is None:
            print("Invalid station range")

        return path_edges

    @staticmethod
    def _convert_points(points, sketch):
        """
        Convert points from sketch coordinate frame to global coordinate frame
        """

        result = []
        g_place = App.Placement()

        for pt_list in points:

            vec_list = []

            for vec in pt_list:
                g_place.Base = vec
                vec_list.append(sketch.Placement.multiply(g_place).Base)

            result.append(vec_list)

        return result

    @staticmethod
    def _copy_sketch(doc, sketch, target_name, empty_copy = False):
        """
        Copy sketch as a new SketchObjectPython
        doc - document object which receives the sketch
        sketch - the sketch object to copy
        target_name - string representing the name of the new sketch
        empty_copy - True = create an empty sketch (only placement is duplicated)
                     False = create a full copy of the original sketch
        """
        doc = App.ActiveDocument

        target = doc.addObject('Sketcher::SketchObject', target_name)

        #_ViewProvider(target.ViewObject)

        if not empty_copy:

            for geo in sketch.Geometry:
                index = target.addGeometry(geo)
                target.setConstruction(index, geo.Construction)

            for constraint in sketch.Constraints:
                target.addConstraint(constraint)

        target.Placement = sketch.Placement

        target.solve()
        target.recompute()

        return target

    def _build_path_sketch(self):
        """
        Creates a new path sketch if it doesn't exist, or deletes the geometry
        in an existing sketch
        """

        sweep_path = self.Object.InList[0].getObject("SweepPath")

        if sweep_path is None:

            sweep_path = self._copy_sketch(App.ActiveDocument, self.Object.SweepPath, "SweepPath", True)
            self.Object.InList[0].addObject(sweep_path)

        else:

            while sweep_path.GeometryCount > 0:
                sweep_path.delGeometry(0)

            sweep_path.recompute()

        return sweep_path

    @staticmethod
    def _build_path(sketch, points):
        """
        Builds the sweep path
        sketch - the target sketch to contain the sweep path
        points - the list of point sublists which describe the final path
        """

        for point_vecs in points:

            point_count = len(point_vecs)
            geo = None

            # Three-point sublist is a curve
            if point_count == 3:
                geo = Part.ArcOfCircle(point_vecs[0], point_vecs[1], point_vecs[2])

            # Two-point sublist is a line
            elif point_count == 2:
                geo = Part.LineSegment(point_vecs[0], point_vecs[1])

            if geo is None:
                continue

            sketch.addGeometry(geo)

    @staticmethod
    def _sort_edges(edges):
        """
        Sort a continuous path of edges
        """

        path_shapes = []

        for path_edge in edges:
            path_shapes.append(path_edge.toShape())

        result = Part.sortEdges(path_shapes)[0]

        #if the first sorted edge is not the same as the first drawn edge,
        #reverse the sorted list
        if not path_shapes[0].Vertexes[0] in result[0].Vertexes:

            for _x in range(0, len(edges)):
                edges[_x].reverse()

            path_shapes = []

            for path_edge in edges:
                path_shapes.append(path_edge.toShape())

            result = Part.sortEdges(path_shapes)[0]

        return result

    @staticmethod
    def _build_sweep(body, template, path):
        """
        Sweep the provided template along the provided path
        """

        template.MapMode = "NormalToEdge"
        template.Support = path, "Edge1"

        add_pipe = body.getObject("Sweep")

        if not add_pipe is None:
            body.removeObject(add_pipe)

        add_pipe = body.newObject("PartDesign::AdditivePipe", "Sweep")

        add_pipe.Profile = template
        add_pipe.Spine = path
        add_pipe.recompute()

    def onChanged(self, obj, prop):

        #dodge onChanged calls during initialization
        if not hasattr(self, 'init'):
            return

        if not hasattr(self, "Object"):
            self.Object = obj

        #Gui.updateGui()

    def execute(self, fpy):

        print (self.Object.Length)

        if self.set_path_length():

            print (self.Object.Length)

            if self.Object.Length == 0.0:
                return

            print("path build...")

            #get the starting and ending station pproperty values as a list
            stations = [self.Object.StartStation.Value, self.Object.EndStation.Value]

            #sort the edges of the sweep path to provide a continuous path
            edges = self._sort_edges(self.Object.SweepPath.Geometry)

            #retrieve the edge points along the ordered path which represents the path segment
            #within the station range
            points = self._get_edge_points(stations, edges)

            print ("stations:\n", stations)
            print("\nfinal edges:\n", points)

            obj = self.Object.InList[0].getObject("Sweep")

            if not obj is None:
                App.ActiveDocument.removeObject("Sweep")

            #prepare the sweep path sketch for the new path
            sweep_path = self._build_path_sketch()

            #convert the points of the path to the sketch's coordinate system
            #points = self._convert_points(points, sweep_path)

            #generate the new sweep path in the empty sketch
            self._build_path(sweep_path, points)

            #sweep the sketch template along the newly-created path
            self._build_sweep(self.Object.InList[0], self.Object.SweepTemplate, sweep_path)

            return

    def addObject(self, child):

        print("adding" + str(child))

        #add the new object to the current group
        if hasattr(self, "Object"):
            grp = self.Object.Group

            if not child in grp:
                grp.append(child)
                self.Object.Group = grp
                return child

        return None

    def removeObject(self, child):

        if hasattr(self, "Object"):
            grp = self.Object.Group

            if child in grp:
                grp.remove(child)
                self.Object.Group = grp

class _ViewProviderCell:

    @staticmethod
    def findBodyOf(fpo):
        """
        Find the parent body of the supplied FPO
        """

        bodies = fpo.Document.findObjects("PartDesign::Body")
        result = [body for body in bodies if fpo in body.Group]

        assert(len(result)<=1)

        if len(result) == 0:
            return None

        return result[0]

    def __init__(self, obj):
        """
        Initialize the view provider
        """
        obj.Proxy = self

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None

    def attach(self, obj):
        """
        View provider scene graph initialization
        """
        self.Object = obj.Object

    #def claimChildren(self):

        #if hasattr(self, "Object"):
        #    if self.Object:
        #        return self.Object.Group
        #return []

    def updateData(self, fp, prop):
        """
        Property update handler
        """
        pass

    def getDisplayMode(self, obj):
        """
        Valid display modes
        """
        return ["Wireframe"]

    def getDefaultDisplayMode(self):
        """
        Return default display mode
        """
        return "Wireframe"

    def onDelete(self, viewprovider, subname):
        """
        Cleanup for when the object is deleted
        """

        body = self.findBodyOf(viewprovider.Object)
        body.removeObject(viewprovider.Object)
        self.Object.Document.removeObject(self.Object.Name)

    def setDisplayMode(self, mode):
        """
        Set mode - wireframe only
        """
        return "Wireframe"

    def onChanged(self, vp, prop):
        """
        Handle individual property changes
        """
        print ("View property changed " + prop)
        pass
