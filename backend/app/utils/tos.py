"""火山引擎 TOS 对象存储上传工具。用于将图片上传到 TOS 获取公网 URL。"""

import uuid
import logging
from app.config import config

logger = logging.getLogger(__name__)


def upload_to_tos(image_bytes: bytes, key_prefix: str, content_type: str = "image/png") -> str:
    """Upload image bytes to TOS and return the public URL.

    Args:
        image_bytes: Image file bytes
        key_prefix: Object key prefix (e.g. "character", "scene", "tail_frame")
        content_type: MIME type

    Returns:
        Public HTTPS URL of the uploaded object
    """
    ak = config.TOS_ACCESS_KEY
    sk = config.TOS_SECRET_KEY
    bucket = config.TOS_BUCKET
    endpoint = config.TOS_ENDPOINT

    if not bucket or not ak or not sk:
        raise ValueError("TOS not configured: missing bucket/AK/SK. Check .env file.")

    from tos import TosClientV2, ACLType
    client = TosClientV2(ak, sk, endpoint, "cn-beijing")
    object_key = f"drama/{key_prefix}_{uuid.uuid4().hex[:8]}.png"
    client.put_object(bucket, object_key, content=image_bytes,
                      content_type=content_type, acl=ACLType.ACL_Public_Read)

    url = f"https://{bucket}.{endpoint}/{object_key}"
    logger.info("TOS upload: %s → %s", key_prefix, url[:80])
    return url
