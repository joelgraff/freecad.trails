# /**********************************************************************
# *                                                                     *
# * Copyright (c) 2021 Hakan Seven <hakanseven12@gmail.com>             *
# *                                                                     *
# * This program is free software; you can redistribute it and/or modify*
# * it under the terms of the GNU Lesser General Public License (LGPL)  *
# * as published by the Free Software Foundation; either version 2 of   *
# * the License, or (at your option) any later version.                 *
# * for detail see the LICENCE text file.                               *
# *                                                                     *
# * This program is distributed in the hope that it will be useful,     *
# * but WITHOUT ANY WARRANTY; without even the implied warranty of      *
# * MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the       *
# * GNU Library General Public License for more details.                *
# *                                                                     *
# * You should have received a copy of the GNU Library General Public   *
# * License along with this program; if not, write to the Free Software *
# * Foundation, Inc., 59 Temple Place, Suite 330, Boston, MA  02111-1307*
# * USA                                                                 *
# *                                                                     *
# ***********************************************************************

'''
Create a Volumes Object from FPO.
'''

import FreeCAD
from freecad.trails import ICONPATH


def create():
    obj=FreeCAD.ActiveDocument.addObject(
        "App::DocumentObjectGroupPython", "Volumes")

    obj.Label = "Volumes"
    Volumes(obj)
    ViewProviderVolumes(obj.ViewObject)

    FreeCAD.ActiveDocument.recompute()

    return obj



class Volumes:
    """
    This class is about Point Group Object data features.
    """

    def __init__(self, obj):
        '''
        Set data properties.
        '''
        self.Type = 'Trails::Volumes'

        obj.Proxy = self

    def onChanged(self, fp, prop):
        '''
        Do something when a data property has changed.
        '''
        return

    def execute(self, fp):
        '''
        Do something when doing a recomputation. 
        '''
        return


class ViewProviderVolumes:
    """
    This class is about Point Group Object view features.
    """

    def __init__(self, vobj):
        '''
        Set view properties.
        '''
        self.Object = vobj.Object
        vobj.Proxy = self

    def attach(self, vobj):
        '''
        Create Object visuals in 3D view.
        '''
        self.Object = vobj.Object
        return

    def getIcon(self):
        '''
        Return object treeview icon.
        '''
        return ICONPATH + '/icons/volume.svg'

    def claimChildren(self):
        """
        Provides object grouping
        """
        return self.Object.Group

    def setEdit(self, vobj, mode=0):
        """
        Enable edit
        """
        return True

    def unsetEdit(self, vobj, mode=0):
        """
        Disable edit
        """
        return False

    def doubleClicked(self, vobj):
        """
        Detect double click
        """
        pass

    def setupContextMenu(self, obj, menu):
        """
        Context menu construction
        """
        pass

    def edit(self):
        """
        Edit callback
        """
        pass

    def __getstate__(self):
        """
        Save variables to file.
        """
        return None
 
    def __setstate__(self,state):
        """
        Get variables from file.
        """
        return None
