# 상전 AI 모시기 - 백엔드 게임 룰 설정

GAME_CONFIG = {
    # 볼륨 임계값
    "LOUD_THRESHOLD": 85,       # 85 이상이면 '시끄러움' (조금만 더 커져도 감점!)
    "GOOD_PRAY_MIN_VOL": 40,    # 55~85 사이의 적절한 성량이 필요함
    "LOW_PRAY_MIN_VOL": 25,     # 최소 35 이상의 소리는 내야 함

    # 게이지 증감량 (초당 변화량)
    "INC_GOOD_PRAY": 30,         # 성공 시 +5 (천천히 차오름)
    "INC_LOW_PRAY": 15,          # 소리 작으면 겨우 +2
    "DEC_LOUD_PUNISH": -8,      # 너무 시끄러우면 무려 -8 (대폭 감점)
    "DEC_IDLE_PUNISH": -4,      # 아무것도 안 할 때 -4 (방치 시 금방 0점 됨)
    
    # 승리 조건
    "TARGET_GAUGE": 100
}
