import numpy as np
import pandas as pd

# Generate synthetic data
np.random.seed(0)  # For reproducibility
time = np.linspace(0, 10, 100)
setpoint = np.ones(100) * 50  # Setpoint (SP) is constant at 50 units

# Simulate a simple pressure regulator
Kp, Ki, Kd = 1.5, 0.1, 0.05
integral = 0
prev_error = 0
pv = []  # Process Variable (PV)
out = []  # Output (OUT)

for t in range(len(time)):
    if t == 0:
        error = setpoint[t] - 0
    else:
        error = setpoint[t] - pv[-1]
    integral += error
    derivative = error - prev_error
    output = Kp * error + Ki * integral + Kd * derivative
    measured = 0.8 * setpoint[t] + 0.2 * output + np.random.normal(0, 1)  # Adding some noise
    pv.append(measured)
    out.append(output)
    prev_error = error

# Create DataFrame
data = pd.DataFrame({
    'time': time,
    'PV': pv,
    'OUT': out,
    'SP': setpoint
})

# Save to CSV (optional)
data.to_csv('synthetic_pressure_regulator_data.csv', index=False)

# Display first few rows of the data
print(data.head())

# Plotting the generated data for visualization
import matplotlib.pyplot as plt

plt.plot(time, pv, label='Process Variable (PV)')
plt.plot(time, setpoint, label='Setpoint (SP)')
plt.plot(time, out, label='Output (OUT)')
plt.xlabel('Time')
plt.ylabel('Pressure')
plt.legend()
plt.title('Synthetic Pressure Regulator Data')
plt.show()
