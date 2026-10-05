"""
=============================================================================
TECNOLÓGICO NACIONAL DE MÉXICO - INSTITUTO TECNOLÓGICO SUPERIOR DE URUAPAN
DIVISIÓN DE ESTUDIOS DE POSGRADO E INVESTIGACIÓN
MAESTRÍA EN INTELIGENCIA ARTIFICIAL

Materia: Inteligencia Artificial y su Ética
Actividad 27: Robótica - Simulación de Enjambre de Búsqueda y Rescate con PSO y Red P2P
Alumno: Juan Pablo Figueroa Moran (Matrícula: M26040059)
=============================================================================
"""

import sys
import math
import random
import numpy as np
import matplotlib.pyplot as plt
from typing import List, Dict, Tuple, Optional, Set

if sys.platform == "win32":
    try:
        sys.stdout.reconfigure(encoding="utf-8")
    except Exception:
        pass


class ObjetivoRescate:
    def __init__(self, id_obj: int, x: float, y: float, descripcion: str = "Superviviente"):
        self.id_obj = id_obj
        self.x = x
        self.y = y
        self.descripcion = descripcion
        self.rescatado = False


class RobotExplorador:
    def __init__(self, id_robot: int, x: float, y: float, radio_comm: float = 35.0, radio_sensor: float = 6.0):
        self.id_robot = id_robot
        self.posicion = np.array([x, y], dtype=float)
        self.velocidad = np.random.uniform(-2.0, 2.0, size=2)
        self.radio_comm = radio_comm
        self.radio_sensor = radio_sensor

        # Memoria individual PSO
        self.pbest_pos = np.copy(self.posicion)
        self.pbest_val = -float('inf')

        # Memoria social compartida P2P
        self.gbest_pos = np.copy(self.posicion)
        self.gbest_val = -float('inf')

        self.historial_trayectoria: List[Tuple[float, float]] = [(x, y)]
        self.objetivos_descubiertos: Set[int] = set()


