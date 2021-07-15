from file_share.tasks import delete_post
from django.shortcuts import render, redirect
from django.urls.base import reverse_lazy
from django.views.generic.edit import DeleteView
from django.views.generic.list import ListView
from .models import User, Post, Comment
from django.contrib import messages
from .forms import FileShareForm, FileCommentForm
from django.views.generic import DetailView
from django import forms
from django.views import View
# Create your views here.
class HomePageView(ListView):

    def get(self, request):
        delete_post()
        return render(request, 'home.html')

    def post(self, request):
        user_name = request.POST['uname']
        pwd1 = request.POST['pwd1']
        pwd2 = request.POST['pwd2']

        if pwd1 == pwd2:
            add_user = User(username=user_name, password=pwd1)
            add_user.save()
            messages.success(request, 'Account has been created successfully.')
            return redirect('home')
        else:
            messages.warning(request, 'Passwords are not same.')
            return redirect('home')


# Create Upload File System
class UploadView(ListView):
    def get(self, request, user_name):
        return render(request, 'upload_file.html')


    def post(self, request, user_name):
        filename = request.FILES['filename']
        title = request.POST['title']
        desc = request.POST['desc']

        user_obj = User.objects.get(username=user_name)
        upload_post = Post(user=user_obj, title=title, file_field=filename, desc=desc)
        upload_post.save()
        messages.success(request, 'Your Post has been uploaded successfully.')
        return render(request, 'upload_file.html')



# View User Profile
class ProfileView(ListView):
    def get(self, request, user_name):
        user_obj = User.objects.get(username=user_name)
        user = User.objects.filter(username = request.session.get('user'))[0]
        user_posts = user.posts.all()
        context = {'user_data':user_obj, 'user_posts': user_posts}
        return render(request, 'profile.html', context)


# Post Delete View

class PostDeleteView(ListView):
    model = Post
    def get(self, request, post_id):
        user = request.session['user']
        delete_post = self.model.objects.get(id=post_id)
        delete_post.delete()
        messages.success(request, 'Your post has been deleted successfully.')
        return redirect(f'/profile/{user}')


# Search View
class SearchView(ListView):
    def get(self, request):
        query = request.GET['query']
        search_users = User.objects.filter(username__icontains=query)
        search_title = Post.objects.filter(title__icontains = query)
        search_desc = Post.objects.filter(desc__icontains = query)
        search_result = search_title.union(search_desc)
        context = {'query':query, 'search_result':search_result, 'search_users':search_users}
        return render(request, 'search.html', context)


# Login System
class LoginView(ListView):
    def get(self, request):
        return redirect('home')

    def post(self, request):
        user_name = request.POST['uname']
        pwd = request.POST['pwd']

        user_exists = User.objects.filter(username=user_name, password=pwd).exists()
        if user_exists:
            request.session['user'] = user_name
            messages.success(request, 'You are logged in successfully.')
            return redirect('home')
        else:
            messages.warning(request, 'Invalid Username or Password.')
            return redirect('home')

class LogoutView(ListView):
    def get(self, request):
        try:
            del request.session['user']
        except:
            return redirect('home') 
        return redirect('home')

from django.http import HttpResponse

class FileShareDetailView(DetailView):
    model = Post
    template_name = 'share.html'
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        return context

class FileShareListView(ListView):
    model = User
    fields = ['username']
    form_class = FileShareForm

    def get(self, request, pk, *args, **kwargs):
        post = Post.objects.filter(pk=pk).first()
        return render(request, 'share.html', context={'post': post, 'form': self.form_class})

    def post(self, request, pk, *args, **kwargs): 
        form = FileShareForm(request.POST)
        post = Post.objects.filter(pk=pk)
        username = request.POST.get('username')
        user = User.objects.filter(username=username).exists()
        if form.is_valid():
            if user:
                user = User.objects.filter(username=username).first()
                user.posts.add(post)
                user.save()

                return redirect(f'/profile/{user}')
            else:
                return redirect('/')
        return render(request, 'share.html', {'form': form}) 


# File's detail views
class FileShareDetailView(DetailView): 
    model = Post
    template_name = 'file-detail.html'
    form_class_detail = FileCommentForm
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = self.form_class_detail
        post = Post.objects.filter(user__username=self.request.session['user']).first()
        context['post'] = post
        return context



class CommentCreateView(View):
    
    @staticmethod
    def post(request, *args, **kwargs):
        form = FileCommentForm(request.POST or None)
        comment = Comment.objects.get(model=kwargs['content'])
        model = comment.model_class().objects.get(pk=kwargs['object_id'])
        if form.is_valid():
            new_comment = form.save(commit=False)
            new_comment.author = request.user
            new_comment.content = form.cleaned_data['content']
            new_comment.content_object = model
            new_comment.save()
            return redirect('/')
        messages.add_message(request, messages.ERROR, 'Something went wrong')
        return redirect('/')
