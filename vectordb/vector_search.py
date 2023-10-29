"""
This module provides the VectorSearch class for performing vector search using various algorithms.
"""

#pylint: disable = line-too-long, trailing-whitespace, trailing-newlines, line-too-long, missing-module-docstring, import-error, too-few-public-methods, too-many-instance-attributes, too-many-locals

from typing import List, Tuple
import numpy as np
import faiss
import sklearn



MRPT_LOADED = True
try:
    import mrpt
except ImportError:
    print(
        "Warning: mrpt could not be imported. Install with 'pip install git+https://github.com/vioshyvo/mrpt/'. "
        "Falling back to Faiss."
    )
    MRPT_LOADED = False


class VectorSearch:
    """
    A class to perform vector search using different methods (MRPT, Faiss, or scikit-learn).
    """

    @staticmethod
    def run_mrpt(vector, vectors, k=15, batch_results="default"):
            """
            Search for the most similar vectors using MRPT method.
            """
            index = mrpt.MRPTIndex(vectors)
            
            if isinstance(vector, (list, np.ndarray)) and len(np.shape(vector)) > 1: # If vector is a list of vectors
                res = index.exact_search(np.array(vector).astype(np.float32), k, return_distances=True)
                
                if batch_results== "flatten":
                    return get_unique_k_elements(res[0], res[1], k, diverse=False)
                elif batch_results== "diverse":
                   return get_unique_k_elements(res[0], res[1], k, diverse=True)
     
                return res[0].tolist(), res[1].tolist()
            else:
                res = index.exact_search(np.array(vector).astype(np.float32), k, return_distances=True)
                return res[0].tolist(), res[1].tolist()

    @staticmethod
    def run_faiss(vector, vectors, k=15, batch_results="default"):
        """
        Search for the most similar vectors using Faiss method.
        """
        index = faiss.IndexFlatL2(vectors.shape[1])
        index.add(vectors)
        
        if isinstance(vector, (list, np.ndarray)) and len(np.shape(vector)) > 1:  # If vector is a list of vectors
            dis, indices = index.search(np.array(vector), k)
            if batch_results== "flatten":
                return get_unique_k_elements(indices, dis, k, diverse=False)
            elif batch_results== "diverse":
               return get_unique_k_elements(indices, dis, k, diverse=True) 
            return indices, dis
        else:
            dis, indices = index.search(np.array([vector]), k)
            return indices[0], dis[0]

  
    @staticmethod
    def search_vectors(
        query_embedding: List[float], embeddings: List[List[float]], top_n: int, batch_results: str = "default"
    ) -> List[Tuple[int, float]]:
        """
        Searches for the most similar vectors to the query_embedding in the given embeddings.

        :param query_embedding: a list of floats representing the query vector.
        :param embeddings: a list of vectors to be searched, where each vector is a list of floats.
        :param top_n: the number of most similar vectors to return.
        :param batch_results: when input is a list of vectors, output can be "default", "flatten" or "diverse".
        :return: a list of indices of the top_n most similar vectors in the embeddings.
        """
        if isinstance(embeddings, list):
            embeddings = np.array(embeddings).astype(np.float32)

        if len(embeddings) < 3000 or not MRPT_LOADED:
            call_search = VectorSearch.run_faiss
        else:
            call_search = VectorSearch.run_mrpt

        indices, dis = call_search(query_embedding, embeddings, top_n, batch_results)

        return list(zip(indices, dis))
