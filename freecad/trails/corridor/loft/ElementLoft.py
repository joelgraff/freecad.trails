# -*- coding: utf-8 -*-
# **************************************************************************
# *                                                                        *
# *  Copyright (c) 2019 Joel Graff <monograff76@gmail.com>                         *
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
DESCRIPTION
"""
import FreeCAD as App
import FreeCADGui as Gui
import Part

from Project.Support import Properties

_CLASS_NAME = 'ElementLoft'
_TYPE = 'Part::FeaturePython'

__title__ = _CLASS_NAME + '.py'
__author__ = "Joel Graff"
__url__ = "https://www.freecadweb.org"

def create(spline, sketch, object_name='', parent=None):
    """
    Class construction method
    object_name - Optional. Name of new object.  Defaults to class name.
    parent - Optional.  Reference to existing DocumentObjectGroup.  Defaults to ActiveDocument
    """

    _obj = None
    _name = _CLASS_NAME

    if object_name:
        _name = object_name

    if parent:
        _obj = parent.newObject(_TYPE, _name)
    else:
        _obj = App.ActiveDocument.addObject(_TYPE, _name)

    fpo = _ElementLoft(_obj, spline, sketch)
    _ViewProviderElementLoft(_obj.ViewObject)

    return fpo

class _ElementLoft(object):

    def __init__(self, obj, spline, sketch):
        """
        Main class initialization
        """

        obj.Proxy = self
        self.Type = '_' + _CLASS_NAME
        self.Object = None

        #add class properties
        Properties.add(obj, 'StringList', 'Control_Schedule', 'Schedule for loft controls', [], is_read_only=True, is_hidden=False)
        Properties.add(obj, 'Link', 'Alignment', 'Linked alignment', spline)
        Properties.add(obj, 'Link', 'Template', 'Linked template', sketch)
        Properties.add(obj, 'Float', 'Interval', 'Section spacing interval', 100.0)
        Properties.add(obj, 'FloatList', 'Interval_Schedule', 'Schedule for loft section intervals', [], is_read_only=True, is_hidden=False)

        self.Object = obj

    def onDocumentRestored(self, fp):
        """
        Restore object references on reload
        """

        self.Object = fp

    def __getstate__(self):
        """
        State method for serialization
        """
        return self.Type

    def __setstate__(self, state):
        """
        State method for serialization
        """
        if state:
            self.Type = state

    def regenerate(self):
        """
        Regenerate the loft
        """

        spline = self.Object.Alignment
        sketch = self.Object.Template
        interval = self.Object.Interval

        #create loft sections
        section_list = self.build_sections(spline, sketch) #, interval)

        #Part.show(Part.Compound(section_list))
        #create a compound of the components (polygons)
        #section_object.Shape = Part.Compound(section_list)

        #loft the polygons to generate the solid
        #loft_object.Sections = section_object.Shape

        self.Object.Shape = Part.makeLoft(section_list, False, True, False)

    def execute(self, obj):
        """
        Class execute for recompute calls
        """

        #early execution protection
        if not self.Object:
            return

        self.regenerate()

    def show_interval_schedule(self):
        """
        Create a temporary spreadsheet for viewing and
        editing the schedule data
        """
        pass

    @staticmethod
    def build_sections(fpo, sketch, average=True):
        """
        Generate / regenerate the loft along a wire path
        """
        comps = []
        z_up = App.Vector(0, 0, 1)

        prev_tangent = None

        for edge in fpo.Shape.Edges:

            tangent = edge.Curve.Direction

            #average the tangent if desired
            if average and prev_tangent:
                tangent = ((tangent + prev_tangent) / 2.0).normalize()

            x_normal = tangent.cross(z_up).normalize()
            z_normal = tangent.cross(x_normal).normalize()

            if z_normal.z < 0.0:
                z_normal = z_normal.negative()

            for _i in range(0, 1):

                origin = edge.Vertexes[_i].Point
                poly_points = []

                #iterate sketch vertices, scaling them along the normal and adding the origin to locate them
                for sk_vtx in sketch.Shape.Vertexes:
                    point = sk_vtx.Point
                    poly_points.append(origin + (point.x * x_normal) + (point.y * z_normal))

                poly_points.append(origin)

                #generate a polygon of the points and save it
                comps += [Part.makePolygon(poly_points)]

                #averaging tangents on the first tangent
                #requires skipping the end vertex
                if average and not prev_tangent:
                    continue

            if average:
                prev_tangent = tangent

        return comps

    @staticmethod
    def _build_spline_sections(spline, sketch, interval):
        """
        Generate / regenerate the loft along a spline path
        """

        #reference spline curve object
        curve = spline.Shape.Curve

        #return first / last parameters
        [_a, _b] = spline.Shape.ParameterRange

        #round the length up and add one
        length = int(round(_b)) + 1

        comps = []
        z_up = App.Vector(0, 0, 1)

        #iterate the range of the length as integers
        i = 0.0
        step = 304.8 * interval

        sketch_points = []

        for vtx in sketch.Shape.Vertexes:
            sketch_points.append(vtx.Point)

        is_last_section = False

        while i <= length:

            #get the coordinate of the sweep path at the first millimeter
            origin = curve.value(i)

            #get the tangent of the sweep path at that coordinate
            tangent = curve.tangent(i)[0]

            #calculate the normal against z-up and normalize
            x_normal = tangent.cross(z_up).normalize()
            z_normal = tangent.cross(x_normal).normalize()

            #z-coordinate should always be positive
            if z_normal.z < 0.0:
                z_normal = z_normal.negative()

            poly_points = []

            for point in sketch_points:
                poly_points.append(origin + (point.x * x_normal) + (point.y * z_normal))

            poly_points.append(origin)

            #generate a polygon of the points and save it
            comps += [Part.makePolygon(poly_points)]

            i += step

            if i > length:
                if not is_last_section:
                    i = length
                    is_last_section = True

        return comps

class _ViewProviderElementLoft():

    def __init__(self, vobj):
        """
        View Provider initialization
        """
        self.Object = vobj
        vobj.Proxy = self

    def onDocumentRestored(self, vobj):
        """
        Restore object references on reload
        """

        self.Object = vobj

    def getIcon(self):
        """
        Object icon
        """
        return ''

    def attach(self, vobj):
        """
        View Provider Scene subgraph
        """
        return

    def __getstate__(self):
        """
        State method for serialization
        """
        return None

    def __setstate__(self,state):

        """
        State method for serialization
        """
        return None

    def setupContextMenu(self, vobj, menu):
        """
        Object-specific context menu items
        """
        action = menu.addAction("Interval Schedule...")
        action.triggered.connect(lambda: Gui.runCommand('EditIntervals'))
