from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from routers import analyze, evaluate, predict, train

app = FastAPI(
    title="ML Classical Service",
    version="0.1.0",
)

# Enable CORS - Allow all origins for development
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins in development
    allow_credentials=False,  # Set to False when using allow_origins=["*"]
    allow_methods=["*"],
    allow_headers=["*"],
)


@app.get("/")
def root():
    return {"service": "ml-classical-service", "status": "ok"}


@app.get("/health")
def health():
    return {"status": "healthy"}


app.include_router(analyze.router, prefix="/analyze", tags=["analyze"])
app.include_router(train.router, prefix="/train", tags=["train"])
app.include_router(predict.router, prefix="/predict", tags=["predict"])
app.include_router(evaluate.router, prefix="/evaluate", tags=["evaluate"])
