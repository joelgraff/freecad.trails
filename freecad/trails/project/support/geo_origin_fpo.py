class GeoOriginFpo(Singleton)):

    def __init__(self, obj):
        """
        Default Constructor
        """
        obj.Proxy = self
        self.Type = "TransientFpo"
        self.Object = obj

        obj.addProperty(
            'App::PropertyFileIncluded', 'filepath', '').filepath = ''

        self.init = True

    def __getstate__(self):
        return self.Type

    def __setstate__(self, state):
        if state:
            self.Type = state

    def onDocumentRestored(self, obj):

        with open(App.ActiveDocument.TransientDir + '/my_file.txt', 'w', encoding='UTF-8') as _f:
            _f.write('updated at ' + str(datetime.datetime.now()))
