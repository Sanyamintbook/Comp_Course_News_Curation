from src.database.vector_manager import VectorManager
from src.ai_processing.gatekeeper import AIGatekeeper

print("Loading...")
gatekeeper = AIGatekeeper()
db = VectorManager()

print("Generating embedding...")
emb = gatekeeper.generate_embedding("Student in grade 6-8. Wants to be a Architect. Likes . Hobbies include Drawing, Chess.")

print("\n--- COMPETITIVE ---")
results = db.search(module="competitive", query_embedding=emb, top_k=5, max_distance=5.0)
for r in results:
    print(f"Distance: {r['distance']:.4f} | Title: {r['title'][:50]}")
    
print("\n--- COURSES ---")
results = db.search(module="courses", query_embedding=emb, top_k=5, max_distance=5.0)
for r in results:
    print(f"Distance: {r['distance']:.4f} | Title: {r['title'][:50]}")
