"""
Vertical alignment generation tool for creating parabolic vertical curves
"""
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

import os
import math

import FreeCAD as App
import FreeCADGui as Gui
import Draft

class GenerateVerticalAlignment():
    """
    Vertical alignment generation class.
    Builds a spline based on a selected group of Vertical curve objects
    """
    dms_to_deg = staticmethod(lambda _x: _x[0] + _x[1] / 60.0 + _x[2] / 3600.0)
    parabolic_curve = staticmethod(lambda g1, g2, e, l, x: e + (g1 * x) + ((g2 - g1) * x * x) / (2 * l))

    def __init__(self):
        self._scale_factor = 10.0

    def GetResources(self):
        """
        Icon resources.
        """

        icon_path = os.path.dirname(os.path.abspath(__file__))

        icon_path += "../../../../icons/new_alignment.svg"

        return {'Pixmap'  : icon_path,
                'Accel'   : "Alt+G",
                'MenuText': "Generate Vertical Alignment",
                'ToolTip' : "Generate the Vertical Alignment from an Alignment group",
                'CmdType' : "ForEdit"}

    def _get_azimuth(self, angle, quadrant):
        """
        Calculate the azimuth from true bearing.
        Angle - bearing angle in radians
        Quadrant - Quadrant of bearing ('NE', 'NW', 'SE', 'SW')
        """

        #1st quadrnat
        result = angle

        if quadrant == 'NW': #4th quadrant
            result = (2.0 * math.pi) - angle

        elif quadrant == 'SW': #3rd quadrant
            result = math.pi + angle

        elif quadrant == 'SE': #2nd quadrant
            result = math.pi - angle

        return result

    def _project_curve(self, pt, ref_elev, curve, meta, segments = 6):
        """
        Generate opints for a parabolic curve or line segment based on
        the starting point of tangency (PT) in stations, and the VerticalCurve object
        """

        _vpc = self._get_global_sta(curve.PC_Station.Value, meta)
        _g1 = (curve.Grade_In * self._scale_factor) / 100
        _g2 = (curve.Grade_Out * self._scale_factor) / 100
        _len = curve.Length.Value
        _e = ref_elev * self._scale_factor

        points = []

        #if there's more than an inch between the curves, or the curve is a breakpoint, start a tangent
#        if offset > 25.4 or _len == 0.0:
#            _g2 = _g1
#            _len = offset
            #_e = _e + offset * _g1
#            _vpc = pt

        seg_len = _len / float(segments)

        start_seg = 1

        offset = abs(pt - _vpc)

        if offset > 25.4:
            start_seg = 0
            _e = _e + _g1 * offset

        #zero length curve is a breakpoint
        if _len == 0.0:
            points.append(App.Vector(pt + offset, _e + offset * _g1, 0.0))
            return points

        for _i in range(start_seg, segments + 1):
            _x = _vpc + seg_len * _i
            _z = self.parabolic_curve(_g1, _g2, _e, _len, seg_len * _i)
            points.append(App.Vector(_x, _z, 0.0))

        return points

    def _generate_spline(self, points, label):
        """
        Generate a spline based on passed points
        """

        if len(points) < 2:
            return None

        obj = App.ActiveDocument.addObject("Part::Part2DObjectPython", label)

        Draft._BSpline(obj)

        obj.Closed = False
        obj.Points = points
        obj.Support = None
        obj.Label = label

        Draft._ViewProviderWire(obj.ViewObject)

        return obj

    def _generate_wire(self, points, label):
        """
        Generate a wire / polyline of the supplied list of points
        """

        if len(points) < 2:
            return None

