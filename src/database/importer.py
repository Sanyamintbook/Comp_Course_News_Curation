"""
Module: FAISS Importer
Purpose: Imports pre-computed external FAISS indices (e.g. from Langchain) into our unified VectorManager.
Logic: Reads the `.faiss` index and its `.pkl` metadata, extracts the documents, and appends them to our unified module databases.
"""
import faiss
import pickle
import os
import sys

# Add project root to path
sys.path.append(os.path.abspath(os.path.join(os.path.dirname(__file__), '../..')))

from src.database.vector_manager import VectorManager

def import_external_faiss(target_module: str, external_dir: str):
    """
    Imports all subdirectories of external_dir containing index.faiss and index.pkl 
    into the target_module of our VectorManager.
    """
    db = VectorManager()
    
    if not os.path.exists(external_dir):
        print(f"Error: Directory {external_dir} does not exist.")
        return

    added = 0
    for subdir in os.listdir(external_dir):
        subdir_path = os.path.join(external_dir, subdir)
        if not os.path.isdir(subdir_path):
            continue
            
        faiss_path = os.path.join(subdir_path, 'index.faiss')
        pkl_path = os.path.join(subdir_path, 'index.pkl')
        
        if os.path.exists(faiss_path) and os.path.exists(pkl_path):
            print(f"Importing {subdir_path} into {target_module}...")
            try:
                # Load external index
                ext_index = faiss.read_index(faiss_path)
                
                # Load external metadata
                with open(pkl_path, 'rb') as f:
                    pkl_data = pickle.load(f)
                    
                docstore = None
                if isinstance(pkl_data, tuple) and len(pkl_data) > 0:
                    docstore_obj = pkl_data[0]
                    if hasattr(docstore_obj, '_dict'):
                        docstore = docstore_obj._dict
                elif isinstance(pkl_data, dict):
                    docstore = pkl_data
                    
                if ext_index.ntotal > 0:
                    if ext_index.d == db.vector_dim:
                        for i in range(ext_index.ntotal):
                            vec = ext_index.reconstruct(i)
                            
                            item_code = subdir
                            meta_title = f"Study Material: {item_code}"
                            if target_module == "courses":
                                meta_link = f"https://www.youtube.com/results?search_query={item_code}+course+video"
                            else:
                                meta_link = f"https://www.google.com/search?q={item_code}+exam+question+paper"
                                
                            try:
                                if docstore and isinstance(pkl_data, tuple) and len(pkl_data) > 1:
                                    idx_to_id = pkl_data[1]
                                    if i in idx_to_id:
                                        real_id = idx_to_id[i]
                                        doc = docstore.get(real_id)
                                        if doc and hasattr(doc, 'metadata'):
                                            real_code = doc.metadata.get('item_code')
                                            if real_code:
                                                item_code = real_code
                                                meta_title = f"Study Material: {item_code}"
                                                if target_module == "courses":
                                                    meta_link = f"https://www.youtube.com/results?search_query={item_code}+course+video"
                                                else:
                                                    meta_link = f"https://www.google.com/search?q={item_code}+exam+question+paper"
                            except Exception:
                                pass
                            
                            meta = {
                                "title": meta_title, 
                                "source": subdir,
                                "grade_level": "All",
                                "subject": "General",
                                "link": meta_link
                            }
                            
                            db.add_article(target_module, vec.tolist(), meta, auto_save=False)
                            added += 1
                    else:
                        print(f"Dimension mismatch: expected {db.vector_dim}, got {ext_index.d}")
            except Exception as e:
                print(f"Failed to import {subdir}: {str(e)}")
                
    if added > 0:
        db._save_module(target_module)
    print(f"Successfully imported {added} vectors into {target_module}!")

if __name__ == "__main__":
    import_external_faiss("competitive", r"C:\Users\Sanyami Jain\Downloads\Generated faiss_index files\Generated faiss_index files\faiss_index")
    import_external_faiss("courses", r"C:\Users\Sanyami Jain\Downloads\Generated faiss_index files\Generated faiss_index files\faiss_video_index")
