#! /usr/bin/env python
# -*- coding: utf-8 -*-
import os
# Comprobamos que existen las librerías necesarias
# python-mysqldb
try:
    import MySQLdb
except ImportError:
    print "No se encuentra la biblioteca MySQLdb"
    exit()
import smtplib
from email.mime.text import MIMEText
# python-lxml
try:
    from lxml import etree
except ImportError:
    print "No se encuentra la biblioteca lxml"
    exit()    
from ConfigParser import SafeConfigParser
from getpass import getpass

# Cargamos en parser el fichero de configuración
parser = SafeConfigParser()
parser.read('infohardware.cfg')

# Realizamos la conexión a la Base de Datos
# Versión IESGN: Se pide contraseña por teclado, si no es correcta termina.
try:
    db = MySQLdb.connect(host = parser.get('mysql','host'),
                         user = parser.get('mysql','user'),
                         passwd = getpass("Contraseña de MySQL: "),
                         db = parser.get('mysql','db'))
except:
    exit()
cursor = db.cursor()

# Versión IESGN: Función que busca el número de serie siguiente para los
# equipos que no tienen número de serie asignados.
def buscar_ns_iesgn():
    sql = "select num_serie from equipo where num_serie like 'iesgn%' \
order by num_serie desc"
    cursor.execute(sql)
    tupla = cursor.fetchone()
    if tupla != None:
        return "%.4d" % ((int)(tupla[0][5:]) + 1)
    else:
        return "0001"

def conversor(cant, columna):
    """
    Función para convertir el tamaño de los discos duros a MB/GB y las
    frecuencias de las memorias RAM a MHz.
    Recibe la cantidad en bytes o Hz y devuelve una cadena que expresa
    la misma cantidad en MB o GB (discos duros) o MHz (ram)
    """
    aux = cant
    if columna == "size" and aux != "":
        unit = ['MB','GB']
        aux = int(cant) / 2**20
        if aux >= 1024:
            aux = "%s %s" % (str(aux / 1024), unit[1])
        else:
            aux = str(aux) + unit[0]
    if columna == "clock" and aux != "":
        aux = "%d MHz" % (int(cant) / 10**6)
    return aux

def obtener_datos(arbol, ruta, datos, adicionales = None):
    """
    Función que lee del arbol xml donde tenemos la configuración del 
    equipo los datos que le indicamos a partir de una expresión xpath.
    Devuelve los datos leidos del arbol xml además de los datos que 
    opcionalmente se pueden pasar en el parámetro adicionales.

    arbol - Objeto ElementTree que representa la información del sistema
    ruta - Expresión xpath base para realizar la consultas
    datos - Lista donde se guarda los datos que vamos a leer
    adicionales - Lista opcional donde guardamos datos que se van a 
    devolver, además de los datos leídos con xpath

    La función devuelve una lista con los datos leidos (diccionario) 
    haciendo las consultas con xpath más los posibles datos que se 
    han recibido en el parámetro adicionales.
    """
    respuesta = []
   
    # Calculamos el número de datos que vamos a consultar con xpath
    # Si hemos enviado datos adicionales, será el tamaño de la lista 
    # datos menos la longitud de la lista adicionales.
    if adicionales != None:
        cantcolxml = len(datos) - len(adicionales)
    else:
        cantcolxml = len(datos)
    
    # Comprobamos el número de componentes (cantidad de discos duros,
    # cantidad de memorias, ...
    num_componentes = int(arbol.xpath('count(%s)' % ruta))
    for i in xrange(num_componentes):
        intermedio = {}
        cont_adicionales = 0
        cont_datos = 1
        # Para cada dato lo intnetamos leer del arbol xml con la expresión xpath
        # sino es posible, si todavía estamos leyendo datos con xpath, el valor
        # es cadena vacia, si ya hemos leido toddos los datos con xpath, el valor
        # se obtendra de la lista adicionales. 
        for dato in datos:
            try:
                valor = arbol.xpath("%s/%s/text()" % (ruta,dato))[i]
            except:
                if cont_datos <= cantcolxml:
                    valor = ""
                else:
                    if adicionales != None:
                        valor = adicionales[cont_adicionales]
                        cont_adicionales += 1
            intermedio[dato] = valor
            cont_datos += 1
        respuesta.append(intermedio)
    return respuesta

def buscar_n_serie(num):
    """
    Función que comprueba si existe un equipo con un determinado número de serie.
    num - Número de serie a buscar
    La función devuelve un valor boolerano (false si nno se ha encontrado un equipo
    con el número de serie recibido.
    """
    sql = "SELECT num_serie FROM equipo WHERE num_serie = '%s'" % num
    cursor.execute(sql)
    if cursor.fetchone():
        return True
    else:
        return False

