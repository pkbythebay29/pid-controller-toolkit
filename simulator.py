import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import ttk, messagebox, filedialog
import matplotlib.pyplot as plt


class PressureSimulatorGUI:
    def __init__(self, master):
        self.master = master
        master.title("Pressure Simulator")

        # === Behavior Selection ===
        ttk.Label(master, text="Select Behavior Type:").grid(row=0, column=0, sticky="w")
        self.behavior_var = tk.StringVar()
        self.behavior_menu = ttk.Combobox(master, textvariable=self.behavior_var, values=[
            "Stable", "Step Change", "Oscillatory", "Nonlinear"
        ])
        self.behavior_menu.grid(row=0, column=1)
        self.behavior_menu.bind("<<ComboboxSelected>>", self.update_sub_options)

        # === Sub-options (Dynamic) ===
        ttk.Label(master, text="Sub-type:").grid(row=1, column=0, sticky="w")
        self.sub_option_var = tk.StringVar()
        self.sub_option_menu = ttk.Combobox(master, textvariable=self.sub_option_var)
        self.sub_option_menu.grid(row=1, column=1)

        # === Delay ===
        ttk.Label(master, text="Delay (seconds):").grid(row=2, column=0, sticky="w")
        self.delay_entry = ttk.Entry(master)
        self.delay_entry.insert(0, "0")
        self.delay_entry.grid(row=2, column=1)

        # === Noise ===
        ttk.Label(master, text="Noise Level (bar):").grid(row=3, column=0, sticky="w")
        self.noise_entry = ttk.Entry(master)
        self.noise_entry.insert(0, "0.5")
        self.noise_entry.grid(row=3, column=1)

        # === Saturation ===
        self.saturation_var = tk.BooleanVar()
        self.saturation_check = ttk.Checkbutton(master, text="Apply Output Saturation", variable=self.saturation_var, command=self.toggle_saturation_entries)
        self.saturation_check.grid(row=4, column=0, columnspan=2, sticky="w")

        ttk.Label(master, text="Min Output (bar):").grid(row=5, column=0, sticky="w")
        self.min_out_entry = ttk.Entry(master)
        self.min_out_entry.grid(row=5, column=1)
        self.min_out_entry.configure(state="disabled")

        ttk.Label(master, text="Max Output (bar):").grid(row=6, column=0, sticky="w")
        self.max_out_entry = ttk.Entry(master)
        self.max_out_entry.grid(row=6, column=1)
        self.max_out_entry.configure(state="disabled")

        # === Buttons ===
        ttk.Button(master, text="Generate & Save", command=self.generate_and_save).grid(row=7, column=0, pady=10)
        ttk.Button(master, text="Show Help / README", command=self.show_help).grid(row=7, column=1, pady=10)

    def update_sub_options(self, event):
        behavior = self.behavior_var.get()
        if behavior == "Stable":
            self.sub_option_menu['values'] = ["Constant", "Drifting", "Random Fluctuations"]
        elif behavior == "Step Change":
            self.sub_option_menu['values'] = ["Single", "Multiple", "Ramp"]
        elif behavior == "Oscillatory":
            self.sub_option_menu['values'] = ["PV Oscillates", "SP Oscillates"]
        elif behavior == "Nonlinear":
            self.sub_option_menu['values'] = ["Saturation Response"]
        self.sub_option_var.set("")

    def toggle_saturation_entries(self):
        state = "normal" if self.saturation_var.get() else "disabled"
        self.min_out_entry.configure(state=state)
        self.max_out_entry.configure(state=state)

    def generate_and_save(self):
        try:
            time = np.linspace(0, 10, 100)
            delay = float(self.delay_entry.get())
            noise = float(self.noise_entry.get())
            min_out = float(self.min_out_entry.get()) if self.saturation_var.get() else None
            max_out = float(self.max_out_entry.get()) if self.saturation_var.get() else None
            behavior = self.behavior_var.get()
            subtype = self.sub_option_var.get()

            if behavior == "Stable":
                sp = np.ones_like(time) * 50
                if subtype == "Drifting":
                    sp += 2 * np.sin(0.2 * time)
                elif subtype == "Random Fluctuations":
                    sp += np.random.normal(0, 1, len(time))
                pv = sp + np.random.normal(0, noise, len(time))

            elif behavior == "Step Change":
                sp = np.ones_like(time) * 40
                if subtype == "Single":
                    sp[time >= 5] = 60
                elif subtype == "Multiple":
                    sp[time >= 3] = 50
                    sp[time >= 6] = 65
                    sp[time >= 8] = 55
                elif subtype == "Ramp":
                    sp = np.linspace(40, 60, len(time))
                pv = np.where(time < delay, sp[0], sp) + np.random.normal(0, noise, len(time))

            elif behavior == "Oscillatory":
                if subtype == "SP Oscillates":
                    sp = 50 + 5 * np.sin(2 * np.pi * 0.2 * time)
                else:
                    sp = np.ones_like(time) * 50
                pv = np.where(time < delay, sp[0], sp) + 8 * np.sin(2 * np.pi * 0.5 * time) + np.random.normal(0, noise, len(time))

            elif behavior == "Nonlinear":
                sp = np.ones_like(time) * 50
                pv = [sp[0] if t < delay else sp[0] + 10 * np.tanh((t - 5) / 2) + np.random.normal(0, noise) for t in time]
                pv = np.array(pv)

            # Generate fake controller output
            out = sp - pv + np.random.normal(0, 0.2, len(time))

            # Saturation
            if self.saturation_var.get():
                pv = np.clip(pv, min_out, max_out)
                out = np.clip(out, min_out, max_out)

            # Save
            path = filedialog.asksaveasfilename(defaultextension=".csv", filetypes=[("CSV", "*.csv")])
            if not path:
                return

            df = pd.DataFrame({'time': time, 'PV': pv, 'OUT': out, 'SP': sp})
            df.to_csv(path, index=False)
            messagebox.showinfo("Saved", f"Data saved to {path}")

            # Plot
            plt.plot(time, pv, label="PV")
            plt.plot(time, sp, label="SP", linestyle="--")
            plt.plot(time, out, label="OUT")
            plt.title(f"Simulated Data ({behavior})")
            plt.xlabel("Time (s)")
            plt.ylabel("Pressure (bar)")
            plt.legend()
            plt.tight_layout()
            plt.show()

        except Exception as e:
            messagebox.showerror("Error", str(e))

    def show_help(self):
        help_text = (
            "📘 Pressure Simulator Help\n\n"
            "This tool generates synthetic pressure control data for PID tuning.\n\n"
            "✅ BEHAVIOR TYPES:\n"
            "- Stable:\n"
            "   • Constant: PV near SP with low noise\n"
            "   • Drifting: PV drifts over time (e.g., leakage)\n"
            "   • Random SP: SP jitters (e.g., manual tuning)\n\n"
            "- Step Change:\n"
            "   • Single: Sudden SP jump\n"
            "   • Multiple: Several SP steps\n"
            "   • Ramp: Gradual increase in SP\n\n"
            "- Oscillatory:\n"
            "   • PV Oscillates: simulates underdamped response\n"
            "   • SP Oscillates: tests controller tracking\n\n"
            "- Nonlinear:\n"
            "   • Simulates actuator saturation and process limits\n\n"
            "🛠️ OPTIONS:\n"
            "- Delay (s): PV lags behind SP\n"
            "- Noise Level (bar): Adds realistic process noise\n"
            "- Saturation (bar): Clamps PV/OUT to mimic equipment limits\n"
        )
        messagebox.showinfo("Help / README", help_text)


# === Launch GUI ===
if __name__ == "__main__":
    root = tk.Tk()
    app = PressureSimulatorGUI(root)
    root.mainloop()
