"""Tests for route accessibility — verify pages load without errors."""



async def test_homepage(client):
    response = await client.get("/")
    assert response.status_code == 200
    assert "PHOENIX" in response.text


async def test_products_page(client):
    response = await client.get("/products")
    assert response.status_code == 200


async def test_login_page(client):
    response = await client.get("/auth/login")
    assert response.status_code == 200
    assert "Sign In" in response.text


async def test_register_page(client):
    response = await client.get("/auth/register")
    assert response.status_code == 200
    assert "Create Account" in response.text


async def test_about_page(client):
    response = await client.get("/about")
    assert response.status_code == 200


async def test_faq_page(client):
    response = await client.get("/faq")
    assert response.status_code == 200


async def test_terms_page(client):
    response = await client.get("/terms")
    assert response.status_code == 200


async def test_contact_page(client):
    response = await client.get("/contact")
    assert response.status_code == 200


async def test_disclaimer_page(client):
    response = await client.get("/disclaimer")
    assert response.status_code == 200


async def test_cart_page(client):
    response = await client.get("/cart")
    assert response.status_code == 200
    assert "empty" in response.text.lower() or "cart" in response.text.lower()


async def test_404_page(client):
    response = await client.get("/nonexistent-page-xyz")
    assert response.status_code in (404, 405)


async def test_api_docs(client):
    response = await client.get("/api/docs")
    assert response.status_code == 200


async def test_security_headers(client):
    response = await client.get("/")
    assert "X-Content-Type-Options" in response.headers
    assert response.headers["X-Content-Type-Options"] == "nosniff"
    assert "X-Frame-Options" in response.headers
