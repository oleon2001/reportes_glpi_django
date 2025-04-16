import bcrypt
import mysql.connector
import logging
from django.conf import settings
from django.contrib.auth.models import User
from django.contrib.auth.backends import BaseBackend
from django.contrib.auth.hashers import make_password

# Set up logging
logger = logging.getLogger(__name__)

class GLPIAuthBackend(BaseBackend):
    """
    Custom authentication backend that authenticates against GLPI database.
    Uses bcrypt to verify passwords that were hashed with PHP's password_hash().
    """
    
    def authenticate(self, request, username=None, password=None):
        if not username or not password:
            logger.warning("Authentication attempt with missing username or password")
            return None
            
        try:
            # Connect to the GLPI database using the 'glpi' database configuration
            conn = mysql.connector.connect(
                user=settings.DATABASES['glpi']['USER'],
                password=settings.DATABASES['glpi']['PASSWORD'],
                host=settings.DATABASES['glpi']['HOST'],
                database=settings.DATABASES['glpi']['NAME'],
                port=int(settings.DATABASES['glpi']['PORT'])  # Ensure port is an integer
            )
            
            cursor = conn.cursor(dictionary=True)
            
            # Query the GLPI users table using the exact query provided
            cursor.execute(
                "SELECT gu.name, gu.password FROM glpi_users gu WHERE gu.name = %s",
                (username,)
            )
            
            user_data = cursor.fetchone()
            cursor.close()
            conn.close()
            
            if not user_data:
                logger.warning(f"User not found in GLPI database: {username}")
                return None
                
            # Verify the password using bcrypt
            # PHP's password_hash() with PASSWORD_DEFAULT uses bcrypt
            # The stored hash is in the format: $2y$... which is compatible with bcrypt
            stored_hash = user_data['password']
            
            # Check if the password matches
            if bcrypt.checkpw(password.encode('utf-8'), stored_hash.encode('utf-8')):
                logger.info(f"Successful authentication for user: {username}")
                
                # Get or create a Django user
                try:
                    user = User.objects.get(username=username)
                    logger.info(f"Existing Django user found: {username}")
                except User.DoesNotExist:
                    # Create a new Django user
                    user = User.objects.create(
                        username=username,
                        email=f"{username}@example.com",  # Placeholder email
                        password=make_password(password)  # Hash the password for Django
                    )
                    logger.info(f"Created new Django user: {username}")
                
                return user
            else:
                logger.warning(f"Invalid password for user: {username}")
                
            return None
            
        except mysql.connector.Error as e:
            logger.error(f"MySQL error during authentication: {str(e)}")
            return None
        except Exception as e:
            logger.error(f"Unexpected error during authentication: {str(e)}")
            return None
    
    def get_user(self, user_id):
        try:
            return User.objects.get(pk=user_id)
        except User.DoesNotExist:
            return None 