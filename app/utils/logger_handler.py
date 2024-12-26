from loguru import logger


logger.add("logs/app.log", rotation="100 MB", retention="10 days", enqueue=True, backtrace=True, diagnose=True)
