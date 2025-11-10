from tkinter import Tk
from gui import TuringMachineGUI

# Punto de entrada que inicializa y ejecuta la aplicación
def main():
    root = Tk()
    root.title("Turing Machine Simulator")
    app = TuringMachineGUI(root)
    root.mainloop()

if __name__ == "__main__":
    main()