class SimuladorEnjambreP2P:
    """
    Simulador de enjambre descentralizado:
    - 10 robots exploradores cooperando en un área de 100x100 metros.
    - Comunicación P2P limitada por radio de alcance (R_comm).
    - Optimización por Enjambre de Partículas (PSO) para seguir gradientes de señal térmica/acústica.
    """
    def __init__(self, n_robots: int = 10, area_size: float = 100.0, seed: int = 42):
        np.random.seed(seed)
        random.seed(seed)
        self.area_size = area_size
        self.robots: List[RobotExplorador] = []
        self.objetivos: List[ObjetivoRescate] = [
            ObjetivoRescate(1, 85.0, 80.0, "Superviviente A (Señal térmica)"),
            ObjetivoRescate(2, 25.0, 75.0, "Superviviente B (Baliza acústica)"),
            ObjetivoRescate(3, 70.0, 20.0, "Caja de emergencia / Viveres")
        ]

        # Desplegar robots en formación aleatoria en zona de inicio segura
        for i in range(n_robots):
            init_x = np.random.uniform(5.0, 30.0)
            init_y = np.random.uniform(5.0, 30.0)
            self.robots.append(RobotExplorador(i, init_x, init_y, radio_comm=35.0, radio_sensor=7.0))

    def funcion_intensidad_senal(self, x: float, y: float) -> float:
        """
        Campo potencial / intensidad de señal compuesto generado por los supervivientes.
        Los robots no conocen las coordenadas a priori; solo miden la intensidad local.
        """
        intensidad_total = 0.0
        for obj in self.objetivos:
            dist = math.hypot(x - obj.x, y - obj.y)
            # Gaussiana de intensidad de señal térmica/radio
            intensidad_total += 100.0 * math.exp(- (dist**2) / (2 * (18.0**2)))
        return intensidad_total

    def paso_comunicacion_p2p(self):
        """
        Intercambio P2P ad-hoc descentralizado:
        Si dos robots están dentro de su radio de comunicación (R_comm),
        comparten información sobre su mejor hallazgo individual (pbest) y objetivos detectados.
        """
        n = len(self.robots)
        for i in range(n):
            for j in range(i + 1, n):
                r1 = self.robots[i]
                r2 = self.robots[j]
                dist_p2p = np.linalg.norm(r1.posicion - r2.posicion)

                if dist_p2p <= r1.radio_comm:
                    # Enlace de comunicación activo
                    if r1.pbest_val > r2.gbest_val:
                        r2.gbest_val = r1.pbest_val
                        r2.gbest_pos = np.copy(r1.pbest_pos)
                    if r2.pbest_val > r1.gbest_val:
                        r1.gbest_val = r2.pbest_val
                        r1.gbest_pos = np.copy(r2.pbest_pos)

                    # Compartir lista de víctimas localizadas
                    r1.objetivos_descubiertos.update(r2.objetivos_descubiertos)
                    r2.objetivos_descubiertos.update(r1.objetivos_descubiertos)

    def ejecutar_simulacion(self, pasos: int = 40):
        print(f"[*] Desplegando enjambre de {len(self.robots)} robots en cuadrante de {self.area_size}x{self.area_size}m...")
        print(f"[*] Objetivos activos a localizar: {len(self.objetivos)}")

        # Parámetros PSO
        w = 0.65       # Inercia
        c1 = 1.4       # Factor cognitivo (memoria personal)
        c2 = 1.6       # Factor social (conocimiento del enjambre P2P)

        for t in range(pasos):
            # 1. Medición Sensorial y Actualización de pbest
            for robot in self.robots:
                x, y = robot.posicion
                senal_local = self.funcion_intensidad_senal(x, y)

                if senal_local > robot.pbest_val:
                    robot.pbest_val = senal_local
                    robot.pbest_pos = np.copy(robot.posicion)

                if senal_local > robot.gbest_val:
                    robot.gbest_val = senal_local
                    robot.gbest_pos = np.copy(robot.posicion)

                # Verificar si alcanzó el radio de contacto físico de un objetivo
                for obj in self.objetivos:
                    dist_obj = math.hypot(x - obj.x, y - obj.y)
                    if dist_obj <= robot.radio_sensor and not obj.rescatado:
                        obj.rescatado = True
                        robot.objetivos_descubiertos.add(obj.id_obj)
                        print(f"  [🚩 HALLAZGO en T={t}] Robot #{robot.id_robot} localizó: '{obj.descripcion}' en ({obj.x:.1f}, {obj.y:.1f})")

            # 2. Intercambio de Información en Red P2P
            self.paso_comunicacion_p2p()

            # 3. Dinámica de Movimiento PSO
            for robot in self.robots:
                r1 = np.random.rand(2)
                r2 = np.random.rand(2)

                # Ecuación canónica de velocidad PSO
                v_cognitiva = c1 * r1 * (robot.pbest_pos - robot.posicion)
                v_social = c2 * r2 * (robot.gbest_pos - robot.posicion)
                robot.velocidad = w * robot.velocidad + v_cognitiva + v_social

                # Limitar velocidad máxima para realismo físico del robot
                v_norm = np.linalg.norm(robot.velocidad)
                if v_norm > 4.5:
                    robot.velocidad = (robot.velocidad / v_norm) * 4.5

                # Actualización de coordenadas con rebote en fronteras del mapa
                robot.posicion += robot.velocidad
                for d in range(2):
                    if robot.posicion[d] < 0:
                        robot.posicion[d] = 0.0
                        robot.velocidad[d] *= -0.5
                    elif robot.posicion[d] > self.area_size:
                        robot.posicion[d] = self.area_size
                        robot.velocidad[d] *= -0.5

                robot.historial_trayectoria.append((robot.posicion[0], robot.posicion[1]))

        self.generar_reporte_y_grafica()

    def generar_reporte_y_grafica(self, output_path="simulacion_enjambre_rescate.png"):
        print("\n" + "=" * 70)
        print("  REPORTE FINAL DE LA MISIÓN DE BÚSQUEDA Y RESCATE")
        print("=" * 70)
        rescatados = sum(1 for o in self.objetivos if o.rescatado)
        print(f"  * Eficacia de Búsqueda: {rescatados}/{len(self.objetivos)} supervivientes alcanzados ({rescatados/len(self.objetivos)*100:.1f}%)")
        for obj in self.objetivos:
            estado = "RESCATADO ✅" if obj.rescatado else "PENDIENTE ⏳"
            print(f"    - Objetivo {obj.id_obj} [{obj.descripcion}]: {estado}")

        plt.figure(figsize=(9, 8))
        # Graficar trayectorias de los robots
        for robot in self.robots:
            tray = np.array(robot.historial_trayectoria)
            plt.plot(tray[:, 0], tray[:, 1], alpha=0.45, linewidth=1.5)
            plt.scatter(robot.posicion[0], robot.posicion[1], marker='o', s=60, label=f"Robot {robot.id_robot}" if robot.id_robot < 3 else "")

        # Graficar supervivientes / objetivos
        for obj in self.objetivos:
            color = 'green' if obj.rescatado else 'red'
            plt.scatter(obj.x, obj.y, marker='*', s=250, color=color, edgecolors='black', zorder=5)
            plt.text(obj.x + 2, obj.y + 2, f"{obj.descripcion}", fontsize=9, weight='bold')

        plt.title("Simulador de Enjambre de Robots (PSO + Red P2P Descentralizada)", fontsize=13)
        plt.xlabel("Coordenada X (metros)")
        plt.ylabel("Coordenada Y (metros)")
        plt.xlim(0, self.area_size)
        plt.ylim(0, self.area_size)
        plt.grid(True, linestyle="--", alpha=0.5)
        plt.tight_layout()
        plt.savefig(output_path, dpi=200)
        plt.close()
        print(f"[+] Mapa final de trayectorias guardado como: '{output_path}'")

        print("\n" + "=" * 75)
        print("  CONSIDERACIONES ÉTICAS EN ENJAMBRES DE ROBOTS AUTÓNOMOS")
        print("=" * 75)
        print("""
    1. Robótica de Rescate Humanitario vs Armas Autónomas Letales (LAWS):
       Los algoritmos de coordinación de enjambres (PSO, boids, feromonas) son
       tecnologías de doble uso. Su aplicación ética debe orientarse a la preservación
       de vidas en catástrofes naturales y no a operaciones ofensivas sin supervisión humana.
    2. Resiliencia ante Fallos: El modelo descentralizado P2P garantiza que la pérdida
       de uno o varios robots no comprometa la misión de rescate ni desampare a las víctimas.
    3. Control Humano Significativo (Meaningful Human Control): Toda decisión crítica
       de intervención médica o logística debe permanecer bajo validación de operadores humanos.
    """)


def main():
    print("=" * 75)
    print("  TECNM / ITSU - SIMULADOR DE ENJAMBRE DE ROBOTS (PSO + P2P)")
    print("=" * 75)

    sim = SimuladorEnjambreP2P(n_robots=10, area_size=100.0, seed=42)
    sim.ejecutar_simulacion(pasos=45)


if __name__ == "__main__":
    main()
