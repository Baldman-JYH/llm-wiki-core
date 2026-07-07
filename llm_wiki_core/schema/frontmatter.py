from __future__ import annotations


def build_frontmatter(
    page_type: str,
    title: str,
    created: str,
    updated: str,
    status: str = "seed",
) -> str:
    return (
        "---\n"
        f"type: {page_type}\n"
        f'title: "{title}"\n'
        f"created: {created}\n"
        f"updated: {updated}\n"
        f"status: {status}\n"
        "---\n\n"
    )
