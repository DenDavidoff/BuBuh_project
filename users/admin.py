from django.contrib import admin
# Импорт модели Users из текущего каталога (".")
from .models import Users

# Register your models here.

# Регистрация модели MyModel для административного сайта
admin.site.register(Users)