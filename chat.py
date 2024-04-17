from tkinter import *
from tkinter import Toplevel, Menu, PhotoImage, Label, Button, Frame, TOP, LEFT, RIGHT, BOTH
from tkinter import scrolledtext, messagebox, simpledialog
from tkinter import ttk
import requests
import sqlite3
from tkinter import Menu
import json
import re
import os
from tkinter import filedialog
from PIL import Image
from tkinter import Toplevel, Label, Button, PhotoImage, filedialog
import tkinter.messagebox as messagebox
import os
from dotenv import load_dotenv

# Inicialización de variables globales
login_window = None
welcome_window = None
chat_window = None

API_URL = "https://api.openai.com/v1/chat/completions"
API_KEY = os.getenv("API_KEY")


conn = sqlite3.connect('usuarios.db')
conn.row_factory = sqlite3.Row # Esto permite acceder a las columnas por nombre
c = conn.cursor()
c.execute('''CREATE TABLE IF NOT EXISTS usuarios
             (ID INTEGER PRIMARY KEY AUTOINCREMENT,
              Nombre TEXT NOT NULL,
              Apellido TEXT NOT NULL)''')
conn.commit()


def create_database():
    if os.path.exists('usuarios.db'):
        messagebox.showinfo("Crear Base de Datos", "La base de datos ya está creada.")
    else:
        c.execute('''CREATE TABLE IF NOT EXISTS usuarios
                     (ID INTEGER PRIMARY KEY AUTOINCREMENT,
                      Nombre TEXT NOT NULL,
                      Apellido TEXT NOT NULL)''')
        conn.commit()
        messagebox.showinfo("Crear Base de Datos", "Base de datos creada exitosamente.")




# --- INTERACCIÓN CON CHATGPT ---


def get_chatgpt_response(user_input):
    headers = {
        "Authorization": f"Bearer {API_KEY}",
        "Content-Type": "application/json"
    }

    # Aquí proporcionas ejemplos de cómo diferentes comandos pueden ser formulados y cómo deberían ser interpretados
    context = """Ejemplos:
    Usuario: quiero añadir un usuario llamado Alex y que tenga el apellido Garcia
    Sistema: añade un nuevo usuario con el nombre Alex y apellido Garcia
    Usuario: por favor, elimina al usuario con identificación 123
    Sistema: elimina el usuario con ID 123
    Usuario: necesito cambiar el apellido del usuario con ID 456 a Martínez
    Sistema: cambia el apellido del usuario con ID 456 a Martínez
    Usuario: cómo puedo agregar a alguien con nombre John y apellido Doe al sistema?
    Sistema: añade un nuevo usuario con el nombre John y apellido Doe
    Usuario: borrar al usuario John Smith por favor
    Sistema: elimina el usuario con nombre John y apellido Smith
    Usuario: actualizar nombre de usuario con ID 789 a Jane
    Sistema: cambia el nombre del usuario con ID 789 a Jane
    Usuario: cuál es el nombre del usuario con apellido Smith
    Sistema: el nombre del usuario con apellido Smith es John
    Usuario: cuál es el apellido del usuario con nombre Jane
    Sistema: el apellido del usuario con nombre Jane es Doe
    Usuario: cuál es la ID del usuario con nombre Alex
    Sistema: la ID del usuario con nombre Alex es 102
    Usuario: cuál es la ID del apellido Segui
    Usuario: cuál es el ID del usuario con apellido García
    Sistema: la ID del usuario con apellido García es 205
    Usuario: cuál es el apellido del usuario con ID 789
    Sistema: el apellido del usuario con ID 789 es Martínez
    Usuario: cuál es el nombre del usuario con ID 456
    Sistema: el apellido de 65
    Usuario: el apellido del usuario con ID 65 es Montero
    Sistema: el nombre del usuario con ID 456 es Pedro
    Usuario: cuál es el nombre de 32
    Sistema: el nombre del usuario con ID 32 es Sofia
    """

    prompt = f"{context}Usuario: {user_input}\nSistema:"

    data = {
        "model": "gpt-4-turbo",
        "messages": [{"role": "system", "content": context}, {"role": "user", "content": user_input}]
    }

    response = requests.post(API_URL, headers=headers, json=data)
    if response.status_code == 200:
        # Interpretar la respuesta para extraer la acción del sistema
        return response.json()['choices'][0]['message']['content'].strip()
    else:
        return "Error en la respuesta de la API."
