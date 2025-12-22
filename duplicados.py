"Duplicados 3"
import os
import hashlib
import shutil
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

def hash_archivo(ruta, bloque=65536):
    """Genera el hash SHA256 de un archivo."""
    sha = hashlib.sha256()
    with open(ruta, "rb") as f:
        while chunk := f.read(bloque):
            sha.update(chunk)
    return sha.hexdigest()

def buscar_duplicados(directorio):
    """Busca archivos duplicados en un directorio con barra de progreso y log en ventana."""
    archivos = []
    for carpeta, _, files in os.walk(directorio):
        for f in files:
            archivos.append(os.path.join(carpeta, f))

    total = len(archivos)
    hashes = {}
    duplicados = []

    # Configurar barra de progreso
    progress["maximum"] = total
    progress["value"] = 0
    root.update_idletasks()

    # Limpiar área de texto
    text_log.delete("1.0", tk.END)

    for i, ruta in enumerate(archivos, start=1):
        try:
            h = hash_archivo(ruta)
            if h in hashes:
                duplicados.append((ruta, hashes[h]))
            else:
                hashes[h] = ruta
        except Exception as e:
            print(f"No se pudo leer {ruta}: {e}")

        # Actualizar barra y log
        progress["value"] = i
        text_log.insert(tk.END, f"Procesando: {ruta}\n")
        text_log.see(tk.END)  # Hace scroll automático
        root.update_idletasks()

    return duplicados

def seleccionar_directorio():
    carpeta = filedialog.askdirectory()
    if carpeta:
        duplicados = buscar_duplicados(carpeta)
        mostrar_resultados(duplicados)

def mostrar_resultados(duplicados):
    for item in tree.get_children():
        tree.delete(item)

    if duplicados:
        for dup in duplicados:
            tree.insert("", "end", values=(dup[0], dup[1]))
        total = len(duplicados)
        lbl_resumen.config(text=f"Se encontraron {total} archivos duplicados.")
        messagebox.showinfo("Resumen", f"Se encontraron {total} archivos duplicados en el análisis.")
    else:
        lbl_resumen.config(text="No se encontraron duplicados.")
        messagebox.showinfo("Resultado", "No se encontraron duplicados.")

def eliminar_seleccionados():
    seleccion = tree.selection()
    if not seleccion:
        messagebox.showwarning("Atención", "No has seleccionado ningún archivo para eliminar.")
        return

    confirm = messagebox.askyesno("Confirmar", "¿Seguro que deseas eliminar los archivos seleccionados?")
    if confirm:
        for item in seleccion:
            archivo = tree.item(item, "values")[0]
            try:
                os.remove(archivo)
                tree.delete(item)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo eliminar {archivo}: {e}")
        messagebox.showinfo("Éxito", "Archivos eliminados correctamente.")

def mover_seleccionados():
    seleccion = tree.selection()
    if not seleccion:
        messagebox.showwarning("Atención", "No has seleccionado ningún archivo para mover.")
        return

    carpeta_respaldo = filedialog.askdirectory(title="Selecciona carpeta de respaldo")
    if not carpeta_respaldo:
        return

    for item in seleccion:
        archivo = tree.item(item, "values")[0]
        try:
            nombre = os.path.basename(archivo)
            destino = os.path.join(carpeta_respaldo, nombre)
            shutil.move(archivo, destino)
            tree.delete(item)
        except Exception as e:
            messagebox.showerror("Error", f"No se pudo mover {archivo}: {e}")

    messagebox.showinfo("Éxito", "Archivos movidos a la carpeta de respaldo.")

# Interfaz gráfica
root = tk.Tk()
root.title("Detector de Archivos Duplicados")

frame = tk.Frame(root)
frame.pack(pady=10)

btn = tk.Button(frame, text="Seleccionar Carpeta", command=seleccionar_directorio)
btn.pack(side="left", padx=5)

btn_del = tk.Button(frame, text="Eliminar Seleccionados", command=eliminar_seleccionados)
btn_del.pack(side="left", padx=5)

btn_move = tk.Button(frame, text="Mover a Respaldo", command=mover_seleccionados)
btn_move.pack(side="left", padx=5)

cols = ("Archivo", "Duplicado de")
tree = ttk.Treeview(root, columns=cols, show="headings", selectmode="extended")
for col in cols:
    tree.heading(col, text=col)
    tree.column(col, width=400)

tree.pack(fill="both", expand=True)

# Barra de progreso
progress = ttk.Progressbar(root, orient="horizontal", length=600, mode="determinate")
progress.pack(pady=5)

# Área de texto con scroll para mostrar archivos procesados
frame_log = tk.Frame(root)
frame_log.pack(fill="both", expand=True, pady=5)

scrollbar = tk.Scrollbar(frame_log)
scrollbar.pack(side="right", fill="y")

text_log = tk.Text(frame_log, height=10, wrap="none", yscrollcommand=scrollbar.set)
text_log.pack(fill="both", expand=True)
scrollbar.config(command=text_log.yview)

lbl_resumen = tk.Label(root, text="Esperando análisis...")
lbl_resumen.pack(pady=5)

root.mainloop()