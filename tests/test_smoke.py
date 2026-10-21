def test_admin_redirects_to_login(client):
    response = client.get('/admin/')
    assert response.status_code == 302
    assert '/admin/login/' in response['Location']
