class A(): #Base

    print('A create' )
    def __init__(self):

        print('init A')
        super().__init__()
"""
    def override_me(self):

        print('A override_me()')
        super().override_me()
"""
class B(): #Style

    print('B create' )
    def __init__(self):

        print('init B')
        super().__init__()

    def refresh(self): print ('style refresh')
"""
    def override_me(self):

        print('B override_me()')
        super().override_me()
"""
class C():

    print('C create' )
    def __init__(self):

        print('init C')
        super().__init__()
"""
    def override_me(self):

        print('C override_me()')
        super().override_me()
"""
class D():

    print('D create' )
    def __init__(self):

        print('init D')
        super().__init__()
"""
    def override_me(self):

        print('D override_me()')
        super().override_me()
"""
class E(D, C): #Selection

    print('E create' )
    def refresh(self): print('self refresh')

    def __init__(self):

        print('init E')
        super().__init__()

        self.refresh()
"""
    def override_me(self):

        print('E override_me()')
        super().override_me()
"""
class F(): #Geometry

    def refresh(self): print('geo refresh')
    print('F create' )
    def __init__(self):

        print('init F')
        super().__init__()

        self.refresh()

    def override_me(self):

        print('F override_me()')

        print(dir(super))
        #super().override_me()


class G(A, B, E, F):

    print('G create')
    def __init__(self):

        print('init G')
        super().__init__()
        self.refresh()

    def override_me(self):

        print('G override_me()')
        super().override_me()
