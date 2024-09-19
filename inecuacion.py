import numpy as np
import matplotlib.pyplot as plt

def graficar_inecuaciones(inecuaciones):
    x = np.linspace(-10, 10, 400)  # Rango para la variable x
    plt.figure()

    for inecuacion in inecuaciones:
        coeficientes, signo = inecuacion
        a, b, c = coeficientes  # ax + by <= c
        y = (c - a * x) / b  # Despejamos y

        if signo == '<=':
            plt.fill_between(x, y, y.min(), where=(y >= y.min()), alpha=0.3)
        elif signo == '>=':
            plt.fill_between(x, y, y.max(), where=(y <= y.max()), alpha=0.3)

        plt.plot(x, y, label=f'{a}x + {b}y {signo} {c}')

    plt.xlim([-10, 10])
    plt.ylim([-10, 10])
    plt.axhline(0, color='black',linewidth=1)
    plt.axvline(0, color='black',linewidth=1)
    plt.grid(True)
    plt.legend()
    plt.show()

def solicitar_inecuaciones():
    inecuaciones = []
    for i in range(2):
        print(f"Inecuación {i+1}:")
        a = float(input("Coeficiente de x: "))
        b = float(input("Coeficiente de y: "))
        c = float(input("Término independiente: "))
        signo = input("Ingrese el signo de la inecuación (<= o >=): ")
        inecuaciones.append(((a, b, c), signo))
    return inecuaciones

# Solicitar las inecuaciones y graficar
inecuaciones = solicitar_inecuaciones()
graficar_inecuaciones(inecuaciones)
