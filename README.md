# Programa de Tablas de Marea para el Servicio Mareográfico Nacional de la UNAM

## Objetivo del programa

Este programa fue realizado como actividad de Servicio Social en el  Servicio Mareográfico Nacional de la UNAM.

Este programa genera un archivo TXT y un archivo PDF con los datos ordenados conforme al formato de Tablas de marea del Servicio Mareográfico Nacional de la UNAM a partir de un archivo .LIS generado con el programa SPL64.

## 

## Créditos

**Realizado por**: José Yair Castro Rojas (2023)

**Revisores**: Octavio Gómez Ramos (jefe del Servicio Mareográfico Nacional) y Miriam Arianna Zarza Alvarado (auxiliar de Servicios Geofísicos).

## Guía de uso

Para ejecutar este programa, se necesita contar con Python en el equipo donde se vaya a utilizar, acompañado de las siguientes librerías del lenguaje:
- pandas
- numpy
- calendar
- os
- fpdf

El código de este archivo debe ejecutarse en el mismo directorio donde se encuentren los archivos "NBMI.txt", "ESTACIONES.txt" y "HL25023.LIS", con el comando:
~~~
python tablasdemarea_SMN_UNAM_v1.py
~~~

Únicamente debe ingresarse el año al que corresponde la tabla, lo que se solicita cuando el programa se ejecuta.

En caso de que el archivo ".LIS" no tenga el nombre "HL25023", habrá que cambiarlo en la variable "archivoDatos", a fin de que el programa funcione.

## Mejoras pendientes
- Modularización de las funciones.
- Añadir espacios extra cuando un día registra cinco o más datos de altura.
- Mejorar la lógica y legibilidad.
- Realizar pruebas empleando datos de distintas estaciones y años.
- Mejorar los comentarios.
- Añadir una interfaz gráfica.
