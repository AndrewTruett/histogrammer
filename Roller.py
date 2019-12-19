

from Roll import Roll

class Roller:

    def __init__(self, user):
        self._rolls = []

        self._user = user



    def add_roll(self, roll):
        self._rolls.append(roll)

    def clear_rolls(self):
        self._rolls = []

    @property
    def rolls(self):
        return self._rolls

    @property
    def user(self):
        return self._user

    