# -*- coding: utf-8 -*-
from ..solver import Solver
from ...tensor_wrapper.vector import Vector
from ...tensor_wrapper.matrix import Matrix

class SolverFS_3d(Solver):
    '''
    3D Finite Sum (FS) solver for elliptic PDEs of the form -div(k grad u) = f.
    See parent class Solver for more details.
    '''
     
    def _gen_coefficients(self, PDE, GRD, d, n, h, dim, mode, tau, verb):
        self.iKx = Vector.func([GRD.xc, GRD.yr, GRD.zr], PDE.k_func, None, 
                               verb, 'iKx', inv=True).diag()
        self.iKy = Vector.func([GRD.xr, GRD.yc, GRD.zr], PDE.k_func, None, 
                               verb, 'iKy', inv=True).diag()
        self.iKz = Vector.func([GRD.xr, GRD.yr, GRD.zc], PDE.k_func, None, 
                               verb, 'iKz', inv=True).diag()
        self.f   = Vector.func([GRD.xr, GRD.yr, GRD.zr], PDE.f_func, None,
                               verb, 'f')
            
    def _gen_matrices(self, d, n, h, dim, mode, tau, verb):
        I = Matrix.eye(d, mode, tau)
        B = Matrix.volterra(d, mode, tau, h)        
        self.Bx = I.kron(I).kron(B) 
        self.By = I.kron(B).kron(I)   
        self.Bz = B.kron(I).kron(I)  
     
        self.iqx = self.iKx.diag().sum_out(dim, 0)
        self.iqy = self.iKy.diag().sum_out(dim, 1)
        self.iqz = self.iKz.diag().sum_out(dim, 2)
        
        self.qx = self.iqx.inv(v0=None, verb=verb, name = 'qx')
        self.qy = self.iqy.inv(v0=None, verb=verb, name = 'qy')
        self.qz = self.iqz.inv(v0=None, verb=verb, name = 'qz')
        
        #TODO! Correct this formulas:
        raise NotImplementedError()
        
        E = Matrix.ones(d, mode, tau)
        self.Wx = self.qx.diag().kron(E)
        self.Wy = E.kron(self.qy.diag())
        self.Wz = E.kron(self.qz.diag())
        
        I3 = Matrix.eye(d*dim, mode, tau)       
        self.Rx = self.iKx.dot(I3-self.Wx.dot(self.iKx)).dot(self.Bx.T)
        self.Ry = self.iKy.dot(I3-self.Wy.dot(self.iKy)).dot(self.By.T)
        self.Rz = self.iKz.dot(I3-self.Wz.dot(self.iKz)).dot(self.Bz.T)
        
        self.Hx = self.Bx.dot(self.Rx)
        self.Hy = self.By.dot(self.Ry)    
        self.Hz = self.Bz.dot(self.Rz)           

    def _gen_system(self, d, n, h, dim, mode, tau, verb):
        self.A = Matrix.block([[self.Hz + self.Hx , self.Hz           ], 
                               [self.Hz           , self.Hz + self.Hy ]])
        self.rhs = self.Hz.dot(self.f)
        self.rhs = Vector.block([self.rhs, self.rhs])
        
    def _gen_solution(self, PDE, LSS, d, n, h, dim, mode, eps, tau, verb):
        sol = LSS.solve(self.A, self.rhs, eps, tau, PDE.sol0, verb)
        self.wx = sol.half(0)
        self.wy = sol.half(1)
        self.ux = self.Rx.dot(self.wx)
        self.uy = self.Ry.dot(self.wy)
        self.uz = self.Rz.dot(self.f - self.wx - self.wy)
        self.u  = self.Hx.dot(self.wx)  