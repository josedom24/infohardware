# *-* coding: utf-8 *-*
import os
import MySQLdb
from lxml import etree

db = MySQLdb.connect(host='192.168.100.254',user='root',passwd='pass',db='inventario')
cursor = db.cursor()

def conversor(cant):
    unit = ['MB','GB']
    aux=int(cant)/(1024*1024)
    if aux > 1024:
        aux = "%s %s" % (str(aux/1024),unit[1])
    else:
        aux=str(tmem)+unit[0]
    return aux

def buscar_n_serie(num):
    sql = "SELECT num_serie FROM equipo WHERE num_serie = %s" % num
    cursor.execute(sql)
    if cursor.fetchone():
        return True
    else:
        return False

def buscar_componente(respuesta):
    try:
        seleccion = arbol.xpath("%s/%s/text()" % (ruta,columnas[0]))[0]
    except:
        seleccion=valores[0]

    sql = "SELECT %s FROM %s WHERE %s = '%s'" % (respuesta,tabla,columnas[0],seleccion)
    cont=1
    for i in columnas[1:]:
        try:
            seleccion = arbol.xpath("%s/%s/text()" % (ruta,i))[0]
        except:
            seleccion = valores[cont]
        cont=cont+1
        sql = sql + " AND %s = '%s'" % (i,seleccion)
    print sql
    tuplas = cursor.execute(sql)

    if tuplas > 0:
        asd = cursor.fetchone()[0]
        return asd
    else:

        return tuplas
        
def insertar_componente():
    num_componentes = int(arbol.xpath('count(%s)' % ruta))
    for i in xrange(num_componentes):
        sql = "INSERT INTO %s(%s" % (tabla,columnas[0])
        for j in columnas[1:]:
            sql = sql + ",%s" % j
        try:
            #valor = arbol.xpath("%s/%s[%d]/text()" % (ruta,columnas[0],i+1))[0]
            valor = arbol.xpath("%s/%s/text()" % (ruta,columnas[0]))[i]
            
            print valor
        except:
        #Si hemos indicado un valor para esa columna en el array valores se toma ese
            if valores[0]!="": 
                valor=valores[0]
        if columnas[0]=="size":
            valor=conversor(valor)
        if columnas[0]=="clock":
             valor="%d MHz" % (int(valor)/1000000)
        sql = sql + ") VALUES ('%s'" % valor
        cont=1
        for j in columnas[1:]:
            try:
                #valor = arbol.xpath("%s/%s[%d]/text()" % (ruta,j,i+1))[0]
                valor = arbol.xpath("%s/%s/text()" % (ruta,j))[i]
            except:
                if valores[cont]!="": 
                    valor=valores[cont]
            cont=cont+1
            if j=="size":
                    valor=conversor(valor)
            if j=="clock":
                valor="%d MHz" % (int(valor)/1000000)
            sql = sql + ",'%s'" % valor
            
        sql = sql + ")"
        print sql
        cursor.execute(sql)

def actualizar_componente():
    num_componentes = int(arbol.xpath('count(%s)' % ruta))
    for i in xrange(num_componentes):
        try:
            valor = arbol.xpath("%s/%s[%d]/text()" % (ruta,columnas[0],i+1))[0]
        except:
        #Si hemos indicado un valor para esa columna en el array valores se toma ese
            if valores[0]!="":
                valor=valores[0]
        sql = "UPDATE %s SET %s='%s'" % (tabla,columnas[0],valor)

        cont=1
        for j in columnas[1:]:
            try:
                #valor = arbol.xpath("%s/%s[%d]/text()" % (ruta,j,i+1))[0]
                valor = arbol.xpath("%s/%s/text()" % (ruta,j))[i]
                
            except:
                if valores[cont]!="":
                    valor=valores[cont]
            cont=cont+1
            if j=="size":
                    valor=conversor(valor)
            if j=="clock":
                valor="%d MHz" % (int(valor)/1000000)
            sql = sql + ",%s='%s'" % (j,valor)
    
        sql = sql + " WHERE "
        for key in condiciones:
            sql=sql+"%s='%s'," % (key,condiciones[key])
        sql=sql[0:-1]
        print sql
        cursor.execute(sql)

#os.system("lshw -xml>/tmp/sys.xml")
arbol = etree.parse ("/tmp/sys.xml")

#Num serie
ns = raw_input("Número de serie: ")


#CPU
ruta = "/node/node/node[description='CPU'][product]"
tabla = "cpu"
columnas = ["vendor","product","slot"]

idcpu=buscar_componente("idcpu")
if idcpu!= 0:
    print "La CPU ya está en la base de datos"
else:
    insertar_componente()
    idcpu = buscar_componente("idcpu")
    print "Se ha incertado una nueva CPU %d" % idcpu



# Placa base

ruta = "/node/node[description='Motherboard']"
tabla = "equipo"
columnas = ["vendor","product","cpu_idcpu","num_serie"]
valores = ["","",idcpu,ns]

if buscar_n_serie(ns):
     # Ya existe el equipo, comprobamos que tenga la misma CPU
     cpubd=buscar_componente("cpu_idcpu")
     # Si las CPU son distintas se tiene que actualizar el equipo
     if cpubd!=idcpu:
         print ""
         columnas = ["cpu_idcpu"]
         valores = [idcpu]
         condiciones = {"num_serie":ns}
         actualizar_componente()
     # Ahora comprobamos si ha cambiado la placa base
     columnas = ["vendor","product","cpu_idcpu","num_serie"]
     valores = ["","",idcpu,ns]
     vendorbd=buscar_componente("vendor")
     productbd=buscar_componente("product")
     if vendorbd==0 or productbd==0:
         print "Se ha encontrado una nueva placa base"
         columnas = ["vendor","producto"]
         valores = ["",""]
         condiciones = {"num_serie":ns}
         actualizar_componente()

else:
    #No existe el equipo, lo insertamos
    insertar_componente()
    
# Memoria RAM
ruta = "/node/node/node[description='System Memory']/node[size]"
tabla = "ram"
columnas = ["equipo_num_serie"]
valores = [ns]
rambd=buscar_componente("idram")
if rambd!=0:
    for r in rambd:
        condiciones={"idram":r}
        print condiciones
        #borrar_componente()
columnas = ["size","clock","equipo_num_serie"]
valores = ["","",ns]
insertar_componente()

#insertar_componente()

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