def buscar_componente(respuesta, tabla, datos):
    """
    Función que busca en la base de datos la información de un equipo.
    respuesta - Atributo que queremos devolver
    tabla - Tabla de la base de datos donde queremos buscar
    datos - Una lista con los campos y valores que se utilizará para
    determinar la condición de busqueda.
    La función puede devolver dos clases de valores:
    - Si sólo se obtiene un registro con un valor se devuelve el valor.
    - Si se obtiene más de un registro se devuelve una tupla 
    """
    sql = "SELECT %s FROM %s WHERE " % (respuesta, tabla)
    for k in datos[0].keys():
        sql = sql + "%s = '%s' AND " % (k,datos[0][k])
    sql = sql[0:-4]
    cursor.execute(sql)
    tuplas = cursor.fetchall()
    if len(tuplas) == 1 and len(tuplas[0]) == 1:
        return tuplas[0][0]
    return tuplas

def insertar_componente(tabla, datos):
    """
    La función realiza la inserción de datos en la base de datos
    tabla - Tabla donde vamos a insertar un nuevo registro
    datos - Lista con los datos que vamos a insertar
    """
    num_componentes = len(datos)
    for i in xrange(num_componentes):
        sql = "INSERT INTO %s(" % tabla
        for j in datos[i].keys():
            sql = sql + "%s," % j
        sql = sql[0:-1]
        sql = sql + ") VALUES ("
        for j in datos[i].keys():
            sql = sql + "'%s'," % conversor(datos[i][j],j)
        sql = sql[0:-1]
        sql = sql + ")"
        cursor.execute(sql)

def borrar_componente(tabla, condiciones):
    """
    La función realiza el borrado de datos en la base de datos
    tabla - Tabla donde vamos a borrar un registro
    datos - Lista con los datos que vamos a utilizar para seleccionar
    el registro que vamos a borrar.
    """
    sql = "DELETE FROM %s WHERE " % tabla
    for key in condiciones:
        sql = sql + "%s='%s'," % (key, condiciones[key])
    sql = sql[0:-1]
    cursor.execute(sql)

def leer_equipo(ns):
    """Función que lee las características de un equipo guardado en 
    la base de datos
    ns - Númerod e serie del equipo que queremos leer
    La función devuelve una lista de listas con las características
    que hemos leido del equipo (CPU,Placa BAse,RAM,HD,RED)
    Se devuelve también los títulos que se van a mostrar para dar la 
    información de los distintos componenetes.
    """
    res=[]
    idcpu=buscar_componente("cpu_idcpu","equipo",[{"num_serie":ns}])
    res.append(["CPU:",buscar_componente("vendor,product,slot","cpu",
                                         [{"idcpu":idcpu}])])
    res.append(["Placa Base:",buscar_componente("vendor,product","equipo",
                                                [{"num_serie":ns}])])
    res.append(["RAM:",buscar_componente("size,clock","ram",
                                         [{"equipo_num_serie":ns}])])
    res.append(["HD:",buscar_componente("serial,vendor,product,\
                                        description,size","hd",
                                        [{"equipo_num_serie":ns}])])
    res.append(["CD:",buscar_componente("vendor,product","cd",
                                        [{"equipo_num_serie":ns}])])
    res.append(["Red:",buscar_componente("serial,vendor,product","red",
                                         [{"equipo_num_serie":ns}])])    
    return res

def escribir_equipo(datos):
    """
    Función que recibe una lista con las características de un equipo
    devuelta por la función leer_equipo. 
    Devuelve un string con dicha información lista para imprimir.
    """
    txt=""
    for linea in datos:
        txt += linea[0]
        txt += "\n"
        for comp in linea[1]:
            txt += escribir_componente(comp)
            txt += "\n"
    return txt

def escribir_componente(comp):
    """
    Función auxiliar que devuelve en un string la información
    de un componenete en concreto. Utilziada por la función 
    escribir_equipo
    """
    txt=""
    for c in comp:
        if c != None:
            txt += c + " "
    return txt

def comparar_equipos(new,old):
    """
    Función que recibe dos listas, con la información de dos equipos.
    Se puede considerar que nos referimos a dos estados de un mismo equipo,
    es decir la información de un equipo ya inventariado y la información
    de dicho equipo después de otro proceso de inventariado.
    Compara dichas listas y devuelve un string con información de los componentes
    que tenía anteriormente y ahora ya no posee, y con infomación de los componenetes 
    que posee en el último uinventario y que no tenía en el anterior.
    componentes 
    """
    txt=""
    for i in xrange(len(old)):
        # Miro los componenetes nuevos que se han añadido
        for j in xrange(len(new[i][1])):
            newc = new[i][1][j]
            encontrado = False
            for k in xrange(len(old[i][1])):
                if newc == old[i][1][k]:
                    encontrado = True
                    break;
            if encontrado == False:
                txt += new[i][0] + "(+) " + escribir_componente(newc)
                txt += "\n"
        # Miro los componenetes antiguos que ya no están
        for j in xrange(len(old[i][1])):
            oldc=old[i][1][j]
            encontrado = False
            for k in xrange(len(new[i][1])):
                if oldc == new[i][1][k]:
                    encontrado = True
                    break;
            if encontrado==False:
                txt += new [i][0] + "(-) " + escribir_componente(oldc)
                txt += "\n"                    
    return txt
           
