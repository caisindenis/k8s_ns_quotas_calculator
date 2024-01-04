from flask import Flask, render_template, request, Response, send_file
import pandas as pd
import os

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    # Retrieve form data (cluster resources, number of namespaces, and buffer percentage)
    cluster_cpu = float(request.form.get('cluster_cpu'))
    cluster_memory = float(request.form.get('cluster_memory'))
    num_namespaces = int(request.form.get('num_namespaces'))
    buffer_percentage = float(request.form.get('buffer_percentage', 0))

    # Apply buffer percentage
    cpu_with_buffer = cluster_cpu * (1 - buffer_percentage / 100)
    memory_with_buffer = cluster_memory * (1 - buffer_percentage / 100)

    # Perform calculations for resource quotas per namespace
    per_namespace_cpu = cpu_with_buffer / num_namespaces
    per_namespace_memory = memory_with_buffer / num_namespaces

    # Create a DataFrame for export
    df = pd.DataFrame({
        'Namespace': [f'Namespace_{i+1}' for i in range(num_namespaces)],
        'Per Namespace CPU': [per_namespace_cpu] * num_namespaces,
        'Per Namespace Memory': [per_namespace_memory] * num_namespaces,
    })

    # Specify the full path or a relative path to the directory where the app is running
    excel_path = os.path.join(os.getcwd(), 'result.xlsx')
    csv_path = os.path.join(os.getcwd(), 'result.csv')

    # Export to Excel and CSV
    df.to_excel(excel_path, index=False)
    df.to_csv(csv_path, index=False)

    # Return results
    result = {
        'per_namespace_cpu': per_namespace_cpu,
        'per_namespace_memory': per_namespace_memory,
    }

    return render_template('result.html', result=result)

@app.route('/export_excel')
def export_excel():
    return send_file('result.xlsx', as_attachment=True)

@app.route('/export_csv')
def export_csv():
    return send_file('result.csv', as_attachment=True)

if __name__ == '__main__':
    app.run(debug=True)
