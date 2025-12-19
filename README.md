# MongoDB MCP Server

FastMCP 기반 MongoDB MCP(Model Context Protocol) 서버입니다.  
Claude 등 LLM에서 MongoDB 데이터를 직접 조회하고 분석할 수 있습니다.

## 기능

| Tool | 설명 |
|------|------|
| `list_databases` | 데이터베이스 목록 조회 |
| `list_collections` | 컬렉션 목록 조회 |
| `find_documents` | 문서 조회 (필터, 정렬, 페이징) |
| `find_one` | 단일 문서 조회 |
| `insert_document` | 문서 삽입 |
| `count_documents` | 문서 개수 조회 |
| `aggregate` | 집계 파이프라인 실행 |
| `distinct` | 필드 고유값 조회 |

## 설치

```bash
git clone https://github.com/rikeey98/mcp-server-mongodb-mcp-server.git
cd mcp-server-mongodb-mcp-server
uv sync
```

## 설정

### 환경변수 설정

1. `.env.example` 파일을 `.env`로 복사:
```bash
cp .env.example .env
```

2. `.env` 파일을 편집하여 MongoDB 연결 정보 입력:
```bash
# .env 파일
MONGO_URI=mongodb://localhost:27017

# 인증이 필요한 경우
# MONGO_URI=mongodb://username:password@host:27017

# MongoDB Atlas 사용 시
# MONGO_URI=mongodb+srv://username:password@cluster.mongodb.net/

# 다른 IP 주소 사용 시
# MONGO_URI=mongodb://192.168.1.100:27017
```

또는 환경변수로 직접 설정:
```bash
export MONGO_URI="mongodb://localhost:27017"
```

## 실행

### 1. 개발/테스트 (fastmcp dev 모드)
```bash
uv run fastmcp dev server.py
```
이 명령으로 MCP Inspector가 열리며 브라우저에서 테스트할 수 있습니다.

### 2. Roo Code (VS Code)에서 사용

이 프로젝트에는 `.roo/mcp.json` 파일이 이미 구성되어 있습니다.

**사용 방법:**
1. VS Code에서 Roo Code extension 설치
2. 이 프로젝트 폴더를 VS Code로 열기
3. `.env` 파일을 생성하고 MongoDB URI 설정:
   ```bash
   cp .env.example .env
   # .env 파일 편집
   ```
4. Roo Code를 시작하면 자동으로 MongoDB MCP 서버가 로드됩니다
5. Roo Code에서 "MongoDB에 연결된 데이터베이스 목록 보여줘" 같은 명령 사용 가능

**`.roo/mcp.json` 설정 예시:**
```json
{
  "mcpServers": {
    "mongodb": {
      "command": "uv",
      "args": [
        "--directory",
        "/home/user/mongodb-mcp-server",
        "run",
        "python",
        "server.py"
      ],
      "env": {
        "MONGO_URI": "mongodb://localhost:27017"
      }
    }
  }
}
```

**주의사항:**
- `--directory` 경로를 프로젝트의 실제 경로로 수정하세요
- 또는 `.env` 파일을 사용하면 `env` 섹션을 제거해도 됩니다

### 3. Claude Desktop 연결
```bash
uv run fastmcp install server.py
```

### 4. 직접 실행
```bash
uv run python server.py
```

## 사용 예시

### 기본 조회
```
"users 데이터베이스의 accounts 컬렉션에서 문서 10개 조회해줘"
```

### 필터링
```
"status가 active인 문서만 조회해줘"
```

### 집계 파이프라인
```
"category별로 문서 개수를 집계해줘"
```

## 테스트

### 개발 의존성 설치
```bash
uv sync --dev
```

### MongoDB 연결 테스트 실행

**pytest로 실행:**
```bash
# 모든 테스트 실행
uv run pytest

# 상세 출력과 함께 실행
uv run pytest -v

# 특정 테스트 파일만 실행
uv run pytest tests/test_connection.py

# 테스트 출력 표시
uv run pytest -s
```

**직접 실행:**
```bash
# Python으로 직접 실행 (pytest 없이)
uv run python tests/test_connection.py
```

### 테스트 내용

`tests/test_connection.py`는 다음을 확인합니다:
- ✓ 환경변수에서 MONGO_URI 로드
- ✓ MongoDB 클라이언트 생성
- ✓ MongoDB 서버 연결
- ✓ 데이터베이스 목록 조회
- ✓ Ping 명령 응답
- ✓ Context manager를 사용한 연결

## 라이선스

MIT