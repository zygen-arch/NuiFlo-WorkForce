from fastapi import APIRouter, Depends, HTTPException, status, Query
from sqlalchemy.orm import Session
from typing import List, Optional

from ...core.database import get_db_dependency
from ...core.auth import get_current_user
from ...services.space_service import SpaceService
from ...schemas.space import (
    SpaceCreate, SpaceUpdate, SpaceResponse, SpaceListResponse,
    SpaceBillingResponse, SpaceActivityResponse, StorageConfig
)
import structlog
logger = structlog.get_logger()

router = APIRouter(prefix="/spaces", tags=["spaces"])

@router.get("/", response_model=SpaceListResponse)
def get_user_spaces(
    skip: int = Query(0, ge=0),
    limit: int = Query(100, ge=1, le=1000),
    db: Session = Depends(get_db_dependency),
    current_user = Depends(get_current_user)
) -> SpaceListResponse:
    """Get all spaces accessible to the current user"""
    try:
        spaces = SpaceService.get_user_spaces(
            user_id=current_user["sub"],
            db=db,
            skip=skip,
            limit=limit
        )
        
        total = len(spaces)  # TODO: Add count query for pagination
        
        return SpaceListResponse(
            spaces=[SpaceResponse.from_orm(space) for space in spaces],
            total=total,
            page=skip // limit + 1,
            size=limit
        )
    except Exception as e:
        logger.error(f"Failed to get user spaces: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve spaces"
        )

@router.get("/{space_id}", response_model=SpaceResponse)
def get_space(
    space_id: str,
    db: Session = Depends(get_db_dependency),
    current_user = Depends(get_current_user)
) -> SpaceResponse:
    """Get a specific space by ID"""
    try:
        space = SpaceService.get_space_by_id(space_id, db)
        if not space:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Space not found"
            )
        
        # TODO: Add authorization check to ensure user can access this space
        
        return SpaceResponse.from_orm(space)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get space {space_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve space"
        )

@router.put("/{space_id}", response_model=SpaceResponse)
def update_space(
    space_id: str,
    space_data: SpaceUpdate,
    db: Session = Depends(get_db_dependency),
    current_user = Depends(get_current_user)
) -> SpaceResponse:
    """Update space configuration"""
    try:
        space = SpaceService.update_space(space_id, space_data, db)
        if not space:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Space not found"
            )
        
        return SpaceResponse.from_orm(space)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to update space {space_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to update space"
        )

@router.put("/{space_id}/storage", response_model=SpaceResponse)
def configure_space_storage(
    space_id: str,
    storage_config: StorageConfig,
    db: Session = Depends(get_db_dependency),
    current_user = Depends(get_current_user)
) -> SpaceResponse:
    """Configure external storage for a space"""
    try:
        space = SpaceService.configure_storage(
            space_id, 
            storage_config.dict(exclude_unset=True), 
            db
        )
        if not space:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Space not found"
            )
        
        return SpaceResponse.from_orm(space)
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to configure storage for space {space_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to configure storage"
        )

@router.get("/{space_id}/billing", response_model=SpaceBillingResponse)
def get_space_billing(
    space_id: str,
    db: Session = Depends(get_db_dependency),
    current_user = Depends(get_current_user)
) -> SpaceBillingResponse:
    """Get billing and usage information for a space"""
    try:
        billing = SpaceService.get_space_billing(space_id, db)
        if not billing:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Space not found or billing data unavailable"
            )
        
        return billing
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get billing for space {space_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve billing information"
        )

@router.get("/{space_id}/activity", response_model=SpaceActivityResponse)
def get_space_activity(
    space_id: str,
    limit: int = Query(50, ge=1, le=200),
    db: Session = Depends(get_db_dependency),
    current_user = Depends(get_current_user)
) -> SpaceActivityResponse:
    """Get recent activity for a space"""
    try:
        activity = SpaceService.get_space_activity(space_id, db, limit)
        if not activity:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Space not found or activity data unavailable"
            )
        
        return activity
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to get activity for space {space_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to retrieve activity data"
        )

@router.delete("/{space_id}", status_code=status.HTTP_204_NO_CONTENT)
def delete_space(
    space_id: str,
    db: Session = Depends(get_db_dependency),
    current_user = Depends(get_current_user)
):
    """Delete a space and all associated data"""
    try:
        success = SpaceService.delete_space(space_id, db)
        if not success:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Space not found"
            )
    except HTTPException:
        raise
    except Exception as e:
        logger.error(f"Failed to delete space {space_id}: {str(e)}")
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail="Failed to delete space"
        ) 