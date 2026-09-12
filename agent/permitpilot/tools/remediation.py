from __future__ import annotations

from copy import deepcopy

from strands import tool


@tool
def apply_approved_remediation(
    documents: list[dict],
    approved_updates: list[dict],
) -> dict:
    """Apply only explicitly approved document remediation updates.

    Args:
        documents: Current project document inventory.
        approved_updates: Human-approved document state changes.
    """

    updated_documents = deepcopy(documents)
    document_map = {
        item["document_type"]: item
        for item in updated_documents
    }

    applied_updates: list[dict] = []
    rejected_updates: list[dict] = []

    for update in approved_updates:
        document_type = update.get("document_type")
        approved = update.get("approved", False)

        if not approved:
            rejected_updates.append(
                {
                    "document_type": document_type,
                    "reason": "Update was not explicitly approved.",
                }
            )
            continue

        document = document_map.get(document_type)

        if document is None:
            rejected_updates.append(
                {
                    "document_type": document_type,
                    "reason": "Document type does not exist in inventory.",
                }
            )
            continue

        previous_state = {
            "present": document.get("present"),
            "status": document.get("status"),
        }

        if "present" in update:
            document["present"] = bool(update["present"])

        if "status" in update:
            document["status"] = update["status"]

        applied_updates.append(
            {
                "document_type": document_type,
                "document_name": document.get("name"),
                "previous_state": previous_state,
                "new_state": {
                    "present": document.get("present"),
                    "status": document.get("status"),
                },
            }
        )

    return {
        "documents": updated_documents,
        "applied_updates": applied_updates,
        "rejected_updates": rejected_updates,
        "applied_count": len(applied_updates),
        "rejected_count": len(rejected_updates),
    }
