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
Customized wire tracker from DraftTrackers.wireTracker
"""

from pivy import coin

from ..support.mouse_state import MouseState

from .base_tracker import BaseTracker, TriState
from .coin_style import CoinStyle

class WireTracker(BaseTracker):
    """
    Customized wire tracker
    """

    def __init__(self, view, names, nodes=None):
        """
        Constructor
        """

        self.line = coin.SoLineSet()
        self.name = names[2]
        self.coord = coin.SoCoordinate3()
        self.points = None

        self.selection_nodes = None
        self.mouse = MouseState()
        self.view = view

        if not nodes:
            nodes = []

        elif not isinstance(nodes, list):
            nodes = [nodes]

        nodes += [self.coord, self.line]

        super().__init__(
            names=names, children=nodes)

        self.set_style(CoinStyle.DEFAULT)

        self.callbacks = {
            'SoLocation2Event':
            self.view.addEventCallback('SoLocation2Event', self.mouse_event),

            'SoMouseButtonEvent':
            self.view.addEventCallback('SoMouseButtonEvent', self.button_event)
        }

    def set_selection_nodes(self, nodes):
        """
        Set the list of node trackers that control wire selection
        """

        self.selection_nodes = nodes

    def update(self, points=None):
        """
        Update the wire tracker coordinates based on passed list of
        SoCoordinate3 references
        """

        if not points:
            points = [_v.point for _v in self.selection_nodes]

        if not points:
            return

        _p = points[:]

        if not isinstance(points[0], tuple):
            _p = [tuple(_v) for _v in _p]

        self.coord.point.setValues(0, len(points), _p)
        self.line.numVertices.setValue(len(points))

        self.points = _p

    def button_event(self, arg):
        """
        Mouse button actions
        """

        if not self.is_enabled():
            return

        #no processing if the wire itself is currently selected
        if self.is_selected():
            return

        _states = [_v.is_selected() for _v in self.selection_nodes]

        self.state.selected = TriState.OFF

        if all(_states):
            self.state.selected = TriState.ON

        elif any(_states):
            self.state.selected = TriState.NONE

        _info = self.view.getObjectInfo(self.mouse.pos)

        if not _info:
            self.set_style(CoinStyle.DEFAULT)
            return

        _comp = _info['Component']

        self._process_conditions(_comp)

        _style = CoinStyle.SELECTED

        if not self.name in _comp:

            if not self.is_selected():
                _style = CoinStyle.DEFAULT

        self.set_style(_style)

    def mouse_event(self, arg):
        """
        Mouse movement actions
        """

        if not self.is_enabled():
            return

        #abort if currently selected
        if self.is_selected():
            return

        #test to see if this node is under the cursor
        self.set_style(CoinStyle.SELECTED)

        _info = self.view.getObjectInfo(self.mouse.pos)
        _comp = ''

        if _info:
            _comp = _info['Component']

        self.on()

        if self.name != _comp:

            self.set_style(CoinStyle.DEFAULT)
            self._process_conditions(_comp)

    def finalize(self, node=None, parent=None):
        """
        Cleanup
        """

        if self.callbacks:
            for _k, _v in self.callbacks.items():
                self.view.removeEventCallback(_k, _v)

        self.callbacks.clear()

        if node is None:
            node = self.switch

        super().finalize(node, parent)
