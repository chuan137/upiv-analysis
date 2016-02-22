from scipy import optimize
from numpy import *


class Parameter(object):

    def __init__(self, value):
        self.value = value

    def set(self, value):
        self.value = value

    def __call__(self):
        return self.value


def fit(function, parameters, y, x = None, yerr = None):
    def errf(params):
        for i, p in enumerate(parameters):
            p.set(params[i])
        return y - function(x)

    if x is None: x = arange(y.shape[0])
    params = [p() for p in parameters]
    optimize.leastsq(errf, params)


def main():
    A = Parameter(1.0)
    B = Parameter(2.0)
    f = lambda x: A() * x + B()

    x = arange(10)
    y = f(x) + random.rand(10)

    fit(f, [B], y, x)
    print A(), B()

    fit(f, [A], y, x)
    print A(), B()

if __name__ == '__main__':
    main()
