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
Support class for creating Coin3D node structures
"""

from . import coin_utils as utils
from .coin_enums import NodeTypes as Nodes

class CoinGroup(object):
    """
    Basic coin scenegraph node structure for use with trackers
    """

    scenegraph_root = None

    def __init__(self, is_separator=False, is_switched=False,
                 switch_first=True, parent=None, name=''):

        """
        Constructor
        parent = CoinGroup or SoNode
        """

        self.name = name

        if not self.name:
            self.name = 'CoinGroup'

        self.top = None
        self.parent = None
        self.group = None
        self.callback = None
        self.picker = None
        self.draw_style = None
        self.transform = None
        self.coordinate = None
        self.color = None
        self.switch = None
        self.line_set = None
        self.marker_set = None
        self.root = None

        _top_group = None

        if is_switched:
            self.switch = utils.add_child(
                Nodes.SWITCH, None, self.name + '__Switch')

            self.root = self.switch

        if is_separator:
            self.separator = utils.add_child(
                Nodes.SEPARATOR, None, self.name + '__TopSeparator')

            _top_group = self.separator

        else:
            self.group = utils.add_child(
                Nodes.GROUP, None, self.name + '__TopGroup')

            _top_group = self.group

        self.top = _top_group

        if not self.root:
            self.root = self.top

        else:
            if not switch_first:
                self.top, self.root = self.root, self.top

            self.root.addChild(self.top)

        if not parent:
            return

        self.parent = parent

        if isinstance(self.parent, CoinGroup):
            self.parent = self.parent.top

        else:
            assert (isinstance(self.parent, Nodes.NODE)),\
                'CoinGroup parent not of CoinGroup or SoNode type'

        utils.insert_child(self.root, self.parent)

    def set_visibility(self, visible=True):
        """
        Update the tracker visibility
        """

        if not self.switch:
            return

        if visible:
            self.switch.whichChild = 0

        else:
            self.switch.whichChild = -1

    def is_visible(self):
        """
        Return the visibility of the tracker
        """
        #pylint: disable=no-member

        if not self.switch:
            return False

        return self.switch.whichChild.getValue() == 0

    def insert_node(self, node, parent=None):
        """
        Insert a node into the current group default node
        """

        if parent is None:
            parent = self.top

        utils.insert_child(node, parent)

    def add_node(self, event_class, name=''):
        """
        Add a new node to the current group
        """

        if not name:
            name = str(event_class.getClassTypeId().getName())

        _name = self.name + '__' + name

        return utils.add_child(event_class, self.top, _name)

    def remove_node(self, node):
        """
        Remove an existing node from the current group
        """

        utils.remove_child(node, self.top)

    def get_path(self, node, parent=None):
        """
        Return the path of a child node of the current parent
        """
        if not parent:
            parent = self.root

        return utils.get_child_path(node, parent)

    def copy(self):
        """
        Return a copy of the group root node
        """

        return self.root.copy()

    def dump(self):
        """
        Convenience function to dump contents of CoinGroup
        """

        utils.dump_node(self.root)

    def finalize(self, parent=None):
        """
        Destroy the CoinGroup Node
        """

        _parent = parent

        if not _parent:
            _parent = self.parent

        if not _parent:
            _parent = CoinGroup.scenegraph_root

        utils.remove_child(self.root, _parent)
