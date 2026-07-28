# Developed by dnoobnerd [https://dnoobnerd.netlify.app]    Made with Streamlit


###### Packages Used ######
import streamlit as st # core package used in this project
import pandas as pd
import base64, random
import time,datetime
import os
import socket
import platform
import geocoder
import sqlite3
import secrets
import io,random
import plotly.express as px # to create visualisations at the admin session
import plotly.graph_objects as go
from geopy.geocoders import Nominatim
# libraries used to parse the pdf files
import nltk
nltk.download('stopwords')
from pyresparser import ResumeParser
try:
    from pdfminer.layout import LAParams, LTTextBox
    from pdfminer.pdfpage import PDFPage
    from pdfminer.pdfinterp import PDFResourceManager, PDFPageInterpreter
    from pdfminer.converter import TextConverter
except ImportError:
    from pdfminer3.layout import LAParams, LTTextBox
    from pdfminer3.pdfpage import PDFPage
    from pdfminer3.pdfinterp import PDFResourceManager
    from pdfminer3.pdfinterp import PDFPageInterpreter
    from pdfminer3.converter import TextConverter
from streamlit_tags import st_tags
from PIL import Image
# pre stored data for prediction purposes
from Courses import ds_course,web_course,android_course,ios_course,uiux_course,resume_videos,interview_videos
import nltk
nltk.download('stopwords')
from dotenv import load_dotenv
load_dotenv()
import google.generativeai as genai
import json
import os

GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")
if not GEMINI_API_KEY:
    try:
        GEMINI_API_KEY = st.secrets["GEMINI_API_KEY"]
    except Exception:
        pass
if GEMINI_API_KEY:
    genai.configure(api_key=GEMINI_API_KEY)


###### Preprocessing functions ######


# Generates a link allowing the data in a given panda dataframe to be downloaded in csv format 
def get_csv_download_link(df,filename,text):
    csv = df.to_csv(index=False)
    ## bytes conversions
    b64 = base64.b64encode(csv.encode()).decode()      
    href = f'<a href="data:file/csv;base64,{b64}" download="{filename}">{text}</a>'
    return href


# Reads Pdf file and check_extractable
def pdf_reader(file):
    resource_manager = PDFResourceManager()
    fake_file_handle = io.StringIO()
    converter = TextConverter(resource_manager, fake_file_handle, laparams=LAParams())
    page_interpreter = PDFPageInterpreter(resource_manager, converter)
    with open(file, 'rb') as fh:
        for page in PDFPage.get_pages(fh,
                                      caching=True,
                                      check_extractable=True):
            page_interpreter.process_page(page)
            print(page)
        text = fake_file_handle.getvalue()

    ## close open handles
    converter.close()
    fake_file_handle.close()
    return text


# show uploaded file path to view pdf_display
def show_pdf(file_path):
    try:
        from streamlit_pdf_viewer import pdf_viewer
        pdf_viewer(file_path, width=700, height=1000)
    except ImportError:
        st.warning("PDF viewer module not found. Please install streamlit-pdf-viewer.")


# course recommendations which has data already loaded from Courses.py
def course_recommender(course_list):
    st.subheader("**Courses & Certificates Recommendations 👨‍🎓**")
    c = 0
    rec_course = []
    ## slider to choose from range 1-10
    no_of_reco = st.slider('Choose Number of Course Recommendations:', 1, 10, 5)
    random.shuffle(course_list)
    for c_name, c_link in course_list:
        c += 1
        st.markdown(f"({c}) [{c_name}]({c_link})")
        rec_course.append(c_name)
        if c == no_of_reco:
            break
    return rec_course


def get_gemini_analysis(name, email, reco_field, cand_level, skills, degree, no_of_pages, resume_text):
    model = genai.GenerativeModel('gemini-pro')
    prompt = f"""
You are an expert resume reviewer and senior technical career coach with 15+ years 
of experience in recruiting across Data Science, Web Development, Android, iOS, 
and UI/UX roles. You give honest, specific, actionable feedback — never generic 
praise or filler compliments.

Analyze the resume data below and produce one complete, structured analysis.

CANDIDATE DATA (already extracted by the system):
- Name: {name}
- Email: {email}
- Predicted field: {reco_field}
- Experience level: {cand_level}
- Skills detected: {skills}
- Degree: {degree}
- Number of resume pages: {no_of_pages}

FULL RAW RESUME TEXT:
'''
{resume_text}
'''

Using ONLY the information above — do not invent companies, dates, job titles, 
metrics, or achievements that are not present in the text — return a single 
JSON object with exactly this structure and nothing else (no markdown fences, 
no preamble, no explanation before or after the JSON):

{{
  "professional_summary": "A 2-3 sentence third-person summary of who this candidate is professionally, written as if it would appear at the top of their resume. Under 60 words.",
  "candidate_level_assessment": "1-2 sentences confirming or refining the experience level (Fresher/Intermediate/Experienced) based on actual evidence in the text, not just keyword presence.",
  "key_strengths": ["3-5 short, specific bullet points on what stands out in this resume"],
  "gaps_or_weaknesses": ["2-4 honest, specific gaps: vague sections, missing quantification, unclear career narrative, formatting issues, thin project descriptions, etc."],
  "skills_to_add": ["5-8 skills relevant to the predicted field that are commonly expected but missing from this resume"],
  "ats_keywords_missing": ["5-8 exact keywords/phrases recruiters or ATS systems would search for in this field that do not appear in the resume text"],
  "resume_score_breakdown": {{
    "estimated_score_out_of_100": 0,
    "reasoning": "1-2 sentences on what pulled the score up or down"
  }},
  "one_line_pitch": "A single elevator-pitch sentence a recruiter could use to describe this candidate to a hiring manager",
  "suggested_next_role": "One specific, realistic job title this resume is best positioned for right now",
  "top_3_action_items": ["The 3 highest-impact edits this candidate should make to their resume, ordered by priority"]
}}

Rules:
- Every claim must be traceable to something actually present in the resume text.
- If the resume text is too short, garbled, or clearly incomplete (e.g. parsing failure) to analyze confidently, state this explicitly inside "gaps_or_weaknesses" and lower the estimated_score_out_of_100 accordingly rather than guessing.
- Keep all list items concise — one line each, no sub-bullets.
- Return valid, parseable JSON only.
"""
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:-3].strip()
        elif text.startswith("```"):
            text = text[3:-3].strip()
        return json.loads(text)
    except Exception as e:
        return {"error": str(e)}

