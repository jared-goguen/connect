from django.shortcuts import render, redirect
from django.views.generic import TemplateView

from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth import authenticate, login

from profiles.models import Profile


class IndexView(TemplateView):
    template_name = 'home/index.html'


class SignupView(TemplateView):
    template_name = 'home/signup.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['form'] = UserCreationForm()
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        form = UserCreationForm(request.POST)

        if form.is_valid():
            form.save()
            username = form.cleaned_data['username']
            password = form.cleaned_data['password1']
            user = authenticate(username=username, password=password)
            
            profile = Profile(user=user)
            profile.save()

            login(request, user)
            return redirect(request.POST.get('next','/'))
            
        context['form'] = form
        return self.render_to_response(context)