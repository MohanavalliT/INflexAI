from sentence_transformers import SentenceTransformer, util
import pandas as pd

model = SentenceTransformer('all-MiniLM-L6-v2')

def match_jobs(resume_text, jobs_df, top_n=3):
    resume_embedding = model.encode(resume_text, convert_to_tensor=True)
    jobs_df["similarity"] = jobs_df["description"].apply(
        lambda x: util.cos_sim(resume_embedding, model.encode(x, convert_to_tensor=True)).item()
    )
    return jobs_df.sort_values(by="similarity", ascending=False).head(top_n)
