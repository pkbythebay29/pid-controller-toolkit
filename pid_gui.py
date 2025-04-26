import tkinter as tk
from tkinter import filedialog, messagebox, ttk
import pandas as pd
import numpy as np
import scipy.optimize as opt
import matplotlib.pyplot as plt

class PIDGUI:
    def __init__(self, master):
        self.master = master
        master.title("PID Controller Parameter Fitting")

        self.data = None
        self.file_loaded = False

        # Labels
        tk.Label(master, text="PID Controller Parameter Fitting", font=('Arial', 16)).pack(pady=10)

        # Upload Button
        self.upload_button = tk.Button(master, text="Upload Data (CSV or Excel)", command=self.upload_data)
        self.upload_button.pack(pady=5)

        # Dropdown for column selection
        self.column_frame = tk.Frame(master)
        self.column_frame.pack(pady=5)

        tk.Label(self.column_frame, text="Select PV Column:").grid(row=0, column=0)
        self.pv_selector = ttk.Combobox(self.column_frame, state='readonly')
        self.pv_selector.grid(row=0, column=1)

        tk.Label(self.column_frame, text="Select OUT Column:").grid(row=1, column=0)
        self.out_selector = ttk.Combobox(self.column_frame, state='readonly')
        self.out_selector.grid(row=1, column=1)

        tk.Label(self.column_frame, text="Select SP Column:").grid(row=2, column=0)
        self.sp_selector = ttk.Combobox(self.column_frame, state='readonly')
        self.sp_selector.grid(row=2, column=1)

        # Initial PID Parameters Input
        self.param_frame = tk.Frame(master)
        self.param_frame.pack(pady=5)

        tk.Label(self.param_frame, text="Initial Kp:").grid(row=0, column=0)
        self.initial_kp = tk.Entry(self.param_frame)
        self.initial_kp.grid(row=0, column=1)

        tk.Label(self.param_frame, text="Initial Ki:").grid(row=1, column=0)
        self.initial_ki = tk.Entry(self.param_frame)
        self.initial_ki.grid(row=1, column=1)

        tk.Label(self.param_frame, text="Initial Kd:").grid(row=2, column=0)
        self.initial_kd = tk.Entry(self.param_frame)
        self.initial_kd.grid(row=2, column=1)

        # Controller Type Selection (PI/PID)
        self.controller_type = tk.StringVar(value="PID")
        self.pi_radio = tk.Radiobutton(master, text="PI", variable=self.controller_type, value="PI")
        self.pid_radio = tk.Radiobutton(master, text="PID", variable=self.controller_type, value="PID")
        self.pi_radio.pack()
        self.pid_radio.pack()

        # Control Type (Flow, Pressure, Temperature)
        tk.Label(master, text="Select Control Type:").pack()
        self.control_selector = ttk.Combobox(master, values=["Flow", "Pressure", "Temperature"])
        self.control_selector.pack()
        self.control_selector.bind("<<ComboboxSelected>>", self.update_initial_constants)

        # Fit Button
        self.fit_button = tk.Button(master, text="Fit PID Parameters", command=self.fit_pid)
        self.fit_button.pack(pady=5)

        # Result Labels
        self.result_label = tk.Label(master, text="", font=('Arial', 12))
        self.result_label.pack()

        self.details = tk.Label(master, text="", fg='blue')
        self.details.pack()

    def upload_data(self):
        file_path = filedialog.askopenfilename(filetypes=[("CSV Files", "*.csv"), ("Excel Files", "*.xlsx *.xls")])
        if file_path:
            try:
                if file_path.endswith('.csv'):
                    self.data = pd.read_csv(file_path)
                elif file_path.endswith('.xlsx') or file_path.endswith('.xls'):
                    self.data = pd.read_excel(file_path)
                else:
                    raise ValueError("Unsupported file format")

                self.file_loaded = True
                columns = list(self.data.columns)
                self.pv_selector['values'] = columns
                self.out_selector['values'] = columns
                self.sp_selector['values'] = columns

                messagebox.showinfo("Success", "Data uploaded successfully! Please select PV, OUT, and SP columns.")
            except Exception as e:
                messagebox.showerror("Error", f"Failed to load file: {e}")

    def update_initial_constants(self, event):
        control_type = self.control_selector.get()
        if control_type == "Flow":
            initial_kp, initial_ki, initial_kd = 2, 0.5, 0.1
            details_text = "Flow Control: Initial constants → Kp=2, Ki=0.5, Kd=0.1"
        elif control_type == "Pressure":
            initial_kp, initial_ki, initial_kd = 10, 2, 0.5
            details_text = "Pressure Control: Initial constants → Kp=10, Ki=2, Kd=0.5"
        elif control_type == "Temperature":
            initial_kp, initial_ki, initial_kd = 1.5, 0.1, 0.05
            details_text = "Temperature Control: Initial constants → Kp=1.5, Ki=0.1, Kd=0.05"
        else:
            initial_kp, initial_ki, initial_kd = 0, 0, 0
            details_text = ""

        self.initial_kp.delete(0, tk.END)
        self.initial_kp.insert(0, initial_kp)
        self.initial_ki.delete(0, tk.END)
        self.initial_ki.insert(0, initial_ki)
        self.initial_kd.delete(0, tk.END)
        self.initial_kd.insert(0, initial_kd)

        self.details.config(text=details_text)

    def fit_pid(self):
        if not self.file_loaded:
            messagebox.showwarning("Warning", "Please upload data and select columns first.")
            return

        try:
            pv_col = self.pv_selector.get()
            out_col = self.out_selector.get()
            sp_col = self.sp_selector.get()
            time = self.data['time'].values
            PV = self.data[pv_col].values
            OUT = self.data[out_col].values
            SP = self.data[sp_col].values

            initial_kp = float(self.initial_kp.get())
            initial_ki = float(self.initial_ki.get())
            initial_kd = float(self.initial_kd.get())
            initial_guess = [initial_kp, initial_ki, initial_kd]

            if self.controller_type.get() == "PI":
                initial_guess = initial_guess[:2]
                result = opt.minimize(self.objective_pi, initial_guess, args=(time, SP, PV))
                Kp_opt, Ki_opt = result.x
                Kd_opt = 0
            else:
                result = opt.minimize(self.objective_pid, initial_guess, args=(time, SP, PV))
                Kp_opt, Ki_opt, Kd_opt = result.x

            self.result_label.config(text=f"Optimized PID Parameters → Kp={Kp_opt:.3f}, Ki={Ki_opt:.3f}, Kd={Kd_opt:.3f}")

            # Plot Initial vs Optimized Response
            plt.figure(figsize=(10, 5))

            plt.subplot(1, 2, 1)
            plt.plot(time, PV, label='Process Variable (PV)')
            plt.plot(time, SP, label='Setpoint (SP)')
            plt.plot(time, self.pid_control([initial_kp, initial_ki, initial_kd], time, SP), label='Initial PID Control (OUT)')
            plt.title("Initial PID Response")
            plt.legend()

            plt.subplot(1, 2, 2)
            plt.plot(time, PV, label='Process Variable (PV)')
            plt.plot(time, SP, label='Setpoint (SP)')
            plt.plot(time, self.pid_control([Kp_opt, Ki_opt, Kd_opt], time, SP), label='Optimized PID Control (OUT)')
            plt.title("Optimized PID Response")
            plt.legend()

            plt.tight_layout()
            plt.show()

        except Exception as e:
            messagebox.showerror("Error", f"An error occurred during fitting: {e}")

    def objective_pid(self, params, time, setpoint, measured):
        return np.sum((measured - self.pid_control(params, time, setpoint))**2)

    def objective_pi(self, params, time, setpoint, measured):
        params = np.append(params, 0)  # Append Kd=0 for PI
        return self.objective_pid(params, time, setpoint, measured)

    def pid_control(self, params, time, setpoint):
        Kp, Ki, Kd = params
        integral = 0
        prev_error = 0
        output = []
        for t, sp in zip(time, setpoint):
            error = sp - t
            integral += error
            derivative = error - prev_error
            output.append(Kp * error + Ki * integral + Kd * derivative)
            prev_error = error
        return np.array(output)

# Run the application
root = tk.Tk()
pid_gui = PIDGUI(root)
root.mainloop()
