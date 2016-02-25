import string
import random
import json
from postmaster import db
from postmaster.models import Configs

class TestMailDbFunctions:

    def test_aliases_get(self, loggedin_client):
        rv = loggedin_client.get("/api/v1/aliases", follow_redirects=True)
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 200

    def test_aliases_add_fail_domain_managed(self, loggedin_client):
        rv = loggedin_client.post("/api/v1/aliases", data=json.dumps(
            {"source": "pickles@test123.com", "destination": "rawr@test123.com"}))
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 400
        assert "not managed" in rv.data

    def test_aliases_add_fail_not_current(self, loggedin_client):
        rv = loggedin_client.post("/api/v1/aliases", data=json.dumps(
            {"source": "pickles@postmaster.com", "destination": "rawr@postmaster.com"}))
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 400
        assert "not a current" in rv.data

    def test_aliases_add_fail_source_empty(self, loggedin_client):
        rv = loggedin_client.post("/api/v1/aliases", data=json.dumps(
            {"source": "", "destination": "rawr@postmaster.com"}))
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 400
        assert "The source email was not specified" in rv.data

    def test_aliases_add_fail_destination_empty(self, loggedin_client):
        rv = loggedin_client.post("/api/v1/aliases", data=json.dumps(
            {"source": "rawr@postmaster.com", "destination": ""}))
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 400
        assert "The destination email was not specified" in rv.data

    def test_aliases_add_pass(self, loggedin_client):
        rv = loggedin_client.post("/api/v1/aliases", data=json.dumps(
            {"source": "rawr@postmaster.com", "destination": "email@postmaster.com"}))
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 201

    def test_aliases_update_source_pass(self, loggedin_client):
        rv = loggedin_client.put("/api/v1/aliases/2", data=json.dumps(
            {"source": "somealias@postmaster.com"}))
        assert rv.status_code == 200

    def test_aliases_update_destination_pass(self, loggedin_client):
        rv = loggedin_client.put("/api/v1/aliases/2", data=json.dumps(
            {"destination": "email@postmaster.org"}))
        assert rv.status_code == 200

    def test_alias_update_fail_source_or_destination_not_supplied(self, loggedin_client):
        rv = loggedin_client.put("/api/v1/aliases/2", data=json.dumps(
            {"someotherdata": "aomeotherdata"}))
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 400
        assert "The source or destination was not supplied in the request" in rv.data

    def test_aliases_delete_pass(self, loggedin_client):
        rv = loggedin_client.delete("/api/v1/aliases/2", follow_redirects=True)
        assert rv.status_code == 204

    def test_users_get(self, loggedin_client):
        rv = loggedin_client.get("/api/v1/users", follow_redirects=True)
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 200

    def test_users_add_fail_not_valid(self, loggedin_client):
        rv = loggedin_client.post("/api/v1/users", data=json.dumps(
            {"email": "picklesasda", "password": "som3passw0rd"}))
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 400
        assert "not a valid" in rv.data

    def test_users_add_fail_domain_managed(self, loggedin_client):
        rv = loggedin_client.post("/api/v1/users", data=json.dumps(
            {"email": "pickles@test123.com", "password": "som3passw0rd"}))
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 400
        assert "not managed" in rv.data

    def test_users_add_fail_password_empty(self, loggedin_client):
        rv = loggedin_client.post("/api/v1/users", data=json.dumps(
            {"email": "pickles@test123.com", "password": ""}))
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 400
        assert "The password was not specified" in rv.data

    def test_users_add_fail_email_empty(self, loggedin_client):
        rv = loggedin_client.post("/api/v1/users", data=json.dumps(
            {"email": "", "password": "som3passw0rd"}))
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 400
        assert "The email address was not specified" in rv.data

    def test_users_update_fail_password_not_supplied(self, loggedin_client):
        rv = loggedin_client.put("/api/v1/users/2", data=json.dumps(
            {"someotherdata": "pickles"}))
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 400
        assert "The password was not supplied in the request" in rv.data

    def test_users_add_pass(self, loggedin_client):
        rv = loggedin_client.post("/api/v1/users", data=json.dumps(
            {"email": "pickles@postmaster.com", "password": "som3passw0rd"}))
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 201

    def test_users_update_pass(self, loggedin_client):
        rv = loggedin_client.put("/api/v1/users/2", data=json.dumps(
            {"password": "som3passw0rd123"}))
        assert rv.status_code == 200

    def test_users_delete_pass(self, loggedin_client):
        rv = loggedin_client.delete("/api/v1/users/2", follow_redirects=True)
        assert rv.status_code == 204

    def test_domains_get(self, loggedin_client):
        rv = loggedin_client.get("/api/v1/domains", follow_redirects=True)
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 200

    def test_users_add_fail_domain_missing(self, loggedin_client):
        rv = loggedin_client.post("/api/v1/domains", data=json.dumps(
            {"lol": "what"}))
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 400
        assert "not specified" in rv.data

    def test_domains_add_fail_already_exists(self, loggedin_client):
        rv = loggedin_client.post("/api/v1/domains", data=json.dumps(
            {"name": "postmaster.com"}))
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 400
        assert "already exists" in rv.data

    def test_domains_add_fail_name_empty(self, loggedin_client):
        rv = loggedin_client.post("/api/v1/domains", data=json.dumps(
            {"name": ""}))
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 400
        assert "The domain name was not specified" in rv.data

    def test_domains_add_pass(self, loggedin_client):
        rv = loggedin_client.post("/api/v1/domains", data=json.dumps(
            {"name": "".join((random.choice(string.ascii_uppercase + string.digits) for _ in range(6))) + ".com"}))
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 201

    def test_domains_delete_pass(self, loggedin_client):
        rv = loggedin_client.delete("/api/v1/domains/2", follow_redirects=True)
        assert rv.status_code == 204

    def test_admins_get_one(self, loggedin_client):
        rv = loggedin_client.get("/api/v1/admins/1", follow_redirects=True)
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 200

    def test_admins_get_all(self, loggedin_client):
        rv = loggedin_client.get("/api/v1/admins", follow_redirects=True)
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 200

    def test_admins_add_pass(self, loggedin_client):
        rv = loggedin_client.post("/api/v1/admins", data=json.dumps(
            {"username": "user_admin@postmaster.com", "password": "som3passw0rd", "name": "Test Admin"}))
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 201

    def test_admins_add_fail_duplicate(self, loggedin_client):
        rv = loggedin_client.post("/api/v1/admins", data=json.dumps(
            {"username": "user@postmaster.com", "password": "som3passw0rd", "name": "Test Admin"}))
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 400
        assert "already exists" in rv.data

    def test_admins_add_fail_no_username(self, loggedin_client):
        rv = loggedin_client.post("/api/v1/admins", data=json.dumps(
            {"password": "som3passw0rd", "name": "Test Admin"}))
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 400
        assert "The username was not specified" in rv.data

    def test_admins_add_fail_no_password(self, loggedin_client):
        rv = loggedin_client.post("/api/v1/admins", data=json.dumps(
            {"username": "user_admin2@postmaster.com", "name": "Test Admin"}))
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 400
        assert "The password was not specified" in rv.data

    def test_admins_add_fail_no_name(self, loggedin_client):
        rv = loggedin_client.post("/api/v1/admins", data=json.dumps(
            {"username": "user_admin2@postmaster.com", "password": "som3passw0rd"}))
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 400
        assert "The name was not specified" in rv.data

    def test_admins_update_password_pass(self, loggedin_client):
        rv = loggedin_client.put("/api/v1/admins/2", data=json.dumps(
            {"password": "som3passw0rd123"}))
        assert rv.status_code == 200

    def test_admins_update_name_pass(self, loggedin_client):
        rv = loggedin_client.put("/api/v1/admins/2", data=json.dumps(
            {"name": "Some New Name"}))
        assert rv.status_code == 200

    def test_admins_update_email_pass(self, loggedin_client):
        rv = loggedin_client.put("/api/v1/admins/2", data=json.dumps(
            {"username": "newemail@postmaster.com"}))
        assert rv.status_code == 200

    def test_admins_update_fail(self, loggedin_client):
        rv = loggedin_client.put("/api/v1/admins/2", data=json.dumps(
            {"randomkey": "random_value"}))
        assert rv.status_code == 400
        assert "The username, password, or name was not supplied in the request" in rv.data

    def test_admins_delete_pass(self, loggedin_client):
        rv = loggedin_client.delete("/api/v1/admins/2", follow_redirects=True)
        assert rv.status_code == 204

    def test_configs_get_one(self, loggedin_client):
        rv = loggedin_client.get("/api/v1/configs/1", follow_redirects=True)
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 200

    def test_configs_get_all(self, loggedin_client):
        rv = loggedin_client.get("/api/v1/configs", follow_redirects=True)
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 200

    def test_configs_update_pass(self, loggedin_client):
        rv = loggedin_client.put("/api/v1/configs/2", data=json.dumps(
            {"value": "True"}))
        assert rv.status_code == 200

    def test_configs_update_fail(self, loggedin_client):
        rv = loggedin_client.put("/api/v1/configs/2", data=json.dumps(
            {"someparameter": "somevalue"}))
        assert rv.status_code == 400
        assert 'An invalid setting value was supplied' in rv.data

    def test_configs_min_pwd_update_pass(self, loggedin_client):
        rv = loggedin_client.put("/api/v1/configs/1", data=json.dumps(
            {"value": "7"}))
        assert rv.status_code == 200

    def test_configs_min_pwd_update_fail(self, loggedin_client):
        rv = loggedin_client.put("/api/v1/configs/1", data=json.dumps(
            {"value": "9999"}))
        assert rv.status_code == 400
        assert 'An invalid minimum password length was supplied.' in rv.data

    def test_configs_update_log_file_fail(self, loggedin_client):
        """ Tests the update_config function (PUT route for configs) when a new log file
        path is specified but isn't writeable. A return value of an error is expected.
        """
        rv = loggedin_client.put("/api/v1/configs/4", data=json.dumps(
            {"value": "s0m3NonExistentDir/new_logfile.txt"}))
        assert rv.status_code == 400
        assert 'The specified log path is not writable' in rv.data

    def test_configs_update_auditing_with_no_log_file_fail(self, loggedin_client):
        """ Tests the update_config function (PUT route for configs) to make sure
        audit settings cannot be set when the log file path is not set.
        """
        # Sets Login Auditing to False
        login_auditing = Configs.query.filter_by(setting='Login Auditing').first()
        old_login_auditing_value = login_auditing.value
        login_auditing.value = 'False'
        db.session.add(login_auditing)
        # Sets Mail Database Auditing to False
        mail_db_auditing = Configs.query.filter_by(setting='Mail Database Auditing').first()
        old_mail_db_auditing = mail_db_auditing.value
        mail_db_auditing.value = 'False'
        db.session.add(mail_db_auditing)
        # Sets the Log File to None
        log_file = Configs.query.filter_by(setting='Log File').first()
        old_log_file_value = log_file.value
        log_file.value = None
        db.session.add(log_file)
        db.session.commit()

        # Attempts to enable Login Auditing
        login_auditing_rv = loggedin_client.put("/api/v1/configs/2", data=json.dumps(
            {"value": "True"}))
        # Attempts to enable Mail Database Auditing
        mail_db_auditing_rv = loggedin_client.put("/api/v1/configs/3", data=json.dumps(
            {"value": "True"}))

        # Reverts changes made to the database previously
        login_auditing.value = old_login_auditing_value
        mail_db_auditing.value = old_mail_db_auditing
        log_file.value = old_log_file_value
        db.session.add(login_auditing)
        db.session.add(mail_db_auditing)
        db.session.add(log_file)
        db.session.commit()

        assert login_auditing_rv.status_code == 400
        assert 'The log file must be set before auditing can be enabled' in login_auditing_rv.data
        assert mail_db_auditing_rv.status_code == 400
        assert 'The log file must be set before auditing can be enabled' in mail_db_auditing_rv.data
