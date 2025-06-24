"""Manage log config"""

import logging
import logging.config
from logging.handlers import TimedRotatingFileHandler
import shutil
import json
import os
import contextvars
from datetime import datetime
import pytz

from app.core.config.application import APPLICATION_CONFIG
logging.getLogger("python_multipart.multipart").setLevel(logging.ERROR)
logging.getLogger("watchfiles").setLevel(logging.ERROR)
add_on_var = contextvars.ContextVar("add_on", default="")


class CustomLogFilter(logging.Filter):
    """Fill submit id"""

    def filter(self, record):
        """fill submit"""
        # ดึงค่า submitId จาก ContextVar และเพิ่มเข้าไปใน LogRecord
        record.add_on = add_on_var.get("")  # ถ้าไม่มี submitId, ใส่เป็นค่าว่าง
        return True


class CustomFormatter(logging.Formatter):
    """Custom format log consoles"""

    def formatTime(self, record, datefmt=None):
        # Convert the time to UTC+7 using pytz
        utc_dt = datetime.utcfromtimestamp(record.created)
        local_tz = pytz.timezone(APPLICATION_CONFIG["timezone"])  # UTC+7 timezone
        local_dt = utc_dt.replace(tzinfo=pytz.utc).astimezone(local_tz)

        if datefmt:
            s = local_dt.strftime(datefmt)[:-3]
        else:
            t = local_dt.strftime("%Y-%m-%d %H:%M:%S,%f")[:-3]
            s = f"{t}.{int(record.msecs):03d}"  # Add milliseconds with a dot
        return s


class CustomTimedRotatingFileHandler(TimedRotatingFileHandler):
    """Class for archived log"""
    def doRollover(self):
        super().doRollover()  # เรียกใช้งานการหมุนไฟล์ตามปกติ

        # กำหนดโฟลเดอร์ปลายทาง
        archived_folder = "logs/archived/"

        # เก็บวันที่ปัจจุบัน
        current_time = datetime.now().strftime("%Y-%m-%d")

        # ตรวจสอบไฟล์ที่ถูกหมุนและเปลี่ยนชื่อไฟล์ให้เป็นรูปแบบที่กำหนด
        log_directory = "logs"
        base_filename = APPLICATION_CONFIG["applicatio_name"]
        log_suffix = ".log"

        # ตรวจสอบไฟล์ที่ถูกหมุน
        for filename in os.listdir(log_directory):
            if filename.startswith(base_filename) and not filename.endswith(log_suffix):
                # นับจำนวนไฟล์ในวันที่เดียวกันเพื่อเพิ่มตัวเลข .0, .1 ฯลฯ
                count = 0
                for file in os.listdir(log_directory):
                    if file.startswith(
                        f"{base_filename}-{current_time}"
                    ) and file.endswith(log_suffix):
                        count += 1

                # เปลี่ยนชื่อไฟล์ให้อยู่ในรูปแบบที่ต้องการ
                new_filename = f"{base_filename}-{current_time}.{count}{log_suffix}"
                source = os.path.join(log_directory, filename)
                destination = os.path.join(archived_folder, new_filename)
                shutil.move(source, destination)

FORMAT_APPLICATION = CustomFormatter(
    "%(asctime)s %(levelname)s [%(thread)d-%(threadName)s%(add_on)s] %(name)s:%(lineno)d %(message)s",
    datefmt="%Y-%m-%d %H:%M:%S,%f",
)

FORMAT_ENTRY_EXIT = CustomFormatter(
    "%(asctime)s %(levelname)s [%(thread)d-%(threadName)s%(add_on)s]%(message)s",
    datefmt="%Y-%m-%d %H:%M:%S,%f",
)

# ฟังก์ชันสำหรับตั้งค่า submitId
def set_add_on_thread(submit_id: str):
    """Set submit id"""
    add_on_var.set(submit_id)

def setup_entry_exit(name:str):
    """Entry & Exit"""
    # กำหนด path ของไฟล์ log-config.json
    log_config_path = os.path.join('resource', 'log-config.json')

    with open(file=log_config_path, mode="r",encoding="utf-8") as f:
        log_config = json.load(f)

    pathfile_name = log_config["handlers"]["file"]["filename"].replace(
        "<my_app>", APPLICATION_CONFIG["applicatio_name"]
    )

    log_config["handlers"]["file"]["filename"] = pathfile_name
    # ตั้งค่า logger จาก log-config.json
    logging.config.dictConfig(log_config)
    logger = logging.getLogger(name)

    custom_filter = CustomLogFilter()
    logger.addFilter(custom_filter)
    return logger

def setup_logger(name: str):
    """set loger each class"""
    # กำหนด path ของไฟล์ log-config.json
    log_config_path = os.path.join("resource", "log-config.json")

    # โหลดไฟล์ config จาก JSON
    with open(file=log_config_path, mode="r",encoding="utf-8") as f:
        log_config = json.load(f)

    pathfile_name = log_config["handlers"]["file"]["filename"].replace(
        "<my_app>", APPLICATION_CONFIG["applicatio_name"]
    )
    log_config["handlers"]["file"]["filename"] = pathfile_name
    if not os.path.exists(log_config["handlers"]["file"]["filename"]):
        os.makedirs(os.path.dirname(pathfile_name), exist_ok=True)
        open(file = pathfile_name, mode = "w",encoding="utf-8").close()
    # ตั้งค่าระบบ logging ด้วย dictConfig
    logging.config.dictConfig(log_config)
    logger = logging.getLogger(name)
    return logger
