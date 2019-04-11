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
# **************************************************************************/

"""
Cell feature generates a 3D cell, consisting of a sketch swept along a spline
"""
__title__ = "CellPathSpline.py"
__author__ = "Joel Graff"
__url__ = "https://www.freecadweb.org"

import FreeCAD as App
import Draft
import Part
import transportationwb
import math

OBJECT_TYPE = "CellPathSpline"

if App.Gui:
    import FreeCADGui as Gui
    from DraftTools import translate
    from PySide.QtCore import QT_TRANSLATE_NOOP

def createCellPath(body_geometry, sweep_template, source_path):
    """
    Creates a cell path object and adds to it the objects in the list
    """

    if source_path is None:
        print("Missing base feature")
        return

    if source_path is None:
        print("Missing body object")

    obj = App.ActiveDocument.addObject("PartDesign::FeaturePython", OBJECT_TYPE)

    #obj.Label = translate("Transportation", OBJECT_TYPE)

    cellpath = _CellPath(obj)

    body_geometry.addObject(obj)

    _ViewProviderCell(obj.ViewObject)

    cellpath.Object.SourcePath = source_path
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
        self.add_property("App::PropertyLength", "Length", "Length of sweep path").Length = 7.00
        obj.setEditorMode("Length", 1)

        self.add_property("App::PropertyLink", "SourcePath", "Source spline for sweep").SourcePath = None
        self.add_property("App::PropertyLink", "SweepPath", "Spline sweep path").SweepPath = None
        self.add_property("Part::PropertyGeometryList", "PathGeometry", "Path geometry shape").PathGeometry = []
        self.add_property("App::PropertyLink", "SweepTemplate", "Sketch containing sweep template").SweepTemplate = None
        self.add_property("App::PropertyLink", "Sweep", "Sweep of template along profile").Sweep = None

        self.add_property("App::PropertyLength", "Resolution", "Resolution of the sweep").Resolution = 0.0

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
        USED
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
    def _discretize_edge(edge, start_pt = 0.0, end_pt = 0.0, number = 3):
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

        if type(edge.Curve) in [Part.Circle, Part.BSplineCurve]:

            if segmentize:
                points = edge.discretize(3)

            else:
                start_prm = edge.Curve.parameterAtDistance(start_pt, edge.FirstParameter)
                end_prm = edge.Curve.parameterAtDistance(end_pt, edge.FirstParameter)

                print("\nstart: ", start_pt, ", ", start_prm)
                print("\nend: ", end_pt, ", ", end_prm, "\n")
                print("Number = ", number, "; Start = ", start_prm, "; End = ", end_prm)

                points.extend(edge.discretize(Number=number, First=start_prm, Last=end_prm))

        elif isinstance(edge.Curve, Part.Line):

            if segmentize:
                points = [edge.Vertexes[0].Point, edge.Vertexes[1].Point]

            else:
                tmp = edge.discretize(Distance=(end_pt - start_pt))
                points = [tmp[0], tmp[1]]

        else:
            print ("Invalid edge type for discretization")

        return points

    @staticmethod
    def _get_edge_points(stations, spline, resolution):
        """
        USED
        Returns a list of point sublists which describe the final sweep path
        stations - list of starting and ending stations
        geometry - list of geometry elements which form a continuous path and
                   whose list order and vertices are sorted from beginning to end
        """
        length = stations[1] - stations[0]

        #if no resolution is defined, provide a minimum
        if resolution == 0.0:
            resolution = length / 3.0

        point_count = math.ceil(length / resolution)

        pts = _CellPath._discretize_edge(number=point_count, start_pt=stations[0], end_pt=stations[1], edge=spline)

        return pts

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

    @staticmethod
    def _build_sweep(body, template, path):
        """
        Sweep the provided template along the provided path
        """

        template.MapMode = "NormalToEdge"
        template.Support = (path, ["Edge1"])

        add_pipe = body.getObject("Sweep")

        if not add_pipe is None:
            body.removeObject(add_pipe)

        add_pipe = body.newObject("PartDesign::AdditivePipe", "Sweep")

        add_pipe.Profile = template
        add_pipe.Spine = (path, ['Edge1'])
        add_pipe.Sections = template

        return add_pipe

    @staticmethod
    def _build_sweep_spline(points):
        """
        Build a spline for the sweep path based on the passed points
        """

        obj_type = "BSpline"

        pt_count = len(points)

        if pt_count < 2:
            return None

        elif len(points) == 2: 
            obj_type = "Line"

        obj = App.ActiveDocument.addObject("Part::Part2DObjectPython", obj_type)

        Draft._BSpline(obj)

        obj.Closed = False
        obj.Points = points
        obj.Support = None
        obj.Label = "SweepPath"

        Draft._ViewProviderWire(obj.ViewObject)

        return obj

    def onChanged(self, obj, prop):

        #dodge onChanged calls during initialization
        if not hasattr(self, 'init'):
            return

        if not hasattr(self, "Object"):
            self.Object = obj

        doRebuild = prop in ["Resolution", "EndStation", "StartStation"]

        if prop=="Resolution":

            #change the length so it doesn't skip the next execution loop
            self.Object.Length.Value = self.Object.Length.Value + 1.0

        if doRebuild:

            if not self.Object.Sweep is None:
                App.ActiveDocument.removeObject(self.Object.Sweep.Name)

            if not self.Object.SweepPath is None:
                App.ActiveDocument.removeObject(self.Object.SweepPath.Name)

        return

    def execute(self, fpy):

        print ("executing...")

        if self.set_path_length():

            print("length changed to: ", self.Object.Length)

            if self.Object.Length == 0.0:
                return

            print("spline path build...")

            #get the starting and ending station pproperty values as a list
            stations = [self.Object.StartStation.Value, self.Object.EndStation.Value]

            #sort the edges of the sweep path to provide a continuous path
            #edges = self._sort_edges(self.Object.SweepPath.Geometry)

            #retrieve the edge points along the ordered path which represents the path segment
            #within the station range
            points = self._get_edge_points(stations, self.Object.SourcePath.Shape, self.Object.Resolution.Value)

            print ("stations:\n", stations)
            print("\nfinal edges:\n", points)

            obj = self.Object.InList[0].getObject("Sweep")

            if not obj is None:
                App.ActiveDocument.removeObject("Sweep")

            #prepare the sweep path sketch for the new path
            #sweep_path = self._build_path_sketch()
            spline = self._build_sweep_spline(points)

            if spline is None:
                return

            self.Object.InList[0].addObject(spline)

            #sweep the sketch template along the newly-created path
            self.Object.Sweep = self._build_sweep(self.Object.InList[0], self.Object.SweepTemplate, spline)

            self.Object.SweepPath = spline

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
