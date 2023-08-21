"""
Class for assisting to build dynamic raw SQL queries.

Usage
-----
::

    sql = RawSQLBuilder()
    sql.add('''
        SELECT *
          FROM my_table
    ''')

    sql.add_if(type, '''
        WHERE type=%s
    ''', [type])

    with sql.execute() as cursor:
        return cursor.fetchall()
"""
from django.db import connections, connection as django_default_connection


class RawSQLBuilder:
    def __init__(self, connection=None):
        if isinstance(connection, str):
            connection = connections[connection]
        self._connection = connection or django_default_connection
        self._sql_parts = []
        self._params = []

    def add(self, sql, params=None):
        self.add_if(True, sql, params)

    def add_if(self, condition_expr, sql, params=None):
        if condition_expr:
            self._sql_parts.append(sql)
            if params:
                self._params.extend(params)

    def get_sql(self):
        return ("\n".join(self._sql_parts), self._params)

    def execute(self):
        cursor = self._connection.cursor()
        cursor.execute(*self.get_sql())
        return cursor

    @staticmethod
    def columns(cursor):
        desc = cursor.description
        return [col[0] for col in desc]

    @staticmethod
    def dictfetchall(cursor):
        desc = cursor.description
        return [dict(zip([col[0] for col in desc], row)) for row in cursor.fetchall()]

    @staticmethod
    def dictfetchalliter(cursor):
        desc = cursor.description
        return (dict(zip([col[0] for col in desc], row)) for row in cursor)
