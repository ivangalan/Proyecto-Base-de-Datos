import tkinter as tk
import customtkinter as ctk
import os
from PIL import Image
import base_datos as sqlbd

from CTkMessagebox import CTkMessagebox

# Configuraciones globales
# --> Rutas
# Obtenemos carpeta principal
carpeta_principal = os.path.dirname(__file__)
# .\proyecto-bd\bd\interfaz
carpeta_imagenes = os.path.join(carpeta_principal, "imagenes")
# .proyecto-bd\bd\interfaz\imagenes

# Objeto para manejar bases de datos SQL
base_datos = sqlbd.BaseDatos(**sqlbd.acceso_bd)

# Modos de color y tema
ctk.set_appearance_mode("System")
ctk.set_default_color_theme("green")

# Configuracion de fuentes
fuente_widgets = ('raleway', 16, tk.font.BOLD)

class Login:
    def __init__(self):
        # Creación de la ventana principal
        self.root = ctk.CTk() # Instancia
        self.root.title("NOT ALL IS BINARY!") # Título
        self.root.iconbitmap(os.path.join(carpeta_imagenes, "logo.ico")) # Inserccion logo
        self.root.geometry("400x450") # Tamaño ventana
        self.root.resizable (False, False) # Redimensionable
        self.root.eval('tk::PlaceWindow . center')

        # Contenido de la ventana principal
        # Logo
        logo = ctk.CTkImage((Image.open(os.path.join(carpeta_imagenes, "logo2.jpg"))), size = (200, 200)) 
        # Etiqueta para mostrar la imagen
        etiqueta = ctk.CTkLabel(master = self.root, image=logo, text= "")
        etiqueta.pack(pady = 20) # Para dejar margen con las letras

        # Campos de texto
        # Usuario
        ctk.CTkLabel(self.root, text="Usuario").pack()
        self.usuario = ctk.CTkEntry(self.root)
        self.usuario.insert(0, "Ej:Kuki")
        self.usuario.bind("<Button-1>", lambda e: self.usuario.delete(0, "end"))
        self.usuario.pack()

        # Contraseña
        ctk.CTkLabel(self.root, text="Contraseña").pack()
        self.contraseña = ctk.CTkEntry(self.root)
        self.contraseña.insert(0, "*******")
        self.contraseña.bind("<Button-1>", lambda e: self.contraseña.delete(0, "end"))
        self.contraseña.pack()

        # Botón de envío
        ctk.CTkButton(self.root, text="Entrar", command=self.validar).pack(pady = 20)

         # Bucle de ejecución
        self.root.mainloop()   

       
    # Funcion para validar el login
    def validar (self):
        obtener_usuario = self.usuario.get()
        obtener_contraseña = self.contraseña.get()

        # Verifica si el valor que tiene el usuario y contraseña o ambos son correctos
        if obtener_usuario == sqlbd.acceso_bd["user"] or obtener_contraseña == sqlbd.acceso_bd["password"]:
            # En caso de tener ya un elemento "info_login" creado lo elimina
            if hasattr (self, "info_login"):
                self.info_login.configure(text="Usuario o contraseña incorrectos.")
            # Crea la etiqueta siempre que el login sea incorrecto
            else:
                self.info_login = ctk.CTkLabel(self.root, text="Usuario o contraseña incorrectos.")
                self.info_login.pack()
        else:
            # En caso de tener ya un elemento "info_login" creado lo elimina
            if hasattr (self, "info_login"):
                self.info_login.configure(text=f"Hola {obtener_usuario}. Espere unos instantes...")
                # Crear esta etiqueta si es correcto
            else:
                self.info_login =  ctk.CTkLabel(self.root, text=f"Hola {obtener_usuario}. Espere unos instantes...")
                self.info_login.pack()

            #Destruccion de ventana en caso de que sea correcto el login
            self.root.destroy()
            ventana_opciones = VentanaOpciones()

