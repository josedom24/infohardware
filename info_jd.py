# *-* coding: utf-8 *-*
import os
import MySQLdb
from lxml import etree

db = MySQLdb.connect(host='192.168.100.254',user='root',passwd='pass',db='inventario')
cursor = db.cursor()

def buscar_n_serie(num):
    sql = "SELECT num_serie FROM equipo WHERE num_serie = %s" % num
    cursor.execute(sql)
    if cursor.fetchone():
        return True
    else:
        return False

def buscar_componente(respuesta):
    seleccion = arbol.xpath("%s/%s/text()" % (ruta,columnas[0]))[0]
    sql = "SELECT %s FROM %s WHERE %s = '%s'" % (respuesta,tabla,columnas[0],seleccion)
    for i in columnas[1:]:
        seleccion = arbol.xpath("%s/%s/text()" % (ruta,i))[0]
        sql = sql + " AND %s = '%s'" % (i,seleccion)

    tuplas = cursor.execute(sql)

    if tuplas > 0:
        asd = cursor.fetchone()[0]
        return asd
    else:

        return tuplas
        
def insertar_componente():
    num_componentes = int(arbol.xpath('count(%s)' % ruta))
    for i in xrange(num_componentes):
        sql = "INSERT INTO %s(%s" % (tabla,columnas[i])
        for j in columnas[1:]:
            sql = sql + ",%s" % j
        valor = arbol.xpath("%s/%s[%d]/text()" % (ruta,columnas[0],i+1))[0]
        sql = sql + ") VALUES ('%s'" % valor
        for j in columnas[1:]:
            valor = arbol.xpath("%s/%s[%d]/text()" % (ruta,j,i+1))[0]
            sql = sql + ",'%s'" % valor
            
    sql = sql + ")"

    cursor.execute(sql)

os.system("lshw -xml>/tmp/sys.xml")
arbol = etree.parse ("sys.xml")

#Num serie
ns = raw_input("Número de serie: ")
#datos["NS"] = ns

# Comprobamos si el equipo está en la base de datos
sql = "SELECT num_serie FROM equipo WHERE num_serie = %s" % ns
cursor.execute(sql)
if cursor.fetchone() == ns:
    print "El equipo ya está en la base de datos"
#else:
#    insertar_equipo()

#CPU
ruta = "/node/node/node[description='CPU'][product]"
tabla = "cpu"
columnas = ["vendor","product","slot"]

if buscar_componente("idcpu") != 0:
    print "La CPU ya está en la base de datos"
else:
    insertar_componente()
    idcpu = buscar_componente("idcpu")
    print idcpu

# # Placa base
# info = arbol.xpath("/node/node[description='Motherboard']")
# for i in info:
#     datos["Placa base"] = "%s %s" % (i.find("vendor").text,i.find("product").text)

# #CPU y socket
# info = arbol.xpath("/node/node/node[description='CPU']")
# datos["Procesadores"] = {}
# cont = 1
# for i in info:
#     if i.find("vendor").text != "Null":
#         datos["Procesadores"][cont] = "%s %s" % (i.find("product").text,i.find("slot").text)
#     cont += 1

# # Memoria RAM
# # info = arbol.xpath("/node/node/node[description='System Memory']/node[size]")
# # datos["Memoria"] = {}
# # cont = 1
# # for i in info:
# #     tmem = conversor(i.find("size").text)
# #     tfreq = int(i.find("clock").text)/1000/1000
# #     datos["Memoria"][cont] = "%s %d MHz" % (tmem,tfreq)
# #     cont += 1

# # HD
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
