"""
Okta User Creation Script

This script creates a new user in Okta using the Okta Python SDK.
"""

import asyncio
import os
from dotenv import load_dotenv
from okta.client import Client as OktaClient
from okta.models import UserProfile, CreateUserRequest, PasswordCredential

# Load environment variables
load_dotenv()


async def create_okta_user(first_name, last_name, email, login=None, activate=True, password=None, group_id=None):
    """
    Create a new user in Okta.
    
    Args:
        first_name (str): User's first name
        last_name (str): User's last name
        email (str): User's email address
        login (str, optional): User's login. Defaults to email if not provided
        activate (bool, optional): Whether to activate the user immediately. Defaults to True
        password (str, optional): User's password. If provided, user will be ACTIVE immediately.
                                  If not provided and activate=True, user will be PROVISIONED and receive activation email.
        group_id (str, optional): Group ID to assign the user to during creation. Defaults to None.
    
    Returns:
        tuple: (user object, response, error) or None if error occurred
    """
    # Get Okta configuration from environment variables
    okta_domain = os.getenv('OKTA_DOMAIN')
    api_token = os.getenv('OKTA_API_TOKEN')
    
    if not okta_domain or not api_token:
        print("Error: OKTA_DOMAIN and OKTA_API_TOKEN must be set in .env file")
        return None
    
    # Initialize the Okta client
    config = {
        'orgUrl': okta_domain,
        'token': api_token
    }
    
    try:
        client = OktaClient(config)
        
        # Use email as login if login not provided
        if login is None:
            login = email
        
        # Define user profile information using keyword arguments
        user_profile = UserProfile(
            firstName=first_name,
            lastName=last_name,
            email=email,
            login=login
        )
        
        # Create user request using keyword arguments
        # If password is provided, include credentials for immediate activation
        # If group_id is provided, include it in the request
        request_kwargs = {
            'profile': user_profile
        }
        
        if password==2:
            password_credential = PasswordCredential(
                value=password
            )
            request_kwargs['credentials'] = {
                'password': password_credential
            }
        
        if group_id:
            # Include groupIds in the create request
            request_kwargs['groupIds'] = [group_id]
        
        create_user_request = CreateUserRequest(**request_kwargs)
        
        # Create user with activate parameter as a boolean keyword argument
        # When activate=True and password is provided, user will be ACTIVE
        # When activate=True and password is None, user will be PROVISIONED (activation email sent)
        # When activate=False, user will be STAGED
        user, response, error = await client.create_user(create_user_request, activate=activate)
        
        if error:
            print(f"Error creating user: {error}")
            return None
        else:
            print(f"User created successfully!")
            print(f"  User ID: {user.id}")
            print(f"  Name: {user.profile.first_name} {user.profile.last_name}")
            print(f"  Email: {user.profile.email}")
            print(f"  Login: {user.profile.login}")
            print(f"  Status: {user.status}")
            if activate and not password:
                print(f"  Note: Activation email has been sent to {email}")
                print(f"        User can set their password via the activation link.")
            if group_id:
                print(f"  Group ID: {group_id} (included in creation request)")
            
            return user, response, error
            
    except Exception as e:
        print(f"Exception occurred: {str(e)}")
        return None


async def main():
    """Main function to create a user with example data."""
    print("Okta User Creation Tool")
    print("=" * 50)
    
    # Example user data - modify as needed
    first_name = 'Shah' #input("Enter first name (or press Enter for 'John'): ").strip() or "John"
    last_name = 'Khan' #input("Enter last name (or press Enter for 'Doe'): ").strip() or "Doe"
    email = 'voyiwiy272@mucate.com' #input("Enter email (or press Enter for 'john.doe@example.com'): ").strip() or "john.doe@example.com"
    password = 'Suaj123!' #input("Enter password (or press Enter for 'Password123!'): ").strip() or "Password123!"
    group_id = '00gxoa95f5IB4NljV697'  # input("Enter group ID (or press Enter to skip): ").strip() or None

    activate_input = 'y' #input("Activate user immediately? (y/n, default: y): ").strip().lower()
    activate = activate_input != 'n'
    
    await create_okta_user(
        first_name=first_name,
        last_name=last_name,
        email=email,
        activate=activate,
        password=None,
        group_id=group_id
    )


if __name__ == "__main__":
    asyncio.run(main())

