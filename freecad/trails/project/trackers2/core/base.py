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
Base class for Tracker objects
"""

from pivy import coin

from DraftGui import todo

from .view_state import ViewState

#from ...containers import TrackerContainer

class Base():
    """
    Base class for Tracker objects
    """

    view_state = ViewState()

    def __init__(self, name):
        """
        Constructor
        """

        #name is three parts, delimited by periods ('doc.task.obj')
        #object name is always first
        self.name = name.split('.')[::-1]

        #pad array to ensure three elements
        if len(self.name) < 3:
            self.name += ['']*(3-len(self.name))

        #self.state = TrackerContainer()

        self.sg_root = sg_root

        self.switch = coin.SoSwitch()

        self.base_node = coin.SoSeparator()
        self.picker = coin.SoPickStyle()

        self.base_node.addChild(self.picker)

        self.switch.addChild(self.base_node)
        self.set_visibility()

        super().__init__()

    def copy(self, node=None):
        """
        Return a copy of the tracker node
        """

        #copy operation assumes the geometry should not be controlled
        #by the node switch.  To copy with switch, call copy(self.get_node())
        if not node:
            node = self.base_node

        return node.copy()

    def insert_node(self, node, parent=None, index=None):
        """
        Insert a node as a child of the passed node
        """

        _idx = index

        _fn = None

        if not parent:
            if _idx is None:
                _idx = 0

            _fn = lambda _x: self.sg_root.insertChild(_x, _idx)

        elif _idx is not None:
            _fn = lambda _x: parent.insertChild(_x, _idx)

        else:
            _fn = parent.addChild

        todo.delay(_fn, node)

    def remove_node(self, node, parent=None):
        """
        Convenience wrapper for _remove_node
        """

        if not parent:
            parent = self.sg_root

        if parent.findChild(node) >= 0:
            todo.delay(parent.removeChild, node)

    def set_visibility(self, visible=True):
        """
        Update the tracker visibility
        """

        if visible:
            self.switch.whichChild = 0

        else:
            self.switch.whichChild = -1

    def is_visible(self):
        """
        Return the visibility of the tracker
        """

        return self.switch.whichChild == 0

    def set_pick_style(self, is_pickable):
        """
        Set the selectability of the node using the SoPickStyle node
        """

        _state = coin.SoPickStyle.UNPICKABLE

        if is_pickable:
            _state = coin.SoPickStyle.SHAPE

        self.picker.style.setValue(_state)

    def is_pickable(self):
        """
        Return a bool indicating whether or not the node may be selected
        """

        return self.picker.style.getValue() != coin.SoPickStyle.UNPICKABLE

    def finalize(self, node=None, parent=None):
        """
        Node destruction / cleanup
        """

        if node is None:
            node = self.base_node

        self.remove_node(node, parent)
