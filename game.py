import random
import discord
from PIL import Image

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
        
        deck_image = await self.compose_deck_image([card])
                        
        deck_image.save('images/player_deck.png')

        await ctx.send(f"<@{current_player_id}> soltó la carta: {card}", file=discord.File('images/player_deck.png'))

        lowest_card_in_round = self.get_lowest_card_in_round()

        if card > lowest_card_in_round:
            self.lose_life()
            await ctx.send(f"`La carta más baja de la ronda era {lowest_card_in_round}\nLes quedan {self.lives} vidas 💔`")

        return True
    
    async def compose_deck_image(self, player_deck):
        deck_image = Image.new('RGBA', (132 * len(player_deck), 169), (255, 255, 255, 255)) # Crea canvas vacío donde pegar las cartas
        
        for i, card_number in enumerate(player_deck):
            card_image = await self.extract_card_image(card_number)
            if card_image:
                deck_image.paste(card_image, (i * 132, 0))
        
        return deck_image

    async def extract_card_image(self, card_number):
        try:
            spritesheet = Image.open('images/numbers.png')
            x_offset = 0
            y_offset = (card_number - 1) * 169
            card_image = spritesheet.crop((x_offset, y_offset, x_offset + 132, y_offset + 169))
            return card_image
        except Exception as e:
            print(f"Error al abrir la imagen de la carta {card_number}: {e}")
            return None