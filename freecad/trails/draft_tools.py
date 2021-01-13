## Transplanted from DraftTools to avoid having to import the module

import FreeCAD
import WorkingPlane

FreeCAD.activeDraftCommand = None

if not hasattr(FreeCAD, "DraftWorkingPlane"):
    FreeCAD.DraftWorkingPlane = WorkingPlane.plane()