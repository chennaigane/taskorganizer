
import streamlit as st
import pandas as pd
from datetime import datetime
import io

# Users
users = {
    "admin" : "admin123",
    "Ganesh": "team123",
    "Raghav": "team123",
    "Dhana" : "team123",
    "New1"  : "team123"
}

# Session state initialization
if "logged_in" not in st.session_state:
    st.session_state.logged_in = False
if "user" not in st.session_state:
    st.session_state.user = ""
if "task_data" not in st.session_state:
    st.session_state.task_data = pd.DataFrame(columns=[
        "Task ID", "Assigned To", "Task", "Due Date", "Status", "Comments", "Last Updated"
    ])

# Login Page
st.title("🧰 Task allocation & Tracking system")


if not st.session_state.logged_in:
    username = st.text_input("Username")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        if username in users and users[username] == password:
            st.session_state.logged_in = True
            st.session_state.user = username
            st.success(f"Welcome {username}!")
            st.rerun()
        else:
            st.error("Invalid username or password")

else:
    username = st.session_state.user
    is_admin = username == "admin"
    st.success(f"Logged in as: {username}")

    # Admin Page
    if is_admin:
        st.header("📌 Assign New Task")
        with st.form("task_form"):
            task_id = f"TASK-{len(st.session_state.task_data) + 1}"
            assigned_to = st.selectbox("Assign To", [u for u in users if u != "admin"])
            task = st.text_input("Task Description")
            due_date = st.date_input("Due Date")
            submit = st.form_submit_button("Assign Task")

            if submit and task.strip():
                new_task = {
                    "Task ID": task_id,
                    "Assigned To": assigned_to,
                    "Task": task,
                    "Due Date": due_date.strftime("%Y-%m-%d"),
                    "Status": "Not Started",
                    "Comments": "",
                    "Last Updated": datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                }
                st.session_state.task_data = pd.concat([
                    st.session_state.task_data,
                    pd.DataFrame([new_task])
                ], ignore_index=True)
                st.success("✅ Task assigned!")

        st.subheader("📋 All Tasks")
        st.dataframe(st.session_state.task_data)

        # Excel download
        output = io.BytesIO()
        st.session_state.task_data.to_excel(output, index=False, engine='openpyxl')
        output.seek(0)
        st.download_button("⬇️ Download Excel", data=output, file_name="tasks.xlsx")

    # Team Page
    else:
        st.header("🧑‍💻 Your Tasks")
        tasks = st.session_state.task_data[st.session_state.task_data["Assigned To"] == username]

        if tasks.empty:
            st.info("No tasks assigned.")
        else:
            for i, row in tasks.iterrows():
                with st.expander(f"{row['Task ID']} - {row['Task']}"):
                    st.write(f"📅 Due Date: {row['Due Date']}")
                    st.write(f"📌 Status: {row['Status']}")
                    st.write(f"📝 Comments: {row['Comments']}")

                    status = st.selectbox("Update Status", ["Not Started", "In Progress", "Completed"], index=["Not Started", "In Progress", "Completed"].index(row["Status"]), key=f"status_{i}")
                    comment = st.text_area("Update Comment", row["Comments"], key=f"comment_{i}")

                    if st.button("Update Task", key=f"update_{i}"):
                        st.session_state.task_data.at[i, "Status"] = status
                        st.session_state.task_data.at[i, "Comments"] = comment
                        st.session_state.task_data.at[i, "Last Updated"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                        st.success("Task updated ✅")

    if st.button("Logout"):
        st.session_state.logged_in = False
        st.session_state.user = ""
        st.rerun()
