
from flask import Flask, request, render_template
from scipy.optimize import linprog
import numpy as np
import math
import sys

# Initialize the Flask application
machine = Flask(__name__)

# Route for the home page that renders the initial form
@machine.route("/script2_home")
def script2_home():
    machine_lines = ['E6SW', 'MRSW', 'Impeller Cell']  # Define available machine lines
    return render_template("script2.html", machine_lines=machine_lines)  # Render the template with the machine lines

# Route to handle the optimization logic after form submission
@machine.route("/optimized_script2", methods=["POST"])
def optimized():
    machine_lines = ['E6SW', 'MRSW', 'Impeller Cell']  # Define the machine lines used in the optimization
    
    # Define various parameters for each machine line
    multiplicative_factor = {
        'E6SW': 0.22973,
        'MRSW': 0.30357,
        'Impeller Cell': 0.1518        
    }
    
    manpowerrequirements = {
        'E6SW': np.array([15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]),
        'MRSW': np.array([11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]),
        'Impeller Cell': np.array([5, 4, 3, 2, 1])
    }
    
    outputs = {
        'E6SW': np.array([370, 346, 322, 298, 274, 250, 226, 202, 178, 154, 130, 106, 82, 58, 34]),
        'MRSW': np.array([280, 255, 230, 205, 180, 155, 130, 105, 80, 55, 30]),
        'Impeller Cell': np.array([560, 448, 336, 224, 112]) 
    }
    
    oeeequivalence = {
        'E6SW': np.array([85.00, 80.00, 75.00, 70.00, 65.00, 60.00, 55.00, 50.00, 45.00, 40.00, 35.00, 30.00, 25.00, 20.00, 15.00]),
        'MRSW': np.array([85.00, 78.00, 71.00, 64.00, 57.00, 50.00, 43.00, 36.00, 29.00, 22.00, 15.00]),
        'Impeller Cell': np.array([85.00, 68.00, 51.00, 34.00, 15.00])
    }
    
    perpersoncontribution = {
        'E6SW': np.array([5.67, 5.71, 5.77, 5.83, 5.91, 6.00, 6.11, 6.25, 6.43, 6.67, 7.00, 7.50, 8.33, 10.00, 15.00]),
        'MRSW': np.array([7.73, 7.80, 7.89, 8.00, 8.14, 8.33, 8.60, 9.00, 9.67, 11.00, 15.00]),
        'Impeller Cell': np.array([17.00, 17.00, 17.00, 17.00, 15.00])
    }
    
    locking = {
        'E6SW': 3,
        'MRSW': 4,
        'Impeller Cell': 2
    }
    
    # Calculate the mean per person contribution for each machine line
    meanperperson = {machine_line: np.mean(perpersoncontribution[machine_line]) for machine_line in machine_lines}
    
    # Get available manpower from the form input
    available_manpower = int(request.form['total_manpower'])
    
    # Get the minimum production required for each machine line from the form input
    minimum_production_required = {machine_line: int(request.form[machine_line.replace(' ', '_')]) for machine_line in machine_lines}
    
    # Dictionary to store the manpower needed for each machine line
    manpower_needed = {}
    
    # Calculate the manpower needed for each machine line based on the production requirements
    for machine_line in machine_lines:
        index = np.argmin(outputs[machine_line] >= minimum_production_required[machine_line])
        if index is not None:
            numerator = minimum_production_required[machine_line] * multiplicative_factor[machine_line]
            denominator = perpersoncontribution[machine_line][index]
            manpower_needed[machine_line] = math.ceil(numerator / denominator)
        else:
            manpower_needed[machine_line] = 0
    
    # Calculate bounds for the manpower allocation based on locking and available manpower
    bounds = [
        (
            max(math.ceil(manpower_needed[machine_line]), locking[machine_line]),
            max(manpowerrequirements[machine_line])
        )
        for machine_line in machine_lines
    ]
    
    # Check if the available manpower matches the total required for maximum manpower; if so, return the max solution
    if available_manpower == sum(max(manpowerrequirements[machine_line]) for machine_line in machine_lines):
        optimal_solution = {machine_line: {'manpower': max(manpowerrequirements[machine_line]), 'oee': max(oeeequivalence[machine_line])} for machine_line in machine_lines}
        oee_max = 85
        return render_template('script2.html', success=True, optimal_solution=optimal_solution, maximized_oee=oee_max)
    
    # Calculate the objective function coefficients (negative for maximization)
    c_oee = -np.array([np.mean(np.array(outputs[machine_line]) * np.array(oeeequivalence[machine_line]) * np.array(perpersoncontribution[machine_line])) for machine_line in machine_lines])

    # Define upper bound constraints for the optimization problem
    A_ub = []
    b_ub = []
    for machine_line in machine_lines:
        A_ub_rows = np.zeros(len(machine_lines))
        A_ub_rows[machine_lines.index(machine_line)] = 1
        A_ub.append(A_ub_rows)
        b_ub.append(minimum_production_required[machine_line])
    
    # Define lower bound constraints for the optimization problem
    A_lb = []
    b_lb = []
    for machine_line in machine_lines:
        A_lb_rows = np.zeros(len(machine_lines))
        A_lb_rows[machine_lines.index(machine_line)] = -1
        A_lb.append(A_lb_rows)
        b_lb.append(-minimum_production_required[machine_line])
    A_lb = np.array(A_lb)
    b_lb = np.array(b_lb)
    
    # Combine the upper and lower bound constraints
    A_combined = np.vstack([A_ub, A_lb])
    b_combined = np.hstack([b_ub, b_lb])
    
    # Define equality constraint (total manpower must equal available manpower)
    A_eq = np.ones((1, len(machine_lines)))
    b_eq = np.array([available_manpower])
    
    # Solve the optimization problem using linear programming
    res = linprog(c_oee, A_ub=A_combined, b_ub=b_combined, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs', options={"tol": 1e-6})

    # If the primary optimization fails, attempt a secondary optimization
    if not res.success:
        c_balance = np.zeros(len(machine_lines))
        res_balance = linprog(c_balance, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs', options={"tol": 1e-6})

        if not res_balance.success:
            return render_template('script2.html', success=False, message='Optimization failed in both primary and secondary attempts', status=res_balance.message)
        else:
            res = res_balance

    # Calculate the optimal solution and production values
    optimal_solution1 = {}
    oee_sum = 0
    for i, machine_line in enumerate(machine_lines):
        index = np.argmax(manpowerrequirements[machine_line] == math.ceil(res.x[i]))
        oee = math.ceil(res.x[i] * perpersoncontribution[machine_line][index])
        if math.ceil(res.x[i]) != 0:
            production = outputs[machine_line][index]
        else:
            production = 0
        optimal_solution1[machine_line] = {
            'manpower': math.ceil(res.x[i]),
            'oee': f"{oee:.2f}",
            'production': production
        }
        oee_sum += oee

    # Calculate the maximized OEE
    max_oee = f"{oee_sum / len(machine_lines):.2f}"

    # Render the results in the template
    return render_template('script2.html', success=True, optimal_solution=optimal_solution1, maximized_oee=max_oee)

# Run the Flask application
if __name__ == '__main__':
    if len(sys.argv) > 1:
        port = int(sys.argv[1])  # If a port is specified, use it
    else:
        port = 5002  # Default port
    
    try:
        machine.run(host='127.0.0.1', port=port, debug=True)  # Start the Flask server
    except OSError as e:
        print(f"Error starting Script1: {e}")  # Handle errors that occur when starting the server
   
    
    
   
     