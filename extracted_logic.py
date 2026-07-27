## Resume Scorer & Resume Writing Tips
                st.subheader("**Resume Tips & Ideas ≡ƒÑé**")
                resume_score = 0
                
                ### Predicting Whether these key points are added to the resume
                if 'Objective' or 'Summary' in resume_text:
                    resume_score = resume_score+6
                    st.markdown('<div class=\"user-checklist-item success\"><span class=\"icon\">✅</span><span>Awesome! You have added Objective/Summary</span></div>', unsafe_allow_html=True)                
                else:
                    st.markdown('<div class=\"user-checklist-item error\"><span class=\"icon\">❌</span><span>Please add your career objective, it will give your career intension to the Recruiters.</span></div>', unsafe_allow_html=True)

                if 'Education' or 'School' or 'College'  in resume_text:
                    resume_score = resume_score + 12
                    st.markdown('<div class=\"user-checklist-item success\"><span class=\"icon\">✅</span><span>Awesome! You have added Education Details</span></div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class=\"user-checklist-item error\"><span class=\"icon\">❌</span><span>Please add Education. It will give Your Qualification level to the recruiter</span></div>', unsafe_allow_html=True)

                if 'EXPERIENCE' in resume_text:
                    resume_score = resume_score + 16
                    st.markdown('<div class=\"user-checklist-item success\"><span class=\"icon\">✅</span><span>Awesome! You have added Experience</span></div>', unsafe_allow_html=True)
                elif 'Experience' in resume_text:
                    resume_score = resume_score + 16
                    st.markdown('<div class=\"user-checklist-item success\"><span class=\"icon\">✅</span><span>Awesome! You have added Experience</span></div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class=\"user-checklist-item error\"><span class=\"icon\">❌</span><span>Please add Experience. It will help you to stand out from crowd</span></div>', unsafe_allow_html=True)

                if 'INTERNSHIPS'  in resume_text:
                    resume_score = resume_score + 6
                    st.markdown('<div class=\"user-checklist-item success\"><span class=\"icon\">✅</span><span>Awesome! You have added Internships</span></div>', unsafe_allow_html=True)
                elif 'INTERNSHIP'  in resume_text:
                    resume_score = resume_score + 6
                    st.markdown('<div class=\"user-checklist-item success\"><span class=\"icon\">✅</span><span>Awesome! You have added Internships</span></div>', unsafe_allow_html=True)
                elif 'Internships'  in resume_text:
                    resume_score = resume_score + 6
                    st.markdown('<div class=\"user-checklist-item success\"><span class=\"icon\">✅</span><span>Awesome! You have added Internships</span></div>', unsafe_allow_html=True)
                elif 'Internship'  in resume_text:
                    resume_score = resume_score + 6
                    st.markdown('<div class=\"user-checklist-item success\"><span class=\"icon\">✅</span><span>Awesome! You have added Internships</span></div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class=\"user-checklist-item error\"><span class=\"icon\">❌</span><span>Please add Internships. It will help you to stand out from crowd</span></div>', unsafe_allow_html=True)

                if 'SKILLS'  in resume_text:
                    resume_score = resume_score + 7
                    st.markdown('<div class=\"user-checklist-item success\"><span class=\"icon\">✅</span><span>Awesome! You have added Skills</span></div>', unsafe_allow_html=True)
                elif 'SKILL'  in resume_text:
                    resume_score = resume_score + 7
                    st.markdown('<div class=\"user-checklist-item success\"><span class=\"icon\">✅</span><span>Awesome! You have added Skills</span></div>', unsafe_allow_html=True)
                elif 'Skills'  in resume_text:
                    resume_score = resume_score + 7
                    st.markdown('<div class=\"user-checklist-item success\"><span class=\"icon\">✅</span><span>Awesome! You have added Skills</span></div>', unsafe_allow_html=True)
                elif 'Skill'  in resume_text:
                    resume_score = resume_score + 7
                    st.markdown('<div class=\"user-checklist-item success\"><span class=\"icon\">✅</span><span>Awesome! You have added Skills</span></div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class=\"user-checklist-item error\"><span class=\"icon\">❌</span><span>Please add Skills. It will help you a lot</span></div>', unsafe_allow_html=True)

                if 'HOBBIES' in resume_text:
                    resume_score = resume_score + 4
                    st.markdown('<div class=\"user-checklist-item success\"><span class=\"icon\">✅</span><span>Awesome! You have added your Hobbies</span></div>', unsafe_allow_html=True)
                elif 'Hobbies' in resume_text:
                    resume_score = resume_score + 4
                    st.markdown('<div class=\"user-checklist-item success\"><span class=\"icon\">✅</span><span>Awesome! You have added your Hobbies</span></div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class=\"user-checklist-item error\"><span class=\"icon\">❌</span><span>Please add Hobbies. It will show your personality to the Recruiters and give the assurance that you are fit for this role or not.</span></div>', unsafe_allow_html=True)

                if 'INTERESTS'in resume_text:
                    resume_score = resume_score + 5
                    st.markdown('<div class=\"user-checklist-item success\"><span class=\"icon\">✅</span><span>Awesome! You have added your Interest</span></div>', unsafe_allow_html=True)
                elif 'Interests'in resume_text:
                    resume_score = resume_score + 5
                    st.markdown('<div class=\"user-checklist-item success\"><span class=\"icon\">✅</span><span>Awesome! You have added your Interest</span></div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class=\"user-checklist-item error\"><span class=\"icon\">❌</span><span>Please add Interest. It will show your interest other that job.</span></div>', unsafe_allow_html=True)

                if 'ACHIEVEMENTS' in resume_text:
                    resume_score = resume_score + 13
                    st.markdown('<div class=\"user-checklist-item success\"><span class=\"icon\">✅</span><span>Awesome! You have added your Achievements </span></div>', unsafe_allow_html=True)
                elif 'Achievements' in resume_text:
                    resume_score = resume_score + 13
                    st.markdown('<div class=\"user-checklist-item success\"><span class=\"icon\">✅</span><span>Awesome! You have added your Achievements </span></div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class=\"user-checklist-item error\"><span class=\"icon\">❌</span><span>Please add Achievements. It will show that you are capable for the required position.</span></div>', unsafe_allow_html=True)

                if 'CERTIFICATIONS' in resume_text:
                    resume_score = resume_score + 12
                    st.markdown('<div class=\"user-checklist-item success\"><span class=\"icon\">✅</span><span>Awesome! You have added your Certifications </span></div>', unsafe_allow_html=True)
                elif 'Certifications' in resume_text:
                    resume_score = resume_score + 12
                    st.markdown('<div class=\"user-checklist-item success\"><span class=\"icon\">✅</span><span>Awesome! You have added your Certifications </span></div>', unsafe_allow_html=True)
                elif 'Certification' in resume_text:
                    resume_score = resume_score + 12
                    st.markdown('<div class=\"user-checklist-item success\"><span class=\"icon\">✅</span><span>Awesome! You have added your Certifications </span></div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class=\"user-checklist-item error\"><span class=\"icon\">❌</span><span>Please add Certifications. It will show that you have done some specialization for the required position.</span></div>', unsafe_allow_html=True)

                if 'PROJECTS' in resume_text:
                    resume_score = resume_score + 19
                    st.markdown('<div class=\"user-checklist-item success\"><span class=\"icon\">✅</span><span>Awesome! You have added your Projects</span></div>', unsafe_allow_html=True)
                elif 'PROJECT' in resume_text:
                    resume_score = resume_score + 19
                    st.markdown('<div class=\"user-checklist-item success\"><span class=\"icon\">✅</span><span>Awesome! You have added your Projects</span></div>', unsafe_allow_html=True)
                elif 'Projects' in resume_text:
                    resume_score = resume_score + 19
                    st.markdown('<div class=\"user-checklist-item success\"><span class=\"icon\">✅</span><span>Awesome! You have added your Projects</span></div>', unsafe_allow_html=True)
                elif 'Project' in resume_text:
                    resume_score = resume_score + 19
                    st.markdown('<div class=\"user-checklist-item success\"><span class=\"icon\">✅</span><span>Awesome! You have added your Projects</span></div>', unsafe_allow_html=True)
                else:
                    st.markdown('<div class=\"user-checklist-item error\"><span class=\"icon\">❌</span><span>Please add Projects. It will show that you have done work related the required position or not.</span></div>', unsafe_allow_html=True)

                