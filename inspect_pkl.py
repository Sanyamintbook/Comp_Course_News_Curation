import pickle

def inspect(path):
    with open(path, 'rb') as f:
        data = pickle.load(f)
        
    docstore = data[0]
    index_to_docstore_id = data[1]
    
    first_id = index_to_docstore_id[0]
    doc = docstore._dict[first_id]
    
    print("Page Content Snippet:", doc.page_content[:100])
    print("Metadata:", doc.metadata)

if __name__ == "__main__":
    inspect(r"C:\Users\Sanyami Jain\Downloads\Generated faiss_index files\Generated faiss_index files\faiss_index\LAX375\index.pkl")
