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
        self._params = None

    def _add_params(self, params):
        if params is None:
            return
        if self._params is None:
            assert isinstance(params, (list, tuple, dict)), "sql params must be list or dict"
            self._params = params
        elif isinstance(self._params, dict):
            assert isinstance(params, dict), "cannot mix positional/named sql params"
            self._params.update(params)
        else:
            assert isinstance(params, (list, tuple)), "cannot mix positional/named sql params"
            self._params.extend(params)

    def add(self, sql, params=None):
        self.add_if(True, sql, params)

    def add_if(self, condition_expr, sql, params=None):
        if condition_expr:
            self._sql_parts.append(sql)
            self._add_params(params)

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
