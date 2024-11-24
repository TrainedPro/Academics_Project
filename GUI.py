import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import pandas as pd

class FileProcessorApp:
    def __init__(self, root):
        self.root = root
        self.root.title("File Processor GUI")
        self.file_path = None
        self.create_first_page()

    def create_first_page(self):
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="Welcome to File Processor", font=("Arial", 16)).pack(pady=10)
        tk.Button(self.root, text="Open File", command=self.open_file).pack(pady=5)
        tk.Button(self.root, text="Insert File", command=self.open_file).pack(pady=5)

    def open_file(self):
        self.file_path = filedialog.askopenfilename(
            filetypes=[("All Files", "*.*"), ("CSV Files", "*.csv"), ("Excel Files", "*.xlsx")]
        )
        if self.file_path:
            self.create_second_page()

    def create_second_page(self):
        # Clear any existing widgets
        for widget in self.root.winfo_children():
            widget.destroy()

        tk.Label(self.root, text="File Contents", font=("Arial", 14)).pack(pady=10)

        # Display file contents
        try:
            if self.file_path.endswith(".csv"):
                self.data = pd.read_csv(self.file_path)
            elif self.file_path.endswith(".xlsx"):
                self.data = pd.read_excel(self.file_path)
            else:
                messagebox.showerror("Error", "Unsupported file format")
                self.create_first_page()
                return

            # Table to display data
            tree = ttk.Treeview(self.root, columns=list(self.data.columns), show='headings')
            for col in self.data.columns:
                tree.heading(col, text=col)
                tree.column(col, width=100)
            for _, row in self.data.iterrows():
                tree.insert("", "end", values=list(row))
            tree.pack(pady=10)

            # Buttons to export file
            tk.Button(self.root, text="Export as CSV", command=self.export_as_csv).pack(side="left", padx=20, pady=10)
            tk.Button(self.root, text="Export as XLSX", command=self.export_as_xlsx).pack(side="right", padx=20, pady=10)

        except Exception as e:
            messagebox.showerror("Error", str(e))
            self.create_first_page()

    def export_as_csv(self):
        save_path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV Files", "*.csv")])
        if save_path:
            self.data.to_csv(save_path, index=False)
            messagebox.showinfo("Success", f"File exported as CSV to {save_path}")

    def export_as_xlsx(self):
        save_path = filedialog.asksaveasfilename(defaultextension=".xlsx", filetypes=[("Excel Files", "*.xlsx")])
        if save_path:
            self.data.to_excel(save_path, index=False)
            messagebox.showinfo("Success", f"File exported as XLSX to {save_path}")

if __name__ == "__main__":
    root = tk.Tk()
    app = FileProcessorApp(root)
    root.mainloop()

