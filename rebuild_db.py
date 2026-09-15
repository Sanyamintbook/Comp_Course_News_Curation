import os
import sys
import pickle
import re
import faiss

# Add project root to path
sys.path.append(os.path.abspath(os.path.dirname(__file__)))

from src.database.vector_manager import VectorManager
from src.ai_processing.gatekeeper import AIGatekeeper

def decode_glyph_text(corrupted_text):
    """Decodes /GXX font glyphs back to ASCII text."""
    if not corrupted_text: return ""
    # Find all /G<digits>
    matches = re.findall(r'/G(\d+)', corrupted_text)
    if matches:
        try:
            return ''.join(chr(int(x)) for x in matches)
        except Exception:
            return corrupted_text
    return corrupted_text

def rebuild_module(target_module, external_dir, gatekeeper, db):
    print(f"Rebuilding module: {target_module} from {external_dir}")
    if not os.path.exists(external_dir):
        print(f"Error: Directory {external_dir} does not exist.")
        return

    added = 0
    for subdir in os.listdir(external_dir):
        subdir_path = os.path.join(external_dir, subdir)
        if not os.path.isdir(subdir_path):
            continue
            
        pkl_path = os.path.join(subdir_path, 'index.pkl')
        if os.path.exists(pkl_path):
            try:
                with open(pkl_path, 'rb') as f:
                    pkl_data = pickle.load(f)
                    
                docstore = None
                if isinstance(pkl_data, tuple) and len(pkl_data) > 0:
                    docstore_obj = pkl_data[0]
                    if hasattr(docstore_obj, '_dict'):
                        docstore = docstore_obj._dict
                
                if docstore and isinstance(pkl_data, tuple) and len(pkl_data) > 1:
                    idx_to_id = pkl_data[1]
                    for i in range(len(idx_to_id)):
                        if i in idx_to_id:
                            real_id = idx_to_id[i]
                            doc = docstore.get(real_id)
                            if doc and hasattr(doc, 'page_content'):
                                raw_text = doc.page_content
                                decoded_text = decode_glyph_text(raw_text).strip()
                                
                                if not decoded_text:
                                    decoded_text = raw_text[:200] # fallback
                                
                                item_code = subdir
                                if hasattr(doc, 'metadata') and doc.metadata:
                                    item_code = doc.metadata.get('item_code', subdir)
                                
                                meta_title = f"Study Material: {item_code}"
                                if target_module == "courses":
                                    meta_link = f"https://www.youtube.com/results?search_query={item_code}+course+video"
                                else:
                                    meta_link = f"https://www.google.com/search?q={item_code}+exam+question+paper"
                                
                                # Generate TRUE semantic embedding
                                emb = gatekeeper.generate_embedding(decoded_text)
                                if emb:
                                    meta = {
                                        "title": meta_title,
                                        "description": decoded_text,
                                        "source": item_code,
                                        "grade_level": "All",
                                        "subject": "General",
                                        "link": meta_link
                                    }
                                    db.add_article(target_module, emb, meta)
                                    added += 1
                                    print(f"[{target_module}] Successfully embedded {item_code}: {decoded_text[:50]}...")
            except Exception as e:
                print(f"Failed to process {subdir}: {str(e)}")
                
    if added > 0:
        db._save_module(target_module)
    print(f"Successfully rebuilt {target_module} with {added} completely new embeddings!")

if __name__ == "__main__":
    db = VectorManager()
    gatekeeper = AIGatekeeper()
    
    # Reset databases
    print("Clearing corrupted vector databases...")
    db.indices["courses"] = faiss.IndexFlatL2(db.vector_dim)
    db.metadata["courses"] = {}
    db.current_ids["courses"] = 0
    
    db.indices["competitive"] = faiss.IndexFlatL2(db.vector_dim)
    db.metadata["competitive"] = {}
    db.current_ids["competitive"] = 0
    
    rebuild_module("competitive", r"C:\Users\Sanyami Jain\Downloads\Generated faiss_index files\Generated faiss_index files\faiss_index", gatekeeper, db)
    rebuild_module("courses", r"C:\Users\Sanyami Jain\Downloads\Generated faiss_index files\Generated faiss_index files\faiss_video_index", gatekeeper, db)
