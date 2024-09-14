from django.urls import path
from . import views

urlpatterns = [
    # Dynamic Table URLs
    path('table/create/', views.create_table, name='create_table'),
    path('table/<str:table_name>/insert/', views.insert_row, name='insert_row'),
    path('table/<str:table_name>/add_column/', views.add_column, name='add_column'),
    path('table/<str:table_name>/data/', views.get_table_data, name='get_table_data'),
    path('table/<str:table_name>/delete_row/<int:row_id>/', views.delete_row, name='delete_row'),
    path('table/<str:table_name>/delete/', views.delete_table, name='delete_table'),

    # Navigation Item URLs (for sidebar menu management)
    path('navigation/', views.list_navigation_items, name='list_navigation_items'),
    path('navigation/create/', views.create_navigation_item, name='create_navigation_item'),
    path('navigation/<int:pk>/update/', views.update_navigation_item, name='update_navigation_item'),
    path('navigation/<int:pk>/delete/', views.delete_navigation_item, name='delete_navigation_item'),

    # Endpoints for managing dynamic tables
    path('tables/', views.list_tables, name='list_tables'),
    path('tables/<int:table_id>/fields/', views.get_table_fields, name='get_table_fields'),

 
]
