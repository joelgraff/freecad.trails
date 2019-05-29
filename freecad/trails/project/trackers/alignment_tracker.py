# -*- coding: utf-8 -*-
#**************************************************************************
#*                                                                     *
#* Copyright (c) 2019 Joel Graff <monograff76@gmail.com>               *
#*                                                                     *
#* This program is free software; you can redistribute it and/or modify*
#* it under the terms of the GNU Lesser General Public License (LGPL)  *
#* as published by the Free Software Foundation; either version 2 of   *
#* the License, or (at your option) any later version.                 *
#* for detail see the LICENCE text file.                               *
#*                                                                     *
#* This program is distributed in the hope that it will be useful,     *
#* but WITHOUT ANY WARRANTY; without even the implied warranty of      *
#* MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the       *
#* GNU Library General Public License for more details.                *
#*                                                                     *
#* You should have received a copy of the GNU Library General Public   *
#* License along with this program; if not, write to the Free Software *
#* Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307*
#* USA                                                                 *
#*                                                                     *
#***********************************************************************
"""
Tracker for alignment drafting
"""

from pivy import coin

from FreeCAD import Vector

from ...geometry import support, arc
from .base_tracker import BaseTracker
from ..support import utils

class AlignmentTracker(BaseTracker):
    """
    Tracker class for alignment design
    """

    class CoinGroup():
        """
        Local class to facilitate tracking nodes in groups
        """

        def __init__(self, id, no_marker=False):
            """
            Constructor
            """

            self.group = coin.SoGroup()
            self.coord = coin.SoCoordinate3()
            self.marker = coin.SoMarkerSet()
            self.line = coin.SoLineSet()

            self.group.addChild(self.coord)

            if not no_marker:
                self.group.addChild(self.marker)

            self.group.addChild(self.line)

            self.group.setName(id)

        def set_coordinates(self, coords):
            """
            Set the coordinate node values
            """

            _count = len(coords)

            self.coord.point.setNum(_count)
            self.coord.point.setValues(0, _count, [list(_v) for _v in coords])

            self.line.numVertices.setValue(_count)

    def __init__(self, doc, view, object_name, model):
        """
        Constructor
        """

        self.model = model
        self.pi_list = model.get_pi_coords()
        self.curves = []
        self.start_pi = Vector()
        self.conn_pi = []
        self.start_path = None
        self.drag_start = Vector()

        self.conn_group = self.CoinGroup('ALIGNMENT_TRACKER_CONNECTION', True)
        self.sel_group = self.CoinGroup('ALIGNMENT_TRACKER_SELECTION')

        self.viewport = \
            view.getViewer().getSoRenderManager().getViewportRegion()

        _names = [doc.Name, object_name, 'ALIGNMENT_TRACKER']
        super().__init__(names=_names, select=False, group=True)

    def get_selection_group(self, pi_coords):
        """
        Return a node of coordinates and lines which represents the
        discretized alignment from the end of the curve at the specified
        PI coordinate to the end of the alignment
        pi-coords = SoCoordinate3 of selected PI's
        """

        if len(pi_coords) < 2:
            return coin.SoGroup()

        _start_sta = 0.0

        for _curve in self.model.data['geometry']:

            _pi = _curve.get('PI')

            if not _pi:
                continue

            if support.within_tolerance(_pi, pi_coords[0], 0.1):
                _start_sta = _curve['InternalStation'][1]

        _geo = self.model.discretize_geometry([_start_sta])

        self.sel_group.set_coordinates(_geo)

        return self.sel_group.group

    def get_connection_group(self, selected):
        """
        Build the connection group based on the passed selected PI's
        """

        #when dragging, if only one node is selected, one PI is transformed
        #and three cruves are re-calculated
        #if multiple nodes are selected, two curves are recalculated

        self.start_pi = -1
        _count = len(selected.point.getValues())
        _start_pi = Vector(selected.point.getValues()[0].getValue())
        _start_pi.z = 0.0

        #get list of curves only (no lines)
        _curves = [
            _v for _v in self.model.data['geometry'] if _v['Type'] == 'Curve'
        ]

        #get the pi index for the selected pi
        for _i, _v in enumerate(self.pi_list):

            if support.within_tolerance(_v, _start_pi, 0.1):
                self.start_pi = _i
                break

        #abort if we can't find the curve under the first selected PI
        if self.start_pi == -1:
            return coin.SoGroup()

        #get a list of curves to be updated
        self.curves = [_curves[_i] \
            if 0 <= _i < len(_curves) else None \
                for _i in list(range(self.start_pi - 2, self.start_pi + 1))
        ]

        #only the first two curves apply in multi-select cases,
        #so just save the next PI as a fake curve
        if _count > 1:
            self.curves[2] = None

        _sta = [_v['InternalStation'] for _v in self.curves if _v]

        #build scenegraph nodes
        _coords = self.model.discretize_geometry([_sta[0][0], _sta[-1][1]])

        self.conn_group.set_coordinates(_coords)

        return self.conn_group.group

    def get_transformed_coordinates(self, path, vecs):
        """
        Return the transformed coordinates of the selected nodes based on the
        transformations applied by the drag tracker
        """

        #get the matrix for the transformation
        _matrix = coin.SoGetMatrixAction(self.viewport)
        _matrix.apply(path)

        _xf = _matrix.getMatrix()

        #create the 4D vectors for the transformation
        _vecs = [coin.SbVec4f(tuple(_v) + (1.0,)) for _v in vecs]

        #multiply each coordinate by the transformation matrix and return
        #a list of the transformed coordinates, omitting the fourth value
        return [Vector(_xf.multVecMatrix(_v).getValue()[:3]) for _v in _vecs]

    def drag_callback(self, xform, path, pos):
        """
        Callback for drag operations
        """

        _new_curves = [None]*3

        _new_pi = self.pi_list[self.start_pi].add(xform)

        if self.curves[0]:
            self.curves[0] = {
                'PI': self.curves[0]['PI'],
                'Radius': self.curves[0]['Radius'],
                'BearingIn': self.curves[0]['BearingIn'],
                'BearingOut': support.get_bearing(
                    _new_pi.sub(self.curves[0]['PI']))
            }

        if self.curves[1]:

            _b_in = None
            _b_out = None

            if self.curves[0]:
                _b_in = _new_pi.sub(self.curves[0]['PI'])

            if self.curves[2]:
                _b_out = self.curves[2]['PI'].sub(_new_pi)

            else:
                _xf_pi = self.pi_list[self.start_pi + 1]
                _xf_pi = self.get_transformed_coordinates(path, [_xf_pi])[0]

                _b_out = _xf_pi.sub(_new_pi)

            #this should never happen
            if not (_b_in or _b_out):
                print('Drag error - selected curve not found.')
                return

            self.curves[1] = {
                'PI': _new_pi,
                'Radius': self.curves[1]['Radius'],
                'BearingIn': support.get_bearing(_b_in),
                'BearingOut': support.get_bearing(_b_out)
            }

        #test to ensure it's not a fake curve for multi-select cases
        if self.curves[2]:
            self.curves[2] = {
                'PI': self.curves[2]['PI'],
                'Radius': self.curves[2]['Radius'],
                'BearingIn': support.get_bearing(
                    self.curves[2]['PI'].sub(_new_pi)),
                'BearingOut': self.curves[2]['BearingOut'],
            }

        _coords = []

        for _v in self.curves:

            if not _v:
                continue

            _v = arc.get_parameters(_v)
            _pts = arc.get_points(_v, _dtype=tuple)[0]
            _coords.extend(_pts)

        self.conn_group.set_coordinates(_coords)

    def update(self, points):
        """
        Update the tracker points and recompute
        """

        pass

    def finalize(self, node=None):
        """
        Override of the parent method
        """

        self.model = None

        if not node:
            node = self.node

        super().finalize(node)
