from pathlib import Path
import json
import logging
import pandas as pd
from fastapi import FastAPI, WebSocket, Depends, Request, UploadFile, File
from fastapi.responses import HTMLResponse, JSONResponse
from fastapi.security import HTTPBasic, HTTPBasicCredentials
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from starlette.websockets import WebSocketDisconnect
from src.strategy import TradingStrategy

logger = logging.getLogger(__name__)

security = HTTPBasic()

USERS = {}

def get_current_user(credentials: HTTPBasicCredentials = Depends(security)):
    correct_password = USERS.get(credentials.username)
    if not correct_password or credentials.password != correct_password:
        raise Exception('Unauthorized')
    return credentials.username

app = FastAPI()
app.mount('/static', StaticFiles(directory=Path(__file__).parent / 'static'), name='static')


@app.middleware('http')
async def log_requests(request: Request, call_next):
    logger.info('Request from %s to %s', request.client.host, request.url.path)
    response = await call_next(request)
    return response

templates = Jinja2Templates(directory=Path(__file__).parent / 'templates')

strategy = None
DATA_DIR = Path('data')

def init(app: FastAPI, data_dir: Path, asset: str, users: dict):
    global strategy, USERS, DATA_DIR
    USERS = users
    DATA_DIR = Path(data_dir)
    strategy = TradingStrategy(asset, DATA_DIR)
    strategy.train()
    logger.info('Strategy trained for %s', asset)

@app.get('/')
async def index(request: Request, user: str = Depends(get_current_user)):
    return templates.TemplateResponse('index.html', { 'request': request })

@app.websocket('/ws')
async def websocket_endpoint(ws: WebSocket):
    await ws.accept()
    while True:
        try:
            df = strategy.load_data()
            signal = strategy.predict_signal(df)
            await ws.send_text(json.dumps({'signal': signal}))
        except WebSocketDisconnect:
            break
        except Exception as e:
            logger.exception(e)
            break


@app.get('/api/data')
async def get_data(symbol: str = 'BTCUSDT', user: str = Depends(get_current_user)):
    path = DATA_DIR / f"{symbol}.csv"
    if not path.exists():
        return JSONResponse(status_code=404, content={'error': 'symbol not found'})
    df = pd.read_csv(path).tail(200)
    return df.to_dict(orient='records')


@app.get('/backtest', response_class=HTMLResponse)
async def backtest_form(request: Request, user: str = Depends(get_current_user)):
    return templates.TemplateResponse('backtest.html', {'request': request})


@app.post('/backtest', response_class=HTMLResponse)
async def run_backtest_view(request: Request, file: UploadFile = File(...), user: str = Depends(get_current_user)):
    content = await file.read()
    temp = DATA_DIR / 'upload.csv'
    temp.write_bytes(content)
    from backtest import run_backtest
    profit, dd, out = run_backtest(temp)
    return templates.TemplateResponse('backtest.html', {'request': request, 'profit': profit, 'drawdown': dd, 'plot': out.name})
