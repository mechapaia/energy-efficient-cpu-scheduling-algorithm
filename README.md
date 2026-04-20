# ⚡ MLFQ Energy-Aware Scheduler

A professional, real-time web-based simulation of a **Multi-Level Feedback Queue (MLFQ)** CPU scheduler integrated with **Dynamic Voltage and Frequency Scaling (DVFS)** for power optimization.

![Project Preview](https://img.shields.io/badge/OS--Project-Advanced-blue?style=for-the-badge)
![Python](https://img.shields.io/badge/python-3.9+-yellow?style=for-the-badge&logo=python)
![Flask](https://img.shields.io/badge/flask-%23000.svg?style=for-the-badge&logo=flask&logoColor=white)

## 🌟 Overview

This project demonstrates the intersection of traditional OS scheduling and modern hardware energy management. It provides a visual dashboard to monitor how scheduling decisions (like task demotion and priority boosting) impact CPU energy consumption across different priority tiers.

### Key Features
*   **Dynamic MLFQ Simulation:** Configure up to 5 priority queues with custom time quanta and boost intervals.
*   **DVFS Modeling:** Real-time calculation of power draw based on CPU Voltage (V) and Frequency (f).
*   **Live System Monitor:** A "Live Mode" that pulls real processes from your host OS and estimates their wattage usage based on TDP.
*   **AI Assistant:** An integrated Gemini-powered chatbot to answer technical questions about the simulation.
*   **Premium UI:** A modern, glassmorphism-inspired dashboard built with Vanilla CSS and JS.

## 🧬 Technical Model

### 1. Energy Formula
Power consumption ($P$) is tracked at every simulation tick using the standard dynamic power equation:
$$P = C \cdot V^2 \cdot f$$
Where:
*   **C**: Capacitance (system constant)
*   **V**: CPU Voltage (mapped per queue level)
*   **f**: Frequency (mapped per queue level)

| Queue | Mode | Voltage (V) | Freq (GHz) | Power (W) |
| :--- | :--- | :--- | :--- | :--- |
| **Q0** | High Perf | 1.2V | 2.0 GHz | ~24.0W |
| **Q1** | Balanced | 1.0V | 1.5 GHz | ~13.5W |
| **Q2** | Eco Save | 0.8V | 1.0 GHz | ~6.4W |
| **Q3** | Ultra Eco | 0.7V | 0.8 GHz | ~3.9W |
| **Q4** | Min Power | 0.6V | 0.5 GHz | ~1.8W |

### 2. MLFQ Rules
1.  **High Priority First**: Tasks in Q0 always preempt tasks in lower queues.
2.  **Time Quanta**: Tasks that exceed their time quantum are demoted (e.g., Q0 $\rightarrow$ Q1).
3.  **Anti-Starvation**: After a "Boost Interval," all tasks are moved back to Q0 to ensure low-priority tasks eventually execute.

## 🛠️ Installation & Setup

1.  **Clone the Repository**
    ```bash
    git clone https://github.com/mechapaia/energy-efficient-cpu-scheduling-algorithm.git
    cd energy-efficient-cpu-scheduling-algorithm
    ```

2.  **Create a Virtual Environment**
    ```bash
    python -m venv myenv
    source myenv/bin/activate  # Windows: myenv\Scripts\activate
    ```

3.  **Install Dependencies**
    ```bash
    pip install flask psutil google-generativeai
    ```

4.  **Configure AI Assistant** (Optional)
    *   Get an API key from [Google AI Studio](https://aistudio.google.com/).
    *   Set it in `scheduler/ai.py` or as an environment variable:
    ```bash
    export GEMINI_API_KEY='your-key-here'
    ```

5.  **Run the Application**
    ```bash
    python app.py
    ```
    Visit `http://localhost:5000` in your browser.

## 🖥️ Project Structure
```text
├── app.py              # Flask server and API routes
├── scheduler/
│   ├── engine.py       # Core MLFQ simulation step-logic
│   ├── models.py       # Task and Config data classes
│   ├── energy.py       # DVFS constants and power formulas
│   └── ai.py           # Gemini AI integration
├── static/
│   ├── css/style.css   # Dashboard styles (Glassmorphism)
│   └── js/main.js      # Simulation & Live Monitor frontend handles
└── templates/
    └── index.html      # Main dashboard structure
```

## 📜 License
Independent project developed for educational purposes in Operating Systems studies.
