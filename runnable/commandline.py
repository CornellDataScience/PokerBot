import argparse
from typing import Match
import click
from torch import jit
import random


class kuhnPokerGame:
    def __init__(self, deck_size, stacks=(10, 10)):
        self.deck_size = deck_size
        self.stacks = stacks
        self.community_pot = (0, 0)
        self.game_tree = ['Start',
                          'Check', 'Bet',
                          'Check', 'Bet', 'Fold', 'Call',
                          '', '', 'Fold', 'Call']
        self.tree_loc = 0  # 2*i + 1, 2*i + 2

    def build_deck():
        # numbers=list(range(self.deck_size))
        #suits = ['H','S','C','D']
        deck = ['J', 'Q', 'K']
        return deck

    def isTerminal(self):
        return self.tree_loc >= 10 or self.tree_loc == 3 or (self.tree_loc >= 5 and self.tree_loc <= 6)

    def getPossibleActions(self):
        return {
            self.game_tree[2 * self.tree_loc + 1]: 2 * self.tree_loc + 1,
            self.game_tree[2 * self.tree_loc + 2]: 2 * self.tree_loc + 2
        }

    def requireAnte(self, ante):
        self.community_pot = (
            self.community_pot[0] + ante, self.community_pot[1] + ante)
        self.stacks = (self.stacks[0] - ante, self.stacks[1] - ante)

    def getPotValue(self):
        return self.community_pot[0] + self.community_pot[1]

    def dealCards(self):
        first = random.randint(0, self.deck_size - 1)
        second = first
        while(second == first):
            second = random.randint(0, self.deck_size - 1)
        return (first, second)


@click.command()
# @click.option('--name', prompt='Your name',help='The person to greet.')
@click.argument('model', type=click.Path(exists=True))
def main(model):
    # click.echo("{}".format(name))
    net = jit.load(model)
    # print(net)

    game = kuhnPokerGame(3, stacks=(1, 1))

    while(True):

        click.echo("Requiring ante of 1: ")
        game.requireAnte(1)
        click.echo(game.stacks)
        cardDealt = game.dealCards()
        click.echo("You have: " + str(cardDealt))

        currentPlayer = 0
        lastAction = ''
        while(not game.isTerminal()):
            actionList = game.getPossibleActions()

            click.echo("Do you choose to: " + str(actionList.keys()))
            action = click.prompt('Please enter exact action: ')
            lastAction = action
            if action == 'Bet':
                game.community_pot = game.community_pot[currentPlayer] + 1
                game.stacks = game.stacks[currentPlayer] - 1
                game.tree_loc = actionList[action]

            elif action == 'Check':
                game.tree_loc = actionList[action]

            elif action == 'Call':
                game.community_pot = game.community_pot[currentPlayer] + 1
                game.stacks = game.stacks[currentPlayer] - 1
                game.tree_loc = actionList[action]

            elif action == 'Fold':
                game.tree_loc = actionList[action]

            currentPlayer = currentPlayer + 1 % 2

        # check winner
        currentStiggityStackz = game.stacks
        click.echo("final amount: " + str(currentStiggityStackz))
        winner = currentPlayer

        if(lastAction == 'Fold'):
            winner = currentPlayer
        else:
            winner = 1 if cardDealt[1] > cardDealt[0] else 0

        click.echo("winner: " + str(winner))
        currentStiggityStackz[winner] = currentStiggityStackz[winner] + \
            game.getPotValue()
        # update stack
        # reinitialize game.
        click.echo("game over")
        game = kuhnPokerGame(3, stacks=currentStiggityStackz)


if __name__ == "__main__":
    main()
