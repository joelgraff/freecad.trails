"""
3D alignment generation tool
"""
# -*- coding: utf-8 -*-
# **************************************************************************
# *                                                                        *
# *  Copyright (c) 2018 Joel Graff <monograff76@gmail.com>                 *
# *                                                                        *
# *  Based on original implementation by microelly.  See stationing.py     *
# *  for original implementation.                                          *
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

import numpy as np
from scipy import interpolate

import FreeCAD as App
import FreeCADGui as Gui
import Draft
import Part

class Generate3dAlignment():
    """
    Horizontal alignment generation class.
    Builds a spline based on a selected group of horizontal curve objects
    """
    dms_to_deg = staticmethod(lambda _x: _x[0] + _x[1] / 60.0 + _x[2] / 3600.0)

    def __init__(self):
        pass

    def GetResources(self):
        """
        Icon resources.
        """

        icon_path = os.path.dirname(os.path.abspath(__file__))

        icon_path += "../../../icons/new_alignment.svg"

        return {'Pixmap'  : icon_path,
                'Accel'   : "Ctrl+Alt+G",
                'MenuText': "Generate 3D Alignment",
                'ToolTip' : "Generate the 3D Alignment from an Alignment group",
                'CmdType' : "ForEdit"}

    def validate_selection(self):
        """
        Validate the selected object as either a horizontal and vertical alignment or
        an alignment group that contains the two alignments.
        Return the two alignments as a list of objects
        """

        sel = Gui.Selection.getSelection()

        objs = []
        obj_list = sel

        if sel[0].TypeId == 'App::DocumentObjectGroup':
            obj_list = sel[0].OutList

        for obj in obj_list:
            if obj.TypeId == 'Part::Part2DObjectPython':
                objs.append(obj)

        if len(objs) == 2:
            if ('HA' in objs[0].Label) & ('VA' in objs[1].Label):
                return objs

            if ('HA' in objs[1].Label) & ('VA' in objs[0].Label):
                return [objs[1], objs[0]]

        return None

    def build_alignment(self, alignments):
        """
        Build a 3D alignment from the supplied alignments
        """

        parent = alignments[0].InList[0]

        #get list of geometry edges
        edges = [alignments[0].Shape.Edges[0], alignments[1].Shape.Edges[0]]

        #get the horizontal curve's first and last parameters
        params = [edges[0].FirstParameter, edges[0].LastParameter]

        #get the length of the curve and set the step interval
        hz_len = edges[0].Length

        #default 1-foot resolution
        step = 304.80

        points = []

        #divide the length by the number of steps, truncating the integer
        #then add one for the concluding point for the steps,
        #plus a point for the end of the edge, if the step point falls short
        point_count = int(hz_len / float(step)) + 1

        if ((point_count - 1) * step) < hz_len:
            point_count += 1

        #vertial curve as equidistant points at the step interval...
        vt_pts = edges[1].discretize(Number=point_count, First=0.00, Last=hz_len)

        end_point = vt_pts[point_count - 1]

        #this pairs coordinates of like axes in three tuples (x_coords,y_coords,z)
        vt_pt_axes = np.array(vt_pts).swapaxes(0, 1)

        #save the x_coords/y_coords coordinate pairs in separate variables
        x_coords = []
        _i = 0.0

        while _i <= hz_len:
            x_coords.append(_i)
            _i += step

        #if we added two to the point count, then the step interval
        #won't quite make it to the end... add the length as the last point
        if len(x_coords) < point_count:
            x_coords.append(hz_len)

        y_coords = vt_pt_axes[1]

        #append the final elevation - see above
        if (len(y_coords) < point_count):
            y_coords = np.append(y_coords, end_point.y)

        #interpolation...
        ff = interpolate.interp1d(x_coords, y_coords, kind='cubic', bounds_error=False, fill_value=0)

        ll = int(edges[0].Length) + 1

        #create a set of x_coords-values evenly spaced between 0 and ll at the specified step interval
        xnew = np.arange(0, ll, step)

        if xnew[-1] != edges[0].Length:
            xnew = np.append(xnew, edges[0].Length)

        #interpolates y_coords values for the specified x_coords values
        ynew = ff(xnew)

        for i in range(xnew.shape[0]):

            position = params[0] + step * (params[1] - params[0]) / hz_len * i

            #x,y coordinate on horizontal
            point = edges[0].Curve.value(position)

            #generate z-coordinate for 3D spline
            points.append(App.Vector(point.x, point.y, ynew[i]))

        res = App.activeDocument().addObject('Part::Feature','Composite_' + parent.Label)

        _s = Part.BSplineCurve()
        _s.interpolate(points)

        res.Shape = _s.toShape()

        parent.addObject(res)

        App.ActiveDocument.recompute()

        return res

    def Activated(self):
        """
        Generate the 3D alignment
        """

        objs = self.validate_selection()

        if objs is None:
            print('Valid alignment group not found')
            return

        self.build_alignment(objs)

Gui.addCommand('Generate3dAlignment', Generate3dAlignment())
