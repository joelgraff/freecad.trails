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

from .coin_group import CoinGroup
from .publisher import Publisher
from .subscriber import Subscriber
from .event import Event
from .view_state import ViewState
from .mouse_state import MouseState
from .coin_nodes import CoinNodes as Nodes

#from ...containers import TrackerContainer

class Base(Publisher, Subscriber, Event):
    """
    Base class for Tracker objects
    """

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    #'virtual' function declarations overriden by class inheritance
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    #Style
    def set_style(self, style=None, draw=None, color=None):
        """prototype"""; pass

    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Class statics
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~

    #global view state singleton
    view_state = None
    mouse_state = None

    pathed_trackers = []

    """
    @staticmethod
    def search_node(node, parent=None):
       # "#""
       # Searches for a node, returning it's path.
       # Scenegraph root assumed if parent is None
        #"#""

        if not parent:
            parent = Base.view_state.sg_root

        _sa = coin.SoSearchAction()
        _sa.setNode(node)
        _sa.apply(parent)

        return _sa.getPath()

    @staticmethod
    def find_node(node, parent=None):
        #"#""
       # Find a node.
        #"#""

        _path = Base.search_node(node, parent)

        if _path:
            return _path.getTail()

        return None
    """
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    # Class Defiintion
    #~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
    def __init__(self, name, parent=None):
        """
        Constructor
        """

        #name is three parts, delimited by periods ('doc.task.obj')
        #object name is always first
        self.names = name.split('.')[::-1]
        self.name = self.names[0]

        #pad array to ensure three elements
        if len(self.names) < 3:
            self.names += ['']*(3-len(self.names))

        if not Base.view_state:
            Base.view_state = ViewState()

        if not Base.mouse_state:
            Base.mouse_state = MouseState()

        #provide reference to scenegraph root for CoinGroup for default
        #node creation / destruction
        CoinGroup.scenegraph_root = Base.view_state.sg_root

        self.sg_root = self.view_state.sg_root

        self.callbacks = {}

        self.base = CoinGroup(
            is_separator=True, is_switched=True,
            name=self.name, parent=parent)

        self.base.group = CoinGroup(
            is_separator=False, is_switched=False,
            parent=self.base, name=self.name + '__GROUP')

        self.base.path_node = None

        _grp = self.base.group

        _grp.transform = _grp.add_node(Nodes.TRANSFORM, 'Transform')
        _grp.picker = _grp.add_node(Nodes.PICK_STYLE, 'Pick_Style')

        super().__init__()

    def insert_into_scenegraph(self):
        """
        Insert the base node into the scene graph and trigger notifications
        """

        _fn = lambda _x: Base.view_state.sg_root.insertChild(_x, 0)

        todo.delay(_fn, self.base.root)

    def set_pick_style(self, is_pickable):
        """
        Set the selectability of the node using the SoPickStyle node
        """

        _state = coin.SoPickStyle.UNPICKABLE

        if is_pickable:
            _state = coin.SoPickStyle.SHAPE

        self.base.group.picker.style.setValue(_state)

    def is_pickable(self):
        """
        Return a bool indicating whether or not the node may be selected
        """

        return (
            self.base.group.picker.style.getValue() \
                != coin.SoPickStyle.UNPICKABLE)

    def finalize(self, node=None, parent=None):
        """
        Node destruction / cleanup
        """

        self.base.finalize()
