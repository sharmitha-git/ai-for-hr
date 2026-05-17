import streamlit as st
import requests
import pandas as pd
import time

API_BASE_URL = "http://backend:8000"


# =========================================
# Page Config
# =========================================

st.set_page_config(
    page_title="HireGuard AI",
    layout="wide"
)


# =========================================
# Sidebar Navigation
# =========================================

page = st.sidebar.radio(
    "Navigation",
    [
        "Hiring Workspace",
        "Governance Console",
        "AI Hiring Copilot"
    ]
)


# =========================================
# Global Header
# =========================================

st.title("HireGuard AI")

st.subheader(
    "Governance-Aware Multi-Agent Hiring Copilot"
)

st.markdown("---")



# =========================================
# Hiring Workspace
# =========================================

if page == "Hiring Workspace":

    st.header(
        "Hiring Workspace"
    )

    # =====================================
    # Create Job
    # =====================================

    st.subheader(
        "Create Job"
    )

    with st.form(
        "create_job_form"
    ):

        title = st.text_input(
            "Job Title"
        )

        description = st.text_area(
            "Job Description"
        )

        required_skills = st.text_input(
            "Required Skills (comma separated)"
        )

        create_job_btn = st.form_submit_button(
            "Create Job"
        )

        if create_job_btn:

            response = requests.post(
                f"{API_BASE_URL}/create-job",
                data={

                    "title":
                        title,

                    "description":
                        description,

                    "required_skills":
                        required_skills
                }
            )

            if response.status_code == 200:

                st.success(
                    "Job created successfully"
                )

                st.json(
                    response.json()
                )

            else:

                st.error(
                    response.text
                )

    st.markdown("---")

    # =====================================
    # Upload Candidate
    # =====================================

    st.subheader(
        "Upload Candidate"
    )

    jobs_response = requests.get(
        f"{API_BASE_URL}/jobs"
    )

    jobs_data = []

    if jobs_response.status_code == 200:

        jobs_data = jobs_response.json()

    jobs_options = {}

    for job in jobs_data:

        option_label = (
            f"{job['id']}: {job['title']}"
        )

        jobs_options[
            option_label
        ] = job["id"]

    with st.form(
        "upload_candidate_form"
    ):

        full_name = st.text_input(
            "Full Name"
        )

        email = st.text_input(
            "Email"
        )

        phone = st.text_input(
            "Phone"
        )

        skills = st.text_input(
            "Skills"
        )

        selected_job = st.selectbox(
            "Select Job",
            list(
                jobs_options.keys()
            )
        )

        uploaded_file = st.file_uploader(
            "Upload Resume PDF",
            type=["pdf"]
        )

        upload_btn = st.form_submit_button(
            "Upload Candidate"
        )

        if upload_btn:

            if uploaded_file is None:

                st.warning(
                    "Please upload a resume"
                )

            else:

                job_id = jobs_options[
                    selected_job
                ]

                files = {

                    "file": (
                        uploaded_file.name,
                        uploaded_file,
                        "application/pdf"
                    )
                }

                data = {

                    "full_name":
                        full_name,

                    "email":
                        email,

                    "phone":
                        phone,

                    "skills":
                        skills,

                    "job_id":
                        job_id
                }

                response = requests.post(
                    f"{API_BASE_URL}/upload-candidate",
                    data=data,
                    files=files
                )

                if response.status_code == 200:

                    st.success(
                        "Candidate uploaded successfully"
                    )

                    st.json(
                        response.json()
                    )

                else:

                    st.error(
                        response.text
                    )

    st.markdown("---")

    # =====================================
    # Recruiter Evaluation Dashboard
    # =====================================

    st.header(
        "Recruiter Evaluation Dashboard"
    )

    jobs_response = requests.get(
        f"{API_BASE_URL}/jobs"
    )

    jobs_data = []

    if jobs_response.status_code == 200:

        jobs_data = jobs_response.json()

    jobs_options = {}

    for job in jobs_data:

        option_label = (
            f"{job['id']}: {job['title']}"
        )

        jobs_options[
            option_label
        ] = job["id"]

    selected_job = st.selectbox(
        "Select Job",
        list(
            jobs_options.keys()
        ),
        key="recruiter_job_select"
    )

    job_id = jobs_options[
        selected_job
    ]

    if st.button(
        "Evaluate Candidates"
    ):

        response = requests.get(
            f"{API_BASE_URL}/evaluate-job/{job_id}"
        )

        if response.status_code == 200:

            results = response.json()
            st.session_state[
                "evaluation_results"
            ] = results
            st.success(
                "Evaluation completed"
            )
        else:
            st.error(
                response.text  )

    if "evaluation_results" in st.session_state:

        results = st.session_state[
            "evaluation_results"
        ]

         
        if len(results) == 0:

            st.warning(
                "No applications found"
            )

        else:

            df = pd.DataFrame(results)

            st.dataframe(
                df,
                width="stretch"
            )

            st.markdown("---")
            
            st.subheader("Governance Status Summary")
            selected_candidate = st.selectbox( 
                "Select Candidate for Governance Status",
                options = [
                    row["candidate_name"] for row in results
                ]
            )
            selected_row = next(    
                row for row in results
                if row["candidate_name"] == selected_candidate
            )
            col1, col2, col3, col4= st.columns(4)

            with col1:
                st.metric(
                    "Semantic Score",
                    f'{selected_row["semantic_score"]}%'
                )        

            with col2:  
                st.metric(
                    "Keyword Score",
                    f'{selected_row["keyword_score"]}%'
                )
            with col3:  
                st.metric(
                    "Final Score",
                    f'{selected_row["final_score"]}%'
                )      
            with col4:  
                st.metric(
                    "Confidence Score",
                    f'{selected_row["confidence_score"]}%'
                )
            st.info(
                f'Governance Decision: '
                f'{selected_row["governance_status"]}'
                )
            st.write(

                f'Explanation: {selected_row["explanation"]}'

            )

            if selected_row.get("recommendation"):
                st.success(
                    f"Decision Support: {selected_row['recommendation']}"
                )

            if selected_row.get("decision_boundary"):
                st.warning(
                    selected_row["decision_boundary"]
                )

            if selected_row.get("policy_evidence"):
                with st.expander(
                    "Policy Evidence"
                ):
                    for snippet in selected_row[
                        "policy_evidence"
                    ]:
                        st.write(snippet)
            
            candidate_response = requests.get(
                f"{API_BASE_URL}/candidate/{selected_row['candidate_id']}"
            )
            if candidate_response.status_code == 200:
                candidate_data = candidate_response.json()
                st.subheader("Candidate Details")
                st.write(f"Full Name: {candidate_data['full_name']}")
                st.write(f"Email: {candidate_data['email']}")
                st.write(f"Phone: {candidate_data['phone']}")
                st.write(f"Skills: {candidate_data['skills']}")
                st.write(f"Masked Resume: {candidate_data['masked_resume']}")

                                               

                # =============================
                # Recruiter Decision
                # =============================

            st.subheader(
                    "Recruiter Decision"
                )

            application_options = {}

            active_results = [

                    row for row in results

                    if row[
                        "application_status"
                    ] not in [

                        "SHORTLISTED",
                        "REJECTED"
                    ]
                ]

            if len(active_results) == 0:

                    st.info(
                        "No pending applications remaining"
                    )

            else:

                    for row in active_results:

                        label = (
                            f"Application "
                            f"{row['application_id']} "
                            f"- "
                            f"{row['candidate_name']}"
                        )

                        application_options[
                            label
                        ] = row[
                            "application_id"
                        ]

                    selected_application = (
                        st.selectbox(

                            "Select Application",

                            list(
                                application_options.keys()
                            ),

                            key=(
                                f"application_select_"
                                f"{job_id}"
                            )
                        )
                    )

                    application_id = (
                        application_options[
                            selected_application
                        ]
                    )

                    selected_row = next (

                        row for row in results

                        if row["application_id"] == application_id
                    )

                    status_options = [

                        "PENDING",
                        "SHORTLISTED",
                        "REJECTED"
                    ]
                    current_index = status_options.index(
                        selected_row[
                            "application_status"
                        ]
                    )

                    status = st.selectbox(

                        "Application Status",

                        status_options,
                        index=current_index,
                        key=(
                            f"status_select_"
                            f"{application_id}"
                        )   
                    )

                    reviewer_name = st.text_input(
                        "Reviewer Name",
                        value="human_reviewer",
                        key=(
                            f"reviewer_name_"
                            f"{application_id}"
                        )
                    )

                    reviewer_notes = st.text_area(
                        "Reviewer Notes",
                        key=(
                            f"reviewer_notes_"
                            f"{application_id}"
                        )
                    )

                    if st.button(
                        "Update Application Status",key=f"update_status_btn_{application_id}"
                    ):
                        st.write("Updating application status...",application_id)
                        st.write("Selected status:",status )

                        update_response = (
                            requests.put(

                                f"{API_BASE_URL}/update-application-status",

                                json={

                                    "application_id":
                                        application_id,

                                    "application_status":
                                        status,

                                    "reviewer_name":
                                        reviewer_name,

                                    "reviewer_notes":
                                        reviewer_notes
                                }
                            )
                        )

                        if (
                            update_response.status_code
                            == 200
                        ):

                            st.success(
                                "Application updated successfully"
                            )

                            st.json(
                                update_response.json()
                            )
                            verify_response = requests.get(
                                f"{API_BASE_URL}/applications"
                            )
                            st.write(verify_response.json())

                            time.sleep(2)

                            st.rerun()

                        else:

                            st.error(
                                update_response.text
                            )

  
