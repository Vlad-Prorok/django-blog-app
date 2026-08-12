from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth import login
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from .models import Article, Comment
from .forms import SingUpForm, ArticleForm, CommentForm

def post_list(request):
    articles = Article.objects.all()
    return render(request, 'blog/post_list.html', {'articles': articles})

def post_detail(request, pk):
    article = get_object_or_404(Article, pk=pk)
    comments = article.comments.all()  # <--- ВАЖНО: переменная должна быть объявлена здесь!
    
    if request.method == 'POST':
        if not request.user.is_authenticated:
            return redirect('login')
        form = CommentForm(request.POST)
        if form.is_valid():
            comment = form.save(commit=False)
            comment.article = article
            comment.author = request.user
            comment.save()
            messages.success(request, 'Комментарий добавлен!')
            return redirect('post_detail', pk=pk)
    else:
        form = CommentForm()
    return render(request, 'blog/post_detail.html', {
        'article': article,
        'comments': comments,
        'comment_form': form
    })
        
@login_required
def post_create(request):
    if request.method == 'POST':
        form = ArticleForm(request.POST)
        if form.is_valid():
            article = form.save(commit=False)
            article.author = request.user
            article.save()
            messages.success(request, 'Статья Успешно опубликованна!')
            return redirect('post_detail', pk=article.pk)
    else:
        form = ArticleForm()
    return render(request, 'blog/post_form.html', {'form': form, 'title': 'Создать статью'})

@login_required
def post_edit(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if article.author != request.user:
        messages.error(request, 'Вы можете редактировать только свои статьи!')
        return redirect('post_detail', pk=pk)
    
    if request.method == 'POST':
        form = ArticleForm(request.POST, instance=article)
        if form.is_valid():
            form.save()
            messages.success(request, 'Статья обновлена')
            return redirect('post_detail', pk=article.pk)
    else:
        form = ArticleForm(instance=article)
    return render(request, 'blog/post_form.html', {'form': form, 'title': 'Редактировать статью'})

@login_required
def post_delete(request, pk):
    article = get_object_or_404(Article, pk=pk)
    if article.author != request.user:
            messages.error(request, 'Вы можете удалять только свои статьи!')
            return redirect('post_detail', pk=pk)
    if request.method == 'POST':
        article.delete()
        messages.success(request, 'Статья успешно удалена')
        return redirect('post_list')
    return render(request, 'blog/post_confirm_delete.html', {'article': article})

def signup(request):
    if request.method == 'POST':
        form = SingUpForm(request.POST)
        if form.is_valid():
            user = form.save()
            login(request, user)
            messages.success(request, 'Регистрация прошла успешно')
            return redirect('post_list')
    else:
        form = SingUpForm()
    return render(request, 'registration/signup.html', {'form': form}) 