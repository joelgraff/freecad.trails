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
import FreeCADGui as Gui

from .coin_style import CoinStyle
from .base_tracker import BaseTracker
from ..support.const import Const

class NodeTracker(BaseTracker):
    """
    A custom edit tracker
    """


    class STYLE(Const):
        """
        Style constants for nodes
        """

        DEFAULT = {
            'id': 'default',
            'shape': 'default',
            'size': 9,
            'color': (0.8, 0.8, 0.8),
            'select': True
        }

        ROLL_OUTER = {
            'id': 'roll_outer',
            'shape': 'circle',
            'size': 9,
            'color': (0.4, 0.8, 0.4),
            'select': True
        }

        ROLL_INNER = {
            'id': 'roll_inner',
            'shape': 'cross',
            'size': 5,
            'color': (0.4, 0.8, 0.4),
            'select': True
        }

        SELECTED = {
            'id': 'selected',
            'shape': 'default',
            'size': 9,
            'color': (1.0, 0.9, 0.0),
            'select': True
        }

        CROSS = {
            'id': 'cross',
            'shape': 'cross',
            'size': 5,
            'color': (0.8, 0.8, 0.8),
            'select': False
        }

    def __init__(self, view, names, point, nodes=None):
        """
        Constructor
        """

        self.type = 'NODE'
        if not nodes:
            nodes = []

        elif not isinstance(nodes, list):
            nodes = [nodes]

        self.selected = False
        self.enabled = True

        self.coin_style = None

        self.view = view
        self.name = names[2]

        #build node structure for the node tracker
        self.coord = coin.SoCoordinate3()
        self.marker = coin.SoMarkerSet()

        super().__init__(names=names, children=[self.coord, self.marker],
                         select=False, group=True)

        self.set_style(CoinStyle.DEFAULT)

        self.callbacks = [
            self.view.addEventCallback('SoLocation2Event', self.mouse_event),
            self.view.addEventCallback('SoMouseButtonEvent', self.button_event)
        ]

    def set_style(self, style):
        """
        Set the node style
        """

        if self.coin_style == style:
            return

        self.color.rgb = style['color']

        self.marker.markerIndex = \
            Gui.getMarkerIndex(style['shape'], style['size'])

        self.coin_style = style
        self.enabled = style['select']

    def update(self, coord):
        """
        Update the coordinate position
        """

        _c = coord

        if not isinstance(coord, tuple):
            _c = tuple(_c)

        self.coord.point.setValue(_c)

    def get(self):
        """
        Get method
        """

        return Vector(self.coord.point.getValues()[0].getValue())

    def mouse_event(self, arg):
        """
        Mouse movement actions
        """
  
        #skip if currently disabled for various actions
        if not self.enabled:
            return

        #no mouseover porcessing if the node is currently selected
        if self.selected:
            return

        #test to see if this node is under the cursor
        _info = self.view.getObjectInfo(self.view.getCursorPos())

        if not _info:
            self.set_style(CoinStyle.DEFAULT)
            return

        if not self.name in _info['Component']:
            self.set_style(CoinStyle.DEFAULT)
            return

        self.set_style(CoinStyle.SELECTED)

    def button_event(self, arg):
        """
        Button click trapping
        """

        if not self.enabled:
            return

        self.selected = False

        _info = self.view.getObjectInfo(self.view.getCursorPos())

        if not _info:
            self.set_style(CoinStyle.DEFAULT)
            return

        _name = _info['Component']

        if arg['AltDown']:

            if int(_name.split('-')[1]) > int(self.name.split('-')[1]):
                self.set_style(CoinStyle.DEFAULT)
                return

        elif not self.name in _name:
            self.set_style(CoinStyle.DEFAULT)
            return

        self.set_style(CoinStyle.SELECTED)
        self.selected = True

    def finalize(self):
        """
        Cleanup
        """

        if self.callbacks:
            self.callbacks.clear()
