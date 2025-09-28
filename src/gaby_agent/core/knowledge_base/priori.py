""" 

src/knowledge_base/priori.py

Temporal module for knowledge base operations that loads prior beliefs from local storage / caches for data type detections. 
This build is more robust than passing an agent through data column. 

This module can then be extended with BigQuery AI for reducing the dimensions into latent space of smaller dimensions (PCA). 
"""

import numpy as np 
import pandas as pd
from sentence_transformers import SentenceTransformer

class Temporal(SentenceTransformer):
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        super().__init__(model_name)
        df = pd.read_csv('src/gaby_agent/data/sample/data_all_types.csv')
        self.data_type_sample = df[sorted(df.columns)]
        self.data_type_embeddings = {col: self.encode(np.array([self.data_type_sample[col].astype(str).values.tolist()])) for col in self.data_type_sample.columns}
        
    @property
    def data_type(self):
        return self.data_type_sample.columns.tolist()
    
    def detect_data_type(self, target_data_column: pd.Series) -> pd.DataFrame:
        """ Compare the similarity of a query against a data column and return a DataFrame with similarity scores. """
        
        if isinstance(target_data_column, pd.Series):
            target_data_column = np.array([target_data_column.dropna().astype(str).tolist()])
        
        print(np.array(list(self.data_type_embeddings.values())).shape)
        target_emb = self.encode(target_data_column) 
        z_sample = np.vstack(list(self.data_type_embeddings.values())) 

        print('Target Embedding Shape:', target_emb.shape, 'Sample Embedding Shape:', z_sample.shape)
        assert target_emb.shape == (len(target_data_column), 384), "Embedding shape mismatch"
        assert z_sample.shape == (len(self.data_type), 384), "Sample embedding shape mismatch"
        
        simi_scores = self.similarity_pairwise(target_emb, z_sample)
        print(simi_scores) 
        voted_index = simi_scores.argmax(axis=1)
        voted_label = self.data_type[voted_index]
        
        return {
            "data_type": voted_label,
            "similarity_score": simi_scores.max(axis=1),
            "logits": simi_scores
        }
        
if __name__ == "__main__":
    temporal = Temporal()
    print(temporal.data_type)
    short_text_sample = pd.Series([
        "alpha42",
        "deltaX",
        "mimi01",
        "orbit7",
        "kappa9",
        "datafy",
        "nexus3"
    ], name="short_text")

    pred = temporal.detect_data_type(short_text_sample)
    print(pred)