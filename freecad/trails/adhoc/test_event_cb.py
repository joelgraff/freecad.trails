"""Adhoc class testing"""
from pivy import coin

from ..project.trackers2.support.view_state import ViewState

class EventCB():
    """Adhoc class testing"""
    def __init__(self, use_path=True):
        """docstring"""
        self.node = coin.SoSeparator()
        self.event_cb = coin.SoEventCallback()
        self.coordinate = coin.SoCoordinate3()
        self.marker = coin.SoMarkerSet()
        self.event_cb_switch = coin.SoSwitch()

        self.coordinate.point.setValue((0.0, 0.0, 0.0))
        self.coordinate.setName('coordinate')
        self.event_cb.setName('event_cb')
        self.marker.setName('marker')

        self.cb_sigs = [
            self.event_cb.addEventCallback(
                coin.SoLocation2Event.getClassTypeId(), self.on_mouse_cb),

            self.event_cb.addEventCallback(
                coin.SoMouseButtonEvent.getClassTypeId(), self.on_button_cb)
        ]

        self.event_cb_switch.addChild(self.event_cb)
        self.node.addChild(self.event_cb_switch)
        self.node.addChild(self.coordinate)
        self.node.addChild(self.marker)

        ViewState().sg_root.insertChild(self.node, 0)

        if not use_path:
            return

        _sa = coin.SoSearchAction()
        _sa.setNode(self.marker)
        _sa.apply(ViewState().sg_root)

        self.event_cb.setPath(_sa.getPath())

        self.toggle_events()

    def get_path(self, node):

        _sa = coin.SoSearchAction()
        _sa.setNode(node)
        _sa.apply(ViewState().sg_root)

        return _sa

    def toggle_events(self):
        """docstring"""
        #pylint: disable=no-member
        if self.event_cb_switch.whichChild.getValue() == 0:
            self.event_cb_switch.whichChild = -1
        else:
            self.event_cb_switch.whichChild = 0

    def on_mouse_cb(self, user_data, event_cb):
        """docstring"""
        print('on_mouse_cb')

    def on_button_cb(self, user_data, event_cb):
        """docstring"""
        print('on_button_cb')

        print(event_cb.getPickedPoint().getPath().getTail().getName())
        event_cb.removeEventCallback(
            coin.SoLocation2Event.getClassTypeId(), self.cb_sigs[0])

        event_cb.removeEventCallback(
            coin.SoMouseButtonEvent.getClassTypeId(), self.cb_sigs[1])

        self.cb_sigs.clear()

    def finish(self):

        ViewState().sg_root.removeChild(self.node)

        if not self.cb_sigs:
            return

        self.event_cb.removeEventCallback(
            coin.SoLocation2Event.getClassTypeId(), self.cb_sigs[0])

        self.event_cb.removeEventCallback(
            coin.SoMouseButtonEvent.getClassTypeId(), self.cb_sigs[1])
