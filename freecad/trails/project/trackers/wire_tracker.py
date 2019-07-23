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

from .base_tracker import BaseTracker
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
        self.view = view
        self.enabled = True
        self.state = 'UNSELECTED'

        self.coin_style = None
        self.selection_nodes = None
        self.mouse = MouseState()

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
            points = self.points

        if not points:
            return

        _p = points[:]

        if not isinstance(points[0], tuple):
            _p = [tuple(_v) for _v in _p]

        self.coord.point.setValues(0, len(points), _p)
        self.line.numVertices.setValue(len(points))

        self.points = _p


    def transform_points(self, points, matrix):
        """
        Update the points with the appropriate transformation and return
        """

        pass

    def set_style(self, style):
        """
        Update the tracker style
        """

        if self.coin_style == style:
            return

        if style['line width']:
            self.draw_style.lineWidth = style['line width']

        self.draw_style.style = style['line style']
        self.draw_style.lineWeight = style['line weight']

        if style['line pattern']:
            self.draw_style.linePattern = style['line pattern']

        self.color.rgb = style['color']

        self.set_selectability(style['select'])

        self.coin_style = style

    def button_event(self, arg):
        """
        Mouse button actions
        """

        if not self.enabled:
            return

        _states = [_v.state == 'SELECTED' for _v in self.selection_nodes]

        self.state = 'UNSELECTED'

        if all(_states):
            self.state = 'SELECTED'
        elif any(_states):
            self.state = 'PARTIAL'

        _info = self.view.getObjectInfo(self.mouse.pos)

        if not _info:
            self.set_style(CoinStyle.DEFAULT)
            return

        _style = CoinStyle.SELECTED

        if not self.name in _info['Component']:

            if self.state == 'UNSELECTED':
                _style = CoinStyle.DEFAULT

        self.set_style(_style)

    def mouse_event(self, arg):
        """
        Mouse movement actions
        """

        #skip if currently disabled for various actions
        if not self.enabled:
            return

        #no mouseover processing if the element can't be selected
        if not self.is_selectable():
            return

        #no mouseover processing if the node is currently selected
        if self.state == 'SELECTED':
            return

        #test to see if this node is under the cursor
        _info = self.view.getObjectInfo(self.mouse.pos)

        if not _info:
            self.set_style(CoinStyle.DEFAULT)
            return

        if not self.name in _info['Component']:
            self.set_style(CoinStyle.DEFAULT)
            return

        self.set_style(CoinStyle.SELECTED)

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
