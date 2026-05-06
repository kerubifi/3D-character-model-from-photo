import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import subprocess
import os
import shutil
import threading
import time
from PIL import Image, ImageTk
import cv2
import numpy as np

class PIFuHD_Simple:
    def __init__(self, root):
        self.root = root
        self.root.title("3D Creator")
        self.root.geometry("750x650")
        self.root.configure(bg="#1e1e1e")
        
        self.image_path = None
        self.process = None
        self.running = False
        self.project_dir = os.getcwd()
        self.has_cv2 = self.check_opencv()
        
        self.setup_ui()
        
    def check_opencv(self):
        try:
            import cv2
            return True
        except:
            return False
        
    def setup_ui(self):
        # Заголовок
        title = tk.Label(self.root, text="3D Character Creator", 
                        font=("Arial", 18, "bold"), bg="#1e1e1e", fg="#4CAF50")
        title.pack(pady=15)
        
        subtitle = tk.Label(self.root, text="Создание 3D модели человека из одной фотографии",
                           font=("Arial", 10), bg="#1e1e1e", fg="#888888")
        subtitle.pack()
        
        # Основной контейнер
        main_frame = tk.Frame(self.root, bg="#1e1e1e")
        main_frame.pack(fill="both", expand=True, padx=20, pady=10)
        
        # Левая панель
        left_panel = tk.Frame(main_frame, bg="#2d2d2d", relief="solid", bd=1)
        left_panel.pack(side="left", fill="both", expand=True, padx=(0, 10))
        
        # Правая панель
        right_panel = tk.Frame(main_frame, bg="#2d2d2d", relief="solid", bd=1)
        right_panel.pack(side="right", fill="both", expand=True)
        
        # === ЛЕВАЯ ПАНЕЛЬ ===
        
        # Выбор фото
        photo_frame = tk.LabelFrame(left_panel, text="Выберите фотографию", 
                                    font=("Arial", 11, "bold"), bg="#2d2d2d", fg="#4CAF50")
        photo_frame.pack(fill="x", padx=10, pady=10)
        
        self.photo_var = tk.StringVar()
        photo_entry = tk.Entry(photo_frame, textvariable=self.photo_var, 
                               width=35, bg="#3c3c3c", fg="white")
        photo_entry.pack(side="left", padx=10, pady=10, fill="x", expand=True)
        
        select_btn = tk.Button(photo_frame, text="Обзор", command=self.select_photo,
                               bg="#2196F3", fg="white", padx=15)
        select_btn.pack(side="right", padx=10)
        
        # Качество
        quality_frame = tk.LabelFrame(left_panel, text="Качество", 
                                      font=("Arial", 11, "bold"), bg="#2d2d2d", fg="#4CAF50")
        quality_frame.pack(fill="x", padx=10, pady=10)
        
        quality_inner = tk.Frame(quality_frame, bg="#2d2d2d")
        quality_inner.pack(pady=10)
        
        self.resolution = tk.StringVar(value="256")
        
        tk.Button(quality_inner, text="Быстрое", width=10,
                 command=lambda: self.set_quality("128"),
                 bg="#3c3c3c", fg="white", relief="flat").pack(side="left", padx=5)
        
        tk.Button(quality_inner, text="Среднее", width=10,
                 command=lambda: self.set_quality("256"),
                 bg="#3c3c3c", fg="white", relief="flat").pack(side="left", padx=5)
        
        tk.Button(quality_inner, text="Высокое", width=10,
                 command=lambda: self.set_quality("512"),
                 bg="#3c3c3c", fg="white", relief="flat").pack(side="left", padx=5)
        
        self.quality_label = tk.Label(quality_frame, text="Текущее: Среднее", 
                                      bg="#2d2d2d", fg="#4CAF50", font=("Arial", 9))
        self.quality_label.pack(pady=5)
        
        # Кнопка запуска
        self.start_btn = tk.Button(left_panel, text="СОЗДАТЬ 3D МОДЕЛЬ", 
                                   command=self.start_processing,
                                   bg="#4CAF50", fg="white", font=("Arial", 12, "bold"),
                                   padx=20, pady=10)
        self.start_btn.pack(pady=20, padx=20, fill="x")
        
        # Прогресс
        self.progress = ttk.Progressbar(left_panel, mode='indeterminate')
        self.progress.pack(fill="x", padx=20, pady=5)
        
        # Статус
        self.status_label = tk.Label(left_panel, text="Готов к работе", 
                                     bg="#2d2d2d", fg="#4CAF50")
        self.status_label.pack(pady=10)
        
        # === ПРАВАЯ ПАНЕЛЬ ===
        
        # Предпросмотр
        preview_frame = tk.LabelFrame(right_panel, text="Предпросмотр", 
                                      font=("Arial", 11, "bold"), bg="#2d2d2d", fg="#4CAF50")
        preview_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.preview_label = tk.Label(preview_frame, text="Фото не выбрано\n\nНажмите 'Обзор'", 
                                      bg="#1e1e1e", fg="#888888", font=("Arial", 10),
                                      width=40, height=12)
        self.preview_label.pack(fill="both", expand=True, padx=10, pady=10)
        
        # Лог выполнения
        log_frame = tk.LabelFrame(right_panel, text="Лог выполнения", 
                                  font=("Arial", 11, "bold"), bg="#2d2d2d", fg="#4CAF50")
        log_frame.pack(fill="both", expand=True, padx=10, pady=10)
        
        self.log_text = tk.Text(log_frame, height=10, wrap=tk.WORD,
                               bg="#1e1e1e", fg="#00ff00", font=("Consolas", 9))
        self.log_text.pack(fill="both", expand=True, padx=5, pady=5)
        
        scrollbar = tk.Scrollbar(self.log_text)
        scrollbar.pack(side="right", fill="y")
        self.log_text.config(yscrollcommand=scrollbar.set)
        scrollbar.config(command=self.log_text.yview)
        
        # Кнопка открытия папки
        open_btn = tk.Button(right_panel, text="Открыть папку с результатом", 
                             command=self.open_folder,
                             bg="#9c27b0", fg="white", padx=15, pady=8)
        open_btn.pack(pady=10, padx=10, fill="x")
    
    def set_quality(self, value):
        self.resolution.set(value)
        names = {"128": "Быстрое", "256": "Среднее", "512": "Высокое"}
        self.quality_label.config(text=f"Текущее: {names[value]}")
        
        # Обновляем цвета кнопок
        for widget in self.quality_label.master.winfo_children():
            if isinstance(widget, tk.Button):
                if (value == "128" and widget.cget("text") == "Быстрое") or \
                   (value == "256" and widget.cget("text") == "Среднее") or \
                   (value == "512" and widget.cget("text") == "Высокое"):
                    widget.config(bg="#4CAF50")
                else:
                    widget.config(bg="#3c3c3c")
            
    
    def auto_detect_rect(self, image_path):
        """Автоматическое определение границ человека"""
        if not self.has_cv2:
            return None
            
        try:
            # Временная копия для обхода русских букв
            temp_dir = os.environ.get('TEMP', 'C:\\temp')
            os.makedirs(temp_dir, exist_ok=True)
            temp_path = os.path.join(temp_dir, "temp_rect.png")
            
            img_pil = Image.open(image_path)
            img_pil.save(temp_path)
            
            img = cv2.imread(temp_path)
            
            try:
                os.unlink(temp_path)
            except:
                pass
            
            if img is None:
                return None
            
            h, w = img.shape[:2]
            gray = cv2.cvtColor(img, cv2.COLOR_BGR2GRAY)
            
            _, mask1 = cv2.threshold(gray, 30, 255, cv2.THRESH_BINARY)
            mask2 = cv2.adaptiveThreshold(gray, 255, cv2.ADAPTIVE_THRESH_GAUSSIAN_C, 
                                          cv2.THRESH_BINARY, 11, 2)
            
            mask = cv2.bitwise_or(mask1, mask2)
            
            kernel = np.ones((5, 5), np.uint8)
            mask = cv2.morphologyEx(mask, cv2.MORPH_CLOSE, kernel)
            mask = cv2.morphologyEx(mask, cv2.MORPH_OPEN, kernel)
            
            contours, _ = cv2.findContours(mask, cv2.RETR_EXTERNAL, cv2.CHAIN_APPROX_SIMPLE)
            
            if not contours:
                return None
            
            areas = [cv2.contourArea(c) for c in contours]
            max_idx = np.argmax(areas)
            main_contour = contours[max_idx]
            x, y, w_box, h_box = cv2.boundingRect(main_contour)
            
            padding_x = int(w_box * 0.2)
            padding_y = int(h_box * 0.2)
            
            x = max(0, x - padding_x)
            y = max(0, y - padding_y)
            w_box = min(w - x, w_box + 2 * padding_x)
            h_box = min(h - y, h_box + 2 * padding_y)
            
            return (x, y, w_box, h_box)
            
        except Exception as e:
            return None
    
    def select_photo(self):
        filename = filedialog.askopenfilename(filetypes=[("Images", "*.jpg *.jpeg *.png")])
        if filename:
            self.image_path = filename
            self.photo_var.set(filename)
            self.show_preview(filename)
            self.add_log(f"Выбрано: {os.path.basename(filename)}")
    
    def show_preview(self, path):
        try:
            img = Image.open(path)
            img.thumbnail((350, 350), Image.Resampling.LANCZOS)
            photo = ImageTk.PhotoImage(img)
            self.preview_label.config(image=photo, text="")
            self.preview_label.image = photo
        except Exception as e:
            self.preview_label.config(text="Ошибка загрузки", image="")
    
    def add_log(self, msg):
        timestamp = time.strftime("%H:%M:%S")
        self.log_text.insert(tk.END, f"[{timestamp}] {msg}\n")
        self.log_text.see(tk.END)
        self.root.update()
    
    def open_folder(self):
        recon_dir = os.path.join(self.project_dir, "results", "pifuhd_final", "recon")
        if os.path.exists(recon_dir):
            os.startfile(recon_dir)
        else:
            messagebox.showinfo("Информация", "Папка с результатами ещё не создана")
    
    def start_processing(self):
        if not self.image_path:
            messagebox.showerror("Ошибка", "Выберите фотографию!")
            return
        
        self.running = True
        self.start_btn.config(state="disabled")
        self.progress.start()
        self.status_label.config(text="Обработка...")
        
        thread = threading.Thread(target=self.process_image, daemon=True)
        thread.start()
    
    def process_image(self):
        try:
            sample_dir = os.path.join(self.project_dir, "sample_images")
            os.makedirs(sample_dir, exist_ok=True)
            
            for f in os.listdir(sample_dir):
                try:
                    os.unlink(os.path.join(sample_dir, f))
                except:
                    pass
            
            ext = os.path.splitext(self.image_path)[1]
            target_path = os.path.join(sample_dir, f"test{ext}")
            shutil.copy2(self.image_path, target_path)
            self.add_log("Фото скопировано")
            
            rect_path = os.path.join(sample_dir, "test_rect.txt")
            
            if self.has_cv2:
                rect = self.auto_detect_rect(target_path)
                if rect:
                    x, y, w, h = rect
                    with open(rect_path, 'w') as f:
                        f.write(f"{x} {y} {w} {h}")
                    self.add_log(f"Автоопределение rect: {x} {y} {w} {h}")
                else:
                    with open(rect_path, 'w') as f:
                        f.write("100 100 600 800")
                    self.add_log("Стандартный rect (автоопределение не удалось)")
            else:
                with open(rect_path, 'w') as f:
                    f.write("100 100 600 800")
                self.add_log("Стандартный rect")
            
            python_exe = os.path.join(self.project_dir, "venv_pifuhd", "Scripts", "python.exe")
            if not os.path.exists(python_exe):
                python_exe = "python"
            
            cmd = [
                python_exe, "-m", "apps.simple_test",
                "--input_path", "sample_images",
                "--out_path", "results",
                "-r", self.resolution.get(),
                "--use_rect"
            ]
            
            quality_names = {"128": "Быстрое", "256": "Среднее", "512": "Высокое"}
            self.add_log(f"Запуск ({quality_names[self.resolution.get()]})...")
            
            self.process = subprocess.Popen(cmd, cwd=self.project_dir,
                                           stdout=subprocess.PIPE, stderr=subprocess.STDOUT,
                                           universal_newlines=True)
            
            for line in self.process.stdout:
                line = line.strip()
                if line:
                    self.add_log(line[:150])
                    if "Saved to" in line and ".obj" in line:
                        self.add_log("3D МОДЕЛЬ СОЗДАНА!")
                        self.status_label.config(text="Модель готова!")
            
            self.process.wait()
            
            if self.process.returncode == 0:
                self.add_log("Готово!")
                messagebox.showinfo("Успех", "3D модель создана!\nСмотрите в папке results")
            else:
                self.add_log(f"Ошибка (код: {self.process.returncode})")
                self.status_label.config(text="Ошибка")
                
        except Exception as e:
            self.add_log(f"Ошибка: {e}")
        finally:
            self.progress.stop()
            self.start_btn.config(state="normal")
            self.running = False
            if self.status_label.cget("text") != "Модель готова!":
                self.status_label.config(text="Готов")

if __name__ == "__main__":
    root = tk.Tk()
    app = PIFuHD_Simple(root)
    root.mainloop()