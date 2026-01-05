"""
图片上传服务

处理图片上传到 ImageBB 的逻辑
"""

import httpx
from app.config.settings import settings
from app.utils.logger import logger


class ImageUploadService:
    """图片上传服务类"""

    def __init__(self):
        self.imagebb_api_key = settings.IMAGEBB_API_KEY
        self.imagebb_url = "https://api.imgbb.com/1/upload"

    async def upload_to_imagebb(self, base64_data: str) -> str:
        """
        上传图片到 ImageBB

        Args:
            base64_data: base64 编码的图片数据（不包含前缀）

        Returns:
            str: 图片 URL

        Raises:
            Exception: 上传失败时抛出异常
        """
        if not self.imagebb_api_key:
            raise ValueError("ImageBB API Key 未配置")

        try:
            async with httpx.AsyncClient() as client:
                # 准备表单数据
                data = {
                    "key": self.imagebb_api_key,
                    "image": base64_data,
                    "type": "base64",
                    "name": f"upload_{httpx._utils.current_time()}"
                }

                response = await client.post(self.imagebb_url, data=data)
                response.raise_for_status()

                result = response.json()

                if result.get("success"):
                    image_url = result["data"]["url"]
                    logger.info(f"图片上传成功: {image_url}")
                    return image_url
                else:
                    error_msg = result.get("error", {}).get("message", "未知错误")
                    raise Exception(f"ImageBB API 错误: {error_msg}")

        except httpx.HTTPStatusError as e:
            logger.error(f"ImageBB HTTP 错误: {e}")
            raise Exception(f"图片上传失败: HTTP {e.response.status_code}")
        except Exception as e:
            logger.error(f"图片上传异常: {e}")
            raise Exception(f"图片上传失败: {str(e)}")

    def extract_base64_data(self, full_base64: str) -> str:
        """
        从完整的 base64 字符串中提取纯数据

        Args:
            full_base64: 完整的 base64 字符串（如 data:image/jpeg;base64,/9j/4AA...）

        Returns:
            str: 纯 base64 数据
        """
        if "," in full_base64:
            return full_base64.split(",", 1)[1]
        return full_base64

    async def upload_image(self, base64_image: str) -> str:
        """
        上传图片并返回 URL

        Args:
            base64_image: 完整的 base64 图片数据

        Returns:
            str: 图片 URL
        """
        base64_data = self.extract_base64_data(base64_image)
        return await self.upload_to_imagebb(base64_data)

    async def get_usage_stats(self) -> dict:
        """
        获取 ImageBB 使用统计

        Returns:
            dict: 使用统计信息
        """
        if not self.imagebb_api_key:
            raise ValueError("ImageBB API Key 未配置")

        try:
            async with httpx.AsyncClient() as client:
                response = await client.get(
                    f"{self.imagebb_url}/stats",
                    params={"key": self.imagebb_api_key}
                )
                response.raise_for_status()
                return response.json()
        except Exception as e:
            logger.error(f"获取使用统计失败: {e}")
            raise Exception(f"获取使用统计失败: {str(e)}")


# 创建单例实例
image_upload_service = ImageUploadService()