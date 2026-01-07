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


async def create_okta_user(first_name, last_name, email, login=None, activate=True, password=None, group_id=None, send_email=True):
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
        send_email (bool, optional): Whether to send activation email. Defaults to True.
                                     Set to False to create active user without password and no email.
    
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
        
        if password:
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
        # If send_email=False and activate=True, create as STAGED then activate without email
        if activate and not password and not send_email:
            # Create user as STAGED first (no activation email will be sent)
            user, response, error = await client.create_user(
                create_user_request, 
                activate=False
            )
            
            if error:
                print(f"Error creating user: {error}")
                return None
            
            # Then activate the user without sending email using direct HTTP API call
            # This is more reliable than using the SDK methods which may not support sendEmail parameter
            print(f"Activating user {user.id} without sending email...")
            try:
                import aiohttp
                
                # Make direct HTTP POST call to Okta API
                url = f"{okta_domain}/api/v1/users/{user.id}/lifecycle/activate"
                headers = {
                    "Authorization": f"SSWS {api_token}",
                    "Content-Type": "application/json",
                    "Accept": "application/json"
                }
                
                async with aiohttp.ClientSession() as session:
                    async with session.post(
                        url,
                        headers=headers,
                        params={"sendEmail": "false"}
                    ) as resp:
                        response_text = await resp.text()
                        
                        if resp.status in [200, 204]:
                            # Activation successful - fetch updated user to check status
                            try:
                                updated_user, _, _ = await client.get_user(user.id)
                                user = updated_user
                                
                                if user.status == "ACTIVE":
                                    print(f"[SUCCESS] User is ACTIVE and ready to use.")
                                elif user.status == "PENDING":
                                    print(f"[SUCCESS] User is PENDING (expected for passwordless users).")
                                    print(f"  User can log in via widget and will be prompted to set password.")
                                    print(f"  After setting password, user will become ACTIVE.")
                                elif user.status == "PROVISIONED":
                                    print(f"[SUCCESS] User is PROVISIONED.")
                                    print(f"  User can log in via widget and will be prompted to set password.")
                                else:
                                    print(f"[SUCCESS] User activated. Status: {user.status}")
                                    print(f"  User can log in via widget to set password.")
                            except Exception as fetch_ex:
                                print(f"[SUCCESS] Activation API call succeeded (status {resp.status}).")
                                print(f"  Note: Could not fetch updated user object: {str(fetch_ex)}")
                        else:
                            raise Exception(f"HTTP {resp.status}: {response_text}")
                            
            except ImportError:
                print(f"[ERROR] aiohttp is required for activation. Installing...")
                print(f"  Please run: pip install aiohttp")
                print(f"  User created in STAGED status. You may need to activate manually.")
            except Exception as activate_ex:
                error_msg = str(activate_ex)
                print(f"[ERROR] Error activating user: {error_msg}")
                print(f"  Attempting to check current user status...")
                # Fetch user to check current status
                try:
                    updated_user, _, _ = await client.get_user(user.id)
                    print(f"  Current user status: {updated_user.status}")
                    user = updated_user
                    
                    if updated_user.status == "ACTIVE":
                        print(f"  [SUCCESS] User is ACTIVE!")
                    elif updated_user.status == "PENDING":
                        print(f"  [INFO] User is PENDING (this is expected for passwordless users).")
                        print(f"  User can log in via widget and will be prompted to set password.")
                        print(f"  After setting password, user will become ACTIVE.")
                    elif updated_user.status == "PROVISIONED":
                        print(f"  [INFO] User is PROVISIONED.")
                        print(f"  User can log in via widget and will be prompted to set password.")
                    else:
                        print(f"  [INFO] User status: {updated_user.status}")
                        print(f"  User can log in via widget to set password.")
                except Exception as fetch_ex:
                    print(f"  Could not fetch user status: {str(fetch_ex)}")
        else:
            # Normal creation flow
            user, response, error = await client.create_user(
                create_user_request, 
                activate=activate
            )
        
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
                if send_email:
                    print(f"  Note: Activation email has been sent to {email}")
                    print(f"        User can set their password via the activation link.")
                else:
                    print(f"  Note: User is ACTIVE without password. No activation email sent.")
                    print(f"        User will set password and authenticator app on first login via widget.")
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
        group_id=group_id,
        send_email=False  # Don't send activation email - user will set password on first login
    )


if __name__ == "__main__":
    asyncio.run(main())

