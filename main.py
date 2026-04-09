import os
import sys
import tkinter as tk
from tkinter import filedialog, messagebox, ttk

import math

import fitz  # PyMuPDF
import pandas as pd

# Color palette (matches BUCM seal)
MINT = '#E8F5E9'
GREEN = '#2E7D32'

# Asset path — works both as .py and as PyInstaller .exe
ASSET_DIR = getattr(sys, '_MEIPASS', os.path.dirname(__file__))


class WatermarkApp:
    def __init__(self, root):
        self.root = root
        self.root.title('BUCM ATLAS - Iwas Leak')
        self.root.geometry('525x630')
        self.root.resizable(False, False)
        self.root.configure(bg=MINT)
        self.pdf_path = None
        self.csv_path = None
        self.output_dir = None
        self.logo_img = None
        self.setup_ui()

    def setup_ui(self):
        # Logo badge centered at top
        logo_path = os.path.join(ASSET_DIR, 'atlas.jpg')
        if os.path.exists(logo_path):
            from PIL import Image, ImageTk
            img = Image.open(logo_path).resize((100, 100), Image.LANCZOS)
            self.logo_img = ImageTk.PhotoImage(img)
            logo_label = tk.Label(self.root, image=self.logo_img, bg=MINT)
            logo_label.place(relx=0.5, y=10, anchor='n')

        # Hover style for buttons
        def btn_hover(widget):
            widget.configure(highlightthickness=0, bd=1, relief='solid',
                             highlightbackground=GREEN)
            widget.bind('<Enter>', lambda e: widget.configure(bg='#C8E6C9'))
            widget.bind('<Leave>', lambda e: widget.configure(bg='white'))

        # Buttons
        btn_y = 120
        self.select_pdf_btn = tk.Button(self.root, text='Select PDF', command=self.select_pdf, width=55, height=2, bg='white', fg='#333333', font=('Arial', 9), relief='solid', bd=1)
        self.select_pdf_btn.place(relx=0.5, y=btn_y, anchor='n')
        btn_hover(self.select_pdf_btn)

        self.select_csv_btn = tk.Button(self.root, text='Select CSV', command=self.select_csv, width=55, height=2, bg='white', fg='#333333', font=('Arial', 9), relief='solid', bd=1)
        self.select_csv_btn.place(relx=0.5, y=btn_y + 45, anchor='n')
        btn_hover(self.select_csv_btn)

        self.select_dir_btn = tk.Button(self.root, text='Select Output Folder', command=self.select_output_dir, width=55, height=2, bg='white', fg='#333333', font=('Arial', 9), relief='solid', bd=1)
        self.select_dir_btn.place(relx=0.5, y=btn_y + 90, anchor='n')
        btn_hover(self.select_dir_btn)

        self.watermark_btn = tk.Button(self.root, text='Watermark PDF', command=self.watermark_pdfs, width=55, height=2, bg='white', fg='#333333', font=('Arial', 9, 'bold'), relief='solid', bd=1)
        self.watermark_btn.place(relx=0.5, y=btn_y + 135, anchor='n')

        # Opacity slider
        self.opacity_frame = tk.Frame(self.root, bg=MINT)
        self.opacity_frame.place(relx=0.5, y=btn_y + 190, anchor='n')
        tk.Label(self.opacity_frame, text='Opacity:', bg=MINT, fg='#555555', font=('Arial', 9), width=7, anchor='e').pack(side='left')
        self.opacity_var = tk.DoubleVar(value=0.15)
        self.opacity_scale = tk.Scale(
            self.opacity_frame, from_=0.05, to=0.50, resolution=0.01,
            orient='horizontal', variable=self.opacity_var, length=280,
            bg=MINT, highlightthickness=0, troughcolor='#C8E6C9',
            activebackground=GREEN, showvalue=False,
        )
        self.opacity_scale.pack(side='left')
        self.opacity_pct = tk.Label(self.opacity_frame, text='15%', bg=MINT, fg=GREEN, font=('Arial', 9, 'bold'), width=4)
        self.opacity_pct.pack(side='left')
        self.opacity_var.trace_add('write', lambda *_: self.opacity_pct.config(text=f'{int(self.opacity_var.get() * 100)}%'))

        # Density slider (1-5 repeats)
        self.density_frame = tk.Frame(self.root, bg=MINT)
        self.density_frame.place(relx=0.5, y=btn_y + 225, anchor='n')
        tk.Label(self.density_frame, text='Density:', bg=MINT, fg='#555555', font=('Arial', 9), width=7, anchor='e').pack(side='left')
        self.density_var = tk.IntVar(value=3)
        self.density_scale = tk.Scale(
            self.density_frame, from_=1, to=5, resolution=1,
            orient='horizontal', variable=self.density_var, length=280,
            bg=MINT, highlightthickness=0, troughcolor='#C8E6C9',
            activebackground=GREEN, showvalue=False,
        )
        self.density_scale.pack(side='left')
        self.density_val = tk.Label(self.density_frame, text='3', bg=MINT, fg=GREEN, font=('Arial', 9, 'bold'), width=4)
        self.density_val.pack(side='left')
        self.density_var.trace_add('write', lambda *_: self.density_val.config(text=str(self.density_var.get())))

        # Selection labels
        label_y = btn_y + 265
        self.pdf_label = tk.Label(self.root, text='PDF: None', anchor='w', width=60, bg='white', fg='#555555', font=('Arial', 8), relief='solid', bd=1, padx=4)
        self.pdf_label.place(relx=0.5, y=label_y, anchor='n')
        self.csv_label = tk.Label(self.root, text='CSV: None', anchor='w', width=60, bg='white', fg='#555555', font=('Arial', 8), relief='solid', bd=1, padx=4)
        self.csv_label.place(relx=0.5, y=label_y + 25, anchor='n')
        self.dir_label = tk.Label(self.root, text='Output: None', anchor='w', width=60, bg='white', fg='#555555', font=('Arial', 8), relief='solid', bd=1, padx=4)
        self.dir_label.place(relx=0.5, y=label_y + 50, anchor='n')

        # Status label
        self.status_label = tk.Label(self.root, text='', wraplength=400, bg=MINT, fg=GREEN, font=('Arial', 9))
        self.status_label.place(relx=0.5, y=label_y + 82, anchor='n')

        # Progress bar
        style = ttk.Style()
        style.theme_use('default')
        style.configure('Green.Horizontal.TProgressbar', troughcolor='#C8E6C9', background=GREEN)
        self.progress = ttk.Progressbar(self.root, length=425, mode='determinate', style='Green.Horizontal.TProgressbar')
        self.progress.place(relx=0.5, y=label_y + 105, anchor='n')

        # Footer — single centered line
        self.footer_frame = tk.Frame(self.root, bg=MINT)
        self.footer_frame.place(relx=0.5, y=label_y + 140, anchor='n')
        tk.Label(self.footer_frame, text='Envisioned by ', font=('Arial', 7), bg=MINT, fg='#999999').pack(side='left')
        tk.Label(self.footer_frame, text='11th Regulus Internus Orange Gandia', font=('Arial', 7, 'bold'), bg=MINT, fg=GREEN).pack(side='left')
        tk.Label(self.footer_frame, text='  \u2502  ', font=('Arial', 7), bg=MINT, fg='#CCCCCC').pack(side='left')
        tk.Label(self.footer_frame, text='Made by ', font=('Arial', 7), bg=MINT, fg='#999999').pack(side='left')
        tk.Label(self.footer_frame, text='KMercad0', font=('Arial', 7, 'bold'), bg=MINT, fg=GREEN).pack(side='left')

    def _update_ready_state(self):
        if self.pdf_path and self.csv_path and self.output_dir:
            self.watermark_btn.configure(bg='#A5D6A7', fg='#1B5E20', text='Watermark PDF  \u2713 Ready')
        else:
            self.watermark_btn.configure(bg='white', fg='#333333', text='Watermark PDF')

    def select_pdf(self):
        path = filedialog.askopenfilename(filetypes=[('PDF Files', '*.pdf')])
        if path:
            self.pdf_path = path
            self.pdf_label.config(text=f'PDF: {os.path.basename(path)}')
            self._update_ready_state()

    def select_csv(self):
        path = filedialog.askopenfilename(filetypes=[('CSV Files', '*.csv')])
        if path:
            self.csv_path = path
            self.csv_label.config(text=f'CSV: {os.path.basename(path)}')
            self._update_ready_state()

    def select_output_dir(self):
        path = filedialog.askdirectory(title='Select Output Folder')
        if path:
            self.output_dir = path
            self.dir_label.config(text=f'Output: {os.path.basename(path)}')
            self._update_ready_state()

    def watermark_pdfs(self):
        missing = []
        if not self.pdf_path:
            missing.append('PDF file')
        if not self.csv_path:
            missing.append('CSV file')
        if not self.output_dir:
            missing.append('Output folder')
        if missing:
            messagebox.showerror('Error', f'Please select: {", ".join(missing)}')
            return
        try:
            df = pd.read_csv(self.csv_path)
            if df.shape[1] < 3:
                messagebox.showerror('Error', 'CSV does not have at least 3 columns.')
                return
            names = df.iloc[:, 2].dropna().astype(str).tolist()
            base_filename = os.path.splitext(os.path.basename(self.pdf_path))[0]
            opacity = self.opacity_var.get()
            total = len(names)
            self.progress['maximum'] = total
            self.progress['value'] = 0
            for i, name in enumerate(names):
                out_pdf = os.path.join(self.output_dir, f"{base_filename}_{name.replace(' ', '_')}.pdf")
                self.create_watermarked_pdf(self.pdf_path, name, out_pdf, opacity, self.density_var.get())
                self.progress['value'] = i + 1
                self.status_label.config(text=f'Processing {i + 1}/{total}: {name}')
                self.root.update_idletasks()
            self.status_label.config(text=f'Done! {total} PDFs saved to {os.path.basename(self.output_dir)}/')
            messagebox.showinfo('Success', f'Created {total} watermarked PDFs!')
        except Exception as e:
            messagebox.showerror('Error', str(e))

    def create_watermarked_pdf(self, pdf_path, watermark_text, output_path, opacity, density=3):
        doc = fitz.open(pdf_path)
        fontsize = 40
        rotation_matrix = fitz.Matrix(45)

        for page in doc:
            rect = page.rect
            shape = page.new_shape()

            if density == 1:
                # Single centered watermark
                pivot = fitz.Point(rect.width / 2, rect.height / 2)
                shape.insert_text(
                    pivot, watermark_text, fontsize=fontsize, fontname='helv',
                    color=(0, 0, 0), fill_opacity=opacity, morph=(pivot, rotation_matrix),
                )
            else:
                # Scale font size to fit the requested density
                # k = text width per unit of fontsize
                k = fitz.get_text_length(watermark_text, fontname='helv', fontsize=1)
                angle_rad = math.radians(45)
                sin_a = math.sin(angle_rad)
                cos_a = math.cos(angle_rad)

                # Available space per row based on density
                available_y = rect.height / density

                # Solve: fontsize * ((k+1)*sin_a + 1) <= available_y
                # The +1 accounts for gap (one em)
                max_fontsize_for_density = available_y / ((k + 1) * sin_a + 1)
                fs = min(fontsize, max_fontsize_for_density)

                # Compute actual spacing from the resolved font size
                text_width = k * fs
                rotated_x = text_width * cos_a + fs * sin_a
                gap = fs  # one em of padding
                step_x = int(rotated_x + gap)
                step_y = int(rect.height / density)

                for x in range(-int(rect.width), int(rect.width * 2), step_x):
                    for y in range(0, int(rect.height), step_y):
                        pivot = fitz.Point(x, y)
                        shape.insert_text(
                            pivot, watermark_text, fontsize=fs, fontname='helv',
                            color=(0, 0, 0), fill_opacity=opacity, morph=(pivot, rotation_matrix),
                        )

            shape.commit()

        doc.save(output_path)
        doc.close()


def main():
    # Must be called BEFORE tk.Tk() — tells Windows this is a standalone app
    try:
        import ctypes
        ctypes.windll.shell32.SetCurrentProcessExplicitAppUserModelID('bucm.atlas.iwasleak')
    except Exception:
        pass

    root = tk.Tk()

    ico_path = os.path.join(ASSET_DIR, 'atlas.ico')
    if os.path.exists(ico_path):
        root.iconbitmap(default=ico_path)

    WatermarkApp(root)
    root.mainloop()


if __name__ == '__main__':
    main()
