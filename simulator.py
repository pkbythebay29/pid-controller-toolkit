import numpy as np
import pandas as pd
import tkinter as tk
from tkinter import filedialog, simpledialog, messagebox, ttk
import matplotlib.pyplot as plt

# === Generation Functions ===
def generate_stable_pressure(time, sp_type="Constant", noise_level=0.5):
    if sp_type == "Constant":
        sp = np.ones_like(time) * 50
    elif sp_type == "Drifting":
        sp = 50 + 2 * np.sin(0.1 * time)  # small slow drift
    elif sp_type == "Random Fluctuations":
        sp = 50 + np.random.normal(0, 1, len(time))
    pv = sp + np.random.normal(0, noise_level, len(time))
    return pv, sp

def generate_step_pressure(time, step_type="Single", delay=0, noise_level=0.5):
    sp = np.ones_like(time) * 40  # Initial SP
    if step_type == "Single":
        sp[np.where(time >= 5)] = 60
    elif step_type == "Multiple":
        sp[np.where(time >= 3)] = 50
        sp[np.where(time >= 6)] = 65
        sp[np.where(time >= 8)] = 55
    elif step_type == "Ramp":
        sp = np.linspace(40, 60, len(time))
    
    pv = np.zeros_like(time)
    for i, t in enumerate(time):
        if t < delay:
            pv[i] = sp[0] + np.random.normal(0, noise_level)
        else:
            pv[i] = sp[i] + np.random.normal(0, noise_level)
    return pv, sp

def generate_oscillatory_pressure(time, sp_oscillates=False, delay=0, noise_level=0.5):
    sp = np.ones_like(time) * 50
    if sp_oscillates:
        sp += 5 * np.sin(2 * np.pi * 0.3 * time)
    pv = np.zeros_like(time)
    for i, t in enumerate(time):
        if t < delay:
            pv[i] = sp[0] + np.random.normal(0, noise_level)
        else:
            pv[i] = sp[i] + 8 * np.sin(2 * np.pi * 0.5 * time[i]) + np.random.normal(0, noise_level)
    return pv, sp

def generate_nonlinear_pressure(time, delay=0, noise_level=0.5):
    sp = np.ones_like(time) * 50
    pv = []
    for i, t in enumerate(time):
        response = sp[i] + 10 * np.tanh((t - 5) / 2)
        if t < delay:
            response = sp[0]
        response += np.random.normal(0, noise_level)
        pv.append(response)
    return np.array(pv), sp

# === Apply Saturation ===
def apply_saturation(signal, min_out=None, max_out=None):
    if min_out is not None:
        signal = np.maximum(signal, min_out)
    if max_out is not None:
        signal = np.minimum(signal, max_out)
    return signal

# === Simulator Main Logic ===
def simulator():
    # Tkinter Setup
    root = tk.Tk()
    root.withdraw()

    behaviors = ["Stable", "Step Change", "Oscillatory", "Nonlinear"]
    behavior = simpledialog.askstring("Behavior Type", f"Choose behavior: {', '.join(behaviors)}")
    if behavior is None:
        messagebox.showinfo("Cancelled", "Simulation cancelled.")
        return

    time = np.linspace(0, 10, 100)
    noise_level = simpledialog.askfloat("Noise Level", "Enter noise level (e.g., 0.5):", initialvalue=0.5)
    delay = simpledialog.askfloat("Delay (seconds)", "Enter delay before PV responds (0 for no delay):", initialvalue=0)

    # Saturation setup
    saturation_choice = messagebox.askyesno("Output Saturation", "Do you want to apply output saturation?")
    min_out, max_out = None, None
    if saturation_choice:
        min_out = simpledialog.askfloat("Min Output", "Minimum Output Value (e.g., 30):")
        max_out = simpledialog.askfloat("Max Output", "Maximum Output Value (e.g., 70):")

    # === Handle Behavior Selection ===
    if behavior == "Stable":
        stable_types = ["Constant", "Drifting", "Random Fluctuations"]
        sp_type = simpledialog.askstring("Stable Type", f"Select stable type: {', '.join(stable_types)}")
        pv, sp = generate_stable_pressure(time, sp_type=sp_type, noise_level=noise_level)
    elif behavior == "Step Change":
        step_types = ["Single", "Multiple", "Ramp"]
        step_type = simpledialog.askstring("Step Type", f"Select step type: {', '.join(step_types)}")
        pv, sp = generate_step_pressure(time, step_type=step_type, delay=delay, noise_level=noise_level)
    elif behavior == "Oscillatory":
        sp_osc = messagebox.askyesno("Oscillating SP?", "Should the setpoint itself oscillate?")
        pv, sp = generate_oscillatory_pressure(time, sp_oscillates=sp_osc, delay=delay, noise_level=noise_level)
    elif behavior == "Nonlinear":
        pv, sp = generate_nonlinear_pressure(time, delay=delay, noise_level=noise_level)
    else:
        messagebox.showerror("Error", "Invalid behavior type selected.")
        return

    # Apply saturation if enabled
    pv = apply_saturation(pv, min_out, max_out)

    # Fake OUT signal
    out = sp - pv + np.random.normal(0, 0.2, len(time))
    out = apply_saturation(out, min_out, max_out)

    # Save to CSV
    output_path = filedialog.asksaveasfilename(
        defaultextension=".csv",
        filetypes=[("CSV files", "*.csv")],
        title="Save generated data as..."
    )

    if output_path:
        df = pd.DataFrame({'time': time, 'PV': pv, 'OUT': out, 'SP': sp})
        df.to_csv(output_path, index=False)
        messagebox.showinfo("Success", f"Data saved to: {output_path}")

        # Plot results
        plt.figure(figsize=(8, 5))
        plt.plot(time, pv, label="Process Variable (PV)")
        plt.plot(time, sp, label="Setpoint (SP)", linestyle="--")
        plt.plot(time, out, label="Output (OUT)")
        plt.xlabel("Time (s)")
        plt.ylabel("Pressure")
        plt.title(f"Simulated Pressure Data ({behavior})")
        plt.legend()
        plt.tight_layout()
        plt.show()
    else:
        messagebox.showinfo("Cancelled", "Save operation cancelled.")

if __name__ == "__main__":
    simulator()
