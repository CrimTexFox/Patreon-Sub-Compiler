"""Locate application data in both source checkouts and frozen builds."""
import sys
from pathlib import Path


def data_path(*parts):
    root = Path(sys._MEIPASS) if getattr(sys, "frozen", False) else Path(__file__).resolve().parents[1]
    return root.joinpath("data", *parts)
