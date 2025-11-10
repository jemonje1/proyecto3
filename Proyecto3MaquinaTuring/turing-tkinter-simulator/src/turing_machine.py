from copy import deepcopy

class TuringMachine:
    # Inicializa la máquina de Turing con sus componentes básicos
    def __init__(self, transitions, start_state, accept_states, tape=None, blank="_"):
        self.transitions = transitions
        self.state = start_state
        self.accept_states = set(accept_states)
        self.blank = blank
        self.tape = list(tape) if tape is not None else [blank]
        self.head = 0
        self.halted = False
        self.accepted = False
        self.step_count = 0
        self.left_extension = 0

    # Crea una máquina vacía con configuración por defecto
    @classmethod
    def empty(cls):
        return cls({}, "q0", set(), tape=["_"])
    
    # Genera una máquina de Turing configurada para validar expresiones regulares predefinidas
    @classmethod
    def from_preset(cls, name, input_string):
        s = list(input_string) if input_string != "" else []
        trans = {}

        if name == "0*1*":
            q0, q1, qf, qd = "q0", "q1", "qf", "qdead"
            trans.update({
                ("q0","0"): (q0,"X","R"),
                ("q0","1"): (q1,"Y","R"),
                ("q1","1"): (q1,"Y","R"),
                ("q1","_"): (qf,"_","L"),
                ("q1","0"): (qd,"0","R"),
                ("qf","X"): (qf,"X","L"),
                ("qf","Y"): (qf,"Y","L"),
            })
            start="q0"; accept={"q0","qf"}

        elif name == "(ab)*":
            q0, q1, qf, qd = "q0","q1","qf","qdead"
            trans.update({
                ("q0","a"): (q1,"X","R"),
                ("q1","b"): (q0,"Y","R"),
                ("q1","_"): (qd,"_","R"),
                ("q1","a"): (qd,"a","R"),
                ("q0","b"): (qd,"b","R"),
                ("q0","_"): None
            })
            trans = {k:v for k,v in trans.items() if v is not None}
            start="q0"; accept={"q0","qf"}

        elif name == "1(01)*0":
            q0, q1, q2, qf, qd = "q0","q1","q2","qf","qdead"
            trans.update({
                ("q0","1"): (q1,"X","R"),
                ("q0","0"): (qd,"0","R"),
                ("q0","_"): (qd,"_","R"),
                ("q1","0"): (q2,"P","R"),
                ("q1","1"): (qd,"1","R"),
                ("q2","1"): (q1,"Q","R"),
                ("q2","0"): (qd,"0","R"),
                ("q2","_"): (qf,"_","R"),
            })
            start="q0"; accept={qf}

        elif name == "(a+b)*a(a+b)*":
            q0, qf, qd = "q0","qf","qdead"
            trans.update({
                ("q0","a"): (qf,"A","R"),
                ("q0","b"): (q0,"B","R"),
                ("q0","_"): (qd,"_","R"),
                ("qf","a"): (qf,"A","R"),
                ("qf","b"): (qf,"B","R"),
            })
            start="q0"; accept={qf}

        elif name == "(a|b)*abb":
            q0, q1, q2, q3, qf, qd = "q0","q1","q2","q3","qf","qdead"
            trans.update({
                ("q0","a"): (q0,"a","R"),
                ("q0","b"): (q0,"b","R"),
                ("q0","_"): (q1,"_","L"),
                ("q1","b"): (q2,"B","L"),
                ("q1","B"): (q2,"B","L"),
                ("q1","a"): (qd,"a","R"),
                ("q1","A"): (qd,"A","R"),
                ("q1","_"): (qd,"_","R"),
                ("q2","b"): (q3,"B","L"),
                ("q2","B"): (q3,"B","L"),
                ("q2","a"): (qd,"a","R"),
                ("q2","A"): (qd,"A","R"),
                ("q2","_"): (qd,"_","R"),
                ("q3","a"): (qf,"A","R"),
                ("q3","A"): (qf,"A","R"),
                ("q3","b"): (qd,"b","R"),
                ("q3","B"): (qd,"B","R"),
                ("q3","_"): (qd,"_","R"),
            })
            start="q0"; accept={qf}

        else:
            start="q0"; accept={"q0"}

        return cls(
            transitions=trans,
            start_state=start,
            accept_states=accept,
            tape=(s + ["_"])
        )

    # Lee el símbolo actual de la cinta y extiende la cinta si es necesario
    def _read_symbol(self):
        if self.head < 0:
            self.tape.insert(0, self.blank)
            self.head = 0
            self.left_extension += 1
            return self.blank
        if self.head >= len(self.tape):
            self.tape.append(self.blank)
            return self.blank
        return self.tape[self.head]

    # Ejecuta un paso de la máquina aplicando la transición correspondiente
    def step(self):
        if self.halted:
            return {"halted": True, "accepted": self.accepted, "pos": self.head}
            
        r = self._read_symbol()
        key = (self.state, r)
        old_pos = self.head
        
        if key not in self.transitions:
            self.halted = True
            self.accepted = (self.state in self.accept_states)
            return {
                "read": r,
                "wrote": r,
                "move": "N",
                "new_state": self.state,
                "halted": True,
                "accepted": self.accepted,
                "pos": self.head
            }

        new_state, write, move = self.transitions[key]
        
        self.tape[self.head] = write
        
        if move == "R":
            self.head += 1
            if self.head >= len(self.tape):
                self.tape.append(self.blank)
        elif move == "L":
            self.head -= 1
            if self.head < 0:
                self.tape.insert(0, self.blank)
                self.head = 0
                self.left_extension += 1

        self.state = new_state
        self.step_count += 1

        return {
            "read": r,
            "wrote": write,
            "move": move,
            "new_state": self.state,
            "halted": False,
            "accepted": False,
            "pos": old_pos,
            "new_pos": self.head
        }