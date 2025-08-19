from app.api.router import api_router


def test_api_router_creation():
    """Test that the API router is created successfully."""
    assert api_router is not None
    assert hasattr(api_router, "routes")
    # Should have routes from included user router
    assert len(api_router.routes) > 0
