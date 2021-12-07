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
