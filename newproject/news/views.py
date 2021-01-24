from django.shortcuts import render
from django.core.paginator import Paginator
from django.views.generic import ListView, DetailView, UpdateView, CreateView, DeleteView
from django.contrib.auth.mixins import LoginRequiredMixin, PermissionRequiredMixin
from django.shortcuts import redirect
from django.contrib.auth.decorators import login_required
from django.core.mail import send_mail

from .models import *
from .filters import NewsFilter
from .forms import PostForm


class NewsList(ListView):
    model = Post
    template_name = 'News.html'
    context_object_name = 'News'
    ordering = ['-datetime']
    paginate_by = 4
    form_class = PostForm

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['category_politic'] = Category.objects.get(category_name='Политика').id
        context['category_sport'] = Category.objects.get(category_name='Спорт').id
        context['category_weather'] = Category.objects.get(category_name='Погода').id
        context['category_economics'] = Category.objects.get(category_name='Экономика').id
        return context


class NewsDetail(DetailView):
    model = Post
    template_name = 'New.html'
    context_object_name = 'New'
    queryset = Post.objects.all()


class PostSearch(ListView):
    model = Post
    template_name = 'search.html'
    context_object_name = 'search'

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['filter'] = NewsFilter(self.request.GET, queryset=self.get_queryset())
        return context


class PostCreate(PermissionRequiredMixin, CreateView):
    model = Post
    template_name = 'post_create.html'
    form_class = PostForm
    permission_required = ('News.add_post', 'News.view_post')


class PostUpdateView(PermissionRequiredMixin, LoginRequiredMixin, UpdateView):
    model = Post
    template_name = 'post_edit.html'
    form_class = PostForm
    login_url = 'login/'
    redirect_file_name = '/'
    permission_required = ('News.change_post', 'News.view_post')


class PostDeleteView(PermissionRequiredMixin, DeleteView):
    model = Post
    template_name = 'post_delete.html'
    queryset = Post.objects.all()
    success_url = '/News/'
    permission_required = ['News.delete_post', 'News.view_post']


class PostCategory(DetailView):
    model = Category
    template_name = 'category.html'
    context_object_name = 'PostCategory'

    def get_context_data(self, **kwargs):
        id = self.kwargs.get('pk')
        context = super().get_context_data(**kwargs)
        # Контекст для списка новостей в текущей категории
        context['category_news'] = Post.objects.filter(post_category=id)
        # Контекст подписан ли пользователь на текущую категорию. .exists() возвращает булево значение
        context['is_subscribe'] = CategorySubscribers.objects.filter(category=id, user=self.request.user).exists()
        return context


@login_required
def subscribe_category(request):
    # Достаем текущего пользователя
    user = request.user
    # Получаем ссылку из адресной строки и берем pk как id категории
    id = request.META.get('HTTP_REFERER')[-1]
    # Получаем текущую категорию
    category = Category.objects.get(id=id)
    print(id)
    # Создаем связь между пользователем и категорией
    category.subscribers.add(user)
    send_mail(
        subject=f'{User.username} ',
        # имя клиента и дата записи будут в теме для удобства
        message=f'Вы были подписаны на категорию {category}',  # сообщение с кратким описанием проблемы
        from_email=settings.DEFAULT_FROM_EMAIL,  # здесь указываете почту, с которой будете отправлять (об этом попозже)
        recipient_list=[f'{user.email}', ]  # здесь список получателей. Например, секретарь, сам врач и т. д.
    )
    print(f'send email to {user.email}')
    return redirect('/')


# Подписка пользователя в категорию новостей


@login_required
def unsubscribe_category(request):
    # Достаем текущего пользователя
    user = request.user
    # Получаем ссылку из адресной строки и берем pk как id категории
    id = request.META.get('HTTP_REFERER')[-1]
    # Получаем текущую категорию
    category = Category.objects.get(id=id)
    # Разрываем связь между пользователем и категорией
    category.subscribers.remove(user)
    send_mail(
        subject=f'{category.subscribers}',
        # имя клиента и дата записи будут в теме для удобства
        message=f'Вы были одписаны на категорию {category}',  # сообщение с кратким описанием проблемы
        from_email=settings.DEFAULT_FROM_EMAIL,  # здесь указываете почту, с которой будете отправлять (об этом попозже)
        recipient_list=[f'{user.email}', ]  # здесь список получателей. Например, секретарь, сам врач и т. д.
    )
    print(f'send email to {user.email}')
    return redirect('/')
