# initialization
import numpy as np

# importing Qiskit
from qiskit import QuantumCircuit, QuantumRegister, ClassicalRegister
from qiskit.quantum_info.operators import Operator, Pauli
from qiskit.circuit import Gate
from qiskit.extensions.unitary import UnitaryGate
from qiskit.extensions import HamiltonianGate

# import backend tools
from qiskit import Aer, transpile, assemble

# import basic plot tools
from qiskit.visualization import plot_histogram

# set up your parameters
order = 3
qc = np.int64(np.ceil(np.log2(order+1)))

D = 1
Q = 1

cells = 4
space = np.int(np.ceil(np.log2(cells)))

# define your circuit and registers
circuit = QuantumCircuit()

x = []

for i in range(D):
    x.append(QuantumRegister(space,"x"+str(i+1)))
    circuit.add_register(x[i])
    circuit.h(x[i])

f = []

for i in range(Q):
    f.append(QuantumRegister(qc,"f"+str(i)))
    circuit.add_register(f[i])
    
# fc = ClassicalRegister(Q*D,"fout")
fc = ClassicalRegister(cells,"fout")

circuit.add_register(fc)

# define your gates

# define pauli+-
sp = Operator((Pauli("X")).to_matrix()+(1j*Pauli("Y")).to_matrix())
sm = Operator((Pauli("X")).to_matrix()-(1j*Pauli("Y")).to_matrix())
io = Operator(Pauli("I").to_matrix())

#define ladder operators

for j in range(qc):
   
    ad = sp
    a = sm
    
    weight = []
    weight = [(np.int64(np.binary_repr(order+1)[k])/2**k) for k in range(j)]
    weight = np.sum(weight)
    weight = np.sqrt(0.5*np.ceil(order+1))*np.sqrt((1/2**j)+weight)
            
    for i in range(qc-j-1):
        ad = ad.expand(sm)
        a = a.expand(sp)
    
    for i in range(j):
        ad = ad.tensor(io)
        a = a.tensor(io)
    
    ad = weight*ad
    a = weight*a
    
    if j == 0:
        Ad = ad
        A = a
    else:
        Ad = Ad+ad
        A = A+a
        
xop = Operator((Ad+A)*(np.sqrt(2))**(-1))

# initialize in the first cell
finit = 0.5
xop = HamiltonianGate(xop,finit)
# cxop = xop.control()
circuit.append(xop,(f[0],x[0][0]))

# stream the data to left
circuit.cx(x[0][1],x[0][0])
circuit.x(x[0][0])

# circuit.cx(x[0][0],f[1][0])
# circuit.cx(x[0][0],f[2][0])
# stream the data to left
# for i in range(D):
#     for j in range(space-1):
#         circuit.mct([x[i][j+1:space],f[0]],x[i][j])
#     circuit.mct(f[0],x[i][space-1])

# stream the data to right
# for i in range(D):
#     for j in range(space-1):
#         circuit.mct([x[i][j+1:space],f[2]],x[i][j])
#     circuit.mct(f[2],x[i][space-1])

# measure results
circuit.measure(x[0][0],fc[0])
circuit.measure(x[0][1],fc[1])

# circuit.measure(f[1][0],fc[1])
# circuit.measure(f[2][0],fc[2])

# visualize results

circuit.draw("mpl")