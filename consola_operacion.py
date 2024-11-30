import tkinter as tk
from tkinter import ttk, messagebox
from reportlab.lib.pagesizes import A4
from reportlab.pdfgen import canvas
import os
import sqlite3
from datetime import datetime  # Para validar la fecha

# Función para validar el formato de la fecha
def validar_fecha(fecha_texto):
    try:
        datetime.strptime(fecha_texto, "%d/%m/%Y")  # Formato DD/MM/YYYY
        return True
    except ValueError:
        return False

# Función para obtener el siguiente número de ticket
def obtener_siguiente_ticket():
    with sqlite3.connect("tickets.db") as conn:
        cursor = conn.cursor()
        cursor.execute("SELECT MAX(ticket_num) FROM tickets")
        max_ticket = cursor.fetchone()[0]
        return int(max_ticket) + 1 if max_ticket else 1

# Función para guardar la información en un archivo PDF
def guardar_pdf():
    # Validar formato de la fecha
    fecha_reporte = fecha_entry.get().strip()
    if not validar_fecha(fecha_reporte):
        messagebox.showerror("Error", "La fecha debe estar en formato DD/MM/YYYY.")
        return

    # Recoger la información del formulario
    ticket_num = ticket_entry.get().strip()
    nombre_usuario = user_entries[0].get()
    user_id = user_entries[1].get()
    tipo_usuario = user_entries[2].get()
    status_usuario = user_entries[3].get()
    departamento = user_entries[4].get()
    division = user_entries[5].get()
    cargo = user_entries[6].get()
    direccion = user_entries[7].get()
    equipo = user_entries[8].get()
    ubicacion = user_entries[9].get()
    causa = causa_entry.get()
    descripcion = desc_text.get("1.0", tk.END).strip()
    status_ticket = status_combobox.get()
    motivo_status = motivo_combobox.get()
    resolucion = resol_text.get("1.0", tk.END).strip()

    # Guardar los datos en la base de datos
    try:
        with sqlite3.connect("tickets.db") as conn:
            cursor = conn.cursor()
            cursor.execute('''CREATE TABLE IF NOT EXISTS tickets (
                ticket_num INTEGER PRIMARY KEY,
                fecha_reporte TEXT,
                nombre_usuario TEXT,
                user_id TEXT,
                tipo_usuario TEXT,
                status_usuario TEXT,
                departamento TEXT,
                division TEXT,
                cargo TEXT,
                direccion TEXT,
                equipo TEXT,
                ubicacion TEXT,
                causa TEXT,
                descripcion TEXT,
                status_ticket TEXT,
                motivo_status TEXT,
                resolucion TEXT
            )''')

            cursor.execute('''
                INSERT INTO tickets (ticket_num, fecha_reporte, nombre_usuario, user_id, tipo_usuario, 
                status_usuario, departamento, division, cargo, direccion, equipo, ubicacion, 
                causa, descripcion, status_ticket, motivo_status, resolucion) 
                VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
            ''', (ticket_num, fecha_reporte, nombre_usuario, user_id, tipo_usuario, status_usuario,
                  departamento, division, cargo, direccion, equipo, ubicacion, causa, descripcion,
                  status_ticket, motivo_status, resolucion))
            conn.commit()
    except sqlite3.IntegrityError:
        messagebox.showerror("Error", f"El ticket #{ticket_num} ya existe en la base de datos.")
        return
    except sqlite3.OperationalError as e:
        messagebox.showerror("Error", f"Error al acceder a la base de datos: {str(e)}")
        return

    # Nombre del archivo PDF
    pdf_filename = f"C:/Users/Administrador/Desktop/Proyecto/ticket_{ticket_num}.pdf"
    
    # Verificar si el archivo ya existe
    if os.path.exists(pdf_filename):
        messagebox.showwarning("Advertencia", f"El archivo '{pdf_filename}' ya existe. No se puede sobrescribir.")
        return
    
    # Crear el PDF
    c = canvas.Canvas(pdf_filename, pagesize=A4)
    c.drawString(100, 800, f"Ticket #: {ticket_num}")
    c.drawString(400, 800, f"Fecha de Reporte: {fecha_reporte}")
    c.drawString(100, 770, "Detalles del Usuario:")
    c.drawString(100, 750, f"Nombre del Usuario: {nombre_usuario}")
    c.drawString(100, 730, f"User ID: {user_id}")
    c.drawString(100, 710, f"Tipo de Usuario: {tipo_usuario}")
    c.drawString(100, 690, f"Status del Usuario: {status_usuario}")
    c.drawString(100, 670, f"Departamento: {departamento}")
    c.drawString(100, 650, f"División: {division}")
    c.drawString(100, 630, f"Cargo: {cargo}")
    c.drawString(100, 610, f"Dirección: {direccion}")
    c.drawString(100, 590, f"Equipo Asignado: {equipo}")
    c.drawString(100, 570, f"Ubicación: {ubicacion}")
    c.drawString(100, 540, "Causa Probable Reportada:")
    c.drawString(100, 520, f"Causa: {causa}")
    c.drawString(100, 500, "Descripción:")
    c.drawString(100, 480, descripcion)
    c.drawString(100, 450, f"Status del Ticket: {status_ticket}")
    c.drawString(100, 430, f"Motivo del Status: {motivo_status}")
    c.drawString(100, 400, "Notas de Resolución:")
    c.drawString(100, 380, resolucion)
    c.save()

    messagebox.showinfo("Guardado", f"El ticket ha sido guardado en {pdf_filename}")

