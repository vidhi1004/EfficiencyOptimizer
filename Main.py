from flask import Flask, request, render_template, redirect, url_for
from eu import *  # Import all functions and variables from eu module
from Index import *  # Import all functions and variables from Index module

# Initialize the Flask application
main = Flask(__name__)

# Route for the home page that renders the main page
@main.route('/')
def home():
    return render_template('main.html')  # Render the template for the home page

# Route to start the application (calls start_home function from Index module)
@main.route('/start_app')
def start_app():
    return start_home()  # Call the start_home function from Index module

# Route to start the EU section (calls index function from eu module)
@main.route('/start_eu')
def start_eu():
    return index()  # Call the index function from eu module

# Route to handle optimization for the EU section after form submission
@main.route('/optimize_eu', methods=['POST'])
def optimize_eu():
    return optimizer()  # Call the optimizer function from eu module

# Route to start the first script (Script1) (calls script1_home function from Index module)
@main.route('/start_script1')
def start_script1():
    return script1_home()  # Call the script1_home function from Index module

# Route to start the second script (Script2) (calls script2_home function from Index module)
@main.route('/start_script2')
def start_script2():
    return script2_home()  # Call the script2_home function from Index module

# Route to handle optimization for the first script (Script1) after form submission
@main.route('/optimize_script1', methods=["POST"])
def optimize_script1():
    return optimize()  # Call the optimize function from Index module

# Route to handle optimization for the second script (Script2) after form submission
@main.route('/optimized_script2', methods=["POST"])
def optimize_script2():
    return optimized()  # Call the optimized function from Index module

# Run the Flask application on port 8001 in debug mode
if __name__ == '__main__':
    main.run(port=8001, debug=True)

    