import streamlit as st
import re
import html
import base64
from datetime import datetime
import json
import os

# =============================================================
# 1. SMART TEXT PROCESSING ENGINE
# =============================================================
def clean_text(text, make_title=False):
    text = text.strip()
    if not text:
        return ""
    if make_title:
        words = text.split()
        protected_words = []
        for w in words:
            if w.isupper() and len(w) > 1:
                protected_words.append(w)
            else:
                protected_words.append(w.capitalize())
        return " ".join(protected_words)
    sentences = re.split(r'(?<=[.!?])\s*', text)
    capitalized_sentences = [s[0].upper() + s[1:] for s in sentences if s.strip()]
    return " ".join(capitalized_sentences)

PROPER_NOUNS = {
    'ali', 'ahmed', 'hassan', 'fatima', 'sara', 'usman', 'zara', 'bilal', 'ayesha',
    'pakistan', 'karachi', 'lahore', 'islamabad', 'peshawar', 'quetta',
    'google', 'microsoft', 'amazon', 'meta', 'apple', 'netflix', 'openai',
    'python', 'pytorch', 'tensorflow', 'pandas', 'numpy', 'linkedin', 'github',
}

def capitalize_proper_nouns(text):
    def fix_word(w):
        clean = w.strip('.,!?:;()[]"\'')
        if clean.lower() in PROPER_NOUNS:
            return w.replace(clean, clean.capitalize(), 1)
        return w
    return ' '.join(fix_word(w) for w in text.split())

def get_article(word):
    if not word:
        return ""
    word_clean = word.strip().upper()
    vowel_sounds = ['A', 'E', 'I', 'O', 'U']
    vowel_acronyms = ['L', 'M', 'N', 'R', 'S', 'X', 'H']
    if word_clean[0] in vowel_sounds or (len(word_clean) > 1 and word_clean[0] in vowel_acronyms):
        return "an"
    return "a"

def merge_and_format_tags(system_tags, user_tags_raw):
    final_tags_set = set(tag.strip() for tag in system_tags)
    if user_tags_raw and user_tags_raw.strip():
        raw_splits = re.split(r'[\s,]+', user_tags_raw)
        for tag in raw_splits:
            clean_tag = tag.replace('#', '').strip()
            if clean_tag:
                formatted_user_tag = "#" + clean_tag[0].upper() + clean_tag[1:]
                final_tags_set.add(formatted_user_tag)
    return " ".join(sorted(list(final_tags_set)))

def sanitize_html(text):
    text = html.escape(text)
    text = re.sub(r'<[^>]*>', '', text)
    return text

# =============================================================
# 2. TEMPLATE BLOCKS
# =============================================================

def _en_project(title, details, acc, tech, tags):
    acc_line = f"• Global Accuracy Achieved: {acc}%\n" if acc else ""
    tech_line = tech if tech else "Modern Tech Stack"
    if not details.strip():
        details = "• End-to-end pipeline successfully deployed\n• Performance optimized and thoroughly tested\n• Complete documentation added\n• Ready for production use"
    return (
        f"🚀 Building in Public: Scaled my latest project '{title}'!\n\n"
        f"I'm excited to share that I have successfully completed and optimized the "
        f"end-to-end processing script.\n\n"
        f"📊 Core Details & Insights:\n"
        f"{acc_line}{details}\n\n"
        f"💻 Tech Stack: {tech_line}.\n\n{tags}"
    )

def _en_recruiter_internship(title, details, acc, tech, tags):
    if not details.strip():
        details = "• Currently enrolled in BS/MSc (CS/IT/DS)\n• Strong foundation in Python/SQL\n• Eager to learn and contribute"
    return (
        f"🚨 New Opportunity Alert: '{title}'! 🚨\n\n"
        f"Hello network, our team is looking for talented interns.\n\n"
        f"📌 Role Details & Requirements:\n{details}\n\n"
        f"Interested candidates can apply below. 👇\n\n{tags}"
    )

def _en_recruiter_job(title, details, acc, tech, tags):
    if not details.strip():
        details = "• 2-4 years of relevant experience\n• Strong proficiency in Python/Data Science\n• Bachelor's degree in CS/related field"
    return (
        f"🚨 New Career Opportunity: Openings for '{title}'! 🚨\n\n"
        f"Hello network, my organization is looking for technical professionals.\n\n"
        f"📌 Core Requirements:\n{details}\n\n"
        f"Apply via the application portal. 👇\n\n{tags}"
    )

