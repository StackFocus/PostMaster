﻿class TestUserFunctions:

    def test_user_login(self, loggedin_client):
        rv = loggedin_client.get("/", follow_redirects=True)
        assert "Logout" in rv.data.decode('utf-8')

    def test_domains_page(self, loggedin_client):
        rv = loggedin_client.get("/domains", follow_redirects=True)
        assert "Domains" in rv.data.decode('utf-8')

    def test_users_page(self, loggedin_client):
        rv = loggedin_client.get("/users", follow_redirects=True)
        assert "Users" in rv.data.decode('utf-8')

    def test_aliases_page(self, loggedin_client):
        rv = loggedin_client.get("/aliases", follow_redirects=True)
        assert "Aliases" in rv.data.decode('utf-8')

    def test_admins_page(self, loggedin_client):
        rv = loggedin_client.get("/admins", follow_redirects=True)
        assert "Administrators" in rv.data.decode('utf-8')

    def test_configs_page(self, loggedin_client):
        rv = loggedin_client.get("/admins", follow_redirects=True)
        assert "Administrators" in rv.data.decode('utf-8')

    def test_user_logout(self, loggedin_client):
        rv = loggedin_client.get("/logout", follow_redirects=True)
        assert "Successfully logged out" in rv.data.decode('utf-8')
