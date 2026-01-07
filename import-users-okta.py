import requests
import time
from concurrent.futures import ThreadPoolExecutor

OKTA_DOMAIN = "https://your-org.okta.com"
API_TOKEN = "YOUR_API_TOKEN"
GROUP_ID = "00g1abcdEFGH12345"

HEADERS = {
    "Authorization": f"SSWS {API_TOKEN}",
    "Content-Type": "application/json"
}

def get_user_by_login(email):
    url = f"{OKTA_DOMAIN}/api/v1/users/{email}"
    r = requests.get(url, headers=HEADERS)
    return r.json() if r.status_code == 200 else None


def add_user_to_group(user_id):
    url = f"{OKTA_DOMAIN}/api/v1/groups/{GROUP_ID}/users/{user_id}"
    requests.put(url, headers=HEADERS)


def expire_password(user_id):
    url = f"{OKTA_DOMAIN}/api/v1/users/{user_id}/lifecycle/expire_password?tempPassword=false"
    requests.post(url, headers=HEADERS)


def create_and_assign(user):
    create_url = f"{OKTA_DOMAIN}/api/v1/users?activate=true"

    payload = {
        "profile": {
            "login": user["email"],
            "email": user["email"],
            "firstName": user["first_name"],
            "lastName": user["last_name"]
        },
        "groupIds": [GROUP_ID],
        "credentials": {
            "password": {
                "hash": {
                    "algorithm": "BCRYPT",
                    "value": user["bcrypt_hash"]
                }
            }
        }
    }

    r = requests.post(create_url, headers=HEADERS, json=payload)

    # ✅ Created
    if r.status_code in (200, 201):
        user_id = r.json()["id"]
        expire_password(user_id)
        print(f"✅ Created + Grouped: {user['email']}")
        return

    # ⏭️ Already exists
    if r.status_code == 400 and "already exists" in r.text.lower():
        existing_user = get_user_by_login(user["email"])
        if existing_user:
            user_id = existing_user["id"]
            add_user_to_group(user_id)
            expire_password(user_id)
            print(f"⏭️ Exists → Grouped: {user['email']}")
        return

    # ⏳ Rate limit
    if r.status_code == 429:
        time.sleep(2)
        return create_and_assign(user)

    print(f"❌ Failed ({user['email']}): {r.status_code} {r.text}")


def migrate_users(users):
    with ThreadPoolExecutor(max_workers=5) as executor:
        executor.map(create_and_assign, users)
