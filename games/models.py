import json

from django.db import models
from django.contrib.auth.models import User
from django.contrib import admin, messages
from django.contrib.postgres.fields import JSONField

from itertools import cycle
from random import shuffle


def get_default_board(rows=6, cols=7):
    return [[-1] * cols] * rows

def get_default_order():
    return []

class Game(models.Model):
    class Meta:
        ordering = ('created',)

    created = models.DateTimeField(auto_now_add=True)
    rows = models.IntegerField(default=6)
    cols = models.IntegerField(default=7)
    board = JSONField(default=get_default_board())
    turn = models.IntegerField(default=-1)
    players = models.ManyToManyField(User, related_name='games', blank=True)
    started = models.BooleanField(default=False)
    done = models.BooleanField(default=False)
    title = models.TextField(max_length=30)
    total_players = models.IntegerField(default=2)
    order = JSONField(default=get_default_order())
    next_player = models.ForeignKey(User, related_name='next_player', blank=True, null=True)
    winner = models.ForeignKey(User, related_name='winner', blank=True, null=True)
    connect = models.IntegerField(default=4)
    full = models.BooleanField(default=False)

    @property
    def status(self):
        if self.done:
            return 'Complete'
        elif self.started:
            return 'In progress'
        return 'Waiting for players'

    def add_player(self, user):
        if user in self.players.all():
            return messages.ERROR, 'You are already in Game #{}'.format(self.id)

        elif not self.full:
            self.players.add(user)
            self.order.append(user.pk)

            if len(self.players.all()) == self.total_players:
                self.full = True
                self.start_game()

            self.save()
            return messages.SUCCESS, 'You have successfully joined Game #{}'.format(self.id)
        
        else:
            return messages.ERROR, 'Game is full'

    @classmethod
    def create_game(cls, user, **kwargs):
        game = cls(**kwargs)
        game.save()
        game.add_player(user)
        game.save()
        return game

    def start_game(self):
        self.started = True
        shuffle(self.order)
        self.advance_turn()
        self.save()

    # does not save on it's own...
    def advance_turn(self):
        self.turn = (self.turn + 1) % self.total_players
        pk = self.order[self.turn]
        self.next_player = self.players.get(pk=pk)

    def is_turn(self, user):
        if self.next_player is not None:
            return user.pk == self.next_player.pk
        return False

    def in_game(self, user):
        return user.pk in self.order

    def can_join(self, user):
        if not self.full:
            return user.is_authenticated() and not self.in_game(user)
        return False

    def check_valid_position(self, row, col):
        if row < 0 or row >= self.rows:
            return False
        if col < 0 or col >= self.cols:
            return False
        if self.board[row][col] != -1:
            return False
        if row != 0 and self.board[row-1][col] == -1:
            return False
        return True

    def get_valid_moves(self):
        positions = []
        for col in range(self.cols):
            for row in range(self.rows):
                if self.board[row][col] == -1:
                    positions.append((row, col))
                    break
        return positions

    def make_move(self, user, row, col):
        if not self.is_turn(user):
            return messages.ERROR, 'It is not your turn...'
        
        if not self.check_valid_position(row, col):
            return messages.ERROR, 'That is not a valid move...'

        self.board[row][col] = self.turn
        
        if self.check_victory():
            self.assign_victor(self.next_player)
            self.save()
            return messages.SUCCESS, 'You won!'
        elif self.is_full():
            self.assign_victor(None)
            self.save()
            return messages.SUCCESS, 'The game is a draw...'
        else:
            self.advance_turn()
            self.save()
            return messages.SUCCESS, 'You have made your move!'

    def assign_victor(self, winner):
        self.done = True
        self.turn = -1
        self.winner = winner
        self.next_player = None

    def is_full(self):
        for col in self.board[-1]:
            if col == -1:
                return False
        return True

    def check_victory(self):     
        # check rows 
        for row in range(self.rows):
            for col in range(self.cols - self.connect + 1):
                for check in range(col, col + self.connect):
                    if self.board[row][check] != self.turn:
                        break
                else:
                    return True

        # check cols 
        for col in range(self.cols):
            for row in range(self.rows - self.connect + 1):
                for check in range(row, row + self.connect):
                    if self.board[check][col] != self.turn:
                        break
                else:
                    return True

        # check forward diagonal
        for row in range(self.rows - self.connect + 1):
            for col in range(self.cols - self.connect + 1):
                for add in range(self.connect):
                    if self.board[row + add][col + add] != self.turn:
                        break
                else:
                    return True

        # check backward diagonal
        for row in range(self.connect - 1, self.rows):
            for col in range(self.cols - self.connect + 1):
                for add in range(self.connect):
                    if self.board[row - add][col + add] != self.turn:
                        break
                else:
                    return True

        return False








admin.site.register(Game)


