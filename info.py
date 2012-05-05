# *-* coding: utf-8 *-*
import os
#import MySQLdb
from lxml import etree

def conversor(cant):
    unit = ['MB','GB']
    aux=int(cant)/(1024*1024)
    if aux > 1024:
        aux = "%s %s" % (str(aux/1024),unit[1])
    else:
        aux=str(tmem)+unit[0]
    return aux



def createinsert(lista,params):

    sql="insert into ordenadores("
    for i in lista:
        sql=sql+i+","
    sql=sql[0:-1]
    sql=sql+") values('"
    for i in params:
        sql=sql+i+"','"
    sql=sql[0:-2]
    sql=sql+")"

    f=open("sql.txt","w")
    f.write(sql)
    f.close

    #db=MySQLdb.connect(host='servidor',user='usuario',passwd='pass',db='basededatos')
    #cursor=db.cursor()
    #cursor.execute(sql)
    #db.commit()

# Creamos un diccionario para agregar los componentes de hardware:

datos = {}
os.system("lshw -xml>/tmp/sys.xml")
arbol = etree.parse ("/tmp/sys.xml")

#Num serie
ns = raw_input("Número de serie: ")
datos["Número de serie"] = ns

# Placa base
info = arbol.xpath("/node/node[description='Motherboard']")
for i in info:
    datos["Placa base"] = "%s %s" % (i.find("vendor").text,i.find("product").text)

#CPU y socket
info = arbol.xpath("/node/node/node[description='CPU']")
datos["Procesadores"] = {}
cont = 1
for i in info:
    if i.find("vendor").text != "Null":
        datos["Procesadores"][cont] = "%s %s" % (i.find("product").text,i.find("slot").text)
    cont += 1

# Memoria RAM
info = arbol.xpath("/node/node/node[description='System Memory']/node[size]")
datos["Memoria"] = {}
cont = 1
for i in info:
    tmem = conversor(i.find("size").text)
    tfreq = int(i.find("clock").text)/1000/1000
    datos["Memoria"][cont] = "%s %d MHz" % (tmem,tfreq)
    cont += 1

# HD
info = arbol.xpath("//node[@class='disk']/description[contains(text(),'Disk')]/../size/text()")
datos["Discos duros"] = {}
cont = 1
for i in info:
    thd = conversor(i)
    datos["Discos duros"][cont] = thd
    cont += 1

#NET
info = arbol.xpath("//node[@class='network' or @class='bridge']/../node[description[contains(text(),'Eth') or contains(text(),'Wire')]]")
datos["Interfaces de red"] = {}
cont = 1
for i in info:
    datos["Interfaces de red"][cont] = i.find("serial").text    
    cont += 1

print datos
#createinsert(lista,params)





	


