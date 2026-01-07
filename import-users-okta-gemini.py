import asyncio
import httpx
import base64

# --- CONFIGURATION ---
OKTA_DOMAIN = "https://your-subdomain.okta.com"
API_TOKEN = "YOUR_OKTA_API_TOKEN"
GROUP_ID = "00gxxxxxxxxxxxx"
CONCURRENCY_LIMIT = 50  # Number of simultaneous requests

HEADERS = {
    "Accept": "application/json",
    "Content-Type": "application/json",
    "Authorization": f"SSWS {API_TOKEN}"
}

def parse_bcrypt(bcrypt_string):
    """
    Splits a standard BCrypt string (e.g., $2a$10$7623...) into components.
    Okta needs the Salt and the Hash value as Base64 encoded strings.
    """
    # Standard BCrypt format: $2a$[cost]$[22-char-salt][31-char-hash]
    parts = bcrypt_string.split('$')
    # parts[1] is version (2a), parts[2] is cost (10)
    work_factor = int(parts[2])
    
    # The remainder is salt + hash
    combined = parts[3]
    salt_str = combined[:22]
    hash_str = combined[22:]
    
    # Okta expects these to be Base64 encoded
    salt_b64 = base64.b64encode(salt_str.encode()).decode()
    hash_b64 = base64.b64encode(hash_str.encode()).decode()
    
    return work_factor, salt_b64, hash_b64

async def create_user(client, user_data, semaphore):
    async with semaphore:
        url = f"{OKTA_DOMAIN}/api/v1/users?activate=true&sendEmail=false"
        
        work_factor, salt, hash_val = parse_bcrypt(user_data['full_bcrypt_string'])
        
        payload = {
            "profile": {
                "firstName": user_data['first_name'],
                "lastName": user_data['last_name'],
                "email": user_data['email'],
                "login": user_data['email']
            },
            "credentials": {
                "password": {
                    "hash": {
                        "algorithm": "BCRYPT",
                        "workFactor": work_factor,
                        "salt": salt,
                        "value": hash_val
                    }
                }
            },
            "groupIds": [GROUP_ID]
        }

        try:
            response = await client.post(url, json=payload)
            
            if response.status_code == 200:
                user_id = response.json().get('id')
                # FORCE RESET: Expire the password immediately
                await client.post(f"{OKTA_DOMAIN}/api/v1/users/{user_id}/lifecycle/expire_password")
                return "CREATED", user_data['email']
            
            elif response.status_code == 409:
                # User already exists - Log and continue
                return "EXISTS", user_data['email']
            
            else:
                return "FAILED", f"{user_data['email']}: {response.text}"
                
        except Exception as e:
            return "ERROR", f"{user_data['email']}: {str(e)}"

async def main():
    # Example list of 15,000 users
    # In production, load this from your DB export
    users_to_import = [
        {
            "first_name": "Test",
            "last_name": "User",
            "email": f"user{i}@example.com",
            "full_bcrypt_string": "$2a$10$n978Ui5LSzqlzLUX7WXfyOTui1UXi6G5OT9/9.E9ViY0f56S.6B9G" 
        } for i in range(15000)
    ]

    semaphore = asyncio.Semaphore(CONCURRENCY_LIMIT)
    
    async with httpx.AsyncClient(headers=HEADERS, timeout=60.0) as client:
        tasks = [create_user(client, user, semaphore) for user in users_to_import]
        results = await asyncio.gather(*tasks)

    # --- FINAL REPORT ---
    counts = {"CREATED": 0, "EXISTS": 0, "FAILED": 0, "ERROR": 0}
    for status, _ in results:
        counts[status] = counts.get(status, 0) + 1

    print("\n--- Migration Summary ---")
    print(f"Total Users Processed: {len(users_to_import)}")
    print(f"Successfully Created:  {counts['CREATED']}")
    print(f"Skipped (Already in Okta): {counts['EXISTS']}")
    print(f"Failed/Errors:        {counts['FAILED'] + counts['ERROR']}")

if __name__ == "__main__":
    asyncio.run(main())