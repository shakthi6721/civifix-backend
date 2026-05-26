"""Admin API routes for user and role management"""
from fastapi import APIRouter, HTTPException, status, Depends, Query
from typing import Dict, Any, List
from app.schemas.user_schema import (
    CreateAdminSchema,
    UserResponseSchema,
    RoleEnum
)
from app.schemas.common_schema import SuccessSchema
from app.core.response import ResponseHandler
from app.core.exceptions import (
    UserAlreadyExistsException,
    UserNotFoundException,
    DistrictAccessException,
    ValidationException
)
from app.dependencies.auth_dependency import get_current_admin, get_current_super_admin
from app.dependencies.role_dependency import require_role
from app.services.user_service import UserService
from app.services.role_service import RoleService
from app.repositories.user_repository import UserRepository
from app.models.user_model import admin_user_document
from app.db.mongodb import db
from app.utils.helpers import serialize_mongo_documents

router = APIRouter()


# =========================
# CREATE INSPECTOR/WORKER/ADMIN
# =========================

@router.post(
    "/users",
    summary="Create new admin/inspector/worker",
    dependencies=[Depends(require_role("DISTRICT_ADMIN", "SUPER_ADMIN"))]
)
async def create_user(
    payload: CreateAdminSchema,
    current_user: Dict[str, Any] = Depends(get_current_admin)
):
    """
    Create a new user with admin/inspector/worker role.
    
    Only DISTRICT_ADMIN can create users in their district.
    SUPER_ADMIN can create users in any district.
    """
    try:
        # Validate district access
        user_role = current_user.get("role")
        user_district = current_user.get("district")
        
        if user_role == "DISTRICT_ADMIN" and user_district != payload.district:
            raise DistrictAccessException("Can only create users in your district")
        
        # Check if user already exists
        existing = await db.users.find_one({
            "$or": [
                {"email": payload.email},
                {"mobile_number": payload.mobile_number}
            ]
        })
        
        if existing:
            raise UserAlreadyExistsException()
        
        # Create user
        user_data = {
            "name": payload.name,
            "email": payload.email,
            "mobile_number": payload.mobile_number,
            "address": payload.address,
            "district": payload.district or user_district,
            "role": payload.role,
            "permissions": [],
            "is_verified": True,
            "is_active": True,
            "status": "ACTIVE",
            "created_by": current_user.get("user_id"),
            "created_at": __import__('datetime').datetime.utcnow(),
            "updated_at": __import__('datetime').datetime.utcnow()
        }
        
        result = await db.users.insert_one(user_data)
        
        return ResponseHandler.success(
            message=f"{payload.role} created successfully",
            data={"user_id": str(result.inserted_id)},
            status_code=status.HTTP_201_CREATED
        )
    
    except (UserAlreadyExistsException, DistrictAccessException) as e:
        return ResponseHandler.error(
            message=e.message,
            status_code=e.status_code
        )
    except Exception as e:
        return ResponseHandler.error(
            message="User creation failed",
            errors=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# =========================
# GET USERS BY DISTRICT
# =========================

@router.get(
    "/users",
    summary="Get users in district",
    dependencies=[Depends(require_role("DISTRICT_ADMIN", "SUPER_ADMIN"))]
)
async def get_users(
    skip: int = Query(0, ge=0),
    limit: int = Query(20, ge=1, le=100),
    role: str = Query(None),
    current_user: Dict[str, Any] = Depends(get_current_admin)
):
    """
    Get all users in the district.
    
    DISTRICT_ADMIN can only see users in their district.
    SUPER_ADMIN can see all users.
    """
    try:
        user_role = current_user.get("role")
        user_district = current_user.get("district")
        
        if user_role == "SUPER_ADMIN":
            if role:
                users = await UserService.get_users_by_role(role, skip, limit)
            else:
                # Get all users
                users = []
        else:
            users = await UserService.get_district_users(
                user_district, # type: ignore
                user_district, # pyright: ignore[reportArgumentType]
                skip,
                limit
            )
        
        return ResponseHandler.success(
            message="Users retrieved",
            data=users
        )
    
    except Exception as e:
        return ResponseHandler.error(
            message="Failed to retrieve users",
            errors=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# =========================
# UPDATE USER ROLE
# =========================

@router.patch(
    "/users/{user_id}/role",
    summary="Update user role",
    dependencies=[Depends(require_role("DISTRICT_ADMIN", "SUPER_ADMIN"))]
)
async def update_user_role(
    user_id: str,
    new_role: RoleEnum,
    current_user: Dict[str, Any] = Depends(get_current_admin)
):
    """
    Update a user's role.
    
    Only DISTRICT_ADMIN and SUPER_ADMIN can update roles.
    """
    try:
        user = await UserRepository.find_by_id(user_id)
        if not user:
            raise UserNotFoundException()
        
        # Check district access
        if (current_user.get("role") == "DISTRICT_ADMIN" and
            user.get("district") != current_user.get("district")):
            raise DistrictAccessException()
        
        await UserService.assign_role(user_id, new_role)
        
        return ResponseHandler.success(
            message=f"User role updated to {new_role}"
        )
    
    except (UserNotFoundException, DistrictAccessException) as e:
        return ResponseHandler.error(
            message=e.message,
            status_code=e.status_code
        )
    except Exception as e:
        return ResponseHandler.error(
            message="Failed to update role",
            errors=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# =========================
# SUSPEND/ACTIVATE USER
# =========================

@router.patch(
    "/users/{user_id}/suspend",
    summary="Suspend user account",
    dependencies=[Depends(require_role("DISTRICT_ADMIN", "SUPER_ADMIN"))]
)
async def suspend_user(
    user_id: str,
    current_user: Dict[str, Any] = Depends(get_current_admin)
):
    """Suspend a user account"""
    try:
        user = await UserRepository.find_by_id(user_id)
        if not user:
            raise UserNotFoundException()
        
        if (current_user.get("role") == "DISTRICT_ADMIN" and
            user.get("district") != current_user.get("district")):
            raise DistrictAccessException()
        
        await UserService.suspend_user(user_id)
        
        return ResponseHandler.success(
            message="User suspended successfully"
        )
    
    except (UserNotFoundException, DistrictAccessException) as e:
        return ResponseHandler.error(
            message=e.message,
            status_code=e.status_code
        )
    except Exception as e:
        return ResponseHandler.error(
            message="Failed to suspend user",
            errors=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.patch(
    "/users/{user_id}/activate",
    summary="Activate user account",
    dependencies=[Depends(require_role("DISTRICT_ADMIN", "SUPER_ADMIN"))]
)
async def activate_user(
    user_id: str,
    current_user: Dict[str, Any] = Depends(get_current_admin)
):
    """Activate a user account"""
    try:
        user = await UserRepository.find_by_id(user_id)
        if not user:
            raise UserNotFoundException()
        
        if (current_user.get("role") == "DISTRICT_ADMIN" and
            user.get("district") != current_user.get("district")):
            raise DistrictAccessException()
        
        await UserService.activate_user(user_id)
        
        return ResponseHandler.success(
            message="User activated successfully"
        )
    
    except (UserNotFoundException, DistrictAccessException) as e:
        return ResponseHandler.error(
            message=e.message,
            status_code=e.status_code
        )
    except Exception as e:
        return ResponseHandler.error(
            message="Failed to activate user",
            errors=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


# =========================
# MANAGE ROLES (SUPER_ADMIN ONLY)
# =========================

@router.post(
    "/roles",
    summary="Create custom role",
    dependencies=[Depends(require_role("SUPER_ADMIN"))]
)
async def create_role(
    name: str,
    description: str,
    permissions: List[str],
    district: str = None, # pyright: ignore[reportArgumentType]
    current_user: Dict[str, Any] = Depends(get_current_super_admin)
):
    """Create a custom role"""
    try:
        role_id = await RoleService.create_custom_role(
            name=name,
            description=description,
            permissions=permissions,
            district=district
        )
        
        return ResponseHandler.success(
            message="Role created successfully",
            data={"role_id": role_id},
            status_code=status.HTTP_201_CREATED
        )
    
    except Exception as e:
        return ResponseHandler.error(
            message="Failed to create role",
            errors=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )


@router.get(
    "/roles",
    summary="Get all roles",
    dependencies=[Depends(require_role("SUPER_ADMIN"))]
)
async def get_roles(
    current_user: Dict[str, Any] = Depends(get_current_super_admin)
):
    """Get all roles"""
    try:
        from app.repositories.role_repository import RoleRepository
        roles = await RoleRepository.get_all_roles()
        roles = serialize_mongo_documents(roles)
        
        return ResponseHandler.success(
            message="Roles retrieved",
            data=roles
        )
    
    except Exception as e:
        return ResponseHandler.error(
            message="Failed to retrieve roles",
            errors=str(e),
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR
        )
