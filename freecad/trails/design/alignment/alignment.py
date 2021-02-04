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
Abstract Class for Alignments
"""

class Alignment():
    """
    Abstract parent class for alignment inheritance
    """

    def __init__(self, obj, label, class_name):
        """
        Constructor
        """

        obj.addProperty('App::PropertyBool', 'Initialized', 'Base', 'Is Initialized').Initialized = True

        obj.Proxy = self

        self.Type = 'Trails::' + class_name
        self.Object = obj

        obj.Label = label

        if not label:
            obj.Label = obj.Name

    def onChanged(self, obj, prop):
        """
        Property change callback stub
        """

        #if Iinitialized property does not exist, object construction is not
        #yet complete and event has been triggered prematurely
        return hasattr(self, 'Object') and hasattr(self.Object, 'Initialized')


    def execute(self, obj):
        """
        Recompute callback stub
        """

        #if Iinitialized property does not exist, object construction is not
        #yet complete and event has been triggered prematurely
        return hasattr(self, 'Object') and hasattr(self.Object, 'Initialized')
