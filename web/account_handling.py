from ast import Pass
from .sql import SqlRunner
import hashlib

import logging
# Get an instance of a logger
logger = logging.getLogger(__name__)

class PasswordHasher:
    def hash_password(password):
        return hashlib.md5((password + "h7dhski").encode()).hexdigest()

class AccountHandler:
    def user_exists(email):
        return SqlRunner.run_sql_get_single('SELECT count(*) FROM device_application.user_accounts WHERE user_email="{}"'.format(email))[0] != 0
    
    def promote_user_admin(user_id):
        SqlRunner.run_sql_no_response("UPDATE `device_application`.`user_accounts` SET `is_admin` = '1' WHERE (`user_id` = '{}')".format(user_id))

    def delete_user_account(user_id):
        SqlRunner.run_sql_no_response("DELETE FROM device_application.user_accounts WHERE user_id='{}'".format(user_id))

    def get_all_accounts(user_id):
        return SqlRunner.run_sql_get_all("SELECT user_id, user_email FROM device_application.user_accounts WHERE user_id != '{}'".format(user_id))


class AccountCreator:
    def user_exists(email):
        return SqlRunner.run_sql_get_single('SELECT count(*) FROM device_application.user_accounts WHERE user_email="{}"'.format(email))[0] != 0

    def attempt_create_user(name, email, password, is_admin):
        try:
            password_hash = PasswordHasher.hash_password(password)
            SqlRunner.run_sql_no_response("INSERT INTO `device_application`.`user_accounts` (`user_display_name`, `user_email`, `user_password_hash`, `is_admin`) VALUES ('{}', '{}', '{}', '{}');".format(name, email, password_hash, is_admin))
            return 1
        except:
            return -1

class LoginHandler:
    #returns true for successful login attempt, otherwise returns false
    def attempt_login(request, email, password):
        if not email or not AccountHandler.user_exists(email):
            return False
        if not password or PasswordHasher.hash_password(password) != SqlRunner.run_sql_get_single('SELECT user_password_hash FROM device_application.user_accounts WHERE user_email="{}"'.format(email))[0]:
            return False
        
        user_details = SqlRunner.run_sql_get_single('SELECT user_id, user_display_name, user_email, is_admin FROM device_application.user_accounts WHERE user_email="{}"'.format(email))
        request.session['logged_in'] = True
        request.session['user_id'] = user_details[0]
        request.session['user_display_name'] = user_details[1]
        request.session['user_email'] = user_details[2]
        request.session['is_admin'] = user_details[3]
        return True
        