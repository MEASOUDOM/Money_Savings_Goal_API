from fastapi import FastAPI, Depends, HTTPException
from sqlalchemy.orm import Session
from decimal import Decimal

from db import engine, get_db
from models import Currency, Goal, GoalTransaction, GoalAdd
from db import Base
import schemas
import uvicorn

app = FastAPI(title="Saving Goal API (FastAPI)")

# Create tables automatically (for dev)
Base.metadata.create_all(bind=engine)

SAVING = 1
WITHDRAW = 2
TRANSFER = 3

# ---------- Helpers ----------
def get_goal_or_404(db: Session, goal_id: int) -> Goal:
    g = db.query(Goal).filter(Goal.id == goal_id).first()
    if not g:
        raise HTTPException(status_code=404, detail=f"Goal not found: {goal_id}")
    return g

def to_decimal(x) -> Decimal:
    # SQLAlchemy returns Decimal already, but safe convert
    return Decimal(str(x))

# ---------- Currency ----------
@app.get("/api/currencies", response_model=list[schemas.CurrencyOut])
def list_currencies(db: Session = Depends(get_db)):
    return db.query(Currency).order_by(Currency.code.asc()).all()

# ---------- Goals ----------
@app.get("/api/goals", response_model=list[schemas.GoalOut])
def list_goals(db: Session = Depends(get_db)):
    return db.query(Goal).order_by(Goal.id.desc()).all()

@app.post("/api/goals", response_model=schemas.GoalOut)
def create_goal(payload: schemas.GoalCreate, db: Session = Depends(get_db)):
    cur = db.query(Currency).filter(Currency.id == payload.currency_id).first()
    if not cur:
        raise HTTPException(status_code=400, detail="Invalid currency_id")

    g = Goal(
        name=payload.name,
        currency_id=payload.currency_id,
        goal_amount=payload.goal_amount,
        saved_amount=Decimal("0.00"),
        note=payload.note,
        image_path=payload.image_path,
        target_date=payload.target_date
    )
    db.add(g)
    db.commit()
    db.refresh(g)
    return g

@app.get("/api/goals/{goal_id}", response_model=schemas.GoalOut)
def get_goal(goal_id: int, db: Session = Depends(get_db)):
    return get_goal_or_404(db, goal_id)


def _update_goal(goal_id: int, payload: schemas.GoalCreate, db: Session) -> Goal:
    goal = get_goal_or_404(db, goal_id)

    cur = db.query(Currency).filter(Currency.id == payload.currency_id).first()
    if not cur:
        raise HTTPException(status_code=400, detail="Invalid currency_id")

    goal.name = payload.name
    goal.currency_id = payload.currency_id
    goal.goal_amount = payload.goal_amount
    goal.note = payload.note
    goal.image_path = payload.image_path
    goal.target_date = payload.target_date

    db.commit()
    db.refresh(goal)
    return goal


@app.put("/api/goals/{goal_id}", response_model=schemas.GoalOut)
def update_goal_put(
    goal_id: int, payload: schemas.GoalCreate, db: Session = Depends(get_db)
):
    return _update_goal(goal_id, payload, db)


@app.patch("/api/goals/{goal_id}", response_model=schemas.GoalOut)
def update_goal_patch(
    goal_id: int, payload: schemas.GoalCreate, db: Session = Depends(get_db)
):
    return _update_goal(goal_id, payload, db)

# ---------- Transactions (Records) ----------
@app.get("/api/goals/{goal_id}/transactions", response_model=list[schemas.TransactionOut])
def list_transactions(goal_id: int, db: Session = Depends(get_db)):
    get_goal_or_404(db, goal_id)
    return (
        db.query(GoalTransaction)
        .filter(GoalTransaction.goal_id == goal_id)
        .order_by(GoalTransaction.txn_date.desc(), GoalTransaction.id.desc())
        .all()
    )

# ---------- Add Saving ----------
@app.post("/api/goals/{goal_id}/saving", response_model=schemas.TransactionOut)
def add_saving(goal_id: int, payload: schemas.MoneyRequest, db: Session = Depends(get_db)):
    goal = get_goal_or_404(db, goal_id)

    # 1) log in goal_add
    add = GoalAdd(goal_id=goal_id, action=SAVING, amount=payload.amount, note=payload.note)
    db.add(add)

    # 2) insert transaction
    txn = GoalTransaction(goal_id=goal_id, type=SAVING, amount=payload.amount, note=payload.note)
    db.add(txn)

    # 3) update saved_amount
    goal.saved_amount = to_decimal(goal.saved_amount) + payload.amount

    db.commit()
    db.refresh(txn)
    return txn

# ---------- Withdraw ----------
@app.post("/api/goals/{goal_id}/withdraw", response_model=schemas.TransactionOut)
def add_withdraw(goal_id: int, payload: schemas.MoneyRequest, db: Session = Depends(get_db)):
    goal = get_goal_or_404(db, goal_id)

    if to_decimal(goal.saved_amount) < payload.amount:
        raise HTTPException(status_code=400, detail="Not enough saved amount to withdraw")

    add = GoalAdd(goal_id=goal_id, action=WITHDRAW, amount=payload.amount, note=payload.note)
    db.add(add)

    txn = GoalTransaction(goal_id=goal_id, type=WITHDRAW, amount=payload.amount, note=payload.note)
    db.add(txn)

    goal.saved_amount = to_decimal(goal.saved_amount) - payload.amount

    db.commit()
    db.refresh(txn)
    return txn

# ---------- Transfer ----------
@app.post("/api/transfer", response_model=schemas.TransactionOut)
def transfer(payload: schemas.TransferRequest, db: Session = Depends(get_db)):
    if payload.from_goal_id == payload.to_goal_id:
        raise HTTPException(status_code=400, detail="from_goal_id and to_goal_id cannot be the same")

    from_goal = get_goal_or_404(db, payload.from_goal_id)
    to_goal = get_goal_or_404(db, payload.to_goal_id)

    if to_decimal(from_goal.saved_amount) < payload.amount:
        raise HTTPException(status_code=400, detail="Not enough saved amount to transfer")

    # log in goal_add (from goal)
    add = GoalAdd(
        goal_id=payload.from_goal_id,
        action=TRANSFER,
        amount=payload.amount,
        note=payload.note,
        to_goal_id=payload.to_goal_id
    )
    db.add(add)

    # single transaction row (type=transfer)
    txn = GoalTransaction(
        goal_id=payload.from_goal_id,
        type=TRANSFER,
        amount=payload.amount,
        note=payload.note,
        from_goal_id=payload.from_goal_id,
        to_goal_id=payload.to_goal_id
    )
    db.add(txn)

    # update balances
    from_goal.saved_amount = to_decimal(from_goal.saved_amount) - payload.amount
    to_goal.saved_amount = to_decimal(to_goal.saved_amount) + payload.amount

    db.commit()
    db.refresh(txn)
    return txn

# ---------- Health ----------
@app.get("/api/health", response_model=schemas.SimpleMsg)
def health():
    return {"message": "OK"}

if __name__ == "__main__":
    # Bind to all interfaces so the API is reachable from other devices on the LAN.
    uvicorn.run(app, host="0.0.0.0", port=8000, reload=True)
