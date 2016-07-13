from django.shortcuts import render, redirect, get_object_or_404
from django.views.generic import TemplateView
from django.contrib.auth.decorators import login_required
from django.contrib import messages

from .models import Game
from .forms import CreateForm


class CellWrapper:
    def __init__(self, row, col, value):
        self.row = row
        self.col = col
        self.value = value

class RowWrapper(list):
    def __init__(self, row, values):
        super(RowWrapper, self).__init__(self)
        self.row = row
        for col, value in enumerate(values):
            self.append(CellWrapper(row, col, value))

class BoardWrapper(list):
    def __init__(self, game):
        super(BoardWrapper, self).__init__(self)
        for row, values in enumerate(game.board):
            self.append(RowWrapper(row, values))


class IndexView(TemplateView):
    template_name = 'games/index.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        games = Game.objects.all()
        context['games'] = games

        return self.render_to_response(context)


class GameView(TemplateView):
    template_name = 'games/game.html'

    def get(self, request, pk, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        game = get_object_or_404(Game, pk=pk)
        context['game'] = game
        context['board'] = BoardWrapper(game)
        context['is_turn'] = game.is_turn(request.user)
        context['in_game'] = game.in_game(request.user)
        context['can_join'] = game.can_join(request.user)

        return self.render_to_response(context)

    def post(self, request, pk, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        game = get_object_or_404(Game, pk=pk)

        row = int(request.POST.get('row'))
        col = int(request.POST.get('col'))
        
        tag, text = game.make_move(request.user, row, col)
        messages.add_message(request, tag, text)

        return redirect(request.path)

class CreateView(TemplateView):
    template_name = 'games/new.html'

    def get(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)
        context['form'] = CreateForm()
        return self.render_to_response(context)

    def post(self, request, *args, **kwargs):
        context = self.get_context_data(**kwargs)

        form = CreateForm(request.POST)

        if form.is_valid():
            game = Game.create_game(request.user, 
                            title=form['title'].value())
            return redirect('game-view', game.id)

        context['form'] = form
        return self.render_to_response(context)


@login_required
def join_game(request, pk):
    follow = request.GET.get('next', '')

    try:
        game = Game.objects.get(pk=pk)
        tag, text = game.add_player(request.user)

    except Game.DoesNotExist:
        tag, text = messages.ERROR, 'Game no longer exists'
        
    messages.add_message(request, tag, text)
    return redirect(follow)