def handle_database_command(command):
    chat_response = get_chatgpt_response(command)

    # Añadir un usuario
    add_match = re.search(r'añade un nuevo usuario con el nombre (\w+) y apellido (\w+)', chat_response, re.IGNORECASE)
    if add_match:
        name, surname = add_match.groups()
        return add_user(name, surname)

    # Eliminar usuario por nombre
    delete_match = re.search(r"elimina el usuario con nombre (\w+)", chat_response, re.IGNORECASE)
    if delete_match:
        name = delete_match.group(1)
        return delete_user_by_name(name)

    # Actualizar nombre de usuario por ID
    update_match = re.search(r"cambia el nombre del usuario con ID (\d+) a (\w+)", chat_response, re.IGNORECASE)
    if update_match:
        user_id, new_name = update_match.groups()
        return update_user_field(user_id, "Nombre", new_name)

    # Cambiar apellido de usuario por ID
    update_surname_match = re.search(r"cambia el apellido del usuario con ID (\d+) a (\w+)", chat_response, re.IGNORECASE)
    if update_surname_match:
        user_id, new_surname = update_surname_match.groups()
        return update_user_field(user_id, "Apellido", new_surname)

    # Consultar nombre de usuario por apellido
    name_query_match = re.search(r"el nombre del usuario con apellido (\w+)", chat_response, re.IGNORECASE)
    if name_query_match:
        surname = name_query_match.group(1)
        return fetch_user_name_by_surname(surname)

    # Consultar apellido de usuario por nombre
    surname_query_match = re.search(r"el apellido del usuario con nombre (\w+)", chat_response, re.IGNORECASE)
    if surname_query_match:
        name = surname_query_match.group(1)
        return fetch_user_surname_by_name(name)

    # Consultar ID de usuario por nombre
    id_query_match = re.search(r"la ID del usuario con nombre (\w+)", chat_response, re.IGNORECASE)
    if id_query_match:
        name = id_query_match.group(1)
        return fetch_user_id_by_name(name)
    id_by_surname_match = re.search(r"la ID del usuario con apellido (\w+)", chat_response, re.IGNORECASE)
    if id_by_surname_match:
        surname = id_by_surname_match.group(1)
        return fetch_user_id_by_surname(surname)

    surname_by_id_match = re.search(r"el apellido del usuario con ID (\d+)", chat_response, re.IGNORECASE)
    if surname_by_id_match:
        user_id = surname_by_id_match.group(1)
        return fetch_user_surname_by_id(user_id)

    name_by_id_match = re.search(r"el nombre del usuario con ID (\d+)", chat_response, re.IGNORECASE)
    if name_by_id_match:
        user_id = name_by_id_match.group(1)
        return fetch_user_name_by_id(user_id)
    return "No se pudo interpretar la acción a realizar basada en la respuesta de ChatGPT"





# Asegúrate de que la función add_user, delete_user_by_id, delete_user_by_name, etc., están correctamente definidas.
    





import sqlite3
from tkinter import messagebox

# Conexión a la base de datos
conn = sqlite3.connect('usuarios.db')
c = conn.cursor()

def add_user(name, surname):
    try:
        c.execute("INSERT INTO usuarios (Nombre, Apellido) VALUES (?, ?)", (name, surname))
        conn.commit()
        return "Usuario añadido correctamente."
    except sqlite3.IntegrityError as e:
        return "Error al añadir el usuario: " + str(e)

def update_user_field(user_id, field, new_value):
    try:
        c.execute(f"UPDATE usuarios SET {field} = ? WHERE ID = ?", (new_value, user_id))
        conn.commit()
        if c.rowcount:
            return f"{field} actualizado a '{new_value}' para el usuario ID {user_id}."
        return f"No se encontró un usuario con la ID {user_id}."
    except sqlite3.Error as e:
        return f"Error al actualizar el usuario: {e}"
def fetch_user_name_by_surname(surname):
    try:
        c.execute("SELECT Nombre FROM usuarios WHERE Apellido = ?", (surname,))
        result = c.fetchone()
        if result:
            return f"El nombre del usuario con apellido {surname} es {result[0]}"  # Acceder por índice si no usas sqlite3.Row
            # return f"El nombre del usuario con apellido {surname} es {result['Nombre']}"  # Descomentar si usas sqlite3.Row
        return f"No se encontró un usuario con el apellido {surname}."
    except sqlite3.OperationalError as e:
        return f"Error en la consulta: {e}"

#---Buscar---#
def fetch_user_id_by_surname(surname):
    try:
        c.execute("SELECT ID FROM usuarios WHERE Apellido = ?", (surname,))
        result = c.fetchone()
        if result:
            return f"El ID del usuario con apellido {surname} es {result[0]}"
        return f"No se encontró un usuario con el apellido {surname}."
    except sqlite3.OperationalError as e:
        return f"Error en la consulta: {e}"
