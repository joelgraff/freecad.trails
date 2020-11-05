
import FreeCADGui
from pivy import coin

class GeoNodes:

    @staticmethod
    def create_origin(system=["UTM", "Z1", "FLAT"], coords=[0.0, 0.0, 0.0]):
        """
        Create or configure SoGeoOrigin node.
        Example: 
        system = ["UTM", "Z35", "FLAT"]
        coords = [4275011518.128912, 507510589.4751387, 0.0]
        get_geo(system, coords)
        """

        sg = FreeCADGui.ActiveDocument.ActiveView.getSceneGraph()
        node = sg.getChild(0)

        if not isinstance(node, coin.SoGeoOrigin):
            node = coin.SoGeoOrigin()
            sg.insertChild(node,0)

            node.geoSystem.setValues(system)
            node.geoCoords.setValue(coords[0], coords[1], coords[2])

        geo_system =  node.geoSystem.getValues()
        geo_origin =  node.geoCoords.getValue().getValue()

        return geo_system, geo_origin

class Event:

    def create_callback(self):
        """
        Create new callback.
        """
        # Create an event callback for SwapEdge() function
        self.callback = FreeCADGui.ActiveDocument.ActiveView.addEventCallbackPivy(
            coin.SoMouseButtonEvent.getClassTypeId(), self.listen_callback)

    def remove_callback(self):
        """
        remove callback.
        """
        FreeCADGui.ActiveDocument.ActiveView.removeEventCallbackPivy(
            coin.SoMouseButtonEvent.getClassTypeId(), self.callback)

    def listen_callback(self):
        """
        listen callback and get index of clicked object element.
        """
        # Get event.
        event = cb.getEvent()

        # If mouse right button pressed finish callback.
        if event.getButton() == coin.SoMouseButtonEvent.BUTTON3 \
                and event.getState() == coin.SoMouseButtonEvent.DOWN:
            self.remove_callback()

        # If mouse left button pressed get picked point.
        if event.getButton() == coin.SoMouseButtonEvent.BUTTON1 \
                and event.getState() == coin.SoMouseButtonEvent.DOWN:
            pickedPoint = cb.getPickedPoint()

            # Get index at picket point
            if pickedPoint is not None:
                detail = pickedPoint.getDetail()

                if detail.isOfType(coin.SoFaceDetail.getClassTypeId()):
                    face_detail = coin.cast(
                        detail, str(detail.getTypeId().getName()))
                    index = face_detail.getFaceIndex()
        
        return index