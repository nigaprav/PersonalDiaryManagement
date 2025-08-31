import streamlit as st
from datetime import datetime
from utils.db_manager import init_db, register_user, login_user, add_entry, get_entries, update_entry, delete_entry
from zoneinfo import ZoneInfo
IST = ZoneInfo("Asia/Kolkata")
# Initialize database
init_db()

# ------------------- LOGIN PAGE -------------------

def login_ui():
    st.title("📖 Personal Diary")
    st.markdown("### Please login to continue")

    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        user = login_user(username, password)
        if user:
            st.session_state.logged_in = True
            st.session_state.username = user[1]
            st.session_state.user_id = user[0]
            st.rerun()
        else:
            st.error("Invalid username or password")

    st.markdown("---")
    st.subheader("New here?")
    new_user = st.text_input("Choose a username")
    new_pass = st.text_input("Choose a password", type="password")

    if st.button("Register"):
        if register_user(new_user, new_pass):
            st.success("✅ Registration successful! Please login.")
        else:
            st.error("⚠️ Username already exists")


# ------------------- MAIN UI -------------------

def add_ui():
    st.subheader("➕ Add New Entry")
    title = st.text_input("Title")
    content = st.text_area("Content", height=200)
    if st.button("Save Entry"):
        if title and content:
            add_entry(st.session_state.user_id, title, content)
            st.success("✅ Entry saved successfully!")
        else:
            st.warning("⚠️ Please fill in both fields.")


def view_ui():
    st.subheader("📂 Your Entries")

    col1, col2 = st.columns([2, 1])  # Left: entries, Right: calendar

    with col2:
        st.markdown("### 📅 Select a Date")
        selected_date = st.date_input("Filter by date", datetime.now(IST).date())

    with col1:
        entries = get_entries(st.session_state.user_id)

        filtered = [e for e in entries if datetime.strptime(e[3], "%d %b %Y, %I:%M %p").replace(tzinfo=IST).date() == selected_date]

        if not filtered:
            st.info("No entries for this date.")
            return

        for entry in filtered:
            ts = datetime.strptime(entry[3], "%d %b %Y, %I:%M %p").replace(tzinfo=IST)
            with st.expander(f"📌 {entry[1]}  —  *{ts.strftime('%d %b %Y, %I:%M %p')}*"):
                st.write(entry[2])
                if st.button("❌ Delete", key=f"del_{entry[0]}"):
                    delete_entry(entry[0])
                    st.success("Entry deleted.")
                    st.rerun()


def update_ui():
    st.subheader("✏️ Update Diary Entry")
    entries = get_entries(st.session_state.user_id)
    if not entries:
        st.info("You don’t have any entries to update.")
        return

    entry_map = {f"{e[1]} ({e[3]})": e for e in entries}
    choice = st.selectbox("Select entry", list(entry_map.keys()))
    entry = entry_map[choice]

    new_title = st.text_input("Title", value=entry[1])
    new_content = st.text_area("Content", value=entry[2], height=200)

    if st.button("Update Entry"):
        update_entry(entry[0], new_title, new_content)
        st.session_state.update_msg = f"✅ '{new_title}' updated successfully!"

    if "update_msg" in st.session_state:
        st.success(st.session_state.update_msg)


# ------------------- LOGOUT (Top Right) -------------------

def topbar_logout():
    st.markdown(
        f"""
        <div style="display:flex; justify-content:space-between; align-items:center;
                    background:#4a90e2; padding:12px; border-radius:8px; color:white;">
            <h2 style="margin:0;">📔 Personal Diary</h2>
            <div>
                👋 {st.session_state.username}
                <form action="/" method="get" style="display:inline;">
                    <button type="submit" style="margin-left:12px; background:#e74c3c; color:white; border:none; 
                                                 padding:6px 12px; border-radius:6px; cursor:pointer;">
                        🚪 Logout
                    </button>
                </form>
            </div>
        </div>
        """,
        unsafe_allow_html=True
    )

    # Reset session on logout
    if st.query_params:
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        st.rerun()


# ------------------- MAIN -------------------

def main():
    if "logged_in" not in st.session_state:
        st.session_state.logged_in = False

    if not st.session_state.logged_in:
        login_ui()
    else:
        topbar_logout()
        tabs = st.tabs(["➕ Add", "📂 View", "✏️ Update"])
        with tabs[0]:
            add_ui()
        with tabs[1]:
            view_ui()
        with tabs[2]:
            update_ui()


if __name__ == "__main__":
    main()
