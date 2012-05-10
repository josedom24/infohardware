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

def strdatos(datos):
    txt=""
    num_componentes = len(datos);
    for i in xrange(num_componentes):
        for j in datos[i].keys():
            if j.find("id")<0 and j!="num_serie":
                   txt+=str(datos[i][j])+" - "
        txt=txt[0:-3]
        txt+="\n"
    return txt

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
        return tuplas[0][0]
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
    num_componentes = int(arbol.xpath('count(%s)' % ruta))
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


#os.system("lshw -xml>/tmp/sys.xml")
arbol = etree.parse ("/tmp/sys.xml")
texto=""
texto+="INVENTARIO - IESGN\n"

#Num serie
ns = raw_input("Número de serie: ")
if buscar_n_serie(ns):
    texto+="Equipo ya enventariado.\n"
else:
    texto+="Equipo nuevo.\n"


#CPU
ruta = "/node/node/node[description='CPU'][product]"
columnas = ["vendor","product","slot"]
datos=obtener_datos(arbol,ruta,columnas);
idcpu=buscar_componente("idcpu","cpu",datos)

if idcpu==0:
   
    insertar_componente("cpu",datos)
    idcpu=buscar_componente("idcpu","cpu",datos)

tcpu=strdatos(datos)


# Placa base

ruta = "/node/node[description='Motherboard']"
columnas = ["vendor","product","cpu_idcpu","num_serie"]
datos=obtener_datos(arbol,ruta,columnas,[idcpu,ns])

if buscar_n_serie(ns):
     # Ya existe el equipo, comprobamos que tenga la misma CPU
     cpubd=buscar_componente("cpu_idcpu","equipo",datos)
     # Si las CPU son distintas se tiene que actualizar el equipo
     if cpubd!=idcpu:
         # Obtenemos CPU actual
         rutacpu = "/node/node/node[description='CPU'][product]"
         columnascpu = ["vendor","product","slot"]
         datoscpu=obtener_datos(arbol,rutacpu,columnascpu)
         newcpu=strdatos(datoscpu)
         texto+="CPU nueva:\n"+newcpu
         # Obtenemos la CPU antigua
         sql="select * from cpu,equipo where cpu_idcpu=idcpu and num_serie='%s'" % ns
         cursor.execute(sql)
         row=cursor.fetchone()
         texto+="CPU antigua:\n%s - %s - %s\n" % (row[3],row[2],row[1])
         #Actualizamos el quipo con la nueva CPU
         datoscpu=[{"cpu_idcpu":idcpu}]
         condiciones = {"num_serie":ns}
         actualizar_componente("equipo",datoscpu,condiciones)
     # Ahora comprobamos si ha cambiado la placa base
     vendorbd=buscar_componente("vendor","equipo",datos)
     productbd=buscar_componente("product","equipo",datos)
     if vendorbd==0 or productbd==0:
         texto+="Se ha encontrado una nueva placa base\n"
         columnas = ["vendor","product"]
         datos=obtener_datos(arbol,ruta,columnas)
         condiciones = {"num_serie":ns}
         # Obtenemos la MB actual
         newplaca=strdatos(datos);
         texto+="Placa Base nueva:\n"+newplaca+"\n"
         # Obtenemos la MB antigua
         sql="select * from equipo where num_serie='%s'" % ns
         cursor.execute(sql)
         row=cursor.fetchone()
         texto+="Placa Base antigua:\n%s - %s\n" % (row[1],row[0])
         # Actualizamos la placa base
         actualizar_componente("equipo",datos,condiciones)
         

else:
    #No existe el equipo, lo insertamos
    texto+="CPU\n###\n"
    texto+="CPU:"+tcpu+"\n"
    texto+="Placa base\n##########\n"
    texto+="Placa Base:"+strdatos(datos)+"\n"
    insertar_componente("equipo",datos)
    
# Memoria RAM
ruta = "/node/node/node[description='System Memory']/node[size]"
columnas = ["equipo_num_serie"]
datos=obtener_datos(arbol,ruta,columnas,[ns])
rambd=buscar_componente("idram,clock,size","ram",datos)
if rambd!=0:
    for r in rambd:
        condiciones={"idram":r[0]}
        print r
#        #borrar_componente()
columnas = ["size","clock","equipo_num_serie"]
datos=obtener_datos(arbol,ruta,columnas,[ns])
insertar_componente("ram",datos)


# # HD

ruta = "//node[@class='disk']/description[contains(text(),'Disk')]/../size"
columnas = ["equipo_num_serie"]
datos=obtener_datos(arbol,ruta,columnas,[ns])
hdbd=buscar_componente("*","hd",datos)
if hdbd!=0:
    for r in hdbd:
        condiciones={"serial":r[0]}
        print r
#        #borrar_componente()
columnas = ["vendor","product","description","size","serial","equipo_num_serie"]
datos=obtener_datos(arbol,ruta,columnas,[ns])
insertar_componente("hd",datos)
# # info = arbol.xpath("//node[@class='disk']/description[contains(text(),'Disk')]/../size/text()")
# # datos["Discos duros"] = {}
# # cont = 1
# # for i in info:
# #     thd = conversor(i)
# #     datos["Discos duros"][cont] = thd
# #     cont += 1

# #NET
# info = arbol.xpath("//node[@class='network' or @class='bridge']/../node[description[contains(text(),'Eth') or contains(text(),'Wire')]]")
# datos["Interfaces de red"] = {}
# datos["MAC"] = {}
# cont = 1
# for i in info:
#     datos["Interfaces de red"][cont] = i.find("product").text    
#     datos["MAC"][cont] = i.find("serial").text    
#     cont += 1

# print datos
# #createinsert(lista,params)

db.commit()
print texto
