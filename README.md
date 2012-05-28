infohardware
============

Programa escrito en python que nos permite leer la información de los componentes hardware de un ordenador. Los siguientes datos que se leen se guardan en una base de datos cuyo modelo entidad-relación se puede consultar en el fichero inventario.mwb. El script para crear la base de datos mysql lo puedes consultar en el fichero inventario.sql

Los datos extraídos son:

* CPU: Proveedor, producto y slot.
* Placa Base: Proveedor y producto.
* RAM: Para cada módulo de memoria, tamaño y frecuencia.
* Discos duros: Para cada disco, número de serie, proveedor, producto, descripción y tamaño.
* CD / DVD: Para cada unidad, proveedor y producto.
* Red: De cada tarjeta de red, MAC, proveedor y producto.

Instalación
===========

El programa infohardware utiliza la utilidad lshw (http://ezix.org/project/wiki/HardwareLiSter) y las librerías python de MySQL y gestión de ficheros xml. Por lo tanto, para que funcione en Debian es necesario tener instalado los siguientes paquetes:

apt-get install lshw python-mysqldb python-lxml

Configuración
=============

La configuración del programa se realiza en el fichero infohardware.cfg donde hay que indicar los siguientes datos:

* Información de acceso a la base de datos (servidor, usuario y nombre de la base de datos).
* Información sobre el envío de correo electrónico (Servidor de correo, dirección de donde se manda y dirección del destinatario).

NOTA: En la versión actual no es necesario indicar la contraseña de acceso a la base de datos, ya que se pide por teclado. Sería muy fácil cambiar esta característica en el código para que la contraseña se indicará en el fichero de configuración.

Funcionamiento
==============

1) Cuando se ejecuta el programa se nos pide la contraseña de acceso a MySQL (esto es una medida de seguridad, si el entorno de utilización del programa es seguro, se puede modificar para que dicha contraseña se guarde en el fichero de configuración)

2) Se nos pide por teclado el número de serie del equipo, con ello determinamos si el equipo es nuevo o ya se ha inventariado con anterioridad. En la versión actual, si el equipo no tiene asignado un número de serie, se puede indicar "iesgn" con lo que se asigna un número de serie de la forma "iesgn y cuatro dígitos", esta característica es fácilmente modificable en el código.

3) Si el equipo es nuevo se guarda en la base de datos los datos del equipo.

4) Si el equipo ya ha sido inventariado, se informa si ha habido alguna diferencia de configuración. Si es así se pide confirmación para actualizar la información.

5) El programa mandará un correo electrónico con la información obtenida a la dirección que hayamos indicado en la configuración.
