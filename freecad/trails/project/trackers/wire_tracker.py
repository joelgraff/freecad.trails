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

from ..support.const import Const
from .base_tracker import BaseTracker
from .coin_style import CoinStyle

class WireTracker(BaseTracker):
    """
    Customized wire tracker
    """


    class STYLE(Const):
        """
        Const Style class
        """

        DEFAULT = {
            'line width': None,
            'line style': coin.SoDrawStyle.LINES,
            'line weight': 3,
            'line pattern': None,
            'color': (0.8, 0.8, 0.8),
            'select': True
        }

        EDIT = {
            'line width': None,
            'line style': coin.SoDrawStyle.LINES,
            'line weight': 3,
            'line pattern': 0x0f0f, #oxaaa
            'select': False
        }

        SELECTED = {
            'id': 'selected',
            'shape': 'default',
            'size': 9,
            'color': (1.0, 0.9, 0.0),
            'select': True
        }

    def __init__(self, view, names, nodes=None, points=None):
        """
        Constructor
        """

        #self.switch = coin.SoSwitch()
        self.line = coin.SoLineSet()
        self.name = names[2]
        self.coord = coin.SoCoordinate3()
        self.points = points
        self.view = view
        self.enabled = True
        self.selected = False
        self.selectable = False
        self.style = CoinStyle.DEFAULT

        if not nodes:
            nodes = []

        elif not isinstance(nodes, list):
            nodes = [nodes]

        nodes += [self.coord, self.line]

        super().__init__(
            names=names, children=nodes, select=self.style['select'])

        self.callbacks = [
            self.view.addEventCallback('SoLocation2Event', self.mouse_event),
            self.view.addEventCallback('SoMouseButtonEvent', self.button_event)
        ]

        self.update()

    def update(self, points=None, placement=None):
        """
        Update
        """

        _tuples = [tuple(_v.get()) for _v in self.points]

        self.coord.point.setValues(0, len(_tuples), _tuples)
        self.line.numVertices.setValue(len(_tuples))

    def update_points(self, points):
        """
        Update the wire tracker coordinates based on passed list of
        SoCoordinate3 references
        """

        _p = points

        if not isinstance(points[0], tuple):
            _p = [tuple(_v) for _v in points]

        self.coord.point.setValues(0, len(points), _p)
        self.line.numVertices.setValue(len(points))

    def update_placement(self, placement):
        """
        Updates the placement for the wire and the trackers
        """

        return

    def default(self):
        """
        Set wire to default style
        """

        self.color.rgb = self.STYLE.DEFAULT['color']

    def select(self):
        """
        Set wire to select style
        """

        self.color.rgb = self.STYLE.SELECTED['color']

    def set_style(self, style):
        """
        Update the tracker style
        """

        if style['line width']:
            self.draw_style.lineWidth = style['line width']

        self.draw_style.style = style['line style']
        self.draw_style.lineWeight = style['line weight']

        if style['line pattern']:
            self.draw_style.linePattern = style['line pattern']

        self.color.rgb = style['color']

    def button_event(self, arg):
        """
        Mouse button actions
        """

        #test to see if the adjacent nodes have been selected.
        #only valid if a multi-selection occurs
        if arg['AltDown'] and not self.selected:
            if all([_v.selected for _v in self.points]):
                self.set_style(CoinStyle.SELECTED)
                self.selected = True

        #if selected and any of the nodes are deselected, then deselect
        elif self.selected:
            if not all([_v.selected for _v in self.points]):
                self.set_style(CoinStyle.DEFAULT)
                self.selected = False

    def mouse_event(self, arg):
        """
        Mouse movement actions
        """

        #skip if currently disabled for various actions
        if not self.enabled:
            return

        #no mouseover processing if the element can't be selected
        if not self.selectable:
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

    def finalize(self):
        """
        Cleanup
        """

        self.remove_node(self.node, self.node)
