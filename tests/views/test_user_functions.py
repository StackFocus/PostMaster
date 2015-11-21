from swagmail import app

class TestUserFunctions:

    def test_user_login(self, loggedin_client):
        rv = loggedin_client.get("/", follow_redirects=True)
        print rv.data
        assert "Logout" in rv.data

    def test_domains_page(self, loggedin_client):
        rv = loggedin_client.get("/domains", follow_redirects=True)
        assert "Domains" in rv.data

    def test_user_logout(self, loggedin_client):
        rv = loggedin_client.get("/logout", follow_redirects=True)
        assert "Successfully logged out" in rv.data
