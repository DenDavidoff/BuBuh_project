from django.shortcuts import render, redirect
from django.views.generic import ListView, CreateView, View, TemplateView
from django.views.generic.base import ContextMixin
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.utils import timezone
from django.urls import reverse_lazy
from .models import Record
from .forms import RecordForm, DateRangeForm
from datetime import timedelta
from django.db.models import Sum, Q
import csv
from django.http import HttpResponse
import matplotlib

matplotlib.use("Agg")  # Используем 'Agg' бэкенд для matplotlib
import matplotlib.pyplot as plt
import io
import base64
from django.utils.timezone import make_aware, make_naive, localtime, now

# Create your views here.


class MenuMixin:
    """
    Класс-миксин для добавления меню в контекст шаблона
    """

    timeout = 30

    def get_menu(self):
        """
        Получение и кеширование меню.
        """
        return [
            # {"title": "Главная", "url": "/", "url_name": "main"},
            # {"title": "О проекте", "url": "/about/", "url_name": "about"},
            {"title": "Бухгалтерия", "url": "/buh/", "url_name": "home"},
            # {"title": "Документация", "url": "/buh/documentation/", "url_name": "documentation"},
        ]

    def get_context_data(self, **kwargs):
        """
        Добавление меню в контекст шаблона.
        """
        context = super().get_context_data(**kwargs)
        context["menu"] = self.get_menu()
        return context


class AboutView(MenuMixin, TemplateView):
    """
    Вьюха для статики. Но можно при желании добавить динамический контент
    """

    template_name = "about.html"
    extra_context = {"title": "О проекте"}  # Обновляется только при загрузке Сервера


class MainView(MenuMixin, TemplateView):
    """
    Вьюха для отображения главной страницы.
    """

    template_name = "main.html"


class HomeView(MenuMixin, LoginRequiredMixin, ListView):
    """
    Вьюха для отображения списка записей.
    """
    model = Record
    template_name = 'budget_app/home.html'
    context_object_name = 'records'
    paginate_by = 10  # количество записей на странице

    def get_queryset(self):
        """
        Получение и фильтрация записей пользователя.
        """
        user = self.request.user
        queryset = Record.objects.filter(user=user).order_by('-date')

        # Текущее время с учетом часового пояса
        current_time = now()

        # Фильтрация по дате
        filter_option = self.request.GET.get('filter', None)
        if filter_option == 'this_month':
            queryset = queryset.filter(date__year=current_time.year, date__month=current_time.month)
        elif filter_option == 'last_7_days':
            last_week = current_time - timedelta(days=7)
            queryset = queryset.filter(date__gte=last_week)
        elif filter_option == 'today':
            today_start = make_aware(timezone.datetime.combine(current_time.date(), timezone.datetime.min.time()))
            today_end = make_aware(timezone.datetime.combine(current_time.date(), timezone.datetime.max.time()))
            queryset = queryset.filter(date__range=(today_start, today_end))
        elif filter_option == 'any_date':
            pass

        # Фильтрация по диапазону дат
        start_date = self.request.GET.get('start_date')
        end_date = self.request.GET.get('end_date')
        if start_date and end_date:
            start_date = make_aware(timezone.datetime.strptime(start_date, "%Y-%m-%d"))
            end_date = make_aware(timezone.datetime.strptime(end_date, "%Y-%m-%d") + timedelta(days=1))
            queryset = queryset.filter(date__gte=start_date, date__lt=end_date)

        # Фильтрация по сумме
        min_amount = self.request.GET.get('min_amount')
        max_amount = self.request.GET.get('max_amount')
        if min_amount:
            queryset = queryset.filter(amount__gte=min_amount)
        if max_amount:
            queryset = queryset.filter(amount__lte=max_amount)

        # Фильтрация по категории
        category = self.request.GET.get('category')
        if category:
            queryset = queryset.filter(category=category)

        # Фильтрация по описанию
        description = self.request.GET.get('description')
        if description:
            queryset = queryset.filter(description__icontains=description)

        # Сортировка
        sort_by = self.request.GET.get('sort_by', 'date')
        order = self.request.GET.get('order', 'desc')
        if order == 'desc':
            sort_by = f'-{sort_by}'
        queryset = queryset.order_by(sort_by)

        return queryset

    def get_context_data(self, **kwargs):
        """
        Добавление данных в контекст шаблона.
        """
        context = super().get_context_data(**kwargs)
        records = self.get_queryset()

        # Преобразуем дату в локальное время пользователя
        for record in records:
            record.local_date = localtime(record.date)

        income = records.filter(category='income').aggregate(total=Sum('amount'))['total'] or 0
        expense = records.filter(category='expense').aggregate(total=Sum('amount'))['total'] or 0

        context['balance'] = income - expense
        context['date_range_form'] = DateRangeForm(self.request.GET or None)

        paginator = Paginator(records, self.paginate_by)
        page_number = self.request.GET.get('page')
        page_obj = paginator.get_page(page_number)

        context['records'] = page_obj
        return context


