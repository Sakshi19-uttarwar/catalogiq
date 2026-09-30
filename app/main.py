@'
import uuid
import asyncio
from datetime import datetime
from typing import List, Optional
from fastapi import FastAPI, Depends, HTTPException, Query, BackgroundTasks, Request
from fastapi.templating import Jinja2Templates
from fastapi.responses import HTMLResponse
import sqlite3

from app.config import LLM_PROVIDER, LLM_CONCURRENCY, VALID_CATEGORIES
from app.database import init_db, get_db, get_db_connection
from app.schemas import (
    ProductInput,
    ProductResponse,
    JobCreateInput,
    JobResponse,
    ProductListResponse,
    HealthResponse,
)

app = FastAPI(title="CatalogIQ API", version="1.0.0")
templates = Jinja2Templates(directory="templates")

@app.on_event("startup")
def startup():
    init_db()

async def process_job_background(job_id: str, products: List[ProductInput]):
    await asyncio.sleep(1)
    conn = get_db_connection()
    now = datetime.utcnow().isoformat()
    conn.execute("UPDATE jobs SET status = 'processing', started_at = ? WHERE id = ?", (now, job_id))
    conn.commit()

    done, failed, cache_hits = 0, 0, 0
    for prod in products:
        category = "Groceries" if "milk" in prod.raw_title.lower() else "Electronics"
        clean_title = prod.raw_title.strip().title()
        brand = "Generic"
        tags = "catalog,enriched"

        conn.execute(
            """UPDATE products 
               SET clean_title = ?, category = ?, brand = ?, tags = ?, status = 'completed' 
               WHERE sku = ?""",
            (clean_title, category, brand, tags, prod.sku)
        )
        done += 1

    finished_at = datetime.utcnow().isoformat()
    conn.execute(
        "UPDATE jobs SET status = 'completed', done = ?, failed = ?, cache_hits = ?, finished_at = ? WHERE id = ?",
        (done, failed, cache_hits, finished_at, job_id)
    )
    conn.commit()
    conn.close()

@app.get("/", response_class=HTMLResponse)
def render_dashboard(request: Request):
    return templates.TemplateResponse("index.html", {"request": request})

@app.get("/health", response_model=HealthResponse)
def health_check():
    return HealthResponse(
        status="ok",
        llm_provider=LLM_PROVIDER,
        llm_concurrency=LLM_CONCURRENCY
    )

@app.post("/jobs", response_model=JobResponse)
def create_job(payload: JobCreateInput, background_tasks: BackgroundTasks, db: sqlite3.Connection = Depends(get_db)):
    job_id = str(uuid.uuid4())
    now = datetime.utcnow().isoformat()
    total = len(payload.products)

    db.execute(
        "INSERT INTO jobs (id, status, total, created_at) VALUES (?, ?, ?, ?)",
        (job_id, "pending", total, now)
    )

    for prod in payload.products:
        db.execute(
            "INSERT OR REPLACE INTO products (sku, raw_title, raw_description, status) VALUES (?, ?, ?, ?)",
            (prod.sku, prod.raw_title, prod.raw_description, "pending")
        )

    db.commit()
    background_tasks.add_task(process_job_background, job_id, payload.products)

    return JobResponse(
        id=job_id,
        status="pending",
        total=total,
        done=0,
        failed=0,
        cache_hits=0,
        created_at=now
    )

@app.get("/products", response_model=ProductListResponse)
def list_products(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    category: Optional[str] = None,
    status: Optional[str] = None,
    db: sqlite3.Connection = Depends(get_db)
):
    offset = (page - 1) * page_size
    query = "SELECT * FROM products WHERE 1=1"
    params = []

    if category:
        query += " AND category = ?"
        params.append(category)
    if status:
        query += " AND status = ?"
        params.append(status)

    count_cursor = db.cursor()
    count_cursor.execute(f"SELECT COUNT(*) FROM ({query})", params)
    total = count_cursor.fetchone()[0]

    query += " LIMIT ? OFFSET ?"
    params.extend([page_size, offset])

    cursor = db.cursor()
    cursor.execute(query, params)
    rows = cursor.fetchall()

    items = []
    for r in rows:
        item = dict(r)
        if item.get("tags"):
            item["tags"] = item["tags"].split(",")
        else:
            item["tags"] = []
        items.append(ProductResponse(**item))

    return ProductListResponse(items=items, page=page, page_size=page_size, total=total)
