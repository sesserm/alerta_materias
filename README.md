# Mantenimiento
NO SE DEBE FUSIONAR JAMÁS CON LA RAMA DE PRODUCCIÓN!!!

Esta es una rama permanente con los códigos de desarrollo. Estos códigos son diferentes a los que están en producción.
Esta rama se utiliza únicamente en caso de que falle el código principal para poder correr el código localmente y detectar el error. Se toma de referencia una versión estable del código (ver tags).

Una vez se solucione el error, se traslada el cambio manualmente a la versión de producción (se prueba que funcione correctamente) y se etiqueta la versión de mantenimiento con el ajuste. También se etiqueta posteriormente la versión de producción.

Por último se anota en archivo de historial_ajustes.md los cambios realizados lo más detallado posible.

