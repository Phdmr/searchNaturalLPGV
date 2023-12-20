import ast
import os
import psycopg2
from psycopg2.extras import DictCursor
from array import array

# Example usage:
directory_path = '/home/pedro/Documentos/GitHub/PubSubUDPpy'
postgres_connection_params = {
    'dbname': 'vectorTest',
    'user': 'tester',
    'password': 'yourPassword',
    'host': 'localhost',
    'port': 'yourPort',
}

def get_method_content(source_code, start_line, end_line):
    lines = source_code.split('\n')
    method_lines = lines[start_line - 1:end_line]
    return '\n'.join(method_lines)

def analyze_file(file_path, connection):
    with open(file_path, 'r') as file:
        source_code = file.read()

    try:
        print(f"Analyzing file: {file_path}")
        tree = ast.parse(source_code)

        # Convert method information to a vector
        method_vectors = [(node.lineno, node.col_offset, node.end_lineno) for node in ast.walk(tree) if isinstance(node, ast.FunctionDef)]

        # Insert method vectors and content into PostgreSQL table
        with connection.cursor() as cursor:
            for method_vector in method_vectors:
                start_line, start_col, end_line = method_vector
                vector_value = array('f', method_vector)  # Create a float array for the vector
                vector_list = list(vector_value)  # Convert the array to a list
                method_content = get_method_content(source_code, start_line, end_line)
                cursor.execute(
                    "INSERT INTO methods (vector, content) VALUES (%s, %s)",
                    (vector_list, method_content)
                )

        connection.commit()
    except SyntaxError as e:
        print(f"Error parsing {file_path}: {e}")

def analyze_directory(directory_path, connection):
    for filename in os.listdir(directory_path):
        if filename.endswith(".py"):
            file_path = os.path.join(directory_path, filename)
            analyze_file(file_path, connection)

def list_methods(connection):
    with connection.cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute("SELECT vector, content FROM methods")
        results = cursor.fetchall()

        for result in results:
            vector_data = result['vector']
            content = result['content']
            # Process the vector and content or extract specific components
            print(f"Vector: {vector_data}, Content: {content}")

try:
    with psycopg2.connect(**postgres_connection_params) as connection:
        with connection.cursor() as cursor:
            # Manually register the vector type
            cursor.execute("CREATE EXTENSION IF NOT EXISTS vector")
            connection.commit()

        # Create a table named 'methods' if it doesn't exist
        with connection.cursor() as cursor:
            cursor.execute("""
                CREATE TABLE IF NOT EXISTS methods (
                    id SERIAL PRIMARY KEY,
                    vector vector,
                    content TEXT
                )
            """)
        connection.commit()

        # Analyze the directory and store method information
        analyze_directory(directory_path, connection)

        # List methods stored in the 'methods' table
        list_methods(connection)

except psycopg2.Error as e:
    print(f"Error connecting to PostgreSQL: {e}")
