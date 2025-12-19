# MongoDB MCP Server 설계 문서

## 개요

이 프로젝트는 MCP(Model Context Protocol)를 통해 LLM이 MongoDB 데이터베이스에 접근할 수 있도록 하는 서버입니다.

## 기술 스택

- **FastMCP**: MCP 서버 프레임워크
- **pymongo**: MongoDB Python 드라이버
- **uv**: Python 패키지 관리자

## 아키텍처

```
┌─────────────┐     MCP      ┌─────────────┐    pymongo    ┌─────────────┐
│   Claude    │ ◄──────────► │  MCP Server │ ◄───────────► │   MongoDB   │
│   (LLM)     │   (stdio)    │  (FastMCP)  │               │   Server    │
└─────────────┘              └─────────────┘               └─────────────┘
```

## Tool 설계

### 설계 원칙

1. **읽기 중심**: 데이터 조회/분석에 초점, 수정/삭제는 제외 (안전성)
2. **단순한 인터페이스**: 필수 파라미터 최소화
3. **유연한 쿼리**: aggregate로 복잡한 쿼리 지원

### Tool 목록

| Tool | 용도 | 위험도 |
|------|------|--------|
| `list_databases` | DB 탐색 | 낮음 |
| `list_collections` | 컬렉션 탐색 | 낮음 |
| `find_documents` | 일반 조회 | 낮음 |
| `find_one` | 단일 문서 조회 | 낮음 |
| `insert_document` | 문서 생성 | 중간 |
| `count_documents` | 개수 확인 | 낮음 |
| `aggregate` | 복잡한 쿼리/집계 | 낮음 |
| `distinct` | 고유값 조회 | 낮음 |

### 제외된 기능 (의도적)

- `update_documents`: 데이터 변경 위험
- `delete_documents`: 데이터 손실 위험
- `drop_collection`: 구조 파괴 위험
- `create_index`: 관리자 기능

## 구현 상세

### 연결 관리

```python
def get_client() -> MongoClient:
    return MongoClient(MONGO_URI)
```

- 각 요청마다 새 연결 생성
- `with` 문으로 자동 연결 해제
- 환경변수 `MONGO_URI`로 연결 문자열 설정

### 직렬화 처리

MongoDB의 `ObjectId`는 JSON 직렬화 불가하므로 문자열로 변환:

```python
def serialize(doc):
    if hasattr(doc, '__str__') and type(doc).__name__ == 'ObjectId':
        return str(doc)
    # ...
```

### aggregate 활용

복잡한 쿼리는 `aggregate` 파이프라인으로 처리:

```python
# 예: 카테고리별 집계
pipeline = [
    {"$match": {"status": "active"}},
    {"$group": {"_id": "$category", "count": {"$sum": 1}}},
    {"$sort": {"count": -1}}
]
```

지원되는 스테이지:
- `$match`: 필터링
- `$group`: 그룹화/집계
- `$sort`: 정렬
- `$limit`, `$skip`: 페이징
- `$project`: 필드 선택
- `$lookup`: 조인
- `$unwind`: 배열 펼치기

## 보안 고려사항

1. **읽기 전용 권장**: 프로덕션에서는 읽기 전용 MongoDB 계정 사용
2. **환경변수**: 연결 문자열을 코드에 하드코딩하지 않음
3. **제한된 기능**: 삭제/수정 기능 미포함

## 향후 확장 가능성

- [ ] 연결 풀링 (고성능 환경)
- [ ] 스키마 조회 tool 추가
- [ ] 인덱스 정보 조회
- [ ] 쿼리 실행 계획 분석
- [ ] update/delete 옵션 추가 (플래그로 활성화)