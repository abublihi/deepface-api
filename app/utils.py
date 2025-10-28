# utils.py
import os
import tempfile
import shutil
import base64
import aiohttp
from typing import Optional
from fastapi import Request, UploadFile, HTTPException
import numpy as np


async def extract_image_from_request(
    request: Request,
    img_key: str,
    file: Optional[UploadFile] = None,
) -> str:
    """
    Extract image path from request, supports:
    - multipart file upload under img_key
    - base64 string or URL in JSON/form data under img_key
    Returns local temp file path.
    """
    # 1) multipart file
    if file is not None:
        if file.filename == "":
            raise HTTPException(status_code=400, detail=f"No file uploaded for '{img_key}'")
        suffix = os.path.splitext(file.filename)[1] or ".jpg"
        tmp = tempfile.NamedTemporaryFile(delete=False, suffix=suffix)
        with open(tmp.name, "wb") as buffer:
            shutil.copyfileobj(file.file, buffer)
        return tmp.name

    # 2) else check JSON or form data for base64 or URL
    data = None
    try:
        data = await request.json()
    except Exception:
        form = await request.form()
        data = dict(form)

    img_value = data.get(img_key)
    if not img_value:
        raise HTTPException(status_code=400, detail=f"'{img_key}' not found in request")

    if is_base64(img_value):
        return save_base64_image(img_value)
    else:
        return await download_image(img_value)


def is_base64(s: str) -> bool:
    try:
        if "," in s:
            s = s.split(",")[1]
        base64.b64decode(s)
        return True
    except Exception:
        return False


def save_base64_image(b64_string: str) -> str:
    if "," in b64_string:
        b64_string = b64_string.split(",")[1]
    binary = base64.b64decode(b64_string)
    tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
    with open(tmp.name, "wb") as f:
        f.write(binary)
    return tmp.name


async def download_image(url: str) -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(url) as resp:
            if resp.status != 200:
                raise HTTPException(status_code=400, detail="Failed to download image from URL")
            tmp = tempfile.NamedTemporaryFile(delete=False, suffix=".jpg")
            content = await resp.read()
            with open(tmp.name, "wb") as f:
                f.write(content)
            return tmp.name


def convert_numpy(obj):
    """
    Recursively convert numpy types to native Python types.
    """
    if isinstance(obj, dict):
        return {k: convert_numpy(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [convert_numpy(i) for i in obj]
    elif isinstance(obj, np.ndarray):
        return obj.tolist()
    elif isinstance(obj, (np.float32, np.float64)):
        return float(obj)
    elif isinstance(obj, (np.int32, np.int64)):
        return int(obj)
    else:
        return obj