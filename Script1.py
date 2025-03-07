      
from flask import Flask, render_template, request
from scipy.optimize import linprog
import numpy as np
import math
import sys

OEE1 = Flask(__name__)

@OEE1.route("/script1_home")
def script1_home():
    """Render the Script1 home page with assembly types."""
    assembly_types = ['LD Assy', 'T&T Assy', 'Supercell', 'MR Turbo', 'ETV']
    return render_template("script1.html", assembly_types=assembly_types)


@OEE1.route("/optimize_script1", methods=["POST"])
def optimize():
    #Handle the optimization request for Script1.
    assembly_types = ['LD Assy', 'T&T Assy', 'Supercell', 'MR Turbo', 'ETV']

    # Define multiplicative factors for each assembly type
    multiplicative_factor = {
        "LD Assy": 0.314814815,
        "T&T Assy": 0.265625,
        "Supercell": 0.2125,
        "MR Turbo": 0.315,
        "ETV": 0.265625
    }

    # Manpower requirements for each assembly type
    manpowerrequirements = {
        "LD Assy": np.array([11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]),
        "T&T Assy": np.array([17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]),
        "Supercell": np.array([12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]),
        "MR Turbo": np.array([19, 18, 17, 16, 15, 14, 13, 12, 11, 10, 9, 8, 7, 6, 5, 4, 3, 2, 1]),
        "ETV": np.array([8, 7, 6, 5, 4, 3, 2, 1])
    }

    # Output values for each assembly type
    outputs = {
        "LD Assy": np.array([270, 260, 240, 230, 215, 205, 180, 150, 120, 40, 30]),
        "T&T Assy": np.array([320, 310, 290, 270, 250, 230, 210, 200, 180, 160, 150, 130, 115, 80, 60, 30, 20]),
        "Supercell": np.array([400, 360, 340, 315, 290, 260, 240, 200, 160, 110, 90, 45]),
        "MR Turbo": np.array([270, 265, 260, 250, 230, 210, 190, 160, 140, 110, 90, 70, 60, 50, 45, 40, 35, 30, 20]),
        "ETV": np.array([320, 295, 245, 200, 160, 120, 70, 30])
    }

    # OEE (Overall Equipment Efficiency) equivalence values
    OEEequivalence = {
        "LD Assy": np.array([85.00, 81.85, 75.56, 72.41, 67.69, 64.54, 56.67, 47.22, 37.78, 12.59, 9.44]),
        "T&T Assy": np.array([85.00, 82.34, 77.03, 71.72, 66.41, 61.09, 55.78, 53.13, 47.81, 42.50, 39.84, 34.53, 30.55, 21.25, 15.94, 7.97, 5.31]),
        "Supercell": np.array([85.00, 76.50, 72.25, 66.94, 61.63, 55.25, 51.00, 42.50, 34.00, 23.38, 19.13, 9.56]),
        "MR Turbo": np.array([85.00, 83.43, 81.85, 78.70, 72.41, 66.11, 59.81, 50.37, 44.07, 34.63, 28.33, 22.04, 18.89, 15.74, 14.17, 12.59, 11.02, 9.44, 6.30]),
        "ETV": np.array([85.00, 78.36, 65.08, 53.13, 42.50, 31.88, 18.59, 7.97])
    }

    # Per person contribution for each assembly type
    perpersoncontribution = {
        "LD Assy": np.array([7.73, 8.19, 8.40, 9.05, 9.67, 10.76, 11.33, 11.81, 12.59, 6.30, 9.44]),
        "T&T Assy": np.array([5.00, 5.15, 5.10, 5.12, 5.11, 5.09, 5.07, 5.31, 5.31, 5.31, 5.69, 5.76, 6.11, 5.31, 5.31, 3.98, 5.31]),
        "Supercell": np.array([7.08, 6.95, 7.23, 7.44, 7.70, 7.89, 8.50, 8.50, 8.50, 7.79, 9.56, 9.56]),
        "MR Turbo": np.array([4.47, 4.63, 4.81, 4.92, 4.83, 4.72, 4.60, 4.20, 4.01, 3.46, 3.15, 2.75, 2.70, 2.62, 2.83, 3.15, 3.60, 4.72, 6.30]),
        "ETV": np.array([10.63, 11.19, 10.85, 10.63, 10.63, 10.63, 9.30, 7.97])
    }

    # Locking values for each assembly type
    locking = {
        "LD Assy": 3,
        "T&T Assy": 4,
        "Supercell": 5,
        "MR Turbo": 6,
        "ETV": 3
    }

    # Calculate mean per person contribution for each assembly type
    mean_perperson = {assembly_type: np.mean(perpersoncontribution[assembly_type]) for assembly_type in assembly_types}

    # Get the available manpower from the form input
    available_manpower = int(request.form['total_manpower'].replace(' ', '_'))

    # Get the minimum customer order for each assembly type from the form input
    minimum_customer_order = {assembly_type: int(request.form[assembly_type.replace(' ', '_')]) for assembly_type in assembly_types}
    
    # Calculate the manpower needed for each assembly type
    manpower_needed = {}
    for assembly_type in assembly_types:
        index = np.argmin(outputs[assembly_type] >= minimum_customer_order[assembly_type])
        if index is not None:
            numerator = minimum_customer_order[assembly_type] * multiplicative_factor[assembly_type]
            denominator = perpersoncontribution[assembly_type][index]
            manpower_needed[assembly_type] = math.ceil(numerator / denominator)
        else:
            manpower_needed[assembly_type] = 0

        # Debug print statements to track computation
        print(f"Assembly type: {assembly_type}, Index: {index}, Numerator: {numerator}, Denominator: {denominator}, Manpower needed: {manpower_needed[assembly_type]}")

    # Print the calculated manpower needed for debugging
    print("Manpower needed:", manpower_needed)

    # Print debug information
    print("Is 'T&T Assy' in assembly_types?", 'T&T Assy' in assembly_types)
    print("Is 'T&T Assy' in manpowerrequirements?", 'T&T Assy' in manpowerrequirements)
    print("Keys in manpower_needed:", manpower_needed.keys())
    print("manpower_needed['T&T Assy']:", manpower_needed.get('T&T Assy'))

    # Set bounds for optimization based on manpower needed and locking values
    bounds = [
        (
            max(math.ceil(manpower_needed[assembly_type]), locking[assembly_type]),
            max(manpowerrequirements[assembly_type])
        )
        for assembly_type in assembly_types
    ]

    # Check if available manpower matches the sum of maximum requirements
    if available_manpower == sum(max(manpowerrequirements[assembly_type]) for assembly_type in assembly_types):
        optimal_solution = {assembly_type: {'manpower': max(manpowerrequirements[assembly_type]), 'oee': max(OEEequivalence[assembly_type]), 'production': max(outputs[assembly_type])} for assembly_type in assembly_types}
        max_oee = 85
        return render_template('script1.html', success=True, optimal_solution=optimal_solution, maximized_oee=max_oee)

    # Define the bounds for optimization
    bounds = [(manpower_needed[assembly_type], max(manpowerrequirements[assembly_type])) for assembly_type in assembly_types]

    # Define the objective function for optimization
    c_oee = -np.array([np.mean(outputs[assembly_type] * OEEequivalence[assembly_type] * perpersoncontribution[assembly_type]) for assembly_type in assembly_types])

    # Define inequality constraints for customer orders
    A_ub = []
    b_ub = []
    for assembly_type in assembly_types:
        A_ub_row = np.zeros(len(assembly_types))
        A_ub_row[assembly_types.index(assembly_type)] = 1
        A_ub.append(A_ub_row)
        b_ub.append(minimum_customer_order[assembly_type])

    # Define lower bounds for customer orders
    A_lb = []
    b_lb = []
    for assembly_type in assembly_types:
        A_lb_row = np.zeros(len(assembly_types))
        A_lb_row[assembly_types.index(assembly_type)] = -1
        A_lb.append(A_lb_row)
        b_lb.append(-minimum_customer_order[assembly_type])

    A_lb = np.array(A_lb)
    b_lb = np.array(b_lb)

    # Combine constraints
    A_combined = np.vstack([A_ub, A_lb])
    b_combined = np.hstack([b_ub, b_lb])

    # Define equality constraint for total manpower
    A_eq = np.ones((1, len(assembly_types)))
    b_eq = np.array([available_manpower])

    # Perform linear programming optimization
    res = linprog(c_oee, A_ub=A_combined, b_ub=b_combined, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs', options={"tol": 1e-6})

    if not res.success:
        # Attempt a secondary optimization if primary fails
        c_balance = np.zeros(len(assembly_types))
        res_balance = linprog(c_balance, A_eq=A_eq, b_eq=b_eq, bounds=bounds, method='highs', options={"tol": 1e-6})

        if not res_balance.success:
            return render_template('script1.html', success=False, message='Optimization failed in both primary and secondary attempts', status=res_balance.message)
        else:
            res = res_balance

    # Process the optimization results
    optimal_solution1 = {}
    oee_sum = 0
    for i, assembly_type in enumerate(assembly_types):
        if assembly_type == "ETV":
            index1 = np.argmax(manpowerrequirements[assembly_type] <= math.floor(res.x[i]))
        else:
            index1 = np.argmax(manpowerrequirements[assembly_type] == math.ceil(res.x[i]))
        if assembly_type == "ETV":
            manpower_ceiled = math.floor(res.x[i])
        else:
            manpower_ceiled = math.ceil(res.x[i])
        if assembly_type == "ETV":
            oee = math.floor(res.x[i]) * perpersoncontribution[assembly_type][index1]
        else:
            oee = math.ceil(res.x[i]) * perpersoncontribution[assembly_type][index1]
        if manpower_ceiled != 0:
            production = outputs[assembly_type][index1]
        else:
            production = 0

        optimal_solution1[assembly_type] = {
            'manpower': manpower_ceiled,
            'oee': f"{oee:.2f}",
            'production': production
        }

        oee_sum += oee

        max_oee = f"{oee_sum / len(assembly_types):.2f}"

    return render_template('script1.html', success=True, optimal_solution=optimal_solution1, maximized_oee=max_oee)

if __name__ == '__main__':
    if len(sys.argv) > 1:
        port = int(sys.argv[1])
    else:
        port = 5001

    try:
        OEE1.run(host='127.0.0.1', port=port, debug=True)
    except OSError as e:
        print(f"Error starting Script1: {e}")