def fetch_user_surname_by_id(user_id):
    try:
        c.execute("SELECT Apellido FROM usuarios WHERE ID = ?", (user_id,))
        result = c.fetchone()
        if result:
            return f"El apellido del usuario con ID {user_id} es {result[0]}"
        return f"No se encontró un usuario con el ID {user_id}."
    except sqlite3.OperationalError as e:
        return f"Error en la consulta: {e}"
def fetch_user_name_by_id(user_id):
    try:
        c.execute("SELECT Nombre FROM usuarios WHERE ID = ?", (user_id,))
        result = c.fetchone()
        if result:
            return f"El nombre del usuario con ID {user_id} es {result[0]}"
        return f"No se encontró un usuario con el ID {user_id}."
    except sqlite3.OperationalError as e:
        return f"Error en la consulta: {e}"

def fetch_user_surname_by_name(name):
    try:
        c.execute("SELECT Apellido FROM usuarios WHERE Nombre = ?", (name,))
        result = c.fetchone()
        if result:
            return f"El apellido del usuario con nombre {name} es {result[0]}"  # Acceder por índice
        return f"No se encontró un usuario con el nombre {name}."
    except sqlite3.OperationalError as e:
        return f"Error en la consulta: {e}"


def fetch_user_id_by_name(name):
    try:
        c.execute("SELECT ID FROM usuarios WHERE Nombre = ?", (name,))
        result = c.fetchone()
        if result:
            return f"El ID del usuario con nombre {name} es {result[0]}"  # Acceder por índice si no usas sqlite3.Row
            # return f"El ID del usuario con nombre {name} es {result['ID']}"  # Descomentar si usas sqlite3.Row
        return f"No se encontró un usuario con el nombre {name}."
    except sqlite3.OperationalError as e:
        return f"Error en la consulta: {e}"



def delete_user_by_name(name):
    try:
        c.execute("DELETE FROM usuarios WHERE Nombre = ?", (name,))
        conn.commit()
        return "Usuario eliminado correctamente."
    except sqlite3.Error as e:
        return "Error al eliminar el usuario: " + str(e)

def delete_user_by_id(user_id):
    try:
        c.execute("DELETE FROM usuarios WHERE ID = ?", (user_id,))
        conn.commit()
        return "Usuario eliminado correctamente."
    except sqlite3.Error as e:
        return "Error al eliminar el usuario: " + str(e)

def add_column(column_name):
    try:
        c.execute(f"ALTER TABLE usuarios ADD COLUMN {column_name} TEXT")
        conn.commit()
        return f"Columna '{column_name}' añadida correctamente."
    except sqlite3.OperationalError as e:
        return "Error al añadir la columna: " + str(e)

def delete_column(column_name):
    # SQLite no soporta directamente la eliminación de columnas, considera crear una nueva tabla sin esa columna
    return "Operación no soportada: SQLite no permite eliminar columnas directamente."

def update_column_info(user_id, column_name, new_info):
    try:
        c.execute(f"UPDATE usuarios SET {column_name} = ? WHERE ID = ?", (new_info, user_id))
        conn.commit()
        return f"Información actualizada en columna '{column_name}'."
    except sqlite3.Error as e:
        return "Error al actualizar la información en la columna: " + str(e)


def delete_database():
    try:
        c.execute("DROP TABLE IF EXISTS usuarios")
        conn.commit()
        return "Base de datos eliminada correctamente."
    except sqlite3.Error as e:
        return "Error al eliminar la base de datos: " + str(e)

def fetch_user_by_id(user_id):
    c.execute("SELECT * FROM usuarios WHERE ID = ?", (user_id,))
    return c.fetchone()

def fetch_user_info(username):
    print(f"Iniciando sesión con usuario: {username}")
    url = 'https://heavenly-olivine-peak.glitch.me/articles/'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            users = response.json()
            for user in users:
                # Comprueba si el username coincide y si el campo username existe
                if 'username' in user and user['username'] == username:
                    return user
            messagebox.showinfo("Usuario no encontrado", "El usuario solicitado no existe.")
            return None
        else:
            messagebox.showerror("Error", f"No se pudo recuperar la información. Código de estado: {response.status_code}")
            return None
    except requests.RequestException as e:
        messagebox.showerror("Error de red", str(e))
        return None




def update_user_info(username, new_password, photo_path):
    url = 'https://heavenly-olivine-peak.glitch.me/articles/'
    data = {'password': new_password, 'photo': photo_path}
    try:
        response = requests.post(url, json=data)
        if response.status_code == 200:
            messagebox.showinfo("Éxito", "Información actualizada correctamente.")
        else:
            messagebox.showerror("Error", f"No se pudo actualizar la información. Código de estado: {response.status_code}")
    except requests.RequestException as e:
        messagebox.showerror("Error de red", str(e))


