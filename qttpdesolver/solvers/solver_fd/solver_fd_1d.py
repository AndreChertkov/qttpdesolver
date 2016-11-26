# -*- coding: utf-8 -*-
from ..solver import Solver
from ...tensor_wrapper.vector import Vector
from ...tensor_wrapper.matrix import Matrix

class SolverFD_1d(Solver):
    '''
    1D Finite difference (FD) solver for elliptic PDEs of the form 
    -div(k grad u) = f. See parent class Solver for more details.
    '''
    
    def _gen_coefficients(self, PDE, GRD, d, n, h, dim, mode, tau, verb):
        self.Kx = Vector.func([GRD.xc], PDE.k_func, None, 
                              verb, 'Kx').diag()
        self.f  = Vector.func([GRD.xr], PDE.f_func, None,
                              verb, 'f')

    def _gen_matrices(self, d, n, h, dim, mode, tau, verb):
        I = Matrix.eye(d, mode, tau)
        
        self.iBx = Matrix.findif(d, mode, tau, h)   
        
        self.Zx = Matrix.unit(d, mode, tau, -1, -1)
        
        self.Sx = I - self.Zx
        
    def _gen_system(self, d, n, h, dim, mode, tau, verb):
        self.A = self.Sx.dot(self.iBx.T).dot(self.Kx).dot(self.iBx).dot(self.Sx)
        self.A+= self.Zx
        self.rhs = self.Sx.dot(self.f)
    
    def _gen_solution(self, PDE, LSS, d, n, h, dim, mode, eps, tau, verb):
        self.u = LSS.solve(self.A, self.rhs, eps, tau, PDE.sol0, verb)        
        self.ux = self.iBx.dot(self.u)