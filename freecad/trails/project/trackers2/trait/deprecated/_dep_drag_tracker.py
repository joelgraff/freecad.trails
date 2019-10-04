    
    #def __init__(self)
        #self.drag_group = None
        #self.drag_copy = None
        #self.show_drag_line = True

    #def refresh(self, style=None, visible=None):
    #    """
    #    Update the tracker to reflect state changes
    #    """

    #    if visible is not None:
    #        self.set_visibility(visible)

    def mouse_event(self, arg):
        """
        SoLocation2Event callback
        """

        #pre-emptive abort conditions
        if not self.state.enabled.value:
            return

        #if not self.is_visible():
        #    self.refresh()

        self.update_dragging()
        

    def button_event(self, arg):
        """
        SoMouseButtonEvent callback
        """

        #preemptive abort if not both enabled and visible
        if not (self.state.enabled.value and self.is_visible()):
            return

        if MouseState().button1.state != 'DOWN':
            self.update_dragging()
            

        self.refresh()

    def update_dragging(self):
        """
        Test for drag conditions and changes
        """

        #all draggable objects get drag events
        if not self.state.draggable:
            return

        #if mouse is dragging, then start / on drag are viable events
        if MouseState().button1.dragging:

            if not self.state.dragging:
                self.before_drag()
                self.start_drag()

            else:
                self.on_drag()

        #otherwise, end_drag is the only option
        elif self.state.dragging:

            self.end_drag()
            self.state.dragging = False

    def start_drag(self):
        """
        Initialize drag ops
        """

        #copy the tracker node structure to the drag state node for
        #transformations during drag operations

        self.select_state = SelectState().is_selected(self)

        self.drag_copy = self.copy()
        self.drag_group = None

        if self.select_state == 'FULL':
            self.drag_group = DragState().add_node(self.drag_copy)

        elif self.select_state == 'PARTIAL':

            if self.partial_idx:
                self.drag_group = \
                    DragState().add_partial_node(
                        self.drag_copy, self.partial_idx)

        elif self.select_state == 'MANUAL':
            self.drag_group = DragState().add_manual_node(self.drag_copy)

        else:
            self.drag_copy = None

        self.state.dragging = True

        if self.name == MouseState().component:

            DragState().drag_node = self
            DragState().start = MouseState().coordinates
            DragState().coordinates = MouseState().coordinates
            DragState().insert()

    def on_drag(self):
        """
        Ongoing drag ops
        """

        #tracker must be picked for dragging and actively dragged.
        #Prevents multiple updates in the same mose movement

        if not self.state.dragging or self != DragState().drag_node:
            return

        _drag_line_start = DragState().start
        _drag_line_end = MouseState().coordinates
        _mouse_coord = MouseState().coordinates

        #drag rotation
        if MouseState().altDown:

            DragState().rotate(_mouse_coord)

            _ctr = Vector(DragState().transform.center.getValue())
            _offset = Vector(DragState().transform.translation.getValue())

            _drag_line_start = _ctr.add(_offset)

            _mouse_coord = DragState().coordinates

        #drag translation
        else:
            DragState().translate(_mouse_coord)

        #save the drag state coordinate as the current mouse coordinate
        DragState().coordinates = _mouse_coord

        if self.show_drag_line:
            DragState().update(_drag_line_start, _drag_line_end)

    def end_drag(self):
        """
        Terminate drag ops
        """

        if not self.state.dragging:
            return

        self.drag_copy = None
        self.drag_group = None
        self.select_state = None
        self.state.dragging = False

        DragState().finish()
