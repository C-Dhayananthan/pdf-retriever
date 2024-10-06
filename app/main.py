from fastapi import FastAPI, Request
import time
from app.routers.router import router
from app.utilities import dc_logger 
from fastapi.middleware.cors import CORSMiddleware
from fastapi.middleware.trustedhost import TrustedHostMiddleware
from fastapi.middleware.gzip import GZipMiddleware
from app.middlewares.contextmiddleware import RequestContextMiddleware


logger = dc_logger.LoggerAdap(dc_logger.get_logger(__name__),{"vectordb":"faiss"})

app = FastAPI()

@app.get("/")
async def root():
    return {"Server is On":"Status Healthy"}

app.add_middleware(TrustedHostMiddleware, allowed_hosts=["*"])
app.add_middleware(GZipMiddleware, minimum_size=1000)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

app.add_middleware(RequestContextMiddleware)


@app.middleware("http")
async def add_process_time_header(request: Request, call_next):
    start_time = time.time()
    response = await call_next(request)
    process_time = time.time() - start_time
    response.headers["X-Process-Time"] = str(process_time)
    logger.info("Process Time: " + str(process_time))
    return response

subapi = FastAPI()
subapi.include_router(router)
app.mount("/vectordb/faiss", subapi)
logger.info("main intitialized")