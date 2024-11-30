import tkinter as tk
from tkinter import messagebox
from tkinter import ttk
import sqlite3
import hashlib
import re  # Para validar el formato del email

# Conectar a la base de datos
conn = sqlite3.connect("gestion_soporte.db")
cursor = conn.cursor()

# Función para verificar si un email tiene un formato válido
def validar_email(email):
    patron = r"^[a-zA-Z0-9_.+-]+@[a-zA-Z0-9-]+\.[a-zA-Z0-9-.]+$"
    return re.match(patron, email)

# Función para verificar credenciales
def verificar_credenciales(email, password):
    if not validar_email(email):
        messagebox.showerror("Error", "Por favor, ingrese un correo electrónico válido.")
        return None

    conn = sqlite3.connect("gestion_soporte.db")
    cursor = conn.cursor()
    
    cursor.execute("SELECT id_usuario, password, tipo_usuario_id FROM Usuarios WHERE email = ?", (email,))
    user = cursor.fetchone()
    conn.close()
    
    if user and user[1] == hashlib.sha256(password.encode()).hexdigest():
        return user  # Devuelve el id de usuario y el tipo de usuario
    return None

# Función para registrar un nuevo usuario
def registrar_usuario(email, password, tipo_usuario_id):
    if not validar_email(email):
        messagebox.showerror("Error", "Por favor, ingrese un correo electrónico válido.")
        return

    conn = sqlite3.connect("gestion_soporte.db")
    cursor = conn.cursor()

    # Encriptar la contraseña
    password_hash = hashlib.sha256(password.encode()).hexdigest()
    
    try:
        cursor.execute("INSERT INTO Usuarios (email, password, tipo_usuario_id) VALUES (?, ?, ?)", 
                       (email, password_hash, tipo_usuario_id))
        conn.commit()
        messagebox.showinfo("Registro", "Usuario registrado exitosamente.")
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", "El correo ya está registrado.")
    finally:
        conn.close()

# Función para cargar el formulario de registro
def ventana_registro():
    registro = tk.Toplevel(root)
    registro.title("Registro de Usuario")
    registro.geometry("400x300")
    registro.resizable(False, False)
    
    ttk.Label(registro, text="Registro de Usuario", font=("Arial", 14, "bold")).pack(pady=10)

    frame = ttk.Frame(registro, padding=10)
    frame.pack(fill=tk.BOTH, expand=True)
    
    ttk.Label(frame, text="Email:").grid(row=0, column=0, pady=5, sticky=tk.W)
    ttk.Label(frame, text="Contraseña:").grid(row=1, column=0, pady=5, sticky=tk.W)
    ttk.Label(frame, text="Rol:").grid(row=2, column=0, pady=5, sticky=tk.W)
    
    email_entry = ttk.Entry(frame, width=30)
    password_entry = ttk.Entry(frame, show="*", width=30)
    role_var = tk.StringVar()
    role_menu = ttk.Combobox(frame, textvariable=role_var, state="readonly", values=["Personal Técnico", "Personal Administrativo", "Usuario Administrador"])
    
    email_entry.grid(row=0, column=1, pady=5)
    password_entry.grid(row=1, column=1, pady=5)
    role_menu.grid(row=2, column=1, pady=5)

    def registrar():
        email = email_entry.get()
        password = password_entry.get()
        role = role_var.get()
        
        # Mapeo de roles a IDs
        tipo_usuario_id = {"Personal Técnico": 1, "Personal Administrativo": 2, "Usuario Administrador": 3}.get(role)
        
        if tipo_usuario_id:
            registrar_usuario(email, password, tipo_usuario_id)
            registro.destroy()
        else:
            messagebox.showerror("Error", "Debe seleccionar un rol.")

    ttk.Button(registro, text="Registrar", command=registrar).pack(pady=20)

# Función de inicio de sesión
def iniciar_sesion():
    email = email_entry.get()
    password = password_entry.get()
    
    if not validar_email(email):
        messagebox.showerror("Error", "Por favor, ingrese un correo electrónico válido.")
        return
    
    user = verificar_credenciales(email, password)
    if user:
        messagebox.showinfo("Bienvenido", f"Ingreso exitoso. Rol: {user[2]}")
        root.destroy()  # Cierra la ventana de login y abre la consola principal
        abrir_sistema_principal(user)
    else:
        messagebox.showerror("Error", "Usuario o contraseña incorrectos.")

# Función para cargar el sistema principal basado en el tipo de usuario
def abrir_sistema_principal(user):
    tipo_usuario_id = user[2]
    if tipo_usuario_id == 1:
        abrir_sistema_principal_tecnico(user)

    elif tipo_usuario_id == 2:
        abrir_sistema_principal_administrativo(user)

    elif tipo_usuario_id == 3:
        abrir_sistema_principal_administrador(user)

def abrir_sistema_principal_tecnico(user):
    import sistema_principal_tecnico  # Carga el módulo correspondiente
    sistema_principal_tecnico.main(user)  # Llamada a la función principal del sistema

def abrir_sistema_principal_administrativo(user):
    import sistema_principal_administrativo  # Carga el módulo correspondiente
    abrir_sistema_principal_administrativo.main(user)  # Llamada a la función principal del sistema

def abrir_sistema_principal_administrador(user):
    import sistema_principal_administrador  # Carga el módulo correspondiente
    abrir_sistema_principal_administrador.main(user)  # Llamada a la función principal del sistema

# Interfaz de Inicio de Sesión
root = tk.Tk()
root.title("Inicio de Sesión")
root.geometry("400x300")
root.resizable(False, False)

# Encabezado
ttk.Label(root, text="Sistema de Gestión", font=("Arial", 16, "bold")).pack(pady=20)

# Formulario
frame = ttk.Frame(root, padding=20)
frame.pack(fill=tk.BOTH, expand=True)

ttk.Label(frame, text="Email:").grid(row=0, column=0, pady=10, sticky=tk.W)
ttk.Label(frame, text="Contraseña:").grid(row=1, column=0, pady=10, sticky=tk.W)

email_entry = ttk.Entry(frame, width=30)
password_entry = ttk.Entry(frame, show="*", width=30)

email_entry.grid(row=0, column=1, pady=10)
password_entry.grid(row=1, column=1, pady=10)

# Botones
button_frame = ttk.Frame(root, padding=10)
button_frame.pack()

ttk.Button(button_frame, text="Iniciar Sesión", command=iniciar_sesion).grid(row=0, column=0, padx=10, pady=10)
ttk.Button(button_frame, text="Registrar Usuario", command=ventana_registro).grid(row=0, column=1, padx=10, pady=10)

root.mainloop()
