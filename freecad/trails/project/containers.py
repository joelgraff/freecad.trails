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
Tracker for drag data
"""

from enum import IntEnum, unique

from FreeCAD import Vector

class DragState():
    """
    State class for drag operations
    """
    def __init__(self):
        """
        Constructor
        """

        self.start = None
        self.center = None
        self.rotation = None
        self.position = None
        self.object = None
        self.angle = 0.0
        self.translation = Vector()
        self.multi = False
        self.curves = []
        self.nodes = []
        self.node_idx = []
        self.tracker_state = []

    def reset(self):
        """
        Reset the object to defaults
        """

        self.__init__()

    def __str__(self):

        return '\nstart = ' + str(self.start) \
               + '\ncenter = ' + str(self.center) \
               + '\nrotation = ' + str(self.rotation) \
               + '\nposition = ' + str(self.position) \
               + '\nobject = ' + str(self.object) \
               + '\nangle = ' + str(self.angle) \
               + '\ntranslation = ' + str(self.translation) \
               + '\nmulti = ' + str(self.multi) \
               + '\ncurves = \n' + str(self.curves) \
               + '\nnodes = \n' + str(self.nodes) \
               + '\nnode_idx = \n' + str(self.node_idx) \
               + '\ntracker_state = \n' + str(self.tracker_state)

class TrackerContainer():
    """
    State container for BaseTracker class
    """

    @unique
    class State(IntEnum):
        """
        Enum class
        """

        UNDEFINED = 0
        OFF = 1
        ON = 2
        NONE = 4

    class Property():

        def __init__(self, value):

            self._value = value
            self._ignore_once = False
            self._ignore = False

        def set_value(self, state):
            """
            Set the property state using bools
            """

            if state:
                self._value = TrackerContainer.State.ON
            else:
                self._value = TrackerContainer.State.OFF

        def get_value(self):
            """
            Get the poerty state as bool
            """

            return self._value == TrackerContainer.State.ON

        def ignore_once(self):
            """
            Set the ignore once flag
            """

            self._ignore_once = True
            self._ignore = True

        def set_ignore(self, state):
            """
            Set the ignore flag, clearing _ignore_once
            """

            self._ignore_once = False
            self._ignore = True

        def get_ignore(self):
            """
            Get the ignore flag, clearing _ignore_once
            """

            _result = self._ignore

            if self._ignore_once:

                self._ignore_once = False
                self._ignore = False

            return _result

        value = property(get_value, set_value)
        ignore = property(get_ignore, set_ignore)

    def __init__(self, is_undefined=False):
        """
        Cosntructor
        """

        self.enabled = self.Property(self.State.ON)
        self.visible = self.Property(self.State.ON)
        self.selected = self.Property(self.State.OFF)

        if is_undefined:

            self.enabled._value = self.State.UNDEFINED
            self.visible._value = self.State.UNDEFINED
            self.selected._value = self.State.UNDEFINED
