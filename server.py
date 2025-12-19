from fastmcp import FastMCP
from pymongo import MongoClient
from typing import Any
import json
import os

# MongoDB 연결 설정
MONGO_URI = os.getenv("MONGO_URI", "mongodb://localhost:27017")

mcp = FastMCP("MongoDB MCP Server")

def get_client() -> MongoClient:
    return MongoClient(MONGO_URI)

def serialize(doc: Any) -> Any:
    """MongoDB 문서를 JSON 직렬화 가능하게 변환"""
    if doc is None:
        return None
    if isinstance(doc, list):
        return [serialize(d) for d in doc]
    if isinstance(doc, dict):
        return {k: serialize(v) for k, v in doc.items()}
    if hasattr(doc, '__str__') and type(doc).__name__ == 'ObjectId':
        return str(doc)
    return doc


@mcp.tool()
def list_databases() -> list[str]:
    """MongoDB 서버의 모든 데이터베이스 목록을 반환합니다."""
    with get_client() as client:
        return client.list_database_names()


@mcp.tool()
def list_collections(database: str) -> list[str]:
    """지정한 데이터베이스의 모든 컬렉션 목록을 반환합니다."""
    with get_client() as client:
        db = client[database]
        return db.list_collection_names()


@mcp.tool()
def find_documents(
    database: str,
    collection: str,
    filter: dict | None = None,
    sort: dict | None = None,
    limit: int = 10,
    skip: int = 0
) -> list[dict]:
    """
    컬렉션에서 문서를 조회합니다.
    
    Args:
        database: 데이터베이스 이름
        collection: 컬렉션 이름
        filter: 검색 조건 (예: {"name": "john"})
        sort: 정렬 조건 (예: {"created_at": -1})
        limit: 반환할 최대 문서 수
        skip: 건너뛸 문서 수
    """
    with get_client() as client:
        coll = client[database][collection]
        cursor = coll.find(filter or {})
        
        if sort:
            cursor = cursor.sort(list(sort.items()))
        if skip:
            cursor = cursor.skip(skip)
        if limit:
            cursor = cursor.limit(limit)
        
        return serialize(list(cursor))


@mcp.tool()
def find_one(
    database: str,
    collection: str,
    filter: dict | None = None
) -> dict | None:
    """
    컬렉션에서 단일 문서를 조회합니다.
    
    Args:
        database: 데이터베이스 이름
        collection: 컬렉션 이름
        filter: 검색 조건
    """
    with get_client() as client:
        coll = client[database][collection]
        doc = coll.find_one(filter or {})
        return serialize(doc)


@mcp.tool()
def insert_document(
    database: str,
    collection: str,
    document: dict
) -> str:
    """
    컬렉션에 새 문서를 삽입합니다.
    
    Args:
        database: 데이터베이스 이름
        collection: 컬렉션 이름
        document: 삽입할 문서
    
    Returns:
        삽입된 문서의 ID
    """
    with get_client() as client:
        coll = client[database][collection]
        result = coll.insert_one(document)
        return str(result.inserted_id)


@mcp.tool()
def count_documents(
    database: str,
    collection: str,
    filter: dict | None = None
) -> int:
    """
    조건에 맞는 문서 개수를 반환합니다.
    
    Args:
        database: 데이터베이스 이름
        collection: 컬렉션 이름
        filter: 검색 조건
    """
    with get_client() as client:
        coll = client[database][collection]
        return coll.count_documents(filter or {})


@mcp.tool()
def aggregate(
    database: str,
    collection: str,
    pipeline: list[dict]
) -> list[dict]:
    """
    집계 파이프라인을 실행합니다.
    
    Args:
        database: 데이터베이스 이름
        collection: 컬렉션 이름
        pipeline: 집계 파이프라인 스테이지 목록
                  예: [{"$match": {"status": "active"}}, {"$group": {"_id": "$category", "count": {"$sum": 1}}}]
    """
    with get_client() as client:
        coll = client[database][collection]
        result = list(coll.aggregate(pipeline))
        return serialize(result)


@mcp.tool()
def distinct(
    database: str,
    collection: str,
    field: str,
    filter: dict | None = None
) -> list:
    """
    특정 필드의 고유값 목록을 반환합니다.
    
    Args:
        database: 데이터베이스 이름
        collection: 컬렉션 이름
        field: 고유값을 추출할 필드명
        filter: 검색 조건
    """
    with get_client() as client:
        coll = client[database][collection]
        return coll.distinct(field, filter or {})


if __name__ == "__main__":
    mcp.run()