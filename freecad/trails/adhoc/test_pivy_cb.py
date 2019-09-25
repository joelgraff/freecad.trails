from pivy import coin
import FreeCADGui as Gui

class pivy_cb_test_class():

    def __init__(self, obj_id):

        self.view = Gui.ActiveDocument.ActiveView
        self.obj_id = obj_id

        self.pivy_end = self.view.addEventCallbackPivy(coin.SoMouseButtonEvent.getClassTypeId(), self.end_cb)

        self.pivy_active = self.view.addEventCallbackPivy(coin.SoLocation2Event.getClassTypeId(), self.active_cb)

        print(self.obj_id, 'start_cb')

    def active_cb(self, arg):

        print(self.obj_id, 'active_cb')

    def end_cb(self, arg):

        print(self.obj_id, 'end_cb')
        self.view.removeEventCallbackPivy(coin.SoMouseButtonEvent.getClassTypeId(), self.pivy_end)

        self.view.removeEventCallbackPivy(coin.SoLocation2Event.getClassTypeId(), self.pivy_active)

def test_pivy_cb(max=100):

    for _i in range(0, max):
        pivy_cb_test_class(_i)

Gui.ActiveDocument.ActiveView.addEventCallbackPivy(
    coin.SoMouseButtonEvent.getClassTypeId(),
    lambda x: print('Button state: ', x.getEvent().getState())
)