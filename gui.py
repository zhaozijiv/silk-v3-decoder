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
        self.status_var = StringVar(value="")

        # UI 构建
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
        Label(master, textvariable=self.status_var, fg="blue").grid(row=5, column=0, columnspan=3, sticky="w", padx=10)

    def browse_input(self):
        path = filedialog.askdirectory() if self.batch_var.get() else filedialog.askopenfilename()
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
        ffmpeg = os.path.join(script_dir, "ffmpeg.exe" if os.name == "nt" else "ffmpeg")

        if not os.path.isfile(decoder):
            messagebox.showerror("Error", f"decoder.exe not found:\n{decoder}")
            return
        if not os.path.isfile(ffmpeg):
            messagebox.showerror("Error", f"ffmpeg not found:\n{ffmpeg}")
            return

        if batch:
            if not os.path.isdir(in_path):
                messagebox.showerror("Error", "Invalid folder selected")
                return
            files = [os.path.join(in_path, f) for f in os.listdir(in_path) if f.lower().endswith(".silk")]
            if not files:
                messagebox.showwarning("Warning", "No .silk files found in the folder.")
                return
        else:
            files = [in_path]
            out_dir = out_dir or os.path.dirname(in_path)

        if not os.path.isdir(out_dir):
            messagebox.showerror("Error", "Please select a valid output directory")
            return

        failed = []

        for src in files:
            base = os.path.splitext(os.path.basename(src))[0]
            pcm = os.path.join(out_dir, base + ".pcm")
            dst = os.path.join(out_dir, f"{base}.{out_fmt}")

            self.status_var.set(f"Converting: {os.path.basename(src)}")
            self.master.update()

            try:
                subprocess.run([decoder, src, pcm], check=True)
                subprocess.run(
                    [ffmpeg, "-y", "-f", "s16le", "-ar", "24000", "-ac", "1", "-i", pcm, dst],
                    check=True
                )
            except subprocess.CalledProcessError:
                failed.append(src)
            finally:
                if os.path.exists(pcm):
                    os.remove(pcm)

        self.status_var.set("")
        if failed:
            messagebox.showwarning("Done", f"{len(failed)} file(s) failed to convert.")
        else:
            messagebox.showinfo("Done", "All conversions completed successfully.")


def main():
    root = Tk()
    SilkGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()

