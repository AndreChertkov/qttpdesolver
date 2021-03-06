from .tensor_wrapper.tensor_base import MODE_NP, MODE_TT, MODE_SP
from .tensor_wrapper.vector import Vector
from .tensor_wrapper.matrix import Matrix
from .solvers.solver import SOLVER_FS, SOLVER_FD, create_solver
from .solve import auto_solve
from .pde.pde import Pde