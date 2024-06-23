from django import forms
from .models import Record
from crispy_forms.helper import FormHelper
from crispy_forms.layout import Submit, Layout, Field, Div
from crispy_forms.bootstrap import FormActions

class RecordForm(forms.ModelForm):
    """
    Форма для добавления новой записи.
    """
    class Meta:
        model = Record
        fields = ['category', 'amount', 'description']
        labels = {
            'category': 'Категория',
            'amount': 'Сумма',
            'description': 'Описание',
        }
        error_messages = {
            'category': {
                'required': 'Пожалуйста, выберите категорию.',
            },
            'amount': {
                'required': 'Пожалуйста, введите сумму.',
                'invalid': 'Введите допустимое числовое значение.',
            },
            'description': {
                'required': 'Пожалуйста, введите описание.',
            },
        }

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['category'].widget.attrs.update({'class': 'form-select', 'placeholder': 'Выберите категорию'})
        self.fields['amount'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Введите сумму'})
        self.fields['description'].widget.attrs.update({'class': 'form-control', 'placeholder': 'Введите описание'})

        self.helper = FormHelper()
        self.helper.form_method = 'post'
        self.helper.form_class = 'form-horizontal'
        self.helper.label_class = 'col-lg-2'
        self.helper.field_class = 'col-lg-8'
        self.helper.layout = Layout(
            Field('category'),
            Field('amount'),
            Field('description'),
            FormActions(
                Submit('submit', 'Сохранить', css_class='btn btn-primary')
            )
        )

class DateRangeForm(forms.Form):
    """
    Форма для фильтрации записей по диапазону дат.
    """
    start_date = forms.DateField(required=False, label='Начальная дата', widget=forms.DateInput(attrs={'type': 'date'}))
    end_date = forms.DateField(required=False, label='Конечная дата', widget=forms.DateInput(attrs={'type': 'date'}))
    min_amount = forms.DecimalField(required=False, label='Минимальная сумма', widget=forms.NumberInput(attrs={'placeholder': 'Минимальная сумма'}))
    max_amount = forms.DecimalField(required=False, label='Максимальная сумма', widget=forms.NumberInput(attrs={'placeholder': 'Максимальная сумма'}))
    category = forms.ChoiceField(required=False, choices=[('', 'Все категории'), ('income', 'Доход'), ('expense', 'Расход')], widget=forms.Select(attrs={'class': 'form-select'}))
    description = forms.CharField(required=False, label='Описание', widget=forms.TextInput(attrs={'placeholder': 'Описание'}))

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.helper = FormHelper()
        self.helper.form_method = 'get'
        self.helper.form_class = 'row'
        self.helper.layout = Layout(
            Div(
                Field('start_date', css_class='col-md-3'),
                Field('end_date', css_class='col-md-3'),
                Field('min_amount', css_class='col-md-2'),
                Field('max_amount', css_class='col-md-2'),
                Field('category', css_class='col-md-2'),
                Field('description', css_class='col-md-3'),
                css_class='row'
            ),
            Submit('submit', 'Фильтр', css_class='btn btn-primary col-md-2')
        )
