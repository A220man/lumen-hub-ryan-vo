"""Backend SMS templates tests."""

import pytest
from httpx import ASGITransport, AsyncClient
from unittest.mock import AsyncMock, patch

from app.main import app
from app.api.sms_templates import _validate_template_format, _render_template


@pytest.mark.asyncio
async def test_list_templates_requires_auth() -> None:
    """Test list templates endpoint requires authentication."""
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.get("/api/v1/sms-templates")
    assert response.status_code == 401


@pytest.mark.asyncio
async def test_create_template_requires_admin_role() -> None:
    """Test create template requires admin or operator role."""
    # This would need proper auth mocking - for now just test the endpoint exists
    async with AsyncClient(transport=ASGITransport(app=app), base_url="http://test") as client:
        response = await client.post(
            "/api/v1/sms-templates",
            json={"name": "test", "content": "Your OTP is {otp}"}
        )
    # Should fail due to auth, not due to missing endpoint
    assert response.status_code in (401, 403)


@pytest.mark.asyncio
async def test_validate_template_format() -> None:
    """Test template format validation."""
    # Valid template with {otp}
    result = _validate_template_format("Your OTP is: {otp}")
    assert result.valid is True
    assert result.is_webotp_compatible is True
    assert len(result.errors) == 0

    # Valid template with {{otp}}
    result = _validate_template_format("Your OTP is: {{otp}}")
    assert result.valid is True
    assert result.is_webotp_compatible is True

    # Invalid template - missing OTP placeholder
    result = _validate_template_format("Hello world")
    assert result.valid is False
    assert "Template must contain an OTP placeholder" in result.errors[0]

    # Invalid template - too long
    long_content = "x" * 1601 + " {otp}"
    result = _validate_template_format(long_content)
    assert result.valid is False
    assert "exceeds maximum length" in result.errors[0]


@pytest.mark.asyncio
async def test_render_template() -> None:
    """Test template rendering with variables."""
    result = _render_template("Hello {name}, your OTP is {otp}", {"name": "John", "otp": "123456"})
    assert result == "Hello John, your OTP is 123456"

    # Test double braces too
    result = _render_template("Hello {{name}}, your OTP is {{otp}}", {"name": "Jane", "otp": "654321"})
    assert result == "Hello Jane, your OTP is 654321"

    # Test mixed
    result = _render_template("Hello {name}, your OTP is {{otp}}", {"name": "Bob", "otp": "111222"})
    assert result == "Hello Bob, your OTP is 111222"

    # Test missing variable (should leave placeholder)
    result = _render_template("Hello {name}, your OTP is {otp}", {"name": "Alice"})
    assert result == "Hello Alice, your OTP is {otp}"


@pytest.mark.asyncio
async def test_segment_count_warning() -> None:
    """Test segment count warning for long templates."""
    # Under 160 chars - no warning
    result = _validate_template_format("Short {otp}")
    assert len(result.warnings) == 0

    # Over 160 chars - should have warning
    long_content = "x" * 200 + " {otp}"
    result = _validate_template_format(long_content)
    assert len(result.warnings) > 0
    assert "exceeds 160 characters" in result.warnings[0]


@pytest.mark.asyncio
async def test_newline_support() -> None:
    """Test template with newlines (Issue #6435)."""
    template_with_newlines = "Hello {name},\\n\\nYour OTP is: {otp}\\n\\nThank you!"
    result = _validate_template_format(template_with_newlines)
    assert result.valid is True
    assert result.is_webotp_compatible is True

    # Test rendering preserves newlines
    rendered = _render_template(template_with_newlines, {"name": "Test", "otp": "123456"})
    assert "\\n" in rendered
    assert "Hello Test" in rendered
    assert "123456" in rendered
