import tkinter as tk
from tkinter import filedialog, font
from turing_machine import TuringMachine

class TuringMachineGUI:
    # Inicializa la interfaz gráfica con todos sus componentes y controles
    def __init__(self, root):
        self.root = root
        self.root.geometry("1000x560")
        self.root.configure(bg="#e8f7fb")
        self.title_font = font.Font(family="Helvetica", size=14, weight="bold")
        self.regular_font = font.Font(family="Helvetica", size=12)

        ctrl = tk.Frame(root, bg="#e8f7fb", padx=10, pady=10)
        ctrl.pack(side=tk.LEFT, fill=tk.Y)

        tk.Label(ctrl, text="Selecciona expresión regular:", bg="#e8f7fb", font=self.title_font).pack(anchor="w")
        self.presets = [
            "(a|b)*abb",
            "0*1*",
            "(ab)*",
            "1(01)*0",
            "(a+b)*a(a+b)*"
        ]
        self.sel = tk.StringVar(value=self.presets[0])
        tk.OptionMenu(ctrl, self.sel, *self.presets).pack(fill="x", pady=6)

        tk.Label(ctrl, text="Cadena a validar:", bg="#e8f7fb", font=self.title_font).pack(anchor="w", pady=(12,0))
        self.input_entry = tk.Entry(ctrl, font=self.regular_font)
        self.input_entry.pack(fill="x", pady=6)

        tk.Button(ctrl, text="Cargar archivo (.txt)", command=self.load_file, bg="#9adcf0").pack(fill="x", pady=4)
        tk.Button(ctrl, text="Validar (iniciar)", command=self.start_machine, bg="#6fcfe0").pack(fill="x", pady=4)

        nav = tk.Frame(ctrl, bg="#e8f7fb")
        nav.pack(fill="x", pady=(12,0))
        tk.Button(nav, text="Paso", command=self.step, bg="#bfeef9").grid(row=0, column=0, padx=4)
        tk.Button(nav, text="Run", command=self.run_toggle, bg="#8fe6f4").grid(row=0, column=1, padx=4)
        tk.Button(nav, text="Reset", command=self.reset, bg="#bff0f7").grid(row=0, column=2, padx=4)

        self.status_label = tk.Label(ctrl, text="Estado: -", bg="#e8f7fb", font=self.regular_font)
        self.status_label.pack(anchor="w", pady=(12,0))

        vis = tk.Frame(root, bg="#ffffff", padx=10, pady=10)
        vis.pack(side=tk.LEFT, fill=tk.BOTH, expand=True)

        canvas_frame = tk.Frame(vis)
        canvas_frame.pack(fill="x", pady=(0,10))

        self.canvas = tk.Canvas(canvas_frame, bg="#f7feff", height=140)
        scrollbar = tk.Scrollbar(canvas_frame, orient="horizontal", command=self.canvas.xview)
        self.canvas.configure(xscrollcommand=scrollbar.set)

        scrollbar.pack(side="bottom", fill="x")
        self.canvas.pack(side="top", fill="x")

        self.log = tk.Listbox(vis, height=14, font=("Consolas", 11))
        self.log.pack(fill="both", expand=True)

        self.machine = None
        self.auto_running = False
        self.auto_delay = 450 
        self.head_visual = None
        self.cells = []
        self.cell_rects = []
        self.reset()

    # Dibuja la cinta de la máquina mostrando las celdas y sus posiciones
    def draw_tape(self):
        self.canvas.delete("all")
        self.cell_rects.clear()
        self.cells = list(self.machine.tape) if self.machine else []
        cell_w = 50
        y0, y1 = 10, 80
        total_width = (len(self.cells) * (cell_w + 6)) + 20

        self.canvas.configure(scrollregion=(0, 0, total_width, y1 + 30))

        for i in range(len(self.cells)):
            x0 = 10 + i * (cell_w + 6)
            pos_num = i - self.machine.left_extension if self.machine else i
            self.canvas.create_text(x0 + cell_w/2, y0 - 10, 
                                  text=str(pos_num), 
                                  font=("Helvetica", 8))
            
            rect = self.canvas.create_rectangle(x0, y0, x0 + cell_w, y1, 
                                             fill="#ffffff", 
                                             outline="#7fc7de")
            txt = self.canvas.create_text(x0 + cell_w/2, (y0+y1)/2, 
                                        text=self.cells[i], 
                                        font=self.regular_font, 
                                        fill="#024f6e")
            self.cell_rects.append((rect, txt))

        if self.machine and self.machine.head < len(self.cell_rects):
            self.canvas.xview_moveto(
                (self.machine.head * (cell_w + 6)) / total_width - 0.3
            )
        
        self.draw_head()

    # Dibuja el indicador visual del cabezal en la posición actual
    def draw_head(self):
        if not self.machine:
            return
        head = self.machine.head
        if head < 0:
            head = 0
        if head >= len(self.cell_rects):
            self.canvas.after(1, self._extend_visual_tape)
            return
        rect, txt = self.cell_rects[head]
        coords = self.canvas.coords(rect)
        x0, y0, x1, y1 = coords
        midx = (x0 + x1) / 2
        arrow_y = y1 + 16
        if self.head_visual:
            self.canvas.delete(self.head_visual)
        self.head_visual = self.canvas.create_polygon(midx-8, arrow_y, midx+8, arrow_y, midx, arrow_y-12, fill="#007ea7")

    # Redibuja la cinta cuando se necesita extender visualmente
    def _extend_visual_tape(self):
        self.draw_tape()

    # Actualiza la etiqueta de estado mostrando el estado actual y número de pasos
    def update_status(self):
        if not self.machine:
            self.status_label.config(text="Estado: -")
            return
        s = f"Estado: {self.machine.state}   Paso: {self.machine.step_count}"
        self.status_label.config(text=s)

    # Ejecuta un paso de la máquina y actualiza la visualización
    def step(self):
        if not self.machine:
            self.log.insert(tk.END, "Carga una máquina primero.")
            return
        info = self.machine.step()
        r = info.get("read")
        w = info.get("wrote")
        mv = info.get("move")
        ns = info.get("new_state")
        pos = info.get("pos")
        self.log.insert(tk.END, f"Pos {pos}: read '{r}' -> wrote '{w}', move {mv}, state {ns}")
        if 0 <= pos < len(self.cell_rects):
            _, txtid = self.cell_rects[pos]
            self.canvas.itemconfig(txtid, text=self.machine.tape[pos])
        else:
            self.draw_tape()
        self.draw_head()
        self.update_status()
        if info.get("halted"):
            if info.get("accepted"):
                self.log.insert(tk.END, "Resultado: ACEPTADA")
            else:
                self.log.insert(tk.END, "Resultado: RECHAZADA")
            self.auto_running = False

    # Activa o desactiva la ejecución automática de pasos
    def run_toggle(self):
        if not self.machine:
            self.log.insert(tk.END, "Carga una máquina primero.")
            return
        self.auto_running = not self.auto_running
        if self.auto_running:
            self._auto_step()

    # Ejecuta pasos automáticamente con intervalos de tiempo
    def _auto_step(self):
        if not self.auto_running:
            return
        if self.machine and not self.machine.halted:
            self.step()
            self.root.after(self.auto_delay, self._auto_step)
        else:
            self.auto_running = False

    # Reinicia la máquina a su estado inicial vacío
    def reset(self):
        self.machine = TuringMachine.empty()
        self.draw_tape()
        self.log.insert(tk.END, "Reset completo.")
        self.update_status()
    
    # Abre un archivo de texto y carga su contenido en el campo de entrada
    def load_file(self):
        filename = filedialog.askopenfilename(
            filetypes=[("Text files", "*.txt")]
        )
        if filename:
            try:
                with open(filename, 'r') as file:
                    content = file.read().strip()
                self.input_entry.delete(0, tk.END)
                self.input_entry.insert(0, content)
                self.log.insert(tk.END, f"Archivo cargado: {filename}")
            except Exception as e:
                self.log.insert(tk.END, f"Error al cargar archivo: {str(e)}")

    # Inicia la máquina con la expresión regular y cadena de entrada seleccionadas
    def start_machine(self):
        preset = self.sel.get()
        input_string = self.input_entry.get().strip()
        
        self.log.delete(0, tk.END)
        self.log.insert(tk.END, f"Iniciando máquina para '{preset}'")
        self.log.insert(tk.END, f"Entrada: '{input_string}'")
        
        self.machine = TuringMachine.from_preset(preset, input_string)
        self.auto_running = False
        self.draw_tape()
        self.update_status()