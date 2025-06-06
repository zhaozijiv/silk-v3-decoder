import os
import subprocess
import sys
from tkinter import Tk, filedialog, messagebox, ttk
from tkinter import StringVar, BooleanVar, Label, Entry, Button, Checkbutton


class SilkGUI:
    def __init__(self, master):
        self.master = master
        master.title("Silk Converter")

        self.input_path = StringVar()
        self.output_dir = StringVar()
        self.format_var = StringVar(value="mp3")
        self.batch_var = BooleanVar(value=False)

        Label(master, text="Input file or folder:").grid(row=0, column=0, sticky="w")
        Entry(master, textvariable=self.input_path, width=50).grid(row=0, column=1, padx=5)
        Button(master, text="Browse", command=self.browse_input).grid(row=0, column=2)

        Checkbutton(master, text="Batch mode (folder)", variable=self.batch_var).grid(row=1, column=1, sticky="w")

        Label(master, text="Output directory:").grid(row=2, column=0, sticky="w")
        Entry(master, textvariable=self.output_dir, width=50).grid(row=2, column=1, padx=5)
        Button(master, text="Browse", command=self.browse_output).grid(row=2, column=2)

        Label(master, text="Output format:").grid(row=3, column=0, sticky="w")
        format_cb = ttk.Combobox(master, textvariable=self.format_var,
                                 values=["mp3", "wav", "ogg"], width=10, state="readonly")
        format_cb.grid(row=3, column=1, sticky="w")

        Button(master, text="Start", command=self.start).grid(row=4, column=1, pady=5)

    def browse_input(self):
        if self.batch_var.get():
            path = filedialog.askdirectory()
        else:
            path = filedialog.askopenfilename()
        if path:
            self.input_path.set(path)

    def browse_output(self):
        path = filedialog.askdirectory()
        if path:
            self.output_dir.set(path)

    def start(self):
        in_path = self.input_path.get()
        out_dir = self.output_dir.get()
        out_fmt = self.format_var.get()
        batch = self.batch_var.get()

        if not in_path:
            messagebox.showerror("Error", "Please select input path")
            return

        script_dir = os.path.dirname(os.path.abspath(__file__))
        decoder = os.path.join(script_dir, "decoder.exe")
        ffmpeg = os.path.join(script_dir, "ffmpeg")
        if os.name == "nt":
            ffmpeg += ".exe"

        if not os.path.isfile(decoder):
            messagebox.showerror("Error", f"decoder.exe not found: {decoder}")
            return
        if not os.path.isfile(ffmpeg):
            messagebox.showerror("Error", f"ffmpeg not found: {ffmpeg}")
            return

        if batch:
            if not out_dir:
                messagebox.showerror("Error", "Please select output directory")
                return
            files = [os.path.join(in_path, f) for f in os.listdir(in_path)]
        else:
            files = [in_path]
            out_dir = out_dir or os.path.dirname(in_path)

        for src in files:
            base = os.path.splitext(os.path.basename(src))[0]
            pcm = os.path.join(out_dir, base + ".pcm")
            dst = os.path.join(out_dir, f"{base}.{out_fmt}")
            try:
                subprocess.run([decoder, src, pcm], check=True)
                subprocess.run(
                    [ffmpeg, "-y", "-f", "s16le", "-ar", "24000", "-ac", "1",
                     "-i", pcm, dst],
                    check=True,
                )
            except subprocess.CalledProcessError:
                if os.path.exists(pcm):
                    os.remove(pcm)
                messagebox.showerror("Error", f"Failed to convert {src}")
                return
            finally:
                if os.path.exists(pcm):
                    os.remove(pcm)

        messagebox.showinfo("Done", "Conversion finished")


def main():
    root = Tk()
    SilkGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
