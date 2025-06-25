"""Manage log config"""

from fastapi import Request
from starlette.responses import Response
import logging
import logging.config
from logging.handlers import TimedRotatingFileHandler
import shutil
import json
import os
import contextvars
from datetime import datetime
from zoneinfo import ZoneInfo

from app.core.config.application import APPLICATION_CONFIG

logging.getLogger("python_multipart.multipart").setLevel(logging.ERROR)
logging.getLogger("watchfiles").setLevel(logging.ERROR)
add_on_var = contextvars.ContextVar("add_on", default="")

TIMEZONE = ZoneInfo(APPLICATION_CONFIG["timezone"])


class CustomLogFilter(logging.Filter):
    """Fill submit id"""

    def filter(self, record):
        """fill submit"""
        # ดึงค่า submitId จาก ContextVar และเพิ่มเข้าไปใน LogRecord
        record.add_on = add_on_var.get("")  # ถ้าไม่มี submitId, ใส่เป็นค่าว่าง
        return True


class CustomFormatter(logging.Formatter):
    """
    Custom Formatter to display log time in a specific timezone.
    Uses the modern 'zoneinfo' library.
    """

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        # Allow use of standard Formatter's datefmt if provided
        if "datefmt" in kwargs:
            self._datefmt = kwargs["datefmt"]
        else:
            self._datefmt = None
        self.timezone = TIMEZONE

    def formatTime(self, record, datefmt=None):
        # Convert the time to UTC+7 using pytz
        effective_datefmt = datefmt or self._datefmt

        dt = datetime.fromtimestamp(record.created, tz=self.timezone)

        if effective_datefmt:
            return dt.strftime(effective_datefmt)[:-3]
        else:
            # A clean ISO 8601 format with milliseconds
            return dt.isoformat(sep=" ", timespec="milliseconds")


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
        base_filename = "".join(os.path.basename(self.baseFilename).split(".")[0:-1])
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


# ฟังก์ชันสำหรับตั้งค่า submitId
def set_add_on_thread(submit_id: str):
    """Set submit id"""
    add_on_var.set(submit_id)


def setup_entry_exit():
    """Init Submitter log"""
    return logging.getLogger("submitter")


def set_application_log(name: str):
    """Init application log"""
    return logging.getLogger(name)


def init_log():
    """Init log setting"""
    log_config_path = os.path.join("resource", "log-config.json")
    with open(log_config_path, "r", encoding="utf-8") as f:
        log_config_dict = json.load(f)

    # แก้ไขชื่อไฟล์ application_log แบบ dynamic
    app_log_filename = log_config_dict["handlers"]["application_log"][
        "filename"
    ].replace("<my_app>", APPLICATION_CONFIG["applicatio_name"])
    log_config_dict["handlers"]["application_log"]["filename"] = app_log_filename

    # ตรวจสอบและสร้าง Directory ถ้ายังไม่มี
    log_dir = os.path.dirname(app_log_filename)
    if not os.path.exists(log_dir):
        os.makedirs(log_dir)

    return log_config_dict


# ฟังก์ชันที่สร้างขึ้นใหม่
def write_access_log(request: Request, response: Response):
    """
    Access log
    """
    access_logger = logging.getLogger("api.access")

    # --- ส่วนประกอบของ Log ---
    client_ip = request.client.host if request.client else "-"
    method = request.method
    path = request.url.path
    http_version = request.scope.get("http_version", "1.1")
    status_code = response.status_code
    body_sent = response.headers.get("content-length", "-")
    user_agent = request.headers.get("user-agent", "-")
    request_host = request.headers.get("host", "-")
    timestamp = datetime.now(TIMEZONE).strftime("%d/%b/%Y:%H:%M:%S %z")

    log_string = (
        f'{client_ip} - - [{timestamp}] "{method} {path} HTTP/{http_version}" '
        f'{status_code} {body_sent} "{request_host}" "{user_agent}"'
    )

    # เขียน log ด้วย logger ที่เราสร้างไว้
    access_logger.info(log_string)
