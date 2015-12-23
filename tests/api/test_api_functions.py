from swagmail import app
import string
import random
import json


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
            {"source": "pickles@swagmail.com", "destination": "rawr@swagmail.com"}))
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 400
        assert "not a current" in rv.data

    def test_aliases_add_pass(self, loggedin_client):
        rv = loggedin_client.post("/api/v1/aliases", data=json.dumps(
            {"source": "rawr@swagmail.com", "destination": "email@swagmail.com"}))
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 201

    def test_aliases_update_source_pass(self, loggedin_client):
        rv = loggedin_client.put("/api/v1/aliases/2", data=json.dumps(
            {"source": "somealias@swagmail.com"}))
        assert rv.status_code == 200

    def test_aliases_update_destination_pass(self, loggedin_client):
        rv = loggedin_client.put("/api/v1/aliases/2", data=json.dumps(
            {"destination": "email@swagmail.org"}))
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
            {"email": "pickles@swagmail.com", "password": "som3passw0rd"}))
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
            {"name": "swagmail.com"}))
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 400
        assert "already exists" in rv.data

    def test_domains_add_pass(self, loggedin_client):
        rv = loggedin_client.post("/api/v1/domains", data=json.dumps(
            {"name": "".join((random.choice(string.ascii_uppercase + string.digits) for _ in range(6)))+ ".com"}))
        try:
            json.loads(rv.data)
        except:
            assert False, "Not json"
        assert rv.status_code == 201

    def test_domains_delete_pass(self, loggedin_client):
        rv = loggedin_client.delete("/api/v1/domains/2", follow_redirects=True)
        assert rv.status_code == 204