def fetch_users_by_surname(surname):
    c.execute("SELECT * FROM usuarios WHERE Apellido = ?", (surname,))
    return c.fetchall()


def fetch_usuarios():
    """Esta función recupera todos los usuarios para verificar existencias."""
    url = 'https://heavenly-olivine-peak.glitch.me/articles/'
    try:
        response = requests.get(url)
        if response.status_code == 200:
            return response.json()
        else:
            return []
    except requests.RequestException:
        messagebox.showerror("Error", "Error de red, intente de nuevo más tarde.")
        return []

def check_login(username, password):
    """Verifica si el usuario existe con la contraseña correcta."""
    users = fetch_usuarios()
    for user in users:
        if 'username' in user and 'password' in user and user['username'] == username and user['password'] == password:
            return True
    return False

def register_user(username, password):
    """Registra un nuevo usuario si no existe."""
    url = 'https://heavenly-olivine-peak.glitch.me/articles/'
    user_data = {'username': username, 'password': password}
    try:
        response = requests.post(url, json=user_data)
        if response.status_code == 201:
            return True
        else:
            return False
    except requests.RequestException:
        messagebox.showerror("Error", "Error de red, intente de nuevo más tarde.")
        return False

# Resto del código sin cambios...


from tkinter import Toplevel, Button, Label, PhotoImage, Frame
import os

from tkinter import Toplevel, Button, Label, PhotoImage, Frame
import os

def show_database_window(username):
    db_window = Toplevel(welcome_window)

    # Añadir una foto
    image = PhotoImage(file="images/robot_base.png")
    photo_label = Label(db_window, image=image)
    photo_label.image = image
    photo_label.pack(pady=10)

    # Saludo y título dentro de la ventana
    greeting_label = Label(db_window, text="Hola, " + username + ", ¿cómo quieres administrar la base de datos hoy?", font=("Helvetica", 16))
    greeting_label.pack()

    # Organizar botones horizontalmente
    button_frame = Frame(db_window)
    button_frame.pack(pady=10)

    # Estilos comunes para todos los botones
    button_style = {'relief': FLAT, 'bg': 'black', 'fg': 'white', 'font': ("Helvetica", 14), 'padx': 15, 'pady': 7}

    # Crear botones
    create_db_button = Button(button_frame, text="Crear Base de Datos", command=create_database, **button_style)
    create_db_button.grid(row=0, column=0, padx=10, sticky='ew')

    insert_data_button = Button(button_frame, text="Insertar Datos Manualmente", command=show_insert_window, **button_style)
    insert_data_button.grid(row=0, column=1, padx=10, sticky='ew')

    manage_db_button = Button(button_frame, text="Administrar Base de Datos", command=show_admin_window, **button_style)
    manage_db_button.grid(row=0, column=2, padx=10, sticky='ew')

    ia_button = Button(button_frame, text="Administrar con NickyGPT", command=lambda: show_chat_interface(username, 1), **button_style)
    ia_button.grid(row=1, column=0, padx=10, sticky='ew')

    delete_db_button = Button(button_frame, text="Eliminar Base de Datos", command=delete_database, **button_style)
    delete_db_button.grid(row=1, column=1, padx=10, sticky='ew')

    back_button = Button(button_frame, text="Volver", command=db_window.destroy, **button_style)
    back_button.grid(row=1, column=2, padx=10, sticky='ew')

    # Ajuste para que los botones ocupen el espacio igualmente en cada fila
    button_frame.grid_columnconfigure(0, weight=1)
    button_frame.grid_columnconfigure(1, weight=1)
    button_frame.grid_columnconfigure(2, weight=1)

    # Verificar si la base de datos ya existe y desactivar el botón de creación si es necesario

    center_window(db_window)


    

    # Verificar si la base de datos ya existe y desactivar el botón de creación si es necesario
    if not os.path.exists('usuarios.db'):
        create_db_button.config(state='disabled')

    center_window(db_window)
 


def get_column_names(cursor, table_name="usuarios"):
    """
    Obtiene los nombres de las columnas de la tabla especificada, excluyendo el ID.
    """
    cursor.execute(f"PRAGMA table_info({table_name})")
    columns = [info[1] for info in cursor.fetchall() if info[1].lower() != 'id']
    return columns


def fetch_users():
    c.execute("SELECT * FROM usuarios")
    return c.fetchall()

def insert_user(nombre, apellido):
    c.execute("INSERT INTO usuarios (Nombre, Apellido) VALUES (?, ?)", (nombre, apellido))
    conn.commit()




    
