import Draft

from DraftGui import todo
from pivy import coin


class TrackerBase:
    "A generic Draft Tracker, to be used by other specific trackers"
    def __init__(self, children=[], ontop=False, name=None):

        self.ontop = ontop

        color = coin.SoBaseColor()

        drawstyle = coin.SoDrawStyle()

        node = coin.SoSeparator()
        
        for c in [drawstyle, color] + children:
            node.addChild(c)

        self.switch = coin.SoSwitch() # this is the on/off switch

        if name:
            self.switch.setName(name)

        self.switch.addChild(node)
        self.switch.whichChild = -3

        self.Visible = False

        todo.delay(self._insertSwitch, self.switch)

    def finalize(self):

        todo.delay(self._removeSwitch, self.switch)
        self.switch = None

    def _insertSwitch(self, switch):
        '''insert self.switch into the scene graph.  Must not be called
        from an event handler (or other scene graph traversal).'''
        sg=Draft.get3DView().getSceneGraph()
        if self.ontop:
            sg.insertChild(switch,0)
        else:
            sg.addChild(switch)

    def _removeSwitch(self, switch):
        '''remove self.switch from the scene graph.  As with _insertSwitch,
        must not be called during scene graph traversal).'''
        sg=Draft.get3DView().getSceneGraph()
        if sg.findChild(switch) >= 0:
            sg.removeChild(switch)

    def on(self):
        self.switch.whichChild = 0
        self.Visible = True

    def off(self):
        self.switch.whichChild = -1
        self.Visible = False

    def lowerTracker(self):
        '''lowers the tracker to the bottom of the scenegraph, so
        it doesn't obscure the other objects'''
        if self.switch:
            sg=Draft.get3DView().getSceneGraph()
            sg.removeChild(self.switch)
            sg.addChild(self.switch)

    def raiseTracker(self):
        '''raises the tracker to the top of the scenegraph, so
        it obscures the other objects'''
        if self.switch:
            sg=Draft.get3DView().getSceneGraph()
            sg.removeChild(self.switch)
            sg.insertChild(self.switch,0)