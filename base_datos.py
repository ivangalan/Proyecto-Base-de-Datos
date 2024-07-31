import mysql.connector
import os
import subprocess
import datetime


#conexion con la base de datos
acceso_bd = {"host" : "localhost",
             "user" : "root",
             "password" : "123Surfing**",
             }

# --> Rutas

#Obtenemos la raíz de la carpeta del proyecto
carpeta_principal = os.path.dirname(__file__)

carpeta_respaldo = os.path.join(carpeta_principal, "respaldo")

class BaseDatos:
    #Conexión y cursor
    def __init__(self, **kwargs):
        self.conector = mysql.connector.connect(**kwargs)
        self.cursor = self.conector.cursor()
        self.host = kwargs["host"]
        self.usuario = kwargs["user"]
        self.contraseña = kwargs["password"]
        self.conexion_cerrada = False
        # Avisa de que se abrió la conexión con el servidor
        print("Se abrió la conexión con el servidor.")
    
    #Decoradora para el reporte de bases de datos en el servidor-------------
    def reporte_bd(funcion_parametro):
        def interno(self, nombre_bd):
            funcion_parametro(self, nombre_bd)
            BaseDatos.mostrar_bd(self)
        return interno
    
    # Decorador para el cierre del cursor y la base de datos--------------------
    def conexion(funcion_parametro):
        def interno(self, *args, **kwargs):
            try:
                if self.conexion_cerrada:
                    self.conector = mysql.connector.connect(
                        host = self.host,
                        user = self.usuario,
                        password = self.contraseña
                    )
                    self.cursor = self.conector.cursor()
                    self.conexion_cerrada = False
                    print("Se abrió la conexión con el servidor.")
                # Se llama a la función externa
                funcion_parametro(self, *args, **kwargs)
            except Exception as e:
                print(f"Ocurrió un error: {e}")
            finally:
                if self.conexion_cerrada:
                    pass
                else:
                    # Cerramos el cursor y la conexión
                    self.cursor.close()
                    self.conector.close()
                    print("Se cerró la conexión con el servidor.")
                    self.conexion_cerrada = True
            return self.resultado
        return interno
    
    # Decorador para comprobar si existe una base de datos-----------------
    def comprueba_bd(funcion_parametro):
        def interno(self, nombre_bd, *args):
            # Verifica si la base de datos existe en el servidor
            sql = f"SHOW DATABASES LIKE '{nombre_bd}'"
            self.cursor.execute(sql)
            resultado = self.cursor.fetchone()
            
            # Si la base de datos no existe, muestra un mensaje de error
            if not resultado:
                print(f'La base de datos {nombre_bd} no existe.')
                return
            # Ejecuta la función decorada y devuelve el resultado
            return funcion_parametro(self, nombre_bd, *args)
        return interno
    
    
    #Consultas SQL 
    @conexion   
    def consulta(self, sql):
        self.cursor.execute(sql)
        self.resultado = (self.cursor.fetchall())
        
    @conexion
    def mostrar_bd(self):
        try:
            # Se informa de que se están obteniendo las bases de datos
            print("Aquí tienes el listado de las bases de datos del servidor:")
            # Realiza la consulta para mostrar las bases de datos
            self.cursor.execute("SHOW DATABASES")
            self.resultado = self.cursor.fetchall()
            # Recorre los resultados y los muestra por pantalla
            for bd in self.resultado:
                print(f"-{bd[0]}.")
        except:  # noqa: E722
            # Si ocurre una excepción, se avisa en la consola
            print("No se pudieron obtener las bases de datos. Comprueba la conexión con el servidor.")
             
    #Eliminar bases de datos
    @conexion
    @reporte_bd
    @comprueba_bd
    def eliminar_bd(self, nombre_bd):
        # Realiza la consulta para eliminar la base de datos
        self.cursor.execute(f"DROP DATABASE {nombre_bd}")
        print(f"Se eliminó la base de datos {nombre_bd} correctamente.")
    
    #Crear bases de datos
    @conexion
    @reporte_bd
    def crear_bd(self, nombre_bd):
        try:
            self.cursor.execute(f"CREATE DATABASE IF NOT EXISTS {nombre_bd}")
            print(f"Se creó la base de datos {nombre_bd} o ya estaba creada.")
        except:  # noqa: E722
            print(f"Ocurrió un error al intentar crear la base de datos {nombre_bd}.")
    
    #Crear backups de bases de datos
    @conexion
    @comprueba_bd
    def copia_bd(self, nombre_bd):
        #Obtiene la hora y fecha actuales
        self.fecha_hora = datetime.datetime.now().strftime("%Y-%m-%d %H-%M-%S")
            
        #Se crea la copia de seguridad
        with open(f'{carpeta_respaldo}/{nombre_bd}_{self.fecha_hora}.sql', 'w') as out:
            subprocess.Popen(f'"C:/Program Files/MySQL/MySQL Workbench 8.0/"mysqldump --user=root --password={self.contrasena} --databases {nombre_bd}', shell=True, stdout=out)
        print("Se creó la copia correctamente.")
    
    @conexion
    @comprueba_bd
    def crear_tabla(self, nombre_bd, nombre_tabla, columnas):
        try:
            #String para guardar el string con las columnas y tipos de datos
            columnas_string = ""
            #Se itera la lista que se le pasa como argumento (cada diccionario)
            for columna in columnas:
                #formamos el string con nombre, tipo y longitud
                columnas_string += f"{columna['name']} {columna['type']}({columna['length']})"
                #Si es clave primaria, auto_increment o no admite valores nulos, lo añade al string
                if columna['primary_key']:
                    columnas_string += " PRIMARY KEY"
                if columna['auto_increment']:
                    columnas_string += " AUTO_INCREMENT"
                if columna['not_null']:
                    columnas_string += " NOT NULL"
                #Hace un salto de línea después de cada diccionario    
                columnas_string += ",\n"
            #Elimina al final del string el salto de línea y la coma    
            columnas_string = columnas_string[:-2]
            #Le indica que base de datos utilizar
            self.cursor.execute(f"USE {nombre_bd}")
            #Se crea la tabla juntando la instrucción SQL con el string generado
            sql = f"CREATE TABLE {nombre_tabla} ({columnas_string});"
            #Se ejecuta la instrucción
            self.cursor.execute(sql)
            #Se hace efectiva
            self.conector.commit()
            # Se informa de que la creación se ha efectuado correctamente.
            print("Se creó la tabla correctamente.")
        except:  # noqa: E722
            print("Ocurrió un error al intentar crear la tabla.")
            
    @conexion
    @comprueba_bd    
    def eliminar_tabla(self, nombre_bd, nombre_tabla):
        try:
            self.cursor.execute(f"USE {nombre_bd}")
            self.cursor.execute(f"DROP TABLE {nombre_tabla}")
            print(f"Tabla '{nombre_tabla}' eliminada correctamente de la base de datos {nombre_bd}.")
        except:  # noqa: E722
            print(f"No se pudo eliminar la tabla '{nombre_tabla}' de la base de datos '{nombre_bd}'.")
            
    # Método para mostrar las tablas de una base de datos
    @conexion
    @comprueba_bd  
    def mostrar_tablas(self, nombre_bd):
        # Se selecciona la base de datos
        self.cursor.execute(f"USE {nombre_bd};")
        # Se informa de que se están obteniendo las tablas
        print("Aquí tienes el listado de las tablas de la base de datos:")
        # Realiza la consulta para mostrar las tablas de la base de datos actual
        self.cursor.execute("SHOW TABLES")
        resultado = self.cursor.fetchall()
        if not resultado:
            print("No hay tablas en esta base de datos.")
            return
        # Recorre los resultados y los muestra por pantalla
        for tabla in resultado:
            print(f"-{tabla[0]}.")
            
    @conexion
    @comprueba_bd
    def mostrar_columnas(self, nombre_bd, nombre_tabla):
        # Establece la base de datos actual
        self.cursor.execute(f"USE {nombre_bd}")
        try:
            # Realiza la consulta para mostrar las columnas de la tabla especificada
            self.cursor.execute(f"SHOW COLUMNS FROM {nombre_tabla}")
            resultado = self.cursor.fetchall()
            
            # Se informa de que se están obteniendo las columnas
            print(f"Aquí tienes el listado de las columnas de la tabla '{nombre_tabla}':")
            # Recorre los resultados y los muestra por pantalla
            for columna in resultado:
                not_null = "No admite valores nulos." if columna[2] == "NO" else "Admite valores nulos."
                primary_key = "Es clave primaria." if columna[3] == "PRI" else ""
                foreign_key = "Es clave externa." if columna[3] == "MUL" else ""
                auto_increment = "Es autoincrementable." if columna[5] == "auto_increment" else ""
                print(f"-{columna[0]} ({columna[1]}) {not_null} {primary_key} {foreign_key} {auto_increment}")
        except:  # noqa: E722
            print("Ocurrió un error. Comprueba el nombre de la tabla.")

     

   
    
        # Método para insertar registros en una tabla
    @conexion
    @comprueba_bd
    def insertar_registro(self, nombre_bd, nombre_tabla, registro):
        try:
            self.cursor.execute(f"USE {nombre_bd}")

            if not registro:  # Si la lista está vacía
                print("La lista de registro está vacía.")
                return

            # Obtener las columnas y los valores de cada diccionario
            columnas = []
            valores = []
            for registro in registro:
                columnas.extend(registro.keys())
                valores.extend(registro.values())

            # Convertir las columnas y los valores a strings
            columnas_string = ''
            for columna in columnas:
                columnas_string += f"{columna}, "
            columnas_string = columnas_string[:-2]  # Quitar la última coma y espacio

            valores_string = ''
            for valor in valores:
                valores_string += f"'{valor}', "
            valores_string = valores_string[:-2]  # Quitar la última coma y espacio

            # Crear la instrucción de inserción
            sql = f"INSERT INTO {nombre_tabla} ({columnas_string}) VALUES ({valores_string})"
            self.cursor.execute(sql)
            self.conector.commit()
            print("Registro añadido a la tabla.")
        except mysql.connector.Error as e:
            print(f"Error{e}")
        except Exception as e:
            print(f"Ocurrió un error inesperado: {e}")


    @conexion
    def eliminar_registro(self, nombre_bd, nombre_tabla, condiciones):
        try:
            self.cursor.execute(f"USE {nombre_bd}")
            self.cursor.execute(f"DELETE FROM {nombre_tabla} WHERE {condiciones}")
            self.conector.commit()
            print("Registros eliminados.")

            if not nombre_tabla:
                print(f"El registro {nombre_tabla} no se ecuentra en la base datos.\n")
        except:  # noqa: E722
            print("Error al intentar borrar el registro en la tabla.")


    @conexion   
    def eliminar_todos_registros(self, nombre_bd, nombre_tabla):
        try:
            self.cursor.execute(f"USE {nombre_bd}")
            self.cursor.execute(f"DELETE FROM {nombre_tabla} ")#si omitimos WHERE se borra la tabla entera
            self.conector.commit()
            print("Registros eliminados.")

            if not nombre_tabla:
                print(f"El registro {nombre_tabla} no se ecuentra en la base datos.\n")
        except:  # noqa: E722
            print("Error al intentar borrar el registro en la tabla.")


    @conexion
    def vaciar_tabla(self, nombre_bd, nombre_tabla):
        try:
            self.cursor.execute(f"USE {nombre_bd}")
            self.cursor.execute(f"TRUNCATE TABLE {nombre_tabla} ")#si omitimos WHERE se borra la tabla entera
            self.conector.commit()
            print("Todos los registros eliminados.")

            if not nombre_tabla:
                print(f"El registro {nombre_tabla} no se ecuentra en la base datos.\n")
        except:  # noqa: E722
            print("Error al intentar borrar los registros en la tabla.")


    @conexion
    def actualizar_registro(self, nombre_bd, nombre_tabla, columna, condiciones):
        try:
            # Selecciona la base de datos
            self.cursor.execute(f"USE {nombre_bd}")

            # Crear la funcion de actualizacion
            self.cursor.execute(f"UPDATE {nombre_tabla} SET {columna} WHERE {condiciones}")
            
            # Se ejecuta la funcion de actualizacion y se hace efectiva
            self.conector.commit()
            print("El registro se actualizó correctamente.")
        
        except:  # noqa: E722
            print("Ha ocurrido un error al actualizar el registro.")
