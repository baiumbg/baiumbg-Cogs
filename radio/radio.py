import discord
import urllib
import json
from discord.ext import commands

class RadioPlayer:
    def __init__(self, bot):
        self.bot = bot
        self.voice_client = None
        self.stream = None

        try:
            with open('stations.json', "r") as stations_file:
                self.stations = json.load(stations_file)
        except FileNotFoundError:
            open('stations.json', 'w')
            self.stations = {}

    @commands.group(pass_context=True, no_pm=True)
    async def radio(self, ctx):
        """Adds/removes radio stations and controls the radio player"""
        if ctx.invoked_subcommand is None:
            await self.bot.send_cmd_help(ctx)

    @radio.command(pass_context=True)
    async def add(self, ctx, name: str, url: str):
        """Adds a station to the list of known stations"""
        if name in self.stations.keys():
            await self.bot.say("There already is a station with that name in the list!")
        else:
            self.stations[name] = url
            with open('stations.json', "w") as stations_file:
                json.dump(self.stations, stations_file)
                await self.bot.say("Station added!")

    @radio.command(pass_context=True)
    async def remove(self, ctx, name: str):
        """Removes a station from the list"""
        if name not in self.stations.keys():
            await self.bot.say("No such station in the list!")
        else:
            self.stations.pop(name)
            await self.bot.say("Station removed!")

    @radio.command(pass_context=True)
    async def list(self, ctx):
        """Lists all available stations"""
        output = "**Name: URL**\n"
        for name, url in self.stations.items():
            output += "{}: {}\n".format(name, url)
        await self.bot.say(output)

    @radio.command(pass_context=True)
    async def play(self, ctx, name: str):
        """Plays a station by its name"""
        if name not in self.stations.keys():
            self.bot.say("Station not found!")
            return

        server = ctx.message.server
        uvc = ctx.message.author.voice.voice_channel
        url = self.stations[name]
        if self.bot.is_voice_connected(server):
            await self.bot.voice_client_in(server).disconnect()
        self.voice_client = await self.bot.join_voice_channel(
            uvc)
        self.stream = urllib.request.urlopen(url)
        self.voice_client.audio_player = self.voice_client.create_ffmpeg_player(self.stream, pipe=True)
        self.voice_client.audio_player.start()

    @radio.command(pass_context=True)
    async def stop(self, ctx):
        """Stops radio playback"""
        if self.voice_client.audio_player.is_playing():
            self.voice_client.audio_player.stop()


def setup(bot):
    bot.add_cog(RadioPlayer(bot))
