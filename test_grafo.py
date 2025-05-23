import os
import math
import pytest
from hoja_trabajo10 import Grafo


def test_cargar_desde_archivo(tmp_path):
    # Crear archivo de prueba
    contenido = """
A B 5 6 7 8
B C 3 4 5 6
A C 10 11 12 13
"""
    archivo = tmp_path / "C:\\Users\\dquan\\OneDrive\\Documentos\\Diego Quan\\UVG\\Ciclo 3\\Algoritmos y Estructura de datos\\Hoja de trabajo 10\\HDT-10\\logistica.txt"
    archivo.write_text(contenido)

    grafo = Grafo()
    grafo.cargar_desde_archivo(str(archivo))

    # Debe haber 3 ciudades
    assert grafo.n == 3
    # Mapear nombres a índices
    assert set(grafo.ciudades) == {"A", "B", "C"}
    # Pesos correctos para arco A->B
    i, j = grafo.indice["A"], grafo.indice["B"]
    assert grafo.pesos[(i, j)]["normal"] == 5
    assert grafo.pesos[(i, j)]["tormenta"] == 8


def test_floyd_and_obtener_ruta():
    grafo = Grafo()
    # Grafo simple: A->B (1), B->C (2), A->C (10)
    grafo._asegurar_ciudad("A")
    grafo._asegurar_ciudad("B")
    grafo._asegurar_ciudad("C")
    grafo.pesos[(0, 1)] = {"normal": 1, "lluvia": 1, "nieve": 1, "tormenta": 1}
    grafo.pesos[(1, 2)] = {"normal": 2, "lluvia": 2, "nieve": 2, "tormenta": 2}
    grafo.pesos[(0, 2)] = {"normal": 10, "lluvia": 10, "nieve": 10, "tormenta": 10}

    dist, sig = grafo.floyd("normal")
    # Distancia óptima de A a C debe ser 1+2=3, no 10
    assert dist[0][2] == 3
    # Ruta reconstruida A->C debe ser ['A','B','C']
    ruta = grafo.obtener_ruta("A", "C", sig)
    assert ruta == ["A", "B", "C"]


def test_obtener_centro():
    grafo = Grafo()
    # Grafo en estrella: X conectado a A,B,C con peso 1.
    ciudades = ["X", "A", "B", "C"]
    for c in ciudades:
        grafo._asegurar_ciudad(c)
    for c in ["A", "B", "C"]:
        grafo.pesos[(0, grafo.indice[c])] = {"normal": 1, "lluvia":1, "nieve":1, "tormenta":1}
        grafo.pesos[(grafo.indice[c], 0)] = {"normal": 1, "lluvia":1, "nieve":1, "tormenta":1}

    dist, sig = grafo.floyd("normal")
    centro = grafo.obtener_centro(dist)
    # En este grafo, X es el centro (menor excentricidad)
    assert centro == "X"


def test_eliminar_agregar_arco():
    grafo = Grafo()
    grafo._asegurar_ciudad("U")
    grafo._asegurar_ciudad("V")
    grafo.pesos[(0,1)] = {"normal": 5, "lluvia":5, "nieve":5, "tormenta":5}

    # Eliminar arco U->V
    grafo.eliminar_arco("U", "V")
    assert (0,1) not in grafo.pesos

    # Agregar arco nuevo
    tiempos = {"normal":2, "lluvia":3, "nieve":4, "tormenta":5}
    grafo.agregar_arco("U", "V", tiempos)
    assert grafo.pesos[(0,1)]["normal"] == 2


def test_establecer_clima():
    grafo = Grafo()
    grafo._asegurar_ciudad("M")
    grafo._asegurar_ciudad("N")
    grafo.pesos[(0,1)] = {"normal": 7, "lluvia":8, "nieve":9, "tormenta":10}

    # Cambiar tiempo para 'nieve'
    grafo.establecer_clima("M", "N", "nieve", 15)
    assert grafo.pesos[(0,1)]["nieve"] == 15
