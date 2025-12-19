# Okta User Creation Project

This Python project uses the Okta SDK and API to create users in Okta with basic required information.

## Prerequisites

- Python 3.10 or higher
- An Okta developer account or Okta organization
- An Okta API token

## Setup

### 1. Install Dependencies

Create a virtual environment (recommended):

```bash
# Windows
python -m venv venv
venv\Scripts\activate

# macOS/Linux
python3 -m venv venv
source venv/bin/activate
```

Install the required packages:

```bash
pip install -r requirements.txt
```

### 2. Configure Okta Credentials

1. Copy the example environment file:
   ```bash
   copy env.example .env
   ```
   (On macOS/Linux: `cp env.example .env`)

2. Edit the `.env` file and add your Okta credentials:
   - **OKTA_DOMAIN**: Your Okta organization URL (e.g., `https://your-company.okta.com`)
   - **OKTA_API_TOKEN**: Your Okta API token

### 3. Get Your Okta API Token

To generate an Okta API token, follow these steps:

#### Step-by-Step Instructions:

1. **Log in to Okta Admin Console**
   - Go to your Okta organization URL (e.g., `https://your-company.okta.com`)
   - Sign in with your administrator credentials

2. **Navigate to API Tokens**
   - Click on the **Admin** button (or user menu) in the top-right corner
   - In the left sidebar, go to **Security** → **API** → **Tokens**
   - Alternatively, you can directly access: `https://your-company.okta.com/admin/access/api/tokens`

3. **Create a New Token**
   - Click the **Create Token** button
   - Enter a descriptive name for your token (e.g., "User Creation Script" or "Python SDK Token")
   - Click **Create Token**

4. **Copy the Token**
   - **IMPORTANT**: The token will be displayed only once immediately after creation
   - Copy the token immediately and store it securely
   - If you lose it, you'll need to delete and create a new one

5. **Add Token to Your `.env` File**
   - Paste the token as the value for `OKTA_API_TOKEN` in your `.env` file

#### Alternative: Using Okta Developer Console

If you're using an Okta Developer account:

1. Go to [developer.okta.com](https://developer.okta.com)
2. Sign in to your developer account
3. Navigate to **API** → **Tokens** in the left menu
4. Follow the same steps above to create and copy your token

#### Important Security Notes:

- ⚠️ **The token is shown only once** - copy it immediately
- 🔒 **Keep your API token secure** - treat it like a password
- 🚫 **Never commit tokens to version control** - always use `.env` file (which is in `.gitignore`)
- 🔄 **Rotate tokens regularly** - delete old tokens and create new ones periodically
- 👤 **Use least privilege** - only grant necessary permissions
- 🗑️ **Delete unused tokens** - remove tokens that are no longer needed

#### Finding Your Okta Domain:

Your Okta domain is typically in one of these formats:
- `https://your-company.okta.com` (for production)
- `https://dev-123456.okta.com` (for developer accounts)

You can find it in:
- The URL when you're logged into Okta
- The **Settings** → **General** section of the Admin Console

## Usage

Run the script:

```bash
python create_user.py
```

The script will prompt you for:
- First name
- Last name
- Email address
- Whether to activate the user immediately

### Programmatic Usage

You can also import and use the `create_okta_user` function in your own code:

```python
import asyncio
from create_user import create_okta_user

async def example():
    await create_okta_user(
        first_name="Jane",
        last_name="Smith",
        email="jane.smith@example.com",
        activate=True
    )

asyncio.run(example())
```

## Required User Information

The script creates users with the following required fields:
- **First Name** (`firstName`)
- **Last Name** (`lastName`)
- **Email** (`email`)
- **Login** (`login`) - defaults to email if not specified

## User Activation

By default, users are created and activated immediately. To create a user in a staged state (not activated), set `activate=False` when calling the function.

## Error Handling

The script includes error handling for:
- Missing configuration (domain or API token)
- API errors from Okta
- Network issues
- Invalid user data

## Project Structure

```
okta-user-creation/
├── create_user.py      # Main script for creating users
├── requirements.txt    # Python dependencies
├── env.example         # Example environment configuration
├── .env                # Your actual configuration (not in git)
├── .gitignore          # Git ignore file
└── README.md           # This file
```

## Additional Resources

- [Okta Python SDK Documentation](https://github.com/okta/okta-sdk-python)
- [Okta Users API Documentation](https://developer.okta.com/docs/api/resources/users)
- [Okta Developer Portal](https://developer.okta.com/)

## Security Notes

- Never commit your `.env` file to version control
- Keep your API token secure
- Use environment variables or secure secret management in production
- Rotate API tokens regularly
- Follow the principle of least privilege when creating API tokens

## License

This project is provided as-is for educational and development purposes.

