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
    title = doc.add_heading('Unified Educational Platform - User Journey Flow', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    doc.add_paragraph('This document outlines the user experience and journey through the Personalized Educational Platform.')

    # Section 1: Introduction
    doc.add_heading('1. Introduction', level=1)
    doc.add_paragraph(
        "The platform acts as a smart, unified learning companion for students. "
        "It acts like a personal tutor that understands a student's career aspirations, grade level, "
        "and interests, and curates the perfect study materials, news, and quizzes for them."
    )

    # Section 2: The Student Journey
    doc.add_heading('2. The Student Journey', level=1)
    
    doc.add_heading('Step 1: Profile Creation', level=2)
    doc.add_paragraph(
        "When a student first visits the platform, they are greeted with a 'Profile Builder' panel. "
        "Here, they provide key information about themselves to help the AI understand their needs:\n"
        "• Grade Level (e.g., 6-8, 9-12, Undergrad)\n"
        "• Target Career (e.g., Doctor, Engineer, Artist)\n"
        "• Favorite Subjects (e.g., Biology, Math)\n"
        "• Hobbies (e.g., Drawing, Chess)"
    )

    doc.add_heading('Step 2: Dashboard Generation', level=2)
    doc.add_paragraph(
        "After building their profile, the student clicks 'Generate Dashboard'. "
        "Behind the scenes, the AI analyzes their goals and filters through thousands of educational resources. "
        "It carefully selects only the materials that are relevant to their chosen career and subjects, "
        "ensuring a distraction-free learning environment."
    )

    doc.add_heading('Step 3: Exploring the 5 Learning Modules', level=2)
    doc.add_paragraph("The generated dashboard is divided into 5 interactive tabs for different learning experiences:")
    
    p = doc.add_paragraph()
    p.add_run('📰 News: ').bold = True
    p.add_run('Provides safe, educational, and age-appropriate news articles tailored to the student\'s interests. It keeps them updated on real-world applications of what they are learning.')
    
    p = doc.add_paragraph()
    p.add_run('📚 Courses: ').bold = True
    p.add_run('Suggests specific video courses and skill-building materials based on the NEP 2020 policy guidelines, strictly tailored for the student\'s particular age group and target career.')
    
    p = doc.add_paragraph()
    p.add_run('🏆 Competitive Exams: ').bold = True
    p.add_run('Recommends preparation materials for Indian competitive exams or Olympiads suitable for their age and goals (e.g., NTSE for middle schoolers, JEE/NEET for high schoolers).')
    
    p = doc.add_paragraph()
    p.add_run('📝 AI Knowledge Check (Tests): ').bold = True
    p.add_run('A fun, custom 5-question multiple-choice quiz generated instantly by the AI, testing the student on their core subjects. It provides immediate feedback on their answers.')
    
    p = doc.add_paragraph()
    p.add_run('🎮 Leisure: ').bold = True
    p.add_run('Offers relaxing yet educational content linked to their hobbies, ensuring a balanced study schedule.')
    
    doc.add_heading('Step 4: Fun Facts & Insights', level=2)
    doc.add_paragraph(
        "To make learning engaging, the dashboard also displays a unique 'Fun Fact'—a rare and mind-blowing piece of information related to the student's career or subjects."
    )

    # Section 3: The Administrator Journey
    doc.add_heading('3. The Administrator Journey', level=1)
    
    doc.add_paragraph(
        "The platform also has a dedicated control panel for teachers or administrators."
    )
    
    doc.add_heading('Step 1: Content Upload', level=2)
    doc.add_paragraph(
        "Administrators can easily upload new premium course packages, practice tests, or competitive materials directly into the system using file uploads."
    )

    doc.add_heading('Step 2: AI Curation', level=2)
    doc.add_paragraph(
        "Once uploaded, the platform's AI automatically 'reads' and understands the new materials. It categorizes them so that they instantly become available to the right students based on their personalized dashboards."
    )

    doc.save('User_Journey_Flow.docx')
    print("Functional flow document successfully created at 'User_Journey_Flow.docx'")

if __name__ == '__main__':
    create_doc()
