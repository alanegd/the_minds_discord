import discord
import responses
from discord.ext import commands
import asyncio
import game as g
import player as p
from security import TOKEN as t

lock = asyncio.Lock()

class MyBot(commands.Bot):
    def __init__(self, command_prefix, intents, **options):
        super().__init__(command_prefix, intents=intents, **options)
        self.game = g.Game()
        self.started = False

    async def wait_for_reaction(self, message, emoji, ctx, timeout=None):
        def check(reaction, user):
            return str(reaction.emoji) == emoji and user != self.user and reaction.message.id == message.id
        
        try:
            reaction, user = await self.wait_for('reaction_add', check=check, timeout=timeout)
            return user
        except asyncio.TimeoutError:
            return None

def run_discord_bot():
    TOKEN = t
    intents = discord.Intents.default()
    intents.message_content = True 
    bot = MyBot(command_prefix='antonieta ', intents=intents)

    async def send_message(message, user_message, is_private):
        try:
            response = responses.get_response(user_message)
            if response:
                await message.author.send(response) if is_private else await message.channel.send(response)
        except Exception as e:
            print(e)

    @bot.event
    async def on_ready():
        print(f'{bot.user} está activo')

    @bot.event
    async def on_message(message):
        if message.author == bot.user:
            return     
        await bot.process_commands(message) 
        username = str(message.author)
        user_message = str(message.content)
        channel = str(message.channel)
        print(f'{username} dijo: "{user_message}" ({channel})')
        await send_message(message, user_message, is_private=False)

    @bot.command()
    async def start(ctx):
        if bot.started:
            await ctx.send("`Error. Ya hay una partida en progreso`")
            return
        
        mensaje = await ctx.send("`El juego está por comenzar. Reacciona a este mensaje para participar`")
        await mensaje.add_reaction('🃏')
        await asyncio.sleep(20)
        await mensaje.edit(content="`El tiempo para unirse al juego ha terminado`")
        await mensaje.clear_reactions()

        bot.started = True

        amount_of_players = len(bot.game.get_players())
        print(f'Cantidad de jugadores: {amount_of_players}')
        if amount_of_players < bot.game.min_amount_of_players:
            await ctx.send("`Lo lamento, no hay suficientes jugadores como para comenzar`")
            return
        await play_round(ctx)


    async def play_round(ctx):
        async with lock:
            while bot.game.current_round <= bot.game.max_round and bot.game.get_lives() > 0:
                await ctx.send(f"\n`⊱ ───────── Ronda {bot.game.current_round} ───────── ⊰`\n")
                bot.game.deal_cards()

                for player in bot.game.get_players():
                    user = await bot.fetch_user(player.get_id())
                    if user:
                        player_deck = player.get_deck()
                        deck_image = await bot.game.compose_deck_image(player_deck)
                        
                        deck_image.save('images/player_deck.png')
                        await user.send(f"\nRonda {bot.game.current_round}\nTu mano: {player_deck}", file=discord.File('images/player_deck.png'))

                while bot.game.get_remaining_cards_amount() > 0 and bot.game.get_lives() > 0:
                    mensaje = await ctx.send("`Reacciona a este mensaje si crees que tienes la carta más baja`")
                    await mensaje.add_reaction('🧠')

                    user = await bot.wait_for_reaction(mensaje, '🧠', ctx, timeout=300)
                    if not user:
                        await stop(ctx)
                        return
                    await bot.game.play_round(user.id, ctx)

                await ctx.send(f"`Ronda {bot.game.current_round} finalizada`")
                if bot.game.current_round % 3 == 0:
                    bot.game.earn_life()
                    await ctx.send(f"`Ganaron una vida ❤️ extra por haber alcanzado el nivel {bot.game.current_round}`")
                bot.game.current_round += 1

            if bot.game.get_lives() < 1:
                await ctx.send("`Perdieron! Se quedaron sin vidas 🖤`")
            elif bot.game.current_round == bot.game.max_round:
                await ctx.send("`Ganaron!`")
            await stop(ctx)

    @bot.command()
    async def stop(ctx):
        if not bot.started:
            await ctx.send("`Error. No hay ninguna partida en progreso`")
            return
        bot.game.reset_game()
        bot.game.current_round = 1
        bot.started = False
        await ctx.send("`El juego ha finalizado`")

    @bot.command()
    async def vidas(ctx):
        if not bot.started:
            await ctx.send("`Error. No hay ninguna partida en progreso`")
            return
        await ctx.send(f"`Les quedan {bot.game.lives} vidas ❤️ restantes`")


    @bot.event
    async def on_reaction_add(reaction, user):
        mensaje = reaction.message
        if mensaje.content == "`El juego está por comenzar. Reacciona a este mensaje para participar`" and user != bot.user:
            player_id = user.id
            new_player = p.Player(player_id)
            bot.game.add_player(new_player)
        elif mensaje.content == "`Reacciona a este mensaje si crees que tienes la carta más baja`" and user != bot.user:
            await mensaje.delete()

    @bot.event
    async def on_reaction_remove(reaction, user):
        mensaje = reaction.message
        if mensaje.content == "`El juego está por comenzar. Reacciona a este mensaje para participar`" and user != bot.user:
            player_id = user.id
            
            # Verificar si el jugador ya está en la lista de jugadores y eliminarlo si es necesario
            for player in bot.game.get_players():
                if player.get_id() == player_id:
                    bot.game.get_players().remove(player)
                    break



    bot.run(TOKEN)

run_discord_bot()
