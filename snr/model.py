import numpy as np
from pykalman import KalmanFilter

ndim = 2
timestep = 1
poslim = 0, 1024

coeff_measnoise = 0.1
coeff_transnoise = 0.1

transgain = np.kron( np.array([(1.0, timestep), (0.0,1.0)]), np.eye(ndim))

_G = np.kron( [0.5*timestep**2, timestep], np.eye(ndim) ).T
transnoise = np.dot( _G, np.dot( np.eye(ndim), _G.T ) )
transnoise *= coeff_transnoise

measgain = np.kron(np.array([1.0, 0.0]), np.eye(ndim))

measnoise =  np.eye(ndim)
measnoise *= coeff_measnoise

initcovar = np.diag([.1, .1, 1, 1]) # initial covariant


def init_tracks(obs):
    ''' Initialize tracks based on obs '''
    return [ Track(0, i, m) for i, m in enumerate(obs) ]


class Track(object):

    _F = np.array(transgain)
    _Q = np.array(transnoise)
    _H = np.array(measgain)
    _R = np.array(measnoise)
    _m = initcovar

    def __init__(self, framenumber, id, obs):
        _F, _H, _Q, _R, _m = self._F, self._H, self._Q, self._R, self._m
        _obs = list(obs) + [0, 0]

        self._frame = [ framenumber ]
        self._id = id
        self._mean = [ _obs ]
        self._covariance = [ _m ]

        self._filter = KalmanFilter(_F, _H, _Q, _R, initial_state_mean = _obs, initial_state_covariance = _m)

    def __call__(self):
        pos = [np.split(np.array(_), 2)[0] for _ in self._mean]
        return np.array([[n, p[0], p[1]] for n, p in zip(self._frame, pos)])


    def prediction(self, n):
        pred = np.array(self._mean[-1])
        for i in range(n - self._frame[-1]):
            pred = self._F.dot(pred)
        return pred

