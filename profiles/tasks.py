import random

from celery.decorators import periodic_task

from django.contrib.auth.models import User
from django.contrib import messages
from games.models import Game



class MoveAnalyzer(object):
    def __init__(self):
        pass

    def get_move(self, game):
        positions = game.get_valid_moves()
        return random.choice(positions)


class Bot(object):
    analyzer = MoveAnalyzer()

    @classmethod
    def get_bots(cls, names):
        return [cls(name) for name in names]

    def __init__(self, username):
        self.username = username
        self.user = User.objects.get(username=username)
        self.open_game = None

    def make_move(self, game):
        row, col = self.analyzer.get_move(game)
        game.make_move(self.user, row, col)

    def make_moves(self):
        for game in self.user.games.all():
            if game.next_player == self.user:
                self.make_move(game)

    def in_game(self):
        for game in self.user.games.all():
            if game.started and not game.done:
                return True
        return False

    def start_game(self):
        Game.create_game(self.user, 
            title='{}\'s game'.format(self.username))

    def join_random_game(self):
        games = Game.objects.filter(full=False)
        not_already_in = [g for g in games if g not in self.user.games.all()]
        if not_already_in:
            game = random.choice(not_already_in)
            game.add_player(self.user)

    def automate(self):
        self.make_moves()
        if not self.in_game():
            self.start_game()
            self.join_random_game()


BOT_NAMES = ('bob', 'albert')
BOTS = Bot.get_bots(BOT_NAMES)

@periodic_task(run_every=5)
def run_bots():
    for bot in BOTS:
        bot.automate()
