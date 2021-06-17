import re
import settings


class Checks:
    max_number = 9223372036854775807
    modules_list = ['allow-spam', 'restart-error', 'emote-react', 'recover-mode', 'post-embed']

    def __init__(self, ctx=None):
        self.ctx = ctx

    @staticmethod
    def prefix(prefix):
        new_prefix = re.sub(r'[^A-Za-z!~,.<>^/$%=+-]', '', prefix)

        if new_prefix == prefix:
            return prefix
        else:
            return settings.default_prefix

    def count(self, number, maxnumber):
        try:
            number = int(number)
        except Exception:
            return 0

        maxnumber = self.maxcount(maxnumber)

        if maxnumber == -1:
            maxnumber = self.max_number

        if maxnumber > number > 0:
            return number
        else:
            return 0

    def maxcount(self, number):
        max_count = -1

        try:
            number = int(number)
        except Exception:
            pass

        if number == -1:
            max_count = number
        elif 0 < number <= self.max_number:
            max_count = number

        return max_count

    @staticmethod
    def ids(ids):
        if ids > 0:
            return ids
        else:
            return 0

    def id_in_guild(self, ids, guild_id):
        ids = self.ids(ids)

        id_is_in_guild = 0

        if self.ctx is not None:
            if self.ctx.guild.id == guild_id:
                id_is_in_guild = ids

        return id_is_in_guild

    def modules(self, modules):
        new_modules = []

        if modules['allow-spam'] == 1 and modules['emote-react'] == 1:
            modules['emote-react'] = 0
        elif modules['emote-react'] == 1 and self.ctx.guild.member_count > 500:
            modules['emote-react'] = 0

        for module in self.modules_list:
            try:
                new_modules.append(int(modules[module]))
            except Exception:
                new_modules.append(0)

        return new_modules
