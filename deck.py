# In[]

import random
import numpy as np

# In[]

def check_if_playable(activeCard, card):

    #Can play any card
    if card.colour == "Wild":
        return True

    #Match colour or symbol
    elif card.value == activeCard.value or card.colour == activeCard.colour:
        return True
    else:
        return False

def UNO(player):

    if player.cpu == False:
        print("UNO! (You, {})".format(player.name))
    else:
        print("UNO! ({})".format(player.name))

class Game():

    def __init__(self, playerCount, names, auto=True, n_players=0):

        #Init variables
        self.names = names
        self.playerCount = playerCount
        self.firstPlayer = random.randrange(0, self.playerCount, 1)
        ## 1 is clockwise, -1 is anti-clockwise
        self.increment = 1
        self.drawStack = 0
        self.auto = auto

        #Ready deck
        self.deck = Deck(True, "unodeck.txt")
        self.deck.shuffle()

        #Ready discard, get starting card
        self.discard = Deck()
        self.discard.cards.insert(0, self.deck.cards.pop(0))

        #Init players
        self.players = []
        for chair in range(self.playerCount):
            newPlayer = Player(names[chair], self.names.index(names[chair]))
            newPlayer.draw(self.deck, n=7)
            self.players.append(newPlayer)

        #Add non-cpu player
        if auto == False:
            for i in range(n_players):
                self.players[i].cpu = False
                print("Player {}, choose a name:".format(i+1))
                pname = input("Enter your name:").capitalize()
                self.players[i].name = pname

        print("First Card is {} {}.".format(self.discard.cards[0].colour, self.discard.cards[0].value))
        self.playCard = self.discard.cards[0]

        #Shuffle player positions
        random.shuffle(self.players)

        #Introduce the table
        seatOrder = ""
        for player in self.players:
            seatOrder += (player.name + ", ")
        print("Our table tonight:")
        print(seatOrder[:-2])

        #Take first turn
        if self.players[self.firstPlayer].cpu == False:
            print("You start")
        else:
            print("{} will start.".format(self.players[self.firstPlayer].name))

        self.Turn(self.firstPlayer)

    def Turn(self, seat):

        #Current card and player
        activeCard = self.discard.cards[0]
        currentPlayer = self.players[seat]

        #Reshuffle discard back into deck if out of cards
        if len(self.deck.cards) == 0:

            self.deck.cards.append(self.discard.cards[1:])
            self.discard.cards = self.discard.cards[0]
            self.deck.shuffle()
            print("Deck re-shuffled")

        #DrawTwo is played
        if activeCard.value == "DrawTwo" and activeCard.action == True:

            #Start draw chain
            if self.drawStack == 0:
                self.drawStack = 2

            #Check for response
            DrawTwos = []
            for card in currentPlayer.hand:
                if card.value == "DrawTwo":
                    DrawTwos.append(card)

            #Option to stack draw chain
            if len(DrawTwos) != 0:

                #If current player
                if currentPlayer.cpu == False:
                    currentPlayer.showHand()

                    #Prompt to draw or play
                    while True:
                        print("{}, Draw? (Y/N):".format(currentPlayer.name))
                        confirm = str(input("(Y/N)")).upper()

                        if confirm != "Y" and confirm != "N":
                            print("Enter Y or N")
                        else:
                            break

                    #Player opts to draw
                    if confirm == "Y":
                        print("You draw {} cards ({})".format(self.drawStack, currentPlayer.name))
                        currentPlayer.draw(self.deck, self.drawStack)

                        #Action has been resolved
                        self.drawStack = 0
                        activeCard.action = False

                    #Player opts to counter
                    elif confirm == "N":

                        #Standard play prompt
                        while True:

                            currentPlayer.showHand()
                            print("{}, Choose card (1, 2, 3, ...):".format(currentPlayer.name))

                            while True:
                                try:
                                    choice = int(input("Choose card (Index):")) - 1
                                    break
                                except ValueError:
                                    print("Pick a number (1, 2, 3, ...)")

                            #Legality check
                            if check_if_playable(activeCard, currentPlayer.hand[choice]):
                                currentPlayer.play(self.discard, currentPlayer.hand[choice])
                                break

                            else:
                                print("Not a legal card (Pick another)")

                        self.drawStack += 2

                #CPU always plays DrawTwo
                else:
                    currentPlayer.play(self.discard, random.choice(DrawTwos))
                    self.drawStack += 2

            #Take draw penalty
            else:
                if currentPlayer.cpu == False:
                    print("You draw {} cards ({})".format(self.drawStack, currentPlayer.name))
                else:
                    print("{} draws {} cards".format(currentPlayer.name, self.drawStack))
                currentPlayer.draw(self.deck, self.drawStack)

                #Action has been resolved
                self.drawStack = 0
                activeCard.action = False

            #Next player
            nextSeat = (seat + self.increment) % self.playerCount

            #Was that the last card?
            if len(currentPlayer.hand) == 0:
                if currentPlayer.cpu == False:
                    print("You win! ({})".format(currentPlayer.name))
                else:
                    print("{} wins!".format(currentPlayer.name))

            #Next turn
            else:
                if len(currentPlayer.hand) == 1:
                    UNO(currentPlayer)
                self.Turn(nextSeat)

        #DrawFour played
        elif activeCard.value == "DrawFour" and activeCard.action == True:

            #Take penalty
            if currentPlayer.cpu == False:
                print("You draw 4 cards")
            else:
                print("{} draws 4 cards".format(currentPlayer.name))

            #Resolve card and go to next seat
            currentPlayer.draw(self.deck, 4)
            activeCard.action = False
            nextSeat = (seat + self.increment) % self.playerCount
            self.Turn(nextSeat)

        else:

            #List possible plays
            options = []
            for card in currentPlayer.hand:
                if check_if_playable(activeCard, card):
                    options.append(card)

            #Play random legal card
            if len(options) != 0:

                if currentPlayer.cpu == False:

                    #Prompt to play a card
                    while True:

                        print("Active card: {} {}".format(activeCard.colour, activeCard.value))
                        currentPlayer.showHand()
                        print("Choose card (1, 2, 3, ...):")

                        while True:
                            try:
                                choice = int(input("Choose card (Index):")) - 1
                                break
                            except ValueError:
                                print("Pick a number (1, 2, 3, ...)")

                        #Legality check
                        if check_if_playable(activeCard, currentPlayer.hand[choice]):
                            self.playCard = currentPlayer.hand[choice]
                            currentPlayer.play(self.discard, currentPlayer.hand[choice])
                            break

                        else:
                            print("Not a legal card (Pick another)")


                #CPU plays random card
                else:
                    self.playCard = random.choice(options)
                    currentPlayer.play(self.discard, self.playCard)

            #No available options
            else:
                if currentPlayer.cpu == False:
                    print("You draw a card ({})".format(currentPlayer.name))
                    currentPlayer.showHand()
                else:
                    print("{} draws a card".format(currentPlayer.name))
                currentPlayer.draw(self.deck)
                newCard = currentPlayer.hand[-1]
                self.playCard.action = False

                #Drawn card is playable
                if check_if_playable(activeCard, newCard):

                    #Prompt to play drawn card
                    if currentPlayer.cpu == False:

                        while True:
                            print("{}, You drew a {} {}, Play? (Y/N)".format(currentPlayer.name, newCard.colour, newCard.value))
                            choice = str(input("Y/N:")).upper()

                            if choice != "Y" and choice != "N":
                                print("Enter Y or N")

                            elif choice == "Y":
                                currentPlayer.play(self.discard, newCard)
                                self.playCard = newCard
                                break

                            elif choice == "N":
                                break

                    #CPU always plays card drawn if playable
                    else:
                        currentPlayer.play(self.discard, newCard)
                        self.playCard = newCard

            #Adjust order for skip/reverse
            if self.playCard.action == True:
                if self.playCard.value == "Reverse":
                    self.increment *= -1
                if self.playCard.value == "Skip":
                    self.increment *= 2

            #Next seat and resolve skip
            nextSeat = (seat + self.increment) % self.playerCount
            self.increment = 1 * np.sign(self.increment)

            if len(currentPlayer.hand) == 0:
                if currentPlayer.cpu == False:
                    print("You Win! ({})".format(currentPlayer.name))
                else:
                    print("{} wins!".format(currentPlayer.name))

            else:
                if len(currentPlayer.hand) == 1:
                    UNO(currentPlayer)
                self.Turn(nextSeat)


