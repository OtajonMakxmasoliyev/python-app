from fastapi import FastAPI, HTTPException
from motor.motor_asyncio import AsyncIOMotorClient
from fastapi.responses import StreamingResponse
from bson import ObjectId
import os
from fastapi.encoders import jsonable_encoder
import uvicorn
from create_pdf import create_final_pdf  # PDF yaratish uchun funksiyani import qilish
import json
from datetime import datetime

app = FastAPI()

# MongoDB ulanish sozlamalari
MONGO_URL = os.getenv("MONGO_URL", "mongodb+srv://abbos:M7d2x3STLlUa0XWp@cluster0.qqdwl.mongodb.net/?retryWrites=true&w=majority&appName=Cluster0")
client = AsyncIOMotorClient(MONGO_URL)
db = client["test"]  # Ma'lumotlar bazasi
collection = db["documents"]  # Kolleksiya

@app.on_event("startup")
async def startup_db_client():
    try:
        print("MongoDB connected successfully")
    except Exception as e:
        print(f"MongoDB connection error: {e}")

@app.on_event("shutdown")
async def shutdown_db_client():
    client.close()

def default_serializer(o):
    """Datetime ob'ektlarini JSON formatiga aylantirish uchun default funksiya."""
    if isinstance(o, datetime):
        return o.isoformat()  # ISO formatida qaytarish
    raise TypeError(f'Type {type(o)} not serializable')

# ID orqali ma'lumot olish
@app.get("/document/{doc_id}")
async def get_document_by_id(doc_id: str):
    try:
        obj_id = ObjectId(doc_id)  # ObjectId'ga aylantirish
    except Exception as e:
        raise HTTPException(status_code=400, detail="Noto'g'ri ID formati")

    document = await collection.find_one({"_id": obj_id})  # Hujjatni qidirish
    
    if document:
        document["_id"] = str(document["_id"])  # ObjectId'ni stringga aylantirish
        
        # JSON formatga aylantirish
        json_string = json.dumps(jsonable_encoder(document), default=default_serializer)  
        print(json_string)

        pdf_buffer = create_final_pdf(json_string)  # PDF yaratish
        
        response = StreamingResponse(pdf_buffer, media_type="application/pdf")
        response.headers["Content-Disposition"] = f"attachment; filename=document_{doc_id}.pdf"
        return response
    else:
        raise HTTPException(status_code=404, detail="Hujjat topilmadi")

# Root route
@app.get("/")
async def read_root():
    return {"message": "MongoDB is connected!"}

if __name__ == "__main__":
    # Portni o'rnatish
    PORT = int(os.getenv('PORT', 8000))
    uvicorn.run(app, host="0.0.0.0", port=PORT)
