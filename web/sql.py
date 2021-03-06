from django.db import connection

class SqlRunner():
    def run_sql_get_single(statement):
        with connection.cursor() as cursor:
            cursor.execute(statement)
            response = cursor.fetchone()
        return response

    # def run_sql_get_all(statement):
    #     with connection.cursor() as cursor:
    #         cursor.execute(statement)
    #         columns = [column[0] for column in cursor.description]
    #     return [
    #         dict(zip(columns, row))
    #         for row in cursor.fetchall()
    #     ]

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

