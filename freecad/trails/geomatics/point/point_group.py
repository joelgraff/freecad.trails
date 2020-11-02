'''Examples for a feature class and its view provider.'''

import FreeCAD, FreeCADGui
from pivy import coin
from ...design.project.support import utils
from freecad.trails import ICONPATH



def create(points, name='Point_group'):
    obj=FreeCAD.ActiveDocument.addObject("App::FeaturePython", name)
    PointGroup(obj)
    obj.Points = points
    ViewProviderPointGroup(obj.ViewObject)


class PointGroup:
    """
    This class is about Point Group Object data features.
    """

    def __init__(self, obj):
        '''
        Set data properties.
        '''

        obj.addProperty(
            "App::PropertyVectorList",
            "Points",
            "Base",
            "List of group points").Points = ()

        obj.Proxy = self
        self.Points = None
   
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


class ViewProviderPointGroup:
    """
    This class is about Point Group Object view features.
    """

    def __init__(self, obj):
        '''
        Set view properties.
        '''

        obj.addProperty(
            "App::PropertyColor",
            "PointColor",
            "Point Style",
            "Color of the point group").PointColor=(1.0,0.0,0.0)

        obj.addProperty(
            "App::PropertyFloatConstraint",
            "PointSize",
            "Point Style",
            "Size of the point group").PointSize=(2.0)

        obj.Proxy = self
        obj.PointSize = (2.0,1.0,64.0,1.0)
 
    def attach(self, obj):
        '''
        Create 3D view.
        '''

        # Get geo system and geo origin.
        geo_system, geo_origin = utils.get_geo(coords=obj.Object.Points[0])

        # Geo coordinates.
        geo_coords = coin.SoGeoCoordinate()
        geo_coords.geoSystem.setValues(geo_system)
        geo_coords.point.values = obj.Object.Points

        # Geo Seperator.
        geo_seperator = coin.SoGeoSeparator()
        geo_seperator.geoSystem.setValues(geo_system)
        geo_seperator.geoCoords.setValue(geo_origin[0], geo_origin[1], geo_origin[2])

        # Point group features.
        points = coin.SoPointSet()
        self.point_color = coin.SoBaseColor()
        self.point_style = coin.SoDrawStyle()
        self.point_style.style = coin.SoDrawStyle.POINTS

        # Highlight for selection.
        highlight = coin.SoType.fromName('SoFCSelection').createInstance()
        highlight.addChild(geo_coords)
        highlight.addChild(points)

        # Point group root.
        point_root = geo_seperator
        point_root.addChild(self.point_color)
        point_root.addChild(self.point_style)
        point_root.addChild(highlight)
        obj.addDisplayMode(point_root,"Point")

        # Take features from properties.
        self.onChanged(obj,"PointSize")
        self.onChanged(obj,"PointColor")
 
    def updateData(self, fp, prop):
        '''If a property of the handled feature has changed we have the chance to handle this here'''
        # fp is the handled feature, prop is the name of the property that has changed
        """
        l = fp.getPropertyByName("Length")
        w = fp.getPropertyByName("Width")
        h = fp.getPropertyByName("Height")
        self.scale.scaleFactor.setValue(float(l),float(w),float(h))
        """
        pass
 
    def getDisplayModes(self,obj):
        '''
        Return a list of display modes.
        '''

        modes=[]
        modes.append("Point")
        return modes
 
    def getDefaultDisplayMode(self):
        '''
        Return the name of the default display mode. It must be defined in getDisplayModes.
        '''

        return "Shaded"
 
    def setDisplayMode(self,mode):
        '''Map the display mode defined in attach with those defined in getDisplayModes.\
                Since they have the same names nothing needs to be done. This method is optional'''
        return mode
 
    def onChanged(self, vp, prop):
        '''Here we can do something when a single property got changed'''

        if prop == "PointSize":
            c = vp.getPropertyByName("PointSize")
            self.point_style.pointSize.setValue(c)

        if prop == "PointColor":
            c = vp.getPropertyByName("PointColor")
            self.point_color.rgb.setValue(c[0],c[1],c[2])
 
    def getIcon(self):
        '''
        Return object treeview icon.
        '''

        return ICONPATH + '/icons/PointGroup.svg'
 
    def __getstate__(self):
        '''When saving the document this object gets stored using Python's json module.\
                Since we have some un-serializable parts here -- the Coin stuff -- we must define this method\
                to return a tuple of all serializable objects or None.'''
        return None
 
    def __setstate__(self,state):
        '''When restoring the serialized object from document we have the chance to set some internals here.\
                Since no data were serialized nothing needs to be done here.'''
        return None