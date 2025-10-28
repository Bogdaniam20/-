from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from src import database
from src.models.Task import Task as TaskModel
from src.schemas.Task import Task, TaskCreate, TaskUpdate

router = APIRouter(
    prefix="/tasks",
    tags=["Tasks"]
)

@router.post("/", response_model=Task)
def create_task(task: TaskCreate, db: Session = Depends(database.get_db)):
    db_task = TaskModel(**task.dict())
    db.add(db_task)
    db.commit()
    db.refresh(db_task)
    return db_task

@router.get("/", response_model=list[Task])
def get_tasks(
    db: Session = Depends(database.get_db),
    # Фильтры
    completed: bool | None = Query(None, description="Фильтр по статусу выполнения"),
    has_due: bool | None = Query(None, description="Есть ли установленный срок"),
    search: str | None = Query(None, description="Поиск по названию/описанию"),
    # Сортировка
    sort_by: str = Query("created", description="Поле сортировки: created|title|due|id"),
    order: str = Query("asc", description="Направление сортировки: asc|desc"),
    # Пагинация
    limit: int = Query(100, ge=1, le=500),
    offset: int = Query(0, ge=0),
):
    q = db.query(TaskModel)

    # Фильтры
    if completed is not None:
        q = q.filter(TaskModel.completed == completed)
    if has_due is not None:
        if has_due:
            q = q.filter(TaskModel.due_time != None)
        else:
            q = q.filter(TaskModel.due_time == None)
    if search:
        like = f"%{search}%"
        q = q.filter((TaskModel.title.ilike(like)) | (TaskModel.description.ilike(like)))

    # Сортировка
    sort_map = {
        "id": TaskModel.id,
        "title": TaskModel.title,
        "due": TaskModel.due_time,
        # created - у нас нет явного поля, используем id как прокси
        "created": TaskModel.id,
    }
    sort_col = sort_map.get(sort_by, TaskModel.id)
    if order.lower() == "desc":
        q = q.order_by(sort_col.desc())
    else:
        q = q.order_by(sort_col.asc())

    # Пагинация
    q = q.offset(offset).limit(limit)
    return q.all()

@router.get("/{task_id}", response_model=Task)
def get_task(task_id: int, db: Session = Depends(database.get_db)):
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    return task

@router.put("/{task_id}", response_model=Task)
def update_task(task_id: int, task_data: TaskUpdate, db: Session = Depends(database.get_db)):
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    for key, value in task_data.dict().items():
        setattr(task, key, value)
    db.commit()
    db.refresh(task)
    return task

@router.delete("/{task_id}")
def delete_task(task_id: int, db: Session = Depends(database.get_db)):
    task = db.query(TaskModel).filter(TaskModel.id == task_id).first()
    if not task:
        raise HTTPException(status_code=404, detail="Task not found")
    db.delete(task)
    db.commit()
    return {"message": "Task deleted successfully"}
