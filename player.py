class Player:
    def __init__(self, player_id):
        self.id = player_id
        self.deck = []

    def get_id(self):
        return self.id

    def get_deck(self):
        return self.deck

    def assign_deck(self, deck):
        self.deck = sorted(deck)

    def get_lowest_card_in_deck(self):
        if self.deck:
            return min(self.deck)
        else:
            return float('inf')

    def play_card(self):
        if self.deck:
            return self.deck.pop(0)
        else:
            return None