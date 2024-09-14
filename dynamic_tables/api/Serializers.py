from rest_framework import serializers
from .models import *

class NavigationItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = NavigationItem
        fields = '__all__'

from rest_framework import serializers
from .models import DynamicTable

class DynamicTableSerializer(serializers.ModelSerializer):
    class Meta:
        model = DynamicTable
        fields = '__all__'

from rest_framework import serializers
from .models import TableField

class TableFieldSerializer(serializers.ModelSerializer):
    class Meta:
        model = TableField
        fields = ['id', 'name', 'field_type', 'created_at']
