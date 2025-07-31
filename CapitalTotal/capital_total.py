from CapitalFunctions import eliminar_fila, editar_fila, borrar_historial
import tkinter as tk
from tkinter import messagebox, simpledialog
from datetime import datetime
import pandas as pd
import os

class CapitalApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Registro de Capital")
        self.instituciones = ["Banco A", "Banco B"]
        self.entries = {}

        self.setup_ui()

    def setup_ui(self):
        # Entrada de fecha
        tk.Label(self.root, text="Fecha (YYYY-MM-DD):").grid(row=0, column=0, sticky='w')
        self.fecha_entry = tk.Entry(self.root)
        self.fecha_entry.grid(row=0, column=1)

        # Área para montos por institución
        self.inputs_frame = tk.Frame(self.root)
        self.inputs_frame.grid(row=1, column=0, columnspan=3, pady=10)
        self.draw_instituciones()

        # Botones de acción
        tk.Button(self.root, text="Agregar Institución", command=self.agregar_institucion).grid(row=2, column=0, pady=5)
        tk.Button(self.root, text="Eliminar Institución", command=self.eliminar_institucion).grid(row=2, column=1, pady=5)
        tk.Button(self.root, text="Guardar Registro", command=self.guardar_datos).grid(row=2, column=2, pady=5)
        tk.Button(self.root, text="Ver historial", command=self.ver_historial).grid(row=3, column=1, pady=10)

    def draw_instituciones(self):
        for widget in self.inputs_frame.winfo_children():
            widget.destroy()
        self.entries.clear()

        for i, nombre in enumerate(self.instituciones):
            tk.Label(self.inputs_frame, text=nombre).grid(row=i, column=0, sticky='w')
            entry = tk.Entry(self.inputs_frame)
            entry.grid(row=i, column=1)
            self.entries[nombre] = entry

    def agregar_institucion(self):
        ventana = tk.Toplevel(self.root)
        ventana.title("Agregar institución")
        ventana.geometry("300x120")

        tk.Label(ventana, text="Nombre de la nueva institución:").pack(pady=5)
        entry_nombre = tk.Entry(ventana)
        entry_nombre.pack(pady=5)

        def confirmar():
            nueva = entry_nombre.get().strip()
            if not nueva:
                messagebox.showwarning("Advertencia", "Debes ingresar un nombre.")
            elif nueva in self.instituciones:
                messagebox.showwarning("Advertencia", f"'{nueva}' ya existe.")
            else:
                self.instituciones.append(nueva)
                self.draw_instituciones()
                ventana.destroy()
                messagebox.showinfo("Agregado", f"'{nueva}' fue añadida correctamente.")

        tk.Button(ventana, text="Agregar", command=confirmar).pack(pady=5)

    def eliminar_institucion(self):
        if not self.instituciones:
            messagebox.showinfo("Aviso", "No hay instituciones para eliminar.")
            return

        ventana = tk.Toplevel(self.root)
        ventana.title("Eliminar institución")
        ventana.geometry("300x100")

        tk.Label(ventana, text="Selecciona una institución a eliminar:").pack(pady=5)
        seleccion = tk.StringVar(ventana)
        seleccion.set(self.instituciones[0])

        menu = tk.OptionMenu(ventana, seleccion, *self.instituciones)
        menu.pack()

        def confirmar():
            nombre = seleccion.get()
            if nombre in self.instituciones:
                self.instituciones.remove(nombre)
                self.draw_instituciones()
                ventana.destroy()
                messagebox.showinfo("Eliminado", f"'{nombre}' fue eliminada.")
            else:
                messagebox.showerror("Error", "Institución no encontrada.")

        tk.Button(ventana, text="Eliminar", command=confirmar).pack(pady=5)

    def guardar_datos(self):
        fecha = self.fecha_entry.get()
        if not fecha:
            fecha = datetime.today().strftime('%Y-%m-%d')
        try:
            datetime.strptime(fecha, '%Y-%m-%d')
        except ValueError:
            messagebox.showerror("Error", "Fecha inválida. Usa el formato YYYY-MM-DD.")
            return

        datos = {'Fecha': fecha}
        total = 0
        for nombre, entry in self.entries.items():
            valor = entry.get()
            try:
                monto = float(valor) if valor else 0
            except ValueError:
                messagebox.showerror("Error", f"El valor de '{nombre}' no es válido.")
                return
            datos[nombre] = monto
            total += monto
        datos['Total'] = total

        nuevo_df = pd.DataFrame([datos])
        archivo = "capital_registros.csv"

        try:
            df_existente = pd.read_csv(archivo)
            df_actualizado = pd.concat([df_existente, nuevo_df], ignore_index=True)
        except FileNotFoundError:
            df_actualizado = nuevo_df

        try:
            df_actualizado.fillna(0).to_csv(archivo, index=False)
            messagebox.showinfo("Guardado", f"Datos registrados correctamente en '{archivo}'.\nTotal: {total}")
            os.startfile(archivo)
        except Exception as e:
            messagebox.showerror("Error al guardar", str(e))

    def ver_historial(self):
        archivo = "capital_registros.csv"

        try:
            df = pd.read_csv(archivo).fillna(0)
        except FileNotFoundError:
            messagebox.showinfo("Sin registros", "Aún no hay registros guardados.")
            return

        ventana = tk.Toplevel(self.root)
        ventana.title("Historial de Registros")
        ventana.geometry("1000x500")

        canvas = tk.Canvas(ventana)
        scrollbar = tk.Scrollbar(ventana, orient="vertical", command=canvas.yview)
        scrollable_frame = tk.Frame(canvas)

        scrollable_frame.bind(
            "<Configure>",
            lambda e: canvas.configure(scrollregion=canvas.bbox("all"))
        )

        canvas.create_window((0, 0), window=scrollable_frame, anchor="nw")
        canvas.configure(yscrollcommand=scrollbar.set)

        canvas.pack(side="left", fill="both", expand=True)
        scrollbar.pack(side="right", fill="y")

        for j, col in enumerate(df.columns):
            tk.Label(scrollable_frame, text=col, borderwidth=1, relief="solid", width=15, bg="lightgray").grid(row=0, column=j)
        tk.Label(scrollable_frame, text="Acciones", borderwidth=1, relief="solid", width=20, bg="lightgray").grid(row=0, column=len(df.columns))

        for i, fila in df.iterrows():
            for j, valor in enumerate(fila):
                valor = 0 if pd.isna(valor) else valor
                tk.Label(scrollable_frame, text=valor, borderwidth=1, relief="solid", width=15).grid(row=i+1, column=j)

            tk.Button(scrollable_frame, text="Editar", command=lambda idx=i: editar_fila(idx, df, ventana, self.ver_historial, self.root)).grid(row=i+1, column=len(df.columns))
            tk.Button(scrollable_frame, text="Eliminar", command=lambda idx=i: eliminar_fila(idx, df, ventana, self.ver_historial)).grid(row=i+1, column=len(df.columns)+1)

        tk.Button(ventana, text="🗑 Borrar historial completo", bg="red", fg="white", command=lambda: borrar_historial(ventana)).pack(pady=10)

# Ejecutar la app
if __name__ == "__main__":
    root = tk.Tk()
    app = CapitalApp(root)
    root.mainloop()
