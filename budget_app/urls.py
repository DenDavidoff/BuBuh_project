from django.urls import path
from .views import HomeView, AddRecordView, ExportCSVView, DocumentationView, ExportChartView

urlpatterns = [
    path('', HomeView.as_view(), name='home'),
    path('add/', AddRecordView.as_view(), name='add_record'),
    path('export_to_csv/', ExportCSVView.as_view(), name='export_to_csv'),
    path('documentation/', DocumentationView.as_view(), name='documentation'),
    path('export_chart/', ExportChartView.as_view(), name='export_chart'),
]
