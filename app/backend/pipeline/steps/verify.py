from __future__ import annotations

from typing import List

from core.models import Citation, Claim, Verification
from indexing.vectorstore import VectorStore


def verify_claims(claims: List[Claim], store: VectorStore) -> List[Verification]:
    verifications: List[Verification] = []
    for claim in claims:
        matches = store.search(claim.text, k=5)
        if not matches:
            verifications.append(
                Verification(claim_id=claim.id, status="insufficient", confidence=0.2)
            )
            continue
        citations = [
            Citation(
                source_title=match["title"],
                source_ref=match["source"],
                snapshot_date=match.get("snapshot_date"),
                page=match.get("page"),
                excerpt=match["excerpt"],
            )
            for match in matches
        ]
        verifications.append(
            Verification(
                claim_id=claim.id,
                status="supported",
                confidence=0.6,
                citations=citations,
            )
        )
    return verifications
