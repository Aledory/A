import tkinter as tk
from tkinter import ttk, messagebox
import sqlite3

import time

def execute_db(self, query, params=()):
    for _ in range(5):  # Reintenta 5 veces
        try:
            conn = sqlite3.connect("tickets.db")
            cursor = conn.cursor()
            cursor.execute(query, params)
            conn.commit()
            conn.close()
            return
        except sqlite3.OperationalError as e:
            if "locked" in str(e).lower():
                time.sleep(0.1)  # Espera 100ms antes de reintentar
            else:
                raise e
    messagebox.showerror("Error", "La base de datos está bloqueada. Inténtalo de nuevo.")

# Configuración inicial de la base de datos
def setup_database():
    conn = sqlite3.connect("tickets.db")
    cursor = conn.cursor()
    cursor.execute("PRAGMA journal_mode=WAL")  # Modo WAL para concurrencia
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS tickets (
            ticket_num TEXT PRIMARY KEY,
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
        )
    """)
    conn.commit()
    conn.close()

# Clase principal del formulario
class TicketManagerApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Gestor de Tickets")

        # Variables para los campos
        self.ticket_num_var = tk.StringVar()
        self.fecha_reporte_var = tk.StringVar()
        self.nombre_usuario_var = tk.StringVar()
        self.user_id_var = tk.StringVar()
        self.tipo_usuario_var = tk.StringVar()
        self.status_usuario_var = tk.StringVar()
        self.departamento_var = tk.StringVar()
        self.division_var = tk.StringVar()
        self.cargo_var = tk.StringVar()
        self.direccion_var = tk.StringVar()
        self.equipo_var = tk.StringVar()
        self.ubicacion_var = tk.StringVar()
        self.causa_var = tk.StringVar()
        self.descripcion_var = tk.StringVar()
        self.status_ticket_var = tk.StringVar()
        self.motivo_status_var = tk.StringVar()
        self.resolucion_var = tk.StringVar()
        self.search_var = tk.StringVar()

        # Configurar interfaz
        self.setup_ui()
        self.load_tickets()

    def setup_ui(self):
        # Formulario de entrada
        form_frame = tk.LabelFrame(self.root, text="Datos del Ticket", padx=10, pady=10)
        form_frame.pack(fill="x", padx=10, pady=5)

        fields = [
            ("Número Ticket", self.ticket_num_var),
            ("Fecha Reporte", self.fecha_reporte_var),
            ("Nombre Usuario", self.nombre_usuario_var),
            ("ID Usuario", self.user_id_var),
            ("Tipo Usuario", self.tipo_usuario_var),
            ("Status Usuario", self.status_usuario_var),
            ("Departamento", self.departamento_var),
            ("División", self.division_var),
            ("Cargo", self.cargo_var),
            ("Dirección", self.direccion_var),
            ("Equipo", self.equipo_var),
            ("Ubicación", self.ubicacion_var),
            ("Causa", self.causa_var),
            ("Descripción", self.descripcion_var),
            ("Status Ticket", self.status_ticket_var),
            ("Motivo Status", self.motivo_status_var),
            ("Resolución", self.resolucion_var),
        ]

        for idx, (label, var) in enumerate(fields):
            tk.Label(form_frame, text=label + ":").grid(row=idx, column=0, sticky="w")
            tk.Entry(form_frame, textvariable=var).grid(row=idx, column=1)

        # Botones CRUD
        button_frame = tk.Frame(form_frame)
        button_frame.grid(row=len(fields), columnspan=2, pady=5)

        tk.Button(button_frame, text="Guardar", command=self.add_ticket).pack(side="left", padx=5)
        tk.Button(button_frame, text="Actualizar", command=self.update_ticket).pack(side="left", padx=5)
        tk.Button(button_frame, text="Eliminar", command=self.delete_ticket).pack(side="left", padx=5)

        # Campo de búsqueda
        tk.Label(self.root, text="Buscar por número de ticket:").pack(pady=5)
        tk.Entry(self.root, textvariable=self.search_var).pack(fill="x", padx=10)
        tk.Button(self.root, text="Buscar", command=self.search_tickets).pack(pady=5)

        # Tabla de datos
        self.table = ttk.Treeview(self.root, columns=[f"C{i}" for i in range(1, 18)], show="headings")
        self.table.pack(fill="both", expand=True, padx=10, pady=5)

        column_names = [
            "Número Ticket", "Fecha Reporte", "Nombre Usuario", "ID Usuario",
            "Tipo Usuario", "Status Usuario", "Departamento", "División",
            "Cargo", "Dirección", "Equipo", "Ubicación", "Causa",
            "Descripción", "Status Ticket", "Motivo Status", "Resolución"
        ]

        for idx, col_name in enumerate(column_names):
            self.table.heading(f"C{idx+1}", text=col_name)
            self.table.column(f"C{idx+1}", width=100)
        self.table.bind("<ButtonRelease-1>", self.select_row)

    def execute_db(self, query, params=()):
        conn = sqlite3.connect("tickets.db")
        cursor = conn.cursor()
        cursor.execute(query, params)
        conn.commit()
        conn.close()

    def fetch_db(self, query, params=()):
        conn = sqlite3.connect("tickets.db")
        cursor = conn.cursor()
        cursor.execute(query, params)
        rows = cursor.fetchall()
        conn.close()
        return rows

    def add_ticket(self):
        values = (
            self.ticket_num_var.get(), self.fecha_reporte_var.get(),
            self.nombre_usuario_var.get(), self.user_id_var.get(),
            self.tipo_usuario_var.get(), self.status_usuario_var.get(),
            self.departamento_var.get(), self.division_var.get(),
            self.cargo_var.get(), self.direccion_var.get(),
            self.equipo_var.get(), self.ubicacion_var.get(),
            self.causa_var.get(), self.descripcion_var.get(),
            self.status_ticket_var.get(), self.motivo_status_var.get(),
            self.resolucion_var.get()
        )

        if all(values):
            try:
                self.execute_db("""
                    INSERT INTO tickets VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
                """, values)
                self.load_tickets()
                self.clear_fields()
            except sqlite3.IntegrityError:
                messagebox.showerror("Error", "El número de ticket ya existe.")
        else:
            messagebox.showwarning("Validación", "Todos los campos son obligatorios.")

    def update_ticket(self):
        selected_item = self.table.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Seleccione un ticket para actualizar.")
            return

        ticket_num = self.table.item(selected_item)["values"][0]
        values = (
            self.fecha_reporte_var.get(), self.nombre_usuario_var.get(),
            self.user_id_var.get(), self.tipo_usuario_var.get(),
            self.status_usuario_var.get(), self.departamento_var.get(),
            self.division_var.get(), self.cargo_var.get(),
            self.direccion_var.get(), self.equipo_var.get(),
            self.ubicacion_var.get(), self.causa_var.get(),
            self.descripcion_var.get(), self.status_ticket_var.get(),
            self.motivo_status_var.get(), self.resolucion_var.get(), ticket_num
        )

        if all(values[:-1]):
            self.execute_db("""
                UPDATE tickets
                SET fecha_reporte = ?, nombre_usuario = ?, user_id = ?, tipo_usuario = ?, status_usuario = ?,
                    departamento = ?, division = ?, cargo = ?, direccion = ?, equipo = ?, ubicacion = ?,
                    causa = ?, descripcion = ?, status_ticket = ?, motivo_status = ?, resolucion = ?
                WHERE ticket_num = ?
            """, values)
            self.load_tickets()
            self.clear_fields()
        else:
            messagebox.showwarning("Validación", "Todos los campos son obligatorios.")

    def delete_ticket(self):
        selected_item = self.table.selection()
        if not selected_item:
            messagebox.showwarning("Advertencia", "Seleccione un ticket para eliminar.")
            return

        ticket_num = self.table.item(selected_item)["values"][0]
        self.execute_db("DELETE FROM tickets WHERE ticket_num = ?", (ticket_num,))
        self.load_tickets()

    def search_tickets(self):
        query = self.search_var.get()
        rows = self.fetch_db("SELECT * FROM tickets WHERE ticket_num LIKE ?", ('%' + query + '%',))
        self.update_table(rows)

    def load_tickets(self):
        rows = self.fetch_db("SELECT * FROM tickets")
        self.update_table(rows)

    def update_table(self, rows):
        for item in self.table.get_children():
            self.table.delete(item)
        for row in rows:
            self.table.insert("", "end", values=row)

    def select_row(self, event):
        selected_item = self.table.selection()
        if selected_item:
            ticket = self.table.item(selected_item)["values"]
            vars = [
                self.ticket_num_var, self.fecha_reporte_var, self.nombre_usuario_var,
                self.user_id_var, self.tipo_usuario_var, self.status_usuario_var,
                self.departamento_var, self.division_var, self.cargo_var,
                self.direccion_var, self.equipo_var, self.ubicacion_var,
                self.causa_var, self.descripcion_var, self.status_ticket_var,
                self.motivo_status_var, self.resolucion_var
            ]
            for var, value in zip(vars, ticket):
                var.set(value)

    def clear_fields(self):
        vars = [
            self.ticket_num_var, self.fecha_reporte_var, self.nombre_usuario_var,
            self.user_id_var, self.tipo_usuario_var, self.status_usuario_var,
            self.departamento_var, self.division_var, self.cargo_var,
            self.direccion_var, self.equipo_var, self.ubicacion_var,
            self.causa_var, self.descripcion_var, self.status_ticket_var,
            self.motivo_status_var, self.resolucion_var
        ]
        for var in vars:
            var.set("")

# Inicializar la app
if __name__ == "__main__":
    setup_database()
    root = tk.Tk()
    app = TicketManagerApp(root)
    root.mainloop()
