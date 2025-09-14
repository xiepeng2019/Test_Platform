from sqlalchemy import Integer, String, DateTime
from sqlalchemy.orm import Mapped, mapped_column
from sqlalchemy.sql import func

from app.core.orm import Base


class TestCaseNode(Base):
    """Represents a node in a hierarchical structure of test cases."""
    __tablename__ = "testcases_node"

    id: Mapped[int] = mapped_column(Integer, primary_key=True, index=True, doc="The unique identifier for the test case node.")
    name: Mapped[str] = mapped_column(String(100), doc="The name of the test case node.")
    project_id: Mapped[int] = mapped_column(Integer, doc="The ID of the project this node belongs to.")
    parent_id: Mapped[int | None] = mapped_column(Integer, doc="The ID of the parent node, forming a hierarchy. Null for root nodes.", nullable=True)
    creater: Mapped[str] = mapped_column(String(100), doc="The user who created this test case node.")
    comment: Mapped[str | None] = mapped_column(String(500), doc="Optional comments or notes about the node.", nullable=True)
    created_at: Mapped[DateTime] = mapped_column(DateTime, server_default=func.now(), doc="Timestamp of when the node was created.")
    updated_at: Mapped[DateTime] = mapped_column(
        DateTime, server_default=func.now(), onupdate=func.now(), doc="Timestamp of the last update to the node."
    )
