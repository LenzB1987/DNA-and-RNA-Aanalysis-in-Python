import customtkinter as ctk
from tkinter import filedialog, messagebox
from Bio.Seq import Seq
import csv
import os

# Set appearance to Dark Mode
ctk.set_appearance_mode("dark")
ctk.set_default_color_theme("blue")

class BioApp(ctk.CTk):
    def __init__(self):
        super().__init__()

        self.title("LENZ BYAHURWA DNA AND RNA ANALYSIS")
        self.geometry("1150x700")

        # UI Layout
        self.grid_columnconfigure((0, 1), weight=1)
        self.grid_rowconfigure(2, weight=1)

        # Header
        self.header = ctk.CTkLabel(self, text="LENZ BYAHURWA DNA AND RNA MANIPULATION TOOL", 
                                  font=ctk.CTkFont(size=22, weight="bold"))
        self.header.grid(row=0, column=0, columnspan=2, padx=20, pady=20)

        # Left Textbox (Input)
        self.input_label = ctk.CTkLabel(self, text="Sequence Input (A, T, C, G, U)", font=ctk.CTkFont(weight="bold"))
        self.input_label.grid(row=1, column=0, padx=20, pady=(0, 5), sticky="sw")
        self.input_text = ctk.CTkTextbox(self, font=("JetBrains Mono", 14), border_width=1)
        self.input_text.grid(row=2, column=0, padx=20, pady=(0, 20), sticky="nsew")
        self.input_text.bind("<KeyRelease>", self.validate_input)

        # Right Textbox (Output)
        self.output_label = ctk.CTkLabel(self, text="Analysis Result", font=ctk.CTkFont(weight="bold"))
        self.output_label.grid(row=1, column=1, padx=20, pady=(0, 5), sticky="sw")
        self.output_text = ctk.CTkTextbox(self, font=("JetBrains Mono", 14), fg_color="#1a1a1a", border_width=1)
        self.output_text.grid(row=2, column=1, padx=20, pady=(0, 20), sticky="nsew")

        # Operations Frame
        self.ops_frame = ctk.CTkFrame(self)
        self.ops_frame.grid(row=3, column=0, columnspan=2, padx=20, pady=10, sticky="ew")
        
        self.buttons = []

        # Row 1 of operations
        self.create_op_btn("Complement", self.do_complement, 0, 0)
        self.create_op_btn("Sequencing", self.do_sequencing, 0, 1)
        self.create_op_btn("Transcripting", self.do_transcribe, 0, 2)
        self.create_op_btn("Translation", self.do_translate, 0, 3)
        
        # Row 2 of operations
        self.create_op_btn("Replication", self.do_replicate, 1, 0)
        self.create_op_btn("Rev. Transcription", self.do_rev_transcribe, 1, 1)
        self.create_op_btn("Rev. Translation", self.do_rev_translate, 1, 2)
        
        # Utility Side Buttons
        self.btn_open = ctk.CTkButton(self.ops_frame, text="Open File", command=self.open_file, width=120, fg_color="#444")
        self.btn_open.grid(row=0, column=4, padx=15, pady=5)
        
        self.btn_save = ctk.CTkButton(self.ops_frame, text="Export", command=self.save_file, 
                                     fg_color="#2b7336", hover_color="#1e5226", width=120)
        self.btn_save.grid(row=1, column=4, padx=15, pady=5)

        # Exit
        self.btn_exit = ctk.CTkButton(self, text="EXIT", command=self.quit, fg_color="#912b2b", 
                                     hover_color="#b33636", width=80)
        self.btn_exit.place(relx=0.98, rely=0.03, anchor="ne")

    def create_op_btn(self, text, cmd, r, c):
        btn = ctk.CTkButton(self.ops_frame, text=text, command=cmd, width=150)
        btn.grid(row=r, column=c, padx=5, pady=5)
        self.buttons.append(btn)
        return btn

    def toggle_btns(self, state):
        for btn in self.buttons:
            btn.configure(state=state)

    def validate_input(self, event=None):
        raw = self.input_text.get("1.0", "end-1c").upper()
        clean = "".join([char for char in raw if char in "ATCGU\n "])
        if raw != clean:
            curr = self.input_text.index("insert")
            self.input_text.delete("1.0", "end")
            self.input_text.insert("1.0", clean)
            self.input_text.mark_set("insert", curr)

    def get_seq(self):
        txt = self.input_text.get("1.0", "end-1c").replace("\n", "").replace(" ", "")
        if len(txt) < 4:
            messagebox.showwarning("Sequence Error", "DNA/RNA must be at least 4 chars.")
            return None
        return Seq(txt)

    def run_safe(self, func):
        self.toggle_btns("disabled")
        try:
            res = func()
            self.output_text.delete("1.0", "end")
            self.output_text.insert("1.0", str(res))
        except Exception as e:
            messagebox.showerror("Analysis Error", str(e))
        finally:
            self.toggle_btns("normal")

    def do_complement(self):
        s = self.get_seq()
        if s: self.run_safe(lambda: s.complement())

    def do_sequencing(self):
        s = self.get_seq()
        if s: self.run_safe(lambda: " ".join([str(s)[i:i+10] for i in range(0, len(s), 10)]))

    def do_transcribe(self):
        s = self.get_seq()
        if s: 
            if "U" in str(s): 
                messagebox.showerror("Error", "Cannot transcribe RNA. Use Rev. Transcription instead.")
                return
            self.run_safe(lambda: s.transcribe())

    def do_translate(self):
        s = self.get_seq()
        if s: 
            # Adjust for triplet codons
            dna_len = len(s)
            if dna_len % 3 != 0: s = s[:-(dna_len % 3)]
            self.run_safe(lambda: s.translate())

    def do_replicate(self):
        s = self.get_seq()
        if s: self.run_safe(lambda: s.complement_reverse())

    def do_rev_transcribe(self):
        s = self.get_seq()
        if s: self.run_safe(lambda: s.back_transcribe())

    def do_rev_translate(self):
        # Bio-logic: This is a complex mapping; providing the reverse frame
        s = self.get_seq()
        if s: self.run_safe(lambda: s[::-1].complement())

    def open_file(self):
        path = filedialog.askopenfilename(filetypes=[("Bio Files", "*.fasta *.txt *.dna")])
        if path:
            with open(path, 'r') as f:
                content = f.read()
                if content.startswith(">"): content = "".join(content.split("\n")[1:])
                clean = "".join([c.upper() for c in content if c.upper() in "ATCGU\n"])
                self.input_text.delete("1.0", "end")
                self.input_text.insert("1.0", clean)

    def save_file(self):
        path = filedialog.asksaveasfilename(defaultextension=".txt", 
                                          filetypes=[("Text", "*.txt"), ("CSV", "*.csv")])
        if path:
            res = self.output_text.get("1.0", "end-1c")
            if path.endswith(".csv"):
                with open(path, 'w', newline='') as f:
                    writer = csv.writer(f)
                    writer.writerow(["Sequence_Type", "Data"])
                    writer.writerow(["Input", self.input_text.get("1.0", "end-1c").strip()])
                    writer.writerow(["Result", res])
            else:
                with open(path, 'w') as f: f.write(res)
            messagebox.showinfo("Export Successful", f"Saved to {os.path.basename(path)}")

if __name__ == "__main__":
    app = BioApp()
    app.mainloop()