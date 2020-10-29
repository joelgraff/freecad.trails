from freecad.trails import import_class

ContextTracker = import_class(
    'pivy_trackers.tracker.context_tracker', 'ContextTracker')

LineTracker= import_class(
    'pivy_trackers.tracker.line_tracker', 'LineTracker')

PolyLineTracker = import_class(
    'pivy_trackers.tracker.polyline_tracker', 'PolyLineTracker')

Drag = import_class(
    'pivy_trackers.trait.drag', 'Drag')
