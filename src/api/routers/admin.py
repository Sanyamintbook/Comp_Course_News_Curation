from fastapi import APIRouter, UploadFile, File, Form, HTTPException
import json
import os
from src.database.vector_manager import VectorManager
from src.ai_processing.gatekeeper import AIGatekeeper

router = APIRouter()
db = VectorManager()
gatekeeper = AIGatekeeper()

@router.post("/api/admin/upload")
async def upload_dataset(module: str = Form(...), file: UploadFile = File(...)):
    """Receives a JSON file, embeds the content, and updates the FAISS database."""
    if not file.filename.endswith(".json"):
        raise HTTPException(status_code=400, detail="Only JSON files are supported.")
        
    try:
        content = await file.read()
        data = json.loads(content.decode("utf-8"))
        
        if not isinstance(data, list):
            raise HTTPException(status_code=400, detail="JSON must contain a list of objects.")
            
        success_count = 0
        for item in data:
            title = item.get("title", "Unknown Title")
            desc = item.get("description", "")
            if not desc:
                continue
                
            # Generate embedding
            emb = gatekeeper.generate_embedding(desc)
            if emb:
                db.add_vector(module, emb, {
                    "title": title,
                    "description": desc,
                    "link": item.get("link", "None"),
                    "published": item.get("published", "Unknown"),
                    "subject": item.get("subject", "General")
                })
                success_count += 1
                
        # Save FAISS index
        db.save_index(module)
        
        return {"detail": f"Successfully embedded and saved {success_count} items to the '{module}' module."}
        
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
