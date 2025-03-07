
from flask import Flask, request, render_template
from scipy.optimize import linprog
import numpy as np 
import math 

# Initialize the Flask application
EU = Flask(__name__)

# Route for the home page that renders the initial form
@EU.route("/start_eu")
def index():
    # Define available assembly lines
    assembly_lines = ['LD Assy', 'T&T Assy', 'MR Turbo', 'ETV']
    # Render the template with the assembly lines
    return render_template("eu.html", assembly_lines=assembly_lines)

# Route to handle the optimization logic after form submission
@EU.route("/optimize_eu", methods=["POST"])
def optimizer():
    # Define the assembly lines used in the optimization
    assembly_lines = ['LD Assy', 'T&T Assy', 'MR Turbo', 'ETV']
    
    # Define various parameters for each assembly line
    multiplicative_factor = {
        "LD Assy": 0.44,
        "T&T Assy": 1.27,
        "MR Turbo": 0.97,
        "ETV": 0.3
    }

    manpowerrequirements = {
        "LD Assy": np.array([11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]),
        "T&T Assy": np.array([17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]),
        "MR Turbo": np.array([19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]),
        "ETV": np.array([8, 7, 6, 5, 4, 3, 2, 1])
    }

    outputs = {
        "LD Assy": np.array([270, 260, 240, 230, 215, 205, 180, 150, 120, 40, 30]),
        "T&T Assy": np.array([320, 310, 290, 270, 250, 230, 210, 200, 180, 160, 150, 130, 115, 80, 60, 30, 20]),
        "MR Turbo": np.array([270, 265, 260, 250, 230, 210, 190, 160, 140, 110, 90, 70, 60, 50, 45, 40, 35, 30, 20]),
        "ETV": np.array([320, 295, 245, 200, 160, 120, 70, 30])
    }

    eu = {
        "LD Assy": np.array([118.8, 114.4, 105.6, 101.2, 94.6, 90.2, 79.2, 66, 52.8, 17.6, 13.2]),
        "T&T Assy": np.array([406.4, 393.7, 368.3, 342.9, 317.5, 292.1, 266.7, 254, 228.6, 203.2, 190.5, 165.1, 146.05, 101.6, 76.2, 38.1, 25.4]),
        "MR Turbo": np.array([261.9, 257.05, 252.2, 242.5, 223.1, 203.7, 184.3, 155.2, 135.8, 106.7, 87.3, 67.9, 58.2, 48.5, 43.65, 38.8, 33.95, 29.1, 19.4]),
        "ETV": np.array([96, 88.5, 73.5, 60, 48, 36, 21, 9])
    }

    perpersoncontribution = {
        "LD Assy": np.array([10.80, 11.44, 11.73, 12.65, 13.51, 15.03, 15.84, 16.50, 17.60, 8.80, 13.20]),
        "T&T Assy": np.array([23.91, 24.61, 24.55, 24.49, 24.42, 24.34, 24.25, 25.40, 25.40, 25.40, 27.21, 27.52, 29.21, 25.40, 25.40, 19.05, 25.40]),
        "MR Turbo": np.array([13.78, 14.28, 14.84, 15.16, 14.87, 14.55, 14.18, 12.93, 12.35, 10.67, 9.70, 8.49, 8.31, 8.08, 8.73, 9.70, 11.32, 14.55, 19.40]),
        "ETV": np.array([12.00, 12.64, 12.25, 12.00, 12.00, 12.00, 10.50, 9.00])
    }

    locking = {
        "LD Assy": 4,
        "T&T Assy": 5,
        "MR Turbo": 3,
        "ETV": 3
    }
    
    # Calculate the mean per person contribution for each assembly line
    mean_perperson = {assembly_line: np.mean(perpersoncontribution[assembly_line]) for assembly_line in assembly_lines}

    # Get available manpower from the form input
    available_manpower = int(request.form['total_manpower'].replace(' ', '_'))

    # Get the minimum production required for each assembly line from the form input
    minimum_output = {assembly_line: int(request.form[assembly_line.replace(' ', '_')]) for assembly_line in assembly_lines}

    # Dictionary to store the manpower needed for each assembly line
    manpower_needed = {}
    
    # Calculate the manpower needed for each assembly line based on the production requirements
    for assembly_line in assembly_lines:
        index = np.argmin(outputs[assembly_line] >= minimum_output[assembly_line])
        if index is not None:
            numerator = minimum_output[assembly_line] * multiplicative_factor[assembly_line]
            denominator = perpersoncontribution[assembly_line][index]
            manpower_needed[assembly_line] = math.ceil(numerator / denominator)
        else:
            manpower_needed[assembly_line] = 0
    
    # Check if the available manpower matches the total required for maximum manpower; if so, return the max solution
    if available_manpower == sum(max(manpowerrequirements[assembly_line]) for assembly_line in assembly_lines):
        optimal_solution = {assembly_line: {'manpower': max(manpowerrequirements[assembly_line]), 'Eu': max(eu[assembly_line]), 'production': max(outputs[assembly_line])} for assembly_line in assembly_lines}
        Eu_max = 220.775
        return render_template('eu.html', success=True, optimal_solution=optimal_solution, maximized_Eu=Eu_max)

    # Calculate bounds for the manpower allocation based on locking and available manpower
    bounds = [
        (
            max(math.ceil(manpower_needed[assembly_line]), locking[assembly_line]),
            max(manpowerrequirements[assembly_line])
        )
        for assembly_line in assembly_lines
    ]

    # Calculate the objective function coefficients (negative for maximization)
    c_oee = -np.array([np.mean(outputs[assembly_line] * eu[assembly_line] * perpersoncontribution[assembly_line]) for assembly_line in assembly_lines])

    # Define upper bound constraints for the optimization problem
    A_ub = []
    b_ub = []

    for assembly_line in assembly_lines:
        A_ub_row = np.zeros(len(assembly_lines))
        A_ub_row[assembly_lines.index(assembly_line)] = 1
        A_ub.append(A_ub_row)
        b_ub.append(minimum_output[assembly_line])

    # Define lower bound constraints for the optimization problem
    A_lb = []
    b_lb = []

    for assembly_line in assembly_lines:
        A_lb_row = np.zeros(len(assembly_lines))
        A_lb_row[assembly_lines.index(assembly_line)] = -1 
        A_lb.append(A_lb_row)
        b_lb.append(-minimum_output[assembly_line])

    A_lb = np.array(A_lb)
    b_lb = np.array(b_lb)

    # Combine the upper and lower bound constraints
    A_combined = np.vstack([A_ub, A_lb])
    b_combined = np.hstack([b_ub, b_lb])

    # Define equality constraint (total manpower must equal available manpower)
    A_eq = np.ones((1, len(assembly_lines)))
    b_eq = np.array([available_manpower])

    # Solve the optimization problem using linear programming
    res = linprog(c_oee, A_ub=A_combined, b_ub=b_combined, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs', options={"tol": 1e-6})

    # If the primary optimization fails, attempt a secondary balancing optimization
    if not res.success:
        c_balance = np.zeros(len(assembly_lines))
        res_balance = linprog(c_balance, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs', options={"tol": 1e-6})

        if not res_balance.success:
            return render_template('eu.html', success=False, message='Optimization failed in both primary and secondary attempts', status=res_balance.message)
        else:
            res = res_balance

    # Extract and format the optimal solution
    optimal_solution1 = {}
    Eu_sum = 0
    for i, assembly_line in enumerate(assembly_lines):
        index = np.argmax(manpowerrequirements[assembly_line] == math.ceil(res.x[i]))
        Eu = math.ceil(res.x[i] * perpersoncontribution[assembly_line][index])
        if math.ceil(res.x[i]) != 0:
            production = outputs[assembly_line][index]
        else:
            production = 0
        optimal_solution1[assembly_line] = {
            'manpower': math.ceil(res.x[i]),
            'Eu': f"{Eu:.2f}",
            'production': production
        }
        Eu_sum += Eu

    # Calculate the maximized Eu
    Eu_max = f"{Eu_sum / len(assembly_lines):.2f}"

    # Render the result page with the optimal solution and maximized Eu
    return render_template('eu.html', success=True, optimal_solution=optimal_solution1, maximized_Eu=Eu_max)

# Run the Flask application on port 4001 in debug mode
if __name__ == '__main__':
    EU.run(debug=True, port=4001)



