# *-* coding: utf-8 *-*
import os
import MySQLdb
from lxml import etree

db = MySQLdb.connect(host='192.168.100.254',user='root',passwd='pass',db='inventario')
cursor = db.cursor()


def conversor(cant,columna):
    aux=cant
    if columna=="size":
        unit = ['MB','GB']
        aux=int(cant)/(1024*1024)
        if aux > 1024:
            aux = "%s %s" % (str(aux/1024),unit[1])
        else:
            aux=str(tmem)+unit[0]
    if columna=="clock":
        aux="%d MHz" % (int(cant)/1000000)
    return aux

def obtener_datos(arbol,ruta,datos,adicionales=None):
    respuesta =[]
    num_componentes = int(arbol.xpath('count(%s)' % ruta))
    for i in xrange(num_componentes):
        intermedio={}
        cont_adicionales=0;
        for dato in datos:
            try:
                valor = arbol.xpath("%s/%s/text()" % (ruta,dato))[i]
            except:
                if adicionales!=None:
                       valor=adicionales[cont_adicionales]
                cont_adicionales+=1
            intermedio[dato]=valor;
        respuesta.append(intermedio)
    return respuesta


def buscar_n_serie(num):
    sql = "SELECT num_serie FROM equipo WHERE num_serie = %s" % num
    cursor.execute(sql)
    if cursor.fetchone():
        return True
    else:
        return False

def buscar_componente(respuesta,tabla,datos):
    
    sql = "SELECT %s FROM %s WHERE " % (respuesta,tabla)
    
    for k in datos[0].keys():
        sql = sql + "%s = '%s' AND " % (k,datos[0][k])
    sql=sql[0:-4]
    cursor.execute(sql)
    tuplas=cursor.fetchall()
    if len(tuplas)==0:
        return 0
    if len(tuplas)==1:
        if len(tuplas[0])==1:
            return tuplas[0][0]
        else:
            return tuplas[0]
    else:
        return tuplas
        
def insertar_componente(tabla, datos):
    num_componentes = len(datos);
    for i in xrange(num_componentes):
        sql = "INSERT INTO %s(" % tabla
        for j in datos[i].keys():
            sql = sql + "%s," % j
        sql=sql[0:-1]
        sql = sql + ") VALUES ("
        for j in datos[i].keys():
            sql = sql + "'%s'," % conversor(datos[i][j],j)
        sql=sql[0:-1]    
        sql = sql + ")"
        cursor.execute(sql)

def actualizar_componente(tabla,datos,condiciones):
    num_componentes = len(datos)
    for i in xrange(num_componentes):
        sql = "UPDATE %s SET " % tabla
        cont=0
        for j in datos[i].keys():
             sql = sql + "%s='%s'," % (j,conversor(datos[i][j],j))
        sql=sql[0:-1]
        sql = sql + " WHERE "
        for key in condiciones:
            sql=sql+"%s='%s'," % (key,condiciones[key])
        sql=sql[0:-1]
        cursor.execute(sql)

def borrar_componente(tabla,condiciones):
    sql = "DELETE FROM %s WHERE " % tabla
    for key in condiciones:
            sql=sql+"%s='%s'," % (key,condiciones[key])
    sql=sql[0:-1]
    cursor.execute(sql)

def leer_equipo(ns):
    res=[]
    idcpu=buscar_componente("cpu_idcpu","equipo",[{"num_serie":ns}])
    res.append(["cpu:",buscar_componente("vendor,product,slot","cpu",[{"idcpu":idcpu}])])
    res.append(["placa:",buscar_componente("vendor,product","equipo",[{"num_serie":ns}])])
    res.append(["ram:",buscar_componente("size,clock","ram",[{"equipo_num_serie":ns}])])
    res.append(["hd:",buscar_componente("serial,vendor,product,description,size","hd",[{"equipo_num_serie":ns}])])
    res.append(["cd:",buscar_componente("vendor,product","cd",[{"equipo_num_serie":ns}])])
    res.append(["red:",buscar_componente("serial,vendor,product","red",[{"equipo_num_serie":ns}])])
    
    return res

def escribir_equipo(datos):

    for linea in datos:
        print linea[0]
        print linea[1]

             #print dato[1]
            
#            txt=""
#            if type(dato)=="<type 'tuple'>":
#                txt=""
#                for i in xrange(len(dato)):
#                    txt+=i+" "
#                print txt
#            else:
#                txt+=dato+" "
#            print txt


                
        


#os.system("lshw -xml>/tmp/sys.xml")
arbol = etree.parse ("/tmp/sys.xml")


#Num serie
ns = raw_input("Número de serie: ")
oldequipo=""
if buscar_n_serie(ns):
    oldequipo=leer_equipo(ns)
    print "Equipo ya inventariado\nComponentes anteriores:\n\n"
    escribir_equipo(oldequipo)


#CPU
ruta = "/node/node/node[description='CPU'][product]"
columnas = ["vendor","product","slot"]
datos=obtener_datos(arbol,ruta,columnas);
idcpu=buscar_componente("idcpu","cpu",datos)

if idcpu==0:
    insertar_componente("cpu",datos)
    idcpu=buscar_componente("idcpu","cpu",datos)


# Placa base

ruta = "/node/node[description='Motherboard']"
columnas = ["vendor","product","cpu_idcpu","num_serie"]
datos=obtener_datos(arbol,ruta,columnas,[idcpu,ns])

if buscar_n_serie(ns):
     # Ya existe el equipo, comprobamos que tenga la misma CPU
     cpubd=buscar_componente("cpu_idcpu","equipo",datos)
     # Si las CPU son distintas se tiene que actualizar el equipo
     if cpubd!=idcpu:
         #Actualizamos el quipo con la nueva CPU
         datoscpu=[{"cpu_idcpu":idcpu}]
         condiciones = {"num_serie":ns}
         actualizar_componente("equipo",datoscpu,condiciones)
     # Ahora comprobamos si ha cambiado la placa base
     vendorbd=buscar_componente("vendor","equipo",datos)
     productbd=buscar_componente("product","equipo",datos)
     if vendorbd==0 or productbd==0:
         columnas = ["vendor","product"]
         datos=obtener_datos(arbol,ruta,columnas)
         # Actualizamos la placa base
         actualizar_componente("equipo",datos,condiciones)
         

else:
    #No existe el equipo, lo insertamos
    insertar_componente("equipo",datos)

# Si el equipo esta ya inventariado: Borramos todos los componenetes guardadoes en la siguiente lista
if buscar_n_serie(ns):
    tablas_a_borrar = ["ram","hd","cd","red"]
    condiciones={"equipo_num_serie":ns}
    for tabla in tablas_a_borrar:
         borrar_componente(tabla,condiciones)
    
# Insertamos los restantes componentes
tablas = ["ram","hd","cd","red"]
rutas = ["/node/node/node[description='System Memory']/node[size]",
"//node[@class='disk' and @id='disk' and @handle!='']/size/..",
"//node[@class='disk' and @id='cdrom' and @handle!='']/..",
"//node[@class='network' or @class='bridge']/../node[description[contains(text(),'Eth') or contains(text(),'Wire')]][@handle!='']"]
columnas = [["size","clock","equipo_num_serie"],["vendor","product","description","size","serial","equipo_num_serie"],["vendor","product","equipo_num_serie"],["vendor","product","serial","equipo_num_serie"]]
for i in xrange(len(tablas)):
    datos=obtener_datos(arbol,rutas[i],columnas[i],[ns])
    insertar_componente(tablas[i],datos)



db.commit()
print "Componentes actuales del equipo:\n\n"
escribir_equipo(leer_equipo(ns))
