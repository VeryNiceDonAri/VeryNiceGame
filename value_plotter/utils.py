from datetime import datetime

def get_value_and_time(source):
    """
    (현재 시간, 값) 반환
    source가 callable이면 호출, 아니면 직접 값을 반환
    """
    if callable(source):
        value = source()
    else:
        value = source
    return datetime.now(), value