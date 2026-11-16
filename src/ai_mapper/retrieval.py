"""Candidate retrieval: TF-IDF similarity between a control and every framework requirement.

This runs fully offline. It is used two ways:
  * to shortlist candidates that the LLM then judges (keeps prompts small and stops the LLM
    inventing requirement IDs, because it may only pick from the shortlist), and
  * on its own as the 'retrieval' backend, a no-LLM baseline the evaluation compares against.
"""
from __future__ import annotations

import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity

from .catalog import expand


class Retriever:
    def __init__(self, catalog: pd.DataFrame, controls: pd.DataFrame):
        self.catalog = catalog.reset_index(drop=True)
        corpus = [expand(t) for t in list(self.catalog.text) + list(controls.text)]
        self.vec = TfidfVectorizer(ngram_range=(1, 2), sublinear_tf=True, stop_words="english", min_df=1)
        self.vec.fit(corpus)
        self.req_matrix = self.vec.transform([expand(t) for t in self.catalog.text])

    def scores(self, control_text: str) -> pd.Series:
        q = self.vec.transform([expand(control_text)])
        return pd.Series(cosine_similarity(q, self.req_matrix)[0], index=self.catalog.index)

    def candidates(self, control_text: str, per_family: int = 5) -> pd.DataFrame:
        """Top requirements per framework family, best first."""
        sims = self.scores(control_text)
        cat = self.catalog.assign(similarity=sims.round(4))
        top = (cat.sort_values("similarity", ascending=False)
                  .groupby("family", sort=False).head(per_family))
        return top.sort_values(["family", "similarity"], ascending=[True, False])

    @staticmethod
    def select(cands: pd.DataFrame, min_score: float = 0.12, relative: float = 0.75,
               max_per_family: int = 2) -> pd.DataFrame:
        """Retrieval-only decision rule: keep the best match per framework if it clears min_score,
        plus a runner up that scores within `relative` of the best."""
        picked = []
        for _, group in cands.groupby("family"):
            group = group.sort_values("similarity", ascending=False)
            best = group.similarity.iloc[0]
            if best < min_score:
                continue
            keep = group[(group.similarity >= min_score) & (group.similarity >= best * relative)]
            picked.append(keep.head(max_per_family))
        return pd.concat(picked) if picked else cands.iloc[0:0]
