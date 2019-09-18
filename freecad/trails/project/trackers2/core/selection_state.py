# -*- coding: utf-8 -*-
#***********************************************************************
#*                                                                     *
#* Copyright (c) 2018 Joel Graff <monograff76@gmail.com>               *
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
Select state class
"""

from ...support.singleton import Singleton
from ...support.const import Const

class SelectionStateEnum(Const):
    """
    Enumerants for selection state management
    """

    NONE = 0
    PARTIAL = 1
    FULL = 2
    MANUAL = 3

class SelectionState(metaclass=Singleton):
    """
    Singlton state class for managing tracker selections
    """

    def __init__(self):
        """
        Constructor
        """

        self._full = []
        self._partial = []
        self._manual = []

    def count(self):
        """
        Return the number of selected trackers
        """

        return len(self._full)

    def is_selected(self, tracker):
        """
        Return whether or not the tracker exists in the list
        """

        if tracker in self._full:
            return SelectionStateEnum.FULL

        if tracker in self._manual:
            return SelectionStateEnum.MANUAL

        if tracker in self._partial:
            return SelectionStateEnum.PARTIAL

        return SelectionStateEnum.NONE

    def clear_state(self):
        """
        Clear the select state completely
        """

        self._full.clear()
        self._partial.clear()
        self._manual.clear()

    def deselect(self, tracker):
        """
        Deselect the provided tracker from whatever state it's found
        """

        if tracker in self._full:
            self._full.remove(tracker)

        if tracker in self._partial:
            self._partial.remove(tracker)

        if tracker in self._manual:
            self._manual.remove(tracker)

    def manual_select(self, tracker=None):
        """
        Manual selection for trackers that are not fully or partially
        managed
        """

        if not tracker:
            self._manual.clear()

        else:
            self._manual.append(tracker)

    def partial_select(self, tracker=None):
        """
        Manual selection for trackers that are not fully or partially
        managed
        """

        if not tracker:
            self._partial.clear()

        else:
            self._partial.append(tracker)

    def select(self, tracker=None, component=None, multi=False, force=False):
        """
        Select or unselect the passed tracker
        A null tracker will clear the selection for single select and
        will have no effect for multi-select
        """

        #manual selection overrides full / partial
        if tracker in self._manual:
            return

        #force-select a node
        if force and tracker:
            if tracker not in self._full:
                self._full.append(tracker)
            return

        #is it already selected?  are we picking it?
        _exists = tracker in self._full
        _picking = tracker.name == component

        ####################
        # Single-select case
        ####################

        if not multi:

            #1. Force clear conditions (choose nothing)
            # -> clear if no tracker is passed or no component is picked
            if tracker is None or not component:
                self.clear_state()

            #2. Support single-select click to begin drag operations
            # -> abort if multiple selections exist
            # -> this ignores partially selected trackers
            if len(self._full) > 1 and tracker in self._full:
                return

            #3. Don't de-select a picked and selected tracker
            # -> clear ONLY IF either the tracker is selected
            # -> or it is picked, but not both.
            if _exists != _picking:
                self.clear_state()

            #if the tracker does not exist and we are picking it, append
            if tracker and not _exists and _picking:
                self._full.append(tracker)

            return

        ###################
        # Multi-select case
        ###################

        #no tracker passed or not picking the curreng tracker:
        if tracker is None or not _picking:
            return

        if not _exists:
            self._full.append(tracker)
