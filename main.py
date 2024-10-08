import tkinter as tk
from tkinter import ttk, filedialog, messagebox
from PyPDF2 import PdfReader, PdfWriter
from PIL import Image, ImageTk
import fitz  # PyMuPDF
import os

class App:
    def __init__(self, root):
        self.root = root
        self.root.title("PDF Organizer")

        # Initialize for later uses
        self.pdf_pages = []
        self.current_page = 0
        self.page_rotations = {}  # To store rotations for each page
        
        self.select_button = ttk.Button(root, text="Select PDFs", command=self.select_pdfs)
        self.select_button.pack(pady=20)
        
        self.carousel_frame = tk.Frame(root)
        self.carousel_frame.pack(fill=tk.BOTH, expand=True)
        
        self.page_label = tk.Label(self.carousel_frame, text="")
        self.page_label.pack(pady=10)
        
        self.navigation_frame = tk.Frame(self.carousel_frame)
        self.navigation_frame.pack(pady=10)
        
        self.prev_button = ttk.Button(self.navigation_frame, text="Previous", command=self.prev_page)
        self.prev_button.grid(row=0, column=0, padx=10)
        
        self.next_button = ttk.Button(self.navigation_frame, text="Next", command=self.next_page)
        self.next_button.grid(row=0, column=1, padx=10)
        
        self.delete_button = ttk.Button(self.carousel_frame, text="Delete Page", command=self.delete_page)
        self.delete_button.pack(pady=10)
        
        self.rotate_left_button = ttk.Button(self.carousel_frame, text="Rotate Left", command=lambda: self.rotate_page(-90))
        self.rotate_left_button.pack(side=tk.LEFT, padx=10)
        
        self.rotate_right_button = ttk.Button(self.carousel_frame, text="Rotate Right", command=lambda: self.rotate_page(90))
        self.rotate_right_button.pack(side=tk.RIGHT, padx=10)

        self.reorder_button = ttk.Button(root, text="Reorder Pages", command=self.reorder_pages)
        self.reorder_button.pack(pady=10)
        
        self.save_button = ttk.Button(root, text="Save", command=self.save_pdf)
        self.save_button.pack(pady=20)

    def select_pdfs(self):
        file_paths = filedialog.askopenfilenames(filetypes=[("PDF files", "*.pdf")])
        if not file_paths:
            return
        self.load_pdfs(file_paths)
        
    def load_pdfs(self, file_paths):
        self.pdf_pages.clear()
        self.page_rotations.clear()
        for file_path in file_paths:
            pdf_reader = PdfReader(file_path)
            for page_num in range(len(pdf_reader.pages)):
                self.pdf_pages.append((file_path, page_num, pdf_reader.pages[page_num]))
                self.page_rotations[(file_path, page_num)] = 0  # Initial rotation is 0
        self.current_page = 0
        self.show_page()
        
    def pdf_page_to_image(self, pdf_page):
        zoom = 2
        mat = fitz.Matrix(zoom, zoom)
        pix = pdf_page.get_pixmap(matrix=mat)
        image = Image.frombytes("RGB", [pix.width, pix.height], pix.samples)
        return image
    
    def show_page(self):
        if not self.pdf_pages:
            self.page_label.config(text="No pages to display")
            return
        file_path, page_num, page = self.pdf_pages[self.current_page]
        pdf_reader = fitz.open(file_path)
        pdf_page = pdf_reader.load_page(page_num)

        # Apply rotation before displaying
        rotation = self.page_rotations[(file_path, page_num)]
        pdf_page.set_rotation(rotation)
        image = self.pdf_page_to_image(pdf_page)
        image.thumbnail((400, 600))  # Adjust the size as needed

        self.photo = ImageTk.PhotoImage(image)
        self.page_label.config(image=self.photo)
        self.page_label.image = self.photo  # Keep a reference to avoid garbage collection
        self.page_label.config(text=f"File: {os.path.basename(file_path)}, Page: {page_num + 1}, Rotation: {rotation}°")

    def prev_page(self):
        if self.pdf_pages and self.current_page > 0:
            self.current_page -= 1
            self.show_page()
            
    def next_page(self):
        if self.pdf_pages and self.current_page < len(self.pdf_pages) - 1:
            self.current_page += 1
            self.show_page()
            
    def delete_page(self):
        if self.pdf_pages:
            del self.pdf_pages[self.current_page]
            if self.current_page >= len(self.pdf_pages):
                self.current_page = len(self.pdf_pages) - 1
            self.show_page()

    def rotate_page(self, angle):
        if self.pdf_pages:
            file_path, page_num, page = self.pdf_pages[self.current_page]
            self.page_rotations[(file_path, page_num)] += angle
            self.page_rotations[(file_path, page_num)] %= 360  # Keep the rotation between 0 and 360 degrees
            self.show_page()

    def reorder_pages(self):
        self.reorder_window = tk.Toplevel(self.root)
        self.reorder_window.title("Reorder Pages")
        tk.Label(self.reorder_window, text="Enter new order of pages (comma-separated):").pack(pady=10)
        self.reorder_entry = tk.Entry(self.reorder_window)
        self.reorder_entry.pack(pady=10)
        ttk.Button(self.reorder_window, text="Apply", command=self.apply_reorder).pack(pady=10)
        
    def apply_reorder(self):
        new_order = self.reorder_entry.get().split(",")
        try:
            new_order = [int(x) - 1 for x in new_order]
            if any(x < 0 or x >= len(self.pdf_pages) for x in new_order):
                raise ValueError
            self.pdf_pages = [self.pdf_pages[i] for i in new_order]
            self.current_page = 0
            self.show_page()
            self.reorder_window.destroy()
        except ValueError:
            messagebox.showerror("Invalid Order", "Please enter a valid order of pages.")
    
    def save_pdf(self):
        save_path = filedialog.asksaveasfilename(defaultextension=".pdf", filetypes=[("PDF files", "*.pdf")])
        if not save_path:
            return
        pdf_writer = PdfWriter()
        for file_path, page_num, page in self.pdf_pages:
            pdf_reader = PdfReader(file_path)
            pdf_page = pdf_reader.pages[page_num]
            
            # Get the rotation from the stored values and apply it
            rotation = self.page_rotations[(file_path, page_num)]
            pdf_page.rotate(rotation)  # Rotate the page using PyPDF2
            
            pdf_writer.add_page(pdf_page)
            
        with open(save_path, "wb") as output_pdf:
            pdf_writer.write(output_pdf)
        messagebox.showinfo("Save PDF", "PDF saved successfully!")
if __name__ == "__main__":
    root = tk.Tk()
    app = App(root)
    root.mainloop()
