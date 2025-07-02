from src.haystack_pipeline import build_pipeline

def run_query_loop(initial_prompt):
    pipeline = build_pipeline()

    result = pipeline.run(query=initial_prompt, params={"Retriever": {"top_k": 10}})
    docs = result["documents"]

    ret_tracks = []
    for doc in docs:
        ret_tracks.append(doc.meta["uri"])
    
    return ret_tracks
          