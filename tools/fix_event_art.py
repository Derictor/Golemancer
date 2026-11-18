#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regenerate only Golemancer event illustrations after fixing opaque grain.

Usage (from mod root):
    python tools/fix_event_art.py
    python tools/fix_event_art.py --all

Creates a .bak copy of each existing image before overwriting it.
"""
import argparse
import os
import shutil

from generate_art import (
    EVENT_VERTICAL_DEFS,
    EVENT_WIDE_DEFS,
    IMG_ROOT,
    make_event_vertical,
    make_event_wide,
    save_img,
)

EVENT_NAME = "EV_A_OFICINA_NO_VALE"


def regenerate(definitions, suffix, maker, all_events):
    output_dir = os.path.join(IMG_ROOT, "Events")
    os.makedirs(output_dir, exist_ok=True)
    for name, title, subtitle, accent, seed in definitions:
        if not all_events and name != EVENT_NAME:
            continue
        filename = os.path.join(output_dir, name + suffix + ".png")
        if os.path.isfile(filename):
            backup = filename + ".bak"
            if not os.path.isfile(backup):
                shutil.copy2(filename, backup)
                print("Backup:", backup)
        save_img(maker(title, subtitle, accent, seed), filename)


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--all", action="store_true", help="Regenerate all event illustrations")
    args = parser.parse_args()
    regenerate(EVENT_VERTICAL_DEFS, "_Vertical", make_event_vertical, args.all)
    regenerate(EVENT_WIDE_DEFS, "_Wide", make_event_wide, args.all)
    print("Finished. Restart Thea 2 to reload the event images.")


if __name__ == "__main__":
    main()
