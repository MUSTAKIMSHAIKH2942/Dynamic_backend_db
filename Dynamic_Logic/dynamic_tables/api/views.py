from django.db import connection
from django.http import JsonResponse
from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from .models import *
from .Serializers import *

# Helper function to run raw SQL queries
def execute_query(query, params=None):
    with connection.cursor() as cursor:
        cursor.execute(query, params)

# ================================
# CRUD OPERATIONS FOR DYNAMIC TABLES
# ================================

# Create table dynamically
# Create table dynamically and store metadata
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
        # Execute the raw SQL to create the table
        execute_query(create_table_query)
        
        # Store metadata in the DynamicTable model
        dynamic_table = DynamicTable.objects.create(name=table_name)

        # Store metadata for each column in the TableField model
        for column in columns:
            TableField.objects.create(
                table=dynamic_table,
                name=column['name'],
                field_type=column['type']
            )
        
        return JsonResponse({'message': f"Table {table_name} created successfully."}, status=201)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# Insert a row into a dynamic table
@api_view(['POST'])
def insert_row(request, table_name):
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

# Add a column to an existing table
# Edit table schema (add a column) and store metadata
@api_view(['POST'])
def add_column(request, table_name):
    column_name = request.data.get('column_name')
    column_type = request.data.get('column_type')

    if not column_name or not column_type:
        return JsonResponse({'error': 'Column name and type are required'}, status=400)

    alter_query = f"ALTER TABLE {table_name} ADD COLUMN {column_name} {column_type}"

    try:
        # Execute the raw SQL to add the column
        execute_query(alter_query)

        # Store metadata for the new column in the TableField model
        dynamic_table = DynamicTable.objects.get(name=table_name)
        TableField.objects.create(
            table=dynamic_table,
            name=column_name,
            field_type=column_type
        )

        return JsonResponse({'message': f"Column {column_name} added to {table_name}."}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# Get all rows of a dynamic table
@api_view(['GET'])
def get_table_data(request, table_name):
    select_query = f"SELECT * FROM {table_name}"

    try:
        with connection.cursor() as cursor:
            cursor.execute(select_query)
            rows = cursor.fetchall()

            # Get column names
            column_names = [desc[0] for desc in cursor.description]

        # Structure the data as a list of dictionaries
        table_data = [dict(zip(column_names, row)) for row in rows]

        return JsonResponse({'data': table_data}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# Delete a row from a dynamic table
@api_view(['DELETE'])
def delete_row(request, table_name, row_id):
    delete_query = f"DELETE FROM {table_name} WHERE id = {row_id}"

    try:
        execute_query(delete_query)
        return JsonResponse({'message': f"Row {row_id} deleted from {table_name}."}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)

# Delete a dynamic table
@api_view(['DELETE'])
def delete_table(request, table_name):
    drop_query = f"DROP TABLE IF EXISTS {table_name}"

    try:
        execute_query(drop_query)
        DynamicTable.objects.filter(name=table_name).delete()
        return JsonResponse({'message': f"Table {table_name} deleted successfully."}, status=200)
    except Exception as e:
        return JsonResponse({'error': str(e)}, status=400)


# ================================
# CRUD OPERATIONS FOR NAVIGATION ITEMS
# ================================

# Get all navigation items (for the sidebar)
@api_view(['GET'])
def list_navigation_items(request):
    items = NavigationItem.objects.all()
    serializer = NavigationItemSerializer(items, many=True)
    return Response(serializer.data)

# Create a new navigation item
@api_view(['POST'])
def create_navigation_item(request):
    serializer = NavigationItemSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Update an existing navigation item
@api_view(['PUT'])
def update_navigation_item(request, pk):
    try:
        item = NavigationItem.objects.get(pk=pk)
    except NavigationItem.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    serializer = NavigationItemSerializer(item, data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(serializer.data)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Delete a navigation item
@api_view(['DELETE'])
def delete_navigation_item(request, pk):
    try:
        item = NavigationItem.objects.get(pk=pk)
    except NavigationItem.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)

    item.delete()
    return Response(status=status.HTTP_204_NO_CONTENT)

@api_view(['GET'])
def list_tables(request):
    tables = DynamicTable.objects.all()
    serializer = DynamicTableSerializer(tables, many=True)
    return Response(serializer.data)


def get_table_fields(request, table_id):
    try:
        # Fetch the DynamicTable instance
        table = DynamicTable.objects.get(id=table_id)
        
        # Fetch fields related to this table
        fields = TableField.objects.filter(table=table)
        
        # Serialize the fields
        fields_data = [{'name': field.name, 'field_type': field.field_type} for field in fields]
        
        return JsonResponse({'fields': fields_data}, status=200)
    except DynamicTable.DoesNotExist:
        return JsonResponse({'error': 'Table not found'}, status=404)
