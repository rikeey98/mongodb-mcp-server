"""MongoDB Connection Tests"""
import os
import pytest
from pymongo import MongoClient
from pymongo.errors import ServerSelectionTimeoutError, ConnectionFailure
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()


class TestMongoDBConnection:
    """MongoDB 연결 테스트"""

    @pytest.fixture
    def mongo_uri(self):
        """MongoDB URI 가져오기"""
        return os.getenv("MONGO_URI", "mongodb://localhost:27017")

    @pytest.fixture
    def client(self, mongo_uri):
        """MongoDB 클라이언트 생성"""
        return MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)

    def test_mongo_uri_env_variable(self, mongo_uri):
        """환경변수에서 MONGO_URI를 제대로 가져오는지 테스트"""
        assert mongo_uri is not None
        assert isinstance(mongo_uri, str)
        assert mongo_uri.startswith("mongodb://") or mongo_uri.startswith("mongodb+srv://")
        print(f"✓ MONGO_URI: {mongo_uri}")

    def test_client_creation(self, client):
        """MongoDB 클라이언트가 제대로 생성되는지 테스트"""
        assert client is not None
        assert isinstance(client, MongoClient)
        print("✓ MongoDB 클라이언트 생성 성공")

    def test_server_connection(self, client):
        """MongoDB 서버에 실제로 연결되는지 테스트"""
        try:
            # 서버 정보 가져오기 (연결 확인)
            server_info = client.server_info()
            assert server_info is not None
            assert "version" in server_info
            print(f"✓ MongoDB 서버 연결 성공")
            print(f"  - MongoDB 버전: {server_info.get('version')}")

        except ServerSelectionTimeoutError:
            pytest.fail("MongoDB 서버에 연결할 수 없습니다. 서버가 실행 중인지 확인하세요.")
        except ConnectionFailure as e:
            pytest.fail(f"MongoDB 연결 실패: {str(e)}")

    def test_list_databases(self, client):
        """데이터베이스 목록을 가져올 수 있는지 테스트"""
        try:
            databases = client.list_database_names()
            assert isinstance(databases, list)
            print(f"✓ 데이터베이스 목록 조회 성공")
            print(f"  - 데이터베이스 개수: {len(databases)}")
            if databases:
                print(f"  - 데이터베이스 목록: {', '.join(databases[:5])}")

        except Exception as e:
            pytest.fail(f"데이터베이스 목록 조회 실패: {str(e)}")

    def test_ping_database(self, client):
        """ping 명령으로 데이터베이스 응답 확인"""
        try:
            result = client.admin.command('ping')
            assert result.get('ok') == 1.0
            print("✓ MongoDB ping 응답 성공")

        except Exception as e:
            pytest.fail(f"MongoDB ping 실패: {str(e)}")

    def test_context_manager(self, mongo_uri):
        """Context manager를 사용한 연결 테스트"""
        try:
            with MongoClient(mongo_uri, serverSelectionTimeoutMS=5000) as client:
                # 연결 확인
                client.admin.command('ping')
                print("✓ Context manager를 사용한 연결 성공")

        except Exception as e:
            pytest.fail(f"Context manager 연결 실패: {str(e)}")


def test_direct_connection():
    """직접 연결 테스트 (fixture 없이)"""
    load_dotenv()
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")

    try:
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        # 연결 확인
        client.admin.command('ping')
        print(f"✓ 직접 연결 성공: {mongo_uri}")
        client.close()

    except ServerSelectionTimeoutError:
        pytest.fail("MongoDB 서버에 연결할 수 없습니다.")
    except Exception as e:
        pytest.fail(f"연결 실패: {str(e)}")


if __name__ == "__main__":
    """pytest 없이 직접 실행하는 경우"""
    print("=" * 60)
    print("MongoDB 연결 테스트")
    print("=" * 60)

    load_dotenv()
    mongo_uri = os.getenv("MONGO_URI", "mongodb://localhost:27017")

    print(f"\n1. 환경변수 확인")
    print(f"   MONGO_URI: {mongo_uri}")

    try:
        print(f"\n2. MongoDB 클라이언트 생성")
        client = MongoClient(mongo_uri, serverSelectionTimeoutMS=5000)
        print("   ✓ 클라이언트 생성 성공")

        print(f"\n3. 서버 연결 확인")
        server_info = client.server_info()
        print(f"   ✓ 연결 성공")
        print(f"   - MongoDB 버전: {server_info.get('version')}")

        print(f"\n4. 데이터베이스 목록 조회")
        databases = client.list_database_names()
        print(f"   ✓ 조회 성공")
        print(f"   - 데이터베이스 개수: {len(databases)}")
        if databases:
            print(f"   - 목록: {', '.join(databases)}")

        print(f"\n5. Ping 테스트")
        result = client.admin.command('ping')
        print(f"   ✓ Ping 성공: {result}")

        client.close()
        print(f"\n{'=' * 60}")
        print("✓ 모든 테스트 통과!")
        print("=" * 60)

    except ServerSelectionTimeoutError:
        print("\n❌ MongoDB 서버에 연결할 수 없습니다.")
        print("   - MongoDB가 실행 중인지 확인하세요")
        print(f"   - URI가 올바른지 확인하세요: {mongo_uri}")

    except ConnectionFailure as e:
        print(f"\n❌ 연결 실패: {e}")

    except Exception as e:
        print(f"\n❌ 오류 발생: {e}")
