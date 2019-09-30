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

import FreeCADGui as Gui

#from .publisher_events import PublisherEvents as Events

from .base import Base
from .style import Style
from .select import Select
from .geometry import Geometry
#from .drag import Drag
from .coin_styles import CoinStyles
from .smart_tuple import SmartTuple
from .coin_nodes import CoinNodes as Nodes

class MarkerTracker(Base, Style, Select, Geometry):
    """
    Tracker object for nodes
    """

    def __init__(self, name, point, parent):
        """
        Constructor
        """

        print('\n\tMARKER init...\n')

        super().__init__(name=name, parent=parent)

        self.is_end_node = False
        self.point = tuple(point)
        self.drag_point = self.point

        #build node structure for the node tracker
        print('\n\tMARKER GEOMETRY init...\n')

        self.marker_set = \
            self.geometry.add_node(Nodes.MARKER_SET, self.name + '__MARKER')

        self.set_style(CoinStyles.DEFAULT)

        #self.base_path_node = self.marker_node

        self.base.set_visibility(True)
        self.update()

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

        Geometry.update(self, _c)

        #if self.do_publish:
        #    self.dispatch(Events.NODE.UPDATED, (self.name, coordinates),
        #False)

    def set_style(self, style=None, draw=None, color=None):
        """
        Override style implementation
        """

        Style.set_style(self, style, draw, color)

        self.marker_set.markerIndex = \
            Gui.getMarkerIndex(self.active_style.shape, self.active_style.size)

    def finalize(self, node=None, parent=None):
        """
        Cleanup
        """

        super().finalize()
