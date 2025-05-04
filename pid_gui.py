import tkinter as tk
from tkinter import filedialog, ttk, messagebox
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
from scipy.optimize import minimize


class PIDTuningApp:
    def __init__(self, master):
        self.master = master
        master.title("PID Tuning GUI")

        # File upload
        self.load_button = ttk.Button(master, text="Load CSV/Excel", command=self.load_file)
        self.load_button.grid(row=0, column=0, columnspan=2, pady=5)

        # Column selectors
        self.pv_col = tk.StringVar()
        self.out_col = tk.StringVar()
        self.sp_col = tk.StringVar()

        ttk.Label(master, text="PV Column:").grid(row=1, column=0, sticky="e")
        self.pv_menu = ttk.Combobox(master, textvariable=self.pv_col)
        self.pv_menu.grid(row=1, column=1)

        ttk.Label(master, text="OUT Column:").grid(row=2, column=0, sticky="e")
        self.out_menu = ttk.Combobox(master, textvariable=self.out_col)
        self.out_menu.grid(row=2, column=1)

        ttk.Label(master, text="SP Column:").grid(row=3, column=0, sticky="e")
        self.sp_menu = ttk.Combobox(master, textvariable=self.sp_col)
        self.sp_menu.grid(row=3, column=1)

        # Initial guesses
        ttk.Label(master, text="Initial Kp:").grid(row=4, column=0, sticky="e")
        self.kp_entry = ttk.Entry(master)
        self.kp_entry.insert(0, "1.0")
        self.kp_entry.grid(row=4, column=1)

        ttk.Label(master, text="Initial Ki:").grid(row=5, column=0, sticky="e")
        self.ki_entry = ttk.Entry(master)
        self.ki_entry.insert(0, "0.5")
        self.ki_entry.grid(row=5, column=1)

        ttk.Label(master, text="Initial Kd:").grid(row=6, column=0, sticky="e")
        self.kd_entry = ttk.Entry(master)
        self.kd_entry.insert(0, "0.1")
        self.kd_entry.grid(row=6, column=1)

        self.fit_button = ttk.Button(master, text="Fit PID", command=self.fit_pid)
        self.fit_button.grid(row=7, column=0, columnspan=2, pady=10)

    def load_file(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV and Excel files", "*.csv *.xlsx")])
        if not file_path:
            return

        try:
            if file_path.endswith(".csv"):
                self.df = pd.read_csv(file_path)
            else:
                self.df = pd.read_excel(file_path)
            columns = list(self.df.columns)
            self.pv_menu['values'] = columns
            self.out_menu['values'] = columns
            self.sp_menu['values'] = columns
        except Exception as e:
            messagebox.showerror("Error", str(e))

    def fit_pid(self):
        try:
            df = self.df
            pv = df[self.pv_col.get()].values
            out = df[self.out_col.get()].values
            sp = df[self.sp_col.get()].values
            time = df['time'].values if 'time' in df.columns else np.linspace(0, len(df)-1, len(df))

            kp0 = float(self.kp_entry.get())
            ki0 = float(self.ki_entry.get())
            kd0 = float(self.kd_entry.get())
            initial_guess = [kp0, ki0, kd0]

            def pid_model(params):
                kp, ki, kd = params
                error = sp - pv
                integral = np.cumsum(error) * np.mean(np.diff(time))
                derivative = np.gradient(error, time)
                model_out = kp * error + ki * integral + kd * derivative
                return model_out

            def loss(params):
                model = pid_model(params)
                return np.mean((model - out) ** 2)

            result = minimize(loss, initial_guess)
            kp_opt, ki_opt, kd_opt = result.x

            # Simulate model output with optimized parameters
            model_output = pid_model([kp_opt, ki_opt, kd_opt])

            # Plot
            plt.figure()
            plt.plot(time, pv, label="PV (Process Variable)", linewidth=2)
            plt.plot(time, sp, label="SP (Setpoint)", linestyle='--', linewidth=2)
            plt.plot(time, out, label="OUT (Controller Output)", linestyle='-.', linewidth=2)
            plt.plot(time, model_output, label="Fitted PID Output", linestyle=':', linewidth=2)
            plt.xlabel("Time")
            plt.ylabel("Value")
            plt.title(f"Fitted PID → Kp={kp_opt:.2f}, Ki={ki_opt:.2f}, Kd={kd_opt:.2f}")
            plt.legend()
            plt.grid(True)
            plt.tight_layout()
            plt.show()

        except Exception as e:
            messagebox.showerror("Fitting Error", str(e))


# === Run App ===
if __name__ == "__main__":
    root = tk.Tk()
    app = PIDTuningApp(root)
    root.mainloop()