def _en_user_internship(title, details, acc, tech, tags):
    if not details.strip():
        details = "• Working on real-world production systems\n• Learning from industry experts\n• Building my professional network"
    art = get_article(title)
    return (
        f"🎉 Excited to share a personal milestone! I have accepted an offer and am starting "
        f"{art} '{title}' role!\n\n"
        f"💼 What I'll be focusing on:\n{details}\n\n"
        f"A huge thank you to everyone who supported me! 🙏\n\n{tags}"
    )

def _en_user_job(title, details, acc, tech, tags):
    if not details.strip():
        details = "• Leading technical initiatives\n• Collaborating with cross-functional teams\n• Architecting scalable solutions"
    art = get_article(title)
    return (
        f"💼 Corporate Update: I'm thrilled to share that I'm starting a new position as "
        f"{art} '{title}'!\n\n"
        f"🚀 Core Responsibilities:\n{details}\n\n"
        f"Thank you to my network for the constant support! ✨\n\n{tags}"
    )

def _en_learning(title, details, acc, tech, tags):
    if not details.strip():
        details = "• Deep dive into core architecture patterns\n• Hands-on implementation of best practices\n• Practical examples and use cases studied"
    return (
        f"📚 Today's Learning: '{title}'\n\n"
        f"Consistency is key in tech. Today, I focused on deep-diving into this domain.\n\n"
        f"💡 Key Takeaways:\n{details}\n\n"
        f"What are you learning today? 👇\n\n{tags}"
    )

def _en_tips(title, details, acc, tech, tags):
    if not details.strip():
        details = "• Use list comprehensions for faster operations\n• Implement caching for repeated calculations\n• Write modular and reusable functions"
    return (
        f"💡 Quick Tech Tip: {title}\n\n"
        f"Here is a quick workflow optimization hack:\n\n"
        f"🔍 Implementation:\n{details}\n\n"
        f"Hope this adds value to your workflow! 📌\n\n{tags}"
    )

# Roman Urdu versions
def _ur_project(title, details, acc, tech, tags):
    acc_line = f"• Hasil Kardah Accuracy: {acc}%\n" if acc else ""
    tech_line = tech if tech else "Python aur modern tools"
    if not details.strip():
        details = "• End-to-end pipeline successfully deploy ho chuki hai\n• Performance optimize aur test ho chuki hai\n• Production use ke liye ready hai"
    return (
        f"🚀 Building in Public: Maine apna naya project '{title}' complete kar liya hai!\n\n"
        f"📊 Project ki Insights:\n{acc_line}{details}\n\n"
        f"💻 Tech Stack: {tech_line}.\n\n{tags}"
    )

def _ur_recruiter_internship(title, details, acc, tech, tags):
    if not details.strip():
        details = "• BS/MSc (CS/IT/DS) mein enrolled hon\n• Python/SQL mein strong foundation ho\n• Seekhne ka jazba ho"
    return (
        f"🚨 Naya Internship Alert: '{title}'! 🚨\n\n"
        f"Hamari team ko interns ki talaash hai.\n\n"
        f"📌 Requirements:\n{details}\n\n"
        f"Agar interested hain toh apply karein. 👇\n\n{tags}"
    )

def _ur_recruiter_job(title, details, acc, tech, tags):
    if not details.strip():
        details = "• 2-4 saal ka experience ho\n• Python/Data Science mein proficiency ho\n• Bachelor's degree ho"
    return (
        f"🚨 Career ka Naya Mauka: '{title}'! 🚨\n\n"
        f"📌 Requirements:\n{details}\n\n"
        f"Interested log apply kar sakte hain. 👇\n\n{tags}"
    )

def _ur_user_internship(title, details, acc, tech, tags):
    if not details.strip():
        details = "• Real-world systems par kaam karunga/karungi\n• Industry experts se seekhna\n• Professional network build karna"
    return (
        f"🎉 Nayi shuruat! Maine '{title}' internship start kar di hai!\n\n"
        f"💼 Mera focus:\n{details}\n\n"
        f"Sab ka shukriya! 🙏\n\n{tags}"
    )

def _ur_user_job(title, details, acc, tech, tags):
    if not details.strip():
        details = "• Technical initiatives ki leadership\n• Cross-functional teams ke saath collaboration\n• Scalable solutions ka design"
    return (
        f"💼 Career Update: Main naye position '{title}' par start kar raha/rahi hoon!\n\n"
        f"🚀 Mera Role:\n{details}\n\n"
        f"Network ka shukriya! ✨\n\n{tags}"
    )