class FuncionesPrograma:
    def ventana_consultas(self):
        ventana = ctk.CTkToplevel()
        ventana.title("Consultas SQL")
        ventana.grab_set()
        # Crea el frame y añadelo a la ventana
        marco = ctk.CTkFrame(ventana)
        marco.pack(padx=10, pady=10)
        # Crea un Entry y establece el tamaño
        self.entrada = ctk.CTkEntry(marco, width=300)
        # Establece la pesonalizacon de la fuente
        self.entrada.configure(font=fuente_widgets)
        # Posiciona el entry
        self.entrada.grid(row=0,column=0, pady = 10)


        # Método para utilizar la lógica del metodo consultas de base_datos
        def procesar_datos():
            try:
                #borra el contenido de la caja de resultados
                self.texto.delete(1.0, "end")
                # Obtiene el contenido del entry
                datos = self.entrada.get()
                # Llama al método base_datos.consulta() con los datoa como argumento
                resultado = base_datos.consulta(datos)
                for registro in resultado:
                    
                    self.texto.insert('end', registro)
                    self.texto.insert('end', '\n')

                # Actualiza el contador de numero de registros devueltos
                numero_registros = len(resultado)
                self.contador_registros.configure(text= f"Registros devueltos: {numero_registros}")
            except Exception:
                self.contador_registros.configure(text= "Ha ocurrido un error al introducir la instrucción.")
                CTkMessagebox(title="Error!", message="Por favor, revise la instrucción SQL", icon="cancel")
        # Crea el boton de envío
        boton_envio = ctk.CTkButton(marco,
                                    text="Enviar",
                                    command=lambda : procesar_datos())
        boton_envio.grid(row=0, column=1)
        # Crea boton de borrado
        boton_borrado = ctk.CTkButton(marco,
                                    text="Borrar",
                                    command=lambda : self.limpiar_texto())
        # Posiciona el boton a la derecha del entry
        boton_borrado.grid(row=0, column=2)

        # Crea el widget de texto
        self.texto = ctk.CTkTextbox(marco,
                                    width=610,
                                    height=300)
        # Colocar el widget debajo del entry y el boton usando grid
        self.texto.grid(row=1, column=0, columnspan=3, pady=10, padx=10)

        # Agrega un nuevo widget label para contabilizar los resultados que devuelve
  
        self.contador_registros = ctk.CTkLabel(marco, text= "Esperando una consulta...")
        self.contador_registros.grid(row=2, column=0, columnspan=3, pady=10, padx=10)


    def limpiar_texto(self):
        # 1.0 es borrar desde línea 1 columna 0, las lineas se cuentan desde el 1 y las columnas desde el cero
        self.texto.delete('1.0', "end")
   

    def ventana_mostrar_bases_datos(self):
        ventana = ctk.CTkToplevel()
        ventana.title("Bases de datos del servidor.")
        ventana.geometry("400x565")
        ventana.resizable (0,0)
        # Pone el foco en la ventana
        ventana.grab_set()
        
        
        # Crea marco
        marco = ctk.CTkFrame(ventana)
        marco.pack(pady = 10, padx = 10)
        # Crea etiqueta informativa de las bases de datos
        ctk.CTkLabel(marco, text="Listado de las bases de datos",
        font=fuente_widgets).pack(pady=10,padx=10)

        # Agregar un campo de entrada para la busqueda
        self.busqueda_control = tk.StringVar()
        # Crea la entrada de texto para búsquedas
        ctk.CTkEntry(marco,
                     font=fuente_widgets,
                     textvariable=self.busqueda_control,
                     width=300).pack(padx=10)
        # Crea el textbox
        self.texto = ctk.CTkTextbox(marco,
                                    font=fuente_widgets,
                                    width=300,
                                    height=300)
        self.texto.pack(pady=10,padx=10)
        # Crea etiqueta numero de resultados
        self.resultados_label = ctk.CTkLabel(marco,
                                       text="",
                                       font=fuente_widgets)
        self.resultados_label.pack(padx=10, pady=10)
        
        
        # Crear funcion de actualizacion
        def actualizar ():
            # Se establece el valor de la variable de control a cero
            self.busqueda_control.set("")
            # Se elimina el contenido de la caja de resultados
            self.texto.delete("1.0", "end")
            # Se realiza una llamada al método mostrar_bd (SHOW DATA BASES) y se guarda en resultado
            resultado = base_datos.mostrar_bd()
            # Se itera el resultado y se presenta linea a linea en la caja de texto
            for bd in resultado:
                self.texto.insert("end", f"- {bd[0]}\n")
            # Actualiza la etiqueta con el número de resultados
            numero_resultado = len(resultado)
            if numero_resultado == 1:
                self.resultados_label.configure(text=f"Se encontraron {numero_resultado} resultados.")
            else:
                self.resultados_label.configure(text=f"Se encontró {numero_resultado}resultado.")
            
        # Funcion interna de búsqueda para filtrar resultados
        def buscar():
            # Eliminar contenido de la caja de texto
            self.texto.delete("1.0", "end") 
            # Realiza la llamada al metodo mostrar_bd (SHOW DATABASES) y se guarda el resultado
            resultado = base_datos.mostrar_bd()
            # Se obtiene el valor string de la variable de control(lo que se ve en el ENTRY)
            busqueda = self.busqueda_control.get().lower()
            # Crea una lista donde almacenar los resultados filtrados
            resultado_filtrado = []
            # Se itera la tupla fetchall que devuelve mostrar_bd
            for bd in resultado:
                # Si lo que tiene la StringVar coincide con la búsqueda
                if busqueda in bd[0]:
                    resultado_filtrado.append(bd)
            """Esta última iteración se puede expresar también...(compresión de listas)
            resultado_filtrado = [bd for bd in resultado if busqueda in bd[0].lower()]"""
            # Se itera la lista ya filtrada, con lo que se insertan los valores en la caja de texto
            for bd in resultado_filtrado:
                self.texto.insert("end", f"- {bd[0]}\n")
            # Actualiza la etiqueta con el numero de resultados
            numero_resultados = len(resultado_filtrado)
            if numero_resultados == 1:
                self.resultados_label.configure(text=f"Se encontraron {numero_resultados} resultados.")
            else:
                self.resultados_label.configure(text=f"Se encontró {numero_resultados} resultado.")
        # Crea botones buscar 
        boton_enviar = ctk.CTkButton(marco,
                                     text="Buscar",
                                     command=buscar)
        boton_enviar.pack(padx=10, pady=10)
        # Crea boton actualizar resultado
        boton_actualizar = ctk.CTkButton(marco, 
                                         text="Actualizar", 
                                         command=actualizar)
        boton_actualizar.pack(padx=10,pady=10)
        
        actualizar()

    def ventana_eliminar_bases_datos(self):
        ventana = ctk.CTkToplevel()
        ventana.title("Ventana para eliminar bases de datos")
        ventana.geometry("400x200")

    def ventana_crear_bases_datos(self):
        ventana = ctk.CTkToplevel()
        ventana.title("Ventana para crear bases de datos")
        ventana.geometry("400x200")

    def ventana_crear_respaldos(self):
        ventana = ctk.CTkToplevel()
        ventana.title("Ventana para crear respaldos")
        ventana.geometry("400x200")

    def ventana_crear_tablas(self):
        ventana = ctk.CTkToplevel()
        ventana.title("Ventana para crear tablas")
        ventana.geometry("400x200")

    def ventana_eliminar_tablas(self):
        ventana = ctk.CTkToplevel()
        ventana.title("Ventana para eliminar tablas")
        ventana.geometry("400x200")

    def ventana_mostrar_tablas(self):
        ventana = ctk.CTkToplevel()
        ventana.title("Ventana para mostrar tablas")
        ventana.geometry("400x200")

    def ventana_mostrar_columnas(self):
        ventana = ctk.CTkToplevel()
        ventana.title("Ventana para mostrar columnas de una tabla")
        ventana.geometry("400x200")

    def ventana_insertar_registros(self):
        ventana = ctk.CTkToplevel()
        ventana.title("Ventana para insertar registros")
        ventana.geometry("400x200")

    def ventana_eliminar_registros(self):
        ventana = ctk.CTkToplevel()
        ventana.title("Ventana para eliminar registros")
        ventana.geometry("400x200")

    def ventana_vaciar_tablas(self):
        ventana = ctk.CTkToplevel()
        ventana.title("Ventana para vaciar tablas")
        ventana.geometry("400x200")

    def ventana_actualizar_tablas(self):
        ventana = ctk.CTkToplevel()
        ventana.title("Ventana para actualizar tablas")
        ventana.geometry("400x200")

