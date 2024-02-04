import random

class Game:
    def __init__(self):
        self.players = []
        self.round = 1
        self.lives = 5

    def get_players(self):
        return self.players

    def add_player(self, player):
        self.players.append(player)

    def get_lives(self):
        return self.lives
    
    def lose_life(self):
        self.lives -= 1

    def earn_life(self):
        self.lives += 1

    def reset_game(self):
        self.players = []
        self.round = 1
        self.lives = 5

    def get_remaining_cards_amount(self):
        remaining_cards_amount = 0
        for player in self.players:
            remaining_cards_amount += len(player.get_deck())

        return remaining_cards_amount

    def deal_cards(self):
        full_deck = list(range(1, 101))  # Cartas del 1 al 100
        random.shuffle(full_deck)
        for player in self.players:
            cards_per_player = self.round
            player_deck = full_deck[:cards_per_player]  # Cortar el mazo según el número de cartas por jugador
            player.assign_deck(player_deck)
            full_deck = full_deck[cards_per_player:]  # Remover las cartas asignadas del mazo completo
    
    def get_lowest_card_in_round(self):
        lowest_card_in_round = 100
        for player in self.players:
            if player.get_lowest_card_in_deck() <= lowest_card_in_round:
                lowest_card_in_round = player.get_lowest_card_in_deck()
        return lowest_card_in_round

    async def play_round(self, current_player_id, ctx):
        current_player = None
        for player in self.players:
            if player.get_id() == current_player_id:
                current_player = player
                break

        if current_player is None:
            await ctx.send(f"<@{current_player_id}> no estás en la partida actual")
            return False

        card = current_player.play_card()
        if card is None:
            await ctx.send(f"<@{current_player_id}> no tienes cartas restantes en tu mazo")
            return False

        await ctx.send(f"<@{current_player_id}> soltó la carta: {card}")

        lowest_card_in_round = self.get_lowest_card_in_round()

        if card > lowest_card_in_round:
            self.lose_life()
            await ctx.send(f"`La carta más baja de la ronda era {lowest_card_in_round}\nLes quedan {self.lives} vidas 💔`")

        return True