def get_gemini_field_recommendation(skills, cand_level, degree, resume_text):
    model = genai.GenerativeModel('gemini-pro')
    prompt = f"""
You are an expert technical recruiter who specializes in matching candidates 
to the right career track based on their actual skills and experience — not 
just keyword presence.

CANDIDATE DATA:
- Skills detected: {skills}
- Experience level: {cand_level}
- Degree: {degree}

FULL RESUME TEXT:
'''
{resume_text}
'''

Evaluate this candidate against these five career tracks: Data Science, 
Web Development, Android Development, iOS Development, UI/UX Design.

Return ONLY valid JSON in this exact structure (no markdown fences, no text 
outside the JSON):

{{
  "rankings": [
    {{
      "field": "Field name",
      "confidence_percent": 0,
      "reasoning": "1-2 sentences on why this field fits, citing specific skills/experience from the resume",
      "matching_skills": ["skills from the resume that support this field"]
    }}
  ],
  "primary_recommendation": "The single best-fit field",
  "note": "1 sentence on whether this candidate looks like a strong single-track specialist or a multi-track generalist"
}}

Rules:
- Return exactly the top 3 fields, ordered by confidence_percent descending.
- confidence_percent values across all 3 fields do not need to sum to 100 — 
  they're independent fit scores, not a probability distribution.
- Base every score strictly on evidence in the resume text and skill list — 
  do not guess based on degree alone.
- If the resume shows almost no relevant skills for any of the 5 fields, say 
  so honestly in "note" and give low confidence scores across the board rather 
  than forcing a match.
"""
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:-3].strip()
        elif text.startswith("```"):
            text = text[3:-3].strip()
        return json.loads(text)
    except Exception as e:
        return {"error": str(e)}

def get_gemini_cover_letter(name, reco_field, cand_level, skills, degree, resume_text, job_title, job_description):
    model = genai.GenerativeModel('gemini-pro')
    prompt = f"""
You are an expert career coach and professional cover letter writer. You write 
tailored, specific, natural-sounding cover letters — never generic templates, 
never robotic phrasing, no clichés like "I am writing to express my interest."

CANDIDATE DATA:
- Name: {name}
- Predicted field: {reco_field}
- Experience level: {cand_level}
- Skills: {skills}
- Degree: {degree}

FULL RESUME TEXT:
'''
{resume_text}
'''

TARGET JOB:
- Job Title: {job_title}
- Job Description: 
'''
{job_description}
'''

Write a personalized cover letter for this candidate applying to this specific 
role. Return ONLY valid JSON in this exact structure (no markdown fences, no 
text outside the JSON):

{{
  "cover_letter": "The full cover letter text, 3-4 paragraphs, ready to send. Use \\n\\n between paragraphs.",
  "tone": "One word describing the tone used (e.g. Professional, Enthusiastic, Confident)",
  "key_points_highlighted": ["2-4 specific things from the resume this letter emphasizes and why they match the JD"],
  "customization_note": "1 sentence flagging anything the candidate should manually verify or add (e.g. a specific company detail not in the resume)"
}}

Rules:
- Only reference skills, experience, and achievements that actually appear in 
  the resume text — never invent anything.
- Directly connect at least 2 requirements from the job description to specific 
  evidence in the resume.
- Keep the letter under 350 words.
- Do not include a greeting/salutation placeholder like "[Hiring Manager Name]" 
  — just write "Dear Hiring Team," instead.
- If the job description is missing or too short to tailor to, say so in 
  "customization_note" and write a strong general cover letter for the 
  predicted field instead.
"""
    try:
        response = model.generate_content(prompt)
        text = response.text.strip()
        if text.startswith("```json"):
            text = text[7:-3].strip()
        elif text.startswith("```"):
            text = text[3:-3].strip()
        return json.loads(text)
    except Exception as e:
        return {"error": str(e)}


###### Database Stuffs ######


# sql connector
try:
    import pymysql
    connection = pymysql.connect(host='localhost',user='root',password='root@MySQL4admin',db='cv')
    cursor = connection.cursor()
    db_backend = 'mysql'
except Exception:
    db_path = os.path.join(os.path.dirname(__file__), 'cv.db')
    connection = sqlite3.connect(db_path)
    cursor = connection.cursor()
    db_backend = 'sqlite'


