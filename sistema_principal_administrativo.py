import tkinter as tk
from tkinter import ttk, messagebox
import os
import glob
import subprocess
import sqlite3

# Función para abrir un ticket en PDF
def abrir_pdf(ticket_num):
    pdf_filename = f"ticket_{ticket_num}.pdf"
    if os.path.exists(pdf_filename):
        try:
            if os.name == 'posix':
                subprocess.call(('xdg-open', pdf_filename))
            else:
                os.startfile(pdf_filename)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo abrir el archivo PDF: {e}")
    else:
        messagebox.showwarning("Advertencia", f"No se encontró el archivo '{pdf_filename}'.")

# Función para inicializar la base de datos
def inicializar_base_datos():
    if os.path.exists("reportes.db"):
        os.remove("reportes.db")

    conn = sqlite3.connect("reportes.db")
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS reportes (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ticket_num TEXT NOT NULL UNIQUE,
            usuario TEXT NOT NULL,
            tipo_reporte TEXT NOT NULL,
            cliente TEXT NOT NULL,
            pdf_filename TEXT NOT NULL
        )
    ''')
    conn.commit()
    conn.close()

# Ejecuta la función de inicialización
inicializar_base_datos()

# Función para actualizar la lista de reportes
def actualizar_lista_reportes(lista_reportes, filtro=""):
    lista_reportes.delete(*lista_reportes.get_children())
    pdf_files = glob.glob("ticket_*.pdf")
    for file in pdf_files:
        ticket_num = file.split("_")[1].split(".")[0]
        if filtro.lower() in ticket_num.lower():
            lista_reportes.insert("", "end", values=(ticket_num, file))

# Función para manejar el doble clic en un reporte de la lista
def on_doble_click(event):
    selected_item = lista_reportes.selection()
    if selected_item:
        ticket_num = lista_reportes.item(selected_item, "values")[0]
        abrir_pdf(ticket_num)

# Función para abrir la consola de operación
def abrir_consola_operacion():
    try:
        subprocess.Popen(["python", "consola_operacion.py"])
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir la consola de operación: {e}")

# Función para abrir la consola de administrador
def abrir_consola_administrador():
    try:
        subprocess.Popen(["python", "consola_administrador.py"])
    except Exception as e:
        messagebox.showerror("Error", f"No se pudo abrir la consola de administrador: {e}")

# Función para buscar reportes
def buscar_reportes(lista_reportes, buscar_entry):
    filtro = buscar_entry.get()
    actualizar_lista_reportes(lista_reportes, filtro)

# Configuración de la ventana principal
root = tk.Tk()
root.title("Sistema Principal de Gestión de Reportes")
root.geometry("900x600")
root.configure(bg="#f4f4f9")

# Estilos de ttk
style = ttk.Style()
style.theme_use("clam")
style.configure("Treeview.Heading", font=("Arial", 12, "bold"), background="#4a90e2", foreground="white")
style.configure("Treeview", font=("Arial", 11), rowheight=25)
style.map("Treeview", background=[("selected", "#4a90e2")])

# Panel de búsqueda
panel_busqueda = tk.Frame(root, bg="#f4f4f9")
panel_busqueda.pack(pady=10)

buscar_label = tk.Label(panel_busqueda, text="Buscar Ticket:", font=("Arial", 12), bg="#f4f4f9")
buscar_label.grid(row=0, column=0, padx=5, sticky="w")
buscar_entry = tk.Entry(panel_busqueda, font=("Arial", 12), width=30)
buscar_entry.grid(row=0, column=1, padx=5)
buscar_button = tk.Button(
    panel_busqueda, text="Buscar", font=("Arial", 12, "bold"), bg="#4a90e2", fg="white",
    command=lambda: buscar_reportes(lista_reportes, buscar_entry)
)
buscar_button.grid(row=0, column=2, padx=5)

# Línea de reportes
linea_reportes_frame = tk.Frame(root, bg="#f4f4f9")
linea_reportes_frame.pack(pady=10, fill="both", expand=True)

lista_reportes = ttk.Treeview(linea_reportes_frame, columns=("Ticket", "Archivo"), show="headings")
lista_reportes.heading("Ticket", text="Número de Ticket")
lista_reportes.heading("Archivo", text="Archivo PDF")
lista_reportes.pack(fill="both", expand=True, padx=20, pady=10)

lista_reportes.bind("<Double-1>", on_doble_click)


# Cargar la lista inicial de reportes
actualizar_lista_reportes(lista_reportes)

# Ejecutar la ventana principal
root.mainloop()
