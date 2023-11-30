"""Alle Bahnhöfe der Betriebsanlage."""
from enum import Enum


class Bhf(Enum):
    """Enum trainstations."""

    DAB = "Dachsburg"
    ENS = "Ensikon"
    CHA = "Charrat"
    GER = "Gerau"
    FUS = "Fusio"
    BLO = "Bloney"
