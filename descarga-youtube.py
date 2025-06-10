import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import yt_dlp
import os
import threading
from pathlib import Path

class YouTubeDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("Descargador de Videos de YouTube")
        self.root.geometry("600x400")
        self.root.resizable(True, True)
        
        # Variables
        self.download_path = str(Path.home() / "Videos")
        self.is_downloading = False
        
        self.setup_ui()
        
    def setup_ui(self):
        # Frame principal
        main_frame = ttk.Frame(self.root, padding="20")
        main_frame.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        
        # Configurar grid weights
        self.root.columnconfigure(0, weight=1)
        self.root.rowconfigure(0, weight=1)
        main_frame.columnconfigure(1, weight=1)
        
        # Título
        title_label = ttk.Label(main_frame, text="Descargador de Videos de YouTube", 
                               font=("Arial", 16, "bold"))
        title_label.grid(row=0, column=0, columnspan=3, pady=(0, 20))
        
        # URL input
        ttk.Label(main_frame, text="URL del video:").grid(row=1, column=0, sticky=tk.W, pady=(0, 10))
        self.url_var = tk.StringVar()
        self.url_entry = ttk.Entry(main_frame, textvariable=self.url_var, width=50)
        self.url_entry.grid(row=1, column=1, sticky=(tk.W, tk.E), pady=(0, 10), padx=(10, 0))
        
        # Botón pegar desde clipboard
        paste_btn = ttk.Button(main_frame, text="Pegar", command=self.paste_url)
        paste_btn.grid(row=1, column=2, padx=(10, 0), pady=(0, 10))
        
        # Carpeta de descarga
        ttk.Label(main_frame, text="Carpeta de descarga:").grid(row=2, column=0, sticky=tk.W, pady=(0, 10))
        self.path_var = tk.StringVar(value=self.download_path)
        path_entry = ttk.Entry(main_frame, textvariable=self.path_var, width=50, state="readonly")
        path_entry.grid(row=2, column=1, sticky=(tk.W, tk.E), pady=(0, 10), padx=(10, 0))
        
        # Botón cambiar carpeta
        browse_btn = ttk.Button(main_frame, text="Cambiar", command=self.browse_folder)
        browse_btn.grid(row=2, column=2, padx=(10, 0), pady=(0, 10))
        
        # Calidad de video
        ttk.Label(main_frame, text="Calidad:").grid(row=3, column=0, sticky=tk.W, pady=(0, 10))
        self.quality_var = tk.StringVar(value="Mejor calidad disponible")
        quality_combo = ttk.Combobox(main_frame, textvariable=self.quality_var, 
                                   values=["Mejor calidad disponible", "720p", "480p", "360p", "Solo audio (MP3)"])
        quality_combo.grid(row=3, column=1, sticky=(tk.W, tk.E), pady=(0, 10), padx=(10, 0))
        quality_combo.state(['readonly'])
        
        # Botón descargar
        self.download_btn = ttk.Button(main_frame, text="Descargar", command=self.start_download)
        self.download_btn.grid(row=4, column=0, columnspan=3, pady=20)
        
        # Barra de progreso
        self.progress_var = tk.StringVar(value="Listo para descargar")
        progress_label = ttk.Label(main_frame, textvariable=self.progress_var)
        progress_label.grid(row=5, column=0, columnspan=3, pady=(0, 10))
        
        self.progress_bar = ttk.Progressbar(main_frame, mode='indeterminate')
        self.progress_bar.grid(row=6, column=0, columnspan=3, sticky=(tk.W, tk.E), pady=(0, 10))
        
        # Área de información del video
        info_frame = ttk.LabelFrame(main_frame, text="Información del video", padding="10")
        info_frame.grid(row=7, column=0, columnspan=3, sticky=(tk.W, tk.E, tk.N, tk.S), pady=10)
        info_frame.columnconfigure(0, weight=1)
        
        self.info_text = tk.Text(info_frame, height=8, wrap=tk.WORD)
        scrollbar = ttk.Scrollbar(info_frame, orient="vertical", command=self.info_text.yview)
        self.info_text.configure(yscrollcommand=scrollbar.set)
        
        self.info_text.grid(row=0, column=0, sticky=(tk.W, tk.E, tk.N, tk.S))
        scrollbar.grid(row=0, column=1, sticky=(tk.N, tk.S))
        
        # Configurar weights para el frame de info
        main_frame.rowconfigure(7, weight=1)
        
    def paste_url(self):
        try:
            clipboard_content = self.root.clipboard_get()
            if "youtube.com" in clipboard_content or "youtu.be" in clipboard_content:
                self.url_var.set(clipboard_content)
                self.get_video_info()
            else:
                messagebox.showwarning("Advertencia", "El contenido del portapapeles no parece ser un enlace de YouTube")
        except tk.TclError:
            messagebox.showerror("Error", "No se pudo acceder al portapapeles")
    
    def browse_folder(self):
        folder = filedialog.askdirectory(initialdir=self.download_path)
        if folder:
            self.download_path = folder
            self.path_var.set(folder)
    
    def get_video_info(self):
        url = self.url_var.get().strip()
        if not url:
            return
            
        def fetch_info():
            try:
                ydl_opts = {
                    'quiet': True,
                    'no_warnings': True,
                }
                with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                    info = ydl.extract_info(url, download=False)
                    
                    # Mostrar información en la UI
                    self.root.after(0, lambda: self.display_video_info(info))
                    
            except Exception as e:
                self.root.after(0, lambda: self.info_text.delete(1.0, tk.END))
                self.root.after(0, lambda: self.info_text.insert(tk.END, f"Error al obtener información: {str(e)}"))
        
        threading.Thread(target=fetch_info, daemon=True).start()
    
    def display_video_info(self, info):
        self.info_text.delete(1.0, tk.END)
        
        title = info.get('title', 'N/A')
        uploader = info.get('uploader', 'N/A')
        duration = info.get('duration', 0)
        view_count = info.get('view_count', 0)
        upload_date = info.get('upload_date', 'N/A')
        
        # Formatear duración
        if duration:
            hours = duration // 3600
            minutes = (duration % 3600) // 60
            seconds = duration % 60
            duration_str = f"{hours:02d}:{minutes:02d}:{seconds:02d}" if hours > 0 else f"{minutes:02d}:{seconds:02d}"
        else:
            duration_str = "N/A"
        
        # Formatear fecha
        if upload_date and upload_date != 'N/A':
            try:
                upload_date = f"{upload_date[6:8]}/{upload_date[4:6]}/{upload_date[0:4]}"
            except:
                pass
        
        info_text = f"""Título: {title}
Canal: {uploader}
Duración: {duration_str}
Visualizaciones: {view_count:,} vistas
Fecha de subida: {upload_date}

Descripción:
{info.get('description', 'Sin descripción')[:300]}{'...' if len(info.get('description', '')) > 300 else ''}"""
        
        self.info_text.insert(tk.END, info_text)
    
    def start_download(self):
        if self.is_downloading:
            messagebox.showwarning("Advertencia", "Ya hay una descarga en progreso")
            return
            
        url = self.url_var.get().strip()
        if not url:
            messagebox.showerror("Error", "Por favor ingresa una URL")
            return
        
        if not os.path.exists(self.download_path):
            try:
                os.makedirs(self.download_path)
            except Exception as e:
                messagebox.showerror("Error", f"No se pudo crear la carpeta: {str(e)}")
                return
        
        self.is_downloading = True
        self.download_btn.config(state="disabled")
        self.progress_bar.start()
        self.progress_var.set("Descargando...")
        
        threading.Thread(target=self.download_video, daemon=True).start()
    
    def download_video(self):
        try:
            url = self.url_var.get().strip()
            quality = self.quality_var.get()
            
            # Configurar opciones según la calidad seleccionada
            if quality == "Solo audio (MP3)":
                ydl_opts = {
                    'format': 'bestaudio/best',
                    'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
                    'postprocessors': [{
                        'key': 'FFmpegExtractAudio',
                        'preferredcodec': 'mp3',
                        'preferredquality': '192',
                    }],
                }
            else:
                format_selector = {
                    "Mejor calidad disponible": "best",
                    "720p": "best[height<=720]",
                    "480p": "best[height<=480]", 
                    "360p": "best[height<=360]"
                }
                
                ydl_opts = {
                    'format': format_selector.get(quality, "best"),
                    'outtmpl': os.path.join(self.download_path, '%(title)s.%(ext)s'),
                }
            
            with yt_dlp.YoutubeDL(ydl_opts) as ydl:
                ydl.download([url])
            
            # Descarga completada
            self.root.after(0, self.download_completed)
            
        except Exception as e:
            self.root.after(0, lambda: self.download_failed(str(e)))
    
    def download_completed(self):
        self.is_downloading = False
        self.download_btn.config(state="normal")
        self.progress_bar.stop()
        self.progress_var.set("¡Descarga completada!")
        messagebox.showinfo("Éxito", f"Video descargado exitosamente en:\n{self.download_path}")
        
        # Preguntar si quiere abrir la carpeta
        if messagebox.askyesno("Abrir carpeta", "¿Quieres abrir la carpeta de descarga?"):
            try:
                os.startfile(self.download_path)  # Windows
            except:
                try:
                    os.system(f'open "{self.download_path}"')  # macOS
                except:
                    os.system(f'xdg-open "{self.download_path}"')  # Linux
    
    def download_failed(self, error_msg):
        self.is_downloading = False
        self.download_btn.config(state="normal")
        self.progress_bar.stop()
        self.progress_var.set("Error en la descarga")
        messagebox.showerror("Error", f"Error al descargar el video:\n{error_msg}")

def main():
    root = tk.Tk()
    app = YouTubeDownloader(root)
    
    # Bind para obtener info del video cuando se pega URL
    def on_url_change(*args):
        url = app.url_var.get().strip()
        if url and ("youtube.com" in url or "youtu.be" in url):
            app.root.after(1000, app.get_video_info)  # Delay de 1 segundo
    
    app.url_var.trace("w", on_url_change)
    
    root.mainloop()

if __name__ == "__main__":
    main()