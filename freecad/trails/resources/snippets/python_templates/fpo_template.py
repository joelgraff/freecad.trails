
# -*- coding: utf-8 -*-
# **************************************************************************
# *                                                                        *
# *  Copyright (c) 20XX AUTHOR_NAME <AUTHOR_EMAIL>                         *
# *                                                                        *
# *  This program is free software; you can redistribute it and/or modify  *
# *  it under the terms of the GNU Lesser General Public License (LGPL)    *
# *  as published by the Free Software Foundation; either version 2 of     *
# *  the License, or (at your option) any later version.                   *
# *  for detail see the LICENCE text file.                                 *
# *                                                                        *
# *  This program is distributed in the hope that it will be useful,       *
# *  but WITHOUT ANY WARRANTY; without even the implied warranty of        *
# *  MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the         *
# *  GNU Library General Public License for more details.                  *
# *                                                                        *
# *  You should have received a copy of the GNU Library General Public     *
# *  License along with this program; if not, write to the Free Software   *
# *  Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307  *
# *  USA                                                                   *
# *                                                                        *
# **************************************************************************

"""
DESCRIPTION
"""
import FreeCAD as App
import Part
from transportationwb import ScriptedObjectSupport as Sos

_CLASS_NAME = 'CLASSNAME'
_TYPE = 'Part::FeaturePython'

__title__ = _CLASS_NAME + '.py'
__author__ = "AUTHOR_NAME"
__url__ = "https://www.freecadweb.org"

def createTEMPLATE_CLASS(object_name='', parent=None):
    """
    Class construction method
    object_name - Optional. Name of new object.  Defaults to class name.
    parent - Optional.  Reference to existing DocumentObjectGroup.  Defaults to ActiveDocument
    """

    _obj = None
    _name = _CLASS_NAME

    if object_name:
        _name = object_name

    if parent:
        _obj = parent.newObject(_TYPE, _name)
    else:
        _obj = App.ActiveDocument.addObject(_TYPE, _name)

    result = _CLASS_TEMPLATE(_obj)
    _ViewProviderCLASS_TEMPLATE(_obj.ViewObject)    

    return result

class _TEMPLATE_CLASS():

    def __init__(self, obj):
        """
        Main class intialization
        """

        self.Enabled = False
        self.Type = "_" + CLASS_NAME
        self.Object = obj

        obj.Proxy = self

        #add class properties
        #Sos._add_property(self, 'PROPERTY_TYPE', 'PROPERTY_NAME', 'PROPERTY_DESC', DEFUALT_VALUE, isReadOnly=False, isHidden=False)

        self.Enabled = True

    def __getstate__(self):
        """
        State method for serialization
        """
        return self.Type

    def __setstate__(self, state):
        """
        State method for serialization
        """
        if state:
            self.Type = state

    def execute(self, obj):
        """
        Class execute for recompute calls
        """
        pass

class _ViewProviderTEMPLATE_CLASS(object):

    def __init__(self, vobj):
        """
        View Provider initialization
        """
        self.Object = vobj.Object

    def getIcon(self):
        """
        Object icon
        """
        return ''

    def attach(self, vobj):
        """
        View Provider Scene subgraph
        """
        pass

    def __getstate__(self):
        """
        State method for serialization
        """
        return None

    def __setstate__(self,state):

        """
        State method for serialization
        """
        return None