class Deck():

    def __init__(self, first=False, filename=None):

        #List of Card class
        self.cards = []
        self.first = first
        self.filename = filename

        if self.first:
            self.build()

    def build(self):

        #Read UNO cards from .txt file
        f = open(self.filename, 'r')

        for card in f.readlines():
            colour = card.split()[0]
            value = card.split()[1]
            action = card.split()[2]

            self.cards.append(Card(colour, value, action))

    def show(self):

        for card in self.cards:
            card.show()

    def shuffle(self):

        #Some shuffle algorithm (can't remember name)
        for i in range(len(self.cards) - 1, 0, -1):
            r = random.randint(0, i)
            self.cards[i], self.cards[r] = self.cards[r], self.cards[i]

    def drawCard(self):

        return self.cards.pop(0)


class Card():

    def __init__(self, colour, val, action):

        #Card has colour, symbol, and action status
        self.colour = colour
        self.value = val
        self.action = action
        if self.action == "False":
            self.action = False
        else:
            self.action = True

    def show(self):

        if self.value == "ChangeColour":
            print("Wild")
        else:
            print("{} {}".format(self.colour, self.value))

class Player():

    def __init__(self, name, seat, cpu=True):

        self.name = name
        self.seat = seat
        self.hand = []
        self.cpu = cpu

    def draw(self, deck, n=1):

        #Number of cards from specified deck
        for i in range(n):
            self.hand.append(deck.drawCard())

    def showHand(self):

        #List of cards
        if self.cpu == False:
            print("Your hand: ({})".format(self.name))
        else:
            print("{}'s Hand:".format(self.name))
        report = ""
        for card in self.hand:
            whatCard = "{}.{} {}, ".format(self.hand.index(card)+1, card.colour, card.value)
            report += whatCard
        print(report[:-2])

    def play(self, deck, card):

        #Play card from hand to specified deck
        if self.cpu == False:
            print("{}, You play {} {} ({} cards left in hand)".format(self.name, card.colour, card.value, len(self.hand)-1))
        else:
            print("{} plays {} {} ({} cards left in hand)".format(self.name, card.colour, card.value, len(self.hand)-1))

        #If wild change the colour of card
        if card.colour == "Wild":
            newColour = random.choice(["Red", "Blue", "Green", "Yellow"])
            if self.cpu == False:

                while True:
                    print("{}, Select colour".format(self.name))
                    newColour = str(input("Select colour:")).capitalize()

                    if newColour in ["Red", "Blue", "Green", "Yellow"]:
                        print("You select {} ({})".format(newColour, self.name))
                        break
                    else:
                        print("Pick valid colour (Red, Blue, Green, Yellow)")
            else:
                print("{} selects {}".format(self.name, newColour))
            card.colour = newColour

        #Move card from hand to discard
        self.hand.remove(card)
        deck.cards.insert(0, card)

# In[]

#Sample test with friends
names = ["Brian", "Scott", "Vlad", "Oisin", "Kenny", "Ruairc", "Jossal", "Eoin", "Darren"]
Game(4 ,names, auto=False, n_players=1)
