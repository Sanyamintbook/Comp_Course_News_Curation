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
    title = doc.add_heading('Unified Educational Platform - Project Flow', 0)
    title.alignment = WD_ALIGN_PARAGRAPH.CENTER
    
    doc.add_paragraph('This document outlines the architecture and data flow of the Unified Educational Platform (Comp_Course_News_Curation).')

    # Section 1: Overview
    doc.add_heading('1. Overview', level=1)
    doc.add_paragraph(
        "The project is a personalized educational platform featuring a 5-module dashboard tailored for students. "
        "It uses a Streamlit frontend and a FastAPI backend powered by advanced AI processing (Ollama + FAISS) "
        "to deliver highly relevant learning materials, news, and quizzes based on the student's profile."
    )

    # Section 2: Architecture Components
    doc.add_heading('2. Architecture Components', level=1)
    
    p = doc.add_paragraph()
    p.add_run('Frontend (Streamlit): ').bold = True
    p.add_run('Located in frontend/app.py. It handles user interactions, profile building, and rendering the 5-tab dashboard.')
    
    p = doc.add_paragraph()
    p.add_run('Backend (FastAPI): ').bold = True
    p.add_run('Located in src/api/main.py. It exposes REST endpoints (e.g., /api/profile_dashboard) to serve the frontend.')
    
    p = doc.add_paragraph()
    p.add_run('AI Gatekeeper: ').bold = True
    p.add_run('Located in src/ai_processing/gatekeeper.py. It acts as the core AI engine, utilizing Ollama (qwen3:8b and mxbai-embed-large). It is responsible for content filtering, embedding generation, quiz generation, and mapping student profiles to Indian competitive exams and NEP 2020 skill courses.')
    
    p = doc.add_paragraph()
    p.add_run('Database (FAISS): ').bold = True
    p.add_run('Vector database used for semantic search of educational materials. Managed by src/database/vector_manager.py.')

    # Section 3: User Flow
    doc.add_heading('3. User Flow', level=1)
    flow = [
        "1. Access Dashboard: The user accesses the Streamlit web application.",
        "2. Profile Building: The user fills out their profile in the sidebar (Grade Level, Target Career, Favorite Subjects, Hobbies).",
        "3. Request Generation: Upon clicking 'Generate Dashboard', the frontend sends a POST request with the profile payload to the FastAPI backend.",
        "4. AI Processing & Filtering: The backend retrieves relevant materials from the FAISS database. The AI Gatekeeper strictly filters these materials, keeping only those aligned with the student's target career and core subjects.",
        "5. Content Generation: The AI Gatekeeper dynamically generates a 5-question AI quiz based on the user's grade and subjects, as well as an educational fun fact.",
        "6. Dashboard Rendering: The backend returns a unified payload. The frontend renders this data across 5 interactive tabs: News, Courses, Competitive, Tests, and Leisure."
    ]
    for step in flow:
        doc.add_paragraph(step, style='List Bullet')

    # Section 4: Admin & Data Ingestion Flow
    doc.add_heading('4. Admin & Data Ingestion Flow', level=1)
    admin_flow = [
        "1. Admin Panel: Accessible via the Streamlit sidebar, allowing administrators to upload premium courses and competitive materials (JSON).",
        "2. Embedding: The AI Gatekeeper processes these uploads by generating dense vector embeddings using the mxbai-embed-large model.",
        "3. Database Rebuilding (rebuild_db.py): The system can decode corrupted FAISS indices (e.g., /GXX font glyphs) and re-embed them via the AI Gatekeeper to cleanly populate the FAISS indices."
    ]
    for step in admin_flow:
        doc.add_paragraph(step, style='List Bullet')

    doc.save('Project_Flow.docx')
    print("Project flow document successfully created at 'Project_Flow.docx'")

if __name__ == '__main__':
    create_doc()