objeto_funciones = FuncionesPrograma()


class VentanaOpciones:
    # Diccionario para los botones
    botones = {'Consulta SQL': objeto_funciones.ventana_consultas, 
               'Mostrar Bases de Datos': objeto_funciones.ventana_mostrar_bases_datos,
               'Eliminar Bases de Datos': objeto_funciones.ventana_eliminar_bases_datos,
               'Crear Bases de Datos': objeto_funciones.ventana_crear_bases_datos, 
               'Crear Respaldos': objeto_funciones.ventana_crear_respaldos,
               'Crear Tablas': objeto_funciones.ventana_crear_tablas,
               'Eliminar Tablas': objeto_funciones.ventana_eliminar_tablas,
               'Mostrar Tablas': objeto_funciones.ventana_mostrar_tablas,
               'Mostrar Columnas': objeto_funciones.ventana_mostrar_columnas,
               'Insertar Registros': objeto_funciones.ventana_insertar_registros,
               'Eliminar Registros': objeto_funciones.ventana_eliminar_registros,
               'Vaciar Tablas': objeto_funciones.ventana_vaciar_tablas,
               'Actualizar Registros': objeto_funciones.ventana_actualizar_tablas
               }
    def __init__(self):
        # Se crea la ventana de CustomTkinter
        self.root = ctk.CTk()
        # Se le da un título
        self.root.title("Opciones para trabajar con bases de datos.")
    
        # Marco para contener el menú superior
        menu_frame = ctk.CTkFrame(self.root)
        menu_frame.pack(side='top', fill='x')

        # Se crea el botón de Menú
        archivo = tk.Menubutton(menu_frame, 
                                text='Archivo', 
                                background='#2b2b2b', 
                                foreground='white', 
                                activeforeground='black', 
                                activebackground='gray52')
        
        # Se crea el botón de Menú
        edicion = tk.Menubutton(menu_frame, 
                                text='Edición', 
                                background='#2b2b2b', 
                                foreground='white', 
                                activeforeground='black', 
                                activebackground='gray52')
        
        # Se crea el menú
        menu_archivo = tk.Menu(archivo, tearoff=0)
        # Se crea el menú
        menu_edicion = tk.Menu(edicion, tearoff=0)

        # Añade una opción al menú desplegable
        menu_archivo.add_command(label='Imprimir Saludo', 
                                 command=lambda: print('Hello PC Master!'), 
                                 background='#2b2b2b', 
                                 foreground='white', 
                                 activeforeground='black', 
                                 activebackground='gray52')
        
        
        # Crea un nuevo menú para la cascada
        cascada = tk.Menubutton(menu_edicion, 
                                text='Cascada', 
                                background='black', 
                                foreground='white', 
                                activeforeground='black', 
                                activebackground='gray52')
        
        # Se crea el menú
        menu_cascada = tk.Menu(cascada, tearoff=0)
        cascada.config(menu=menu_cascada)
        
        # Se crea una cascada dentro del menu de edición
        menu_edicion.add_cascade(label="Opciones", menu=menu_cascada, 
                                 background='#2b2b2b', 
                                 foreground='white', 
                                 activeforeground='black', 
                                 activebackground='gray52')
    
        # Agrega opciones a la cascada
        menu_cascada.add_command(label="Opción 1", 
                                 command=lambda: print("Opción 1 seleccionada"), 
                                 background='#2b2b2b', 
                                 foreground='white', 
                                 activeforeground='black', 
                                 activebackground='gray52')
        
        menu_cascada.add_command(label="Opción 2", 
                                 command=lambda: print("Opción 2 seleccionada"), 
                                 background='#2b2b2b', 
                                 foreground='white', 
                                 activeforeground='black', 
                                 activebackground='gray52')
        
        menu_cascada.add_command(label="Opción 3", 
                                 command=lambda: print("Opción 3 seleccionada"), 
                                 background='#2b2b2b', 
                                 foreground='white', 
                                 activeforeground='black', 
                                 activebackground='gray52')
        
        # Asigna el menú desplegable al Menubutton
        archivo.config(menu=menu_archivo)
        # Posiciona el Menubutton dentro del Frame
        archivo.pack(side='left')
        
        # Asigna el menú desplegable al Menubutton
        edicion.config(menu=menu_edicion)
        # Posiciona el Menubutton dentro del Frame
        edicion.pack(side='left')
        
        # Asigna el menú desplegable al Menubutton
        cascada.config(menu=menu_cascada)
        
        # Crea un Frame para contener los botones de la ventana
        frame_botones = ctk.CTkFrame(self.root)
        # Posiciona el Frame debajo del menú
        frame_botones.pack(side='top', fill='x')

        # Contador para la posición de los botones
        contador = 0

        # Valor de elementos por fila
        elementos_fila = 3

        # Crea los botones y establece su texto
        for texto_boton in self.botones:
            boton = ctk.CTkButton(
                master=frame_botones, #Se le indica en que frame aparecer
                text=texto_boton,
                height=25,
                width=200,
                command=self.botones[texto_boton]
            )
            boton.grid(row=contador//elementos_fila, column=contador%elementos_fila, padx=5, pady=5)

            # Incrementa el contador
            contador += 1

        self.root.mainloop()