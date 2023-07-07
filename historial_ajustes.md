# Historial de Ajustes
## 06/07/2023 
Se realizó un ajuste en el script de "codigo_python/calendario.py".

Se dio un error en el scrapeo, dado que la página oficial no puso una fecha en formato dd/mm/yyyy o dd/mm/yyy. Esto ocurrió 2 veces.
Estos casos ya fueron contemplados (se agrega una fecha de 01/01/9999) para no perder el dato. 

Se genera una variable de conteo de errores, donde siempre que se tenga esa fecha en el calendario se dara en cada ejecución un total de 2 errores.

Adicionalmente, en caso de que la cantidad de errores sea mayor a 2 (es decir, aparece algun error no contemplado) se notifica.

Se hace un nuevo tag: v.0.0.2
