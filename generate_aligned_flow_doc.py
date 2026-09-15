import sys
try:
    from docx import Document
    from docx.shared import Pt, Inches
    from docx.enum.text import WD_ALIGN_PARAGRAPH
except ImportError:
    print("python-docx is not installed. Please install it using 'python -m pip install python-docx'")
    sys.exit(1)

def create_doc():
    doc = Document()
    
    # Title
    title = doc.add_heading('AI-Powered Student Curation Platform', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    doc.add_heading('1. Purpose', level=1)
    doc.add_paragraph("Build a single AI-powered curation platform that automatically understands educational content and delivers personalized curations across Courses, Competitive, News, and Leisure based on each student's profile and learning journey.")

    doc.add_heading('2. Business Principle', level=1)
    doc.add_paragraph("The platform does not depend on manually created metadata. Every new content item is processed by the AI Gatekeeper so the platform can understand what the content is about before it becomes searchable. The curation engine then combines the student's profile, AI understanding and student behaviour to deliver relevant curated materials.")

    doc.add_heading('3. End-to-End Architecture', level=1)
    
    flow = [
        "CONTENT SOURCES\n• Courses (JSON datasets)\n• Competitive materials\n• News\n• Leisure",
        "        ↓",
        "Content Ingestion (Automated Data Pipelines)",
        "        ↓",
        "AI Content Understanding & Quality Validation (AI Gatekeeper uses Qwen LLM)",
        "        ↓",
        "Embedding Generation (mxbai-embed-large)",
        "        ↓",
        "Content Repository + Vector Database (FAISS)",
        "────────────────────────────────────",
        "Student Onboarding (Streamlit Profile Builder)",
        "        ↓",
        "Student Profile (Grade Level, Career, Subjects, Hobbies)",
        "        ↓",
        "Semantic Search (FAISS retrieval)",
        "        ↓",
        "Business Rule Engine (NEP 2020 Policy Guidelines for Age Group, Core Subject Filtering)",
        "        ↓",
        "AI Re-ranking & Curation (Gatekeeper LLM Filtering)",
        "        ↓",
        "Personalized Dashboard (Streamlit Frontend)"
    ]
    for step in flow:
        doc.add_paragraph(step)

    doc.add_heading('4. Student Profile', level=1)
    doc.add_paragraph("The student initiates the journey through the 'Profile Builder' panel. Key information collected includes:\n• Grade Level\n• Target Career\n• Favorite Subjects\n• Hobbies")

    doc.add_heading('5. Curation Logic', level=1)
    doc.add_paragraph("The curation engine never asks AI to curate from the entire repository.\n\n"
                      "Step 1: Retrieve semantically similar content using embeddings from the FAISS database.\n"
                      "Step 2: Apply business rules (student profile, career goals, subject constraints, NEP 2020 policy rules for the specific age group).\n"
                      "Step 3: Ask the AI Gatekeeper (LLM) to intelligently filter and rank only the shortlisted candidates, removing irrelevant entries.\n"
                      "Step 4: Display the highest ranked curations.")

    doc.add_heading('6. Personalization Flow', level=1)
    doc.add_paragraph("Initial curations are based on the onboarding profile (target career, grade level, and core subjects). "
                      "As students interact with the dashboard, the AI will continuously adapt to provide more refined curations based on their evolving educational journey.")

    doc.add_heading('7. Dashboard Experience', level=1)
    doc.add_paragraph("Each module is dynamically personalized in the unified Streamlit interface:\n"
                      "• Courses – Suggests specific video courses and skill-building materials based on the NEP 2020 policy guidelines, strictly tailored for the student's particular age group and target career. (e.g., an 8th grader aiming to be an engineer will see age-appropriate introductory robotics or coding courses).\n"
                      "• Competitive – Recommends highly targeted preparation materials for Indian competitive exams or Olympiads suitable for their age and goals. (e.g., IIT-JEE or NEET material for high schoolers, NTSE or Math Olympiad material for middle schoolers).\n"
                      "• News – Provides safe, educational, and age-appropriate news articles tailored to their interests to keep them updated on real-world applications of their subjects. (e.g., recent NASA discoveries for a student interested in astronomy).\n"
                      "• Leisure – Suggests relaxing yet mentally stimulating content and activities linked to their personal hobbies to maintain a balanced schedule. (e.g., chess strategies or drawing tutorials).\n\n"
                      "The dashboard also displays a unique 'Fun Fact'—a rare and mind-blowing piece of information related to the student's career or subjects.")

    doc.add_heading('8. Mandatory Components', level=1)
    components = [
        "• Content Ingestion",
        "• AI Content Understanding (Gatekeeper LLM Categorization)",
        "• Embedding Generation (mxbai-embed-large)",
        "• Vector Database (FAISS vector_manager)",
        "• Student Profile Builder",
        "• Semantic Search Retrieval",
        "• Business Rule Engine (NEP 2020 rules, subject filtering)",
        "• AI Re-ranking & Filtering",
        "• Personalized Dashboard (Streamlit UI)"
    ]
    for c in components:
        doc.add_paragraph(c)

    doc.add_heading('9. Future Enhancements', level=1)
    doc.add_paragraph("Collaborative filtering, curation explanations, adaptive learning paths, detailed analytics dashboards and continuous model evaluation to further refine the AI Gatekeeper.")

    doc.add_heading('10. Conclusion', level=1)
    doc.add_paragraph("This architecture separates content understanding from curation. The AI Gatekeeper first embeds and understands content, then the curation engine combines semantic similarity, NEP 2020 business rules, and the student's profile to deliver an automated, highly personalized educational dashboard. The design is modular, scalable, and effectively delivers all 4 core modules seamlessly.")

    doc.save('User_Journey_Flow.docx')
    print("Curation flow document successfully created at 'User_Journey_Flow.docx'")

if __name__ == '__main__':
    create_doc()
