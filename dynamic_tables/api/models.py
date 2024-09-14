from django.db import models

class DynamicTable(models.Model):
    name = models.CharField(max_length=255, unique=True)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name


class TableField(models.Model):
    table = models.ForeignKey(DynamicTable, related_name='fields', on_delete=models.CASCADE)
    name = models.CharField(max_length=255)
    field_type = models.CharField(max_length=50)  # Reduced field length for types
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"{self.name} ({self.field_type})"


class NavigationItem(models.Model):
    name = models.CharField(max_length=255)
    url = models.CharField(max_length=255)  # Consider URLField if appropriate
    order = models.PositiveIntegerField(default=0)  # Ordering for side panel
    parent = models.ForeignKey('self', null=True, blank=True, on_delete=models.CASCADE, related_name='children')  # For hierarchical menus
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.name

    class Meta:
        ordering = ['order']
