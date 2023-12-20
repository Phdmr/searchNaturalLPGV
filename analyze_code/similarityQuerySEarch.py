import psycopg2
from psycopg2.extras import DictCursor

postgres_connection_params = {
    'dbname': 'vectorTest',
    'user': 'tester',
    'password': 'yourPassword',
    'host': 'localhost',
    'port': 'yourPort',
}

def find_similar_methods(target_vector, connection):
    with connection.cursor(cursor_factory=DictCursor) as cursor:
        cursor.execute(
            "SELECT id, vector, content, vector <-> %s AS distance FROM methods ORDER BY distance LIMIT 5",
            (target_vector,)
        )
        results = cursor.fetchall()

        for result in results:
            method_id = result['id']
            vector_data = result['vector']
            content = result['content']
            distance = result['distance']
            print(f"Method ID: {method_id}, Vector: {vector_data}, Content: {content}, Distance: {distance}")

target_vector = '[4, 0, 15]'

try:
    with psycopg2.connect(**postgres_connection_params) as connection:
        find_similar_methods(target_vector, connection)

except psycopg2.Error as e:
    print(f"Error connecting to PostgreSQL: {e}")
