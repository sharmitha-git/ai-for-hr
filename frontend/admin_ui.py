import streamlit as st
import requests


API_BASE_URL = (
    "http://backend:8000"
)


st.set_page_config(
    page_title="HireGuard AI Admin Panel",
    layout="wide"
)


st.title("HireGuard AI")
st.subheader(
    "Admin ATS Management Panel"
)


menu = st.sidebar.radio(

    "Admin Actions",

    [

        "Create Job",

        "Upload Candidate"
    ]
)


# =========================================
# CREATE JOB
# =========================================

if menu == "Create Job":

    st.header(
        "Create Job Description"
    )

    title = st.text_input(
        "Job Title"
    )

    description = st.text_area(
        "Job Description"
    )

    required_skills = st.text_area(
        "Required Skills"
    )

    if st.button(
        "Create Job"
    ):

        response = requests.post(

            f"{API_BASE_URL}/create-job",

            data={

                "title": title,

                "description": description,

                "required_skills": required_skills
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


# =========================================
# UPLOAD CANDIDATE
# =========================================

elif menu == "Upload Candidate":

    st.header(
        "Upload Candidate Resume"
    )

    # -----------------------------
    # Fetch jobs dynamically
    # -----------------------------

    jobs_response = requests.get(
        f"{API_BASE_URL}/jobs"
    )

    jobs = jobs_response.json()

    if len(jobs) == 0:

        st.warning(
            "Create a job first before "
            "uploading candidates."
        )

        st.stop()

    job_options = {

        f"{job['id']} - {job['title']}":
        job["id"]

        for job in jobs
    }

    selected_job = st.selectbox(

        "Select Job",

        list(job_options.keys()), key='admin_job_select'
    )

    # -----------------------------
    # Candidate form
    # -----------------------------

    full_name = st.text_input(
        "Candidate Name"
    )

    email = st.text_input(
        "Email"
    )

    phone = st.text_input(
        "Phone"
    )

    skills = st.text_area(
        "Skills"
    )

    resume_file = st.file_uploader(
        "Upload Resume PDF",
        type=["pdf"]
    )

    # -----------------------------
    # Upload button
    # -----------------------------

    if st.button(
        "Upload Candidate"
    ):

        if resume_file is None:

            st.error(
                "Please upload a resume."
            )

            st.stop()

        files = {

            "file": (

                resume_file.name,

                resume_file.getvalue(),

                resume_file.type
            )
        }

        data = {

            "full_name": full_name,

            "email": email,

            "phone": phone,

            "skills": skills,

            "job_id": job_options[
                selected_job
            ]
        }

        response = requests.post(

            f"{API_BASE_URL}/upload-candidate",

            files=files,

            data=data
        )

        if response.status_code == 200:

            result = response.json()

            st.success(
                "Candidate uploaded successfully"
            )

            st.subheader(
                "Upload Result"
            )

            st.json(result)

            st.subheader(
                "Masked Resume Preview"
            )

            st.code(
                result["masked_preview"]
            )

        else:

            st.error(
                response.text
            )