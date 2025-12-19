"""Pytest Configuration and Shared Fixtures"""
import os
import pytest
from pymongo import MongoClient
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()


@pytest.fixture(scope="session")
def mongo_uri():
    """MongoDB URI 반환 (세션 전체에서 공유)"""
    uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")
    return uri


@pytest.fixture(scope="session")
def mongo_client(mongo_uri):
    """MongoDB 클라이언트 생성 (세션 전체에서 공유)"""
    client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
    yield client
    client.close()


@pytest.fixture(scope="function")
def test_database(mongo_client):
    """테스트용 데이터베이스 (각 테스트마다 새로 생성/삭제)"""
    db_name = "test_mongodb_mcp"
    db = mongo_client[db_name]

    yield db

    # 테스트 후 데이터베이스 삭제
    mongo_client.drop_database(db_name)


@pytest.fixture(scope="function")
def test_collection(test_database):
    """테스트용 컬렉션"""
    collection_name = "test_collection"
    collection = test_database[collection_name]

    yield collection

    # 테스트 후 컬렉션 삭제
    collection.drop()
