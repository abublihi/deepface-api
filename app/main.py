# main.py
import os
from typing import Optional
from fastapi import FastAPI, Request, UploadFile, File, Query
from deepface import DeepFace
from app.utils import extract_image_from_request, convert_numpy
from fastapi import HTTPException

app = FastAPI(title="DeepFace API with flexible image input")

def parse_bool(value: Optional[str], default: bool) -> bool:
    if value is None:
        return default
    return value.lower() in ["true", "1", "yes"]

@app.post("/represent")
async def represent(
    request: Request,
    img: Optional[UploadFile] = File(None),
    model_name: str = Query("SFace", description="DeepFace model"),
    detector_backend: str = Query("yunet", description="Face detector backend"),
    enforce_detection: Optional[str] = Query("true", description="Enforce face detection (true/false)"),
    align: Optional[str] = Query("true", description="Align face before processing (true/false)"),
    anti_spoofing: Optional[str] = Query("true", description="Enable anti_spoofing (true/false)"),
    max_faces: Optional[int] = Query(None, description="Set a limit on the number of faces to be processed (default is None)")
):
    enforce_detection_bool = parse_bool(enforce_detection, True)
    align_bool = parse_bool(align, True)
    anti_spoofing_bool = parse_bool(anti_spoofing, True)

    img_path = None

    try:
        img_path = await extract_image_from_request(request, "img", img)

        try:
            result = DeepFace.represent(
                img_path=img_path,
                model_name=model_name,
                detector_backend=detector_backend,
                enforce_detection=enforce_detection_bool,
                align=align_bool,
                anti_spoofing=anti_spoofing_bool,
                max_faces=max_faces
            )
        except Exception as e:
            if "spoof detected" in str(e).lower():
                raise HTTPException(
                    status_code=422,
                    detail={
                        "spoofed": True,
                        "message":"Spoofed image detected during representation extraction. you can disable anti spoofing by setting `anti_spoofing=false`"
                    },
                )
            raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

        return result

    finally:
        if img_path and os.path.exists(img_path):
            os.remove(img_path)



@app.post("/analyze")
async def analyze(
    request: Request,
    img: Optional[UploadFile] = File(None),
    actions: str = Query("age,gender,race,emotion", description="Comma separated analysis actions"),
    detector_backend: str = Query("opencv", description="Face detector backend"),
    enforce_detection: Optional[str] = Query("true", description="Enforce face detection (true/false)"),
    align: Optional[str] = Query("true", description="Align face before processing (true/false)"),
    anti_spoofing: Optional[str] = Query("true", description="Enable anti_spoofing (true/false)"),
):
    enforce_detection_bool = parse_bool(enforce_detection, True)
    align_bool = parse_bool(align, True)
    action_list = [a.strip() for a in actions.split(",") if a.strip()]
    anti_spoofing_bool = parse_bool(anti_spoofing, True)

    image_path = None
    try:
        image_path = await extract_image_from_request(request, "img", img)
        try:
            result = DeepFace.analyze(
                img_path=image_path,
                actions=action_list,
                detector_backend=detector_backend,
                enforce_detection=enforce_detection_bool,
                align=align_bool,
                anti_spoofing=anti_spoofing_bool
            )
        except Exception as e:
            if "spoof detected" in str(e).lower():
                raise HTTPException(
                    status_code=422,
                    detail={
                        "spoofed": True,
                        "message":"Spoofed image detected during representation extraction. you can disable anti spoofing by setting `anti_spoofing=false`"
                    },
                )
            raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")
        
        return convert_numpy(result)

    finally:
        if image_path and os.path.exists(image_path):
            os.remove(image_path)


@app.post("/verify")
async def verify(
    request: Request,
    img1: Optional[UploadFile] = File(None),
    img2: Optional[UploadFile] = File(None),
    model_name: str = Query("SFace", description="DeepFace model"),
    detector_backend: str = Query("yunet", description="Face detector backend"),
    distance_metric: str = Query("cosine", description="Distance metric"),
    enforce_detection: Optional[str] = Query("true", description="Enforce face detection (true/false)"),
    align: Optional[str] = Query("true", description="Align face before processing (true/false)"),
    anti_spoofing: Optional[str] = Query("true", description="Enable anti_spoofing (true/false)"),
):
    enforce_detection_bool = parse_bool(enforce_detection, True)
    align_bool = parse_bool(align, True)
    anti_spoofing_bool = parse_bool(anti_spoofing, True)

    img1_path, img2_path = None, None
    try:
        img1_path = await extract_image_from_request(request, "img1", img1)
        img2_path = await extract_image_from_request(request, "img2", img2)

        try:
            result = DeepFace.verify(
                img1_path=img1_path,
                img2_path=img2_path,
                model_name=model_name,
                detector_backend=detector_backend,
                distance_metric=distance_metric,
                enforce_detection=enforce_detection_bool,
                align=align_bool,
                anti_spoofing=anti_spoofing_bool,
            )
        except Exception as e:
            # Deepface will only throw an error "Exception while processing" without giving us a hit if it was spoofed
            # if "spoof detected" in str(e).lower():
            #     raise HTTPException(
            #         status_code=422,
            #         detail={
            #             "spoofed": True,
            #             "message":"Spoofed image detected during representation extraction. you can disable anti spoofing by setting `anti_spoofing=false`"
            #         },
            #     )
            raise HTTPException(status_code=500, detail=f"Internal error: {str(e)}")

        return result
        
    finally:
        for path in [img1_path, img2_path]:
            if path and os.path.exists(path):
                os.remove(path)
