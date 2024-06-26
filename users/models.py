from django.db import models

# Create your models here.

# Определение класса Users, который наследует модель Django Model
# class Users(models.Model):
#     # Определение поля user_id типа AutoField как первичного ключа
#     user_id = models.AutoField(primary_key=True)
#     # Определение поля name типа CharField с максимальной длиной в 20 символов
#     name = models.CharField(max_length=20)
#     # Определение поля email типа CharField с максимальной длиной в 20 символов
#     email = models.CharField(max_length=20)

#     # Определение метода __str__, который будет использоваться для представления экземпляров модели в виде строки
#     def __str__(self):
#         return self.name