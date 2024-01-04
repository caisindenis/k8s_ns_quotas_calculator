from flask import Flask, render_template, request

app = Flask(__name__)

@app.route('/')
def index():
    return render_template('index.html')

@app.route('/calculate', methods=['POST'])
def calculate():
    # Retrieve form data
    cluster_cpu = float(request.form.get('cluster_cpu'))
    cluster_memory = float(request.form.get('cluster_memory'))
    
    # Ensure 'num_namespaces' is an integer, default to 0 if not provided
    num_namespaces = int(request.form.get('num_namespaces', 0))
    
    buffer_percentage = float(request.form.get('buffer_percentage', 0))

    # Retrieve exceptions data
    exceptions = []
    for i in range(num_namespaces):
        namespace_number = i + 1
        namespace_name = f'namespace_{namespace_number}'
        cpu_input = request.form.get(f'{namespace_name}_cpu', '')
        memory_input = request.form.get(f'{namespace_name}_memory', '')

        if cpu_input and memory_input:
            exceptions.append({
                'namespace_number': namespace_number,
                'namespace_name': namespace_name,
                'cpu': float(cpu_input),
                'memory': float(memory_input),
            })

    # Perform exception allocation
    buffered_cluster_cpu = cluster_cpu * (1 - buffer_percentage / 100)
    buffered_cluster_memory = cluster_memory * (1 - buffer_percentage / 100)
    excemption_counter = len(exceptions)
    for exception in exceptions:
        buffered_cluster_cpu -= exception['cpu']
        buffered_cluster_memory -= exception['memory']

    num_namespaces_no_exception = num_namespaces - excemption_counter

    # Calculate 'Per Namespace CPU' and 'Per Namespace Memory'
    per_namespace_cpu = buffered_cluster_cpu / num_namespaces_no_exception
    per_namespace_memory = buffered_cluster_memory / num_namespaces_no_exception

    # Prepare data for each namespace, including exceptions
    namespace_allocations = []
    for i in range(1, num_namespaces + 1):
        namespace_name = f'namespace_{i}'
        is_exception = any(exception['namespace_name'] == namespace_name for exception in exceptions)

        if is_exception:
            # For exceptions, use the specific values
            exception = next((ex for ex in exceptions if ex['namespace_name'] == namespace_name), None)
            per_namespace_cpu_for_namespace = exception['cpu']
            per_namespace_memory_for_namespace = exception['memory']
        else:
            # For non-exceptions, use the general values
            per_namespace_cpu_for_namespace = per_namespace_cpu
            per_namespace_memory_for_namespace = per_namespace_memory

        namespace_allocations.append({
            'namespace_number': i,
            'namespace_name': namespace_name,
            'per_namespace_cpu': per_namespace_cpu_for_namespace,
            'per_namespace_memory': per_namespace_memory_for_namespace,
        })

    # Return results
    result = {
        'cluster_cpu': cluster_cpu,
        'cluster_memory': cluster_memory,
        'num_namespaces': num_namespaces,
        'buffer_percentage': buffer_percentage,
        'per_namespace_cpu': per_namespace_cpu,
        'per_namespace_memory': per_namespace_memory,
        'namespace_allocations': namespace_allocations,  # Pass the data to the template
        'exceptions': exceptions,
    }

    return render_template('result.html', result=result)

if __name__ == '__main__':
    app.run(debug=True)
