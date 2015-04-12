# -*- coding: utf-8 -*-
from __future__ import absolute_import, division, print_function, \
                       with_statement

import sqlite3
from hashlib import sha256


class User(object):

    """docstring for user"""

    def __init__(self, dbfile):
        assert dbfile is not None
        self._conn = sqlite3.connect(dbfile)

    def db_init(self):
        """Initialize the sqlite3 database."""
        sql = ("CREATE TABLE IF NOT EXISTS users ( "
               "    id INTEGER PRIMARY KEY AUTOINCREMENT, "
               "    username NOT NULL UNIQUE, "
               "    password NOT NULL)")
        self._conn.execute(sql)
        self._conn.commit()

    def db_truncate(self, reset_id=False):
        """Truncate the sqlite3 database."""
        self._conn.execute("DELETE FROM users")
        if reset_id:
            sql = "UPDATE sqlite_sequence SET seq=0 WHERE name='users'"
            self._conn.execute(sql)
        self._conn.execute("VACUUM")
        self._conn.commit()

    def db_compact(self):
        self._conn.execute("VACUUM")
        self._conn.commit()

    def id(self, username):
        """Get the id by username."""
        assert username is not None

        sql_fmt = "SELECT id FROM users WHERE username=?"
        sql_args = (username,)
        c = self._conn.execute(sql_fmt, sql_args)
        return c.fetchone()[0]

    def add(self, username, password):
        """Add a user by username and password."""
        assert username is not None and password is not None

        password = self._hexdigest_password(password)
        sql_fmt = "INSERT INTO users (username, password) VALUES(?, ?)"
        sql_args = (username, password)
        try:
            self._conn.execute(sql_fmt, sql_args)
        except sqlite3.OperationalError:
            self._conn.rollback()
        finally:
            self._conn.commit()

    def delete(self, username):
        """Delete a user by username."""
        assert username is not None

        sql_fmt = "DELETE FROM users WHERE username=?"
        sql_args = (username,)
        self._conn.execute(sql_fmt, sql_args)
        self._conn.commit()

    def passwd(self, id, username=None, password=None):
        """Update username or password by id."""
        assert id is not None

        if password is not None:
            password = self._hexdigest_password(password)
        if username is not None and password is not None:
            sql_fmt = "UPDATE users SET username=?, password=? WHERE id=?"
            sql_args = (username, password, id)
        elif username is not None:
            sql_fmt = "UPDATE users SET username=? WHERE id=?"
            sql_args = (username, id)
        elif password is not None:
            sql_fmt = "UPDATE users SET password=? WHERE id=?"
            sql_args = (password, id)
        self._conn.execute(sql_fmt, sql_args)
        self._conn.commit()

    def find(self, id=None, username=None, password=None):
        """
        Find user by one or more conditions.
        It returns True on success, or False on fault.

        The three arguments MUST NOT be None at the same time.
        """
        assert id is not None or username is not None or password is not None

        if password is not None:
            password = self._hexdigest_password(password)
        sql_fmt = sql_args = None
        """
        `-` means None
        `X` means not None

        | id | username | password |
        |----|----------|----------|
        | -  |    X     |    X     | condition 1
        | -  |    X     |    -     | condition 2
        | -  |    -     |    X     | condition 3
        | X  |    X     |    X     | condition 4
        | X  |    X     |    -     | condition 5
        | X  |    -     |    X     | condition 6
        | X  |    -     |    -     | condition 7
        """
        # condition 1
        if id is None and username is not None and password is not None:
            sql_fmt = "SELECT id \
                       FROM users \
                       WHERE username=? AND password=?"
            sql_args = (username, password)
        # condition 2
        elif id is None and username is not None and password is None:
            sql_fmt = "SELECT id \
                       FROM users \
                       WHERE username=?"
            sql_args = (username,)
        # condition 3
        elif id is None and username is None and password is not None:
            sql_fmt = "SELECT id \
                       FROM users \
                       WHERE password=?"
            sql_args = (password,)
        # condition 4
        elif id is not None and password is not None and password is not None:
            sql_fmt = "SELECT id \
                       FROM users \
                       WHERE id=? AND username=? AND password=?"
            sql_args = (id, username, password)
        # condition 5
        elif id is not None and username is not None and password is None:
            sql_fmt = "SELECT id \
                       FROM users \
                       WHERE id=? AND username=?"
            sql_args = (id, username)
        # condition 6
        elif id is not None and password is None and password is not None:
            sql_fmt = "SELECT id \
                       FROM users \
                       WHERE id=? AND password=?"
            sql_args = (id, password)
        # condition 7
        elif id is not None and password is None and password is None:
            sql_fmt = "SELECT id \
                       FROM users \
                       WHERE id=?"
            sql_args = (id,)
        assert(sql_fmt is not None)
        assert(sql_args is not None)

        cur = self._conn.cursor()
        cur.execute(sql_fmt, sql_args)
        if cur.fetchone() is None:
            return False
        else:
            return True

    @property
    def count(self):
        """Returns the row count of table users."""
        return self._conn.execute("SELECT COUNT(id) FROM users").fetchone()[0]

    def _hexdigest_password(self, password):
        assert password is not None

        return sha256(password.encode('utf8')).hexdigest()

    def dump(self, full=True):
        def make_header(maxlen_id, maxlen_username, maxlen_password):
            fmt = "| {:^%s} | {:^%s} | {:^%s} |\n" % (
                max(2, maxlen_id), max(8, maxlen_username),
                max(8, maxlen_password))
            s = fmt.format("id", "username", "password")
            fmt = "|-{:-^%s}-|-{:-^%s}-|-{:-^%s}-|" % (
                max(2, maxlen_id), max(8, maxlen_username),
                max(8, maxlen_password))
            s += fmt.format("", "", "")
            return s

        sql = "SELECT MAX(LENGTH(id)), MAX(LENGTH(username)), \
               MAX(LENGTH(password)) FROM users"
        r = self._conn.execute(sql).fetchone()
        maxlen_id, maxlen_username, maxlen_password = r

        sql = "SELECT id, username, password FROM users"
        if full:
            retval = make_header(maxlen_id, maxlen_username, maxlen_password)
            for row in self._conn.execute(sql):
                retval += "\n| %2s | %-8s | %8s |" % row
        else:
            retval = make_header(maxlen_id, maxlen_username, 19)
            for row in self._conn.execute(sql):
                retval += "\n| %2s | %-8s | %8s |" % (
                    row[0], row[1],
                    row[2][:8] + "..." + row[2][len(row[2]) - 8:])

        return retval


