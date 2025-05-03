import time
import matplotlib.pyplot as plt
import warnings
from concurrent.futures import ThreadPoolExecutor
from .debug import setup_logging, setup_debugger
from .utils import get_value_and_time

warnings.filterwarnings("ignore")

# 스레드 풀 생성 (최대 2개 워커)
_executor = ThreadPoolExecutor(max_workers=2)


def plot_value(variable_source, *, interval=1.0, enable_logging=False, enable_debug=False, show_plot=True):
    """
    실시간 변수 모니터링 및 플로팅

    Args:
        variable_source: 값을 반환하는 함수 또는 직접 변수
        interval (float): 샘플링 주기(초)
        enable_logging (bool): 로깅 활성화
        enable_debug (bool): 디버거 활성화
        show_plot (bool): 플롯 창 표시 여부
    """
    if enable_logging:
        setup_logging()
    if enable_debug:
        setup_debugger()

    def _worker():
        times, values = [], []
        plt.ion()                     # 인터랙티브 모드 켜기
        fig = plt.figure()
        ax = fig.add_subplot(1, 1, 1)
        plt.show(block=False)
        while True:
            ts, val = get_value_and_time(variable_source)
            times.append(ts)
            values.append(val)
            ax.clear()
            ax.plot(times, values)
            fig.autofmt_xdate(rotation=30)
            if show_plot:
                plt.pause(0.01)         # 비차단 업데이트
            time.sleep(interval)

    _executor.submit(_worker)