def delete_account(username):
    # Suponiendo que la URL y los parámetros son correctos
    url = 'https://heavenly-olivine-peak.glitch.me/articles/'
    try:
        response = requests.delete(url, params={'username': username})
        if response.status_code == 200:
            messagebox.showinfo("Cuenta eliminada", "Su cuenta ha sido eliminada correctamente.")
            logout(username)
        else:
            messagebox.showerror("Error", f"No se pudo eliminar la cuenta. Código de error: {response.status_code}")
    except requests.RequestException as e:
        messagebox.showerror("Error de red", f"No se pudo conectar al servidor. Error: {str(e)}")


    # Cerrar la sesión
    logout(username)


from tkinter import ttk

def show_admin_window():
    admin_window = Toplevel(welcome_window)
    admin_window.title("Administrar Base de Datos")

    # Crear el Treeview widget
    tree = ttk.Treeview(admin_window, columns=("ID", "Nombre", "Apellido"), show="headings")
    tree.pack(expand=YES, fill=BOTH)

    # Configurar las columnas y los encabezados
    tree.heading("ID", text="ID")
    tree.heading("Nombre", text="Nombre")
    tree.heading("Apellido", text="Apellido")

    tree.column("ID", anchor="center", width=80)
    tree.column("Nombre", anchor="center", width=150)
    tree.column("Apellido", anchor="center", width=150)

    # Rellenar el Treeview con datos de la base de datos
    fill_treeview(tree)

    center_window(admin_window)
    admin_window.mainloop()

def fill_treeview(tree):
    # Limpiar el treeview
    for i in tree.get_children():
        tree.delete(i)

    # Consulta para obtener los datos
    c.execute("SELECT ID, Nombre, Apellido FROM usuarios")
    rows = c.fetchall()
    for row in rows:
        # Insertar los datos en el Treeview
        tree.insert("", "end", values=(row["ID"], row["Nombre"], row["Apellido"]))



def show_insert_window():
    global welcome_window

    # Obtener los nombres de las columnas desde la base de datos, excluyendo el ID
    column_names = get_column_names(c)

    insert_window = Toplevel(welcome_window)
    insert_window.title("Insertar Usuario")

    # Diccionario para almacenar las referencias de las entradas
    entry_fields = {}

    # Crear una entrada para cada columna en la base de datos, excepto el ID
    for index, column in enumerate(column_names):
        Label(insert_window, text=column).grid(row=index, column=0, padx=5, pady=5)
        entry = Entry(insert_window)
        entry.grid(row=index, column=1, padx=5, pady=5)
        entry_fields[column] = entry

    def save_user():
        # Crear un diccionario para los datos ingresados, excluyendo el ID
        data = {column: entry.get().strip() for column, entry in entry_fields.items()}

        if all(data.values()):  # Verificar que todos los campos estén completos
            try:
                columns = ', '.join(data.keys())
                placeholders = ', '.join('?' * len(data.values()))
                values = tuple(data.values())
                c.execute(f"INSERT INTO usuarios ({columns}) VALUES ({placeholders})", values)
                conn.commit()
                messagebox.showinfo("Éxito", "Usuario insertado correctamente.")
                insert_window.destroy()
            except sqlite3.Error as e:
                messagebox.showerror("Error", f"Error al insertar en la base de datos: {e}")
        else:
            messagebox.showwarning("Error", "Por favor, complete todos los campos.")

    # Botón para guardar el usuario
    insert_button = Button(insert_window, text="Insertar", command=save_user)
    insert_button.grid(row=len(column_names) + 1, columnspan=2, padx=5, pady=5)
    center_window(insert_window)

def delete_database():
    confirm = messagebox.askyesno("Eliminar Base de Datos", "¿Está seguro que desea eliminar la base de datos?")
    if confirm:
        try:
            # Cerrar la conexión a la base de datos si está abierta
            if conn:
                conn.close()
            
            # Eliminar el archivo de la base de datos
            os.remove('usuarios.db')
            messagebox.showinfo("Eliminar Base de Datos", "La base de datos ha sido eliminada con éxito.")
            
            # Aquí puedes incluir cualquier otro código necesario después de eliminar la base de datos
            # Por ejemplo, cerrar la aplicación o actualizar la interfaz
            
        except OSError as e:
            messagebox.showerror("Error", f"Error al eliminar la base de datos: {e}")

    
def is_database_query(user_input):
    database_keywords = ['id', 'nombre', 'apellido', 'añade', 'elimina']
    return any(keyword in user_input.lower() for keyword in database_keywords)



