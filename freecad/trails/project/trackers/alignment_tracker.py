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
        _curve_list = [None]*num_pi - 2

        _pi_list = [None]*num_pi
        _pi_list[_pi_idx] = self.pi_list[_pi_idx]

        #always start at the curve previous to the current PI, clamped
        _start = utils.clamp(_pi_idx - 2, 0)

        #end for single-select case, first or last node,
        _end = _start + 1

        #single-select case
        if len(selected) == 1:

            #last curve is the curve under the next PI
            if _pi_idx > 0 and _pi_idx < num_pi - 1:
                _end = utils.clamp(_pi_idx + 1, max_val=num_pi)

        #multi-select - set the next PI to None so it's recalculated,
        #last curve is the curve under the previous PI
        else:
            _pi_list[_pi_idx + 1] = self.pi_list[_pi_idx + 1]
            _end = _pi_idx

        #build the curve list
        #all curves None, except the ones to be recalculated
        _curve_list[_start:_end] = self.curves[_start:_end]

        if not isinstance(_curve_list, list):
            _curve_list = [_curve_list]

        self.pi_update = _pi_list

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

        pass

    def drag_callback_dep(self, xform, path, pos):
        """
        Callback for drag operations
        """

        _new_curves = [
            self.curves[_i] if _i else None for _i in self.curve_idx
        ]

        #curve at index 1 will always be defined
        _new_pi = _new_curves[1]['PI'].add(xform)

        if _new_curves[0]:

            _new_curves[0] = {
                'PI': _new_curves[0]['PI'],
                'Radius': _new_curves[0]['Radius'],
                'BearingIn': _new_curves[0]['BearingIn'],
                'BearingOut': support.get_bearing(
                    _new_pi.sub(_new_curves[0]['PI']))
            }

        if _new_curves[1]:

            _b_in = None
            _b_out = None

            if _new_curves[0]:
                _b_in = _new_pi.sub(_new_curves[0]['PI'])

            if _new_curves[2]:
                _b_out = _new_curves[2]['PI'].sub(_new_pi)

            else:
                #get the PI following the selected curve for the bearing
                _xf_pi = self.pi_list[self.curve_idx[1] + 1]
                _xf_pi = self.get_transformed_coordinates(path, [_xf_pi])[0]

                _b_out = _xf_pi.sub(_new_pi)

            #this should never happen
            if not (_b_in or _b_out):
                print('Drag error - selected curve not found.')
                return

            _new_curves[1] = {
                'PI': _new_pi,
                'Radius': _new_curves[1]['Radius'],
                'BearingIn': support.get_bearing(_b_in),
                'BearingOut': support.get_bearing(_b_out)
            }

        #test to ensure it's not a fake curve for multi-select cases
        if _new_curves[2]:

            _new_curves[2] = {
                'PI': _new_curves[2]['PI'],
                'Radius': _new_curves[2]['Radius'],
                'BearingIn': support.get_bearing(
                    _new_curves[2]['PI'].sub(_new_pi)),
                'BearingOut': _new_curves[2]['BearingOut'],
            }

        _coords = []

        for _v in self.curves:

            if not _v:
                continue

            print('getting parameters for arc ', _v)
            _v[1] = arc.get_parameters(_v[1])

            _pts = arc.get_points(_v[1], _dtype=tuple)[0]
            _coords.extend(_pts)

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
