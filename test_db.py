# test_db.py

from utils import db_manager

def main():
    print("🔄 Initializing database...")
    db_manager.init_db()
    print("✅ Tables created or already exist.")

    # Try registering a test user
    print("\n🔄 Registering test user...")
    if db_manager.register_user("testuser", "testpass"):
        print("✅ Test user created.")
    else:
        print("⚠️ Test user already exists.")

    # Try logging in
    print("\n🔄 Logging in with test user...")
    user = db_manager.login_user("testuser", "testpass")
    if user:
        print(f"✅ Login successful: {user}")
    else:
        print("❌ Login failed.")

    # Add a sample diary entry
    print("\n🔄 Adding test diary entry...")
    db_manager.add_entry(user[0], "My First Entry", "This is a test diary entry.")
    print("✅ Entry added.")

    # Fetch entries
    print("\n🔄 Fetching diary entries...")
    entries = db_manager.get_entries(user[0])
    for e in entries:
        print(f"📖 {e}")

if __name__ == "__main__":
    main()
