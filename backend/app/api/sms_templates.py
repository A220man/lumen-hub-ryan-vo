"""SMS OTP template management API endpoints."""

from fastapi import APIRouter, Depends, HTTPException, status
from pydantic import BaseModel, Field, validator
from typing import Optional, List

from app.core.auth import get_current_user, require_roles

router = APIRouter(prefix="/sms-templates", tags=["sms-templates"])


class SMSTemplateCreate(BaseModel):
    """Request model for creating an SMS template."""
    name: str = Field(..., min_length=1, max_length=100, description="Unique template name")
    content: str = Field(..., min_length=1, max_length=1600, description="Template content with placeholders")
    description: Optional[str] = Field(None, max_length=500, description="Optional template description")


class SMSTemplateUpdate(BaseModel):
    """Request model for updating an SMS template."""
    content: Optional[str] = Field(None, min_length=1, max_length=1600, description="Template content with placeholders")
    description: Optional[str] = Field(None, max_length=500, description="Optional template description")


class SMSTemplateResponse(BaseModel):
    """Response model for SMS template."""
    name: str
    content: str
    description: Optional[str] = None
    created_at: str
    updated_at: str


class SMSTemplatePreviewRequest(BaseModel):
    """Request model for previewing a template with variables."""
    content: str = Field(..., min_length=1, max_length=1600, description="Template content")
    variables: dict = Field(default_factory=dict, description="Variables to substitute in template")


class SMSTemplatePreviewResponse(BaseModel):
    """Response model for template preview."""
    rendered: str
    is_webotp_compatible: bool
    character_count: int
    segment_count: int


class SMSValidationResponse(BaseModel):
    """Response model for template validation."""
    valid: bool
    errors: List[str] = []
    warnings: List[str] = []
    is_webotp_compatible: bool


# In-memory storage (will be replaced with database later)
_templates: dict[str, dict] = {}


def _validate_template_format(content: str) -> SMSValidationResponse:
    """Validate SMS template format for WebOTP compatibility."""
    errors: List[str] = []
    warnings: List[str] = []
    
    # Check for required OTP placeholder
    if "{otp}" not in content and "{{otp}}" not in content:
        errors.append("Template must contain an OTP placeholder: {otp} or {{otp}}")
    
    # Check character count
    if len(content) > 1600:
        errors.append("Template content exceeds maximum length of 1600 characters")
    
    # Check for WebOTP format: "Your OTP is: {otp}" or similar
    # WebOTP expects format like: "Your verification code is: 123456"
    # or just the code with domain context
    is_webotp_compatible = False
    if "{otp}" in content or "{{otp}}" in content:
        # Basic WebOTP check: code should be at end or clearly identifiable
        # RFC spec suggests format like "Your OTP is: {otp}" or "{otp} is your code"
        # For now, we check if OTP is present and template is reasonable
        is_webotp_compatible = True
        if len(content) > 160:
            warnings.append("Template exceeds 160 characters (single SMS segment limit)")
    
    # Count segments (160 chars per segment for GSM-7)
    char_count = len(content)
    segment_count = max(1, (char_count + 159) // 160)
    
    return SMSValidationResponse(
        valid=len(errors) == 0,
        errors=errors,
        warnings=warnings,
        is_webotp_compatible=is_webotp_compatible,
    )


def _render_template(content: str, variables: dict) -> str:
    """Render template with variable substitution. Supports both {key} and {{key}} formats."""
    result = content
    for key, value in variables.items():
        # Replace double braces first, then single braces
        result = result.replace(f"{{{{{key}}}}}", str(value))
        result = result.replace(f"{{{key}}}", str(value))
    return result


@router.get("", response_model=List[SMSTemplateResponse])
async def list_templates(
    user: dict = Depends(require_roles("admin", "operator"))
) -> List[SMSTemplateResponse]:
    """List all SMS templates. Requires admin or operator role."""
    return [
        SMSTemplateResponse(**template)
        for template in _templates.values()
    ]


@router.post("", response_model=SMSTemplateResponse, status_code=status.HTTP_201_CREATED)
async def create_template(
    template_data: SMSTemplateCreate,
    user: dict = Depends(require_roles("admin", "operator"))
) -> SMSTemplateResponse:
    """Create a new SMS template. Requires admin or operator role."""
    # Validate template format
    validation = _validate_template_format(template_data.content)
    if not validation.valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Invalid template format", "errors": validation.errors}
        )
    
    if template_data.name in _templates:
        raise HTTPException(
            status_code=status.HTTP_409_CONFLICT,
            detail=f"Template with name '{template_data.name}' already exists"
        )
    
    from datetime import datetime, timezone
    now = datetime.now(timezone.utc).isoformat()
    
    template = {
        "name": template_data.name,
        "content": template_data.content,
        "description": template_data.description,
        "created_at": now,
        "updated_at": now,
    }
    _templates[template_data.name] = template
    
    return SMSTemplateResponse(**template)


@router.get("/{name}", response_model=SMSTemplateResponse)
async def get_template(
    name: str,
    user: dict = Depends(require_roles("admin", "operator"))
) -> SMSTemplateResponse:
    """Get a specific SMS template by name. Requires admin or operator role."""
    if name not in _templates:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template '{name}' not found"
        )
    return SMSTemplateResponse(**_templates[name])


@router.put("/{name}", response_model=SMSTemplateResponse)
async def update_template(
    name: str,
    template_data: SMSTemplateUpdate,
    user: dict = Depends(require_roles("admin", "operator"))
) -> SMSTemplateResponse:
    """Update an existing SMS template. Requires admin or operator role."""
    if name not in _templates:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template '{name}' not found"
        )
    
    template = _templates[name]
    
    if template_data.content is not None:
        validation = _validate_template_format(template_data.content)
        if not validation.valid:
            raise HTTPException(
                status_code=status.HTTP_400_BAD_REQUEST,
                detail={"message": "Invalid template format", "errors": validation.errors}
            )
        template["content"] = template_data.content
    
    if template_data.description is not None:
        template["description"] = template_data.description
    
    from datetime import datetime, timezone
    template["updated_at"] = datetime.now(timezone.utc).isoformat()
    
    return SMSTemplateResponse(**template)


@router.delete("/{name}", status_code=status.HTTP_204_NO_CONTENT)
async def delete_template(
    name: str,
    user: dict = Depends(require_roles("admin"))
) -> None:
    """Delete an SMS template. Requires admin role."""
    if name not in _templates:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail=f"Template '{name}' not found"
        )
    del _templates[name]


@router.post("/validate", response_model=SMSValidationResponse)
async def validate_template(
    template_data: SMSTemplateCreate,
    user: dict = Depends(require_roles("admin", "operator"))
) -> SMSValidationResponse:
    """Validate an SMS template format without saving. Requires admin or operator role."""
    return _validate_template_format(template_data.content)


@router.post("/preview", response_model=SMSTemplatePreviewResponse)
async def preview_template(
    request: SMSTemplatePreviewRequest,
    user: dict = Depends(require_roles("admin", "operator"))
) -> SMSTemplatePreviewResponse:
    """Preview a template with variables substituted. Requires admin or operator role."""
    validation = _validate_template_format(request.content)
    if not validation.valid:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail={"message": "Invalid template format", "errors": validation.errors}
        )
    
    rendered = _render_template(request.content, request.variables)
    char_count = len(rendered)
    segment_count = max(1, (char_count + 159) // 160)
    
    return SMSTemplatePreviewResponse(
        rendered=rendered,
        is_webotp_compatible=validation.is_webotp_compatible,
        character_count=char_count,
        segment_count=segment_count,
    )
