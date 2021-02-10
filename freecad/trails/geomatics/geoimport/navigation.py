from pivy import coin
import math

class Navigation:
    def __init__(self):
        self.view = FreeCADGui.ActiveDocument.ActiveView
        self.camera = self.view.getCameraNode()
        self.view.setCameraType("Perspective")

        campos = FreeCAD.Vector( 0, 0, 2000)
        self.camera.position.setValue(campos)
        nD=100
        fD=12000000
        self.camera.nearDistance.setValue(nD)
        self.camera.farDistance.setValue(fD)

        self.direction = 0.5*math.pi
        self.length = 0.0
        self.width = 0.0
        self.roll = 0.0
        self.speed = 1000

        # Create an event callback for navigator() function
        self.eventcb = self.view.addEventCallbackPivy(coin.SoButtonEvent.getClassTypeId(), self.navigator)

    def navigator(self, cb):
        # Get event
        event = cb.getEvent()

        if event.getTypeId().isDerivedFrom(coin.SoKeyboardEvent.getClassTypeId()):
            campos = FreeCAD.Vector(self.camera.position.getValue().getValue())
            print(campos)

            # If mouse right button pressed finish navigator
            if event.getKey() == coin.SoKeyboardEvent.ESCAPE and event.getState() == coin.SoKeyboardEvent.DOWN:
                self.view.removeEventCallbackPivy(coin.SoButtonEvent.getClassTypeId(), self.eventcb)

                print('FINISH')

            if event.getKey() == coin.SoKeyboardEvent.W and event.getState() == coin.SoKeyboardEvent.DOWN:
                print('FORWARD')

                delta = FreeCAD.Vector(
                    -self.speed*math.cos(self.direction),
                    self.speed*math.sin(self.direction),
                    self.speed*math.sin(self.width/180*math.pi))

                campos = campos.add(delta)

            if event.getKey() == coin.SoKeyboardEvent.A and event.getState() == coin.SoKeyboardEvent.DOWN:
                print('LEFT')

                self.direction -= 0.1
                self.length = -90+self.direction*180/math.pi

            if event.getKey() == coin.SoKeyboardEvent.S and event.getState() == coin.SoKeyboardEvent.DOWN:
                print('BACK')

                delta = FreeCAD.Vector(
                    self.speed*math.cos(self.direction),
                    -self.speed*math.sin(self.direction),
                    -self.speed*math.sin(self.width/180*math.pi))

                campos = campos.add(delta)

            if event.getKey() == coin.SoKeyboardEvent.D and event.getState() == coin.SoKeyboardEvent.DOWN:
                print('RIGHT')

                self.direction += 0.1
                self.length = -90+self.direction*180/math.pi

            pos = FreeCAD.Vector(
                1000*math.sin(self.length/180*math.pi)*math.cos(self.width/180*math.pi),
                1000*math.cos(self.length/180*math.pi)*math.cos(self.width/180*math.pi),
                1000*math.sin(self.width/180*math.pi))

            step = pos.normalize().multiply(200)
            print(campos)
            next_position=campos.add(step)
            print(next_position)

            # camera position
            self.camera.position.setValue(campos) 
            self.camera.pointAt(
                coin.SbVec3f(next_position),
                coin.SbVec3f(0,0.0+math.sin(math.pi*self.roll/180),
                0.0+math.cos(math.pi*self.roll/180)))


