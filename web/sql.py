from django.db import connection
import re
import logging

logger = logging.getLogger(__name__)

class SqlRunner():
    def run_sql_get_single(statement):
        with connection.cursor() as cursor:
            cursor.execute(statement)
            response = cursor.fetchone()
        return response

    def run_sql_get_all(statement):
        output=[]
        with connection.cursor() as cursor:
            cursor.execute(statement)
            for row in cursor.fetchall():
                # logger.error(row)
                output.append(row)
        return output

    def run_sql_no_response(statment):
        with connection.cursor() as cursor:
            cursor.execute(statment)
            return
    
    def validate_args(args):
        for arg in args:
            if "'" in arg or '"' in arg or '-' in arg:
                raise Exception("Arguments passed from user contain a banned character. [', \", -")
        return True