def _ur_learning(title, details, acc, tech, tags):
    if not details.strip():
        details = "• Core architecture patterns ko samjha\n• Best practices ko implement kiya\n• Practical examples study kiye"
    return (
        f"📚 Aaj ki Learning: '{title}'\n\n"
        f"💡 Takeaways:\n{details}\n\n"
        f"Aap kya seekh rahe hain? 👇\n\n{tags}"
    )

def _ur_tips(title, details, acc, tech, tags):
    if not details.strip():
        details = "• List comprehensions use karo\n• Caching implement karo\n• Modular code likho"
    return (
        f"💡 Tech Tip: {title}\n\n"
        f"🔍 Implementation:\n{details}\n\n"
        f"Umeed hai kaam aayega! 📌\n\n{tags}"
    )

POST_TEMPLATES = {
    "English (Professional)": {
        "Recruiter - Internship Opportunity": _en_recruiter_internship,
        "Recruiter - Job Opportunity": _en_recruiter_job,
        "User - Internship Offer": _en_user_internship,
        "User - Job Offer": _en_user_job,
        "Project Upload": _en_project,
        "Daily Learning / Roadmap": _en_learning,
        "Tips & Tricks": _en_tips,
    },
    "Roman Urdu (Conversational)": {
        "Recruiter - Internship Opportunity": _ur_recruiter_internship,
        "Recruiter - Job Opportunity": _ur_recruiter_job,
        "User - Internship Offer": _ur_user_internship,
        "User - Job Offer": _ur_user_job,
        "Project Upload": _ur_project,
        "Daily Learning / Roadmap": _ur_learning,
        "Tips & Tricks": _ur_tips,
    }
}

BASE_TAGS_MAP = {
    "Recruiter - Internship Opportunity": ["#Hiring", "#InternshipOpportunity", "#TechInterns"],
    "Recruiter - Job Opportunity": ["#Hiring", "#JobOpportunity", "#TechJobs"],
    "User - Internship Offer": ["#Internship", "#CareerUpdate", "#NewJourney"],
    "User - Job Offer": ["#NewJob", "#CareerGrowth", "#TechIndustry"],
    "Project Upload": ["#MachineLearning", "#DataScience", "#BuildingInPublic"],
    "Daily Learning / Roadmap": ["#ContinuousLearning", "#TechRoadmap", "#Python"],
    "Tips & Tricks": ["#TechTips", "#PythonHacks", "#CodingLife"],
}

def determine_final_intent(selected_dropdown, title, details):
    combined_text = f"{title.lower()} {details.lower()}"
    recruiter_triggers = ['hiring', 'apply now', 'opening', 'vacancy', 'looking for']

    if selected_dropdown == "Internship Offer":
        if any(kw in combined_text for kw in recruiter_triggers):
            return "Recruiter - Internship Opportunity"
        return "User - Internship Offer"
    elif selected_dropdown == "Job Offer":
        if any(kw in combined_text for kw in recruiter_triggers):
            return "Recruiter - Job Opportunity"
        return "User - Job Offer"
    elif selected_dropdown == "Hiring / Opportunity Share":
        if any(kw in combined_text for kw in ['intern', 'internship']):
            return "Recruiter - Internship Opportunity"
        return "Recruiter - Job Opportunity"
    elif selected_dropdown == "Project Upload":
        if any(kw in combined_text for kw in ['tip', 'trick', 'hack']):
            return "Tips & Tricks"
        return "Project Upload"
    return selected_dropdown

# =============================================================
# 3. STREAMLIT UI
# =============================================================

st.set_page_config(
    page_title="LinkedIn Post Generator",
    page_icon="📝",
    layout="wide"
)

# Custom CSS
st.markdown("""
    <style>
    .main-header {
        background: linear-gradient(90deg, #0a66c2 0%, #0a66c2 100%);
        padding: 20px;
        border-radius: 10px;
        color: white;
        text-align: center;
        margin-bottom: 30px;
    }
    .stTextArea textarea {
        font-size: 14px;
    }
    </style>
""", unsafe_allow_html=True)

# Header
st.markdown('<div class="main-header"><h1>📝 LinkedIn Post Generator</h1><p>Generate engaging LinkedIn posts for tech professionals</p></div>', unsafe_allow_html=True)

# Sidebar
with st.sidebar:
    st.header("⚙️ Settings")
    
    language = st.selectbox(
        "🌐 Post Language",
        ["English (Professional)", "Roman Urdu (Conversational)"],
        help="Choose your preferred language"
    )
    
    post_type = st.selectbox(
        "📌 Post Type",
        ["Project Upload", "Internship Offer", "Job Offer", 
         "Hiring / Opportunity Share", "Daily Learning / Roadmap", "Tips & Tricks"]
    )
    
    st.divider()
    st.caption("💡 Tip: Leave details empty for professional default content")

