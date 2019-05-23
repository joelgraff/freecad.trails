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

from ...geometry import support
from .base_tracker import BaseTracker

class AlignmentTracker(BaseTracker):
    """
    Tracker class for alignment design
    """

    def __init__(self, doc, view, object_name, model):
        """
        Constructor
        """

        self.model = model

        _names = [doc.Name, object_name, 'ALIGNMENT_TRACKER']
        super().__init__(names=_names, select=False, group=True)

    def get_selection_group(self, pi_coords):
        """
        Return a node of coordinates and lines which represents the
        discretized alignment from the end of the curve at the specified
        PI coordinate to the end of the alignment
        """

        if len(pi_coords) < 2:
            return coin.SoGroup()

        pi_coord = pi_coords[0]

        _start_sta = 0.0

        for _curve in self.model.data['geometry']:

            _pi = _curve.get('PI')

            if not _pi:
                continue

            if support.within_tolerance(_pi, pi_coord, 0.1):
                _start_sta = _curve['InternalStation'][1]

        _geo = self.model.discretize_geometry([_start_sta])

        _group = coin.SoGroup()
        _group.setName('ALIGNMENT_TRACKER')

        _coord = coin.SoCoordinate3()
        _coord.point.setValues(0, len(_geo), [list(_v) for _v in _geo])

        _line = coin.SoLineSet()

        _group.addChild(_coord)
        _group.addChild(_line)

        return _group

    def get_connection_group(self, selected):
        """
        Build the connection group based on passed selected PI's
        """

        if len(selected) < 1:
            return coin.SoGroup()

        _pi_start = selected[0]
        _curves = [{}]

        for _curve in self.model.data['geometry']:

            _pi = _curve.get('PI')

            if _pi is None:
                continue

            #if the start curve is selected, save the next curve and break
            #(only one PI is selected)
            if len(_curves) == 2:
                _curves.append(_curve)
                break

            #save the start curve and break if more than one PI is selected
            if support.within_tolerance(_pi, _pi_start, 0.1):
                _curves.append(_curve)

                if len(selected) > 1:
                    break

            #save the pi as the previous curve until the start curve is found
            if len(_curves) == 1:
                _curves[0] = _curve

        _start_sta = _curves[0]['InternalStation'][0]
        _end_sta = _curves[-1]['InternalStation'][1]

        _coords = self.model.discretize_geometry([_start_sta, _end_sta])

        _group = coin.SoGroup()
        _group.setName('ALIGNMENT_TRACKER')

        _coord = coin.SoCoordinate3()
        _coord.point.setValues(0, len(_coords), [list(_v) for _v in _coords])

        _line = coin.SoLineSet()

        _group.addChild(_coord)
        _group.addChild(_line)

        return _group

    def drag_callback(self, xform, pos):
        """
        Callback for drag operations
        """

        pass

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
