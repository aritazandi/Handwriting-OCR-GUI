import tkinter as tk  # برای ساخت رابط گرافیکی
from tkinter import ttk, messagebox, colorchooser
import cv2  #پردازش تصویر
import pytesseract
from PIL import Image, ImageDraw, ImageTk, ImageEnhance, ImageFilter #پردازش تصویر
import numpy as np
import os  #عملیات سیستم عامل
import re
from scipy import ndimage
import threading
import warnings
warnings.filterwarnings('ignore')

class HandwritingOCRApp:
    def __init__(self, root):
        self.root = root
        self.root.title("Handwriting OCR")
        self.root.geometry("1200x800")
        self.root.configure(bg='#f0f0f0')
        
        # تنظیمات اولیه
        self.canvas_width = 800
        self.canvas_height = 600
        self.brush_size = 3
        self.brush_color = '#000000'
        self.is_drawing = False
        self.last_x = 0
        self.last_y = 0
        
        # تصویر PIL برای ذخیره
        self.pil_image = Image.new('RGB', (self.canvas_width, self.canvas_height), 'white')
        self.pil_draw = ImageDraw.Draw(self.pil_image) #ساخت تصویر برای ذخیره آنچه کاربر می‌نویسد
        
        # متغیرهای OCR
        self.recognized_text = "the text you wrote:"
        self.processing = False
        
        self.setup_tesseract()
        self.setup_ui()
        
        print("Handwriting OCR GUI initialized!")
    
    def setup_tesseract(self):
        """Setup Tesseract path"""
        possible_paths = [
            r'C:\Program Files\Tesseract-OCR\tesseract.exe',
            r'C:\Program Files (x86)\Tesseract-OCR\tesseract.exe',
        ]
        
        for path in possible_paths:
            if os.path.exists(path):
                pytesseract.pytesseract.tesseract_cmd = path
                print(f"Tesseract found: {path}")
                return
        print("Tesseract not found")
    
    def setup_ui(self):
        """راه‌اندازی رابط کاربری"""
        
        # فریم اصلی
        main_frame = tk.Frame(self.root, bg='#f0f0f0')
        main_frame.pack(fill='both', expand=True, padx=10, pady=10)
        
        # عنوان
        title_frame = tk.Frame(main_frame, bg='#4facfe', height=80)
        title_frame.pack(fill='x', pady=(0, 10))
        title_frame.pack_propagate(False)
        
        title_label = tk.Label(
            title_frame, 
            text="Handwriting OCR",
            font=('Arial', 20, 'bold'),
            bg='#4facfe',
            fg='white'
        )
        title_label.pack(expand=True)
        
        # فریم محتوای اصلی
        content_frame = tk.Frame(main_frame, bg='#f0f0f0')
        content_frame.pack(fill='both', expand=True)
        
        # بخش چپ - Canvas
        left_frame = tk.Frame(content_frame, bg='white', relief='raised', bd=2)
        left_frame.pack(side='left', fill='both', expand=True, padx=(0, 5))
        
        # کنترل‌ها
        self.setup_controls(left_frame)
        
        # Canvas
        self.setup_canvas(left_frame)
        
        # بخش راست - نتایج
        right_frame = tk.Frame(content_frame, bg='#f8f9ff', relief='raised', bd=2, width=350)
        right_frame.pack(side='right', fill='both', padx=(5, 0))
        right_frame.pack_propagate(False)
        
        self.setup_results_panel(right_frame)
    
    def setup_controls(self, parent):
        """راه‌اندازی کنترل‌ها"""
        controls_frame = tk.Frame(parent, bg='white', pady=10)
        controls_frame.pack(fill='x', padx=10)
        
        # ردیف اول - اندازه قلم
        row1 = tk.Frame(controls_frame, bg='white')
        row1.pack(fill='x', pady=5)
        
        tk.Label(row1, text="Brush Size:", bg='white', font=('Arial', 10)).pack(side='left', padx=(0, 5))
        
        self.size_var = tk.IntVar(value=self.brush_size)
        size_scale = tk.Scale(
            row1, from_=1, to=20, orient='horizontal',
            variable=self.size_var, command=self.update_brush_size,
            bg='white', highlightthickness=0
        )
        size_scale.pack(side='left', padx=(0, 10))
        
        self.size_label = tk.Label(row1, text=str(self.brush_size), bg='white', font=('Arial', 10, 'bold'))
        self.size_label.pack(side='left', padx=(0, 20))
        
        # دکمه انتخاب رنگ
        color_btn = tk.Button(
            row1, text="Color", command=self.choose_color,
            bg='#667eea', fg='white', font=('Arial', 10, 'bold'),
            relief='flat', padx=15, pady=5,
            activebackground='#764ba2', activeforeground='white'
        )
        color_btn.pack(side='left', padx=(0, 10))
        
        self.color_preview = tk.Label(
            row1, text="  ", bg=self.brush_color,
            width=3, relief='raised', bd=2
        )
        self.color_preview.pack(side='left')
        
        # ردیف دوم - دکمه‌ها
        row2 = tk.Frame(controls_frame, bg='white')
        row2.pack(fill='x', pady=10)
        
        clear_btn = tk.Button(
            row2, text="Clear", command=self.clear_canvas,
            bg='#fcb69f', fg='#333', font=('Arial', 12, 'bold'),
            relief='flat', padx=20, pady=8,
            activebackground='#ffecd2', activeforeground='#333'
        )
        clear_btn.pack(side='left', padx=(0, 10))
        
        self.recognize_btn = tk.Button(
            row2, text="Recognize Text", command=self.start_recognition,
            bg='#f5576c', fg='white', font=('Arial', 12, 'bold'),
            relief='flat', padx=20, pady=8,
            activebackground='#f093fb', activeforeground='white'
        )
        self.recognize_btn.pack(side='left')
    
    def setup_canvas(self, parent):
        """راه‌اندازی Canvas"""
        canvas_frame = tk.Frame(parent, bg='white', pady=10)
        canvas_frame.pack(fill='both', expand=True, padx=10)
        
        # Canvas با Scrollbar
        canvas_container = tk.Frame(canvas_frame, bg='white', relief='sunken', bd=3)
        canvas_container.pack(fill='both', expand=True)
        
        self.canvas = tk.Canvas(
            canvas_container,
            width=self.canvas_width,
            height=self.canvas_height,
            bg='white',
            cursor='pencil'
        )
        
        # Scrollbars
        v_scrollbar = ttk.Scrollbar(canvas_container, orient='vertical', command=self.canvas.yview)
        h_scrollbar = ttk.Scrollbar(canvas_container, orient='horizontal', command=self.canvas.xview)
        
        self.canvas.configure(yscrollcommand=v_scrollbar.set, xscrollcommand=h_scrollbar.set)
        self.canvas.configure(scrollregion=self.canvas.bbox("all"))
        
        # Pack scrollbars and canvas
        v_scrollbar.pack(side='right', fill='y')
        h_scrollbar.pack(side='bottom', fill='x')
        self.canvas.pack(side='left', fill='both', expand=True)
        
        # Event bindings
        self.canvas.bind('<Button-1>', self.start_draw)
        self.canvas.bind('<B1-Motion>', self.draw)
        self.canvas.bind('<ButtonRelease-1>', self.stop_draw)
        
        # راهنمای اولیه
        self.canvas.create_text(
            self.canvas_width//2, self.canvas_height//2,
            text="Start writing here",
            font=('Arial', 16), fill='#ccc', tags='guide'
        )
    
    def setup_results_panel(self, parent):
        """راه‌اندازی پنل نتایج"""
        # عنوان
        title_frame = tk.Frame(parent, bg='#f8f9ff', pady=10)
        title_frame.pack(fill='x', padx=10)
        
        tk.Label(
            title_frame, text="Recognized Text",
            font=('Arial', 16, 'bold'), bg='#f8f9ff', fg='#333'
        ).pack()
        
        # پنل نتیجه
        text_frame = tk.Frame(parent, bg='white', relief='sunken', bd=2)
        text_frame.pack(fill='both', expand=True, padx=10, pady=(0, 10))
        
        # متن نتیجه
        self.text_result = tk.Text(
            text_frame,
            wrap='word',
            font=('Arial', 11),
            bg='white',
            relief='flat',
            padx=10,
            pady=10
        )
        
        text_scrollbar = ttk.Scrollbar(text_frame, command=self.text_result.yview)
        self.text_result.configure(yscrollcommand=text_scrollbar.set)
        
        text_scrollbar.pack(side='right', fill='y')
        self.text_result.pack(side='left', fill='both', expand=True)
        
        # پیغام اولیه
        initial_text = "the text you wrote:"
        self.text_result.insert('1.0', initial_text)
        self.text_result.configure(state='disabled')
        
        # پنل آمار
        self.stats_frame = tk.Frame(parent, bg='#f0f8ff', relief='raised', bd=1)
        self.stats_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        tk.Label(
            self.stats_frame, text="Statistics",
            font=('Arial', 12, 'bold'), bg='#f0f8ff'
        ).pack(pady=5)
        
        self.stats_text = tk.Label(
            self.stats_frame, text="", font=('Arial', 10),
            bg='#f0f8ff', fg='#666', justify='left'
        )
        self.stats_text.pack(pady=5)
        
        # Progress bar
        self.progress_frame = tk.Frame(parent, bg='#f8f9ff')
        self.progress_frame.pack(fill='x', padx=10, pady=(0, 10))
        
        self.progress_label = tk.Label(
            self.progress_frame, text="", font=('Arial', 10),
            bg='#f8f9ff', fg='#666'
        )
        self.progress_label.pack()
        
        self.progress_bar = ttk.Progressbar(
            self.progress_frame, mode='indeterminate'
        )
        self.progress_bar.pack(fill='x', pady=5)
    
    def update_brush_size(self, value):
        """به‌روزرسانی اندازه قلم"""
        self.brush_size = int(value)
        self.size_label.config(text=str(self.brush_size))
    
    def choose_color(self):
        """انتخاب رنگ قلم"""
        color = colorchooser.askcolor(color=self.brush_color)[1]
        if color:
            self.brush_color = color
            self.color_preview.config(bg=self.brush_color)
    
    def start_draw(self, event):
        """شروع نقاشی"""
        self.is_drawing = True
        self.last_x = event.x
        self.last_y = event.y
        
        # حذف راهنما
        self.canvas.delete('guide')
    
    def draw(self, event):
        """نقاشی"""
        if self.is_drawing:
            x, y = event.x, event.y
         
            self.canvas.create_line(
                self.last_x, self.last_y, x, y,
                width=self.brush_size,
                fill=self.brush_color,
                capstyle='round',
                smooth=True
            )
            
            self.pil_draw.line(
                [self.last_x, self.last_y, x, y],
                fill=self.brush_color,
                width=self.brush_size
            )
            
            self.last_x = x
            self.last_y = y
    
    def stop_draw(self, event):
        """پایان نقاشی"""
        self.is_drawing = False
    
    def clear_canvas(self):
        """پاک کردن Canvas"""
        self.canvas.delete('all')
        
        # ساخت تصویر جدید
        self.pil_image = Image.new('RGB', (self.canvas_width, self.canvas_height), 'white')
        self.pil_draw = ImageDraw.Draw(self.pil_image)
        
        # نمایش راهنما
        self.canvas.create_text(
            self.canvas_width//2, self.canvas_height//2,
            text="Start writing here!",
            font=('Arial', 16), fill='#ccc', tags='guide'
        )
        
        # پاک کردن نتایج
        self.text_result.configure(state='normal')
        self.text_result.delete('1.0', 'end')
        initial_text = ""
        self.text_result.insert('1.0', initial_text)
        self.text_result.configure(state='disabled')
        
        self.stats_text.config(text="")
        
        print("Canvas cleared!")
    
    def start_recognition(self):
        """شروع فرآیند تشخیص متن"""
        if self.processing:
            return
        
        # نمایش progress
        self.progress_label.config(text=" analyzing your handwriting...")
        self.progress_bar.start(10)
        self.recognize_btn.configure(state='disabled')
        
        # اجرا در thread جداگانه
        thread = threading.Thread(target=self.recognize_text)
        thread.daemon = True
        thread.start()
    
    def recognize_text(self):
        """تشخیص متن با OCR"""
        try:
            self.processing = True
            print("Starting OCR recognition...")
            
            # آماده‌سازی تصویر برای OCR
            processed_image = self.preprocess_image(self.pil_image)
            
            # OCR
            text = pytesseract.image_to_string(
                processed_image,
                lang='eng',
                config='--oem 1 --psm 6'
            ).strip()  #فضاهای خالی اول و آخر متن رو حذف می‌کنه
            
            self.recognized_text = self.clean_text(text)
            
            # به‌روزرسانی UI در main thread
            self.root.after(0, self.update_results)
            
        except Exception as e:
            print(f"OCR Error: {e}")
            self.root.after(0, lambda: self.show_error("Please try again."))
        
        finally:
            self.processing = False
    
    def preprocess_image(self, pil_img):
        """پیش‌پردازش تصویر برای OCR بهتر"""
        img = pil_img.copy()
        
        # تبدیل به grayscale
        if img.mode != 'L':
            img = img.convert('L')
        
        # بزرگ کردن
        width, height = img.size
        if width < 1200:
            scale_factor = 1200 / width
            new_size = (int(width * scale_factor), int(height * scale_factor))
            img = img.resize(new_size, Image.Resampling.LANCZOS)
        
        # افزایش کنتراست
        enhancer = ImageEnhance.Contrast(img)
        img = enhancer.enhance(2.0)
        
        # تیز کردن
        img = img.filter(ImageFilter.SHARPEN)
        
        # آستانه‌گذاری
        img_array = np.array(img)
        _, binary = cv2.threshold(img_array, 0, 255, cv2.THRESH_BINARY + cv2.THRESH_OTSU)
        
        return Image.fromarray(binary)
    
    def clean_text(self, text):
        """تمیز کردن متن"""
        if not text:
            return text
        
        # حذف خطوط خالی اضافی
        text = re.sub(r'\n\s*\n', '\n', text)
        
        # حذف فاصله‌های اضافی
        text = re.sub(r'[ \t]+', ' ', text)
        
        # حذف کاراکترهای عجیب اما حفظ علائم نگارشی
        text = re.sub(r'[^\w\s.,!?;:()"\'-]', '', text)
        
        return text.strip()
    
    def update_results(self):
        """به‌روزرسانی نتایج در UI"""
        # توقف progress bar
        self.progress_bar.stop()
        self.progress_label.config(text="")
        self.recognize_btn.configure(state='normal')
        
        # نمایش نتیجه
        self.text_result.configure(state='normal')
        self.text_result.delete('1.0', 'end')
        
        if self.recognized_text:
            self.text_result.insert('1.0', self.recognized_text)
            
            # نمایش آمار
            print(f"OCR completed: {self.recognized_text[:50]}...")
        else:
            error_msg = " No text could be recognized"
            self.text_result.insert('1.0', error_msg)
        
        self.text_result.configure(state='disabled')
    
    
    def show_error(self, message):
        """نمایش خطا"""
        self.progress_bar.stop()
        self.progress_label.config(text="")
        self.recognize_btn.configure(state='normal')
        
        self.text_result.configure(state='normal')
        self.text_result.delete('1.0', 'end')
        self.text_result.insert('1.0', message)
        self.text_result.configure(state='disabled')

def main():
    """Main function"""
    root = tk.Tk() #پنجره ای که برنامه توش ران شه 
    HandwritingOCRApp(root)
    # تنظیمات پنجره
    root.minsize(1000, 700)
    root.mainloop()

if __name__ == "__main__":
    main()