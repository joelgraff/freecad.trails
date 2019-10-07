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
Geometry tracker base class
"""

from .trait.base import Base
from .trait.style import Style
from .trait.event import Event
from .trait.select import Select
from .trait.geometry import Geometry

from .trait.coin.coin_styles import CoinStyles
from .trait.coin.coin_enums import NodeTypes as Nodes
from .trait.coin.coin_enums import MarkerStyles

class GeometryTracker(Base, Style, Event, Select, Geometry):
    """
    Geometry tracker base class
    """

    def __init__(self, name, parent):
        """
        Constructor
        """

        super().__init__(name=name, parent=parent)

        self.coordinates = None
        self.markers = []
        self.lines = []
        self.enforce_pathing = True
        self.coin_style = CoinStyles.DEFAULT
        self.set_style()
        self.separate_select = False

    def update(self, coordinates):
        """
        Update the geometry coordinates
        """

        self.coordinates = coordinates
        Geometry.update(self, coordinates)

    def add_marker_set(self, name=''):
        """
        Add a SoMarkerSet to the tracker
        """

        if not name:
            name = 'MarkerSet'

        _node = self.geometry.add_node(Nodes.MARKER_SET, name)

        self.markers.append(_node)
        self.add_node_events(_node)

    def add_line_set(self, name=''):
        """
        Add a SoLineSet to the tracker
        """

        if not name:
            name = 'LineSet'

        _line = self.geometry.add_node(Nodes.LINE_SET, name)

        self.lines.append(_line)
        self.add_node_events(_line)

    def add_node_events(self, node):
        """
        Set up node events for the passed node
        """

        #optionally create a separate callback node for new geometry
        if self.separate_select:
            self.add_event_callback_node()

        #events are added to the last-added event callback node
        self.add_mouse_event(self.select_mouse_event)
        self.add_button_event(self.select_button_event)

        self.path_nodes.append(node)

    def set_style(self, style=None, draw=None, color=None):
        """
        Override style implementation
        """

        Style.set_style(self, style, draw, color)

        if not self.markers:
            return

        if style is None:
            style = self.active_style

        _marker_index = MarkerStyles.get(style.shape, style.size)

        for _marker in self.markers:
            _marker.markerIndex = _marker_index
