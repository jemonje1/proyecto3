# Turing Machine Simulator

Simulador visual de Máquina de Turing para validar expresiones regulares mediante una interfaz gráfica interactiva.

## Descripción

Este proyecto implementa un simulador de Máquina de Turing que permite visualizar paso a paso el proceso de validación de cadenas contra expresiones regulares predefinidas. La interfaz gráfica muestra la cinta, el cabezal y el estado actual de la máquina en tiempo real.

## Características principales

- Visualización gráfica de la cinta y movimiento del cabezal
- Ejecución paso a paso o automática
- Soporte para 5 expresiones regulares predefinidas
- Carga de cadenas desde archivos de texto
- Log detallado de cada transición
- Indicador visual del resultado final

## Expresiones regulares soportadas

- `(a|b)*abb` - Cadenas que terminan en "abb"
- `0*1*` - Ceros seguidos de unos
- `(ab)*` - Repeticiones de "ab"
- `1(01)*0` - Comienza con 1, termina con 0, con pares 01 en medio
- `(a+b)*a(a+b)*` - Cadenas que contienen al menos una "a"

## Requisitos

```
tkinter
numpy
regex
Pillow
```

## Instalación

Instalar las dependencias necesarias:

```bash
pip install numpy regex Pillow
```

Nota: Tkinter generalmente viene preinstalado con Python. Si no está disponible, instalarlo según el sistema operativo.

## Uso

Ejecutar el programa principal:

```bash
python main.py
```

### Pasos para usar el simulador

1. Seleccionar una expresión regular del menú desplegable
2. Ingresar la cadena a validar manualmente o cargar desde un archivo .txt
3. Hacer clic en "Validar (iniciar)" para inicializar la máquina
4. Usar los botones de control:
   - Paso: Ejecuta una transición individual
   - Run: Ejecuta automáticamente hasta completar
   - Reset: Reinicia la máquina

## Estructura del proyecto

- `main.py` - Punto de entrada de la aplicación
- `turing_machine.py` - Lógica de la Máquina de Turing
- `gui.py` - Interfaz gráfica con Tkinter

## Funcionamiento técnico

La máquina de Turing lee símbolos de la cinta, aplica transiciones según el estado actual y el símbolo leído, escribe nuevos símbolos y mueve el cabezal hacia la izquierda o derecha. La cinta se extiende automáticamente cuando es necesario.

Cada expresión regular tiene su propio conjunto de estados y transiciones predefinidas. La máquina acepta la cadena si termina en un estado de aceptación, de lo contrario la rechaza.