import os
import sqlite3
from contextlib import closing
from decimal import Decimal, InvalidOperation, ROUND_CEILING, ROUND_FLOOR
from pathlib import Path


BUDGET_PATH = Path.home() / '.local/state/yamalemma/hosted-budget.sqlite3'


class BudgetError(RuntimeError):
    pass


def microdollars(value, rounding=ROUND_CEILING):
    try:
        amount = Decimal(str(value))
        if not amount.is_finite() or amount < 0 or amount > 1000000:
            raise ValueError('budget amount must be finite and between zero and one million dollars')
        return int((amount * 1000000).to_integral_value(rounding=rounding))
    except InvalidOperation as error:
        raise ValueError('invalid budget amount') from error


def initialize_budget(max_calls=3, max_cost_usd=0.25, initial_calls=0, initial_reserved_usd=0):
    cap = microdollars(max_cost_usd, ROUND_FLOOR)
    reserved = microdollars(initial_reserved_usd)
    if type(max_calls) is not int or not 1 <= max_calls <= 10000:
        raise ValueError('shared call limit must be between 1 and 10000')
    if type(initial_calls) is not int or not 0 <= initial_calls <= max_calls or reserved > cap:
        raise ValueError('historical reservations exceed the shared budget')
    path = BUDGET_PATH
    path.parent.mkdir(parents=True, exist_ok=True, mode=0o700)
    try:
        descriptor = os.open(path, os.O_CREAT | os.O_EXCL | os.O_WRONLY, 0o600)
    except FileExistsError as error:
        raise BudgetError('shared budget already exists; initialization cannot reset it') from error
    os.close(descriptor)
    with closing(sqlite3.connect(path)) as connection, connection:
        connection.execute('CREATE TABLE budget (id INTEGER PRIMARY KEY CHECK (id = 1), version INTEGER NOT NULL, max_calls INTEGER NOT NULL, cap INTEGER NOT NULL, calls INTEGER NOT NULL, reserved INTEGER NOT NULL)')
        connection.execute('CREATE TABLE reservations (id INTEGER PRIMARY KEY, request_key TEXT NOT NULL, amount INTEGER NOT NULL, created TEXT NOT NULL DEFAULT CURRENT_TIMESTAMP)')
        connection.execute('INSERT INTO budget VALUES (1, 1, ?, ?, ?, ?)', (max_calls, cap, initial_calls, reserved))
        if initial_calls or reserved:
            connection.execute('INSERT INTO reservations (request_key, amount) VALUES (?, ?)', ('historical-import', reserved))
    return budget_status()


def connect_budget():
    try:
        return sqlite3.connect(BUDGET_PATH.resolve().as_uri() + '?mode=rw', uri=True, timeout=10)
    except sqlite3.Error as error:
        raise BudgetError('shared budget unavailable; initialize it with yamalemma budget-init before hosted calls') from error


def read_budget(connection):
    rows = connection.execute('SELECT version, max_calls, cap, calls, reserved FROM budget').fetchall()
    if len(rows) != 1:
        raise BudgetError('invalid shared budget')
    version, max_calls, cap, calls, reserved = rows[0]
    if any(type(value) is not int for value in rows[0]) or version != 1 or not 1 <= max_calls <= 10000 or not 0 <= calls <= max_calls or not 0 <= reserved <= cap <= 1000000000000:
        raise BudgetError('invalid shared budget')
    return {'max_calls': max_calls, 'calls': calls, 'remaining_calls': max_calls - calls,
            'max_cost_usd': cap / 1000000, 'reserved_usd': reserved / 1000000,
            'remaining_usd': (cap - reserved) / 1000000}


def budget_status():
    try:
        with closing(connect_budget()) as connection:
            return read_budget(connection)
    except sqlite3.Error as error:
        raise BudgetError('shared budget is unreadable; hosted calls are blocked') from error


def change_budget_limits(max_calls, max_cost_usd):
    cap = microdollars(max_cost_usd, ROUND_FLOOR)
    if type(max_calls) is not int or not 1 <= max_calls <= 10000:
        raise ValueError('shared call limit must be between 1 and 10000')
    try:
        with closing(connect_budget()) as connection, connection:
            connection.execute('BEGIN IMMEDIATE')
            read_budget(connection)
            updated = connection.execute('UPDATE budget SET max_calls = ?, cap = ? WHERE id = 1 AND calls <= ? AND reserved <= ?', (max_calls, cap, max_calls, cap))
            if updated.rowcount != 1:
                raise ValueError('new limits cannot be below existing usage')
            return read_budget(connection)
    except sqlite3.Error as error:
        raise BudgetError('shared budget limits could not be updated') from error


def reserve_hosted(amount, request_key):
    amount = microdollars(amount)
    try:
        with closing(connect_budget()) as connection, connection:
            connection.execute('BEGIN IMMEDIATE')
            read_budget(connection)
            updated = connection.execute('UPDATE budget SET calls = calls + 1, reserved = reserved + ? WHERE id = 1 AND calls < max_calls AND reserved + ? <= cap', (amount, amount))
            if updated.rowcount != 1:
                return None
            receipt = connection.execute('INSERT INTO reservations (request_key, amount) VALUES (?, ?)', (request_key, amount))
            return receipt.lastrowid
    except sqlite3.Error as error:
        raise BudgetError('shared budget reservation failed; hosted call blocked') from error
