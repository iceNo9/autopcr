# ============ module/notify.py ============

import smtplib
from email.header import Header
from email.mime.text import MIMEText

from ...model.enums import *
from ...model.error import *
from ...util.logger import instance as logger
from ..config import *
from ..modulebase import *

# ============ 配置定义 ============

# 纯字符串列表，与 cron.py 风格一致
EMAIL_PROVIDERS = ["QQ邮箱", "163邮箱", "126邮箱"]

# 服务商到 SMTP 配置的映射
SMTP_CONFIGS = {
    "QQ邮箱": {"host": "smtp.qq.com", "port": 587},
    "163邮箱": {"host": "smtp.163.com", "port": 465},
    "126邮箱": {"host": "smtp.126.com", "port": 465},
}


# ============ 抽象基类 ============

class NotifyModule(Module):
    """通知模块抽象基类"""

    def is_configured(self) -> bool:
        """检查配置是否完整"""
        raise NotImplementedError

    async def send_notification(
        self, subject: str, body: str, is_html: bool = False
    ) -> bool:
        """发送通知"""
        raise NotImplementedError


# ============ SMTP 实现 ============

class SmtpNotify(NotifyModule):
    """SMTP 邮件通知实现（单例 + 连接复用）"""

    _instance = None  # 单例实例
    _server = None    # SMTP 连接（复用）

    def __new__(cls, *args, **kwargs):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
        return cls._instance

    def __init__(self, modulemgr=None):
        # 避免重复初始化
        if hasattr(self, '_initialized'):
            return
        self._initialized = True
        super().__init__(modulemgr)

    def get_notify_email_enable(self) -> bool:
        """是否启用邮件通知"""
        return self.get_config("notify_email_enable")

    def get_notify_email_user(self) -> str:
        """获取发件人邮箱"""
        return self.get_config("notify_email_user")

    def get_notify_email_to(self) -> str:
        """获取收件人邮箱"""
        return self.get_config("notify_email_to")

    def get_notify_email_password(self) -> str:
        """获取邮箱授权码"""
        return self.get_config("notify_email_password")

    def get_notify_email_provider(self) -> str:
        """获取邮箱服务商（如 'QQ邮箱'）"""
        return self.get_config("notify_email_provider")

    def get_smtp_config(self) -> dict:
        """根据服务商获取 SMTP 配置"""
        provider = self.get_notify_email_provider()
        return SMTP_CONFIGS.get(provider, SMTP_CONFIGS["QQ邮箱"])

    def _get_server(self):
        """获取或创建 SMTP 连接（复用）"""
        if self._server is not None:
            return self._server

        smtp = self.get_smtp_config()
        try:
            if smtp.get("port") == 465:
                server = smtplib.SMTP_SSL(smtp["host"], smtp["port"])
            else:
                server = smtplib.SMTP(smtp["host"], smtp["port"])
                server.starttls()

            user = self.get_notify_email_user()
            password = self.get_notify_email_password()
            server.login(user, password)

            self._server = server
            return server

        except smtplib.SMTPException as e:
            logger.error(f"SMTP 连接失败: {e}")
            return None
        except Exception as e:
            logger.error(f"连接失败: {e}")
            return None

    def _close_server(self):
        """关闭 SMTP 连接"""
        if self._server is not None:
            try:
                self._server.quit()
            except Exception as e:
                logger.warning(f"关闭 SMTP 连接时出错: {e}")
                pass
            self._server = None

    def is_configured(self) -> bool:
        """检查 SMTP 配置是否完整"""
        enable = self.get_notify_email_enable()
        user = self.get_notify_email_user()
        to = self.get_notify_email_to()
        password = self.get_notify_email_password()
        
        # 逐个检查，方便断点调试
        if not enable:
            return False
        if not bool(user):
            return False
        if not bool(to):
            return False
        return bool(password)

    async def send_notification(
        self, subject: str, body: str, is_html: bool = False
    ) -> bool:
        """发送 SMTP 邮件（复用连接）"""
        if not self.is_configured():
            logger.warning("邮件通知未配置，跳过发送")
            return False

        user = self.get_notify_email_user()
        to = self.get_notify_email_to()

        content_type = "html" if is_html else "plain"
        msg = MIMEText(body, content_type, "utf-8")
        msg["From"] = Header(user)
        msg["To"] = Header(to)
        msg["Subject"] = Header(subject, "utf-8")

        try:
            server = self._get_server()
            if server is None:
                return False

            server.sendmail(user, [to], msg.as_string())
            logger.info(f"邮件发送成功: {subject} -> {to}")
            return True

        except smtplib.SMTPServerDisconnected:
            logger.warning("SMTP 连接已断开，尝试重新连接...")
            # 连接断开，尝试重新连接
            self._close_server()
            server = self._get_server()
            if server is None:
                logger.error("重新连接 SMTP 失败")
                return False
            try:
                server.sendmail(user, [to], msg.as_string())
                logger.info(f"邮件重发成功: {subject} -> {to}")
                return True
            except Exception as e:
                logger.error(f"重发邮件失败: {e}")
                return False

        except smtplib.SMTPException as e:
            logger.error(f"SMTP 邮件发送失败: {e}")
            self._close_server()
            return False
        except Exception as e:
            logger.error(f"邮件发送失败: {e}")
            return False


# ============ 配置类 ============

@texttype("notify_email_to", "接收通知的邮箱", "")
@texttype("notify_email_password", "邮箱授权码", "")
@texttype("notify_email_user", "发送通知的邮箱", "")
@singlechoice("notify_email_provider", "邮箱服务商", "QQ邮箱", EMAIL_PROVIDERS)
@booltype("notify_email_enable", "启用邮件通知", False)
@description("邮件通知配置 - 任务完成后发送邮件提醒")
@name("邮件通知")
@default(False)
@notrunnable
class email_notify(SmtpNotify):
    """邮件通知模块"""