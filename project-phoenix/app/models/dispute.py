from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, ForeignKey, String, Text, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, CompatUUID


class DisputeType(StrEnum):
    REFUND = "refund"
    REPLACEMENT = "replacement"


class DisputeStatus(StrEnum):
    OPEN = "open"
    UNDER_REVIEW = "under_review"
    RESOLVED = "resolved"
    REJECTED = "rejected"
    CLOSED = "closed"


class DisputeReason(StrEnum):
    DEFECTIVE = "defective"
    WRONG_ITEM = "wrong_item"
    MISSING_ITEM = "missing_item"
    DAMAGED_IN_TRANSIT = "damaged_in_transit"
    NOT_AS_DESCRIBED = "not_as_described"
    OTHER = "other"


class ResolutionType(StrEnum):
    REFUND = "refund"
    REPLACEMENT = "replacement"
    REJECTED = "rejected"


class Dispute(Base):
    __tablename__ = "disputes"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )
    user_id: Mapped[str] = mapped_column(
        CompatUUID(), ForeignKey("users.id", ondelete="CASCADE"), nullable=False
    )
    type: Mapped[DisputeType] = mapped_column(String(20), nullable=False)
    reason: Mapped[DisputeReason] = mapped_column(String(30), nullable=False)
    description: Mapped[str] = mapped_column(Text, nullable=False)
    status: Mapped[DisputeStatus] = mapped_column(
        String(20), default=DisputeStatus.OPEN
    )
    resolution_type: Mapped[str | None] = mapped_column(String(20), nullable=True)
    resolution_notes: Mapped[str | None] = mapped_column(Text, nullable=True)
    admin_notes: Mapped[str | None] = mapped_column(Text, nullable=True)

    opened_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    responded_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    resolved_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    sla_deadline: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    # Relationships
    order: Mapped["Order"] = relationship("Order")  # noqa: F821
    evidence: Mapped[list["DisputeEvidence"]] = relationship(
        back_populates="dispute", cascade="all, delete-orphan"
    )


class DisputeEvidence(Base):
    __tablename__ = "dispute_evidence"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    dispute_id: Mapped[int] = mapped_column(
        ForeignKey("disputes.id", ondelete="CASCADE"), nullable=False
    )
    file_url: Mapped[str] = mapped_column(String(500), nullable=False)
    description: Mapped[str | None] = mapped_column(Text, nullable=True)
    uploaded_by: Mapped[str] = mapped_column(
        CompatUUID(), ForeignKey("users.id"), nullable=False
    )
    uploaded_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    dispute: Mapped["Dispute"] = relationship(back_populates="evidence")
