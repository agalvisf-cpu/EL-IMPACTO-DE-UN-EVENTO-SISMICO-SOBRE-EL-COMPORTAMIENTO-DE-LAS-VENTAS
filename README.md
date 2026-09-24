# Actividad 5 — 

Autores: Juan Sebastian Muñoz Riaño - Anyi Lizeth Galvis Fajardo 

---

# 1. Planteamiento

**Pregunta analítica.** ¿Hubo un comportamiento anormal en las ventas —por
regiones, segmentos, clase y subcategorías— durante la semana del
terremoto en Colombia (10 de agosto de 2026) y la semana siguiente, frente a
la semana previa?

**Usuario del resultado.** El equipo de planeación de inventarios y
abastecimiento de las cadenas, que necesita anticipar posibles quiebres de
producto esencial ante futuros eventos sísmicos.

**Datos.** Ventas, unidades vendidas e inventario de 14 proveedores
principales de consumo masivo, en tres cadenas (Éxito, Olímpica y Alkosto,
anonimizadas), para todos sus puntos de venta y productos, en tres semanas
consecutivas de agosto de 2026:

# 2. Resultado en una frase

En el **nivel agregado no hubo cambio significativo** —el ANOVA no rechaza la
hipótesis nula, ni en pesos ni en unidades, ni siquiera al restringir la
prueba a las cuatro regiones más afectadas—, pero **sí hubo un cambio de
composición**: la semana del sismo la canasta se recompuso hacia bienes de
emergencia (cereales, bebidas, agua, arroz, conservas, licores) y en contra
de productos aplazables (café, galletas, lácteos), con un efecto heterogéneo
por región y un enfriamiento general la semana siguiente. El inventario y la
tasa de quiebre se mantuvieron estables (~9 %).


## 3. Decisiones de datos relevantes

- **Ventas/unidades vacías o en 0 = no venta.** Un vacío o un 0 significa que
  ese producto no se vendió esa semana en ese punto de venta; no es un error.
  Se conserva como 0 y la fila se mantiene. El inventario vacío sí es una
  lectura faltante y se deja como NaN.
- **Números con coma decimal.** Las semanas 33 y 34 usan coma decimal
  (`"212256,24"`); se convierte a punto para no inflar los valores.
- **Taxonomía consistente.** Se verifica por código de barras (GTIN) que cada
  producto conserva su misma familia/categoría/subcategoría en las tres
  semanas (100 %), de modo que las comparaciones por categoría son válidas.

## 4. Prueba de hipótesis y hallazgo

El **ANOVA general no rechaza H0** (ventas p = 0,84; unidades p = 0,90) y el
**ANOVA restringido a las regiones foco tampoco** (ventas p = 0,91; unidades
p = 0,92): el nivel promedio de ventas no cambia entre periodos. La razón es
que dentro de cada región/periodo las categorías que suben (emergencia) se
compensan con las que bajan (aplazables). La prueba pareada de Friedman
—apropiada porque las mismas celdas se repiten en los tres periodos— sí
rechaza H0 (p < 0,001): el cambio existe, pero es de **composición**, no de
nivel promedio. El detalle está en el informe y el notebook.