#        obj = App.ActiveDocument.addObject("Part::Part2DObjectPython", label)

        pl = App.Placement()
        pl.Rotation.Q = (0.0, -0.0, -0.0, 1.0)
        pl.Base = points[0]

        line = Draft.makeWire(points, placement=pl, closed=False, face=True, support=None)

        Draft.autogroup(line)

        return line

    def _get_global_sta(self, local_sta, meta):
        """
        Convert a station to a generic, zero-based global station
        independent of alignment station equations.
        This is equivalent to the distance along an alignment
        from the start station provided by the metadata objecet
        """

        eq_name = 'Equation_1'
        eq_no = 1
        eq_list = []

        while eq_name in meta.PropertiesList:

            eq_list.append(meta.getPropertyByName(eq_name))
            eq_no += 1

            eq_name = 'Equation_' + str(eq_no)

        fwd_sta = meta.Start_Station.Value
        end_sta = meta.End_Station.Value
        offset = 0

        for st_eq in eq_list:

            bck_sta = st_eq[0] * 304.8

            if fwd_sta <= local_sta <= bck_sta:
                return  (local_sta - fwd_sta) + offset

            offset += (bck_sta - fwd_sta)
            fwd_sta = st_eq[1] * 304.8

        #if we're still here, the value hasn't been located.
        #final test between the last forward station and the end
        if fwd_sta <= local_sta <= end_sta:
            return (local_sta - fwd_sta) + offset

        return -1.0

    def _get_reference_coordinates(self, alignment, station):
        """
        Return the x,y,z coordinates of a station along the specified alignment
        """

        spline = App.ActiveDocument.getObject('HA_' + alignment)
        parent_meta = App.ActiveDocument.getObject(alignment + '_metadata')

        if spline is None:
            print('Reference spline not found: ', 'HA_' + alignment)
            return None

        distance = self._get_global_sta(station, parent_meta)

        if distance < 0.0:
            print('invalid station')
            return None

        result = spline.Shape.discretize(Distance=distance)[1]

        if len(result) < 2:
            print('failed to discretize')
            return None

        return result

    def build_alignment(self, alignment):
        """
        Generate the Vertical alignment
        """

        meta = None
        curves = None

        for item in alignment.InList[0].OutList:

            if 'metadata' in item.Label:
                meta = item

            if 'Vertical' in item.Label:
                curves = item

        if meta is None:
            print('Alignment metadata not found')
            return

        if curves is None:
            print('Vertical curve data not found')
            return

        cur_pt = self._get_global_sta(meta.Start_Station.Value, meta)

        if cur_pt == -1:
            print("unable to convert station ", meta.Start_Station, "to global stationing")
            return

        App.ActiveDocument.recompute()

        ref_elev = curves.OutList[0].PC_Elevation.Value
        points = [App.Vector(0.0, ref_elev * self._scale_factor, 0.0)]

        count = 0

        for curve in curves.OutList:

            points.extend(self._project_curve(cur_pt, ref_elev, curve, meta))
            cur_pt = self._get_global_sta(curve.PT_Station.Value, meta)
            ref_elev = curve.PT_Elevation.Value

            count += 1

        parent = curves.InList[0]

        spline_name = 'VA_' + parent.Label

        #rebuild the spline
        spline = self._generate_spline(points, spline_name)

        parent.addObject(spline)

        return spline

###########################

        #adjust vertices by the reference delta, if there's a reference point
        ref_point = None

        if meta.Alignment != '':
            print('getting reference alignment...')
            ref_point = self._get_reference_coordinates(meta.Alignment, meta.Primary.Value)

            if ref_point is None:
                print("Invalid reference alignment")
                return

        if not ref_point is None:

            #get the distance of the reference point along the secondary alignment
            #first converting to global stationing
            side_position = self._get_global_sta(meta.Secondary.Value, meta)
            side_start_sta = self._get_global_sta(meta.Start_Station.Value, meta)

            ref_dist = side_position - side_start_sta
            ref_delta = ref_point

            #discretize the spline to get the cartesian coordinate of the reference point
            #and subtract it from the starting point to get the deltas
            if ref_dist > 0.0:
                ref_coord = spline.Shape.discretize(Distance=ref_dist)[1]
                ref_delta = ref_delta.add(points[0].sub(ref_coord))

            #adjust the alignment points by the deltas
            for _x in range(0, len(points)):
                points[_x] = points[_x].add(ref_delta)

            #rebuild the spline
            spline = self._generate_spline(points, spline_name)

        parent.addObject(spline)

        App.ActiveDocument.recompute()

    def validate_selection(self, grp):
        """
        Validate the selected object as either a Vertical group or
        an alignment group that contains a Vertical group.
        """

        if grp.TypeId != 'App::DocumentObjectGroup':
            return None

        if 'Vertical' in grp.Label:
            return grp

        for item in grp.OutList:
            if 'Vertical' in item.Label:
                return item

        return None

    def Activated(self):
        """
        Generate the Vertical alignment
        """

        group = self.validate_selection(Gui.Selection.getSelection()[0])

        if group is None:
            print('Valid Vertical curve group not found')
            return

        print('generating alignment for ', group.Label)
        self.build_alignment(group)

Gui.addCommand('GenerateVerticalAlignment', GenerateVerticalAlignment())