# =========================================
# Governance Console
# =========================================

if page == "Governance Console":

    st.header(
        "Governance Console"
    )

    # =====================================
    # Governance Audit Logs
    # =====================================
    st.subheader(
        "Application Governance Summary"
    )

    applications_response = requests.get(
        f"{API_BASE_URL}/applications"
    )

    if applications_response.status_code == 200:

        applications_data = (
            applications_response.json()
        )

        if len(applications_data) == 0:

            st.info(
                "No applications available"
            )

        else:

            applications_df = pd.DataFrame(
                applications_data
            )

            st.dataframe(
                applications_df,
                width="stretch"
            )

    else:

        st.error(
            applications_response.text
        )

    st.markdown("---")


    st.subheader(
        "Governance Audit Logs"
    )

    audit_response = requests.get(
        f"{API_BASE_URL}/audit-logs"
    )

    if audit_response.status_code == 200:

        audit_logs = (
            audit_response.json()
        )

        if len(audit_logs) == 0:

            st.info(
                "No audit logs available"
            )

        else:

            audit_df = pd.DataFrame(
                audit_logs
            )

            st.dataframe(
                audit_df,
                width="stretch"
            )

    else:

        st.error(
            audit_response.text
        )


# =====================================
# AI Copilot
# =====================================

elif page == "AI Hiring Copilot":

    st.header(
        "HireGuard AI Copilot"
    )

    query = st.text_input(
        "Ask HireGuard AI"
    )

    if query:

        with st.spinner(
            "Running orchestration workflow..."
        ):

            response = requests.post(

                f"{API_BASE_URL}/copilot",

                json={
                    "query": query
                }
            )

        if (
            response.status_code
            == 200
        ):

            result = (
                response.json()
            )

            st.success(
                "Workflow completed"
            )

            if "response" in result:
                st.markdown(result["response"])
            with st.expander(
                "Technical Response"
            ):
                st.json(
                    result
                )

        else:

            st.error(
                response.text
            )
