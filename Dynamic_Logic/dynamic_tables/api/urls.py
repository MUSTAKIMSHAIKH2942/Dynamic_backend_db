from django.urls import path
from . import views

urlpatterns = [
    path('create-table/', views.create_table, name='create_table'),
    path('insert-row/<str:table_name>/', views.insert_row, name='insert_row'),
    path('add-column/<str:table_name>/', views.add_column, name='add_column'),
    path('delete-row/<str:table_name>/<int:row_id>/', views.delete_row, name='delete_row'),
    path('delete-table/<str:table_name>/', views.delete_table, name='delete_table'),
    path('get-table-data/<str:table_name>/', views.get_table_data, name='get_table_data'),
    path('insert-row/', views.insert_row, name='insert_row'),
]
