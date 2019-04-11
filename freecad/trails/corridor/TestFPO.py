import FreeCAD as App
import Draft
import Part
import transportationwb

OBJECT_TYPE = "TestFPO"

if App.Gui:
    import FreeCADGui as Gui
    from DraftTools import translate
    from PySide.QtCore import QT_TRANSLATE_NOOP

import FreeCAD as App
import Part

def test_arc():

    # Vectors 
    v0 = App.Vector(0.0, 0.0, 0.0)
    v1 = App.Vector(10.0, 0.0, 0.0)
    v2 = App.Vector(10.0, 10.0, 0.0)

    # Wire
    Draft.makeWire([v0, v1, v2])

    # Arc
    arc = Part.ArcOfCircle(v0, v1, v2)
    Part.show(arc.toShape())
    c = Draft.makeCircle(arc.toShape())

    Draft.autogroup(c)

def makeSweep(path, sections):
    """
    Create a Part::Sweep object and definte it's parameters
    sections - a list containing one or more sections to sweep
    path - the sweep path edge
    """
    sweep = App.ActiveDocument.addObject('Part::Sweep','Sweep')
    sweep.Sections = sections
    sweep.Spine = path
    sweep.Solid=False #True?

    App.ActiveDocument.recompute()

def createTestFpo():

    obj_parent = App.ActiveDocument.addObject("Part::Part2DObjectPython", OBJECT_TYPE)
    obj_child = App.ActiveDocument.addObject("Part::Part2DObjectPython", OBJECT_TYPE)

    #obj.Label = translate("Transportation", OBJECT_TYPE)

    fpo_parent = _TestFPO(obj_parent, 'parent')

    Draft._ViewProviderWire(obj_parent.ViewObject)

    fpo_child = _TestFPO_child(obj_child, 'child')
    fpo_child.Object.FpoParent = fpo_parent.Object

    App.ActiveDocument.recompute()

class _TestFPO(Draft._Wire):

    def __init__(self, obj, nam):
        """
        Default Constructor
        """
        obj.Proxy = self
        self.Type = OBJECT_TYPE
        self.Object = obj
        self.name = nam
        super(_TestFPO, self).__init__(obj)

        self.add_property('App::PropertyLink', 'FpoParent', 'FpoParent').FpoParent = None

        self.init = True

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state

    def CustomFunction(self):

        print ('CUSTOM FUNCTION')

    def add_property(self, prop_type, prop_name, prop_desc):

        return self.Object.addProperty(prop_type, prop_name, OBJECT_TYPE, QT_TRANSLATE_NOOP("App::Property", prop_desc))

    def onChanged(self, obj, prop):

        if not hasattr(self, 'init'):
            return

        print ("property " + prop)
        print (prop)

        prop_obj = obj.getPropertyByName(prop)

        if prop in ["StartStation", "EndStation"]:

            print ("updating property " + prop)
            self.Object.Length = self.Object.EndStation - self.Object.StartStation

        Gui.updateGui()

        if not hasattr(self, "Object"):
            self.Object = obj

class _TestFPO_child(Draft._Wire):

    def __init__(self, obj, nam):
        """
        Default Constructor
        """
        obj.Proxy = self
        self.Type = OBJECT_TYPE
        self.Object = obj
        self.name = nam
        super(_TestFPO_child, self).__init__(obj)

        self.add_property('App::PropertyLink', 'FpoParent', 'FpoParent').FpoParent = None

        self.init = True

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state

    def CustomFunction(self):

        print ('CUSTOM FUNCTION')

    def add_property(self, prop_type, prop_name, prop_desc):

        return self.Object.addProperty(prop_type, prop_name, OBJECT_TYPE, QT_TRANSLATE_NOOP("App::Property", prop_desc))

    def onChanged(self, obj, prop):

        if not hasattr(self, 'init'):
            return

        print ("property " + prop)
        print (prop)

        prop_obj = obj.getPropertyByName(prop)

        if prop in ["StartStation", "EndStation"]:

            print ("updating property " + prop)
            self.Object.Length = self.Object.EndStation - self.Object.StartStation

        Gui.updateGui()

        if not hasattr(self, "Object"):
            self.Object = obj

    def execute(self, fpy):

        print("execute ", self.name)
        print(fpy.FpoParent)

        #self.CustomFunction()

        Gui.updateGui()

        return False

class _ViewProviderCell:

    def __init__(self, obj):
        """
        Initialize the view provider
        """
        obj.Proxy = self

    def __getstate__(self):
        return None
    
    def __setstate__(self, state):
        return None

    def attach(self, obj):
        """
        View provider scene graph initialization
        """
        self.Object = obj.Object

    def updateData(self, fp, prop):
        """
        Property update handler
        """
        print("update data " + prop)
    
    def getDisplayMode(self, obj):
        """
        Valid display modes
        """
        return ["Wireframe"]

    def getDefaultDisplayMode(self):
        """
        Return default display mode
        """
        return "Wireframe"

    def setDisplayMode(self, mode):
        """
        Set mode - wireframe only
        """
        return "Wireframe"

    def onChanged(self, vp, prop):
        """
        Handle individual property changes
        """
        print ("View property changed " + prop)