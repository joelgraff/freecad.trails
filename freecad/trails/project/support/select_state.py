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

    def count(self):
        """
        Return the number of selected elements
        """

        return len(self._selected)

    def exists(self, element):
        """
        Return whether or not the element exists in the list
        """

        return element in self._selected

    def update(self, element=None):
        """
        Select or unselect the passed element
        A null element will clear the selection for single select and
        will have no effec for multi-select
        """

        #is it already selected?  are we picking it?
        _exists = element in self._selected
        _picking = element.name == MouseState().component

        ####################
        # Single-select case
        ####################

        if not MouseState().ctrlDown:

            #clear if no element is passed or no component is picked
            if element is None or not MouseState().component:
                self._selected.clear()

            #abort if multiple selections exist
            if len(self._selected) > 1:
                return

            #clear ONLY IF either the element is selected
            #or it is picked, but not both.
            if _exists != _picking:
                self._selected.clear()

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
        else:
            self._selected.append(element)

    def is_multi(self):
        """
        Indicates multi-selection state if ctrl is pressed or more than
        one element is selected
        """

        return MouseState().ctrlDown or self.count() > 1
