# -*- coding: utf-8 -*-
"""Who every handle and name belongs to, shared by mkhtml.py and check.py.

For each season: an anchor (the row in The-Scene-Characters.md, published as
#s<season>-<anchor>), then every handle and name that means that character.
Longer spellings are tried first, so a full Jabber ID wins over the bare nick
inside it. Season 2 mostly calls people by name, so names are here as well as
handles.
"""
import re

HANDLES = {
    1: [('drosan', ['BrianSan333', 'BrianSan', 'dro_5544', 'brian.sandro@gmail.com',
                    'Brian Sandro', 'Brian', 'Drosan']),
        ('teflon', ['monticello222@yahoo.com', 'monticello222', 'monticello235', 'copleyr785',
                    'collangello998', 'spinnaker', 'Edward G. Koenig', 'Koenig', 'teflon']),
        ('trooper', ['troopercamy0@yahoo.com', 'troopercamy', 'trooper', 'Jodi']),
        ('pyr0', ['pyr0']),
        ('slipknot', ['slipknot']),
        ('coda', ['cOda']),
        ('melissa', ['melissbliss04', 'Melissa']),
        ('dana', ['danaburke123', 'danaburke55', 'Dana Burke', 'Dana']),
        ('todd', ['Tremor2212', 'Todd']),
        ('suzy', ['suzyxiao', 'Suzy']),
        ('luckychi', ['LuckyChi2203', 'Lucky Chi', 'luckychi']),
        ('gryffin', ['gryffin', 'Timothy Brudiger', 'Brudiger']),
        ('burroughs', ['burroughs485', 'Burroughs', 'burroughs']),
        ('agents', ['brenner2604', 'alanmeans06']),
        ('chris', ['chOppr998', 'Chris']),
        ('badger', ['r3dbadg3r'])],
    2: [('danika', ['houdini6@jabber.org', 'houdini6', 'DanikaLi99', 'sng330', 'lukai', 'Danika']),
        ('talisman', ['talisman']),
        ('t0mb0', ['t0mb0@jabber.org', 't0mb0', 'tombo', 'Tomasz']),
        ('stan', ['tann3r@jabber.org', 'tann3r', 'Stan']),
        ('murph', ['t!nman@jabber.org', 't!nman', 'spartan', 'Murph']),
        ('ralph', ['jimbrandon09@jabber.org', 'jimbrandon09', 'Ralph Lasky', 'Jim Brandon',
                   'jim brandon', 'Ralph']),
        ('mike', ['MikeyD5550', 'Mike Davis', 'Mike']),
        ('katerina', ['Katerina']),
        ('vicky', ['Vicky', 'vicky']),
        ('zhen', ['bellbird', 'zheng', 'Zhen', 'zhen']),
        ('greenberg', ['Greenberg']),
        ('cunningham', ['michaelrcunningham5@gmail.com', 'Michael Cunningham', 'Cunningham']),
        ('laurent', ['jlaurent@bbvabankltd.ch', 'J. Laurent']),
        ('weichang', ['Wei Chang', 'wei chang'])],
}

INDEX = 'The-Scene-Characters.html'

# A handle is a whole token: not glued to a word, an address or a leet "!".
BOUND = r'(?<![\w@.!])(%s)(?![\w@])'


def handle_re(season):
    """One regex for every spelling in a season, and spelling -> anchor."""
    alts = sorted(((h, a) for a, hs in HANDLES[season] for h in hs), key=lambda x: -len(x[0]))
    return re.compile(BOUND % '|'.join(re.escape(h) for h, _ in alts)), dict(alts)


def anchor_for(cell):
    """The (season, anchor) whose spellings appear in a table cell, if any."""
    for season in (1, 2):
        for anchor, hs in HANDLES[season]:
            if re.search(BOUND % '|'.join(map(re.escape, hs)), cell):
                return season, anchor
    return None
