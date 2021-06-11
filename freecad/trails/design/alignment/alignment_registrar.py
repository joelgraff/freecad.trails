# -*- coding: utf-8 -*-
#***********************************************************************
#*                                                                     *
#* Copyright (c) 2021, Joel Graff <monograff76@gmail.com               *
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
Class for restoring alignment data after a document has loaded
"""

from freecad_python_support.singleton import Singleton

class AlignmentRegistrar(metaclass=Singleton):
    """
    Registrar class for managing object data restoration
    """

    def __init__(self):
        """
        Constructor
        """

        self.alignments = []
        self.group = None

    def set_group(self, obj):
        """
        Set the AlignmentGroup object
        """

        self.group = obj

        #force initizliation if alignments are defined:
        if self.alignments:

            for _a in self.alignments:
                self.group.initialize_alignment(_a)

            self.alignments = []

    def register_alignment(self, obj):
        """
        Add the alignment object
        """

        #initialize alignment if group is defined
        if self.group:
            self.group.initialize_alignment(obj)

        #save to list until group is defined
        else:
            self.alignments.append(obj)