# inserting miscellaneous data, fetched results, prediction and recommendation into user_data table
def insert_data(sec_token,ip_add,host_name,dev_user,os_name_ver,latlong,city,state,country,act_name,act_mail,act_mob,name,email,res_score,timestamp,no_of_pages,reco_field,cand_level,skills,recommended_skills,courses,pdf_name):
    DB_table_name = 'user_data'
    if db_backend == 'sqlite':
        insert_sql = "insert into " + DB_table_name + """
        values (NULL,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?,?)"""
    else:
        insert_sql = "insert into " + DB_table_name + """
        values (0,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s,%s)"""
    rec_values = (str(sec_token),str(ip_add),host_name,dev_user,os_name_ver,str(latlong),city,state,country,act_name,act_mail,act_mob,name,email,str(res_score),timestamp,str(no_of_pages),reco_field,cand_level,skills,recommended_skills,courses,pdf_name)
    cursor.execute(insert_sql, rec_values)
    connection.commit()


# inserting feedback data into user_feedback table
def insertf_data(feed_name,feed_email,feed_score,comments,Timestamp):
    DBf_table_name = 'user_feedback'
    if db_backend == 'sqlite':
        insertfeed_sql = "insert into " + DBf_table_name + """
        values (NULL,?,?,?,?,?)"""
    else:
        insertfeed_sql = "insert into " + DBf_table_name + """
        values (0,%s,%s,%s,%s,%s)"""
    rec_values = (feed_name, feed_email, feed_score, comments, Timestamp)
    cursor.execute(insertfeed_sql, rec_values)
    connection.commit()


###### Setting Page Configuration (favicon, Logo, Title) ######


BASE_DIR = os.path.dirname(os.path.abspath(__file__))
LOGO_DIR = os.path.join(BASE_DIR, 'Logo')

st.set_page_config(
   page_title="AI Resume Analyzer",
   page_icon=os.path.join(LOGO_DIR, 'recommend.png'),
)


###### Main function run() ######


