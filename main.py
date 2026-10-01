import threading
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from api.auth_routes import router as auth_router
from api.network_routes import router as network_router
from ai_analysis.flow_collector import FlowCollector

app = FastAPI(title="NAC & AI Security API", version="1.0.0")

# CORS Middleware KESİNLİKLE BURAYA (Router'lardan Önce) EKLENMELİDİR
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=False,
    allow_methods=["*"],
    allow_headers=["*"],
)

# API rotalarını sisteme entegre et
app.include_router(auth_router, prefix="/api/auth", tags=["Authentication"])
app.include_router(network_router, prefix="/api/network", tags=["Network Operations"])

# Arka planda çalışacak AI Network Flow otomasyonu
def run_ai_automation():
    collector = FlowCollector()
    collector.start_monitoring()


@app.on_event("startup")
def startup_event():
    """FastAPI sunucusu ayağa kalktığında otomatik olarak çalışır."""
    print("API Sunucusu başlatılıyor...")

    # Ana API'yi kilitlememek için otomasyonu ayrı bir Thread (iş parçacığı) üzerinde başlat
    ai_thread = threading.Thread(target=run_ai_automation, daemon=True)
    ai_thread.start()


@app.get("/")
def root():
    return {
        "status": "ok",
        "message": "NAC Backend ve AI Ağ Akışı İzleme API'si çalışıyor."
    }