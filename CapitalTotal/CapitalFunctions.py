import pandas as pd
import os
import tkinter as tk
from tkinter import messagebox
from datetime import datetime

def eliminar_fila(index, df, ventana, refrescar_callback):
    confirm = messagebox.askyesno("Confirmar", "¿Seguro que quieres eliminar este registro?")
    if confirm:
        df = df.drop(index).reset_index(drop=True)
        df.to_csv("capital_registros.csv", index=False)
        ventana.destroy()
        refrescar_callback()

def editar_fila(index, df, ventana, refrescar_callback, root):
    fila = df.loc[index]

    editor = tk.Toplevel(root)
    editor.title("Editar registro")
    editor.geometry("400x600")

    nuevas_entradas = {}
    tk.Label(editor, text=f"Editando fila #{index+1}", font=("Arial", 12, "bold")).pack(pady=10)

    for i, (col, val) in enumerate(fila.items()):
        tk.Label(editor, text=col).pack()
        entry = tk.Entry(editor)
        entry.insert(0, val)
        entry.pack()
        nuevas_entradas[col] = entry

    def guardar_cambios():
        for col, entry in nuevas_entradas.items():
            if col == "Fecha":
                continue  # No permitir editar la fecha
            val = entry.get()
            try:
                val = float(val) if val.strip() else 0
            except ValueError:
                messagebox.showerror("Error", f"'{col}' debe ser numérico.")
                return
            df.at[index, col] = val

        # Recalcular Total si existe
        if 'Total' in df.columns:
            cols_dinero = [c for c in df.columns if c not in ['Fecha', 'Total']]
            df.at[index, 'Total'] = sum(float(df.at[index, c]) for c in cols_dinero)

        df.to_csv("capital_registros.csv", index=False)
        editor.destroy()
        ventana.destroy()
        refrescar_callback()

    tk.Button(editor, text="Guardar cambios", command=guardar_cambios).pack(pady=15)

def borrar_historial(ventana):
    confirm = messagebox.askyesno("Confirmar", "¿Seguro que quieres borrar TODO el historial?")
    if confirm:
        try:
            os.remove("capital_registros.csv")
            ventana.destroy()
            messagebox.showinfo("Listo", "Historial eliminado correctamente.")
        except FileNotFoundError:
            messagebox.showinfo("Aviso", "No hay historial que borrar.")
        except Exception as e:
            messagebox.showerror("Error", str(e))
