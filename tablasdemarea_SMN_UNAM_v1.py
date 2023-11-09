'''
=== PROGRAMA PARA GENERAR TABLAS DE MAREA ===

Este programa fue realizado como actividad de Servicio Social en el 
Servicio Mareográfico Nacional de la UNAM.

Este programa genera un archivo TXT y un archivo PDF con los datos 
ordenados conforme al formato de tablas de marea del Servicio 
Mareográfico Nacional de la UNAM. 

Realizado por:
- José Yair Castro Rojas

Revisores:
- Octavio Gómez Ramos (jefe del Servicio Mareográfico Nacional)
- Miriam Arianna Zarza Alvarado (auxiliar de Servicios Geofísicos)
'''

'''
=== MANUAL DE USO ===

El código de este archivo debe ejecutarse en el mismo directorio donde
se encuentren los archivos "NBMI.txt", "ESTACIONES.txt" y "HL25023.LIS".

Únicamente debe ingresarse el año al que corresponde la tabla, lo que
se solicita cuando el programa se ejecuta.

En caso de que el archivo ".LIS" no tenga el nombre "HL25023", habrá que
cambiarlo en la variable "archivoDatos", a fin de que el programa funcione.
'''

# Librerías empleadas:
# pandas -> para manipular los datos a través de DataFrames.
# numpy -> para usar algunas funciones matemáticas.
# calendar -> para usar la función que determina si un año es o no bisiesto.
# os -> para funciones propias del Sistema Operativo.
# fpdf -> para exportar el PDF final.
import pandas as pd
import numpy as np
import calendar
import os
from fpdf import FPDF


# Input para recibir el año al que corresponden los datos.
year_tabla = int(input("Por favor, ingrese el año al que corresponden los datos: "))


# Lectura del archivo "ESTACIONES.txt" con los datos de las estaciones.
# Usamos una Expresión Regular (RegEx) para obtener la separación adecuada de las columnas.
# Especificamos "Python" como valor de "engine" para evitar problemas al tratar con RegEx.
estaciones = pd.read_csv("ESTACIONES.txt",
                         # Lógica de la Expresión Regular:
                         # espacios después de un punto | espacios después de un número | espacios antes de dos números o más
                         sep="(?<=\.)\s+|(?<=[0-9])\s+|\s+(?=\d{2})",
                         engine="python",
                         header = None)


# Lectura del archivo "NBMI.txt", también datos de las estaciones.
# Usamos una Expresión Regular (RegEx) para obtener la separación adecuada de las columnas.
# Especificamos "Python" como valor de "engine" para evitar problemas al tratar con RegEx.
ff = pd.read_csv("NBMI.txt",
                 # Lógica de la Expresión Regular:
                 # tabulación + un espacio o más | tres espacios o más | tabulaciones
                sep="\t+\s{1,}|\s{3,}|\t",
                engine="python")


# Lectura del archivo "HL25023.LIS" con los datos de la predicción para la estación.
# Usamos una Expresión Regular (RegEx) para obtener la separación adecuada de las columnas.
# Especificamos "Python" como valor de "engine" para evitar problemas al tratar con RegEx.

# Editar esta variable para especificar el nombre del archivo .LIS si este no es "HL25023".
archivoDatos = "HL25023.LIS" 
archivoH = pd.read_csv(archivoDatos,
                 # Lógica de la Expresión Regular: un espacio o más.
                sep="\s{1,}",
                engine="python")
# Eliminamos la primera columna de los datos importados...
# para que el número de columnas en el encabezado y en los datos sea igual.
archivoH = archivoH.reset_index(drop = True)

# Se colocan los encabezados de las columnas "DATE" y "STN" en el lugar correcto (OPCIONAL).
#archivoH.rename(columns = {"DATE":"HL", "STN":"DATE", "HL":"STN"}, inplace = True)


# Selecciona la fila donde se encuentra la coincidencia del número de estación...
# en los Dataframes "ff" (NBMI.txt) y "archivoH" (.LIS).
stationNumber = ff.loc[ff["000"] == archivoH.loc[0][0]]