def run():
    
    # (Logo, Heading, Sidebar etc)
    img_path = os.path.join(LOGO_DIR, 'RESUM.png')
    img = Image.open(img_path)
    st.image(img)
    st.sidebar.markdown("# Choose Something...")
    activities = ["User", "Feedback", "About", "Admin"]
    choice = st.sidebar.selectbox("Choose among the given options:", activities)
    
    link = '<b>Built with 🤍 by <a href="#" style="text-decoration: none; color: #021659;">Nithish</a></b>' 
    st.sidebar.markdown(link, unsafe_allow_html=True)
    st.sidebar.markdown('''
        <!-- site visitors -->

        <div id="sfct2xghr8ak6lfqt3kgru233378jya38dy" hidden></div>

        <noscript>
            <a href="https://www.freecounterstat.com" title="hit counter">
                <img src="https://counter9.stat.ovh/private/freecounterstat.php?c=t2xghr8ak6lfqt3kgru233378jya38dy" border="0" title="hit counter" alt="hit counter"> -->
            </a>
        </noscript>
    
        <p>Visitors <img src="https://counter9.stat.ovh/private/freecounterstat.php?c=t2xghr8ak6lfqt3kgru233378jya38dy" title="Free Counter" Alt="web counter" width="60px"  border="0" /></p>
    
    ''', unsafe_allow_html=True)

    ###### Creating Database and Table ######


    # Create the DB / tables
    if db_backend == 'mysql':
        db_sql = """CREATE DATABASE IF NOT EXISTS CV;"""
        cursor.execute(db_sql)

        DB_table_name = 'user_data'
        table_sql = "CREATE TABLE IF NOT EXISTS " + DB_table_name + """
                        (ID INT NOT NULL AUTO_INCREMENT,
                        sec_token varchar(20) NOT NULL,
                        ip_add varchar(50) NULL,
                        host_name varchar(50) NULL,
                        dev_user varchar(50) NULL,
                        os_name_ver varchar(50) NULL,
                        latlong varchar(50) NULL,
                        city varchar(50) NULL,
                        state varchar(50) NULL,
                        country varchar(50) NULL,
                        act_name varchar(50) NOT NULL,
                        act_mail varchar(50) NOT NULL,
                        act_mob varchar(20) NOT NULL,
                        Name varchar(500) NOT NULL,
                        Email_ID VARCHAR(500) NOT NULL,
                        resume_score VARCHAR(8) NOT NULL,
                        Timestamp VARCHAR(50) NOT NULL,
                        Page_no VARCHAR(5) NOT NULL,
                        Predicted_Field BLOB NOT NULL,
                        User_level BLOB NOT NULL,
                        Actual_skills BLOB NOT NULL,
                        Recommended_skills BLOB NOT NULL,
                        Recommended_courses BLOB NOT NULL,
                        pdf_name varchar(50) NOT NULL,
                        PRIMARY KEY (ID)
                        );
                    """
        cursor.execute(table_sql)

        DBf_table_name = 'user_feedback'
        tablef_sql = "CREATE TABLE IF NOT EXISTS " + DBf_table_name + """
                        (ID INT NOT NULL AUTO_INCREMENT,
                            feed_name varchar(50) NOT NULL,
                            feed_email VARCHAR(50) NOT NULL,
                            feed_score VARCHAR(5) NOT NULL,
                            comments VARCHAR(100) NULL,
                            Timestamp VARCHAR(50) NOT NULL,
                            PRIMARY KEY (ID)
                        );
                    """
        cursor.execute(tablef_sql)
    else:
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_data (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                sec_token TEXT NOT NULL,
                ip_add TEXT,
                host_name TEXT,
                dev_user TEXT,
                os_name_ver TEXT,
                latlong TEXT,
                city TEXT,
                state TEXT,
                country TEXT,
                act_name TEXT NOT NULL,
                act_mail TEXT NOT NULL,
                act_mob TEXT NOT NULL,
                Name TEXT NOT NULL,
                Email_ID TEXT NOT NULL,
                resume_score TEXT NOT NULL,
                Timestamp TEXT NOT NULL,
                Page_no TEXT NOT NULL,
                Predicted_Field TEXT NOT NULL,
                User_level TEXT NOT NULL,
                Actual_skills TEXT NOT NULL,
                Recommended_skills TEXT NOT NULL,
                Recommended_courses TEXT NOT NULL,
                pdf_name TEXT NOT NULL
            )
        """)
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS user_feedback (
                ID INTEGER PRIMARY KEY AUTOINCREMENT,
                feed_name TEXT NOT NULL,
                feed_email TEXT NOT NULL,
                feed_score TEXT NOT NULL,
                comments TEXT,
                Timestamp TEXT NOT NULL
            )
        """)
        connection.commit()


    ###### CODE FOR CLIENT SIDE (USER) ######

    if choice == 'User':
        
        # Collecting Miscellaneous Information
        act_name = st.text_input('Name*')
        act_mail = st.text_input('Mail*')
        act_mob  = st.text_input('Mobile Number*')
        sec_token = secrets.token_urlsafe(12)
        host_name = socket.gethostname()
        ip_add = socket.gethostbyname(host_name)
        dev_user = os.environ.get('USER', os.environ.get('USERNAME', 'admin'))
        os_name_ver = platform.system() + " " + platform.release()
        g = geocoder.ip('me')
        latlong = g.latlng
        try:
            geolocator = Nominatim(user_agent="ai_resume_analyzer_app")
            location = geolocator.reverse(latlong, language='en', timeout=5)
            address = location.raw['address']
            cityy = address.get('city', '')
            statee = address.get('state', '')
            countryy = address.get('country', '')  
        except Exception:
            cityy, statee, countryy = "Unknown", "Unknown", "Unknown"
        city = cityy
        state = statee
        country = countryy


        # Upload Resume
        st.markdown('''<h5 style='text-align: left; color: #021659;'> Upload Your Resume, And Get Smart Recommendations</h5>''',unsafe_allow_html=True)
        
        ## file upload in pdf format
        pdf_file = st.file_uploader("Choose your Resume", type=["pdf"])
        if pdf_file is not None:
            with st.spinner('Hang On While We Cook Magic For You...'):
                time.sleep(4)
        
            ### saving the uploaded resume to folder
            uploads_dir = os.path.join(BASE_DIR, 'Uploaded_Resumes')
            os.makedirs(uploads_dir, exist_ok=True)
            safe_name = os.path.basename(pdf_file.name)
            save_image_path = os.path.join(uploads_dir, safe_name)
            pdf_name = safe_name
            with open(save_image_path, "wb") as f:
                f.write(pdf_file.getbuffer())
            show_pdf(save_image_path)

            ### parsing and extracting whole resume 
            resume_data = ResumeParser(save_image_path).get_extracted_data()
            if resume_data:
                
                ## Get the whole resume data into resume_text
                resume_text = pdf_reader(save_image_path)

                ## Showing Analyzed data from (resume_data)
                st.header("**Resume Analysis 🤘**")
                st.success("Hello "+ resume_data['name'])
                st.subheader("**Your Basic info 👀**")
                try:
                    st.text('Name: '+resume_data['name'])
                    st.text('Email: ' + resume_data['email'])
                    st.text('Contact: ' + resume_data['mobile_number'])
                    st.text('Degree: '+str(resume_data['degree']))                    
                    st.text('Resume pages: '+str(resume_data['no_of_pages']))

                except:
                    pass
                ## Predicting Candidate Experience Level 

                ### Trying with different possibilities
                cand_level = ''
                if resume_data['no_of_pages'] < 1:                
                    cand_level = "NA"
                    st.markdown( '''<h4 style='text-align: left; color: #d73b5c;'>You are at Fresher level!</h4>''',unsafe_allow_html=True)
                
                #### if internship then intermediate level
                elif 'INTERNSHIP' in resume_text:
                    cand_level = "Intermediate"
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
                elif 'INTERNSHIPS' in resume_text:
                    cand_level = "Intermediate"
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
                elif 'Internship' in resume_text:
                    cand_level = "Intermediate"
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
                elif 'Internships' in resume_text:
                    cand_level = "Intermediate"
                    st.markdown('''<h4 style='text-align: left; color: #1ed760;'>You are at intermediate level!</h4>''',unsafe_allow_html=True)
                
                #### if Work Experience/Experience then Experience level
                elif 'EXPERIENCE' in resume_text:
                    cand_level = "Experienced"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',unsafe_allow_html=True)
                elif 'WORK EXPERIENCE' in resume_text:
                    cand_level = "Experienced"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',unsafe_allow_html=True)
                elif 'Experience' in resume_text:
                    cand_level = "Experienced"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',unsafe_allow_html=True)
                elif 'Work Experience' in resume_text:
                    cand_level = "Experienced"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at experience level!''',unsafe_allow_html=True)
                else:
                    cand_level = "Fresher"
                    st.markdown('''<h4 style='text-align: left; color: #fba171;'>You are at Fresher level!!''',unsafe_allow_html=True)


                ## Skills Analyzing and Recommendation
                st.subheader("**Skills Recommendation 💡**")
                
                ### Current Analyzed Skills
                keywords = st_tags(label='### Your Current Skills',
                text='See our skills recommendation below',value=resume_data['skills'],key = '1  ')

                ### Keywords for Recommendations
                ds_keyword = ['tensorflow','keras','pytorch','machine learning','deep Learning','flask','streamlit']
                web_keyword = ['react', 'django', 'node jS', 'react js', 'php', 'laravel', 'magento', 'wordpress','javascript', 'angular js', 'C#', 'Asp.net', 'flask']
                android_keyword = ['android','android development','flutter','kotlin','xml','kivy']
                ios_keyword = ['ios','ios development','swift','cocoa','cocoa touch','xcode']
                uiux_keyword = ['ux','adobe xd','figma','zeplin','balsamiq','ui','prototyping','wireframes','storyframes','adobe photoshop','photoshop','editing','adobe illustrator','illustrator','adobe after effects','after effects','adobe premier pro','premier pro','adobe indesign','indesign','wireframe','solid','grasp','user research','user experience']
                n_any = ['english','communication','writing', 'microsoft office', 'leadership','customer management', 'social media']
                ### Skill Recommendations Starts                
                recommended_skills = []
                reco_field = ''
                rec_course = ''

                ### condition starts to check skills from keywords and predict field
                if GEMINI_API_KEY:
                    with st.spinner("Analyzing career tracks with Gemini AI..."):
                        field_ai = get_gemini_field_recommendation(
                            skills=str(resume_data.get('skills', [])),
                            cand_level=cand_level,
                            degree=str(resume_data.get('degree', 'NA')),
                            resume_text=resume_text
                        )
                    if "error" not in field_ai:
                        reco_field = field_ai.get('primary_recommendation', 'NA')
                        st.success(f"** Our AI analysis says your profile best fits: {reco_field} **")
                        st.info(f"**Note:** {field_ai.get('note', '')}")
                        
                        st.subheader("**Career Track Rankings 🏆**")
                        for rank in field_ai.get('rankings', []):
                            with st.expander(f"{rank.get('field', 'Unknown')} - {rank.get('confidence_percent', 0)}% Match"):
                                st.write(f"**Reasoning:** {rank.get('reasoning', '')}")
                                st.write(f"**Matching Skills:** {', '.join(rank.get('matching_skills', []))}")
                    else:
                        st.error("Error communicating with Gemini AI for field recommendation.")
                        reco_field = 'NA'
                else:
                    st.warning("AI field recommendation is unavailable without an API Key.")
                    reco_field = 'NA'

                # Map to legacy database fields
                if reco_field == 'Data Science':
                    recommended_skills = ['Data Visualization','Predictive Analysis','Statistical Modeling','Data Mining','Clustering & Classification','Data Analytics','Quantitative Analysis','Web Scraping','ML Algorithms','Keras','Pytorch','Probability','Scikit-learn','Tensorflow',"Flask",'Streamlit']
                    rec_course = course_recommender(ds_course)
                elif reco_field == 'Web Development':
                    recommended_skills = ['React','Django','Node JS','React JS','php','laravel','Magento','wordpress','Javascript','Angular JS','c#','Flask','SDK']
                    rec_course = course_recommender(web_course)
                elif reco_field == 'Android Development':
                    recommended_skills = ['Android','Android development','Flutter','Kotlin','XML','Java','Kivy','GIT','SDK','SQLite']
                    rec_course = course_recommender(android_course)
                elif reco_field == 'IOS Development':
                    recommended_skills = ['IOS','IOS Development','Swift','Cocoa','Cocoa Touch','Xcode','Objective-C','SQLite','Plist','StoreKit',"UI-Kit",'AV Foundation','Auto-Layout']
                    rec_course = course_recommender(ios_course)
                elif reco_field == 'UI-UX Development' or reco_field == 'UI/UX Design':
                    recommended_skills = ['UI','User Experience','Adobe XD','Figma','Zeplin','Balsamiq','Prototyping','Wireframes','Storyframes','Adobe Photoshop','Editing','Illustrator','After Effects','Premier Pro','Indesign','Wireframe','Solid','Grasp','User Research']
                    rec_course = course_recommender(uiux_course)
                else:
                    recommended_skills = ['No Recommendations']
                    rec_course = "Sorry! Not Available for this Field"
                
                recommended_keywords = st_tags(label='### Recommended skills for you.',
                text='Recommended skills generated from System',value=recommended_skills,key = 'legacy_skills')



                ## Resume Scorer & Resume Writing Tips using Gemini API
                st.subheader("**AI Resume Analysis & Tips 🤖**")
                
                resume_score = 0
                if not GEMINI_API_KEY:
                    st.warning("AI summary is temporarily unavailable.")
                else:
                    with st.spinner("Analyzing your resume with Gemini AI..."):
                        degree = str(resume_data.get('degree', 'NA'))
                        pages = str(resume_data.get('no_of_pages', 'NA'))
                        ai_result = get_gemini_analysis(
                            name=resume_data.get('name', 'NA'),
                            email=resume_data.get('email', 'NA'),
                            reco_field=reco_field,
                            cand_level=cand_level,
                            skills=str(resume_data.get('skills', 'NA')),
                            degree=degree,
                            no_of_pages=pages,
                            resume_text=resume_text
                        )
                    
                    if "error" in ai_result:
                        st.error(f"Error communicating with Gemini AI: {ai_result['error']}")
                    else:
                        st.markdown(f"**Professional Summary:** {ai_result.get('professional_summary', 'N/A')}")
                        st.markdown(f"**Candidate Level Assessment:** {ai_result.get('candidate_level_assessment', 'N/A')}")
                        st.markdown(f"**Elevator Pitch:** {ai_result.get('one_line_pitch', 'N/A')}")
                        st.markdown(f"**Suggested Next Role:** {ai_result.get('suggested_next_role', 'N/A')}")
                        
                        st.subheader("**Key Strengths 💪**")
                        for strength in ai_result.get('key_strengths', []):
                            st.markdown(f"- {strength}")
                            
                        st.subheader("**Gaps or Weaknesses ⚠️**")
                        for gap in ai_result.get('gaps_or_weaknesses', []):
                            st.markdown(f"- {gap}")
                            
                        st.subheader("**Skills to Add 📈**")
                        if ai_result.get('skills_to_add'):
                            st_tags(label='Missing Required Skills', text='', value=ai_result.get('skills_to_add', []), key='skills_to_add_tags')
                            
                        st.subheader("**Missing ATS Keywords 🔍**")
                        if ai_result.get('ats_keywords_missing'):
                            st_tags(label='ATS Keywords to Add', text='', value=ai_result.get('ats_keywords_missing', []), key='ats_keywords_missing_tags')
                            
                        st.subheader("**Top 3 Action Items 🎯**")
                        for item in ai_result.get('top_3_action_items', []):
                            st.markdown(f"✅ {item}")
                            
                        resume_score = ai_result.get('resume_score_breakdown', {}).get('estimated_score_out_of_100', 0)
                        reasoning = ai_result.get('resume_score_breakdown', {}).get('reasoning', '')
                        
                        st.subheader("**AI Resume Score 📝**")
                        st.markdown(
                            """
                            <style>
                                .stProgress > div > div > div > div {
                                    background-color: #d73b5c;
                                }
                            </style>""",
                            unsafe_allow_html=True,
                        )
                        my_bar = st.progress(0)
                        score = 0
                        for percent_complete in range(resume_score):
                            score += 1
                            time.sleep(0.02)
                            my_bar.progress(percent_complete + 1)
                            
                        st.success(f"** Your AI Resume Score: {score} / 100 **")
                        st.info(f"**Reasoning:** {reasoning}")

                ## AI Cover Letter Generator
                st.subheader("**AI Cover Letter Generator ✉️**")
                if not GEMINI_API_KEY:
                    st.warning("AI Cover Letter Generator is temporarily unavailable without an API Key.")
                else:
                    st.markdown("Enter the details of the job you are applying for to generate a personalized cover letter.")
                    with st.form("cover_letter_form"):
                        job_title = st.text_input("Job Title", placeholder="e.g. Senior Frontend Developer")
                        job_description = st.text_area("Job Description", placeholder="Paste the full job description here...", height=200)
                        submitted = st.form_submit_button("Generate Cover Letter")
                        
                    if submitted:
                        if not job_title or not job_description:
                            st.error("Please provide both Job Title and Job Description.")
                        else:
                            with st.spinner("Drafting your personalized cover letter..."):
                                cl_result = get_gemini_cover_letter(
                                    name=resume_data.get('name', 'Candidate'),
                                    reco_field=reco_field,
                                    cand_level=cand_level,
                                    skills=str(resume_data.get('skills', 'NA')),
                                    degree=str(resume_data.get('degree', 'NA')),
                                    resume_text=resume_text,
                                    job_title=job_title,
                                    job_description=job_description
                                )
                                
                            if "error" in cl_result:
                                st.error(f"Error communicating with Gemini AI: {cl_result['error']}")
                            else:
                                st.success("Cover Letter Generated!")
                                st.markdown(f"**Tone:** {cl_result.get('tone', 'N/A')}")
                                st.info(f"**Note:** {cl_result.get('customization_note', '')}")
                                
                                st.markdown("**Key Points Highlighted:**")
                                for point in cl_result.get('key_points_highlighted', []):
                                    st.markdown(f"- {point}")
                                    
                                st.markdown("**Your Cover Letter:**")
                                st.text_area("Review and Copy", value=cl_result.get('cover_letter', ''), height=400)

                ### Getting Current Date and Time
                ts = time.time()
                cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
                cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
                timestamp = str(cur_date+'_'+cur_time)


                ## Calling insert_data to add all the data into user_data                
                insert_data(str(sec_token), str(ip_add), (host_name), (dev_user), (os_name_ver), (latlong), (city), (state), (country), (act_name), (act_mail), (act_mob), resume_data['name'], resume_data['email'], str(resume_score), timestamp, str(resume_data['no_of_pages']), reco_field, cand_level, str(resume_data['skills']), str(recommended_skills), str(rec_course), pdf_name)

                ## Recommending Resume Writing Video
                st.header("**Bonus Video for Resume Writing Tips💡**")
                resume_vid = random.choice(resume_videos)
                st.video(resume_vid)

                ## Recommending Interview Preparation Video
                st.header("**Bonus Video for Interview Tips💡**")
                interview_vid = random.choice(interview_videos)
                st.video(interview_vid)

                ## On Successful Result 
                st.balloons()

            else:
                st.error('Something went wrong..')                


    ###### CODE FOR FEEDBACK SIDE ######
    elif choice == 'Feedback':   
        
        # timestamp 
        ts = time.time()
        cur_date = datetime.datetime.fromtimestamp(ts).strftime('%Y-%m-%d')
        cur_time = datetime.datetime.fromtimestamp(ts).strftime('%H:%M:%S')
        timestamp = str(cur_date+'_'+cur_time)

        # Feedback Form
        with st.form("my_form"):
            st.write("Feedback form")            
            feed_name = st.text_input('Name')
            feed_email = st.text_input('Email')
            feed_score = st.slider('Rate Us From 1 - 5', 1, 5)
            comments = st.text_input('Comments')
            Timestamp = timestamp        
            submitted = st.form_submit_button("Submit")
            if submitted:
                ## Calling insertf_data to add dat into user feedback
                insertf_data(feed_name,feed_email,feed_score,comments,Timestamp)    
                ## Success Message 
                st.success("Thanks! Your Feedback was recorded.") 
                ## On Successful Submit
                st.balloons()    


        # query to fetch data from user feedback table
        query = 'select * from user_feedback'        
        plotfeed_data = pd.read_sql(query, connection)                        


        # fetching feed_score from the query and getting the unique values and total value count 
        labels = plotfeed_data.feed_score.unique()
        values = plotfeed_data.feed_score.value_counts()


        # plotting pie chart for user ratings
        st.subheader("**Past User Rating's**")
        fig = px.pie(values=values, names=labels, title="Chart of User Rating Score From 1 - 5", color_discrete_sequence=px.colors.sequential.Aggrnyl)
        st.plotly_chart(fig)


        #  Fetching Comment History
        cursor.execute('select feed_name, comments from user_feedback')
        plfeed_cmt_data = cursor.fetchall()

        st.subheader("**User Comment's**")
        dff = pd.DataFrame(plfeed_cmt_data, columns=['User', 'Comment'])
        st.dataframe(dff, width=1000)

    
    ###### CODE FOR ABOUT PAGE ######
    elif choice == 'About':   

        st.subheader("**About The Tool - AI RESUME ANALYZER**")

        st.markdown('''

        <p align='justify'>
            A tool which parses information from a resume using natural language processing and finds the keywords, cluster them onto sectors based on their keywords. And lastly show recommendations, predictions, analytics to the applicant based on keyword matching.
        </p>

        <p align="justify">
            <b>How to use it: -</b> <br/><br/>
            <b>User -</b> <br/>
            In the Side Bar choose yourself as user and fill the required fields and upload your resume in pdf format.<br/>
            Just sit back and relax our tool will do the magic on it's own.<br/><br/>
            <b>Feedback -</b> <br/>
            A place where user can suggest some feedback about the tool.<br/><br/>
            <b>Admin -</b> <br/>
            For login use <b>admin</b> as username and <b>admin@resume-analyzer</b> as password.<br/>
            It will load all the required stuffs and perform analysis.
        </p><br/><br/>

        <p align="justify">
            Built with 🤍 by 
            <a href="#" style="text-decoration: none; color: grey;">Nithish</a> through 
            <a href="https://www.linkedin.com/in/mrbriit/" style="text-decoration: none; color: grey;">Dr Bright --(Data Scientist)</a>
        </p>

        ''',unsafe_allow_html=True)  


    ###### CODE FOR ADMIN SIDE (ADMIN) ######
    else:
        st.success('Welcome to Admin Side')

        #  Admin Login
        ad_user = st.text_input("Username")
        ad_password = st.text_input("Password", type='password')

        if st.button('Login'):
            
            ## Credentials 
            if ad_user == 'admin' and ad_password == 'admin@resume-analyzer':
                
                ### Fetch miscellaneous data from user_data(table) and convert it into dataframe
                if db_backend == 'mysql':
                    cursor.execute('''SELECT ID, ip_add, resume_score, convert(Predicted_Field using utf8), convert(User_level using utf8), city, state, country from user_data''')
                else:
                    cursor.execute('''SELECT ID, ip_add, resume_score, Predicted_Field, User_level, city, state, country from user_data''')
                datanalys = cursor.fetchall()
                plot_data = pd.DataFrame(datanalys, columns=['Idt', 'IP_add', 'resume_score', 'Predicted_Field', 'User_Level', 'City', 'State', 'Country'])
                
                ### Total Users Count with a Welcome Message
                values = plot_data.Idt.count()
                st.success("Welcome Nithish ! Total %d " % values + " User's Have Used Our Tool : )")                
                
                ### Fetch user data from user_data(table) and convert it into dataframe
                if db_backend == 'mysql':
                    cursor.execute('''SELECT ID, sec_token, ip_add, act_name, act_mail, act_mob, convert(Predicted_Field using utf8), Timestamp, Name, Email_ID, resume_score, Page_no, pdf_name, convert(User_level using utf8), convert(Actual_skills using utf8), convert(Recommended_skills using utf8), convert(Recommended_courses using utf8), city, state, country, latlong, os_name_ver, host_name, dev_user from user_data''')
                else:
                    cursor.execute('''SELECT ID, sec_token, ip_add, act_name, act_mail, act_mob, Predicted_Field, Timestamp, Name, Email_ID, resume_score, Page_no, pdf_name, User_level, Actual_skills, Recommended_skills, Recommended_courses, city, state, country, latlong, os_name_ver, host_name, dev_user from user_data''')
                data = cursor.fetchall()                

                st.header("**User's Data**")
                df = pd.DataFrame(data, columns=['ID', 'Token', 'IP Address', 'Name', 'Mail', 'Mobile Number', 'Predicted Field', 'Timestamp',
                                                 'Predicted Name', 'Predicted Mail', 'Resume Score', 'Total Page',  'File Name',   
                                                 'User Level', 'Actual Skills', 'Recommended Skills', 'Recommended Course',
                                                 'City', 'State', 'Country', 'Lat Long', 'Server OS', 'Server Name', 'Server User',])
                
                ### Viewing the dataframe
                st.dataframe(df)
                
                ### Downloading Report of user_data in csv file
                st.markdown(get_csv_download_link(df,'User_Data.csv','Download Report'), unsafe_allow_html=True)

                ### Fetch feedback data from user_feedback(table) and convert it into dataframe
                cursor.execute('''SELECT * from user_feedback''')
                data = cursor.fetchall()

                st.header("**User's Feedback Data**")
                df = pd.DataFrame(data, columns=['ID', 'Name', 'Email', 'Feedback Score', 'Comments', 'Timestamp'])
                st.dataframe(df)

                ### query to fetch data from user_feedback(table)
                query = 'select * from user_feedback'
                plotfeed_data = pd.read_sql(query, connection)                        

                ### Analyzing All the Data's in pie charts

                # fetching feed_score from the query and getting the unique values and total value count 
                labels = plotfeed_data.feed_score.unique()
                values = plotfeed_data.feed_score.value_counts()
                
                # Pie chart for user ratings
                st.subheader("**User Rating's**")
                fig = px.pie(values=values, names=labels, title="Chart of User Rating Score From 1 - 5 🤗", color_discrete_sequence=px.colors.sequential.Aggrnyl)
                st.plotly_chart(fig)

                # fetching Predicted_Field from the query and getting the unique values and total value count                 
                labels = plot_data.Predicted_Field.unique()
                values = plot_data.Predicted_Field.value_counts()

                # Pie chart for predicted field recommendations
                st.subheader("**Pie-Chart for Predicted Field Recommendation**")
                fig = px.pie(df, values=values, names=labels, title='Predicted Field according to the Skills 👽', color_discrete_sequence=px.colors.sequential.Aggrnyl_r)
                st.plotly_chart(fig)

                # fetching User_Level from the query and getting the unique values and total value count                 
                labels = plot_data.User_Level.unique()
                values = plot_data.User_Level.value_counts()

                # Pie chart for User's👨‍💻 Experienced Level
                st.subheader("**Pie-Chart for User's Experienced Level**")
                fig = px.pie(df, values=values, names=labels, title="Pie-Chart 📈 for User's 👨‍💻 Experienced Level", color_discrete_sequence=px.colors.sequential.RdBu)
                st.plotly_chart(fig)

                # fetching resume_score from the query and getting the unique values and total value count                 
                labels = plot_data.resume_score.unique()                
                values = plot_data.resume_score.value_counts()

                # Pie chart for Resume Score
                st.subheader("**Pie-Chart for Resume Score**")
                fig = px.pie(df, values=values, names=labels, title='From 1 to 100 💯', color_discrete_sequence=px.colors.sequential.Agsunset)
                st.plotly_chart(fig)

                # fetching IP_add from the query and getting the unique values and total value count 
                labels = plot_data.IP_add.unique()
                values = plot_data.IP_add.value_counts()

                # Pie chart for Users
                st.subheader("**Pie-Chart for Users App Used Count**")
                fig = px.pie(df, values=values, names=labels, title='Usage Based On IP Address 👥', color_discrete_sequence=px.colors.sequential.matter_r)
                st.plotly_chart(fig)

                # fetching City from the query and getting the unique values and total value count 
                labels = plot_data.City.unique()
                values = plot_data.City.value_counts()

                # Pie chart for City
                st.subheader("**Pie-Chart for City**")
                fig = px.pie(df, values=values, names=labels, title='Usage Based On City 🌆', color_discrete_sequence=px.colors.sequential.Jet)
                st.plotly_chart(fig)

                # fetching State from the query and getting the unique values and total value count 
                labels = plot_data.State.unique()
                values = plot_data.State.value_counts()

                # Pie chart for State
                st.subheader("**Pie-Chart for State**")
                fig = px.pie(df, values=values, names=labels, title='Usage Based on State 🚉', color_discrete_sequence=px.colors.sequential.PuBu_r)
                st.plotly_chart(fig)

                # fetching Country from the query and getting the unique values and total value count 
                labels = plot_data.Country.unique()
                values = plot_data.Country.value_counts()

                # Pie chart for Country
                st.subheader("**Pie-Chart for Country**")
                fig = px.pie(df, values=values, names=labels, title='Usage Based on Country 🌏', color_discrete_sequence=px.colors.sequential.Purpor_r)
                st.plotly_chart(fig)

            ## For Wrong Credentials
            else:
                st.error("Wrong ID & Password Provided")

# Calling the main (run()) function to make the whole process run
run()
