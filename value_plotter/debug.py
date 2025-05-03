import logging
import remote_pdb as rpdb


def setup_logging():
    """스레드명 포함 기본 로깅 설정"""
    logging.basicConfig(
        level=logging.DEBUG,
        format="%(asctime)s [%(threadName)s] %(levelname)s: %(message)s"
    )


def setup_debugger(port=4444):
    """원격 디버거 대기 상태 설정"""
    logging.debug(f"Starting remote debugger on port {port}")
    rpdb.set_trace(port=port)