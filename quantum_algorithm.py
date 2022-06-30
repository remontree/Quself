import Quself as qs
import numpy as np

def Hardarmard_N(state, n):
    for i in range(n):
        state.H(i)
    return state.base
def make_basis(target):
    one_qubit_zero = np.array([[1],[0]]) #|0>
    one_qubit_one = np.array([[0],[1]]) #|1>
    base = np.array([[1]])
    for i in range(len(target)):
        if target[i]=='0':
            base = np.kron(base,one_qubit_zero)
        elif target[i]=='1':
            base = np.kron(base,one_qubit_one)
        else:
            raise ValueError("target 입력이 잘못되었습니다.")
    return base
def outer_product(w):
    result = []
    for i in range(w.shape[0]):
        row = []
        for j in range(w.shape[0]):
            value = w[i][0]*w[j][0]
            row.append(value)
        result.append(row)
    return np.array(result)

#grover algorithm----------------------------------------------------------------------------------------------------
def grover_oracle(state, target):
    base = make_basis(target)
    outer = outer_product(base)
    return state - 2*(outer.dot(state))  # (I-2|target><target|)*(|state>)

def grover_algorithm(state,target):
    oracle = grover_oracle(state, target)
    diffuser = 2*(outer_product(state)).dot(oracle) - oracle # (2|state><state| - I)*oracle(|state>)
    return diffuser
#--------------------------------------------------------------------------------------------------------------------
#Deutsch–Jozsa algorithm---------------------------------------------------------------------------------------------
def Deutsch_Jozsa(circuit, oracle):
    Hardarmard_N(circuit,circuit.n_resister)
    oracle(circuit)
    Hardarmard_N(circuit,circuit.n_resister-1)

#--------------------------------------------------------------------------------------------------------------------
