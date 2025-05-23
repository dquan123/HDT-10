# hoja_trabajo10.py

import math
from typing import List, Dict, Tuple, Optional

class Grafo:
    """
    Clase para representar un grafo dirigido con tiempos según condiciones climáticas.
    """

    def __init__(self):
        # Lista de nombres de ciudades
        self.ciudades: List[str] = []
        # Mapeo de ciudad a índice interno
        self.indice: Dict[str, int] = {}
        # Pesos de arcos: clave (i,j) -> tiempos {'normal':..., 'lluvia':..., 'nieve':..., 'tormenta':...}
        self.pesos: Dict[Tuple[int, int], Dict[str, int]] = {}
        # Número de ciudades
        self.n: int = 0

    def _asegurar_ciudad(self, ciudad: str) -> None:
        """Añade una ciudad si no existía previamente."""
        if ciudad not in self.indice:
            self.indice[ciudad] = self.n
            self.ciudades.append(ciudad)
            self.n += 1

    def cargar_desde_archivo(self, ruta_archivo: str) -> None:
        """
        Lee un archivo de texto donde cada línea contiene:
        Ciudad1 Ciudad2 tiempoNormal tiempoLluvia tiempoNieve tiempoTormenta
        Construye el grafo a partir de esos datos.
        """
        with open(ruta_archivo, encoding='utf-8') as f:
            for linea in f:
                partes = linea.strip().split()
                if len(partes) != 6:
                    continue
                c1, c2, tN, tL, tNv, tT = partes
                self._asegurar_ciudad(c1)
                self._asegurar_ciudad(c2)
                i, j = self.indice[c1], self.indice[c2]
                self.pesos[(i, j)] = {
                    'normal': int(tN),
                    'lluvia': int(tL),
                    'nieve': int(tNv),
                    'tormenta': int(tT)
                }

    def floyd(self, clima: str = 'normal') -> Tuple[List[List[float]], List[List[Optional[int]]]]:
        """
        Implementa el algoritmo de Floyd–Warshall para el clima indicado.
        Devuelve:
          - dist: matriz de distancias mínimas entre pares de ciudades.
          - siguiente: matriz para reconstruir rutas.
        """
        # Inicialización de matrices
        dist = [[math.inf] * self.n for _ in range(self.n)]
        siguiente: List[List[Optional[int]]] = [[None] * self.n for _ in range(self.n)]
        for i in range(self.n):
            dist[i][i] = 0
            siguiente[i][i] = i
        # Cargar costos según pesos
        for (i, j), tiempos in self.pesos.items():
            tiempo = tiempos.get(clima, math.inf)
            dist[i][j] = tiempo
            siguiente[i][j] = j
        # Recorrido principal de Floyd
        for k in range(self.n):
            for i in range(self.n):
                for j in range(self.n):
                    if dist[i][k] + dist[k][j] < dist[i][j]:
                        dist[i][j] = dist[i][k] + dist[k][j]
                        siguiente[i][j] = siguiente[i][k]
        return dist, siguiente

    def obtener_centro(self, dist: List[List[float]]) -> str:
        """
        Calcula la ciudad que minimiza la excentricidad (max distancia a otras).
        """
        excentricidades: List[float] = []
        for i in range(self.n):
            max_dist = max(dist[i][j] for j in range(self.n) if dist[i][j] < math.inf)
            excentricidades.append(max_dist)
        idx_centro = min(range(self.n), key=lambda x: excentricidades[x])
        return self.ciudades[idx_centro]

    def obtener_ruta(self, origen: str, destino: str, siguiente: List[List[Optional[int]]]) -> List[str]:
        """
        Reconstruye la ruta más corta de 'origen' a 'destino' usando la matriz 'siguiente'.
        """
        if origen not in self.indice or destino not in self.indice:
            return []
        i, j = self.indice[origen], self.indice[destino]
        if siguiente[i][j] is None:
            return []
        ruta_indices = [i]
        while i != j:
            i = siguiente[i][j]  # type: ignore
            ruta_indices.append(i)
        return [self.ciudades[idx] for idx in ruta_indices]

    def eliminar_arco(self, c1: str, c2: str) -> None:
        """Elimina la conexión dirigida de c1 a c2."""
        if c1 in self.indice and c2 in self.indice:
            i, j = self.indice[c1], self.indice[c2]
            self.pesos.pop((i, j), None)

    def agregar_arco(self, c1: str, c2: str, tiempos: Dict[str, int]) -> None:
        """Agrega o actualiza la conexión de c1 a c2 con los tiempos proporcionados."""
        self._asegurar_ciudad(c1)
        self._asegurar_ciudad(c2)
        i, j = self.indice[c1], self.indice[c2]
        self.pesos[(i, j)] = tiempos

    def establecer_clima(self, c1: str, c2: str, clima: str, tiempo: int) -> None:
        """Actualiza el tiempo para un clima específico en el arco c1->c2."""
        if c1 in self.indice and c2 in self.indice:
            i, j = self.indice[c1], self.indice[c2]
            if (i, j) in self.pesos:
                self.pesos[(i, j)][clima] = tiempo


