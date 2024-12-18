from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI(title="LinguaLearn API")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def read_root():
    return {"status": "ok"}

# Import and include routers
try:
    from .routers import process, languages, terms
    app.include_router(process.router)
    app.include_router(languages.router)
    app.include_router(terms.router)
except ImportError as e:
    print(f"Warning: Some routers could not be loaded: {e}")
