import json
from ollama import Client
from typing import Dict, Any, Optional

class AIGatekeeper:
    def __init__(self, llm_model: str = "qwen3:8b", embed_model: str = "mxbai-embed-large"):
        # We use the models specified in your request
        self.llm_model = llm_model
        self.embed_model = embed_model
        # Configure client to connect to external Ollama server
        self.client = Client(host='http://10.80.100.214:11434')

    def analyze_article(self, article_text: str) -> Optional[Dict[str, Any]]:
        """
        Uses the Qwen LLM to analyze the article.
        Returns metadata if educational and safe, otherwise returns None.
        """
        prompt = f"""
        You are an AI gatekeeper for a student learning platform.
        Read the following short news snippet (which may just be a title).
        Make your best judgment to determine if it is educational and safe for students.
        It is perfectly fine if it is just a short title, do your best to categorize it!
        Extract the primary Subject and the appropriate Grade Level (e.g., '6-8', '9-12').
        
        Snippet/Title:
        {article_text[:2000]} # Limit length to avoid context overflow
        
        Respond ONLY with a valid JSON object in this exact format:
        {{
            "is_educational": true/false,
            "is_safe": true/false,
            "subject": "string",
            "grade_level": "string"
        }}
        """
        try:
            # We use Ollama to get the response, enforcing JSON format.
            response = self.client.chat(model=self.llm_model, messages=[
                {"role": "user", "content": prompt}
            ], format="json")
            
            result = json.loads(response['message']['content'])
            
            # Filtering logic: Discard if unsafe or non-educational
            if result.get("is_educational") and result.get("is_safe"):
                return {
                    "subject": result.get("subject", "General"),
                    "grade_level": result.get("grade_level", "All")
                }
            else:
                print("Article rejected by AI Gatekeeper.")
                return None
                
        except Exception as e:
            print(f"Error in LLM analysis: {str(e)}")
            return None

    def filter_materials(self, materials: list, career: str, subjects: list, grade_level: str = "All") -> list:
        """Uses the LLM to intelligently filter out irrelevant FAISS results."""
        if not materials: 
            return []
            
        # Assign temporary IDs so the LLM can reference them
        for i, m in enumerate(materials):
            m['_tmp_id'] = i
            
        prompt = f"""
        You are an AI educational curriculum expert.
        A student wants to be a {career}. Their core subjects are {', '.join(subjects)}. They are in grade {grade_level}.
        Here is a list of study materials:
        """
        for m in materials:
            prompt += f"\n- ID {m['_tmp_id']}: {m['title']}"
            if 'description' in m and m['description']:
                prompt += f" | Desc: {m['description'][:100]}"
                
        prompt += """
        You are an advanced curation engine for an ed-tech company. Your job is to curate the BEST possible materials for this student.
        Evaluate each item based on its title and description.
        - REMOVE any materials that are irrelevant to their specific profile. For example, if they are a Biology student, ban Math/Engineering. If they are an Engineering student, ban Biology/Medical.
        - ENSURE that the course suggestions adhere to the NEP 2020 policy guidelines for this specific age group (grade level).
        - RESTRICT any materials that are age-inappropriate or too complex for their grade level.
        - RESTRICT any pseudoscience, misinformation, or unverified claims (e.g., flat earth, anti-vaccine).
        - RESTRICT purely distracting "junk food" leisure (e.g., mind-numbing gaming streams) unless highly educational.
        - RESTRICT toxic, violent, or politically extreme content.
        - If a title is generic (e.g., "LT70", "CE114") use your knowledge to deduce what it is. If it does not match their career and core subjects, REMOVE IT.
        - Be aggressive. If an item does not clearly support the student's career or core subjects, REMOVE IT. 
        - ONLY keep IDs that are definitively relevant or at least safe and broadly applicable to their goals.
        Return ONLY a JSON list of approved IDs. Example: [0, 2, 3]
        """
        try:
            response = self.client.chat(model=self.llm_model, messages=[
                {"role": "user", "content": prompt}
            ])
            text = response['message']['content'].strip()
            
            import re, json
            match = re.search(r'\[.*?\]', text, re.DOTALL)
            if match:
                approved_ids = json.loads(match.group(0))
                return [m for m in materials if m['_tmp_id'] in approved_ids]
            return materials
        except Exception as e:
            print(f"LLM Filter Error: {e}")
            return materials

    def generate_embedding(self, text: str) -> list[float]:
        """Generates a dense vector embedding using mxbai."""
        try:
            response = self.client.embeddings(model=self.embed_model, prompt=text)
            return response['embedding']
        except Exception as e:
            print(f"Error generating embedding: {str(e)}")
            return []

    def generate_fun_fact(self, subjects: list, career: str) -> str:
        """Generates a quick 1-sentence educational fun fact based on student profile."""
        import random
        prompt = f"""
        You are an educational assistant. Provide exactly ONE interesting, mind-blowing educational fact 
        related to the subjects: {', '.join(subjects)} or the career: {career}.
        Ensure this is a highly unique and rare fact that people rarely hear. (Randomization Seed: {random.randint(1, 100000)})
        Keep it to exactly one short sentence. Do not add any introductory or concluding text. 
        Just the fact.
        """
        try:
            response = self.client.chat(model=self.llm_model, messages=[
                {"role": "user", "content": prompt}
            ], options={"temperature": 0.9})
            return response['message']['content'].strip(' "')
        except Exception as e:
            print(f"Error generating fun fact: {str(e)}")
            return "Learning new subjects builds new neural pathways in your brain!"


    def analyze_nep_and_exams(self, target_career: str, grade_level: str, favorite_subjects: list) -> dict:
        """Analyzes profile to map career to Indian competitive exams and suggest NEP 2020 skill courses."""
        subs = ", ".join(favorite_subjects) if favorite_subjects else "General"
        prompt = f"""
        Act as an expert Indian Career Counselor. 
        1. Map the career '{target_career}' to its specific Indian competitive entrance exam syllabus. 
           CRITICAL RULE: If the student is in grade '6-8', do NOT suggest advanced 12th-grade exams like IIT/JEE or NEET. Instead, map the career to a relevant middle-school scholarship or Olympiad preparation (e.g., 'NTSE Science', 'Math Olympiad').
        2. Based on the NEP 2020 framework for a student in grade '{grade_level}' interested in '{subs}', suggest exactly one highly specific skill course (e.g. 'Financial Literacy', 'Artificial Intelligence Basics', 'Vocational Woodworking').
        
        Return ONLY valid JSON in this exact format:
        {{"competitive_exam": "<EXACT_EXAM_NAME_HERE>", "nep_skill_course": "<EXACT_COURSE_NAME_HERE>"}}
        """
        try:
            response = self.client.chat(model=self.llm_model, messages=[
                {"role": "user", "content": prompt}
            ], format="json")
            return json.loads(response['message']['content'].strip())
        except Exception as e:
            print(f"NEP Analysis failed: {e}")
            return {"competitive_exam": f"{target_career} exam preparation", "nep_skill_course": subs}

if __name__ == "__main__":
    gatekeeper = AIGatekeeper()
    sample_text = "NASA's Perseverance rover has discovered new evidence of ancient organic molecules on Mars, suggesting that the Red Planet may have once harbored life."
    print("Analyzing sample text...")
    meta = gatekeeper.analyze_article(sample_text)
    print("Metadata extracted:", meta)
    if meta:
        print("Generating embedding...")
        emb = gatekeeper.generate_embedding(sample_text)
        print(f"Success! Embedding length: {len(emb)}")
