import os
import logbook
from logbook import Logger,TimedRotatingFileHandler
from logbook.more import ColorizedStderrHandler

from core.env import env

DATETIME_FORMAT = "%Y-%m-%d %H:%M:%S.%f"

# 日志打印到屏幕
def log_formatter(record, subject):

    # log = "{dt} {level} {msg}".format(
    #     dt=record.time.strftime(DATETIME_FORMAT),           # 日志时间
    #     level=record.level_name,                            # 日志等级
    #     msg=record.message,                                 # 日志内容

    # )

    #return log

    log = "[{date}] [{level}] [{filename}] [{func_name}] [{lineno}] {msg}".format(
        date = record.time,                              # 日志时间
        level = record.level_name,                       # 日志等级
        filename = os.path.split(record.filename)[-1],   # 文件名
        func_name = record.func_name,                    # 函数名
        lineno = record.lineno,                          # 行号
        msg = record.message                             # 日志内容
    )

    return log

std_handler = ColorizedStderrHandler(bubble=True)
std_handler.formatter = log_formatter


# 日志存放路径
LOG_DIR = env.log_dir
if not os.path.exists(LOG_DIR):
    os.makedirs(LOG_DIR)


# 日志打印到文件
log_file_debug = TimedRotatingFileHandler(os.path.join(LOG_DIR, '{}.log'.format('debug')), date_format='%Y-%m-%d', level=logbook.DEBUG, bubble=True, encoding='utf-8')
log_file_debug.formatter = log_formatter

log_file_info = TimedRotatingFileHandler(os.path.join(LOG_DIR, '{}.log'.format('info')), date_format='%Y-%m-%d', level=logbook.INFO, bubble=True, encoding='utf-8')
log_file_info.formatter = log_formatter

log_file_err = TimedRotatingFileHandler(os.path.join(LOG_DIR, '{}.log'.format('err')), date_format='%Y-%m-%d', level=logbook.WARNING, bubble=True, encoding='utf-8')
log_file_err.formatter = log_formatter

def init_logger(level=logbook.INFO):
    logbook.set_datetime_format("local")

    system_log = Logger("system_log")
    system_log.handlers = []
    system_log.handlers.append(log_file_debug)
    system_log.handlers.append(log_file_info)
    system_log.handlers.append(log_file_err)
    system_log.handlers.append(std_handler)

    system_log.level = level

    return system_log

system_log = init_logger()

__all__ = [
    "system_log",
]