# Selecciona la fila donde se encuentra la coincidencia del número de estación...
# en los Dataframes "estaciones" (ESTACIONES.txt) y "archivoH" (.LIS).
stationName = estaciones.loc[estaciones[0] == archivoH.loc[0][0]]


# archivoSalida -> obtenemos el nombre del archivo base de "archivoH" a partir de su ruta.
archivoSalida = os.path.basename(archivoDatos)
# Nos quedamos solo con la parte del nombre y omitimos la extensión.
archivoSalida = os.path.splitext(archivoSalida)[0]
# archivoSalidaTXT -> agregamos la extensión del archivo TXT que obtendremos como salida.
archivoSalidaTXT = str(archivoSalida) + ".txt"
# archivoSalidaPDF -> agregamos la extensión del archivo PDF que obtendremos como salida.
archivoSalidaPDF = str(archivoSalida) + ".pdf"

# Si el archivo TXT ya existe en la ruta donde se está ejecutando el programa, se elimina.
if os.path.exists(archivoSalidaTXT):
    os.remove(archivoSalidaTXT)
    
# Si el archivo PDF ya existe en la ruta donde se está ejecutando el programa, se elimina.
if os.path.exists(archivoSalidaPDF):
    os.remove(archivoSalidaPDF)


# Restamos el BMI (promedio de bajamar) de la estación a los datos "HGT" (alturas) en el DataFrame "archivoH".
BMI = stationNumber.values[0][5]
archivoH["HGT"] = archivoH["HGT"] - BMI
# Función para restar el BMI a todas las columnas "HGT", ya que cuando hay varias columnas con el mismo nombre...
# ... Pandas les añade un número para diferenciarlas.
for i in range(1,5,1):
    archivoH["HGT.{}".format(i)] = archivoH["HGT.{}".format(i)] - BMI


# Removemos la primera y última fila si el valor "DATE" no corresponde con el primer y último día del año, respectivamente.
# Borrar si la primera fila en DATE no es 1.
if archivoH.values[0][1] != 1:
    archivoH = archivoH.drop(0)

# ultimafila -> último índice de la tabla, que es igual al número de filas en la tabla menos uno.
ultimaFila = archivoH.shape[0] - 1
# Si la variable 'ultimafila' no es igual a 31, eliminarla.
if archivoH.values[ultimaFila][1] != 31: 
    archivoH = archivoH.drop(ultimaFila + 1)


# Creamos un diccionario con los meses según su número. Los valores son:
# 1. El nombre del mes.
# 2. Los días que tiene el mes.
# 3. La fila donde comienzan los datos del mes en "archivoH".
dictMeses = {1: ("ENERO", 31, 0), 2: ("FEBRERO", 28, 31), 3: ("MARZO", 31, 59), 4: ("ABRIL", 30, 90), 
             5: ("MAYO", 31, 120), 6: ("JUNIO", 30, 151), 7: ("JULIO", 31, 181), 8: ("AGOSTO", 31, 212), 
             9: ("SEPTIEMBRE", 30, 243), 10: ("OCTUBRE", 31, 273), 11: ("NOVIEMBRE", 30, 304), 12: ("DICIEMBRE", 31, 334),
            13: ("ENERO", 31, 365)}


