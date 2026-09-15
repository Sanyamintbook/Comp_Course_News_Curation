import os
import glob
import subprocess
import sys

def main():
    print("==========================================")
    print("🧹 Cleaning up old duplicate databases...")
    base_dir = os.path.join(os.path.dirname(__file__), "src", "database", "indices")
    
    # We must wipe the old database because it contains the fake placeholder links!
    patterns = ["courses*", "competitive*"]
    for pattern in patterns:
        for f in glob.glob(os.path.join(base_dir, pattern)):
            try:
                os.remove(f)
                print(f" -> Deleted old file: {os.path.basename(f)}")
            except Exception as e:
                print(f"❌ Error: Could not delete {os.path.basename(f)}!")
                print("⚠️  You MUST press CTRL+C in your terminal to stop the old server first!")
                return

    print("\n🚀 Re-importing clean FAISS vectors with REAL YouTube/Google links...")
    subprocess.run([sys.executable, "src/database/importer.py"])
    
    print("\n✅ All clean! Starting the unified platform...")
    subprocess.run([sys.executable, "run.py"])

if __name__ == "__main__":
    main()
