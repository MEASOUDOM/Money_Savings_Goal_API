from sqlalchemy import Column, Integer, BigInteger, String, Date, DateTime, DECIMAL, ForeignKey, SmallInteger, func
from sqlalchemy.orm import relationship
from db import Base

class Currency(Base):
    __tablename__ = "currencies"

    id = Column(Integer, primary_key=True, autoincrement=True)
    code = Column(String(10), nullable=False, unique=True)
    symbol = Column(String(10), nullable=False)
    name = Column(String(50), nullable=False)
    is_active = Column(SmallInteger, default=1)

class Goal(Base):
    __tablename__ = "goals"

    id = Column(BigInteger, primary_key=True, autoincrement=True)
    name = Column(String(120), nullable=False)
    image_path = Column(String(255), nullable=True)
    note = Column(String(255), nullable=True)

    currency_id = Column(Integer, ForeignKey("currencies.id"), nullable=False)
    currency = relationship("Currency")

    goal_amount = Column(DECIMAL(18, 2), nullable=False, default=0)
    saved_amount = Column(DECIMAL(18, 2), nullable=False, default=0)

    target_date = Column(Date, nullable=True)

    created_at = Column(DateTime, server_default=func.now())
    updated_at = Column(DateTime, server_default=func.now(), onupdate=func.now())

class GoalTransaction(Base):
    __tablename__ = "goal_transactions"

    # type: 1=saving, 2=withdraw, 3=transfer
    id = Column(BigInteger, primary_key=True, autoincrement=True)

    goal_id = Column(BigInteger, ForeignKey("goals.id"), nullable=False)
    goal = relationship("Goal", foreign_keys=[goal_id])

    type = Column(SmallInteger, nullable=False)
    amount = Column(DECIMAL(18, 2), nullable=False)
    note = Column(String(255), nullable=True)
    txn_date = Column(DateTime, server_default=func.now())

    from_goal_id = Column(BigInteger, ForeignKey("goals.id"), nullable=True)
    to_goal_id = Column(BigInteger, ForeignKey("goals.id"), nullable=True)

    from_goal = relationship("Goal", foreign_keys=[from_goal_id])
    to_goal = relationship("Goal", foreign_keys=[to_goal_id])

class GoalAdd(Base):
    __tablename__ = "goal_add"

    # action: 1=saving, 2=withdraw, 3=transfer
    id = Column(BigInteger, primary_key=True, autoincrement=True)

    goal_id = Column(BigInteger, ForeignKey("goals.id"), nullable=False)
    goal = relationship("Goal", foreign_keys=[goal_id])

    action = Column(SmallInteger, nullable=False)
    amount = Column(DECIMAL(18, 2), nullable=False)
    note = Column(String(255), nullable=True)
    created_at = Column(DateTime, server_default=func.now())

    to_goal_id = Column(BigInteger, ForeignKey("goals.id"), nullable=True)
    to_goal = relationship("Goal", foreign_keys=[to_goal_id])