class AddRecordView(MenuMixin, LoginRequiredMixin, CreateView):
    """
    Вьюха для добавления новой записи
    """

    model = Record
    form_class = RecordForm
    template_name = "budget_app/add_record.html"
    success_url = reverse_lazy("home")

    def form_valid(self, form):
        """
        Добавление пользователя в форму перед сохранением.
        """
        form.instance.user = self.request.user
        return super().form_valid(form)


class ExportCSVView(LoginRequiredMixin, View):
    """
    Вьюха для экспорта данных в формате CSV
    """

    def get(self, request, *args, **kwargs):
        user = request.user
        records = Record.objects.filter(user=user).order_by("-date")

        response = HttpResponse(content_type="text/csv; charset=utf-8")
        response.write(
            "\ufeff".encode("utf8")
        )  # Включение BOM для корректной кодировки
        response["Content-Disposition"] = 'attachment; filename="records.csv"'

        writer = csv.writer(response, delimiter=';')
        writer.writerow(['Дата', 'Категория', 'Сумма', 'Описание'])

        for record in records:
            writer.writerow([
                localtime(record.date).strftime('%Y-%m-%d %H:%M:%S'),
                'Доход' if record.category == 'income' else 'Расход',
                record.amount,
                record.description
            ])

        return response


class ExportChartView(MenuMixin, LoginRequiredMixin, ContextMixin, View):
    """
    Вьюха для экспорта данных в виде графика
    """

    def get(self, request, *args, **kwargs):
        user = request.user
        records = Record.objects.filter(user=user).order_by("date")

        income_dates = records.filter(category="income").values_list("date", flat=True)
        income_amounts = records.filter(category="income").values_list(
            "amount", flat=True
        )

        expense_dates = records.filter(category="expense").values_list(
            "date", flat=True
        )
        expense_amounts = records.filter(category="expense").values_list(
            "amount", flat=True
        )

        plt.figure(figsize=(10, 5))
        plt.plot(income_dates, income_amounts, label="Доходы", color="green")
        plt.plot(expense_dates, expense_amounts, label="Расходы", color="red")
        plt.xlabel("Дата")
        plt.ylabel("Сумма")
        plt.title("Доходы и Расходы")
        plt.legend()
        plt.grid(True)

        buffer = io.BytesIO()
        plt.savefig(buffer, format="png")
        buffer.seek(0)
        image_png = buffer.getvalue()
        buffer.close()

        # Закрытие графика
        plt.close()

        graphic = base64.b64encode(image_png)
        graphic = graphic.decode("utf-8")

        context = self.get_context_data()
        context["graphic"] = graphic

        return render(request, "budget_app/chart.html", context)

    def get_context_data(self, **kwargs):
        """
        Добавление данных в контекст шаблона.
        """
        context = super().get_context_data(**kwargs)
        context["menu"] = self.get_menu()
        return context


class DocumentationView(MenuMixin, TemplateView):
    """
    Вьюха для отображения страницы документации.
    """

    template_name = "budget_app/documentation.html"
    extra_context = {"title": "Документация"}
