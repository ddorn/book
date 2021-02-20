import json
from collections import defaultdict
from operator import attrgetter, itemgetter
from pathlib import Path
from typing import Dict

import yaml

from models import *

DATA = Path(__file__).parent / "data"
DB_FILE = DATA / 'slots.yaml'
COMMANDES_FILE = DATA / 'commandes.csv'


def load_data() -> Dict[int, TimeSlotDB]:
    DB_FILE.touch()
    d = yaml.safe_load(DB_FILE.read_text() or '{}')
    return {k: TimeSlotDB(**v) for k, v in d.items()}


def save_data(slots):
    assert isinstance(slots, dict)
    DB_FILE.write_text(yaml.safe_dump({k: v.dict() for k, v in slots.items()}))


def new_id(slots):
    return max(slots, default=-1) + 1


def load_commandes():
    commandes = defaultdict(list)
    for line in COMMANDES_FILE.open():
        email, color, size, surname, name = line.split('\t')
        if email == "Email": continue
        commandes[email.lower()].append(
            CommandeDB(color=color,
                       size=size,
                       name=name,
                       surname=surname)
        )
    return commandes



def get(l, **kwargs):
    getters = [
        (attrgetter(key) if key[0] != '_' else itemgetter(key[1:]), value)
        for key, value in kwargs.items()
    ]
    for el in l:
        if all(getter(el) == value for getter, value in getters):
            return el
    return None


if __name__ == '__main__':
    pass
