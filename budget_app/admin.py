from django.contrib import admin
from .models import Record

# Register your models here.

@admin.register(Record)
class RecordAdmin(admin.ModelAdmin):
    list_display = ('user', 'category', 'amount', 'description', 'date')
    search_fields = ('description',)
    list_filter = ('category', 'date', 'user')
    date_hierarchy = 'date'
    ordering = ('-date',)