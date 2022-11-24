import sys
import quself_torch as qs
from PyQt5.QtWidgets import *
from PyQt5.QtCore import *
import qdarktheme
from matplotlib.figure import Figure
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
import numpy as np
import psutil

class MyApp(QMainWindow):
    def __init__(self):
        super().__init__()
        self.qubits = 2
        try:
            self.showDialog()
        except:
            pass
        self.circuit = qs.Qcircuit(self.qubits)
        print("data init")
        self.base = None
        self.initUI()

    def showDialog(self):
        qubit, ok = QInputDialog.getInt(self, 'Qubits', 'Enter the num of qubits:', min = 1, max = 15)
        if ok:
            self.qubits = int(qubit)
    def add(self):
        gate = str(self.select_gate.currentText())
        self.item = QTreeWidgetItem()
        if gate in qs.help[:12]:
            element = [str(self.select_gate.currentText()),str(self.target.value()), "None"]
        elif gate in qs.help[12:-1]:
            element = [str(self.select_gate.currentText()), str(self.target.value()),str(self.control.value())]
        else:
            element = [str(self.select_gate.currentText()), str(self.target.value()), str(self.control.value())+','+str(self.control2.value())]
        for idx, data in enumerate(element):
            self.item.setText(idx, data)
        self.lecture_root.addChild(self.item)

        func = [self.circuit.I, self.circuit.H, self.circuit.X, self.circuit.Y, self.circuit.Z, self.circuit.S, self.circuit.T, self.circuit.SqrtX, self.circuit.U, self.circuit.RX, self.circuit.RY, self.circuit.RZ, self.circuit.CNOT, self.circuit.CY, self.circuit.CZ,self.circuit.CS, self.circuit.SWAP, self.circuit.TOFFOLI]
        if gate in qs.help[:8]:
            func[qs.help.index(gate)](int(self.target.value()))
        elif gate in qs.help[8:12]:
            if gate == 'U':
                func[qs.help.index(gate)](int(self.target.value()), float(self.theta.value()),float(self.phi.value()),float(self.lamda.value()))
            elif gate == 'RZ':
                func[qs.help.index(gate)](int(self.target.value()), float(self.phi.value()))
            else:
                func[qs.help.index(gate)](int(self.target.value()), float(self.theta.value()))
        elif gate in qs.help[12:-1]:
            func[qs.help.index(gate)](int(self.target.value()),int(self.control.value()))
        else:
            func[qs.help.index(gate)](int(self.target.value()),int(self.control.value()),int(self.control2.value()))

        self.circuit.graph(self.canvas)
        self.states.setText(str(self.circuit.base))
        self.ram.setText(self.system_info())
        print(self.circuit.base)

    def disable(self):
        gate = str(self.select_gate.currentText())
        if gate in qs.help[:8]:
            self.control.setDisabled(True)
            self.control2.setDisabled(True)
            self.theta.setDisabled(True)
            self.phi.setDisabled(True)
            self.lamda.setDisabled(True)
        elif gate in qs.help[8:12]:
            self.control.setDisabled(True)
            self.control2.setDisabled(True)
            self.theta.setDisabled(False)
            self.phi.setDisabled(False)
            self.lamda.setDisabled(False)
        elif gate in qs.help[12:-1]:
            self.control.setDisabled(False)
            self.control2.setDisabled(True)
            self.theta.setDisabled(True)
            self.phi.setDisabled(True)
            self.lamda.setDisabled(True)
        else:
            self.control.setDisabled(False)
            self.control2.setDisabled(False)
            self.theta.setDisabled(True)
            self.phi.setDisabled(True)
            self.lamda.setDisabled(True)
    def M_r(self):
        result  =self.circuit.Measure(self.num.value())
        print(result)
        self.ram.setText(self.system_info())
        self.circuit.M_graph(result,self.canvas)
    def Measure(self):
        grid = QGridLayout()
        self.states = QLabel(str(self.circuit.base))
        grid.addWidget(self.states, 0, 0)
        self.num = QSpinBox()
        self.num.setMinimum(1)
        self.num.setMaximum(50000)
        self.num.setSingleStep(1)
        grid.addWidget(QLabel("측정 횟수"),1,0)
        grid.addWidget(self.num, 2, 0)
        M_button = QPushButton('측정')
        M_button.clicked.connect(self.M_r)
        grid.addWidget(M_button, 2, 1)

        s_button = QPushButton('상태 그래프')
        s_button.clicked.connect(lambda: self.circuit.graph(self.canvas))
        grid.addWidget(s_button, 2, 2)

        return grid
    def system_info(self):
        memory_usage_dict = dict(psutil.virtual_memory()._asdict())
        memory_usage_percent = memory_usage_dict['percent']
        return f"RAM Usage: {memory_usage_percent}%"
    def add_gate(self):
        Add_button = QPushButton('추가')
        Add_button.clicked.connect(self.add)

        del_button = QPushButton('초기화')
        del_button.clicked.connect(self.state_init)

        self.select_gate = QComboBox()
        for i in qs.help:
            self.select_gate.addItem(i)
        self.select_gate.currentTextChanged.connect(self.disable)

        self.target = QSpinBox()
        self.target.setMinimum(0)
        self.target.setMaximum(self.qubits-1)
        self.target.setSingleStep(1)

        self.control = QSpinBox()
        self.control.setMinimum(0)
        self.control.setMaximum(self.qubits-1)
        self.control.setSingleStep(1)

        self.control2 = QSpinBox()
        self.control2.setMinimum(0)
        self.control2.setMaximum(self.qubits-1)
        self.control2.setSingleStep(1)

        self.theta = QDoubleSpinBox()
        self.theta.setMinimum(-np.inf)
        self.theta.setMaximum(np.inf)
        self.theta.setSingleStep(1)

        self.phi = QDoubleSpinBox()
        self.phi.setMinimum(-np.inf)
        self.phi.setMaximum(np.inf)
        self.phi.setSingleStep(1)

        self.lamda = QDoubleSpinBox()
        self.lamda.setMinimum(-np.inf)
        self.lamda.setMaximum(np.inf)
        self.lamda.setSingleStep(1)

        self.disable()
        grid = QGridLayout()
        grid.addWidget(QLabel('Select Gate'),0,0)
        grid.addWidget(self.select_gate,1,0)

        grid.addWidget(QLabel('Target Qubit'), 0, 1)
        grid.addWidget(self.target, 1, 1)
        grid.addWidget(QLabel('Control Qubit1'), 2, 1)
        grid.addWidget(self.control, 3, 1)
        grid.addWidget(QLabel('Control Qubit2'), 4, 1)
        grid.addWidget(self.control2, 5, 1)

        grid.addWidget(QLabel('Theta'), 0, 2)
        grid.addWidget(self.theta, 1, 2)
        grid.addWidget(QLabel('Phi'), 2, 2)
        grid.addWidget(self.phi, 3, 2)
        grid.addWidget(QLabel('lamda'), 4, 2)
        grid.addWidget(self.lamda, 5, 2)

        grid.addWidget(Add_button, 4, 5)
        grid.addWidget(del_button, 5, 5)
        grid.addWidget(QLabel('RAM Size: ' + str(round(psutil.virtual_memory().total / (1024.0 ** 3))) + "(GB)"),3,0)
        self.ram = QLabel(self.system_info())
        grid.addWidget(self.ram, 4, 0)

        return grid

    def graph(self):
        vbox = QVBoxLayout()
        self.canvas = FigureCanvas(Figure(figsize=(4, 3)))
        self.canvas.figure.set_facecolor("#202124")
        self.circuit.graph(self.canvas)
        vbox.addWidget(self.canvas)
        return vbox

    def state_init(self):
        cnt = self.lecture_root.childCount()
        while cnt-1>=0:
            currNode = self.lecture_root.child(cnt-1)
            self.lecture_root.removeChild(currNode)
            cnt-=1
        self.circuit.base = self.circuit.base2.copy()
        self.circuit.graph(self.canvas)
        self.states.setText(str(self.circuit.base))

    def initUI(self):
        #self.qubits = 3-1
        menubar = self.menuBar()
        menubar.setNativeMenuBar(True)
        file = menubar.addMenu('File')
        edit = menubar.addMenu('Edit')
        view = menubar.addMenu('View')
        tool = menubar.addMenu('Tools')

        main_layout = QHBoxLayout()
        Circuit_Layout = QVBoxLayout()
        state = QFrame()
        state.setFrameShape(QFrame.Panel | QFrame.Sunken)
        circuit = QFrame()
        circuit.setFrameShape(QFrame.Panel | QFrame.Sunken)
        circuit.setLayout(self.graph())
        measure = QFrame()
        measure.setLayout(self.Measure())
        measure.setFrameShape(QFrame.Panel | QFrame.Sunken)

        self.tree = QTreeWidget(self)
        headers = ['Gate', 'target', 'control']
        self.tree.setColumnCount(len(headers))
        self.tree.setHeaderLabels(headers)

        self.lecture_root = QTreeWidget.invisibleRootItem(self.tree)

        treebox = QVBoxLayout()
        treebox.addWidget(self.tree)
        state.setLayout(treebox)

        gate = QFrame()
        gate.setFrameShape(QFrame.Panel | QFrame.Sunken)
        gate.setLayout(self.add_gate())
        splitter1 = QSplitter(Qt.Horizontal)
        splitter1.addWidget(state)
        splitter1.addWidget(circuit)
        splitter1.addWidget(measure)
        splitter1.setSizes([150, 550, 150])

        splitter2 = QSplitter(Qt.Vertical)
        splitter2.addWidget(splitter1)
        splitter2.addWidget(gate)
        splitter2.setSizes([1900, 650])

        Circuit_Layout.addWidget(splitter1)

        hbox = QHBoxLayout()
        hbox.addWidget(splitter2)
        centralWidget = QWidget()
        centralWidget.setLayout(hbox)
        self.setCentralWidget(centralWidget)



        self.setWindowTitle('Quself')
        self.setGeometry(300, 100, 1250, 800)
        self.setMinimumSize(1250, 800)
        self.show()

if __name__ == '__main__':
   app = QApplication(sys.argv)
   #app.setPalette(DarkPalette())
   ex = MyApp()
   ex.setStyleSheet(qdarktheme.load_stylesheet())
   sys.exit(app.exec_())