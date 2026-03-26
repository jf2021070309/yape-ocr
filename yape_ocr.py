import os
import warnings
# Ocultar advertencias técnicas de PyTorch/Torch
warnings.filterwarnings("ignore", category=UserWarning)
os.environ['TORCH_CPP_LOG_LEVEL'] = 'ERROR'
os.environ['KMP_DUPLICATE_LIB_OK'] = 'TRUE'

import tkinter as tk
from tkinter import filedialog, ttk
import easyocr
import re
import threading
import time
from PIL import Image, ImageTk, ImageEnhance, ImageOps

class YapeOCRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Yape OCR Extractor Pro")
        self.root.geometry("950x650") 
        self.root.configure(bg="#f8f9fa")
        
        self.yape_purple = "#6f42c1"
        self.yape_deep_purple = "#5a32a3"
        self.text_color = "#343a40"
        
        self.header = tk.Frame(self.root, bg=self.yape_purple, height=80)
        self.header.pack(fill="x")
        self.header_label = tk.Label(self.header, text="Yape OCR Extractor", 
                                   fg="white", bg=self.yape_purple, 
                                   font=("Segoe UI", 20, "bold"), pady=15)
        self.header_label.pack()

        self.main_container = tk.Frame(self.root, bg="#f8f9fa")
        self.main_container.pack(expand=True, fill="both", padx=20, pady=10)

        self.left_col = tk.Frame(self.main_container, bg="#f8f9fa")
        self.left_col.pack(side="left", expand=True, fill="both", padx=(0, 10))

        self.instr_label = tk.Label(self.left_col, text="Selecciona una captura de pantalla de Yape", 
                                  bg="#f8f9fa", fg=self.text_color, font=("Segoe UI", 11))
        self.instr_label.pack(pady=10)

        self.btn = tk.Button(self.left_col, text="Subir Imagen y Escanear", 
                           command=self.start_ocr_thread, 
                           bg=self.yape_purple, fg="white", 
                           activebackground=self.yape_deep_purple,
                           activeforeground="white",
                           font=("Segoe UI", 12, "bold"), 
                           padx=20, pady=10, cursor="hand2", relief="flat")
        self.btn.pack(pady=10)

        self.loading_frame = tk.Frame(self.left_col, bg="#f8f9fa")
        self.loading_frame.pack(pady=5)
        self.loading_label = tk.Label(self.loading_frame, text="", bg="#f8f9fa", 
                                    fg=self.yape_purple, font=("Segoe UI", 11, "italic"))
        self.loading_label.pack()
        self.progress = ttk.Progressbar(self.loading_frame, orient="horizontal", 
                                      length=250, mode="indeterminate")

        self.results_card = tk.LabelFrame(self.left_col, text=" Resultados del Escaneo ", 
                                        bg="white", fg=self.yape_purple,
                                        font=("Segoe UI", 10, "bold"), padx=20, pady=20)
        self.results_card.pack(pady=10, fill="x")

        self.monto_text = tk.StringVar(value="-")
        self.codigo_text = tk.StringVar(value="-")
        self.create_result_row("Monto:", self.monto_text)
        self.create_result_row("Cód. Seguridad:", self.codigo_text)

        self.right_col = tk.Frame(self.main_container, bg="#e9ecef", relief="sunken", borderwidth=1)
        self.right_col.pack(side="right", expand=True, fill="both")
        
        self.img_label = tk.Label(self.right_col, text="No hay imagen cargada", 
                                 bg="#e9ecef", fg="#6c757d", font=("Segoe UI", 10))
        self.img_label.pack(expand=True, fill="both")

        self.is_processing = False
        self.reader = None
        self.tk_img = None

    def create_result_row(self, label_text, var):
        row = tk.Frame(self.results_card, bg="white", pady=5)
        row.pack(fill="x")
        tk.Label(row, text=label_text, bg="white", fg="#6c757d", 
                 font=("Segoe UI", 11, "bold"), width=15, anchor="w").pack(side="left")
        tk.Label(row, textvariable=var, bg="white", fg=self.text_color, 
                 font=("Segoe UI", 16, "bold"), anchor="w").pack(side="left")

    def animate_loading(self):
        chars = ["⠋", "⠙", "⠹", "⠸", "⠼", "⠴", "⠦", "⠧", "⠇", "⠏"]
        idx = 0
        while self.is_processing:
            self.loading_label.config(text=f"{chars[idx]} Escaneando imagen...")
            idx = (idx + 1) % len(chars)
            time.sleep(0.1)
        self.loading_label.config(text="")
        self.progress.stop()
        self.progress.pack_forget()

    def display_preview(self, image_path):
        try:
            img = Image.open(image_path)
            img.thumbnail((450, 500))
            self.tk_img = ImageTk.PhotoImage(img)
            self.img_label.config(image=self.tk_img, text="")
        except Exception as e:
            self.img_label.config(image="", text=f"Error al cargar imagen:\n{str(e)}")

    def start_ocr_thread(self):
        if self.is_processing: return
        file_path = filedialog.askopenfilename(
            title="Seleccionar captura de Yape",
            filetypes=[("Imágenes", "*.png *.jpg *.jpeg *.bmp *.webp")]
        )
        if not file_path: return
        self.display_preview(file_path)
        self.monto_text.set("...")
        self.codigo_text.set("...")
        self.is_processing = True
        self.btn.config(state="disabled")
        self.progress.pack(pady=5)
        self.progress.start(10)
        threading.Thread(target=self.animate_loading, daemon=True).start()
        threading.Thread(target=self.process_image, args=(file_path,), daemon=True).start()

    def process_image(self, image_path):
        try:
            if self.reader is None:
                print("Cargando modelos OCR...")
                self.reader = easyocr.Reader(['es'])
            
            # --- Pre-procesamiento de Alta Sensibilidad ---
            img = Image.open(image_path).convert('RGB')
            w, h = img.size
            img = img.resize((w*2, h*2), Image.Resampling.BICUBIC)
            
            img_gray = ImageOps.grayscale(img)
            # Ecualización para balancear luces y sombras (ayuda mucho a las cajas)
            img_gray = ImageOps.equalize(img_gray)
            
            img_sharp = ImageEnhance.Sharpness(img_gray).enhance(2.0)
            img_enhanced = ImageEnhance.Contrast(img_sharp).enhance(1.2) # Menos contraste, más detalle
            
            temp_path = "temp_ocr_process.jpg"
            img_enhanced.save(temp_path)

            # Umbrales bajísimos para capturar cajas grises
            result = self.reader.readtext(temp_path, detail=0, paragraph=False, 
                                        width_ths=0.2, text_threshold=0.2, 
                                        low_text=0.1, contrast_ths=0.1)
            
            if os.path.exists(temp_path): os.remove(temp_path)
            
            full_text = " ".join(result)
            print("Texto detectado:", full_text)
            text_upper = full_text.upper().replace('¡', '').replace('!', '')
            
            # --- Monto ---
            monto = "No encontrado"
            ref_index = text_upper.find("YAPEASTE")
            search_text = full_text[ref_index:] if ref_index != -1 else full_text
            
            candidates = []
            monto_matches = re.finditer(r'(?<![0-9])[S5s][/\s\.\-Il]{1,4}\s*([0-9IlioOB\.,]{1,10})', search_text)
            
            for match in monto_matches:
                raw_val = match.group(1)
                clean_val = raw_val.replace('l', '1').replace('I', '1').replace('i', '1').replace('o', '0').replace('O', '0').replace('B', '8')
                clean_val = re.sub(r'[^0-9\.,]', '', clean_val)
                if clean_val and any(char.isdigit() for char in clean_val):
                    if re.match(r'^\d+([\.,]\d{1,2})?$', clean_val):
                        candidates.append(clean_val)
            
            if candidates:
                monto = candidates[0]
            elif ref_index != -1:
                near = re.search(r'(\d+([\.,]\d{1,2})?)', search_text[:50])
                if near: monto = near.group(1)

            # --- Código de Seguridad ---
            codigo = "No encontrado"
            keywords = ["SEGURIDAD", "CÓDIGO", "CODIGO", "S3GURIDAD", "SECU", "S3GU", "CURIDAD"]
            target_index = -1
            for kw in keywords:
                target_index = text_upper.find(kw)
                if target_index != -1: break
            
            if target_index != -1:
                # Delimitar sección (desde SEGURIDAD hasta DATOS de transacción)
                # El icono (i) a veces se lee como '1' o '2', por eso tomamos los ÚLTIMOS 3 dígitos
                end_index = text_upper.find("DATOS", target_index)
                if end_index == -1: end_index = target_index + 100
                
                section = full_text[target_index:end_index]
                all_digits = re.sub(r'\D', '', section)
                
                if len(all_digits) >= 3:
                    # Siempre son los últimos 3 del bloque de seguridad (el icono i va primero)
                    codigo = all_digits[-3:]
                else:
                    # Fallback si están muy separados
                    matches = re.findall(r'\d', section)
                    if len(matches) >= 3:
                        codigo = "".join(matches[-3:])

            self.root.after(0, lambda: self.update_results(monto, codigo))
        except Exception as e:
            self.root.after(0, lambda: self.show_error(str(e)))
        finally:
            self.is_processing = False
            self.root.after(0, lambda: self.btn.config(state="normal"))

    def update_results(self, monto, codigo):
        self.monto_text.set(monto)
        self.codigo_text.set(codigo)
        print(f"Resultados -> Monto: {monto}, Código: {codigo}")

    def show_error(self, message):
        self.monto_text.set("ERROR")
        self.codigo_text.set("ERROR")
        print(f"Error: {message}")

if __name__ == "__main__":
    root = tk.Tk()
    app = YapeOCRApp(root)
    root.mainloop()