# Crear la ventana principal
root = tk.Tk()
root.title("Consola de Operaciones")
root.geometry("800x1080")
style = ttk.Style()
style.theme_use("clam")
style.configure("TLabel", font=("Arial", 10))
style.configure("TButton", font=("Arial", 10, "bold"))
style.configure("TEntry", font=("Arial", 10))

# Contenedor principal
main_frame = ttk.Frame(root, padding="10")
main_frame.pack(fill="both", expand=True)

# Sección del título del Ticket
ticket_frame = ttk.LabelFrame(main_frame, text="Información del Ticket", padding="10")
ticket_frame.grid(row=0, column=0, columnspan=2, pady=10, sticky="ew")

ttk.Label(ticket_frame, text="Ticket #:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
ticket_entry = ttk.Entry(ticket_frame, width=20)
ticket_entry.insert(0, obtener_siguiente_ticket())  # Ticket inicial
ticket_entry.config(state="disabled")
ticket_entry.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(ticket_frame, text="Fecha de Reporte:").grid(row=0, column=2, padx=5, pady=5, sticky="e")
fecha_entry = ttk.Entry(ticket_frame, width=20)
fecha_entry.grid(row=0, column=3, padx=5, pady=5)

# Detalles del Usuario
user_frame = ttk.LabelFrame(main_frame, text="Detalles del Usuario", padding="10")
user_frame.grid(row=1, column=0, columnspan=2, pady=10, sticky="ew")

user_labels = ["Nombre del Usuario", "Técnico", "Tipo de Usuario", "Status del Usuario",
               "Departamento", "División", "Cargo", "Dirección", "Equipo Asignado", "Ubicación"]
user_entries = []

for i, label in enumerate(user_labels):
    ttk.Label(user_frame, text=label + ":").grid(row=i, column=0, padx=5, pady=5, sticky="w")
    entry = ttk.Entry(user_frame, width=40)
    entry.grid(row=i, column=1, padx=5, pady=5)
    user_entries.append(entry)

# Información de la Incidencia
incident_frame = ttk.LabelFrame(main_frame, text="Información de la Incidencia", padding="10")
incident_frame.grid(row=2, column=0, columnspan=2, pady=10, sticky="ew")

ttk.Label(incident_frame, text="Causa Probable:").grid(row=0, column=0, padx=5, pady=5, sticky="w")
causa_entry = ttk.Entry(incident_frame, width=80)
causa_entry.grid(row=0, column=1, padx=5, pady=5)

ttk.Label(incident_frame, text="Descripción:").grid(row=1, column=0, padx=5, pady=5, sticky="nw")
desc_text = tk.Text(incident_frame, width=80, height=5, font=("Arial", 10))
desc_text.grid(row=1, column=1, padx=5, pady=5)

ttk.Label(incident_frame, text="Status del Ticket:").grid(row=2, column=0, padx=5, pady=5, sticky="w")
status_combobox = ttk.Combobox(incident_frame, values=["Abierto", "En Proceso", "Cerrado"], width=20)
status_combobox.grid(row=2, column=1, padx=5, pady=5)

ttk.Label(incident_frame, text="Motivo del Status:").grid(row=3, column=0, padx=5, pady=5, sticky="w")
motivo_combobox = ttk.Combobox(incident_frame, values=["Sin comentarios", "En espera de información", "Solucionado"], width=20)
motivo_combobox.grid(row=3, column=1, padx=5, pady=5)

# Notas de Resolución
resolution_frame = ttk.LabelFrame(main_frame, text="Notas de Resolución", padding="10")
resolution_frame.grid(row=3, column=0, columnspan=2, pady=10, sticky="ew")

resol_text = tk.Text(resolution_frame, width=80, height=5, font=("Arial", 10))
resol_text.grid(row=0, column=0, padx=5, pady=5)

# Botones de Acción
button_frame = ttk.Frame(main_frame)
button_frame.grid(row=4, column=0, columnspan=2, pady=10, sticky="ew")

ttk.Button(button_frame, text="Guardar en PDF", command=guardar_pdf).pack(pady=10)

root.mainloop()
