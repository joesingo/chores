#!/usr/bin/env python3
from __future__ import annotations

import argparse
import enum
import sys
import json

from csv import DictReader
from dataclasses import dataclass
from datetime import date, time, datetime, timedelta
from typing import Iterable, Tuple

DATE_FORMAT = "%d/%m/%Y"

class ParseError(Exception):
    pass

class Period(enum.Enum):
    DAY = enum.auto()
    WEEK = enum.auto()

    @classmethod
    def from_str(cls, s: str) -> Period:
        match s.lower():
            case "day" | "days":
                return cls.DAY
            case "week" | "weeks":
                return cls.WEEK
        raise ParseError(f"Invalid period '{s}'")

    def to_days(self) -> int:
        return 7 if self == Period.WEEK else 1

@dataclass
class Frequency:
    count: int
    period: Period

    @classmethod
    def from_str(cls, s: str) -> Frequency:
        match [w.strip() for w in s.lower().split(" ")]:
            case [count_str, period_str]:
                try:
                    count = int(count_str)
                except ParseError:
                    pass
                else:
                    return cls(count=count, period=Period.from_str(period_str))
        raise ParseError(f"Invalid frequency '{s}'")

    def to_timedelta(self) -> timedelta:
        return timedelta(days=self.count * self.period.to_days())

    def __str__(self) -> str:
        period_str = "week" if self.period == Period.WEEK else "day"
        if self.count == 1:
            return period_str
        elif self.count > 1:
            period_str += "s"  # Pluralise
        return f"{self.count} {period_str}"

@dataclass
class Chore:
    name: str
    frequency: Frequency
    next_due: date

    def __lt__(self, other: Chore) -> bool:
        """
        Sort by due date
        """
        def sort_key(c: Chore) -> Tuple[date, str, int]:
            return (c.next_due, c.name, hash(repr(c)))
        return sort_key(self) < sort_key(other)

class LastCompletedDb:
    def __init__(self, path: str):
        self.path = path

        with open(self.path) as f:
            data = json.load(f)

        if not isinstance(data, dict):
            raise ParseError("Invalid last completion JSON: expected object")

        self.data: dict[str, date] = {}
        for chore_name, date_str in data.items():
            if not isinstance(chore_name, str):
                raise ParseError(f"Invalid chore name: '{chore_name}'")
            try:
                date = datetime.strptime(date_str, DATE_FORMAT).date()
            except ValueError:
                raise ParseError(f"Invalid last completion date: '{date_str}'")
            self.data[chore_name] = date

    def __getitem__(self, key: str) -> date:
        return self.data[key]

    def complete(self, chore_name: str):
        self.data[chore_name] = datetime.now().date()

    def save(self):
        midnight = time(hour=0, minute=0)
        data: dict[str, str] = {
            chore_name: datetime.strftime(datetime.combine(date, midnight),
                                   DATE_FORMAT)
            for chore_name, date in self.data.items()
        }
        with open(self.path, "w") as f:
            json.dump(data, f)

def parse_chores(db: LastCompletedDb, chores_csv: Iterable[str]) \
        -> Iterable[Chore]:

    for i, row in enumerate(DictReader(chores_csv)):
        # Get columns
        try:
            name = row["name"]
            # Note: leading space, because I want to use a space after commas
            # for aesthetic reasons
            frequency_str = row[" frequency"]
        except KeyError as ex:
            raise ParseError(f"Missing column {ex}")

        if not name:
            raise ParseError(f"Empty name at line {i + 1}")
        if not frequency_str:
            raise ParseError(f"Empty frequency at line {i + 1}")

        name = name.strip()
        frequency = Frequency.from_str(frequency_str.strip())

        try:
            last_completed = db[name]
        except KeyError:
            # If a chore has never been completed, consider it due today
            next_due = datetime.now().date()
        else:
            next_due = last_completed + frequency.to_timedelta()

        yield Chore(name=name, frequency=frequency, next_due=next_due)

def main(args: argparse.Namespace):
    db = LastCompletedDb(args.last_completed_json)
    with open(args.chores_csv) as f:
        chores = sorted(list(parse_chores(db, f)))
    for chore in chores:
        print(chore)

    return 0

if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "chores_csv",
        help="Path to chores list CSV"
    )
    parser.add_argument(
        "last_completed_json",
        help="Path to JSON file containing last completion date for each chore"
    )

    args = parser.parse_args()
    try:
        main(args)
    except ParseError as ex:
        print(f"{parser.prog}: {ex}", file=sys.stderr)
        sys.exit(1)
    sys.exit(0)