# --- FUNCIÓN PARA IDENTIFICAR Y ASIGNAR LAS HORAS DE LOS DATOS ---
# Recibe tres parámetros:
# 1. tabladf -> Dataframe al que se le realizarán las modificaciones.
# 2. mes -> número de mes (asocia el valor a su mes en el diccionario "dictMeses").
# 3. year -> para evaluar si el año es o no bisiesto.
def horasdf(tabladf, mes, year):
    # col -> corresponde a la primera columna "TIME" de "archivoH".
    col = 3  
    # row -> identifica la fila donde comienza el mes en los datos de "arhivoH" conforme a la información en "dictMeses".
    row = dictMeses[mes][2]  
    
    # Si ese año febrero es bisiesto, comenzar a recorrer las filas una posición después.
    if mes != 2 and calendar.isleap(year) == True: 
        row += 1 

    # En este bucle, "i" es para recorrer las columnas y "j" para recorrer las filas en el Dataframe vacío.
    for i in range(1, 10, 4): 
        for j in range(50):
            # Si la hora no es igual a 9999 y la fila es menor a la última fila del mes más uno...
            # agregar los datos indicados.
            if archivoH.values[row][col] != 9999 and row < dictMeses[mes+1][2]:
                # Usamos una variable auxiliar para evitar amonontar todo en una sola línea.
                aux = int(archivoH.values[row][col])
                #se usa el método "format()" para forzar a que aparezcan 4 dígitos.
                tabladf.loc[j][i] = "{:04d}".format(aux)
            # Si no se cumple la condición del "if", rellenar celda con un espacio en blanco.
            else:
                tabladf.loc[j][i] = " "
            
            # Si la columna actual en "archivoH" es la columna con índice 11,...
            # ir dos filas después de la posición actual.
            # Si la columna actual en "archivoH" es la columna 11 o posterior,...
            # regresar a la columna 3 y pasar a la siguiente fila.
            # **IMPORTANTE**: esta condición influye directamente en la posición final de los datos.
            if col < 11:
                col += 2
            else:
                col = 3
                row += 1

    # Condición con bucle anidado para añadir datos cuando el mes tiene 31 días.
    if dictMeses[mes][1] == 31:
        # En este bucle, "i" es para recorrer las columnas y "j" para recorrer las filas en el Dataframe.
        # Comenzamos en la fila 50 y terminamos en la fila 55.
        for j in range(50, 55, 1):
            # Comenzamos a añadir datos al Dataframe a partir de la columna 9.
            i = 9
            # Si la hora no es igual a 9999 y la fila es menor a la última fila con los datos del mes más uno,...
            # agregar los datos indicados.
            if archivoH.values[row][col] != 9999 and row < dictMeses[mes+1][2]:
                aux = int(archivoH.values[row][col])
                tabladf.loc[j][i] = "{:04d}".format(aux)
            # Si no se cumple la condición del "if", rellenar celda con un espacio en blanco.
            else:
                tabladf.loc[j][i] = " "

            # Si la columna actual en "archivoH" es la columna con índice 11,...
            # ir dos filas después de la posición actual.
            # Si la columna actual en "archivoH" es la columna 11 o posterior,...
            # regresar a la columna 3 y pasar a la siguiente fila.
            # **IMPORTANTE**: esta condición influye directamente en la posición final de los datos
            if col < 11:
                col += 2
            else:
                col = 3
                row += 1


