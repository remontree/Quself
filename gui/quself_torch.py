import numpy as np
import matplotlib.pyplot as plt
import math
import torch
#from splash import Ui_SplashScreen

version = 1.2
help = ("I","H","X","Y","Z","S","T","SQRT_X","U","RX","RY","RZ","CNOT","CY","CZ","CS","SWAP","TOFFOLI")
class Qcircuit:
    # outer result
    outer_zero = np.array([[1,0],[0,0]]) # |0><0|
    outer_one = np.array([[0,0],[0,1]]) # |1><1|

    # single Quantum Gates
    I_gate = np.array([[1,0],[0,1]])
    H_gate = (1/math.sqrt(2))*np.array([[1,1],[1,-1]])
    X_gate = np.array([[0,1],[1,0]])
    Y_gate = np.array([[0,-1j],[1j,0]])
    Z_gate = np.array([[1,0],[0,-1]])
    S_gate = np.array([[1,0],[0,1j]])
    T_gate = np.array([[1,0],[0,(1+1j)/math.sqrt(2)]])
    SqrtX_gate = (1/math.sqrt(2))*np.array([[1,-1],[1,1]])

    # Class Initalize
    def __init__(self, n):
        self.device = torch.device("cuda:0" if torch.cuda.is_available() else "cpu")
        self.n_resister = n
        self.one_qubit_zero = np.array([[1],[0]]) # |0>
        self.one_qubit_one = np.array([[0],[1]]) # |1>
        self.base = np.array([[1]])
        self.base2 = np.array([[1]])
        for i in range(n):
            self.base = self.mm(self.base,self.one_qubit_zero)
        for i in range(n):
            self.base2 = self.mm(self.base2,self.one_qubit_zero)
    # Function Making a Uf Matrix
    def make_uf_matrix(self,n,gate):
        basis = torch.tensor([[1]]).to(self.device)
        Gate = torch.tensor(gate).to(self.device)
        I_Gate = torch.tensor(self.I_gate).to(self.device)
        for i in range(self.n_resister):
            if i == n:
                basis = torch.kron(basis,Gate)
            else:
                basis = torch.kron(basis,I_Gate)
        
        if self.device != "cpu":
            return np.array((basis.cpu()))
        else:
            return np.array((basis.cpu()))

    def mm(self, a,b):
        result = torch.kron(torch.tensor(a).to(self.device),torch.tensor(b).to(self.device))
        return np.array(result.cpu())

    # Make n qubit gate
    def Two_qubit_gate_to_Nresister(self, U, control, target):
        basis1 = np.array([[1]])
        basis2 = np.array([[1]])
        if control == target:
            raise ValueError("control and target is same!!")
        if self.n_resister < 2:
            raise ValueError("This gate requires least 2 qubits but your circuit is just one or zero qubits")
        if control >= self.n_resister or target >= self.n_resister:
            raise ValueError("control and target should be small than N")
        for i in range(self.n_resister):
            if i == control:
                basis1 = self.mm(basis1,self.outer_zero)
            else:
                basis1 = self.mm(basis1,self.I_gate)
        for i in range(self.n_resister):
            if i == control:
                basis2 = self.mm(basis2,self.outer_one)
            elif i == target:
                basis2 = self.mm(basis2,U)
            else:
                basis2 = self.mm(basis2,self.I_gate)
        return basis1+basis2

    # Apply one qubit gate to the circuit
    def I(self,n):
        basis = self.make_uf_matrix(n,self.I_gate)
        self.base = basis.dot(self.base)
    def H(self,n):
        basis = self.make_uf_matrix(n,self.H_gate)
        self.base = basis.dot(self.base)
    def X(self,n):
        basis = self.make_uf_matrix(n,self.X_gate)
        self.base = basis.dot(self.base)
    def Y(self,n):
        basis = self.make_uf_matrix(n,self.Y_gate)
        self.base = basis.dot(self.base)
    def Z(self,n):
        basis = self.make_uf_matrix(n,self.Z_gate)
        self.base = basis.dot(self.base)
    def S(self,n):
        basis = self.make_uf_matrix(n,self.S_gate)
        self.base = basis.dot(self.base)
    def T(self,n):
        basis = self.make_uf_matrix(n,self.T_gate)
        self.base = basis.dot(self.base)
    def SqrtX(self,n):
        basis = self.make_uf_matrix(n,self.SqrtX_gate)
        self.base = basis.dot(self.base)
    def U(self,n,theta,phi,lamda):
        U_gate = np.array([[math.cos(theta/2),-math.e**(1j*lamda)*math.sin(theta/2)],[math.e**(1j*phi)*math.sin(theta/2),math.e**(1j*(phi+lamda))*math.cos(theta/2)]])
        basis = self.make_uf_matrix(n,U_gate)
        self.base = basis.dot(self.base)
    def RX(self,n,theta):
        self.U(n,theta,-(np.pi/2),np.pi/2)
    def RY(self,n,theta):
        self.U(n,theta,0,0)
    def RZ(self,n,phi):
        self.U(n,0,0,phi)

    # Apply two qubit gate to the circuit
    def CNOT(self,control,target):
        basis = self.Two_qubit_gate_to_Nresister(U = self.X_gate,control = control, target = target)
        self.base = basis.dot(self.base)
    def CY(self,control,target):
        basis = self.Two_qubit_gate_to_Nresister(U = self.Y_gate,control = control, target = target)
        self.base = basis.dot(self.base)
    def CZ(self,control,target):
        basis = self.Two_qubit_gate_to_Nresister(U = self.Z_gate,control = control, target = target)
        self.base = basis.dot(self.base)
    def CS(self,control,target):
        basis = self.Two_qubit_gate_to_Nresister(U = self.S_gate,control = control, target = target)
        self.base = basis.dot(self.base)
    def SWAP(self,target1,target2):
        if(target1==target2):
            raise ValueError("targets are same")
        if(target1>target2):
            target1,target2 = target2,target1
        self.CNOT(target1,target2)
        self.CNOT(target2,target1)
        self.CNOT(target1,target2)

    # Apply three qubit gate to the circuit
    def TOFFOLI(self,control1,control2,target):
        if((control1==control2 and control1 == target)or(control1==target)or(control1==control2)or(control2==target)):
            raise ValueError("given values are not collect")
        control1 += 1
        control2 += 1
        target += 1
        basis = np.array([([0] * 2**self.n_resister)] * 2**self.n_resister)
        M = 2**(self.n_resister-control1)+2**(self.n_resister-control2)
        d = lambda i : 2**(self.n_resister-target) if (2**(self.n_resister-target)) & (i) == 0 else -(2**(self.n_resister-target))
        for i in range(2**self.n_resister) :
            for j in range(2**self.n_resister) :
                basis[i][j] = 1 if (i & M == M and j == d(i) + i) or (i & M != M and j == i) else 0
        self.base = basis.dot(self.base)

    # Visualization the statevector and Probabilities
    def graph(self,fig):
        statevector = []
        probabilities = []
        fig.figure.clf()
        plt.style.use("dark_background")
        for i in range(len(self.base)):
            statevector.append(self.base[i][0])
            probabilities.append(abs(self.base[i][0])**2) #확률진폭의 제곱
        x = np.arange(2**self.n_resister)
        try:
            ax = fig.figure.add_subplot(1,2,1)
            ax.bar(x, statevector, color = '#D99282')
            ax.set_facecolor('#0000')
            ax.set_xlabel("value", size=14)
            ax.set_ylabel("amplitude", size=14)
            ax.set_title("Statevector")
        except:
            ax = fig.figure.add_subplot(1, 2, 1)
            ax.bar(x, self.base2)
            ax.set_xlabel("value", size=14)
            ax.set_ylabel("amplitude", size=14)
            ax.set_title("Statevector - imagine number")

        ax2 = fig.figure.add_subplot(1,2,2)
        ax2.bar(x,probabilities,color = '#8EBFA3')
        ax2.set_xlabel("value",size=14)
        ax2.set_facecolor('#0000')
        ax2.set_ylabel("probabilities",size=14)
        ax2.set_title("Probabilities")
        ax2.set_ylim([0, 1])
        fig.draw()
        return plt

    # Measure all qubits (simulation)
    def Measure(self,shot=1):
        probabilities = []
        result = [0]*2**self.n_resister
        for i in range(len(self.base)):
            probabilities.append(abs(self.base[i][0])**2)
        x = np.arange(2**self.n_resister)
        for i in range(shot):
            b = np.random.choice(x, 1, replace=False, p=probabilities)
            result[int(b)] += 1
        return result
    def M_graph(self,result,fig):
        fig.figure.clf()
        x = np.arange(2**self.n_resister)
        y = result
        plt.figure(facecolor='#202124')
        ax = fig.figure.add_subplot()
        ax.bar(x, y, color="#7BA1A6")
        ax.set_title("Measure")
        ax.set_facecolor('#202124')
        #plt.style.use("dark_background")
        fig.draw()
        return plt
    # Print Circuit Value
    def __str__(self):
        output = ""
        for i in range(2**self.n_resister):
            output+="{0}|{1}>".format(complex(self.base[i]),i)
            if i != 2**self.n_resister-1:
                output+="+"
        return output

    # delete instance
    def __del__(self):
        pass
