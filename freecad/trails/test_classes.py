from pivy import coin
import FreeCADGui as Gui

class A(): #Base

    print('A create' )
    def __init__(self):

        print('init A')
        super().__init__()

class B(): #Style

    print('B create' )
    def __init__(self):

        print('init B')
        super().__init__()

    def refresh(self): print ('style refresh')

class C():

    print('C create' )
    def __init__(self):

        print('init C')
        super().__init__()

class D():

    print('D create' )
    def __init__(self):

        print('init D')
        super().__init__()

class E(D, C): #Selection

    print('E create' )
    def refresh(self): print('sel refresh')

    def __init__(self):

        print('init E')
        super().__init__()

        self.refresh()

class F(): #Geometry

    def refresh(self): print('geo refresh')
    print('F create' )
    def __init__(self):

        print('init F')
        super().__init__()

        self.refresh()

class G(A, B, E, F):

    print('G create')
    def __init__(self):

        print('init G')
        super().__init__()
        self.refresh()

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
