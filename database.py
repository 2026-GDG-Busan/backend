import os
from google.cloud import firestore
from dotenv import load_dotenv

# .env 파일 로드 (로컬 환경용)
load_dotenv()

# 환경변수에서 값 가져오기
PROJECT_ID = os.getenv("GCP_PROJECT_ID")
DATABASE_ID = os.getenv("GCP_DATABASE_ID")

# Firestore 클라이언트 초기화
db = firestore.Client(project=PROJECT_ID, database=DATABASE_ID)

def get_user_state(user_id: str):
    """유저의 현재 게이지 및 상태를 DB에서 가져옵니다."""
    doc_ref = db.collection("user_states").document(user_id)
    doc = doc_ref.get()
    
    if doc.exists:
        return doc.to_dict()
    else:
        # 데이터가 없으면 기본값 반환
        return {
            "gauge": 0,
            "prayer_required": False,
            "last_change_tick": 0
        }

def update_user_state(user_id: str, data: dict):
    """유저의 상태 정보를 DB에 저장합니다."""
    doc_ref = db.collection("user_states").document(user_id)
    doc_ref.set(data, merge=True)

def submit_ranking(name: str, time_spent: float):
    """새로운 랭킹 기록을 저장합니다."""
    # 서버 시간 기준으로 타임스탬프와 함께 저장
    db.collection("rankings").add({
        "name": name,
        "time": round(time_spent, 2),
        "created_at": firestore.SERVER_TIMESTAMP
    })

def get_top_rankings(limit: int = 10):
    """가장 빨리 깨운 순서대로 랭킹을 가져옵니다."""
    rankings_ref = db.collection("rankings")
    # 시간(time) 기준 오름차순 정렬
    query = rankings_ref.order_by("time", direction=firestore.Query.ASCENDING).limit(limit)
    docs = query.stream()
    
    return [{"name": doc.to_dict()["name"], "time": doc.to_dict()["time"]} for doc in docs]
