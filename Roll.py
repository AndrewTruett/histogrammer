import random

class Roll:
    """This class represents a single roll instance, created from typing a roll command"""
    def __init__(self, num_dice, dice, author, created_at):
        self.author = author
        self.created_at = created_at

        self._rolls = []

        # make sure values are reasonable
        if num_dice < 1:
            raise ValueError("Number of dice cannot be less than 1")

        if num_dice > 100000:
            raise ValueError("Number of dice cannot exceed 100,000")


        if dice < 2:
            raise ValueError("Dice value cannot be less than 2")

        if dice > 1000000:
            raise ValueError("Dice value cannot exceed 1,000,000")

        self.num_dice = num_dice 
        self.dice = dice

        self._roll = self.get_roll()

    def get_roll(self):

        for i in range(self.num_dice):
            self.rolls.append(random.randint(1, self.dice))

        return sum(self.rolls)


    @property
    def roll(self):
        return self._roll

    @property
    def rolls(self):
        return self._rolls

    @rolls.setter
    def rolls(self, value):
        self._rolls = value

    @rolls.deleter
    def rolls(self):
        del self._rolls

    def __str__(self):
        return str(self._roll)
