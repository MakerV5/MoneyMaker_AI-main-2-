from pathlib import Path
import json
import logging
import pandas as pd
from fastapi import FastAPI, WebSocket, Depends, Request
from fastapi.responses import HTMLResponse
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

templates = Jinja2Templates(directory=Path(__file__).parent / 'templates')

strategy = None

def init(app: FastAPI, data_dir: Path, asset: str, users: dict):
    global strategy, USERS
    USERS = users
    strategy = TradingStrategy(asset, data_dir)
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
