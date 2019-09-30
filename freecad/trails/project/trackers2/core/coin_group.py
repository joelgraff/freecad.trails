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

from pivy import coin

from DraftGui import todo

class CoinGroup(object):
    """
    Basic coin scenegraph node structure for use with trackers
    """

    scenegraph_root = None

    @staticmethod
    def add_child(event_class, parent, name=''):
        """
        Node creation/insertion function
        """

        _name = name

        if _name == '':
            _name = str(event_class.getClassTypeId().getName())

        _node = event_class()
        _node.setName(_name)

        if parent:
            CoinGroup.insert_child(_node, parent)

        return _node

    @staticmethod
    def remove_child(node, parent):
        """
        Convenience wrapper for _remove_node
        """

        if parent.findChild(node) >= 0:
            todo.delay(parent.removeChild, node)

    @staticmethod
    def insert_child(node, parent, index=-1):
        """
        Insert a node as a child of the passed node
        """

        _fn = parent.addChild

        if index >= 0:
            _fn = lambda _x: parent.insertChild(_x, index)

        print('inserting', node.getName(), 'into parent', parent.getName())
        todo.delay(_fn, node)

    def __init__(
            self, is_separator=False, is_switched=False, parent=None, name=''):

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

        if is_switched:
            self.switch = CoinGroup.add_child(
                coin.SoSwitch, self.root, self.name + '__Switch')

            self.root = self.switch

        if is_separator:
            self.top = CoinGroup.add_child(
                coin.SoSeparator, self.root, self.name + '__TopSeparator')

        else:
            self.top = CoinGroup.add_child(
                coin.SoGroup, self.root, self.name + '__TopGroup')

        #still no root?  the separator / group is top-level
        if not self.root:
            self.root = self.top

        if not parent:
            return

        print('\t\n',self.name, 'Adding root to parent...')

        self.parent = parent

        if isinstance(self.parent, CoinGroup):
            self.parent = self.parent.top

        else:
            assert (isinstance(self.parent, coin.SoNode)),\
                'CoinGroup parent not of CoinGroup or SoNode type'

        CoinGroup.insert_child(self.root, self.parent)

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

    def insert_group(self, coin_group):
        """
        Insert a CoinGroup's root to the current group default node
        """

        CoinGroup.insert_child(coin_group.root, self.top)

    def insert_node(self, node):
        """
        Insert a node into the current group default node
        """

        CoinGroup.insert_child(node, self.top)

    def add_node(self, event_class, name=''):
        """
        Add a new node to the current group
        """

        if not name:
            name = str(event_class.getClassTypeId().getName())

        _name = self.name + '__' + name

        return CoinGroup.add_child(event_class, self.top, _name)

    def copy(self):
        """
        Return a copy of the group root node
        """

        return self.root.copy()

    def finalize(self, parent=None):
        """
        Destroy the CoinGroup Node
        """

        _parent = parent

        if not _parent:
            _parent = self.parent

        if not _parent:
            _parent = CoinGroup.scenegraph_root

        CoinGroup.remove_child(self.root, _parent)