def test():
    u = user("test.db")

    u.db_init()
    u.db_truncate()

    print(">>>>>>>>>> testing add() <<<<<<<<<<")
    u.add("user1", "password1")
    u.add("user2", "password2")
    u.add("user3", "password3")
    u.add("user4", "password4")
    u.add("user5", "password5")
    u.add("user6", "password6")
    print(u.dump(full=False))

    print(">>>>>>>>>> testing id() <<<<<<<<<<")
    print("u.id(\"user3\")=", u.id("user3"))
    print("u.id(\"user6\")=", u.id("user6"))

    print(" >>>>>>>>>> testing delete() <<<<<<<<<<")
    u.delete("user5")
    print(u.dump(full=False))

    print(">>>>>>>>>> testing passwd() <<<<<<<<<<")
    u.passwd(1, username="USER2")
    u.passwd(2, password="a new password")
    u.passwd(3, username="USER3", password="a new password")
    print(u.dump(full=False))
    print(u.dump(full=True))

    print(">>>>>>>>>> testing find() <<<<<<<<<<")
    print("u.find(id=2)=", u.find(id=2))
    print("u.find(id=12)=", u.find(id=12))
    print("u.find(username=\"user3\")=", u.find(username="user3"))
    print("u.find(username=\"USER3\")=", u.find(username="USER3"))
    print("u.find(username=\"USER3\", password=\"password3\")=",
          u.find(username="USER3", password="password3"))
    print("u.find(username=\"USER3\", password=\"a new password\")=",
          u.find(username="USER3", password="a new password"))


if __name__ == "__main__":
    test()

# vim: tw=78 ts=8 et sw=4 sts=4 fdm=indent
