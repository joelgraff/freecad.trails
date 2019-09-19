class A():

    def __init__(self):

        print('init A')
        super().__init__()

class B():

    def __init__(self):

        print('init B')
        super().__init__()

class C():

    def __init__(self):

        print('init C')
        super().__init__()

class D(B, C):

    def __init__(self):

        print('init D')
        super().__init__()

class E():

    def __init__(self):

        print('init E')
        super().__init__()

class F():

    def __init__(self):

        print('init F')
        super().__init__()

class G(F, E, D, A):

    def __init__(self):

        self.x = 15
        self.y = 25
        self.z = 87

        print('init G')
        super().__init__()

    def __str__(self):
        print('_s_')
        return '({}, {}, {})'.format(self.x, self.y, self.z)

    def __repr__(self):
        print('_r_')
        return self.__str__()
