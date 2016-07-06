from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView

from .models import Profile


class IndexView(TemplateView):
    template_name = 'profiles/index.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        profiles = Profile.objects.all()
        context['profiles'] = profiles

        return self.render_to_response(context)


class ProfileView(TemplateView):
    template_name = 'profiles/profile.html'

    def get(self, request, pk, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        profile = get_object_or_404(Profile, pk=pk)
        context['profile'] = profile

        return self.render_to_response(context)