def show_chat_interface(username, num):
    global chat_window
    chat_window = Toplevel(welcome_window)
    chat_window.title("Chatbot")

    # Crear la ventana principal, luego crear la imagen
    welcome_window.update_idletasks()
    bot_icon = PhotoImage(file='images/robot7.png')  # Asegúrate de tener la ruta correcta a tu imagen

    chat_history = scrolledtext.ScrolledText(chat_window, state='disabled', height=20, width=60)
    chat_history.grid(row=0, column=0, columnspan=2, padx=5, pady=5)

    # Insertar mensaje de bienvenida
    if num == 1:
        welcome_message = "Bienvenido al chat con NickyGPT, estoy preparado para administrar la base de datos."
        chat_history.config(state='normal')
        chat_history.image_create(END, image=bot_icon)
        chat_history.insert(END, ": " + welcome_message + "\n\n")
        chat_history.config(state='disabled')
    elif num == 2:
        welcome_message = "Bienvenido al chat con NickyGPT, soy tu asistente personal y estoy preparado para cualquier pregunta."
        chat_history.config(state='normal')
        chat_history.image_create(END, image=bot_icon)
        chat_history.insert(END, ": " + welcome_message + "\n\n")
        chat_history.config(state='disabled')

    user_input_entry = Text(chat_window, height=3, width=50)
    user_input_entry.grid(row=1, column=0, padx=5, pady=5)
    
    def send_message():
        user_input = user_input_entry.get("1.0", END).strip()
        if not user_input:
            messagebox.showwarning("Requerido", "Por favor, introduce algún texto para enviar.")
            return

        # Verificar si el mensaje es un comando para la base de datos
        if is_database_query(user_input):
            response = handle_database_command(user_input)
        else:
            # Si no es un comando de base de datos, pasar a ChatGPT
            response = get_chatgpt_response(user_input)

        chat_history.config(state='normal')
        chat_history.insert(END, f"{username}: {user_input}\n")
        # Insertar la imagen antes del nombre "NickyGPT"
        chat_history.image_create(END, image=bot_icon)
        chat_history.insert(END, ": {}\n\n".format(response))
        chat_history.config(state='disabled')
        user_input_entry.delete('1.0', END)

    send_button = Button(chat_window, text="Enviar", command=send_message)
    send_button.grid(row=1, column=1, padx=5, pady=5)
    center_window(chat_window)



def ask_chatgpt_about_users():
    users = fetch_users()
    user_list = ', '.join([f"{user[1]} {user[2]}" for user in users])
    prompt = f"Tell me about the users: {user_list}"
    return get_chatgpt_response(prompt)

def logout(username):
    # Cierra cualquier ventana abierta relacionada con la sesión activa
    if welcome_window and welcome_window.winfo_exists():
        welcome_window.destroy()  # Cierra la ventana de bienvenida
    if welcome_window_1 and welcome_window_1.winfo_exists():
        welcome_window_1.destroy()  # Cierra cualquier otra ventana adicional que podría estar abierta
    login_window.deiconify()  # Muestra nuevamente la ventana de inicio de sesión


#--- Bienvenida ---#

def welcome_screen(username):
    global welcome_window, welcome_window_1
    if welcome_window_1 and welcome_window_1.winfo_exists():
        welcome_window_1.destroy()

    welcome_window = Toplevel()
    welcome_window.title(f"Servicios - NickyGPT")
    welcome_window.geometry('1000x550')

    # Configuración de la barra de menú
    menubar = Menu(welcome_window)
    welcome_window.config(menu=menubar)

    # Agregar opciones al menú
    option_menu = Menu(menubar, tearoff=0)
    option1_menu = Menu(menubar, tearoff=0)
    option2_menu = Menu(menubar, tearoff=0)
    menubar.add_cascade(label="Cerrar sesión", menu=option_menu)
    menubar.add_cascade(label="Eliminar cuenta", menu=option1_menu)
    menubar.add_cascade(label="Salir del programa", menu=option2_menu)
    option_menu.add_command(label="Cerrar sesión", command=lambda: logout(username))
    option1_menu.add_command(label="Eliminar cuenta", command=lambda: delete_account(username))
    option2_menu.add_command(label="Salir del programa", command=welcome_window.destroy)

    # Cargar y mostrar la imagen
    photo = PhotoImage(file="images/robot3.png")
    photo_label = Label(welcome_window, image=photo)
    photo_label.image = photo
    photo_label.pack(side=TOP, pady=10)

    # Título principal
    title_label = Label(welcome_window, text="Servicios", font=("Helvetica", 20, "bold"))
    title_label.pack(side=TOP, pady=5)
    title_label1 = Label(welcome_window, text="Descubre la magia de la inteligencia artificial con NickyGPT a tu disposición", font=("Helvetica", 15, "bold"))
    title_label1.pack(side=TOP, pady=5)

    # Frame para botones de servicio
    button_frame = Frame(welcome_window)
    button_frame.pack(expand=True, fill=BOTH)

    # Botones de servicio
    connect_db_button = Button(button_frame, text="Base de datos", command=lambda: show_database_window(username), relief=FLAT, bg='#00a2ed', fg='white', font=("Helvetica", 12))
    connect_db_button.pack(side=LEFT, expand=True, fill=BOTH, padx=10, pady=10)
        
    chat_button = Button(button_frame, text="NickyGPT    ", command=lambda: show_chat_interface(username, 2), relief=FLAT, bg='#00a2ed', fg='white', font=("Helvetica", 12))
    chat_button.pack(side=LEFT, expand=True, fill=BOTH, padx=10, pady=10)

    service_button = Button(button_frame, text="Servicio3  ", command=lambda: show_chat_interface(username), relief=FLAT, bg='#00a2ed', fg='white', font=("Helvetica", 12))
    service_button.pack(side=LEFT, expand=True, fill=BOTH, padx=10, pady=10)

    volver_button = Button(button_frame, text="Volver     ", command=lambda: [welcome_window.destroy(), welcome_screen1(username)], relief=FLAT, bg='#00a2ed', fg='white', font=("Helvetica", 12))
    volver_button.pack(side=LEFT, expand=True, fill=BOTH, padx=10, pady=10)



    center_window(welcome_window)


    # No llamar a mainloop() aquí



