from flask import Flask, request, jsonify, render_template
from sqlalchemy import create_engine, text
from src.utils.db import DB

app = Flask(__name__)
connection_string = 'your_connection_string_here'  # Replace with your connection string
engine = create_engine(connection_string)

# Home route
@app.route('/')
def home():
    return render_template('index.html')

# Get all employees
@app.route('/api/employees', methods=['GET'])
def get_employees():
    try:
        with engine.connect():
            query = "SELECT id, name FROM employees"
            result = DB.query_with_return_df(connection_string, query)
            employees = [{"id": row['id'], "name": row['name']} for index, row in result.iterrows()]
        return jsonify(employees)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Add a new employee
@app.route('/api/employees', methods=['POST'])
def add_employee():
    try:
        data = request.json
        name = data.get('name')
        emp_id = data.get('id')

        if not name or not emp_id:
            return jsonify({"error": "Missing employee name or ID"}), 400

        with engine.connect():
            getQuery = f"select  from employees where id = '{emp_id}'"
            result = DB.query_with_return_df(connection_string, getQuery)
            if len(result) > 0:
                return jsonify({"error":"Employee already exists"}), 400

            query = f"INSERT INTO employees (id, name) VALUES ('{emp_id}', '{name}')"
            try:
                DB.statement_call(connection_string, query)
            except Exception as e:
                print("error: ", e)
        return jsonify({"message": "Employee added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Update an employee's details
@app.route('/api/employees/<emp_id>', methods=['PUT'])
def update_employee(emp_id):
    try:
        data = request.json
        name = data.get('name')

        if not name:
            return jsonify({"error": "Missing new employee name"}), 400

        with engine.connect():
            result = DB.query_with_return_df(connection_string, f"select * from employees where id = '{emp_id}'")
            if len(result) > 0:
                return jsonify({"error": "Employee not found"}), 404

            query = f"UPDATE employees SET name = '{name}' WHERE id = '{emp_id}'"
            DB.statement_call(connection_string, query)
        return jsonify({"message": "Employee updated successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Remove an employee
@app.route('/api/employees/<emp_id>', methods=['DELETE'])
def delete_employee(emp_id):
    try:
        with engine.connect():
            # First, remove leaves associated with the employee
            query_delete_leaves = f"DELETE FROM leaves WHERE employee_id = '{emp_id}'"
            DB.statement_call(connection_string, query_delete_leaves)

            # Then, remove the employee
            result = DB.query_with_return_df(connection_string, f"select * from employees where id = '{emp_id}'")
            if len(result) == 0:
                return jsonify({"error": "Employee not found"}), 404
            else:
                query_delete_employee = f"DELETE FROM employees WHERE id = '{emp_id}'"
                DB.statement_call(connection_string, query_delete_employee)

        return jsonify({"message": "Employee deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Get all leaves
@app.route('/api/leaves', methods=['GET'])
def get_leaves():
    try:
        with engine.connect():
            result = DB.query_with_return_df(connection_string, "SELECT employee_id, start_date, end_date, type FROM leaves")
            leaves = [
                {
                    "employee_id": row['employee_id'],
                    "start_date": row['start_date'].strftime('%Y-%m-%d'),
                    "end_date": row['end_date'].strftime('%Y-%m-%d'),
                    "type": row['type'],
                }
                for index, row in result.iterrows()
            ]
        return jsonify(leaves)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Add leave for an employee
@app.route('/api/leaves', methods=['POST'])
def add_leave():
    try:
        data = request.json
        employee_id = data.get('employee_id')
        start_date = data.get('start_date')
        end_date = data.get('end_date')
        leave_type = data.get('type')

        if not employee_id or not start_date or not end_date or not leave_type:
            return jsonify({"error": "Missing leave details"}), 400
        
        if start_date > end_date:
            return jsonify({"error": "Start date cannot be after end date"}), 400

        with engine.connect():
            search_query = f"""
            select  from leaves
            where employee_id = '{employee_id}'
            and start_date = '{start_date}'
            and end_date = '{end_date}'
            """
            result = DB.query_with_return_df(connection_string, search_query)
            if len(result) > 0:
                return jsonify({"error": "Leave already exists"}), 400

            query = f"INSERT INTO leaves (employee_id, start_date, end_date, type) VALUES ('{employee_id}', '{start_date}', '{end_date}', '{type}')"
            DB.statement_call(connection_string, query)
        return jsonify({"message": "Leave added successfully"}), 201
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# Remove leave
@app.route('/api/leaves/', methods=['DELETE'])
def delete_leave(leave_id):
    try:
        employee_id = request.args.get('employeeId')
        start_date = requests.args.get('startDate')
        end_date = requests.args.get('endDate')
        leave_type = requests.args.get('leaveType')

        missing_params = []
        if not employee_id:
            missing_params.append("employee_id")
        if not start_date:
            missing_params.append("start_date")
        if not end_date:
            missing_params.append("end_date")
        if not leave_type:
            missing_params.append("leaveType")
        if missing_params:
            return jsonify({"error": "Missing required parameters", "missing": missing_params}), 400
 
        with engine.connect():
            query = f"""
            select * from leaves
            where employee_id = '{employee_id}'
            and start_date = '{start_date}'
            and end_date = '{end_date}'
            and type = '{leave_type}'
            """
            result = DB.query_with_return_df(connection_string, query)
            if len(result) > 0:
                return jsonify({"error": "Leave not found"}), 404
            else:
                delete_query = f"""
                DELETE FROM leaves 
                WHERE employee_id = '{employee_id}'
                and start_date = '{start_date}'
                and end_date = '{end_date};
                and type = '{leave_type}'
                """
                DB.statement_call(connection_string, delete_query)
            
        return jsonify({"message": "Leave deleted successfully"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host='0.0.0.0', port=8001, debug=True, use_reloader=True, threaded=True)
