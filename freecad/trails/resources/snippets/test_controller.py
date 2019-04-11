from pivy import coin
import FreeCAD
import FreeCADGui

def handler(arg):
    FreeCAD.Console.PrintMessage("dragger moved")

dragger = coin.SoTranslate1Dragger()
view = FreeCADGui.ActiveDocument.ActiveView
sg = view.getSceneGraph()
sg.addChild(dragger)
view.addDraggerCallback(dragger, "addFinishCallback", handler)