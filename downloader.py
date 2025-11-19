import os
import sys
import subprocess
import threading
import tkinter as tk
import webbrowser
import base64
import tempfile
from tkinter import scrolledtext, messagebox, ttk
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from PIL import Image
from io import BytesIO

ICON_BASE64 = """"""

class IframeCaptureDownloader:
    def __init__(self, root):
        self.root = root
        self.root.title("Video Capture Pro - VycoCode | @vycocode | vycocode.com")
        self.root.geometry("750x580")
        self.root.resizable(False, False)
        
        self.colors = {
            'bg_primary': '#0a0a0a',
            'bg_secondary': '#1a1a1a',
            'accent': '#2a2a2a',
            'success': '#d4d4d4',
            'danger': '#8a8a8a',
            'text': '#e5e5e5',
            'text_secondary': '#9a9a9a'
        }
        
        self.root.configure(bg=self.colors['bg_primary'])
        
        self.driver = None
        self.capturing = False
        self.captured_urls = set()
        self.check_thread = None
        self.default_url = "https://academia.mwcmd.com/"
        
        self.results_folder = "Resultados"
        
        self.create_widgets()
        self.install_dependencies()
        self.set_window_icon()
        
        self.create_results_folder()
    
    def create_results_folder(self):
        """Crea la carpeta Resultados si no existe"""
        try:
            if getattr(sys, 'frozen', False):
                base_path = os.path.dirname(sys.executable)
            else:
                base_path = os.path.dirname(os.path.abspath(__file__))
            
            self.results_folder = os.path.join(base_path, "Resultados")
            
            if not os.path.exists(self.results_folder):
                os.makedirs(self.results_folder)
                self.log(f"✅ Carpeta creada: {self.results_folder}", "success")
            else:
                self.log(f"✅ Carpeta encontrada: {self.results_folder}", "success")
        except Exception as e:
            self.results_folder = os.path.join(os.getcwd(), "Resultados")
            try:
                if not os.path.exists(self.results_folder):
                    os.makedirs(self.results_folder)
                self.log(f"✅ Carpeta creada en: {self.results_folder}", "success")
            except Exception as e2:
                self.log(f"⚠️ Error creando carpeta: {e2}. Usando carpeta actual.", "warning")
                self.results_folder = os.getcwd()
    
    def set_window_icon(self):
        """Crea el icono .ico desde base64 y lo aplica a la ventana"""
        try:
            icon_data = base64.b64decode(ICON_BASE64)
            icon_image = Image.open(BytesIO(icon_data))
            
            temp_dir = tempfile.gettempdir()
            icon_path = os.path.join(temp_dir, 'vycocode_icon.ico')
            
            icon_sizes = [(16, 16), (32, 32), (48, 48), (64, 64)]
            icon_image.save(icon_path, format='ICO', sizes=icon_sizes)
            
            self.root.iconbitmap(icon_path)
            
            self.log("✅ Icono personalizado aplicado", "success")
        except Exception as e:
            self.log(f"⚠️ No se pudo aplicar el icono: {e}", "warning")
    
    def create_widgets(self):
        header_frame = tk.Frame(self.root, bg=self.colors['bg_secondary'], height=70)
        header_frame.pack(fill=tk.X, pady=(0, 15))
        header_frame.pack_propagate(False)
        
        title_label = tk.Label(
            header_frame, 
            text="Video Capture Pro | @vycocode",
            font=("Segoe UI", 18, "bold"),
            bg=self.colors['bg_secondary'],
            fg=self.colors['success']
        )
        title_label.pack(side=tk.LEFT, padx=20, pady=15)
        
        watermark_frame = tk.Frame(header_frame, bg=self.colors['bg_secondary'])
        watermark_frame.pack(side=tk.RIGHT, padx=20)
        
        tk.Label(
            watermark_frame,
            text="@vycocode",
            font=("Segoe UI", 10, "bold"),
            bg=self.colors['bg_secondary'],
            fg=self.colors['success']
        ).pack(anchor=tk.E)
        
        website_label = tk.Label(
            watermark_frame,
            text="vycocode.com",
            font=("Segoe UI", 8),
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_secondary'],
            cursor="hand2"
        )
        website_label.pack(anchor=tk.E)
        website_label.bind("<Button-1>", lambda e: self.open_website())
        
        main_container = tk.Frame(self.root, bg=self.colors['bg_primary'])
        main_container.pack(fill=tk.BOTH, expand=True, padx=20, pady=(0, 15))
        
        url_section = tk.Frame(main_container, bg=self.colors['accent'], bd=0)
        url_section.pack(fill=tk.X, pady=(0, 15), ipady=12, ipadx=15)
        
        tk.Label(
            url_section,
            text="🌐 URL:",
            font=("Segoe UI", 10, "bold"),
            bg=self.colors['accent'],
            fg=self.colors['text']
        ).pack(side=tk.LEFT, padx=(0, 10))
        
        self.url_entry = tk.Entry(
            url_section,
            font=("Segoe UI", 10),
            bg='#0a0a0a',
            fg=self.colors['text'],
            insertbackground=self.colors['text'],
            relief=tk.FLAT,
            bd=0,
            state='readonly',
            readonlybackground='#0a0a0a'
        )
        self.url_entry.config(state=tk.NORMAL)
        self.url_entry.insert(0, self.default_url)
        self.url_entry.config(state='readonly')
        self.url_entry.pack(side=tk.LEFT, fill=tk.X, expand=True, ipady=6)
        
        button_frame = tk.Frame(main_container, bg=self.colors['bg_primary'])
        button_frame.pack(pady=(0, 15))
        
        button_style = {
            'font': ("Segoe UI", 11, "bold"),
            'relief': tk.FLAT,
            'bd': 0,
            'cursor': 'hand2',
            'activebackground': '#4a4a4a'
        }
        
        self.start_button = tk.Button(
            button_frame,
            text="▶ Start Capture",
            command=self.start_capture,
            bg='#3a3a3a',
            fg='white',
            width=16,
            **button_style
        )
        self.start_button.pack(side=tk.LEFT, padx=8, ipady=8)
        
        self.stop_button = tk.Button(
            button_frame,
            text="⏹ Stop Capture",
            command=self.stop_capture,
            bg='#2a2a2a',
            fg='white',
            width=16,
            state=tk.DISABLED,
            **button_style
        )
        self.stop_button.pack(side=tk.LEFT, padx=8, ipady=8)
        
        log_header = tk.Frame(main_container, bg=self.colors['accent'])
        log_header.pack(fill=tk.X, pady=(0, 8), ipady=6, ipadx=10)
        
        tk.Label(
            log_header,
            text="📋 CAPTURADOR DE VIDEO",
            font=("Segoe UI", 10, "bold"),
            bg=self.colors['accent'],
            fg=self.colors['text']
        ).pack(side=tk.LEFT)
        
        self.url_count_label = tk.Label(
            log_header,
            text="(0)",
            font=("Segoe UI", 10),
            bg=self.colors['accent'],
            fg=self.colors['success']
        )
        self.url_count_label.pack(side=tk.LEFT, padx=8)
        
        log_container = tk.Frame(main_container, bg=self.colors['bg_secondary'])
        log_container.pack(fill=tk.BOTH, expand=True, pady=(0, 15))
        
        self.log_area = scrolledtext.ScrolledText(
            log_container,
            height=12,
            font=("Consolas", 9),
            bg='#050505',
            fg='#c9d1d9',
            insertbackground=self.colors['success'],
            relief=tk.FLAT,
            bd=0,
            wrap=tk.WORD
        )
        self.log_area.pack(fill=tk.BOTH, expand=True, padx=2, pady=2)
        
        self.download_button = tk.Button(
            main_container,
            text="⬇ Download All Videos",
            command=self.download_all,
            bg='#3a3a3a',
            fg='white',
            font=("Segoe UI", 11, "bold"),
            relief=tk.FLAT,
            bd=0,
            cursor='hand2',
            activebackground='#4a4a4a'
        )
        self.download_button.pack(fill=tk.X, ipady=10)
        
        status_frame = tk.Frame(self.root, bg=self.colors['bg_secondary'], height=30)
        status_frame.pack(side=tk.BOTTOM, fill=tk.X)
        status_frame.pack_propagate(False)
        
        self.status_label = tk.Label(
            status_frame,
            text="● Ready",
            font=("Segoe UI", 9),
            bg=self.colors['bg_secondary'],
            fg=self.colors['text_secondary'],
            anchor=tk.W
        )
        self.status_label.pack(side=tk.LEFT, padx=15, fill=tk.X, expand=True)
        
        self.add_hover_effects()
    
    def add_hover_effects(self):
        """Añade efectos hover a los botones"""
        def on_enter_start(e):
            if self.start_button['state'] == tk.NORMAL:
                self.start_button['bg'] = '#4a4a4a'
        
        def on_leave_start(e):
            self.start_button['bg'] = '#3a3a3a'
        
        def on_enter_stop(e):
            if self.stop_button['state'] == tk.NORMAL:
                self.stop_button['bg'] = '#3a3a3a'
        
        def on_leave_stop(e):
            self.stop_button['bg'] = '#2a2a2a'
        
        def on_enter_download(e):
            self.download_button['bg'] = '#4a4a4a'
        
        def on_leave_download(e):
            self.download_button['bg'] = '#3a3a3a'
        
        self.start_button.bind("<Enter>", on_enter_start)
        self.start_button.bind("<Leave>", on_leave_start)
        self.stop_button.bind("<Enter>", on_enter_stop)
        self.stop_button.bind("<Leave>", on_leave_stop)
        self.download_button.bind("<Enter>", on_enter_download)
        self.download_button.bind("<Leave>", on_leave_download)
    
    def open_website(self):
        """Abre vycocode.com en el navegador predeterminado"""
        try:
            webbrowser.open("https://vycocode.com")
        except:
            self.log("⚠️ No se pudo abrir el navegador", "warning")
    
    def install_dependencies(self):
        """Instala dependencias necesarias"""
        try:
            import selenium
            import webdriver_manager
            import yt_dlp
            from PIL import Image
            self.log("✅ Todas las dependencias están instaladas", "success")
        except ImportError:
            self.log("🔧 Instalando dependencias necesarias...", "info")
            packages = ["selenium", "webdriver-manager", "yt-dlp", "Pillow"]
            for package in packages:
                try:
                    subprocess.run([sys.executable, "-m", "pip", "install", package], 
                                 check=True, capture_output=True)
                    self.log(f"✅ {package} instalado correctamente", "success")
                except subprocess.CalledProcessError as e:
                    self.log(f"❌ Error instalando {package}: {e}", "error")
    
    def log(self, message, type="info"):
        """Agrega mensaje al área de log con colores"""
        color_map = {
            "success": "#c4c4c4",
            "error": "#8a8a8a",
            "info": "#e5e5e5",
            "warning": "#a5a5a5"
        }
        
        self.log_area.insert(tk.END, message + "\n")
        
        line_start = self.log_area.index("end-2c linestart")
        line_end = self.log_area.index("end-1c")
        
        tag_name = f"color_{type}"
        if tag_name not in self.log_area.tag_names():
            self.log_area.tag_config(tag_name, foreground=color_map.get(type, "#eaeaea"))
        
        self.log_area.tag_add(tag_name, line_start, line_end)
        self.log_area.see(tk.END)
        self.root.update()
    
    def update_status(self, message, type="info"):
        """Actualiza la barra de estado con indicador de color"""
        indicators = {
            "success": "●",
            "error": "●",
            "warning": "●",
            "info": "●"
        }
        colors = {
            "success": "#c4c4c4",
            "error": "#8a8a8a",
            "warning": "#a5a5a5",
            "info": "#9a9a9a"
        }
        
        indicator = indicators.get(type, "●")
        self.status_label.config(
            text=f"{indicator} {message}",
            fg=colors.get(type, "#b0b0b0")
        )
        self.root.update()
    
    def update_url_count(self):
        """Actualiza el contador de URLs"""
        self.url_count_label.config(text=f"({len(self.captured_urls)})")
    
    def start_capture(self):
        """Inicia la captura de URLs"""
        if self.capturing:
            return
        
        url = self.url_entry.get().strip()
        if not url:
            messagebox.showerror("Error", "Por favor ingresa una URL válida")
            return
        
        self.capturing = True
        self.start_button.config(state=tk.DISABLED)
        self.stop_button.config(state=tk.NORMAL)
        
        self.log("━" * 70, "info")
        self.log("🚀 Iniciando captura de URLs...", "success")
        self.log("━" * 70, "info")
        
        threading.Thread(target=self.open_browser, args=(url,), daemon=True).start()
    
    def open_browser(self, url):
        """Abre el navegador Chromium y comienza la captura"""
        try:
            self.update_status("Iniciando navegador...", "info")
            
            chrome_options = Options()
            chrome_options.add_argument("--start-maximized")
            chrome_options.add_experimental_option("excludeSwitches", ["enable-logging"])
            
            service = Service(ChromeDriverManager().install())
            self.driver = webdriver.Chrome(service=service, options=chrome_options)
            
            self.log(f"✅ Navegador abierto - Navegando a: {url}", "success")
            self.driver.get(url)
            
            self.update_status("Capturando URLs... (Navega manualmente)", "success")
            
            self.check_thread = threading.Thread(target=self.monitor_iframes, daemon=True)
            self.check_thread.start()
            
        except Exception as e:
            self.log(f"❌ Error al abrir navegador: {e}", "error")
            self.capturing = False
            self.start_button.config(state=tk.NORMAL)
            self.stop_button.config(state=tk.DISABLED)
            self.update_status("Error al iniciar navegador", "error")
    
    def monitor_iframes(self):
        """Monitorea constantemente los iframes en la página"""
        self.log("👁️ Monitoreando iframes en tiempo real...", "info")
        
        while self.capturing and self.driver:
            try:
                iframes = self.driver.find_elements(By.TAG_NAME, "iframe")
                
                for iframe in iframes:
                    try:
                        iframe_src = iframe.get_attribute("src")
                        
                        if iframe_src and iframe_src not in self.captured_urls:
                            if any(keyword in iframe_src.lower() for keyword in 
                                  ['video', 'player', 'embed', 'stream', 'vimeo', 'youtube', 'wistia', 'cloudflare']):
                                self.captured_urls.add(iframe_src)
                                self.log(f"🎯 Nueva URL capturada: {iframe_src[:80]}...", "success")
                                self.update_url_count()
                                self.update_status(f"{len(self.captured_urls)} URLs capturadas", "success")
                    except:
                        pass
                
                threading.Event().wait(2)
                
            except Exception as e:
                if self.capturing:
                    self.log(f"⚠️ Error en monitoreo: {e}", "warning")
                break
    
    def stop_capture(self):
        """Detiene la captura y cierra el navegador"""
        self.capturing = False
        
        if self.driver:
            try:
                self.driver.quit()
                self.log("🛑 Navegador cerrado correctamente", "info")
            except:
                pass
            self.driver = None
        
        self.start_button.config(state=tk.NORMAL)
        self.stop_button.config(state=tk.DISABLED)
        
        self.log(f"✅ Captura finalizada. Total URLs capturadas: {len(self.captured_urls)}", "success")
        self.update_status(f"Captura detenida - {len(self.captured_urls)} URLs guardadas", "info")
    
    def download_all(self):
        """Descarga todos los videos capturados"""
        if not self.captured_urls:
            messagebox.showwarning("Sin URLs", "No hay URLs capturadas para descargar")
            return
        
        if messagebox.askyesno("Confirmar Descarga", 
                              f"¿Descargar {len(self.captured_urls)} videos?\n\nEsto puede tomar varios minutos."):
            self.log("━" * 70, "info")
            self.log("📥 Iniciando proceso de descarga...", "success")
            self.log(f"📁 Guardando en carpeta: {self.results_folder}/", "info")
            self.log("━" * 70, "info")
            
            threading.Thread(target=self.download_videos, daemon=True).start()
    
    def download_videos(self):
        """Descarga los videos usando yt-dlp"""
        self.download_button.config(state=tk.DISABLED)
        
        for i, url in enumerate(self.captured_urls, 1):
            try:
                nombre = os.path.join(self.results_folder, f"video_{i}.mp4")
                
                self.root.after(0, lambda idx=i, u=url: self.log(
                    f"[{idx}/{len(self.captured_urls)}] Descargando: {u[:60]}...", "info"
                ))
                
                self.root.after(0, lambda idx=i: self.update_status(
                    f"Descargando video {idx}/{len(self.captured_urls)}...", "info"
                ))
                
                comando = [
                    sys.executable, "-m", "yt_dlp",
                    "-f", "best[ext=mp4]/best",
                    url,
                    "-o", nombre,
                    "--quiet",
                    "--no-warnings"
                ]
                
                resultado = subprocess.run(comando, capture_output=True, text=True)
                
                if resultado.returncode == 0:
                    self.root.after(0, lambda idx=i, n=nombre: self.log(
                        f"✅ Video {idx} descargado: {n}", "success"
                    ))
                else:
                    self.root.after(0, lambda idx=i: self.log(
                        f"❌ Error descargando video {idx}", "error"
                    ))
                    
            except Exception as e:
                self.root.after(0, lambda idx=i, err=e: self.log(
                    f"❌ Excepción en video {idx}: {err}", "error"
                ))
        
        self.root.after(0, lambda: self.log("━" * 70, "info"))
        self.root.after(0, lambda: self.log("🎉 ¡Proceso de descarga completado!", "success"))
        self.root.after(0, lambda: self.log(f"📁 Videos guardados en: {os.path.abspath(self.results_folder)}/", "success"))
        self.root.after(0, lambda: self.log("━" * 70, "info"))
        self.root.after(0, lambda: self.update_status("Todas las descargas completadas", "success"))
        self.root.after(0, lambda: self.download_button.config(state=tk.NORMAL))

def main():
    root = tk.Tk()
    app = IframeCaptureDownloader(root)
    
    root.update_idletasks()
    width = root.winfo_width()
    height = root.winfo_height()
    x = (root.winfo_screenwidth() // 2) - (width // 2)
    y = (root.winfo_screenheight() // 2) - (height // 2)
    root.geometry(f'{width}x{height}+{x}+{y}')
    
    root.mainloop()

if __name__ == "__main__":

    main()
