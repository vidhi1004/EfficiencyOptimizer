# Efficiency Optimizer 🚀

A web-based tool for optimizing manufacturing processes using linear programming. This application helps in resource allocation to maximize metrics like Overall Equipment Effectiveness (OEE) and EU.

## ✨ Features

- **OEE Optimization:** Allocate manpower to different assembly lines to maximize OEE based on customer orders.
- **EU Optimization:** Determine the optimal manpower distribution to maximize EU while meeting minimum production requirements.
- **Web-Based Interface:** Easy-to-use interface built with Flask.

## 🛠️ Installation

1.  **Clone the repository:**
    ```bash
    git clone [https://github.com/vidhi1004/EfficiencyOptimizer.git](https://github.com/vidhi1004/EfficiencyOptimizer.git)
    cd EfficiencyOptimizer
    ```

2.  **Create a virtual environment and activate it:**
    ```bash
    python -m venv venv
    # On Windows
    venv\Scripts\activate
    # On macOS/Linux
    source venv/bin/activate
    ```

3.  **Install the dependencies:**
    ```bash
    pip install -r requirements.txt
    ```

## ▶️ Usage

1.  **Run the Flask application:**
    ```bash
    python app.py
    ```

2.  **Open your web browser and navigate to `http://127.0.0.1:8001`.**

3.  **Choose either the OEE or EU optimizer, fill in the required values, and click "Calculate" to see the results.**

## 📜 License

This project is licensed under the MIT License. See the [LICENSE](LICENSE) file for details.