def welcome_screen1(username):
    global welcome_window_1, welcome_window
    print(f"Iniciando sesión con usuario: {username}")
    # Asegurarse de que welcome_window no existe o no está visible antes de crear welcome_window_1
    if welcome_window and not welcome_window.winfo_exists():
        welcome_window.destroy()

    welcome_window_1 = Toplevel()
    welcome_window_1.title(f"Bienvenido a NickyGPT, {username}")
    welcome_window_1.geometry('1000x610')

    welcome_window_1.update_idletasks()

    photo = PhotoImage(file="images/robot_bienvenida.png")
    photo_label = Label(welcome_window_1, image=photo)
    photo_label.image = photo
    photo_label.pack(side=TOP, pady=20)

    title_label = Label(welcome_window_1, text="Bienvenido a NickyGPT", font=("Helvetica", 24, "bold"))
    title_label.pack(side=TOP, pady=10)

    description_label = Label(welcome_window_1, text="Descubre la magia de la inteligencia artificial con NickyGPT. "
                               "Explora un mundo de posibilidades a través de nuestra tecnología avanzada que te ofrece "
                               "soluciones personalizadas y eficientes en tiempo real para tus necesidades diarias, educativas y empresariales.",
                              font=("Helvetica", 16))
    description_label.pack(side=TOP, pady=10)

    start_button = Button(welcome_window_1, text="Empezar", command=lambda: welcome_screen(username),
                          relief=FLAT, bg='#00a2ed', fg='white', font=("Helvetica", 14))
    start_button.pack(side=LEFT, expand=True, fill=BOTH, padx=50, pady=20)

    account_button = Button(welcome_window_1, text="Mi Cuenta", command=lambda: show_account_info(username),
                            relief=FLAT, bg='#00a2ed', fg='white', font=("Helvetica", 14))
    account_button.pack(side=RIGHT, expand=True, fill=BOTH, padx=50, pady=20)


    center_window(welcome_window_1)

from tkinter import *
from tkinter import filedialog

from tkinter import *

