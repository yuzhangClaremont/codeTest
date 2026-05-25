from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import StreamingResponse
from pydantic import BaseModel
from typing import Optional
from datetime import datetime, timezone
import asyncio
import io
import uuid
import os

from PIL import Image

app = FastAPI(title="Image Compression Service", version="1.0.0")

ALLOWED_EXTENSIONS = {".jpg", ".jpeg", ".png", ".gif", ".bmp", ".webp", ".tiff"}
MAX_FILE_SIZE = 10 * 1024 * 1024  # 10MB

_history: list[dict] = []
_lock = asyncio.Lock()


class HistoryItem(BaseModel):
    id: str
    original_filename: str
    original_size: int
    compressed_size: int
    compression_ratio: float
    content_type: str
    timestamp: str


class HistoryResponse(BaseModel):
    total: int
    items: list[HistoryItem]


class CompressResponse(BaseModel):
    id: str
    original_filename: str
    original_size: int
    compressed_size: int
    compression_ratio: float
    content_type: str
    timestamp: str


def _get_file_extension(filename: str) -> str:
    """从文件名中获取扩展名，转小写"""
    _, ext = os.path.splitext(filename)
    return ext.lower()


MIN_IMAGE_SIZE = 2

def _validate_image(file: UploadFile, content: bytes) -> str:
    """
    检查上传的文件是不是合法图片。
    返回图片格式字符串，如 'jpeg', 'png' 等。
    """
    if not file or not file.filename:
        raise HTTPException(status_code=400, detail="No file uploaded")

    if len(content) == 0:
        raise HTTPException(status_code=400, detail="Uploaded file is empty")

    if len(content) > MAX_FILE_SIZE:
        raise HTTPException(
            status_code=413,
            detail=f"File size exceeds maximum allowed size of {MAX_FILE_SIZE // (1024 * 1024)}MB",
        )

    ext = _get_file_extension(file.filename)
    if ext not in ALLOWED_EXTENSIONS:
        raise HTTPException(
            status_code=400,
            detail=f"Unsupported file type: {ext}. Allowed types: {', '.join(ALLOWED_EXTENSIONS)}",
        )

    try:
        img = Image.open(io.BytesIO(content))
        img.verify()
    except Exception:
        raise HTTPException(status_code=400, detail="File is not a valid image")

    ext_to_format = {".jpg": "jpeg", ".jpeg": "jpeg", ".png": "png", ".gif": "gif",
                     ".bmp": "bmp", ".webp": "webp", ".tiff": "tiff"}
    return ext_to_format.get(ext, "jpeg")


def _compress_image(content: bytes, image_type: str) -> bytes:
    """
    压缩图片：缩小尺寸 + 降低质量。
    思路很简单 - 把图片缩小到原来的50%，然后降低保存质量。
    """
    try:
        img = Image.open(io.BytesIO(content))

        if img.width < MIN_IMAGE_SIZE or img.height < MIN_IMAGE_SIZE:
            raise HTTPException(status_code=400, detail="Image is too small to compress")

        new_width = max(img.width // 2, 1)
        new_height = max(img.height // 2, 1)
        img = img.resize((new_width, new_height))

        if image_type == "jpeg" and img.mode in ("RGBA", "P", "LA"):
            img = img.convert("RGB")

        output = io.BytesIO()

        if image_type == "jpeg":
            img.save(output, format="JPEG", quality=50)
        elif image_type == "png":
            img.save(output, format="PNG")
        elif image_type == "webp":
            img.save(output, format="WEBP", quality=50)
        else:
            img.save(output, format=image_type.upper())

        return output.getvalue()
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Image compression failed: {str(e)}")


@app.post("/api/compress", response_model=CompressResponse)
async def compress_image(file: UploadFile = File(...)):
    """
    上传图片并压缩。
    返回压缩后的图片信息（id、原始大小、压缩后大小、压缩率等）。
    """
    content = await file.read()

    image_type = _validate_image(file, content)

    compressed_content = _compress_image(content, image_type)

    original_size = len(content)
    compressed_size = len(compressed_content)
    compression_ratio = round((1 - compressed_size / original_size) * 100, 2) if original_size > 0 else 0.0
    if compression_ratio < 0:
        compression_ratio = 0.0

    record = {
        "id": str(uuid.uuid4()),
        "original_filename": file.filename,
        "original_size": original_size,
        "compressed_size": compressed_size,
        "compression_ratio": compression_ratio,
        "content_type": f"image/{image_type}",
        "timestamp": datetime.now(timezone.utc).isoformat(),
        "_compressed_data": compressed_content,
    }

    async with _lock:
        _history.append(record)

    return CompressResponse(
        id=record["id"],
        original_filename=record["original_filename"],
        original_size=original_size,
        compressed_size=compressed_size,
        compression_ratio=compression_ratio,
        content_type=record["content_type"],
        timestamp=record["timestamp"],
    )


@app.get("/api/compress/{image_id}")
async def get_compressed_image(image_id: str):
    """
    根据id下载压缩后的图片。
    """
    async with _lock:
        record = next((item for item in _history if item["id"] == image_id), None)

    if not record:
        raise HTTPException(status_code=404, detail="Image not found")

    compressed_data = record.get("_compressed_data")
    if not compressed_data:
        raise HTTPException(status_code=404, detail="Compressed image data not available")

    return StreamingResponse(
        io.BytesIO(compressed_data),
        media_type=record["content_type"],
        headers={"Content-Disposition": f"attachment; filename=compressed_{record['original_filename']}"},
    )


@app.get("/api/history", response_model=HistoryResponse)
async def get_history():
    """
    获取压缩历史记录。
    """
    async with _lock:
        items = list(_history)

    clean_items = []
    for item in items:
        clean_items.append(
            HistoryItem(
                id=item["id"],
                original_filename=item["original_filename"],
                original_size=item["original_size"],
                compressed_size=item["compressed_size"],
                compression_ratio=item["compression_ratio"],
                content_type=item["content_type"],
                timestamp=item["timestamp"],
            )
        )

    return HistoryResponse(total=len(clean_items), items=clean_items)


@app.delete("/api/history/{image_id}")
async def delete_history_item(image_id: str):
    """
    根据id删除一条历史记录。
    """
    async with _lock:
        index = next((i for i, item in enumerate(_history) if item["id"] == image_id), None)

    if index is None:
        raise HTTPException(status_code=404, detail="History item not found")

    async with _lock:
        _history.pop(index)

    return {"message": "History item deleted successfully", "id": image_id}


@app.get("/")
async def root():
    return {"message": "Image Compression Service"}
