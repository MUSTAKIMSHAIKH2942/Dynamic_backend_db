from django.db import connection
from django.http import JsonResponse
from rest_framework.decorators import api_view
from .models import DynamicTable

# Helper function to run raw SQL
def execute_query(query, params=None):
    with connection.cursor() as cursor:
        cursor.execute(query, params)


# Insert a row into a dynamic table
@api_view(['POST'])
def insert_row(request):
    table_name = request.data.get('table_name')
    columns = request.data.get('columns')  # {'column1': 'value1', 'column2': 'value2'}

    if not table_name or not columns:
        return JsonResponse({'error': 'Table name and columns are required'}, status=400)

    column_names = ', '.join(columns.keys())
    placeholders = ', '.join(['%s'] * len(columns))
    column_values = list(columns.values())

    # Construct the SQL query
    insert_query = f"INSERT INTO {table_name} ({column_names}) VALUES ({placeholders})"

    try:
        execute_query(insert_query, column_values)  # Call with query and parameters
        return JsonResponse({'message': f"Row added to {table_name}."}, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
    

# Create table dynamically
@api_view(['POST'])
def create_table(request):
    table_name = request.data.get('table_name')
    columns = request.data.get('columns')  # List of dicts [{'name': 'column1', 'type': 'VARCHAR(255)'}, ...]

    if not table_name or not columns:
        return JsonResponse({'error': 'Table name and columns are required'}, status=400)

    # Check if 'id' column is already provided in the request
    primary_key_exists = any(col['name'].lower() == 'id' for col in columns)

    # Create column definitions string
    column_definitions = ", ".join([f"{col['name']} {col['type']}" for col in columns])

    # If no primary key is provided, add 'id SERIAL PRIMARY KEY'
    if not primary_key_exists:
        column_definitions = f"id SERIAL PRIMARY KEY, {column_definitions}"

    create_table_query = f"CREATE TABLE {table_name} ({column_definitions})"
    
    try:
        execute_query(create_table_query)
        DynamicTable.objects.create(name=table_name)
        return JsonResponse({'message': f"Table {table_name} created successfully."}, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# Edit table schema (add a column)
@api_view(['POST'])
def add_column(request, table_name):
    column_name = request.data.get('column_name')
    column_type = request.data.get('column_type')

    if not column_name or not column_type:
        return JsonResponse({'error': 'Column name and type are required'}, status=400)

    alter_query = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"

    try:
        execute_query(alter_query)
        return JsonResponse({'message': f"Column {column_name} added to {table_name}."}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# Delete a row by ID
@api_view(['DELETE'])
def delete_row(request, table_name, row_id):
    delete_query = f"DELETE FROM {table_name} WHERE id = {row_id}"

    try:
        execute_query(delete_query)
        return JsonResponse({'message': f"Row {row_id} deleted from {table_name}."}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# Delete the entire table
@api_view(['DELETE'])
def delete_table(request, table_name):
    drop_query = f"DROP TABLE IF EXISTS {table_name}"

    try:
        execute_query(drop_query)
        DynamicTable.objects.filter(name=table_name).delete()
        return JsonResponse({'message': f"Table {table_name} deleted successfully."}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

@api_view(['GET'])
def get_table_data(request, table_name):
    select_query = f"SELECT * FROM {table_name}"

    try:
        with connection.cursor() as cursor:
            cursor.execute(select_query)
            # Fetch all rows from the table
            rows = cursor.fetchall()

            # Get the column names
            column_names = [desc[0] for desc in cursor.description]

        # Structure the data as a list of dictionaries (for better UI handling)
        table_data = [dict(zip(column_names, row)) for row in rows]

        return JsonResponse({'data': table_data}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)
