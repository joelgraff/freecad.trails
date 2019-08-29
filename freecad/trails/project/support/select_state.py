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

from .singleton import Singleton
from .mouse_state import MouseState

class SelectState(metaclass=Singleton):
    """
    Singlton state class for managing element selections
    """

    def __init__(self):
        """
        Constructor
        """

        self._selected = []
        self._partial_selected = []
        self._manual_selected = []

    def count(self):
        """
        Return the number of selected elements
        """

        return len(self._selected)

    def is_selected(self, element):
        """
        Return whether or not the element exists in the list
        """

        if element in self._selected:
            return 'FULL'

        if element in self._manual_selected:
            return 'MANUAL'

        if element in self._partial_selected:
            return 'PARTIAL'

        return ''

    def clear_state(self):
        """
        Clear the select state completely
        """

        self._selected.clear()
        self._partial_selected.clear()
        self._manual_selected.clear()

    def manual_select(self, element=None):
        """
        Manual selection for elements that are not fully or partially
        managed
        """

        if not element:
            self._manual_selected.clear()

        else:
            self._manual_selected.append(element)

    def partial_select(self, element=None):
        """
        Manual selection for elements that are not fully or partially
        managed
        """

        if not element:
            self._partial_selected.clear()

        else:
            self._partial_selected.append(element)

    def select(self, element=None, force=False):
        """
        Select or unselect the passed element
        A null element will clear the selection for single select and
        will have no effect for multi-select
        """

        #manual selection overrides full / partial
        if element in self._manual_selected:
            return

        #force-select a node
        if force:
            if not element in self._selected:
                self._selected.append(element)
            return

        #is it already selected?  are we picking it?
        _exists = element in self._selected
        _picking = element.name == MouseState().component

        ####################
        # Single-select case
        ####################

        if not MouseState().ctrlDown:

            #1. Force clear conditions (choose nothing)
            # -> clear if no element is passed or no component is picked
            if element is None or not MouseState().component:
                self.clear_state()

            #2. Support single-select click to begin drag operations
            # -> abort if multiple selections exist
            # -> this ignores partially selected elements
            if len(self._selected) > 1 and element in self._selected:
                return

            #3. Don't de-select a picked and selected element
            # -> clear ONLY IF either the element is selected
            # -> or it is picked, but not both.
            if _exists != _picking:
                self.clear_state()

            #if the element does not exist and we are picking it, append
            if element and not _exists and _picking:
                self._selected.append(element)

            return

        ###################
        # Multi-select case
        ###################

        #no element passed or not picking the curreng element:
        if element is None or not _picking:
            return

        #remove if it exists, append if not
        if _exists:
            self._selected.remove(element)

            if element in self._partial_selected:
                del self._partial_selected[element]

        else:
            self._selected.append(element)

    def is_multi(self):
        """
        Indicates multi-selection state if ctrl is pressed or more than
        one element is selected
        """

        return MouseState().ctrlDown or self.count() > 1
