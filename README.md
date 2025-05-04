# PID Controller Toolkit

A complete GUI-based toolkit for **PID controller tuning, testing, and simulation**, designed for process control engineers, students, and researchers.

This toolkit allows you to:
- ✅ **Fit PID parameters** (Kp, Ki, Kd) from uploaded process data (CSV or Excel).
- ✅ **Simulate pressure control systems** under common scenarios like step changes, oscillations, nonlinear behaviors, and load disturbances.
- ✅ **Visualize and compare controller performance** (initial guess vs. optimized parameters).
- ✅ Generate synthetic process data for testing your controllers.

---

## 🚀 Quick Start Guide (For Forks, Clones, and Contributors)

### 🐍 **If You Have Python + Conda Installed:**

1. **Clone the repository:**

git clone https://github.com/yourusername/pid-controller-toolkit.git
cd pid-controller-toolkit

2. **Create the Environment:**

conda env create -f environment.yml
conda activate pid_control_env

3. **Run the PID Tuning GUI:**
python pid_gui.py

4. **(Optional) Run the Pressure Simulator:**
python simulator.py


🖥️ Option 2: No Python Installed? Use the EXE (Windows Only)

    ✅ Download the standalone .exe files from the Releases page.

    ✅ No Python setup required.

    ✅ Just double-click:

        pid_gui.exe → PID tuning and data fitting.

        simulator.exe → Pressure data generation and simulation.

🧪 Toolkit Features

    PID Parameter Fitting:

        Upload CSV or Excel data.

        Select PV, OUT, SP columns interactively.

        Choose between PI or PID control strategies.

        Enter initial estimates or use recommended defaults.

    Built-In Simulator for Testing:

        Stable process scenarios (constant, drifting, random SP).

        Step changes (single, multiple, ramp).

        Oscillatory systems (SP or PV oscillations).

        Nonlinear behavior (e.g., saturation effects).

        PV Step Disturbance (load disturbance rejection testing).

    Adjustable Simulation Parameters:

        Noise level (bar).

        Delay (seconds).

        Output saturation limits (min/max bar).

    Interactive Visualization:

        Side-by-side plots of process variable (PV), setpoint (SP), and controller output (OUT).

        Compare initial parameters vs. optimized fitted results.

💡 Why This Project Exists

This toolkit was built to make PID controller tuning and testing easier and more visual for engineers and students working on:

    Process control systems.

    Industrial automation.

    Pressure regulation systems.

    Learning PID behavior through simulation.


Initial Guess:

    You provide Kp, Ki, Kd via the GUI (or use defaults).

Controller Modeling:

    A PID formula is simulated:
    u(t)=Kpe(t)+Ki∫e(t)dt+Kdde(t)dt
    u(t)=Kp​e(t)+Ki​∫e(t)dt+Kd​dtde(t)​

    where e(t)=SP−PVe(t)=SP−PV

Loss Function:

    The optimizer compares actual vs. simulated controller output (OUT), minimizing mean squared error (MSE).

Optimization:

    scipy.optimize.minimize() is used (typically BFGS or L-BFGS-B).

Result:

    Updated Kp, Ki, Kd values and a plot comparing original vs. fitted response
	
	
	🧠 This Toolkit’s Method (Data-Driven Optimization-Based Fitting)

This approach uses a numerical optimizer (like scipy.optimize.minimize) to find the best Kp, Ki, Kd values by minimizing the error between actual and simulated control behavior.
🧪 How It Works:

    Simulate PID controller output using current Kp, Ki, Kd.

    Compare simulated output to real recorded data (e.g. OUT, PV).

    Minimize mean squared error (MSE) using an optimizer.

✅ Advantages:

    Works on real, noisy, or nonlinear data.

    No need to model or step-test the process.

    Fully automated and scriptable.

    Can be used post-hoc with historical data.

❌ Limitations:

    Slower than rule-based methods.

    Requires good initial guesses for best results.

    Needs a reasonable amount of quality data to converge.

📊 Summary Comparison
Feature	Classic Tuning (ZN, CC, etc.)	This Toolkit (Optimization-Based)
Model or step test required?	✅ Yes	❌ No
Real data supported?	⚠️ Partially	✅ Fully
Handles nonlinear processes?	❌ Poorly	✅ Yes
Noise-tolerant?	❌ No	✅ Yes
Tuning speed	✅ Fast	⚠️ Slower
Accuracy	⚠️ Approximate	✅ Higher with good data
Automation-ready	❌ Manual	✅ Scriptable + reproducible

✅ This approach makes the toolkit ideal for modern process control systems, historical log analysis, student experiments, and noisy environments where traditional methods struggle.

📜 License

This project is licensed under the MIT License.

See the LICENSE file for details.
🤝 Contributing

Pull requests and contributions are welcome!


🧑‍💻 Maintainer

    Created and maintained by pkbythebay29
    Connect on [https://www.linkedin.com/in/pranavkannan/]