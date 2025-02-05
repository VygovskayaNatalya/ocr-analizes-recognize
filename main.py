from fastapi import FastAPI, File, UploadFile, Form, Request, HTTPException
from fastapi.responses import JSONResponse, HTMLResponse
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles 
from fastapi.templating import Jinja2Templates
from fastapi.middleware.cors import CORSMiddleware
from io import BytesIO
import easyocr
import pytesseract
from paddleocr import PaddleOCR
from pydantic import BaseModel
from typing import List
from PIL import Image
import base64
import numpy as np
import time
import uvicorn
import os
from typing import Dict, Any


app = FastAPI()

class OCRRequest(BaseModel):
    file: str  # Строка Base64
    engines: list
    use_gpu: bool

# Здесь 'directory' должен указывать на папку, где находятся static файлы
app.mount("/static", StaticFiles(directory="static"), name="static")

templates = Jinja2Templates(directory="templates")

# Разрешаем запросы CORS от любого источника
origins = ["*"]  # Для простоты можно разрешить доступ со всех источников
app.add_middleware(
    CORSMiddleware,
    allow_origins=origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# @app.get("/")
# async def root():
#     return {"message": "Welcome to the OCR API!"}




@app.get("/", response_class=HTMLResponse)
async def index_page(request: Request):
    # Просто рендерим страницу без параметров engines
    return templates.TemplateResponse("index.html", {"request": request})

@app.post("/ocr")  # Убедитесь, что здесь используется POST
async def ocr(request: OCRRequest):
    try:
        image_data = base64.b64decode(request.file)
        image = Image.open(BytesIO(image_data))
    except Exception as e:
        raise HTTPException(status_code=400, detail=f"Ошибка при декодировании изображения: {str(e)}")
    
    results = []
    
    # Работа с выбранными OCR движками
    if "easyocr" in request.engines:
        reader = easyocr.Reader(['ru'], gpu=request.use_gpu)
        start_time = time.time()
        result = reader.readtext(np.array(image))
        execution_time = time.time() - start_time
        results.append({"engine": "easyocr", "execution_time": f"{execution_time:.2f}", "text": " ".join([r[1] for r in result])})
    
    if "tesseract" in request.engines:
        start_time = time.time()
        result =  pytesseract.image_to_string(image, lang='rus')
        execution_time = time.time() - start_time
        results.append({"engine": "tesseract", "execution_time": f"{execution_time:.2f}", "text": result.replace("\n", "  ")})
    
    if "paddleocr" in request.engines:
        ocr = PaddleOCR(use_angle_cls=True, lang='ru', gpu=request.use_gpu)
        start_time = time.time()
        result = ocr.ocr(np.array(image))
        execution_time = time.time() - start_time
        text_blocks = [(item[1][0], item[1][1]) for sublist in result for item in sublist]
        chunks=[block for block in text_blocks if len(block) > 0]
        results.append({"engine": "paddleocr", "execution_time": f"{execution_time:.2f}", "text": " ".join(chunk[0] for chunk in chunks)})
    
        print(results)
    
    return {"results": results}
    


if __name__ == '__main__':

    uvicorn.run("main:app", host="127.0.0.1", port=int(os.environ.get('PORT', 8000)))

from services.ollama_service import OllamaService

# Add at the beginning of the file with other imports
ollama_service = OllamaService()

async def process_with_ollama(text: str) -> Dict[str, Any]:
    prompt = f"""
    Analyze this medical test data and create a structured response:
    {text}
    
    Format the data into these categories:
    1. Parameter name
    2. Value
    3. Units
    4. Normal range
    
    Highlight any abnormal values.
    """
    
    response = requests.post(
        OLLAMA_URL,
        json={
            "model": "llama2",
            "prompt": prompt,
            "stream": False,
            "options": {
                "temperature": 0.1,
                "num_predict": 1024
            }
        }
    )
    
    return response.json()

@app.post("/analyze_medical")
async def analyze_medical_data(request: Request):
    data = await request.json()
    text = data.get("text", "")
    
    analysis_result = await process_with_ollama(text)
    return JSONResponse(content=analysis_result)

import aiohttp
from aiohttp import ClientSession
from typing import Dict, Any

@app.post("/structure_analysis")
async def structure_analysis(request: Request):
    try:
        data = await request.json()
        ocr_text = data.get("text", "")
        
        async with aiohttp.ClientSession() as session:
            async with session.post("http://localhost:11434/api/generate", json={
                "model": "llama2",
                "prompt": ocr_text,
                "stream": False
            }) as response:
                result = await response.json()
                formatted_table = """
                    <table>
                        <tr>
                            <th>Параметр</th>
                            <th>Значение</th>
                            <th>Единицы</th>
                            <th>Норма</th>
                        </tr>
                        <tr>
                            <td>{}</td>
                            <td></td>
                            <td></td>
                            <td></td>
                        </tr>
                    </table>
                """.format(result.get('response', ''))
                
                return JSONResponse(content={
                    "structured_analysis": formatted_table
                })
                
    except Exception as e:
        return JSONResponse(
            content={"error": str(e), "details": "Ошибка при анализе текста"},
            status_code=500
        )
@app.get("/analysis", response_class=HTMLResponse)
async def analysis_page(request: Request):
    return templates.TemplateResponse("analysis.html", {
        "request": request,
    })