# --- FUNCIÓN PARA IDENTIFICAR Y ASIGNAR LAS ALTURAS AL DATAFRAME ---
# Recibe tres parámetros:
# 1. tabladf -> dataframe al que se le realizarán las modificaciones.
# 2. mes -> número de mes (con el valor exploramos el diccionario).
# 3. year -> para evaluar si el año es o no bisiesto.
def alturasdf(tabladf, mes, year):
    # col -> corresponde a la primera columna "HGT" de "archivoH".
    col = 4
    # row -> identifica la fila donde comienza el mes en los datos de "arhivoH" conforme a la información en "dictMeses".
    row = dictMeses[mes][2]
    
    # Si ese año febrero es bisiesto pero el mes no es enero ni febrero, se comienza a recorrer las filas una posición después.
    if mes != 1 and mes != 2 and calendar.isleap(year) == True:
        row += 1

    # En este bucle, "i" es para recorrer las columnas y "j" para recorrer las filas del DataFrame "tabladf".
    for i in range(3, 12, 4):
        for j in range(50):
            # Si la hora no es igual a 9999 y la fila es menor a la última fila del mes más uno...
            # agregar los datos indicados.
            if archivoH.values[row][col-1] != 9999 and row < dictMeses[mes+1][2]:
                # aux -> valores de "HGT" convetidos a METROS (divididos entre 100).
                aux = archivoH.values[row][col] / 100
                # aux2 -> valores de "HGT" convertidos a PIES (multiplicando los METROS por 3.28084).
                aux2 = aux * 3.28084
                # Se convierte el dato númerico de los Metros en una cadena de texto.
                aux = str(aux)
                # Se limitan los datos a 5 caracteres como máximo.
                tabladf.loc[j][i] = aux[:5]
                # Se convierte el dato númerico de los Pies en una cadena de texto.
                aux2 = str(aux2)
                # Se limitan los datos a 5 caracteres como máximo.
                tabladf.loc[j][i-1] = aux2[:5]
            # Si no se cumple la condición del "if", rellenar las celdas de Pies y Metros con un espacio en blanco.
            else:
                tabladf.loc[j][i] = " "
                tabladf.loc[j][i-1] = " "

            # Si la columna actual en "archivoH" es la columna con índice 12,...
            # ir dos filas después de la posición actual.
            # Si la columna actual en "archivoH" es la columna 12 o posterior,...
            # regresar a la columna 4 y pasar a la siguiente fila.
            # **IMPORTANTE**: esta condición influye directamente en la posición final de los datos.
            if col < 12:
                col += 2
            else:
                col = 4
                row += 1

    # Condición con bucle anidado para añadir datos cuando el mes tiene 31 días.
    if dictMeses[mes][1] == 31:
        # En este bucle, "i" es para recorrer las columnas y "j" para recorrer las filas en el Dataframe.
        # Comenzamos en la fila 50 y terminamos en la fila 55.
        for j in range(50, 55, 1):
             # Comenzamos a añadir datos al Dataframe a partir de la columna 9.
            i = 11
            # Si la hora no es igual a 9999 y la fila es menor a la última fila con los datos del mes más uno,...
            # agregar los datos indicados.
            if archivoH.values[row][col-1] != 9999 and row < dictMeses[mes+1][2]:
                # aux -> valores de "HGT" convetidos a METROS (divididos entre 100).
                aux = archivoH.values[row][col] / 100
                # aux2 -> valores de "HGT" convertidos a PIES (multiplicando los METROS por 3.28084).
                aux2 = aux * 3.28084
                # Se convierte el dato númerico de los Metros en una cadena de texto.
                aux = str(aux)
                # Se limitan los datos a 5 caracteres como máximo.
                tabladf.loc[j][i] = aux[:5]
                # Se convierte el dato númerico de los Pies en una cadena de texto.
                aux2 = str(aux2)
                # Se limitan los datos a 5 caracteres como máximo.
                tabladf.loc[j][i-1] = aux2[:5]
            # Si no se cumple la condición del "if", rellenar las celdas de Pies y Metros con un espacio en blanco.
            else:
                tabladf.loc[j][i] = " "
                tabladf.loc[j][i-1] = " "

            # Si la columna actual en "archivoH" es la columna con índice 12,...
            # ir dos filas después de la posición actual.
            # Si la columna actual en "archivoH" es la columna 12 o posterior,...
            # regresar a la columna 4 y pasar a la siguiente fila.
            # **IMPORTANTE**: esta condición influye directamente en la posición final de los datos.
            if col < 12:
                col += 2
            else:
                col = 4
                row += 1


# --- FUNCIÓN PARA CREAR UN NUEVO DATAFRAME MENSUAL ---
# Recibe dos parámetros:
# 1. mes -> número de mes al que corresponde el DataFrame a crear.
# 2. year -> año de los datos, para evaluar si el año es o no bisiesto.
def nuevoMes(mes, year):
    # Se crea un nuevo DataFrame con las columnas especificadas y con 50 filas iniciales.
    tabladf = pd.DataFrame(columns = ["DIA", "HORA", "PIES", "METROS", "DIA", "HORA", "PIES", "METROS", "DIA", "HORA", "PIES", "METROS"],
                      index = np.arange(50))
    # k = contador para ir agregando los días del mes.
    k = 0
    # diaLimite -> asocia el número al mes y sus valores conforme al diccionario de meses "dictMeses" que creamos.
    diaLimite = dictMeses[mes][1]  
    # Si el año es bisiesto y el mes es febrero, añadir un día extra a los "28" del febrero regular.
    if mes == 2 and calendar.isleap(year) == True:  
        diaLimite += 1

    # En este bucle, "i" recorre las columnas y "j" las filas del Dataframe que acabamos de crear...
    # y donde se irán añadiendo los días del mes cada 5 filas.
    for i in range(0, 9, 4):
        for j in range(0, 50, 5):
            k += 1
            # Se coloca el día "k" en la celda "[j][i]" de nuestro DataFrame.
            tabladf.loc[j][i] = k 
            # Cuando el día "k" llega al último día del mes, el bucle se finaliza.
            if k == diaLimite:
                break
                
    #se agregan 5 filas extra al DataFrame (por si el mes tuviera 31 días)
    for i in range(5):
            tabladf.loc[len(tabladf)] = float("nan")
    
    # Si el mes tiene 31 días, se añade el día "31".
    if diaLimite == 31:
        tabladf.loc[50][8] = diaLimite

    # Se invoca la función "horasdf" para agregar las horas al dataframe.
    horasdf(tabladf, mes, year)
    # Se invoca la función "alturasdf" para agregar las alturas en metros y pies al dataframe.
    alturasdf(tabladf, mes, year)
    
    # Se remueven los valores NAN en el DataFrame.
    tabladf = tabladf.replace(np.nan, " ")

    # Se retorna el Dataframe resultante.
    return tabladf


