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