def main():
    grafo = Grafo()
    try:
        grafo.cargar_desde_archivo('logistica.txt')
    except FileNotFoundError:
        print("Error: no se encontró 'logistica.txt'. Verifica su existencia.")
        return

    clima_actual = 'normal'
    dist, siguiente = grafo.floyd(clima_actual)

    while True:
        print("\nOpciones:")
        print("1) Ruta más corta entre dos ciudades")
        print("2) Mostrar ciudad centro del grafo")
        print("3) Modificar grafo")
        print("4) Salir")
        opcion = input("Selecciona opción: ").strip()

        if opcion == '1':
            origen = input("Ciudad origen: ")
            destino = input("Ciudad destino: ")
            ruta = grafo.obtener_ruta(origen, destino, siguiente)
            if not ruta:
                print("No existe ruta entre esas ciudades.")
            else:
                i, j = grafo.indice[origen], grafo.indice[destino]
                print(f"Ruta: {' -> '.join(ruta)} | Costo ({clima_actual}): {dist[i][j]}")

        elif opcion == '2':
            centro = grafo.obtener_centro(dist)
            print(f"La ciudad centro es: {centro}")

        elif opcion == '3':
            print("a) Eliminar conexión")
            print("b) Agregar conexión")
            print("c) Cambiar tiempo por clima en conexión")
            accion = input("Elige acción: ").strip().lower()
            if accion == 'a':
                c1 = input("Ciudad1: ")
                c2 = input("Ciudad2: ")
                grafo.eliminar_arco(c1, c2)
            elif accion == 'b':
                c1 = input("Ciudad1: ")
                c2 = input("Ciudad2: ")
                tn = int(input("Tiempo normal: "))
                tl = int(input("Tiempo lluvia: "))
                tnV = int(input("Tiempo nieve: "))
                tt = int(input("Tiempo tormenta: "))
                grafo.agregar_arco(c1, c2, {'normal': tn, 'lluvia': tl, 'nieve': tnV, 'tormenta': tt})
            elif accion == 'c':
                c1 = input("Ciudad1: ")
                c2 = input("Ciudad2: ")
                cl = input("Clima (normal/lluvia/nieve/tormenta): ")
                t = int(input("Nuevo tiempo: "))
                grafo.establecer_clima(c1, c2, cl, t)
            else:
                print("Acción inválida.")
                continue
            dist, siguiente = grafo.floyd(clima_actual)
            print("Grafo actualizado y rutas recalculadas.")

        elif opcion == '4':
            print("Programa finalizado.")
            break
        else:
            print("Opción inválida, intenta de nuevo.")

if __name__ == '__main__':
    main()
