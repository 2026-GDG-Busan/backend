import random
import time
from fastapi import APIRouter
from backend.models import WakeUpRequest
from backend.config import GAME_CONFIG
from backend.database import get_user_state, update_user_state

router = APIRouter()

@router.post("/wakeup")
async def process_wakeup(data: WakeUpRequest):
    # 1. DB에서 유저 세션 정보 가져오기
    session = get_user_state(data.user_id)
    current_gauge = session["gauge"]
    
    # 처음 시작하거나 리셋된 후라면 시작 시간 기록
    if current_gauge == 0 and session.get("start_time") is None:
        session["start_time"] = time.time()
        update_user_state(data.user_id, session)

    # 2. 랜덤하게 기도 요구 상태 전환 (약 10% 확률로 상태 변경)
    if random.random() < 0.1:
        session["prayer_required"] = not session["prayer_required"]

    message = ""
    change = 0
    status = "sleeping"

    # 3. 킹받는 채점 로직 (랜덤 요소 반영)
    is_loud = data.volume > GAME_CONFIG["LOUD_THRESHOLD"]
    is_good_vol = GAME_CONFIG["GOOD_PRAY_MIN_VOL"] <= data.volume <= GAME_CONFIG["LOUD_THRESHOLD"]
    is_low_vol = GAME_CONFIG["LOW_PRAY_MIN_VOL"] <= data.volume < GAME_CONFIG["GOOD_PRAY_MIN_VOL"]

    if is_loud:
        change = GAME_CONFIG["DEC_LOUD_PUNISH"]
        message = "아 시끄러워!!! 조용히 좀 깨워!!"
    
    elif session["prayer_required"]:
        # [기도가 꼭 필요한 상태]
        if data.is_praying:
            if is_good_vol:
                change = GAME_CONFIG["INC_GOOD_PRAY"]
                message = "오... 기도가 아주 정성스럽구나! 계속해!"
            elif is_low_vol:
                change = GAME_CONFIG["INC_LOW_PRAY"]
                message = "기도는 좋은데 목소리가 작다?"
            else:
                change = GAME_CONFIG["DEC_IDLE_PUNISH"]
                message = "기도만 하지 말고 말도 좀 해봐!"
        else:
            # 기도를 안 함 (감점 강화)
            change = GAME_CONFIG["DEC_IDLE_PUNISH"] * 2
            message = "지금은 기도가 필요한 타이밍이야! 당장 빌어!"
    
    else:
        # [기도가 필수는 아닌 상태]
        if is_good_vol:
            change = GAME_CONFIG["INC_GOOD_PRAY"]
            # 기도를 안 해도 되는데 하면 가산점 (1.2배)
            if data.is_praying:
                change = int(change * 1.2)
                message = "오! 시키지도 않았는데 기도까지? 기특하군."
            else:
                message = "음... 목소리가 아주 좋구나. 계속해봐."
        elif is_low_vol:
            change = GAME_CONFIG["INC_LOW_PRAY"]
            message = "소리가 좀 작다? 더 크게!"
        else:
            change = GAME_CONFIG["DEC_IDLE_PUNISH"]
            message = "가만히 있지 말고 뭐라도 해봐!"

    # 4. 게이지 업데이트
    # 만약 팝업(민원)이 활성 상태라면 게이지 상승을 막음
    if data.is_popup_active and change > 0:
        change = 0
        message = "민원 처리 중입니다... (상승 불가)"

    new_gauge = max(0, min(GAME_CONFIG["TARGET_GAUGE"], current_gauge + change))
    session["gauge"] = new_gauge
    
    # DB에 최종 상태 저장
    update_user_state(data.user_id, session)

    elapsed_time = 0
    if new_gauge >= GAME_CONFIG["TARGET_GAUGE"]:
        status = "awoken"
        message = "알았어, 일어났어! 근데 나 다시 졸려..."
        # 경과 시간 계산
        if "start_time" in session and session["start_time"] is not None:
            elapsed_time = time.time() - session["start_time"]
            # 성공 후에는 다음 게임을 위해 세션 데이터에서 start_time 제거
            session["start_time"] = None
            session["gauge"] = 0 # 다음을 위해 리셋
            update_user_state(data.user_id, session)

    return {
        "gauge": new_gauge,
        "message": message,
        "status": status,
        "prayer_required": session["prayer_required"],
        "voice_trigger": "angry" if is_loud else "lazy",
        "elapsed_time": round(elapsed_time, 2)
    }

@router.post("/reset")
async def reset_gauge(data: WakeUpRequest):
    # DB 데이터 초기화 (시간 정보도 삭제)
    update_user_state(data.user_id, {
        "gauge": 0,
        "prayer_required": False,
        "start_time": None
    })
    return {"message": "Reset successful", "gauge": 0}
