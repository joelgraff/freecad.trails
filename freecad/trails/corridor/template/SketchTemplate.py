

#http://free-cad.sourceforge.net/SrcDocu/dc/d77/
# classSketcher_1_1SketchObjectPy.html
#https://forum.freecadweb.org/viewtopic.php?t=6121
#https://forum.freecadweb.org/viewtopic.php?t=12829

import FreeCAD as App
from ...project.support import properties

def create(sketch_object, template_name):
    """
    Constructor method foor creating a new sketch template
    """

    obj = App.ActiveDocument.addObject(
        "Sketcher::SketchObjectPython", template_name
    )

    _o = _Sketch(obj)

    _o.duplicate(sketch_object)

    App.activeDocument().recompute()

    return _o


class _Sketch(object):

    def __init__(self, obj):

        obj.Proxy = self
        self.Type = self.__class__.__name__
        self.Object = None

        _ViewProvider(obj.ViewObject)

        properties.add(
            obj, 'LinkList', 'Lofts', 'List of dependent lofts',
            is_read_only=True, default_value=[]
        )

        self.Object = obj

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

    def duplicate(self, sketch):
        """
        Duplicate the source sketch in the SketchObjectPython
        """

        for geo in sketch.Geometry:
            index = self.Object.addGeometry(geo)
            self.Object.setConstruction(index, geo.Construction)

        for constraint in sketch.Constraints:
            self.Object.addConstraint(constraint)

        self.Object.Placement = sketch.Placement

        for expr in sketch.ExpressionEngine:
            self.Object.setExpression(expr[0], expr[1])

        self.Object.solve()
        self.Object.recompute()

    def onChanged(self, obj, prop):

        #avoid call during object initializtion
        if not hasattr(self, 'Object'):
            return

        self.myExecute(obj)


    def myExecute(self, obj):

        #if self.Object.Lofts:
        pass
#        try: fa=App.ActiveDocument.curve
#        except: fa=App.ActiveDocument.addObject('Part::Spline','curve')
#        fa.Shape=bc.toShape()
#        fa.ViewObject.LineColor=(.0,1.0,.0)

class _ViewProvider():

    def execute(self, obj):
        obj.recompute()
        #self.myExecute(obj)

    def __init__(self, vobj):
        self.Object = vobj.Object
        vobj.Proxy = self

    def getIcon(self):
        return ''

    def __getstate__(self):
        return None

    def __setstate__(self, state):
        return None
