import uuid as uuid_mod
from datetime import datetime
from enum import StrEnum

from sqlalchemy import DateTime, Enum, ForeignKey, String, func
from sqlalchemy.orm import Mapped, mapped_column, relationship

from app.database import Base, CompatUUID, CompatJSON


class TaskStatus(StrEnum):
    ASSIGNED = "assigned"
    IN_PROGRESS = "in_progress"
    COMPLETED = "completed"
    RETURNED = "returned"


class HandoverStatus(StrEnum):
    OPEN = "open"
    COMPLETED = "completed"


class PickingTask(Base):
    __tablename__ = "picking_tasks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )
    picker_user_id: Mapped[uuid_mod.UUID | None] = mapped_column(
        CompatUUID(), ForeignKey("users.id"), nullable=True
    )
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus), default=TaskStatus.ASSIGNED
    )
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    order: Mapped["Order"] = relationship("Order")  # noqa: F821


class PackingTask(Base):
    __tablename__ = "packing_tasks"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )
    packer_user_id: Mapped[uuid_mod.UUID | None] = mapped_column(
        CompatUUID(), ForeignKey("users.id"), nullable=True
    )
    status: Mapped[TaskStatus] = mapped_column(
        Enum(TaskStatus), default=TaskStatus.ASSIGNED
    )
    scan_log: Mapped[list | None] = mapped_column(CompatJSON(), default=list)
    started_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    order: Mapped["Order"] = relationship("Order")  # noqa: F821


class HandoverBatch(Base):
    __tablename__ = "handover_batches"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    courier: Mapped[str | None] = mapped_column(String(50), nullable=True)
    sender_user_id: Mapped[uuid_mod.UUID | None] = mapped_column(
        CompatUUID(), ForeignKey("users.id"), nullable=True
    )
    status: Mapped[HandoverStatus] = mapped_column(
        Enum(HandoverStatus), default=HandoverStatus.OPEN
    )
    created_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )
    completed_at: Mapped[datetime | None] = mapped_column(
        DateTime(timezone=True), nullable=True
    )

    items: Mapped[list["HandoverItem"]] = relationship(
        back_populates="batch", cascade="all, delete-orphan"
    )


class HandoverItem(Base):
    __tablename__ = "handover_items"

    id: Mapped[int] = mapped_column(primary_key=True, autoincrement=True)
    batch_id: Mapped[int] = mapped_column(
        ForeignKey("handover_batches.id", ondelete="CASCADE"), nullable=False
    )
    order_id: Mapped[int] = mapped_column(
        ForeignKey("orders.id", ondelete="CASCADE"), nullable=False
    )
    scanned_at: Mapped[datetime] = mapped_column(
        DateTime(timezone=True), server_default=func.now()
    )

    batch: Mapped["HandoverBatch"] = relationship(back_populates="items")
    order: Mapped["Order"] = relationship("Order")  # noqa: F821
