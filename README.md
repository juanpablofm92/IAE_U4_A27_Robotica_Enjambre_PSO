# Actividad 27: Simulación de Enjambre de Búsqueda y Rescate con PSO y Red P2P

**Tecnológico Nacional de México**  
**Instituto Tecnológico Superior de Uruapan**  
**División de Estudios de Posgrado e Investigación**  
**Maestría en Inteligencia Artificial**  

* **Asignatura:** Inteligencia Artificial y su Ética  
* **Alumno:** Juan Pablo Figueroa Moran  
* **Matrícula:** M26040059  

---

## 📌 1. Descripción del Proyecto

Este proyecto implementa un simulador en Python de un **enjambre cooperativo descentralizado compuesto por 10 robots exploradores** destinados a misiones de búsqueda y rescate en escenarios de desastre.

### Principios del Sistema:
1. **Red P2P Ad-Hoc Descentralizada:** No existe un nodo coordinador central. Los robots intercambian información únicamente cuando se sitúan dentro de su radio de transmisión inalámbrica ($R_{comm} = 35.0$ metros).
2. **Optimización por Enjambre de Partículas (PSO Espacial):** La navegación hacia las fuentes de señal térmica o acústica emitidas por supervivientes combina tres fuerzas dinámicas:
$$v_i(t+1) = w \cdot v_i(t) + c_1 r_1 (p_{best, i} - x_i(t)) + c_2 r_2 (g_{best, i} - x_i(t))$$
   - Inercia ($w = 0.65$)
   - Componente cognitivo ($c_1 = 1.4$)
   - Componente social vecinal P2P ($c_2 = 1.6$)
3. **Mapeo y Visualización de Trayectorias:** Exportación de `simulacion_enjambre_rescate.png` que ilustra las trayectorias convergentes y los objetivos asegurados.

---

## 🚀 2. Instalación y Ejecución

```bash
pip install -r requirements.txt
python swarm_simulation.py
```

---

## ⚖️ 3. Consideraciones Éticas en Enjambres Autónomos

1. **Doble Uso Tecnológico:** La robótica de enjambre debe estar estrictamente regulada para prevenir su militarización como sistemas de armas autónomas letales (*Lethal Autonomous Weapons Systems - LAWS*).
2. **Misiones Humanitarias de Alta Prioridad:** El valor de la robótica colectiva reside en salvar vidas humanas en incendios, terremotos y rescates marítimos sin exponer al personal de auxilio.
3. **Control Humano Significativo:** La confirmación del rescate y la priorización médica debe permanecer sujeta a la decisión humana.
