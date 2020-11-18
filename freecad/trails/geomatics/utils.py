
import FreeCADGui
from pivy import coin



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