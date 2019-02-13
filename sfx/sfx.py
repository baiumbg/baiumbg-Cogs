from redbot.core import commands, checks, data_manager, Config
import tempfile
import gtts
import discord
import asyncio
import os
import random
import lavalink
import pydub
import aiohttp

class SFX(commands.Cog):
    """Play uploaded sounds or text-to-speech using gTTS"""

    def __init__(self):
        self.tts_languages = list(gtts.lang.tts_langs().keys())
        self.last_track_info = None
        self.current_sfx = None
        self.config = Config.get_conf(self, identifier=134621854878007296)
        self.sound_base = (data_manager.cog_data_path(self) / 'sounds').as_posix()
        self.session = aiohttp.ClientSession()
        default_config = {
            'tts': {
                'lang': 'en',
                'padding': 700
            },
            'sfx': {
                'sounds': {}
            }
        }
        self.config.register_guild(**default_config)
        lavalink.register_event_listener(self.ll_check)
        if not os.path.exists(self.sound_base):
            os.makedirs(self.sound_base)


    def __unload(self):
        lavalink.unregister_event_listener(self.ll_check)


    @commands.command(usage='[language code] <text>')
    async def tts(self, ctx, *, text):
        """
        Text-to-speech

        Turns a string of text into audio using the server's default language, if none is specified.
        Use `[p]ttslangs` for a list of valid language codes.
        """

        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send('You are not connected to a voice channel.')
            return

        tts_config = await self.config.guild(ctx.guild).tts()
        lang = tts_config['lang']
        try:
            lang, text = text.split(' ', maxsplit=1)
            if lang not in self.tts_languages:
                lang = tts_config['lang']
                text = f'{lang} {text}'
        except ValueError:
            pass

        tts_audio = gtts.gTTS(text, lang=lang)
        audio_file = os.path.join(tempfile.gettempdir(), ''.join(random.choice('0123456789ABCDEF') for i in range(12)) + '.mp3')
        tts_audio.save(audio_file)
        audio_data = pydub.AudioSegment.from_mp3(audio_file)
        silence = pydub.AudioSegment.silent(duration=tts_config['padding'])
        padded_audio = silence + audio_data + silence
        padded_audio.export(audio_file, format='mp3')
        await self._play_sfx(ctx.author.voice.channel, audio_file)

    @commands.group(name='ttsconfig')
    async def ttsconfig(self, ctx):
        """Configure TTS"""
        pass

    @ttsconfig.command(name='lang', usage='[language code]')
    @checks.guildowner()
    async def _tts_lang(self, ctx, *args):
        """
        Configure the default TTS language

        Gets/sets the default language for the `[p]tts` command.
        Use `[p]ttslangs` for a list of language codes.
        """

        tts_config = await self.config.guild(ctx.guild).tts()
        if len(args) == 0:
            await ctx.send(f"Current value of `lang`: {tts_config['lang']}")
            return

        lang = args[0]
        if lang not in self.tts_languages:
            await ctx.send('Invalid langauge. Use [p]ttsconfig langlist for a list of languages.')
            return

        tts_config['lang'] = lang
        await self.config.guild(ctx.guild).tts.set(tts_config)
        await ctx.send(f'`lang` set to {lang}.')


    @ttsconfig.command(name='padding', usage='<duration>')
    @checks.guildowner()
    async def _tts_padding(self, ctx, *args):
        """
        Configure the default TTS padding

        Gets/sets the default duration of padding (in ms) for the `[p]tts` command.
        Adjust if the sound gets cut off at the beginning or the end.
        """

        tts_config = await self.config.guild(ctx.guild).tts()
        if len(args) == 0:
            await ctx.send(f"Current value of `padding`: {tts_config['padding']}")
            return

        padding = 0
        try:
            padding = int(args[0])
        except ValueError:
            await ctx.send_help()
            return

        tts_config['padding'] = padding
        await self.config.guild(ctx.guild).tts.set(tts_config)
        await ctx.send(f'`padding` set to {padding}.')

    @commands.command(name='ttslangs')
    async def _tts_lang_list(self, ctx):
        """
        List of TTS Languages

        Prints the list of valid languages for use with `[p]tts`.
        """

        await ctx.send(f"List of valid languages: {', '.join(self.tts_languages)}")

    @commands.command()
    async def sfx(self, ctx, soundname: str):
        if not ctx.author.voice or not ctx.author.voice.channel:
            await ctx.send('You are not connected to a voice channel.')
            return

        if str(ctx.guild.id) not in os.listdir(self.sound_base):
            os.makedirs(os.path.join(self.sound_base, str(ctx.guild.id)))

        sfx_config = await self.config.guild(ctx.guild).sfx()
        if soundname not in sfx_config['sounds'].keys():
            await ctx.send(f'Sound `{soundname}` does not exist. Try `{ctx.prefix}allsfx` for a list.')
            return

        filepath = os.path.join(self.sound_base, str(ctx.guild.id), sfx_config['sounds'][soundname])
        if not os.path.exists(filepath):
            del sfx_config['sounds'][soundname]
            await self.config.guild(ctx.guild).sfx.set(sfx_config)
            await ctx.send('Looks like this sound\'s file has gone missing! I\'ve removed it from the list of sounds.')
            return

        await self._play_sfx(ctx.author.voice.channel, filepath)

    @commands.command()
    async def addsfx(self, ctx, name: str, link: str=None):
        sfx_config = await self.config.guild(ctx.guild).sfx()

        if str(ctx.guild.id) not in os.listdir(self.sound_base):
            os.makedirs(os.path.join(self.sound_base, str(ctx.guild.id)))

        attach = ctx.message.attachments
        if len(attach) > 1 or (attach and link):
            await ctx.send('Please only add one sound at a time.')
            return

        url = ''
        filename = ''
        if attach:
            a = attach[0]
            url = a.url
            filename = a.filename
        elif link:
            url = ''.join(link)
            filename = os.path.basename(
                '_'.join(url.split()).replace('%20', '_'))
        else:
            await ctx.send('You must provide either a Discord attachment or a direct link to a sound.')
            return

        filepath = os.path.join(self.sound_base, str(ctx.guild.id), filename)

        if name in sfx_config['sounds'].keys():
            await ctx.send('A sound with that name already exists. Please choose another name and try again.')
            return

        if os.path.exists(filepath):
            await ctx.send('A sound with that filename already exists. Please change the filename and try again.')
            return

        async with self.session.get(url) as new_sound:
            f = open(filepath, 'wb')
            f.write(await new_sound.read())
            f.close()

        sfx_config['sounds'][name] = filename
        await self.config.guild(ctx.guild).sfx.set(sfx_config)

        await ctx.send(f'Sound {name} added.')

    @commands.command()
    async def delsfx(self, ctx, soundname: str):
        """Deletes an existing sound."""

        if str(ctx.guild.id) not in os.listdir(self.sound_base):
            os.makedirs(os.path.join(self.sound_base, str(ctx.guild.id)))

        sfx_config = await self.config.guild(ctx.guild).sfx()

        if soundname not in sfx_config['sounds'].keys():
            await ctx.send(f'Sound `{soundname}` does not exist. Try `{ctx.prefix}allsfx` for a list.')
            return

        filepath = os.path.join(self.sound_base, str(ctx.guild.id), sfx_config['sounds'][soundname])

        if os.path.exists(filepath):
            os.remove(filepath)

        del sfx_config['sounds'][soundname]
        await self.config.guild(ctx.guild).sfx.set(sfx_config)

        await ctx.send(f'Sound {soundname} deleted.')

    @commands.command()
    async def allsfx(self, ctx):
        """Prints all available sounds for this server."""

        if str(ctx.guild.id) not in os.listdir(self.sound_base):
            os.makedirs(os.path.join(self.sound_base, str(ctx.guild.id)))

        sfx_config = await self.config.guild(ctx.guild).sfx()

        if len(sfx_config['sounds'].items()) == 0:
            await ctx.send(f'No sounds found. Use `{ctx.prefix}addsfx` to add one.')
            return

        paginator = discord.ext.commands.formatter.Paginator()
        for soundname, filepath in sfx_config['sounds'].items():
            paginator.add_line(soundname)

        await ctx.send('Sounds for this server:')
        for page in paginator.pages:
            await ctx.send(page)

    @commands.command(no_pm=True, pass_context=True, aliases=['getsound'])
    async def getsfx(self, ctx, soundname: str):
        """Gets the given sound."""

        if str(ctx.guild.id) not in os.listdir(self.sound_base):
            os.makedirs(os.path.join(self.sound_base, str(ctx.guild.id)))

        sfx_config = await self.config.guild(ctx.guild).sfx()

        if soundname not in sfx_config['sounds'].keys():
            await ctx.send(f'Sound `{soundname}` does not exist. Try `{ctx.prefix}allsfx` for a list.')
            return

        filepath = os.path.join(self.sound_base, str(ctx.guild.id), sfx_config['sounds'][soundname])
        if not os.path.exists(filepath):
            del sfx_config['sounds'][soundname]
            await self.config.guild(ctx.guild).sfx.set(sfx_config)
            await ctx.send('Looks like this sound\'s file has gone missing! I\'ve removed it from the list of sounds.')
            return

        await ctx.send(file=discord.File(filepath))

    async def _play_sfx(self, vc, filepath):
        player = await lavalink.connect(vc)
        track = (await player.get_tracks(query=filepath))[0]

        if player.current is None:
            player.queue.append(track)
            self.current_sfx = track
            await player.play()
            return

        if self.current_sfx is not None:
            player.queue.insert(0, track)
            await player.skip()
            os.remove(self.current_sfx.uri)
            self.current_sfx = track
            return

        self.last_track_info = (player.current, player.position)
        self.current_sfx = track
        player.queue.insert(0, track)
        player.queue.insert(1, player.current)
        await player.skip()

    async def ll_check(self, player, event, reason):
        if self.current_sfx is None and self.last_track_info is None:
            return

        if event == lavalink.LavalinkEvents.TRACK_EXCEPTION and self.current_sfx is not None:
            os.remove(self.current_sfx.uri)
            self.current_sfx = None
            return

        if event == lavalink.LavalinkEvents.TRACK_STUCK and self.current_sfx is not None:
            os.remove(self.current_sfx.uri)
            self.current_sfx = None
            await player.skip()
            return

        if event == lavalink.LavalinkEvents.TRACK_END and player.current is None and self.current_sfx is not None:
            os.remove(self.current_sfx.uri)
            self.current_sfx = None
            return

        if event == lavalink.LavalinkEvents.TRACK_END and player.current.track_identifier == self.last_track_info[0].track_identifier:
            print(str(self.last_track_info[0].uri))
            os.remove(self.current_sfx.uri)
            self.current_sfx = None
            await player.pause()
            await player.seek(self.last_track_info[1])
            await player.pause(False)
            self.last_track_info = None