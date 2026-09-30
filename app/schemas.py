from typing import List, Optional
from pydantic import BaseModel, Field

class EnrichmentOutput(BaseModel):
    clean_title: str
    category: str
    brand: Optional[str] = None
    tags: List[str] = Field(default_factory=list)

class ProductInput(BaseModel):
    sku: str
    raw_title: str
    raw_description: Optional[str] = None

class ProductUpdate(BaseModel):
    clean_title: Optional[str] = None
    category: Optional[str] = None
    tags: Optional[List[str]] = None

class ProductResponse(BaseModel):
    sku: str
    raw_title: str
    raw_description: Optional[str] = None
    clean_title: Optional[str] = None
    category: Optional[str] = None
    brand: Optional[str] = None
    tags: Optional[List[str]] = None
    status: str
    error: Optional[str] = None

class JobCreateInput(BaseModel):
    products: List[ProductInput]

class JobResponse(BaseModel):
    id: str
    status: str
    total: int
    done: int
    failed: int
    cache_hits: int
    created_at: str
    started_at: Optional[str] = None
    finished_at: Optional[str] = None

class ProductListResponse(BaseModel):
    items: List[ProductResponse]
    page: int
    page_size: int
    total: int

class MetricsResponse(BaseModel):
    llm_calls_total: int
    llm_errors_total: int
    max_concurrent_llm_calls: int

class HealthResponse(BaseModel):
    status: str
    llm_provider: str
    llm_concurrency: int
# Project directory me jayein
