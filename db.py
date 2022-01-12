import json
import os


class DB:
    __PREFS = 'prefs'
    __STATS = 'stats'

    @staticmethod
    def __get():
        with open("./db.json", "r") as f:
            data = json.loads(f.read())
        return data

    @staticmethod
    def __save(data):
        with open("./db.json", "w") as f:
            f.write(json.dumps(data))

    @staticmethod
    def iniciar():
        if not os.path.isfile('./db.json'):
            with open("./db.json", "w") as f:
                f.write("{}")

        data = DB.__get()
        if DB.__PREFS not in data:
            data[DB.__PREFS] = {}
        if DB.__STATS not in data:
            data[DB.__STATS] = {}
        DB.__save(data)

    @staticmethod
    def get_idioma(usuario):
        usuario = str(usuario)
        prefs = DB.__get()[DB.__PREFS]
        if usuario not in prefs:
            return "es", "es"
        u = prefs[usuario]
        return u['lang'], u['tld']

    @staticmethod
    def save_idioma(usuario, lang, tld):
        usuario = str(usuario)
        data = DB.__get()
        prefs = data[DB.__PREFS]
        prefs[usuario] = {'lang': lang, 'tld': tld}
        DB.__save(data)

    @staticmethod
    def save_estadistica(clip):
        data = DB.__get()
        stats = data[DB.__STATS]
        if clip not in stats:
            stats[clip] = 0
        stats[clip] += 1
        DB.__save(data)


class Admin:
    __ADMINS = 'admins'
    __BANS = 'bans'

    @staticmethod
    def __get():
        with open("./admin.json", "r") as f:
            data = json.loads(f.read())
        return data

    @staticmethod
    def __save(data):
        with open("./admin.json", "w") as f:
            f.write(json.dumps(data))

    @staticmethod
    def iniciar():
        if not os.path.isfile('./admin.json'):
            with open("./admin.json", "w") as f:
                f.write("{}")

        data = Admin.__get()
        if Admin.__ADMINS not in data:
            data[Admin.__ADMINS] = []
        if Admin.__BANS not in data:
            data[Admin.__BANS] = {}
        Admin.__save(data)

    @staticmethod
    def is_clip_banned_for_user(clip, guild, user):
        guild = str(guild)
        user = str(user)
        data = Admin.__get()
        bans = data[Admin.__BANS]
        if guild not in bans:
            return False
        g = bans[guild]
        if '_' in g and clip in g['_']:
            return True
        if user in g and clip in g[user]:
            return True
        return False

    @staticmethod
    def ban_clip(clip, guild, user):
        guild = str(guild)
        user = str(user)
        data = Admin.__get()
        bans = data[Admin.__BANS]
        if guild not in bans:
            bans[guild] = {}
        g = bans[guild]
        if user not in g:
            g[user] = []
        g[user].append(clip)
        Admin.__save(data)

    @staticmethod
    def unban_clip(clip, guild, user):
        guild = str(guild)
        user = str(user)
        data = Admin.__get()
        bans = data[Admin.__BANS]
        if guild not in bans:
            return
        g = bans[guild]
        if user not in g:
            return
        g[user].remove(clip)
        if len(g[user]) == 0:
            del g[user]
        if g == {}:
            del bans[guild]
        Admin.__save(data)

    @staticmethod
    def is_user_admin(user):
        user = str(user)
        data = Admin.__get()
        admins = data[Admin.__ADMINS]
        if user not in admins:
            return False
        return True

    @staticmethod
    def get_banned(guild):
        guild = str(guild)
        data = Admin.__get()
        bans = data[Admin.__BANS]
        if guild not in bans:
            return {}
        return bans[guild]
