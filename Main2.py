from flask import Flask, render_template
from Script1 import *  # Import all functions and variables from Script1
from Script2 import *  # Import all functions and variables from Script2

# Initialize the Flask application
app = Flask(__name__)

# Route for the home page that renders the initial start page
@app.route('/start_app')
def start_home():
    return render_template('start_app.html')  # Render the template for the start page

# Route to start the first script (Script1)
@app.route('/start_script1')
def start_script1():
    return script1_home()  # Call the script1_home function from Script1

# Route to start the second script (Script2)
@app.route('/start_script2')
def start_script2():
    return script2_home()  # Call the script2_home function from Script2

# Route to handle the optimization logic for Script1 after form submission
@app.route('/optimize_script1', methods=["POST"])
def optimize_script1():
    return optimize()  # Call the optimize function from Script1

# Route to handle the optimization logic for Script2 after form submission
@app.route('/optimized_script2', methods=["POST"])
def optimize_script2():
    return optimized()  # Call the optimized function from Script2

# Run the Flask application on port 5000 in debug mode
if __name__ == '__main__':
    app.run(port=5000, debug=True)