def show_account_info(username):
    user_info = fetch_user_info(username)
    if not user_info:
        messagebox.showinfo("Error", "Usuario no encontrado")
        return

    account_window = Toplevel()
    account_window.title("Información de Cuenta")
    account_window.geometry('400x250')

    # Dimensiones deseadas para la imagen
    desired_size = (100, 100)  # Por ejemplo, 100x100 píxeles

    # Función para cambiar la contraseña
    def change_password():
        # Aquí deberías agregar la lógica para cambiar la contraseña
        print("La contraseña ha sido actualizada")

    # Función para actualizar foto y ajustar su tamaño
    def update_photo():
        photo_path = filedialog.askopenfilename()
        if photo_path:
            # Cargar y ajustar tamaño de la imagen
            new_photo = PhotoImage(file=photo_path)
            new_photo = new_photo.subsample(new_photo.width() // desired_size[0], new_photo.height() // desired_size[1])
            photo_label.configure(image=new_photo)
            photo_label.image = new_photo  # Mantener referencia
            print("La foto de perfil ha sido actualizada")

    # Cargar y ajustar tamaño de la imagen predeterminada
    global default_photo
    default_photo = PhotoImage(file="images/robot1.png")
    default_photo = default_photo.subsample(default_photo.width() // desired_size[0], default_photo.height() // desired_size[1])
    photo_label = Label(account_window, image=default_photo)
    photo_label.pack()

    # Muestra el nombre de usuario
    username_label = Label(account_window, text=f"Nombre de Usuario: {user_info.get('username', 'No disponible')}", font=("Helvetica", 16))
    username_label.pack()

    # Muestra la fecha de creación de la cuenta
    creation_date_label = Label(account_window, text=f"Fecha de Creación: {user_info.get('creation_date', 'Desconocida')}")
    creation_date_label.pack()

    # Botones de acción
    Button(account_window, text="Cambiar contraseña", command=change_password, relief=FLAT, bg='#00a2ed', fg='white', font=("Helvetica", 12)).pack(side=LEFT, expand=True, fill=BOTH, padx=10, pady=10)
    Button(account_window, text="Cambiar Foto de perfil", command=update_photo, relief=FLAT, bg='#00a2ed', fg='white', font=("Helvetica", 12)).pack(side=RIGHT, expand=True, fill=BOTH, padx=10, pady=10)

    center_window(account_window)





def safe_destroy(window):
    if window and window.winfo_exists():
        window.destroy()

#--- Inicio de sesiom ---#

from tkinter import *
from tkinter import messagebox, simpledialog, PhotoImage

def initialize_login():
    global login_window
    login_window = Tk()  # Esta es la única llamada a Tk()
    login_window.title("NickyGPT - Acceso")
    login_window.geometry('1000x660')  # Define un tamaño más grande para la ventana

    # Cargar y mostrar un logo
    logo = PhotoImage(file='images/robot.png')  # Asegúrate de usar el path correcto al archivo de logo
    logo_label = Label(login_window, image=logo)
    logo_label.image = logo  # Guardar referencia
    logo_label.pack(pady=10)

    # Título del programa
    title_label = Label(login_window, text="Bienvenido a NickyGPT", font=("Helvetica", 16, "bold"))
    title_label.pack()

    container = Frame(login_window, padx=20, pady=20)
    container.pack(expand=True, fill=BOTH)

    login_button = Button(container, text="Inicio de sesión", command=login, relief=FLAT, bg='#00a2ed', fg='white', font=("Helvetica", 12))
    login_button.pack(side=LEFT, expand=True, fill=BOTH, padx=10, pady=10)

    register_button = Button(container, text="Registro", command=register, relief=FLAT, bg='#00a2ed', fg='white', font=("Helvetica", 12))
    register_button.pack(side=RIGHT, expand=True, fill=BOTH, padx=10, pady=10)

    center_window(login_window)

def center_window(win):
    win.update_idletasks()
    width = win.winfo_width()
    height = win.winfo_height()
    x = (win.winfo_screenwidth() // 2) - (width // 2)
    y = (win.winfo_screenheight() // 2) - (height // 2)
    win.geometry(f'{width}x{height}+{x}+{y}')

def login():
    global username  # Declara username como global si aún no lo has hecho
    username = simpledialog.askstring("Inicio de sesión", "Ingrese su nombre de usuario", parent=login_window)
    if not username:
        messagebox.showwarning("Inicio de sesión fallido", "Debe ingresar un nombre de usuario.")
        return
    password = simpledialog.askstring("Inicio de sesión", "Ingrese su contraseña", show='*', parent=login_window)
    if not password:
        messagebox.showwarning("Inicio de sesión fallido", "Debe ingresar una contraseña.")
        return

    if check_login(username, password):
        messagebox.showinfo("Inicio de sesión exitoso", "Ha iniciado sesión correctamente.")
        login_window.withdraw()  # Oculta la ventana de inicio de sesión
        welcome_screen1(username)  # Muestra la ventana de bienvenida
    else:
        messagebox.showwarning("Inicio de sesión fallido", "Usuario o contraseña incorrectos.")


def register():
    username = simpledialog.askstring("Registro", "Elija un nombre de usuario", parent=login_window)
    if username is None or username.strip() == "":
        return
    password = simpledialog.askstring("Registro", "Elija una contraseña", parent=login_window)
    if password is None or password.strip() == "":
        messagebox.showwarning("Registro fallido", "El nombre de usuario y la contraseña no pueden estar vacíos.")
        return
    if register_user(username, password):
        messagebox.showinfo("Registro exitoso", "Se ha registrado correctamente.")
    else:
        messagebox.showwarning("Registro fallido", "No se pudo completar el registro.")

# Asegúrate de tener las funciones check_login, welcome_screen y register_user correctamente implementadas.


if __name__ == "__main__":
    initialize_login()
    login_window.mainloop()
