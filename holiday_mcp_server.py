import json
import datetime
import os
import logging
from typing import Optional, Tuple, List, Dict, Any, Callable, Awaitable
from functools import lru_cache

import aiohttp

from mcp.server.fastmcp import FastMCP

# 配置日志
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s"
)
logger = logging.getLogger("holiday_mcp")

# 常量定义
current_year = datetime.datetime.now().year
holiday_url = (
    f"https://cdn.jsdelivr.net/gh/NateScarlet/holiday-cn@master/{current_year}.json"
)
DATA_PATH = "holiday_data/holiday_data.json"
DATA_DIR = "holiday_data"

# 确保数据目录存在
os.makedirs(DATA_DIR, exist_ok=True)


def _need_update_holiday_file() -> bool:
    """检查是否需要更新节假日数据文件

    Returns:
        bool: 如果需要更新返回True，否则返回False
    """
    if not os.path.exists(DATA_PATH):
        return True
    
    creation_time = os.path.getctime(DATA_PATH)
    creation_year = datetime.datetime.fromtimestamp(creation_time).year
    return creation_year != current_year


async def download_holiday_data() -> List[Dict[str, Any]]:
    """从网络下载节假日数据

    Returns:
        List[Dict[str, Any]]: 节假日数据列表

    Raises:
        Exception: 下载失败时抛出异常
    """
    logger.info(f"正在从 {holiday_url} 下载节假日数据...")
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(holiday_url, timeout=10) as resp:
                if resp.status != 200:
                    logger.error(f"下载节假日数据失败: HTTP {resp.status}")
                    raise Exception(f"下载节假日数据失败: HTTP {resp.status}")
                
                holiday_data = await resp.json()
                
                # 保存数据到本地
                with open(DATA_PATH, "w", encoding="utf-8") as f:
                    json.dump(holiday_data, f, ensure_ascii=False, indent=4)
                
                logger.info("节假日数据下载成功并保存到本地")
                return holiday_data["days"]
    except aiohttp.ClientError as e:
        logger.error(f"网络请求错误: {e}")
        raise Exception(f"网络请求错误: {e}")
    except Exception as e:
        logger.error(f"下载节假日数据失败: {e}")
        raise Exception(f"下载节假日数据失败: {e}")


async def get_holiday_data() -> List[Dict[str, Any]]:
    """获取节假日数据，优先从本地读取，如需更新则从网络下载

    Returns:
        List[Dict[str, Any]]: 节假日数据列表

    Raises:
        Exception: 获取数据失败时抛出异常
    """
    try:
        if not _need_update_holiday_file():
            logger.info("从本地读取节假日数据")
            with open(DATA_PATH, "r", encoding="utf-8") as f:
                holiday_data = json.load(f)
                return holiday_data["days"]
        
        logger.info("需要更新节假日数据")
        return await download_holiday_data()
    except (json.JSONDecodeError, KeyError) as e:
        logger.warning(f"读取本地节假日数据出错: {e}，尝试重新下载")
        return await download_holiday_data()
    except Exception as e:
        logger.error(f"获取节假日数据失败: {e}")
        raise Exception(f"获取节假日数据失败: {e}")


async def get_date_list() -> Tuple[List[str], List[str]]:
    """获取节假日和休息日列表

    Returns:
        Tuple[List[str], List[str]]: (holiday_list, offday_list)
            - holiday_list: 所有节假日列表
            - offday_list: 休息日列表
    """
    try:
        holiday_list = []
        offday_list = []

        holiday_data = await get_holiday_data()

        for item in holiday_data:
            if item["isOffDay"]:
                offday_list.append(item["date"])
            holiday_list.append(item["date"])

        logger.info(f"成功获取节假日列表，共 {len(holiday_list)} 个节假日，{len(offday_list)} 个休息日")
        return holiday_list, offday_list
    except Exception as e:
        logger.error(f"获取日期列表失败: {e}")
        raise Exception(f"获取日期列表失败: {e}")


def validate_date(date: Optional[str]) -> str:
    """验证并格式化日期

    Args:
        date: 日期字符串，格式为 %Y-%m-%d，如果为None则使用当前日期

    Returns:
        str: 格式化后的日期字符串

    Raises:
        ValueError: 日期格式错误
    """
    if date is None:
        return datetime.datetime.today().strftime("%Y-%m-%d")
    
    try:
        datetime.datetime.strptime(date, "%Y-%m-%d")
        return date
    except ValueError:
        raise ValueError("无效的日期格式，请使用 YYYY-MM-DD 格式")


# 创建 MCP 服务
mcp = FastMCP("Holiday 📅")


@mcp.resource("date://is_holiday/{date}")
async def is_holiday(date: Optional[str] = None) -> bool:
    formatted_date = validate_date(date)
    holiday_list, _ = await get_date_list()
    
    return formatted_date in holiday_list

@mcp.resource("date://is_workday/{date}")
async def is_workday(date: Optional[str] = None) -> bool:
    formatted_date = validate_date(date)
    _, offday_list = await get_date_list()
    
    # 判断是否是周末
    is_weekend = datetime.datetime.strptime(formatted_date, "%Y-%m-%d").weekday() >= 5
    
    # 如果是休息日或者是周末（且不是调休工作日），则不是工作日
    if formatted_date in offday_list or (is_weekend and formatted_date not in offday_list):
        return False
    
    return True


@mcp.resource("date://get_holiday_info/{date}")
async def get_holiday_info(date: Optional[str] = None) -> Dict[str, Any]:
    """获取指定日期的节假日信息

    Args:
        date: 日期字符串，格式为 %Y-%m-%d，如果为None则使用当前日期

    Returns:
        Dict[str, Any]: 包含日期信息的字典
    """
    formatted_date = validate_date(date)
    is_holiday_result = await is_holiday(formatted_date)
    is_workday_result = await is_workday(formatted_date)
    
    dt = datetime.datetime.strptime(formatted_date, "%Y-%m-%d")
    weekday = dt.weekday()
    weekday_names = ["周一", "周二", "周三", "周四", "周五", "周六", "周日"]
    
    return {
        "date": formatted_date,
        "is_holiday": is_holiday_result,
        "is_workday": is_workday_result,
        "weekday": weekday,
        "weekday_name": weekday_names[weekday]
    }


if __name__ == "__main__":
    logger.info("启动 Holiday MCP 服务...")
    mcp.run(transport="stdio")
