# -*- coding: utf-8 -*-
"""Tkinter GUI for encoding or decoding Silk v3 audio files.

The script wraps ``silk_v3_decoder.exe`` and ``silk_v3_encoder.exe``
along with ``ffmpeg`` so Windows users can convert between common audio
formats and Silk v3.  Both single file and batch modes are supported and
several encoder parameters can be tweaked from the GUI.
"""

import os
import subprocess
import sys
from tkinter import filedialog, messagebox, ttk
from tkinter import Tk, StringVar, BooleanVar, Button, Label, Entry, Checkbutton


class SilkConverterGUI:
    def __init__(self, master):
        self.master = master
        master.title("Silk Converter")

        self.input_path = StringVar()
        self.output_dir = StringVar()

        self.mode_var = StringVar(value="decode")
        self.format_var = StringVar()
        self.sample_rate = StringVar(value="24000")
        self.bitrate = StringVar(value="25000")
        self.packet = StringVar(value="20")
        self.complexity = StringVar(value="2")
        self.tencent = BooleanVar(value=True)

        self.batch_var = BooleanVar(value=False)

        Label(master, text="Input file or folder:").grid(row=0, column=0, sticky="w")
        Entry(master, textvariable=self.input_path, width=50).grid(row=0, column=1, padx=5)
        Button(master, text="Browse", command=self.browse_input).grid(row=0, column=2)

        Label(master, text="Output directory:").grid(row=1, column=0, sticky="w")
        Entry(master, textvariable=self.output_dir, width=50).grid(row=1, column=1, padx=5)
        Button(master, text="Browse", command=self.browse_output).grid(row=1, column=2)

        Label(master, text="Mode:").grid(row=2, column=0, sticky="w")
        mode_cb = ttk.Combobox(master, textvariable=self.mode_var,
                               values=["decode", "encode"], width=10, state="readonly")
        mode_cb.grid(row=2, column=1, sticky="w")

        Label(master, text="Output format:").grid(row=3, column=0, sticky="w")
        self.format_combo = ttk.Combobox(master, textvariable=self.format_var, width=10)
        self.format_combo.grid(row=3, column=1, sticky="w")

        Label(master, text="Sample rate:").grid(row=4, column=0, sticky="w")
        Entry(master, textvariable=self.sample_rate, width=10).grid(row=4, column=1, sticky="w")

        Label(master, text="Bitrate (encode):").grid(row=5, column=0, sticky="w")
        Entry(master, textvariable=self.bitrate, width=10).grid(row=5, column=1, sticky="w")

        Label(master, text="Packet(ms):").grid(row=6, column=0, sticky="w")
        Entry(master, textvariable=self.packet, width=10).grid(row=6, column=1, sticky="w")

        Label(master, text="Complexity:").grid(row=7, column=0, sticky="w")
        Entry(master, textvariable=self.complexity, width=10).grid(row=7, column=1, sticky="w")

        Checkbutton(master, text="Tencent mode", variable=self.tencent).grid(row=8, column=1, sticky="w")
        Checkbutton(master, text="Batch mode (folder)", variable=self.batch_var).grid(row=9, column=1, sticky="w")

        Button(master, text="Start", command=self.start).grid(row=10, column=1, pady=5)

        self.mode_var.trace_add("write", lambda *a: self.update_format_options())
        self.update_format_options()

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

    def update_format_options(self):
        if self.mode_var.get() == "decode":
            self.format_combo["values"] = ["mp3", "wav", "ogg"]
            if self.format_var.get() not in ("mp3", "wav", "ogg"):
                self.format_var.set("mp3")
        else:
            self.format_combo["values"] = ["silk"]
            self.format_var.set("silk")

    def start(self):
        in_path = self.input_path.get()
        out_dir = self.output_dir.get()
        out_fmt = self.format_var.get()
        batch = self.batch_var.get()

        if not in_path or not out_dir:
            messagebox.showerror("Error", "Please select input and output paths")
            return

        base_dir = os.path.dirname(os.path.abspath(__file__))
        decoder = os.path.join(base_dir, "silk_v3_decoder.exe")
        encoder = os.path.join(base_dir, "silk_v3_encoder.exe")

        if self.mode_var.get() == "decode" and not os.path.isfile(decoder):
            messagebox.showerror("Error", f"Decoder not found: {decoder}")
            return
        if self.mode_var.get() == "encode" and not os.path.isfile(encoder):
            messagebox.showerror("Error", f"Encoder not found: {encoder}")
            return

        if batch:
            files = [os.path.join(in_path, f) for f in os.listdir(in_path)]
        else:
            files = [in_path]

        for f in files:
            self.convert_file(f, out_fmt, out_dir, decoder, encoder)

        messagebox.showinfo("Done", "Conversion finished")

    def convert_file(self, in_file, out_fmt, out_dir, decoder, encoder):
        base = os.path.splitext(os.path.basename(in_file))[0]
        pcm = os.path.join(out_dir, base + ".pcm")

        if self.mode_var.get() == "decode":
            out_file = os.path.join(out_dir, f"{base}.{out_fmt}")
            cmd = [decoder, "-Fs_API", self.sample_rate.get(), in_file, pcm]
            subprocess.run(cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            if not os.path.isfile(pcm):
                subprocess.run(["ffmpeg", "-y", "-i", in_file, out_file], check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
                return
            ffmpeg_cmd = [
                "ffmpeg", "-y", "-f", "s16le",
                "-ar", self.sample_rate.get(), "-ac", "1",
                "-i", pcm, out_file
            ]
            subprocess.run(ffmpeg_cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
        else:
            out_file = os.path.join(out_dir, f"{base}.silk")
            ffmpeg_cmd = [
                "ffmpeg", "-y", "-i", in_file,
                "-f", "s16le", "-ar", self.sample_rate.get(), "-ac", "1",
                pcm
            ]
            subprocess.run(ffmpeg_cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            enc_cmd = [
                encoder, pcm, out_file,
                "-Fs_API", self.sample_rate.get(),
                "-packetlength", self.packet.get(),
                "-rate", self.bitrate.get(),
                "-complexity", self.complexity.get()
            ]
            if self.tencent.get():
                enc_cmd.append("-tencent")
            subprocess.run(enc_cmd, check=False, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)

        if os.path.isfile(pcm):
            os.remove(pcm)


def main():
    root = Tk()
    SilkConverterGUI(root)
    root.mainloop()


if __name__ == "__main__":
    main()