# Creamos las 12 tablas, una para cada mes, a través de la función "nuevoMes"
tablaMes1 = nuevoMes(1, year_tabla)
tablaMes2 = nuevoMes(2, year_tabla)
tablaMes3 = nuevoMes(3, year_tabla)
tablaMes4 = nuevoMes(4, year_tabla)
tablaMes5 = nuevoMes(5, year_tabla)
tablaMes6 = nuevoMes(6, year_tabla)
tablaMes7 = nuevoMes(7, year_tabla)
tablaMes8 = nuevoMes(8, year_tabla)
tablaMes9 = nuevoMes(9, year_tabla)
tablaMes10 = nuevoMes(10, year_tabla)
tablaMes11 = nuevoMes(11, year_tabla)
tablaMes12 = nuevoMes(12, year_tabla)

# Convertimos las tablas de cada mes en cadenas de texto con separación de 6 espacios entre columnas
stringMes1 = tablaMes1.to_string(index=False, col_space = 6)
stringMes2 = tablaMes2.to_string(index=False, col_space = 6)
stringMes3 = tablaMes3.to_string(index=False, col_space = 6)
stringMes4 = tablaMes4.to_string(index=False, col_space = 6)
stringMes5 = tablaMes5.to_string(index=False, col_space = 6)
stringMes6 = tablaMes6.to_string(index=False, col_space = 6)
stringMes7 = tablaMes7.to_string(index=False, col_space = 6)
stringMes8 = tablaMes8.to_string(index=False, col_space = 6)
stringMes9 = tablaMes9.to_string(index=False, col_space = 6)
stringMes10 = tablaMes10.to_string(index=False, col_space = 6)
stringMes11 = tablaMes11.to_string(index=False, col_space = 6)
stringMes12 = tablaMes12.to_string(index=False, col_space = 6)


# Variable con la cadena de texto correspondiente a la "HORA DEL MERIDIANO"...
# conforme a los datos reservados en la variable "stationNumber"
meridiano = "\nHORA DEL MERIDIANO {:03d}° W.".format(int(stationNumber.values[0][4]))

# - - - FUNCIÓN PARA ENCONTRAR Y REEMPLAZAR UNA COINCIDENCIA CONCRETA EN EL TEXTO - - - 
def cambiar_coincidencia(texto, coincidencia, reemplazo, n):
    encontrar = texto.find(coincidencia)
    i = encontrar != -1
    while encontrar != -1 and i != n:
        encontrar = texto.find(coincidencia, encontrar + 1)
        i += 1
    if i == n:
        return texto[:encontrar] + reemplazo + texto[encontrar + len(coincidencia):]

