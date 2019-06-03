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
from ..support import utils
from .base_tracker import BaseTracker
from .coin_group import CoinGroup
from .coin_style import CoinStyle

class AlignmentTracker(BaseTracker):
    """
    Tracker class for alignment design
    """

    def __init__(self, doc, view, object_name, alignment):
        """
        Constructor
        """

        self.alignment = alignment
        self.pi_list = self.alignment.model.get_pi_coords()
        self.curves = self.alignment.get_curves()
        self.curve_update = []
        self.pi_update = []
        self.pi_index = -1

        self.start_path = None
        self.drag_start = Vector()
        self.stations = [-1.0, -1.0]

        self.connection = CoinGroup('ALIGNMENT_TRACKER_CONNECTION', True)
        self.selection = CoinGroup('ALIGNMENT_TRACKER_SELECTION', True)

        self.viewport = \
            view.getViewer().getSoRenderManager().getViewportRegion()

        _names = [doc.Name, object_name, 'ALIGNMENT_TRACKER']
        super().__init__(names=_names, select=False, group=True)

    def build_selection_group(self, selected):
        """
        Build the selection group based on the passed selected PI's
        """

        _start_sta = -1.0

        for _curve in self.alignment.get_curves():

            if support.within_tolerance(_curve['PI'], selected[0], 0.1):
                _start_sta = _curve['InternalStation'][1]
                break

        #abort if starting point not found
        if _start_sta < 0.0:
            return

        _geo = self.alignment.model.discretize_geometry([_start_sta])

        self.selection.set_coordinates(_geo)

    def build_connection_group(self, selected):

        _pi_idx = -1

        for _i, _v in enumerate(self.pi_list):

            if support.within_tolerance(_v, selected[0], 0.1):
                _pi_idx = _i
                break

        if _pi_idx == -1:
            return

        num_pi = len(self.pi_list)

        #PI's = #curves + 2 (start and end points)
        _curve_list = [None]*(num_pi-2)

        #first index is the PI that is being dragged / updated
        #second index, if not zero, indicates multi-selection
        _pi_list = [_pi_idx, 0]

        #always start at the curve previous to the current PI, clamped
        _start = utils.clamp(_pi_idx - 2, 0)

        #end for single-select case, first or last node (default case)
        _end = _start + 1

        #multi-select - set the next PI so it gets recaluculated
        if len(selected) > 1:

            _pi_list[1] = _pi_idx + 1
            _end = _pi_idx

        #single-select case, pi selected that isn't start / end
        elif 0 < _pi_idx < num_pi - 1:
                _end = utils.clamp(_pi_idx + 1, max_val=num_pi)

        #build the curve list
        #all curves None, except the ones to be recalculated
        _curve_list[_start:_end] = self.curves[_start:_end]

        if not isinstance(_curve_list, list):
            _curve_list = [_curve_list]

        self.pi_update = _pi_list
        self.curve_update = _curve_list

        _s = [_v['InternalStation'] for _v in _curve_list if _v]

        #create connection geometry nodes
        _sta = [_s[0][0], _s[-1][1]]

        _geo = self.alignment.model.discretize_geometry(_sta)

        self.connection.set_coordinates(_geo)

    def get_transformed_coordinates(self, path, vecs):
        """
        Return the transformed coordinates of the selected nodes based
        on the transformations applied by the drag tracker
        """

        #get the matrix for the transformation
        _matrix = coin.SoGetMatrixAction(self.viewport)
        _matrix.apply(path)

        _xf = _matrix.getMatrix()

        #create the 4D vectors for the transformation
        _vecs = [coin.SbVec4f(tuple(_v) + (1.0,)) for _v in vecs]

        #multiply each coordinate by transformation matrix and return
        #a list of the transformed coordinates, omitting fourth value
        return [Vector(_xf.multVecMatrix(_v).getValue()[:3]) for _v in _vecs]

    def drag_callback(self, xform, path, pos):
        """
        Callback for drag operations
        """

        _new_curves = [None]*len(self.curve_update)

        for _i, _v in enumerate(self.curve_update):

            if not _v:
                continue

            _new_curves[_i] = {
                'BearingIn': _v['BearingIn'],
                'BearingOut': _v['BearingOut'],
                'PI': _v['PI'],
                'Radius': _v['Radius']
            }

            _curve = _new_curves[_i]
            _bearings = [None, None]

            #define selected pi (transformed) and pi immediately after
            _start = xform.add(self.pi_list[self.pi_update[0]])

            #update preceeds the current curve (bearing in only)
            if self.pi_update[0] == _i:
                _bearings[0] = self.pi_list[_i + 1].sub(_start)

            #update is the PI of the current curve (PI and bearings)
            elif self.pi_update[0] == _i + 1:

                _curve['PI'] = _start
                _bearings[0] = _start.sub(self.pi_list[_i])

                _v = self.pi_list[self.pi_update[0] + 1]

                #transform second pi with rotation (multi-selection)
                if self.pi_update[1]:
                    _v = self.get_transformed_coordinates(path, [_v])[0]

                _bearings[1] = _v.sub(_start)

            #update bearings and PI's
            elif self.pi_update[0] == _i + 2:

                _bearings[1] = _start.sub(self.pi_list[_i + 1])

            #update curve bearing angles from the calculated vectors
            for _i, _v in enumerate(['BearingIn', 'BearingOut']):

                if _bearings[_i]:
                    _curve[_v] = support.get_bearing(_bearings[_i])

        _coords = []

        self.connection.set_style(CoinStyle.DEFAULT)

        #recalculate curves
        for _i, _v in enumerate(_new_curves):

            if not _v:
                _last_tan = self.curves[_i]['Tangent']
                continue

            _v = arc.get_parameters(_v)

            _new_curves[_i] = _v
            _pts = arc.get_points(_v, _dtype=tuple)[0]
            _coords.extend(_pts)

        #check for errors, first between the curves
        _prev_tan = 0.0
        _prev_pi = self.pi_list[0]

        for _i, _v in enumerate(_new_curves):

            if not _v:
                _prev_tan = self.curves[_i]['Tangent']
                _prev_pi = self.curves[_i]['PI']
                continue

            if _prev_tan + _v['Tangent'] \
                > _v['PI'].distanceToPoint(_prev_pi):

                self.connection.set_style(CoinStyle.ERROR)
                break

            _prev_tan = _v['Tangent']
            _prev_pi = _v['PI']

        #check for errors next between the last curve and end,
        if self.connection.style != CoinStyle.ERROR:

            _c = _new_curves[-1]

            if _c:

                _p = self.pi_list[-1]

                if self.pi_update[0] == len(self.pi_list) - 1:
                    _p = _start

                if _c['Tangent'] > _c['PI'].distanceToPoint(_p):
                    self.connection.set_style(CoinStyle.ERROR)

        #check for errors next between the last curve and end,
        if self.connection.style != CoinStyle.ERROR:

            _c = _new_curves[0]

            if _c:

                _p = self.pi_list[0]

                if self.pi_update[0] == 0:
                    _p = _start

                if _c['Tangent'] > _c['PI'].distanceToPoint(_p):
                    self.connection.set_style(CoinStyle.ERROR)

        #update connection coordinates
        self.connection.set_coordinates(_coords)

    def begin_drag(self, selected):
        """
        Initialize for dragging operations, initializing selected portion
        of the alignment
        """

        if not selected:
            return

        if len(selected) > 1:
            self.build_selection_group(selected)

        if len(selected) < len(self.pi_list):
            self.build_connection_group(selected)

    def end_drag(self, path=None):
        """
        Cleanup after dragging operations
        """


        pass

    def finalize(self, node=None):
        """
        Override of the parent method
        """

        self.alignment = None

        if not node:
            node = self.node

        super().finalize(node)
