# /**********************************************************************
# *                                                                     *
# * Copyright (c) 2019 Hakan Seven <hakanseven12@gmail.com>             *
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
Create a Point Group Object from FPO.
'''

import FreeCAD, FreeCADGui
from pivy import coin
from freecad.trails import ICONPATH, zone_list



def get(origin=(0, 0, 0)):
    """
    Find the existing Point Groups object
    """
    # Return an existing instance of the same name, if found.
    obj = FreeCAD.ActiveDocument.getObject('GeoOrigin')

    if obj:
        if obj.Origin == FreeCAD.Vector(0, 0, 0):
            obj.Origin = origin
        return obj

    obj = create(origin)
    return obj

def create(origin):
    obj=FreeCAD.ActiveDocument.addObject(
        "App::DocumentObjectGroupPython", "GeoOrigin")
    GeoOrigin(obj)
    obj.UtmZone = "Z1"
    obj.Origin = origin
    ViewProviderGeoOrigin(obj.ViewObject)

    return obj


class GeoOrigin:
    """
    This class is about Point Group Object data features.
    """

    def __init__(self, obj):
        '''
        Set data properties.
        '''
        self.Type = 'Trails::GeoOrigin'

        obj.addProperty(
            "App::PropertyEnumeration",
            "UtmZone",
            "Base",
            "UTM zone").UtmZone = zone_list
        
        obj.addProperty(
            "App::PropertyVector",
            "Origin",
            "Base",
            "Origin point.").Origin = (0, 0, 0)
        
        obj.Proxy = self

        self.UtmZone = None
        self.Origin = None

    def onChanged(self, fp, prop):
        '''
        Do something when a data property has changed.
        '''
        # Set geo origin.
        sg = FreeCADGui.ActiveDocument.ActiveView.getSceneGraph()
        node = sg.getChild(0)

        if not isinstance(node, coin.SoGeoOrigin):
            node = coin.SoGeoOrigin()
            sg.insertChild(node,0)

        if prop == "UtmZone":
            zone = fp.getPropertyByName("UtmZone")
            geo_system = ["UTM", zone, "FLAT"]
            node.geoSystem.setValues(geo_system)

        if prop == "Origin":
            origin = fp.getPropertyByName("Origin")
            node.geoCoords.setValue(
                origin.x, origin.y, 0)

    def execute(self, fp):
        '''
        Do something when doing a recomputation. 
        '''
        return



class ViewProviderGeoOrigin:
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
        return ICONPATH + '/icons/GeoOrigin.svg'

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
        '''
        When saving the document this object gets
        stored using Python's json module.
        '''
        return None
 
    def __setstate__(self,state):
        '''
        When restoring the serialized object from document
        we have the chance to set some internals here.
        '''
        return None