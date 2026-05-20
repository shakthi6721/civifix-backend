"""MongoDB indexes setup"""
import logging
from app.db.mongodb import db

logger = logging.getLogger(__name__)


async def create_indexes():
    """Create all necessary MongoDB indexes"""
    
    try:
        # Users collection indexes
        await db.users.create_index("email", unique=True)
        await db.users.create_index("mobile_number", unique=True)
        await db.users.create_index("district")
        await db.users.create_index("role")
        await db.users.create_index("status")
        await db.users.create_index("created_at")
        
        # OTP logs indexes
        await db.otp_logs.create_index("identifier")
        await db.otp_logs.create_index("created_at", expireAfterSeconds=604800)  # 7 days
        
        # Roles collection indexes
        await db.roles.create_index("name", unique=True)
        await db.roles.create_index("district")
        
        # Permissions collection indexes
        await db.permissions.create_index("name", unique=True)
        await db.permissions.create_index("category")
        
        # Refresh tokens indexes
        await db.refresh_tokens.create_index("user_id")
        await db.refresh_tokens.create_index("expires_at", expireAfterSeconds=0)
        
        # Complaints collection indexes
        await db.complaints.create_index("citizen_id")
        await db.complaints.create_index("district")
        await db.complaints.create_index("inspector_id")
        await db.complaints.create_index("status")
        await db.complaints.create_index("created_at")
        
        logger.info("MongoDB indexes created successfully")
        
    except Exception as e:
        logger.error(f"Failed to create indexes: {str(e)}")
        raise