# Main content - Two columns
col1, col2 = st.columns([1, 1], gap="large")

with col1:
    st.subheader("📝 Post Details")
    
    title = st.text_input("**Title / Role**", placeholder="e.g., Data Scientist, AI Engineer")
    tech_stack = st.text_input("**💻 Tech Stack**", placeholder="e.g., Python, Pandas, PyTorch")
    accuracy = st.text_input("**🎯 Accuracy (%)**", placeholder="e.g., 94.2")
    custom_tags = st.text_input("**🏷️ Custom Tags**", placeholder="e.g., career, AI, opensource (comma separated)")
    
    uploaded_files = st.file_uploader(
        "**📎 Attach Files**", 
        accept_multiple_files=True,
        type=['png', 'jpg', 'jpeg', 'pdf', 'txt']
    )

with col2:
    st.subheader("📄 Main Content")
    
    details = st.text_area(
        "**Write your post content here**",
        placeholder="Describe your project, job, internship or share your learnings...\n(Leave empty for professional default content)",
        height=250
    )
    
    char_count = len(details)
    if char_count > 3000:
        st.error(f"⚠️ {char_count}/3000 characters - Exceeds LinkedIn limit!")
    elif char_count > 2800:
        st.warning(f"⚠️ {char_count}/3000 characters - Getting close to limit")
    else:
        st.success(f"✅ {char_count}/3000 characters")
    
    # Generate button
    generate = st.button("⚡ Generate Post", type="primary", use_container_width=True)

# Generate post logic
if generate:
    if not title and not details:
        st.error("❌ Please fill in either Title or Details!")
    else:
        with st.spinner("Generating your LinkedIn post..."):
            # Process inputs
            clean_title = clean_text(title, make_title=True) if title else "Untitled"
            clean_tech = clean_text(tech_stack, make_title=True) if tech_stack else ""
            clean_details = sanitize_html(details)
            clean_details = capitalize_proper_nouns(clean_text(clean_details))
            
            # Determine intent and generate
            final_intent = determine_final_intent(post_type, clean_title, clean_details)
            merged_tags = merge_and_format_tags(BASE_TAGS_MAP[final_intent], custom_tags)
            
            generated_post = POST_TEMPLATES[language][final_intent](
                clean_title, clean_details, accuracy, clean_tech, merged_tags
            )
            
            # Success message
            st.success("✅ Post Generated Successfully!")
            
            # Display post with LinkedIn styling
            st.markdown("---")
            st.subheader("📱 Your LinkedIn Post")
            
            st.markdown(f"""
            <div style="border: 2px solid #0a66c2; border-radius: 12px; padding: 20px; background: #f8fafc; margin: 10px 0;">
                <div style="display: flex; justify-content: space-between; margin-bottom: 10px;">
                    <strong style="color: #0a66c2;">👁️ Post Preview</strong>
                    <span style="color: gray; font-size: 12px;">{len(generated_post)} characters</span>
                </div>
                <div style="border-top: 1px solid #ddd; padding-top: 10px; white-space: pre-wrap; font-family: -apple-system, BlinkMacSystemFont, 'Segoe UI', Roboto, sans-serif;">
                    {generated_post.replace(chr(10), '<br>')}
                </div>
            </div>
            """, unsafe_allow_html=True)
            
            # Action buttons
            col_a, col_b, col_c = st.columns(3)
            with col_a:
                st.download_button(
                    label="📥 Download",
                    data=generated_post,
                    file_name=f"linkedin_post_{datetime.now().strftime('%Y%m%d_%H%M%S')}.txt",
                    mime="text/plain"
                )
            with col_b:
                st.code(generated_post, language='text', line_numbers=False)
                st.caption("📋 Select and copy the text above")
            with col_c:
                st.markdown("[🌐 Open LinkedIn](https://www.linkedin.com/feed/)", unsafe_allow_html=True)
            
            # Show attached files
            if uploaded_files:
                st.subheader("📎 Attached Files")
                for file in uploaded_files:
                    if file.type.startswith('image/'):
                        st.image(file, width=150, caption=file.name)
                    else:
                        st.write(f"📄 {file.name}")

# Footer
st.markdown("---")
st.markdown("<center>Made with ❤️ for LinkedIn Professionals | Generate posts in English & Roman Urdu</center>", unsafe_allow_html=True)