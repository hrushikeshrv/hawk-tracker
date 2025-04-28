from django.contrib.auth import login
from django.http import HttpResponse, HttpResponseRedirect
from django.shortcuts import render, reverse
from django.views.generic import View

from users.forms import UserRegistrationForm


def test_view(request, *args, **kwargs):
    return HttpResponse("Test View")


class UserRegistrationView(View):
    def get(self, request):
        if request.user.is_authenticated:
            return HttpResponseRedirect(reverse('core:index'))
        return render(request, 'users/register.html', {
            'form': UserRegistrationForm(),
        })

    def post(self, request):
        form = UserRegistrationForm(request.POST)
        if form.is_valid():
            new_user = form.save()
            login(request, new_user)
            return HttpResponseRedirect(reverse('core:index'))
        else:
            return render(request, 'users/register.html', {
                'form': form,
            })
