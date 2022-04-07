from .sql import SqlRunner

class DeviceModelRetriever():
    def get_all_models():
        return SqlRunner.run_sql_get_all("SELECT model_id, model_name FROM device_application.device_models")

class UserDeviceRetriever():
    def get_user_devices(user_id, exclude_open_transfers=None):
        query = """SELECT device_assignments.device_id, device_models.model_name, device_assignments.status FROM device_application.device_assignments
                    INNER JOIN device_application.device_models ON device_assignments.model_id = device_models.model_id 
                    WHERE device_assignments.user_id = {}""".format(user_id)

        if exclude_open_transfers:
            query+=" AND device_assignments.open_transfer=0"
        return SqlRunner.run_sql_get_all(query)

class DeviceHandler():
    def change_device_status(device_id, change_to):
        SqlRunner.run_sql_no_response("UPDATE `device_application`.`device_assignments` SET `status` = '{}' WHERE (`device_id` = '{}')".format(change_to, device_id))
    
    def assign_new_device(device_id, user_id, model_id):
        SqlRunner.run_sql_no_response("INSERT INTO `device_application`.`device_assignments` (`device_id`, `user_id`, `model_id`, `status`, `open_transfer`) VALUES ('{}', '{}', '{}', 'SECURE', '0')".format(device_id, user_id, model_id))
    
    def get_incoming_transfers(user_id):
        return SqlRunner.run_sql_get_all("""SELECT device_transfers.device_id, device_models.model_name, user_accounts.user_display_name, user_accounts.user_email
                                            FROM device_application.device_transfers
                                            INNER JOIN device_application.device_assignments ON device_transfers.device_id = device_assignments.device_id
                                            INNER JOIN device_application.device_models ON device_models.model_id = device_assignments.model_id
                                            INNER JOIN device_application.user_accounts ON user_accounts.user_id = device_transfers.current_owner_id
                                            WHERE device_transfers.new_owner_id = '{}'""".format(user_id))
    
    def get_outgoing_transfers(user_id):
        return SqlRunner.run_sql_get_all("""SELECT device_assignments.device_id, device_models.model_name, user_accounts.user_display_name, user_accounts.user_email
                                            FROM device_application.device_assignments
                                            INNER JOIN device_transfers ON device_assignments.device_id = device_transfers.device_id
                                            INNER JOIN device_models ON device_assignments.model_id = device_models.model_id
                                            INNER JOIN user_accounts ON device_transfers.new_owner_id = user_accounts.user_id
                                            WHERE device_assignments.user_id={} AND device_assignments.open_transfer=1""".format(user_id))
    
    def decline_transfer(device_id):
        SqlRunner.run_sql_no_response("DELETE FROM `device_application`.`device_transfers` WHERE (`device_id` = '{}')".format(device_id))
        SqlRunner.run_sql_no_response("UPDATE `device_application`.`device_assignments` SET `open_transfer` = 0 WHERE (`device_id` = '{}')".format(device_id))

    
    def accept_transfer(device_id, user_id):
        SqlRunner.run_sql_no_response("UPDATE `device_application`.`device_assignments` SET `user_id` = '{}', `open_transfer` = 0 WHERE (`device_id` = '{}')".format(user_id, device_id))
        SqlRunner.run_sql_no_response("DELETE FROM `device_application`.`device_transfers` WHERE (`device_id` = '{}')".format(device_id))

    def create_transfer(device_id, user_id, new_user_email):
        SqlRunner.run_sql_no_response("INSERT INTO `device_application`.`device_transfers` (`device_id`, `current_owner_id`, `new_owner_id`) SELECT '{}', '{}', user_accounts.user_id FROM device_application.user_accounts WHERE user_accounts.user_email='{}'".format(device_id, user_id, new_user_email))
        SqlRunner.run_sql_no_response("UPDATE `device_application`.`device_assignments` SET `open_transfer` = 1 WHERE (`device_id` = '{}')".format(device_id))