###################### Programa principal #####################################
# Ejecuto la utilidad lshw (http://ezix.org/project/wiki/HardwareLiSter) con
# la opción de que el resultado lo guarde en un fichero con formato xml que
# leemos posteriormente
os.system("lshw -xml>/tmp/sys.xml")
arbol = etree.parse ("/tmp/sys.xml")

# La variable string texto la vamos a usar para guardar en ella la información
# que vamos a mostrar por pantalla y vamos a mandar por correo electrónico
texto=""

# Num serie
ns = ""
# Versión IESGN: Si el equipo no tiene número de serie asignado se puede poner
# iesgn, y entonces automáticamente se asignará$
while ns == "":
    ns = raw_input("Número de serie ('iesgn' si el equipo no tiene asignado\
uno): ")
if ns == "iesgn":
    ns = "iesgn%s" % buscar_ns_iesgn()
oldequipo = ""
# Si el equipo ya está inventariado, leemos la información que tenemos actualmente
# guardada en la base de datos.
if buscar_n_serie(ns):
    oldequipo = leer_equipo(ns)
    texto += "Equipo ya inventariado\n"
else:
    texto += "Equipo nuevo\n"
texto += "Número de serie: " + ns + "\n"

# Componente CPU
# Leemos los datos de la CPU del equipo, si no la tenemos guardada anteriormente
# en la base de datos, la insrtamos
ruta = "/node/node/node[description='CPU'][product]"
columnas = ["vendor","product","slot"]
datos = obtener_datos(arbol, ruta, columnas)
idcpu = buscar_componente("idcpu", "cpu", datos)
try:
    if len(idcpu) == 0:
        insertar_componente("cpu",datos)
        idcpu=buscar_componente("idcpu","cpu",datos)
except:
    idcpu = idcpu
# Si el equipo esta ya inventariado: Borramos todos los componenetes guardados
# en la siguiente lista
if buscar_n_serie(ns):
    tablas_a_borrar = ["ram","hd","cd","red","equipo"]
    for tabla in tablas_a_borrar:
        if tabla == "equipo":
            condiciones={"num_serie":ns}
        else:
            condiciones = {"equipo_num_serie" : ns}
        borrar_componente(tabla, condiciones)

    
# Insertamos de nuevo los nuevos componentes
tablas = ["equipo","ram","hd","cd","red"]
rutas = ["/node/node[description='Motherboard']",
         "/node/node/node[description='System Memory']/node[size]",
"//node[@class='disk' and starts-with(@id,'disk') and @handle!='']/size/../serial/..",
"//node[@class='disk' and @id='cdrom' and @handle!='']/..",
"//node[@class='network' or @class='bridge']/../node[description[contains(text(),\
'Eth') or contains(text(),'Wireless')]][@handle!='']"]
columnas = [
["vendor","product","cpu_idcpu","num_serie"],
["size","clock","equipo_num_serie"],
["vendor","product","description","size","serial","equipo_num_serie"],
["vendor","product","equipo_num_serie"],
["vendor","product","serial","equipo_num_serie"]]

for i in xrange(len(tablas)):
    if tablas[i] == "equipo":
        datos = obtener_datos(arbol, rutas[i], columnas[i], [idcpu,ns])
    else:
        datos = obtener_datos(arbol, rutas[i], columnas[i], [ns])
    insertar_componente(tablas[i], datos)

# Leemos la información de los componenetes actuales
# Si el equipo ya estaba inventariado, comparamos el estado de los dos equipos 
newequipo = leer_equipo(ns)
texto += escribir_equipo(newequipo)
if oldequipo != "":
    dif = comparar_equipos(newequipo, oldequipo)
    if dif != "":
        texto += "\nDIFERENCIAS\n"
        texto += dif + "\n"
    else:
        texto += "\nNo ha habido ningún cambio desde el último inventario\n"

# Imprimimos la información y la enviamos por correo electrónico
print texto
msg = MIMEText(texto)
me = '%s' % parser.get('smtp', 'smtp_from')
you = '%s' % parser.get('smtp', 'smtp_to')
msg['Subject'] = 'Inventario equipo número de serie ' + ns
msg['From'] = me
msg['To'] = you

# Si el equipo ya esta invnetariado y ha habido diferencia, confirmo la actualización
actualizacion = True
if oldequipo != "" and dif != "":
    resp = " "
    while resp != "s" and resp != "n":
        resp = raw_input("¿Estás seguro de modificar la configuración del equipo %s (s/n)" % ns)
        if resp == "n":
            actualizacion = False
            
if actualizacion:
    db.commit()
    s = smtplib.SMTP('%s' % parser.get('smtp', 'smtp_server'))
    s.sendmail(me, [you], msg.as_string())
    s.quit()