# # --- FUNCIÓN PARA DAR FORMATO A LAS CADENAS DE TEXTO DE CADA MES (PARA EL ARCHIVO TXT) ---
def formato_tabla(stringTabla, num_mes):
    # Reemplaza los tres espacios en blanco al inicio de cada columna por solo un salto de línea.
    stringTabla = stringTabla.replace("\n   ", "\n")
    # Agrega un salto de línea adicional entre los nombres de las columnas y los datos.
    stringTabla = stringTabla.replace("METROS\n", "METROS\n\n")
    # Elimina los primeros tres espacios en blanco juntos encontrados en el texto. 
    stringTabla = stringTabla.replace("   ", "", 1)
    # Se utiliza la función cambiar_coincidencia para agregar "HORA DEL MERIDIANO" en columna 51.
    stringTabla = cambiar_coincidencia(stringTabla, "\n", "\nHORA DEL MERIDIANO {:03d}° W.".format(int(stationNumber.values[0][4])), 52)
    # Se eliminan los espacios en blanco que reemplazará el texto "HORA DEL MERIDIANO" en la fila.
    stringTabla = stringTabla.replace("W." + (" " * len(meridiano)), "W. ", 1)
    # Se agrega un salto de línea al inicio del texto.
    stringTabla = "\n" + stringTabla

    # split_stringTabla -> divide el texto en cada salto de línea y guarda los valores separados en una lista.
    split_stringTabla = stringTabla.split("\n")
    # num_caracteres -> número de caracteres que tiene la primera cadena de la lista "split_stringTabla".
    num_caracteres = len(split_stringTabla[1])
    # cabecera -> cadena de texto que se agregará al inicio del texto.
    # stationName.iat[0, 1] -> nombre de la estación en la variable tipo Dataframe "stationName".
    # dictMeses[num_mes][0] -> nombre del mes conforme al diccionario "dictMeses" que creamos.
    # year_tabla -> año que se pide al ejecutar el programa y corresponde al año de los datos.
    cabecera = "ESTACION" + stationName.iat[0, 1] + dictMeses[num_mes][0] + " " + str(year_tabla)
    # len_cabecera -> número de caracteres en la cabecera entre dos.
    len_cabecera = int((num_caracteres - len(cabecera))/2)
    # cabecera -> se agregan espacios en blanco conforme al número de "len_cabecera"...
    # a fin de dejar el nombre de la estación en medio.
    cabecera = "\n\n\n" + "ESTACION" + " " * len_cabecera + stationName.iat[0, 1] + " " * len_cabecera + dictMeses[num_mes][0] + " " + str(year_tabla)
    
    # Se agrega un salto de línea entre la cabecera y los datos.
    stringTabla = cabecera + "\n" + stringTabla
    
    return stringTabla


# Obtenemos los textos de los 12 meses de la tabla ya con un formato legible para exportarlo a TXT.
resultado1 = formato_tabla(stringMes1, 1)
resultado2 = formato_tabla(stringMes2, 2)
resultado3 = formato_tabla(stringMes3, 3)
resultado4 = formato_tabla(stringMes4, 4)
resultado5 = formato_tabla(stringMes5, 5)
resultado6 = formato_tabla(stringMes6, 6)
resultado7 = formato_tabla(stringMes7, 7)
resultado8 = formato_tabla(stringMes8, 8)
resultado9 = formato_tabla(stringMes9, 9)
resultado10 = formato_tabla(stringMes10, 10)
resultado11 = formato_tabla(stringMes11, 11)
resultado12 = formato_tabla(stringMes12, 12)


# Salvamos el texto del primer mes un archivo TXT con el nombre que guardamos en la variable "archivoSalida".
archivo = open(archivoSalidaTXT, "w")
archivo.write(resultado1)
archivo.close()

# Creamos un bucle para editar el archivo creado y agregar los textos de el resto de los meses.
for i in range(2, 13, 1):
    archivo = open(archivoSalidaTXT, "a")
    numResultado = "resultado" + str(i)
    archivo.write(eval(numResultado))
    archivo.close()


# Salvamos ahora el resultado en un archivo PDF a través de la líbrería fpdf.
pdf = FPDF()
pdf.set_font("Courier", "B", 10.5)

# Creamos un bucle para añadir los datos correspondientes a cada página del PDF.
for i in range (1, 13, 1):
    pdf.add_page()
    pdf.image("unam_logo.png", y = 60, w = pdf.epw)
    numResultado = "resultado" + str(i)
    pdf.multi_cell(0, None, "\n\n\n\n\n\n" + eval(numResultado), border = 0, align = "C", center = True)

pdf.output(archivoSalidaPDF)
