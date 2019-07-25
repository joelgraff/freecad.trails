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
Customized edit tracker from DraftTrackers.editTracker
"""

from pivy import coin

from FreeCAD import Vector

from .coin_style import CoinStyle
from .base_tracker import BaseTracker

from ..support.mouse_state import MouseState

class NodeTracker(BaseTracker):
    """
    Tracker object for nodes
    """

    def __init__(self, view, names, point, nodes=None):
        """
        Constructor
        """

        self.type = 'NODE'

        if not nodes:
            nodes = []

        elif not isinstance(nodes, list):
            nodes = [nodes]

        self.view = view
        self.name = names[2]
        self.mouse = MouseState()
        self.is_end_node = False
        self.point = point

        #build node structure for the node tracker
        self.coord = coin.SoCoordinate3()
        self.marker = coin.SoMarkerSet()

        super().__init__(
            names=names, children=[self.coord, self.marker] + nodes, group=True
        )

        self.set_style(CoinStyle.DEFAULT)

        self.callbacks = {
            'SoLocation2Event':
            self.view.addEventCallback('SoLocation2Event', self.mouse_event),

            'SoMouseButtonEvent':
            self.view.addEventCallback('SoMouseButtonEvent', self.button_event)
        }

        self.update()

    def update(self, coord=None):
        """
        Update the coordinate position
        """

        if not coord:
            coord = self.point

        #if we have a list of points, pick the first
        if isinstance(coord, list):
            coord = coord[0]

        _c = coord

        if not isinstance(coord, tuple):
            _c = tuple(_c)

        self.coord.point.setValue(_c)

        self.point = _c

    def get(self):
        """
        Get method
        """

        return Vector(self.coord.point.getValues()[0].getValue())

    def mouse_event(self, arg):
        """
        Mouse movement actions
        """

        if not self.is_enabled():
            return

        #skip if currently invisible
        #if not self.is_visible():
        #    return

        #skip if the node can't be selected
        if not self.is_selectable():
            return

        #no mouseover processing if the node is currently selected
        if self.is_selected():
            return

        #test to see if this node is under the cursor
        _info = self.view.getObjectInfo(self.mouse.pos)

        _comp = ''

        if _info:
            _comp = _info['Component']

        self.on()

        _style = CoinStyle.SELECTED

        if self.name != _comp:

            self.state.selected = self.State.SELECT_OFF
            _style = CoinStyle.DEFAULT
            self._process_conditions(_comp)

        self.set_style(_style)

    def button_event(self, arg):
        """
        Button click trapping
        """
        #do nothing - state freeze
        if not self.is_enabled():
            return

        #only if mouse button is being released
        if self.mouse.button1.state == 'UP':
            return

        _info = self.view.getObjectInfo(self.mouse.pos)

        #clicking over nothing always unselects everything
        if not _info:
            self.state.selected = self.State.SELECT_OFF
            self.set_style(CoinStyle.DEFAULT)
            return

        _name = _info['Component']

        self._process_conditions(_name)

        #unselction for multi-select case
        if arg['AltDown']:

            if int(_name.split('-')[1]) > int(self.name.split('-')[1]):
                self.state.selected = self.State.SELECT_OFF
                self.set_style(CoinStyle.DEFAULT)
                return

        #show as unselected, but leave state unchanged, as it may be
        #controlled externally
        elif not self.name in _name:

            self.state.selected = self.State.SELECT_OFF
            self.set_style(CoinStyle.DEFAULT)
            return

        self.set_style(CoinStyle.SELECTED)
        self.state.selected = self.State.SELECT_ON

    def finalize(self, node=None, parent=None):
        """
        Cleanup
        """

        if self.callbacks:
            for _k, _v in self.callbacks.items():
                self.view.removeEventCallback(_k, _v)

            self.callbacks.clear()

        super().finalize(self.node, parent)
