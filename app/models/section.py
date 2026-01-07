from dataclasses import dataclass


@dataclass
class Section:
    """
    A cleaned, logical section of content.
    This is the unit used for question generation.
    """
    section_id: str
    title: str
    content: str
