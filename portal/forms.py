import re
from django import forms
from django.core.exceptions import ValidationError
from .models import CustomUser, Application, Category


class RegisterForm(forms.ModelForm):
    password = forms.CharField(label='Пароль', widget=forms.PasswordInput)
    password_confirm = forms.CharField(label='Повтор пароля', widget=forms.PasswordInput)

    class Meta:
        model = CustomUser
        fields = ['full_name', 'username', 'email', 'password', 'password_confirm', 'consent']
        labels = {
            'full_name': 'ФИО',
            'username': 'Логин',
            'email': 'Email',
            'consent': 'Согласие на обработку персональных данных',
        }

    def clean_full_name(self):
        full_name = self.cleaned_data.get('full_name', '').strip()
        if not re.match(r'^[А-Яа-яЁё\s-]+$', full_name):
            raise ValidationError('ФИО должно содержать только кириллические буквы, дефис и пробелы.')
        return full_name

    def clean_username(self):
        username = self.cleaned_data.get('username', '').strip()
        if not re.match(r'^[A-Za-z-]+$', username):
            raise ValidationError('Логин должен содержать только латиницу и дефис.')
        if CustomUser.objects.filter(username__iexact=username).exists():
            raise ValidationError('Пользователь с таким логином уже зарегистрирован.')
        return username

    def clean_email(self):
        email = self.cleaned_data.get('email', '').strip()
        if CustomUser.objects.filter(email__iexact=email).exists():
            raise ValidationError('Этот Email уже используется.')
        return email

    def clean_consent(self):
        consent = self.cleaned_data.get('consent')
        if not consent:
            raise ValidationError('Необходимо дать согласие на обработку персональных данных.')
        return consent

    def clean(self):
        cleaned_data = super().clean()
        password = cleaned_data.get('password')
        password_confirm = cleaned_data.get('password_confirm')
        if password and password_confirm and password != password_confirm:
            self.add_error('password_confirm', 'Пароли не совпадают.')
        return cleaned_data


class ApplicationForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['title', 'description', 'category', 'photo']

    def clean_photo(self):
        photo = self.cleaned_data.get('photo')
        if photo:
            ext = photo.name.split('.')[-1].lower()
            if ext not in ['jpg', 'jpeg', 'png', 'bmp']:
                raise ValidationError('Допустимые форматы изображения: jpg, jpeg, png, bmp.')
            if photo.size > 2 * 1024 * 1024:
                raise ValidationError('Максимальный размер файла — 2 МБ.')
        return photo


class CategoryForm(forms.ModelForm):
    class Meta:
        model = Category
        fields = ['name']

    def clean_name(self):
        name = self.cleaned_data.get('name', '').strip()
        if Category.objects.filter(name__iexact=name).exists():
            raise ValidationError('Категория с таким названием уже существует.')
        return name


class StatusChangeForm(forms.ModelForm):
    class Meta:
        model = Application
        fields = ['status', 'admin_comment', 'design_image']

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self.fields['status'].choices = [
            ('in_progress', 'Принято в работу'),
            ('completed', 'Выполнено'),
        ]

    def clean(self):
        cleaned_data = super().clean()
        status = cleaned_data.get('status')
        comment = cleaned_data.get('admin_comment')
        design_image = cleaned_data.get('design_image')

        if status == 'in_progress' and not comment:
            self.add_error('admin_comment', 'Укажите комментарий при переводе в статус «Принято в работу».')

        if status == 'completed':
            if not design_image:
                self.add_error('design_image', 'Прикрепите изображение готового дизайна.')
            else:
                ext = design_image.name.split('.')[-1].lower()
                if ext not in ['jpg', 'jpeg', 'png', 'bmp']:
                    self.add_error('design_image', 'Допустимые форматы: jpg, jpeg, png, bmp.')
                if design_image.size > 2 * 1024 * 1024:
                    self.add_error('design_image', 'Максимальный размер файла — 2 МБ.')
        return cleaned_data