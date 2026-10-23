import streamlit as st
import pandas as pd

from github_client import fetch_repo, fetch_user_repos

# REMINDER for myself: Use Rubberducking

st.title("Specific Issues")
st.caption("Find personalized open source issues that match your skills and interests.")

repo_url = st.text_input(
    "GitHub repository URL",
    placeholder="https://github.com/owner/repository"
    )

if st.button("Fetch repository details", type="primary"):
    if not repo_url.strip():
        st.warning("Enter a repository URL.")
    else:
        try:
            with st.spinner("Fetching repository data..."):
                data = fetch_repo(repo_url)

            # Persist state under dict key
            st.session_state["repo_data"] = data
            st.success("Repository data fetched succesfully.")

        except Exception as e:
            st.error(str(e))

# Retreiving state key
data = st.session_state.get("repo_data")

if data:
    st.subheader(data["name"])

    if data["description"]:
        st.write(data["description"])

    st.markdown(f"[Open repository]({data['url']})")

    c1, c2 = st.columns(2)
    c1.metric("Stars", data["stars"])
    c2.metric("Open issues fetched", len(data["issues"]))

    st.write("### Languages")
    st.bar_chart(data["languages"])

    st.write("### Open Issues")

    rows = [
        {
            "Number": issue["number"],
            "Title": issue["title"],
            "Labels": ", ".join(label["name"] for label in issue["labels"]),
            "Comments": issue["comments"],
            "Updated": issue["updated_at"],
            "URL": issue["html_url"]
        }
        for issue in data["issues"]
    ]

    if rows:
        st.dataframe(
            pd.DataFrame(rows),
            width="stretch",
            hide_index=True,
            column_config={"URL": st.column_config.LinkColumn("Issue link")}
        )
    else:
        st.info("No open issues found.")

# For user profile
username = st.text_input(
    "Enter your GitHub username",
    placeholder="Username"
    )

if st.button("Fetch repositories details"):
    if not username.strip():
        st.warning("Enter an username.")
    else:
        try:
            with st.spinner("Fetching repositories details..."):
                repos = fetch_user_repos(username)

            # Persist state under dict key
            st.session_state["repos"] = repos
            st.success("Repositories details fetched succesfully.")

        except Exception as e:
            st.error(str(e))

repos = st.session_state.get("repos")


