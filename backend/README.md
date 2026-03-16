# AI鏅鸿兘鑿滆氨鐢熸垚骞冲彴 - 鍚庣

鍩轰簬FastAPI鐨凙I鏅鸿兘鑿滆氨鐢熸垚骞冲彴鍚庣鏈嶅姟銆?

## 鎶€鏈爤

- Python 3.10+
- FastAPI 0.104+
- SQLAlchemy 2.0+
- Pydantic 2.5+
- Uvicorn

## 椤圭洰缁撴瀯

```
backend/
鈹溾攢鈹€ app/
鈹?  鈹溾攢鈹€ core/           # 鏍稿績閰嶇疆鍜屾暟鎹簱
鈹?  鈹溾攢鈹€ models/         # SQLAlchemy鏁版嵁妯″瀷
鈹?  鈹溾攢鈹€ schemas/        # Pydantic妯″瀷
鈹?  鈹溾攢鈹€ routers/        # API璺敱
鈹?  鈹溾攢鈹€ services/       # 涓氬姟閫昏緫灞?
鈹?  鈹斺攢鈹€ repositories/   # 鏁版嵁璁块棶灞?
鈹溾攢鈹€ main.py            # 搴旂敤鍏ュ彛
鈹溾攢鈹€ requirements.txt   # 渚濊禆鍖?
鈹斺攢鈹€ .env.example      # 鐜鍙橀噺绀轰緥
```

## 蹇€熷紑濮?

### 1. 瀹夎渚濊禆

```bash
cd backend
pip install -r requirements.txt
```

### 2. 閰嶇疆鐜鍙橀噺

澶嶅埗 `.env.example` 涓?`.env` 骞跺～鍐欓厤缃細

```bash
cp .env.example .env
```

缂栬緫 `.env` 鏂囦欢锛屽～鍐欒眴鍖匒PI瀵嗛挜绛夐厤缃€?

### 3. 杩愯寮€鍙戞湇鍔″櫒

```bash
python main.py
```

鎴栦娇鐢╱vicorn锛?

```bash
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

### 4. 璁块棶API鏂囨。

- Swagger UI: http://localhost:8000/docs
- ReDoc: http://localhost:8000/redoc

## API绔偣

### 鍋ュ悍妫€鏌?
- `GET /` - 鏍硅矾寰?
- `GET /health` - 鍋ュ悍妫€鏌?

### 鑿滆氨鐩稿叧
- `POST /api/recipes/generate` - 鐢熸垚鑿滆氨
- `POST /api/recipes/save` - 淇濆瓨鑿滆氨
- `GET /api/recipes/history` - 鑾峰彇鍘嗗彶鑿滆氨
- `GET /api/recipes/{recipe_id}` - 鑾峰彇鑿滆氨璇︽儏

### 鍥剧墖鐩稿叧
- `POST /api/images/recognize` - 璇嗗埆鍥剧墖涓殑椋熸潗

## 寮€鍙戣鏄?

1. 鎵€鏈堿PI璺敱鍦?`app/routers/` 鐩綍涓?
2. 涓氬姟閫昏緫鍦?`app/services/` 鐩綍涓?
3. 鏁版嵁璁块棶鍦?`app/repositories/` 鐩綍涓?
4. 鏁版嵁妯″瀷鍦?`app/models/` 鐩綍涓?
5. 璇锋眰/鍝嶅簲妯″瀷鍦?`app/schemas/` 鐩綍涓?

## 鐜鍙橀噺璇存槑

- `LLM_API_KEY`: 璞嗗寘API瀵嗛挜
- `LLM_BASE_URL`: 璞嗗寘API鍩虹URL
- `DATABASE_URL`: 鏁版嵁搴撹繛鎺RL
- `UPLOAD_DIR`: 鏂囦欢涓婁紶鐩綍
- `SECRET_KEY`: 搴旂敤瀵嗛挜
- `CORS_ORIGINS`: 鍏佽鐨勮法鍩熸簮


