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
Marker tracker class for tracker objects
"""

from .support.smart_tuple import SmartTuple
from .geometry_tracker import GeometryTracker

class MarkerTracker(GeometryTracker):
    """
    Tracker object for nodes
    """

    def __init__(self, name, point, parent):
        """
        Constructor
        """

        super().__init__(name=name, parent=parent)

        self.is_end_node = False
        self.point = tuple(point)
        self.drag_point = self.point

        #build node structure for the node tracker

        self.add_marker_set()

        #self.base_path_node = self.marker_node
        self.set_style()
        self.set_visibility(True)
        self.update(self.point)

    def update(self, coordinates=None):
        """
        Update the coordinate position
        """

        _c = coordinates

        if not _c:
            _c = self.point
        else:
            self.point = SmartTuple(_c)._tuple

        self.drag_point = self.point

        super().update(_c)

        #if self.do_publish:
        #    self.dispatch(Events.NODE.UPDATED, (self.name, coordinates),
        #False)
