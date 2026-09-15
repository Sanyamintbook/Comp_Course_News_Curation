"""
Module: VectorManager
Purpose: Manages FAISS vector databases and metadata for all 5 educational modules.
Logic: 
- Initializes 4 separate FAISS indices (News, Courses, Competitive, Leisure).
- Provides methods to add items to specific modules.
- Provides a unified search method to query across one or all modules simultaneously.
"""
import faiss
import numpy as np
import json
import os
from typing import List, Dict, Any
from email.utils import parsedate_to_datetime
from datetime import datetime, timezone

class VectorManager:
    def __init__(self, base_dir: str = None, vector_dim: int = 1024):
        # Default to src/database/indices relative to this file's root
        if base_dir is None:
            self.base_dir = os.path.join(os.path.dirname(__file__), "indices")
        else:
            self.base_dir = base_dir
            
        self.vector_dim = vector_dim
        self.modules = ["news", "courses", "competitive", "leisure"]
        
        self.indices = {}
        self.metadata = {}
        self.current_ids = {}
        
        os.makedirs(self.base_dir, exist_ok=True)
        for mod in self.modules:
            self._load_module(mod)
            
    def _load_module(self, module: str):
        """Loads a specific module's FAISS index and metadata."""
        idx_path = os.path.join(self.base_dir, f"{module}.faiss")
        meta_path = os.path.join(self.base_dir, f"{module}_meta.json")
        
        self.metadata[module] = {}
        self.indices[module] = None
        self.current_ids[module] = 0

        if os.path.exists(idx_path) and os.path.exists(meta_path):
            try:
                self.indices[module] = faiss.read_index(idx_path)
                with open(meta_path, 'r') as f:
                    content = f.read().strip()
                    if content:
                        self.metadata[module] = {int(k): v for k, v in json.loads(content).items()}
                self.current_ids[module] = max(self.metadata[module].keys()) + 1 if self.metadata[module] else 0
            except Exception as e:
                print(f"Error loading {module} index/meta, initializing new: {e}")
                self.indices[module] = faiss.IndexFlatL2(self.vector_dim)
                self.metadata[module] = {}
                self.current_ids[module] = 0
        else:
            self.indices[module] = faiss.IndexFlatL2(self.vector_dim)

    def _save_module(self, module: str):
        """Saves a specific module to disk."""
        idx_path = os.path.join(self.base_dir, f"{module}.faiss")
        meta_path = os.path.join(self.base_dir, f"{module}_meta.json")
        faiss.write_index(self.indices[module], idx_path)
        with open(meta_path, 'w') as f:
            json.dump(self.metadata[module], f)

    def article_exists(self, module: str, link: str) -> bool:
        """Checks if a document with the given link exists in a module."""
        for meta in self.metadata[module].values():
            if meta.get("link") == link:
                return True
        return False

    def add_article(self, module: str, embedding: List[float], meta: Dict[str, Any], auto_save: bool = True):
        """Adds a single embedded document to a specific module."""
        if module not in self.modules:
            print(f"Module {module} not found!")
            return
        vector = np.array([embedding], dtype=np.float32)
        self.indices[module].add(vector)
        self.metadata[module][self.current_ids[module]] = meta
        self.current_ids[module] += 1
        if auto_save:
            self._save_module(module)

    def search(self, module: str, query_embedding: List[float], top_k: int = 5, filters: Dict[str, str] = None, max_distance: float = 1.2, today_only: bool = False) -> List[Dict[str, Any]]:
        """Searches a specific module for similar vectors."""
        if module not in self.modules or self.indices[module].ntotal == 0:
            return []
            
        vector = np.array([query_embedding], dtype=np.float32)
        fetch_k = min(top_k * 5, self.indices[module].ntotal)
        distances, indices = self.indices[module].search(vector, fetch_k)
        
        results = []
        for i in range(len(indices[0])):
            idx = int(indices[0][i])
            if idx == -1: continue
            dist = float(distances[0][i])
            if max_distance is not None and dist > max_distance: continue
            
            meta = self.metadata[module][idx]
            
            # Today Only Filter (primarily for News)
            if today_only:
                pub_date = meta.get('published')
                is_today = False
                if pub_date and pub_date != 'Unknown date':
                    try:
                        dt = parsedate_to_datetime(pub_date)
                        if dt.tzinfo is None: dt = dt.replace(tzinfo=timezone.utc)
                        today_midnight = datetime.now(timezone.utc).replace(hour=0, minute=0, second=0, microsecond=0)
                        if dt >= today_midnight: is_today = True
                    except Exception: pass
                if not is_today: continue
            
            # Apply hard filters
            if filters:
                match = True
                for key, val in filters.items():
                    meta_val = str(meta.get(key, "General")).lower()
                    if isinstance(val, list):
                        allowed = [str(v).lower() for v in val] + ["general"]
                        if meta_val not in allowed:
                            match = False; break
                    else:
                        if meta_val != str(val).lower() and meta_val != "general":
                            match = False; break
                if not match: continue
            
            results.append({"id": idx, "distance": dist, "module": module, **meta})
            
        # Optional sorting by date if it exists
        def get_date(item):
            pub_date = item.get('published')
            if pub_date and pub_date != 'Unknown date':
                try:
                    dt = parsedate_to_datetime(pub_date)
                    if dt.tzinfo is None: dt = dt.replace(tzinfo=timezone.utc)
                    return dt
                except Exception: pass
            return datetime.min.replace(tzinfo=timezone.utc)

        results.sort(key=get_date, reverse=True)
        return results[:top_k]
