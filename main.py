# -*- coding: utf-8 -*-
# ═══════════════════════════════════════════════════════════════════
#  TEAM RBC — Squad Bot (Create → Invite → Accept → PK → In-Game)
# ═══════════════════════════════════════════════════════════════════
import sys, asyncio, httpx, random, json, socket, struct, time, os, uuid
import itertools, secrets, traceback, base64
from contextvars import ContextVar
_squad_log_id_context = ContextVar("squad_log_id_context", default=None)
from datetime import datetime
from typing import Dict, List, Optional, Tuple, Any

if sys.platform == "win32":
    try:
        if hasattr(sys.stdout, 'reconfigure'):
            sys.stdout.reconfigure(encoding='utf-8', errors='replace')
            sys.stderr.reconfigure(encoding='utf-8', errors='replace')
    except Exception: pass

from google_play_scraper import app as play_scraper
from Crypto.Cipher import AES
from Crypto.Util.Padding import pad
from protobuf_decoder.protobuf_decoder import Parser
from message_ids import MESSAGE_ID_TO_NAME
import RbcTeam_pb2
import RbcFF_pb2
import thunderFF_pb2


# ═════════════════════ EMBEDDED DASHBOARD ═════════════════════
from aiohttp import web

INDEX_HTML = r"""<!DOCTYPE html>
<html lang="en" data-theme="neon">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width, initial-scale=1.0">
<title>CODEXGOJO — Level Up Bot</title>
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link href="https://fonts.googleapis.com/css2?family=Orbitron:wght@500;700;900&family=Rajdhani:wght@400;500;600;700&family=JetBrains+Mono:wght@400;500;700&display=swap" rel="stylesheet">
<link rel="stylesheet" href="https://cdnjs.cloudflare.com/ajax/libs/font-awesome/6.4.0/css/all.min.css">
<style>
:root{
  --void:#05020a;--bg:#080413;--panel:#0d0720;--panel-2:#130a2b;--panel-3:#1b0f3a;
  --border:#261548;--border-hi:#3b2270;
  --txt:#f1ecff;--txt-2:#b3a6d6;--txt-3:#75679c;
  --a-rgb:255,43,214;--b-rgb:0,240,255;--ok-rgb:182,255,0;--warn-rgb:255,184,0;--bad-rgb:255,59,92;
  --a:rgb(var(--a-rgb));--b:rgb(var(--b-rgb));--ok:rgb(var(--ok-rgb));--warn:rgb(var(--warn-rgb));--bad:rgb(var(--bad-rgb));
  --r:14px;--r-sm:9px;
  --display:'Orbitron',system-ui,sans-serif;--ui:'Rajdhani',system-ui,sans-serif;--mono:'JetBrains Mono',ui-monospace,monospace;
}
html[data-theme="blood"]{--void:#090203;--bg:#0f0405;--panel:#1a0709;--panel-2:#240a0d;--panel-3:#300e12;--border:#4a151b;--border-hi:#6e1f28;--a-rgb:255,34,52;--b-rgb:255,138,0;--txt-3:#9a6a70;--txt-2:#d4aeb2;}
html[data-theme="matrix"]{--void:#010603;--bg:#020b05;--panel:#04140a;--panel-2:#071d0f;--panel-3:#0a2814;--border:#0f3a1d;--border-hi:#17572b;--a-rgb:0,255,102;--b-rgb:160,255,0;--ok-rgb:0,255,170;--txt:#e4ffe9;--txt-2:#9fd3ad;--txt-3:#5a8a68;}
html[data-theme="ice"]{--void:#02060c;--bg:#040c18;--panel:#071427;--panel-2:#0a1c36;--panel-3:#0f2748;--border:#143258;--border-hi:#1f4a82;--a-rgb:56,189,255;--b-rgb:170,120,255;--txt-3:#6a86ad;--txt-2:#a9c0e0;}
html.rainbow{animation:hue 4s linear infinite;}
@keyframes hue{to{filter:hue-rotate(360deg);}}

*{box-sizing:border-box;margin:0;padding:0;}
html,body{overflow-x:hidden;}
body{font-family:var(--ui);background:var(--void);color:var(--txt);font-size:15px;line-height:1.45;min-height:100vh;padding:22px 22px 64px;-webkit-font-smoothing:antialiased;position:relative;}
body::before{content:"";position:fixed;inset:0;z-index:-2;pointer-events:none;
  background:radial-gradient(ellipse 70% 45% at 50% -10%,rgba(var(--a-rgb),.22),transparent 62%),
             radial-gradient(ellipse 45% 40% at 100% 100%,rgba(var(--b-rgb),.12),transparent 60%),
             radial-gradient(ellipse 40% 35% at 0% 80%,rgba(var(--a-rgb),.08),transparent 60%);}
body::after{content:"";position:fixed;inset:0;z-index:50;pointer-events:none;opacity:.5;mix-blend-mode:overlay;
  background:repeating-linear-gradient(0deg,rgba(0,0,0,.28) 0,rgba(0,0,0,.28) 1px,transparent 1px,transparent 3px);}
body.nofx::after,body.nofx #bg-canvas,body.nofx .cursor-glow{display:none;}
#bg-canvas{position:fixed;inset:0;z-index:-1;width:100%;height:100%;opacity:.35;pointer-events:none;}
.cursor-glow{position:fixed;width:420px;height:420px;border-radius:50%;pointer-events:none;z-index:-1;left:0;top:0;
  background:radial-gradient(circle,rgba(var(--a-rgb),.16),transparent 65%);transform:translate(-50%,-50%);transition:opacity .3s;}
.container{max-width:1440px;margin:0 auto;position:relative;}
button{font-family:inherit;}
:focus-visible{outline:2px solid var(--b);outline-offset:2px;}

/* TOPBAR */
.topbar{display:flex;align-items:center;justify-content:space-between;gap:20px;flex-wrap:wrap;padding:16px 22px;margin-bottom:18px;
  background:linear-gradient(180deg,var(--panel),var(--bg));border:1px solid var(--border-hi);border-radius:var(--r);position:relative;overflow:hidden;
  box-shadow:0 0 0 1px rgba(var(--a-rgb),.08),0 18px 50px -24px rgba(var(--a-rgb),.6);}
.topbar::before{content:"";position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,transparent,var(--a),var(--b),transparent);background-size:60% 100%;background-repeat:no-repeat;animation:slideLine 3s ease-in-out infinite;}
@keyframes slideLine{0%{background-position:-60% 0;}100%{background-position:160% 0;}}
.brand{display:flex;align-items:center;gap:16px;}
.logo{position:relative;width:54px;height:54px;border-radius:14px;display:grid;place-items:center;font-family:var(--display);font-weight:900;font-size:24px;color:#fff;flex-shrink:0;
  background:conic-gradient(from 180deg,var(--a),var(--b),var(--a));box-shadow:0 0 28px -4px rgba(var(--a-rgb),.9),inset 0 0 0 2px rgba(255,255,255,.25);animation:spinGlow 6s linear infinite;}
.logo span{position:absolute;inset:3px;border-radius:11px;background:var(--void);display:grid;place-items:center;}
.logo b{background:linear-gradient(135deg,var(--a),var(--b));-webkit-background-clip:text;background-clip:text;color:transparent;}
@keyframes spinGlow{50%{box-shadow:0 0 40px 2px rgba(var(--b-rgb),.8),inset 0 0 0 2px rgba(255,255,255,.25);}}
.glitch{font-family:var(--display);font-weight:900;font-size:26px;letter-spacing:.06em;position:relative;display:inline-block;color:var(--txt);text-shadow:0 0 18px rgba(var(--a-rgb),.7);}
.glitch::before,.glitch::after{content:attr(data-text);position:absolute;inset:0;overflow:hidden;}
.glitch::before{color:var(--b);transform:translate(-2px,0);clip-path:inset(0 0 60% 0);animation:gl1 3.2s infinite steps(1);}
.glitch::after{color:var(--a);transform:translate(2px,0);clip-path:inset(60% 0 0 0);animation:gl2 3.2s infinite steps(1);}
@keyframes gl1{0%,88%,100%{clip-path:inset(0 0 100% 0);}90%{clip-path:inset(10% 0 55% 0);transform:translate(-4px,0);}94%{clip-path:inset(40% 0 20% 0);transform:translate(3px,0);}}
@keyframes gl2{0%,86%,100%{clip-path:inset(100% 0 0 0);}89%{clip-path:inset(55% 0 12% 0);transform:translate(4px,0);}95%{clip-path:inset(20% 0 50% 0);transform:translate(-3px,0);}}
.tagline{font-size:13px;color:var(--txt-3);margin-top:3px;display:flex;align-items:center;gap:10px;flex-wrap:wrap;font-weight:500;letter-spacing:.04em;}
.pill{display:inline-flex;align-items:center;gap:7px;padding:3px 10px;border-radius:99px;font-size:12px;font-weight:700;letter-spacing:.06em;border:1px solid var(--border-hi);background:rgba(255,255,255,.03);}
.pill i{font-size:7px;}
.pill.live{color:var(--ok);border-color:rgba(var(--ok-rgb),.4);background:rgba(var(--ok-rgb),.08);}
.pill.live i{animation:blink 1.4s infinite;}
.pill.demo{color:var(--warn);border-color:rgba(var(--warn-rgb),.45);background:rgba(var(--warn-rgb),.08);}
.pill.off{color:var(--bad);border-color:rgba(var(--bad-rgb),.45);background:rgba(var(--bad-rgb),.08);}
@keyframes blink{50%{opacity:.25;}}
.clock{font-family:var(--mono);font-size:12px;color:var(--txt-2);}
.actions{display:flex;gap:9px;flex-wrap:wrap;align-items:center;}
.btn{position:relative;display:inline-flex;align-items:center;gap:8px;padding:9px 16px;border-radius:var(--r-sm);font-size:14px;font-weight:700;letter-spacing:.04em;cursor:pointer;border:1px solid transparent;transition:transform .18s,box-shadow .18s,border-color .18s,background .18s;white-space:nowrap;color:var(--txt);}
.btn i{font-size:12px;}
.btn-ghost{background:rgba(255,255,255,.02);color:var(--txt-2);border-color:var(--border-hi);}
.btn-ghost:hover{background:var(--panel-3);color:var(--txt);border-color:var(--a);transform:translateY(-1px);}
.btn-primary{background:linear-gradient(135deg,var(--a),rgba(var(--a-rgb),.55) 55%,var(--b));color:#fff;text-shadow:0 1px 6px rgba(0,0,0,.5);box-shadow:0 6px 24px -6px rgba(var(--a-rgb),.9),inset 0 1px 0 rgba(255,255,255,.25);}
.btn-primary:hover{transform:translateY(-2px);box-shadow:0 10px 30px -6px rgba(var(--a-rgb),1);}
.btn:disabled{opacity:.5;cursor:not-allowed;transform:none;}
.kbd{font-family:var(--mono);font-size:10.5px;padding:1px 6px;border-radius:5px;border:1px solid var(--border-hi);color:var(--txt-3);background:var(--bg);}

/* STATS */
.stats{display:grid;grid-template-columns:repeat(4,1fr);gap:14px;margin-bottom:18px;}
@media(max-width:1000px){.stats{grid-template-columns:repeat(2,1fr);}}
@media(max-width:520px){.stats{grid-template-columns:1fr;}}
.stat{position:relative;background:linear-gradient(180deg,var(--panel),var(--bg));border:1px solid var(--border);border-radius:var(--r);padding:16px 18px;display:flex;flex-direction:column;gap:8px;overflow:hidden;transition:transform .25s,border-color .25s,box-shadow .25s;}
.stat::before{content:"";position:absolute;inset:0;background:radial-gradient(220px circle at var(--mx,50%) var(--my,0%),rgba(var(--a-rgb),.16),transparent 60%);opacity:0;transition:opacity .25s;pointer-events:none;}
.stat:hover{transform:translateY(-3px);border-color:var(--a);box-shadow:0 14px 40px -18px rgba(var(--a-rgb),.9);}
.stat:hover::before{opacity:1;}
.stat-head{display:flex;align-items:center;justify-content:space-between;}
.stat-label{font-size:12.5px;font-weight:700;color:var(--txt-3);letter-spacing:.1em;text-transform:uppercase;}
.stat-icon{width:32px;height:32px;border-radius:9px;display:grid;place-items:center;font-size:13px;background:rgba(var(--a-rgb),.14);color:var(--a);}
.stat-icon.b{background:rgba(var(--b-rgb),.14);color:var(--b);}
.stat-icon.ok{background:rgba(var(--ok-rgb),.14);color:var(--ok);}
.stat-icon.warn{background:rgba(var(--warn-rgb),.14);color:var(--warn);}
.stat-value{font-family:var(--display);font-size:27px;font-weight:700;line-height:1.1;font-variant-numeric:tabular-nums;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.stat-value.mono{font-size:23px;}
.stat-value .unit{font-family:var(--ui);font-size:13px;font-weight:600;color:var(--txt-3);margin-left:5px;}
.stat-foot{font-size:12.5px;color:var(--txt-3);}

/* CHART */
.panel{background:linear-gradient(180deg,var(--panel),var(--bg));border:1px solid var(--border);border-radius:var(--r);overflow:hidden;}
.panel-head{display:flex;align-items:center;justify-content:space-between;gap:12px;flex-wrap:wrap;padding:14px 20px;border-bottom:1px solid var(--border);background:rgba(255,255,255,.012);}
.panel-title{font-family:var(--display);font-size:13px;font-weight:700;letter-spacing:.08em;display:flex;align-items:center;gap:10px;}
.panel-title i{color:var(--a);}
.panel-hint{font-size:12.5px;color:var(--txt-3);display:flex;align-items:center;gap:8px;}
.chart-wrap{padding:14px 18px 10px;position:relative;}
#chart{width:100%;height:150px;display:block;}
.chart-meta{display:flex;gap:18px;flex-wrap:wrap;font-size:12.5px;color:var(--txt-3);padding:0 20px 14px;font-family:var(--mono);}
.chart-meta b{color:var(--b);font-weight:700;}
.mb{margin-bottom:18px;}

/* TOOLBAR */
.toolbar{display:flex;gap:10px;flex-wrap:wrap;align-items:center;padding:12px 14px;border-bottom:1px solid var(--border);}
.search{position:relative;flex:1 1 180px;min-width:150px;}
.search i{position:absolute;left:12px;top:50%;transform:translateY(-50%);font-size:12px;color:var(--txt-3);}
.input,select.input{width:100%;background:var(--void);border:1px solid var(--border-hi);border-radius:var(--r-sm);padding:9px 12px;color:var(--txt);font-size:14px;font-family:var(--ui);font-weight:500;outline:none;transition:border-color .2s,box-shadow .2s;}
.search .input{padding-left:34px;}
textarea.input{resize:vertical;min-height:90px;font-family:var(--mono);font-size:12px;}
.input:focus{border-color:var(--a);box-shadow:0 0 0 3px rgba(var(--a-rgb),.18);}
.input::placeholder{color:var(--txt-3);}
select.input{width:auto;cursor:pointer;}
.chips{display:flex;gap:6px;flex-wrap:wrap;}
.chip{padding:5px 11px;border-radius:99px;font-size:12.5px;font-weight:700;letter-spacing:.05em;cursor:pointer;border:1px solid var(--border-hi);background:transparent;color:var(--txt-3);transition:all .18s;}
.chip:hover{color:var(--txt);border-color:var(--a);}
.chip.on{background:rgba(var(--a-rgb),.18);color:var(--txt);border-color:var(--a);box-shadow:0 0 14px -4px rgba(var(--a-rgb),.8);}
.seg{display:inline-flex;border:1px solid var(--border-hi);border-radius:var(--r-sm);overflow:hidden;}
.seg button{background:transparent;border:0;color:var(--txt-3);padding:8px 11px;cursor:pointer;font-size:12px;}
.seg button.on{background:rgba(var(--a-rgb),.2);color:var(--txt);}

/* ACCOUNTS */
.layout{display:grid;grid-template-columns:1.55fr 1fr;gap:18px;align-items:start;}
@media(max-width:1100px){.layout{grid-template-columns:1fr;}}
.accounts{padding:12px;display:grid;grid-template-columns:repeat(auto-fill,minmax(310px,1fr));gap:12px;}
.accounts.list{grid-template-columns:1fr;}
.account{position:relative;padding:16px 18px;border:1px solid var(--border);border-radius:var(--r);background:var(--panel-2);overflow:hidden;transition:border-color .25s,transform .25s,box-shadow .25s;}
.account::before{content:"";position:absolute;inset:0;background:radial-gradient(240px circle at var(--mx,50%) var(--my,0%),rgba(var(--a-rgb),.17),transparent 60%);opacity:0;transition:opacity .25s;pointer-events:none;}
.account::after{content:"";position:absolute;left:0;top:0;bottom:0;width:3px;background:linear-gradient(180deg,var(--a),var(--b));}
.account:hover{border-color:var(--a);transform:translateY(-2px);box-shadow:0 14px 40px -20px rgba(var(--a-rgb),.9);}
.account:hover::before{opacity:1;}
.account.new{animation:enter .5s cubic-bezier(.2,.9,.3,1.2);}
.account.lvup{animation:lvup 1.2s ease;}
@keyframes enter{from{opacity:0;transform:scale(.92) translateY(14px);}}
@keyframes lvup{0%,100%{box-shadow:none;}30%{box-shadow:0 0 0 2px var(--ok),0 0 44px rgba(var(--ok-rgb),.6);}}
.acc-row{display:flex;align-items:center;justify-content:space-between;gap:10px;margin-bottom:12px;}
.acc-id{display:flex;align-items:center;gap:12px;min-width:0;}
.acc-avatar{position:relative;width:42px;height:42px;border-radius:11px;flex-shrink:0;display:grid;place-items:center;font-size:16px;color:var(--tier,var(--a));background:linear-gradient(135deg,var(--panel-3),var(--border-hi));border:1px solid var(--tier,var(--border-hi));box-shadow:0 0 16px -4px var(--tier,transparent);}
.acc-avatar::after{content:"";position:absolute;right:-3px;bottom:-3px;width:11px;height:11px;border-radius:50%;background:var(--ok);border:2px solid var(--panel-2);}
.acc-meta{min-width:0;}
.acc-name{font-size:16px;font-weight:700;display:flex;align-items:center;gap:8px;white-space:nowrap;overflow:hidden;text-overflow:ellipsis;}
.badge{font-size:10.5px;font-weight:700;letter-spacing:.08em;padding:1px 7px;border-radius:5px;border:1px solid rgba(var(--a-rgb),.35);color:var(--a);background:rgba(var(--a-rgb),.12);}
.badge.tier{color:var(--tier);border-color:var(--tier);background:transparent;}
.acc-uid{font-size:12px;color:var(--txt-3);font-family:var(--mono);margin-top:2px;cursor:pointer;}
.acc-uid:hover{color:var(--b);}
.status{display:inline-flex;align-items:center;gap:6px;font-size:12.5px;font-weight:700;padding:4px 10px;border-radius:7px;white-space:nowrap;}
.status::before{content:"";width:6px;height:6px;border-radius:50%;background:currentColor;}
.status.online{background:rgba(var(--ok-rgb),.1);color:var(--ok);}
.status.match{background:rgba(var(--a-rgb),.14);color:var(--a);border:1px solid rgba(var(--a-rgb),.4);}
.status.match::before{animation:blink 1s infinite;box-shadow:0 0 10px currentColor;}
.status.searching{background:rgba(var(--warn-rgb),.1);color:var(--warn);}
.status.error{background:rgba(var(--bad-rgb),.12);color:var(--bad);}
.status.connecting{background:rgba(255,255,255,.05);color:var(--txt-2);}
.exp-grid{display:grid;grid-template-columns:repeat(4,1fr);gap:1px;background:var(--border);border:1px solid var(--border);border-radius:var(--r-sm);overflow:hidden;margin-bottom:12px;}
.exp-cell{background:var(--void);padding:9px 11px;}
.exp-label{font-size:10.5px;font-weight:700;color:var(--txt-3);letter-spacing:.09em;text-transform:uppercase;margin-bottom:3px;}
.exp-value{font-size:13px;font-weight:700;font-family:var(--mono);font-variant-numeric:tabular-nums;white-space:nowrap;}
.exp-value.green{color:var(--ok);}
.exp-value.cyan{color:var(--b);}
.progress-head{display:flex;justify-content:space-between;font-size:13px;margin-bottom:6px;color:var(--txt-2);}
.progress-head .lv{color:var(--txt);font-weight:700;}
.progress-track{height:7px;background:var(--void);border:1px solid var(--border);border-radius:5px;overflow:hidden;}
.progress-fill{height:100%;border-radius:5px;background:linear-gradient(90deg,var(--a),var(--b));background-size:200% 100%;animation:flow 2.5s linear infinite;transition:width .7s cubic-bezier(.2,.8,.2,1);}
@keyframes flow{to{background-position:-200% 0;}}
.acc-foot{display:flex;align-items:center;justify-content:space-between;padding-top:12px;margin-top:12px;border-top:1px solid var(--border);}
.acc-note{font-size:12.5px;color:var(--txt-3);display:flex;align-items:center;gap:6px;min-width:0;}
.icon-actions{display:flex;gap:6px;}
.icon-btn{width:31px;height:31px;border-radius:8px;background:var(--void);border:1px solid var(--border);color:var(--txt-2);font-size:12px;display:grid;place-items:center;cursor:pointer;transition:all .18s;}
.icon-btn:hover{background:var(--panel-3);color:var(--txt);border-color:var(--a);transform:translateY(-2px);box-shadow:0 6px 16px -6px rgba(var(--a-rgb),.9);}
.icon-btn.danger:hover{color:var(--bad);border-color:var(--bad);}
.icon-btn.on{color:var(--ok);border-color:var(--ok);}
.accounts.list .account{display:grid;grid-template-columns:1.2fr 2fr auto;align-items:center;gap:16px;}
.accounts.list .acc-row,.accounts.list .exp-grid,.accounts.list .acc-foot{margin:0;padding:0;border:0;}
.accounts.list .progress{grid-column:1 / -1;}
@media(max-width:700px){.accounts.list .account{display:block;}.exp-grid{grid-template-columns:repeat(2,1fr);}}

.empty{padding:56px 24px;text-align:center;color:var(--txt-3);grid-column:1 / -1;}
.empty i{font-size:38px;color:var(--border-hi);display:block;margin-bottom:12px;}

/* LOGS */
.logs-tools{display:flex;gap:8px;flex-wrap:wrap;align-items:center;padding:10px 14px;border-bottom:1px solid var(--border);}
.logs-tools .search{flex:1 1 120px;}
.logs-stream{height:560px;overflow-y:auto;padding:12px 16px;font-family:var(--mono);font-size:12px;line-height:1.75;background:var(--void);}
.logs-stream::-webkit-scrollbar{width:8px;}
.logs-stream::-webkit-scrollbar-thumb{background:var(--border-hi);border-radius:4px;}
.log-line{display:flex;gap:10px;padding:1px 0;word-break:break-word;animation:logIn .3s ease;}
@keyframes logIn{from{opacity:0;transform:translateX(-8px);}}
.log-ts{color:var(--txt-3);flex-shrink:0;}
.log-msg{color:var(--txt-2);}
.log-msg.info{color:rgb(var(--b-rgb));}
.log-msg.success{color:var(--ok);}
.log-msg.warning{color:var(--warn);}
.log-msg.error{color:var(--bad);}

/* MODALS */
.overlay{position:fixed;inset:0;z-index:100;background:rgba(4,1,10,.8);backdrop-filter:blur(8px);display:none;align-items:center;justify-content:center;padding:20px;}
.overlay.on{display:flex;animation:fade .2s ease;}
@keyframes fade{from{opacity:0;}}
.modal{position:relative;width:100%;max-width:480px;background:linear-gradient(180deg,var(--panel),var(--bg));border:1px solid var(--border-hi);border-radius:var(--r);box-shadow:0 30px 90px -20px #000,0 0 70px -24px rgba(var(--a-rgb),.8);animation:pop .3s cubic-bezier(.2,.9,.3,1.2);overflow:hidden;max-height:92vh;overflow-y:auto;}
@keyframes pop{from{opacity:0;transform:scale(.94) translateY(18px);}}
.modal::before{content:"";position:absolute;top:0;left:0;right:0;height:2px;background:linear-gradient(90deg,transparent,var(--a),var(--b),transparent);}
.modal-head{display:flex;align-items:center;justify-content:space-between;padding:18px 22px;border-bottom:1px solid var(--border);}
.modal-head h3{font-family:var(--display);font-size:14px;letter-spacing:.08em;display:flex;align-items:center;gap:10px;}
.modal-head h3 i{color:var(--a);}
.modal-body{padding:22px;}
.field{margin-bottom:14px;}
.field label{display:block;font-size:13px;font-weight:700;color:var(--txt-2);margin-bottom:6px;letter-spacing:.04em;}
.modal-foot{display:flex;justify-content:flex-end;gap:10px;padding-top:6px;}
.hint{font-size:12.5px;color:var(--txt-3);margin-top:6px;}
.tabs{display:flex;gap:6px;margin-bottom:16px;}
.tabs .chip{flex:1;text-align:center;}

/* PALETTE */
.palette{max-width:560px;align-self:flex-start;margin-top:12vh;}
.palette .input{border:0;border-bottom:1px solid var(--border);border-radius:0;padding:16px 20px;font-size:16px;background:transparent;}
.cmd-list{max-height:360px;overflow-y:auto;padding:8px;}
.cmd{display:flex;align-items:center;gap:12px;padding:10px 12px;border-radius:9px;cursor:pointer;font-weight:600;color:var(--txt-2);}
.cmd i{width:18px;text-align:center;color:var(--a);}
.cmd .kbd{margin-left:auto;}
.cmd.sel,.cmd:hover{background:rgba(var(--a-rgb),.16);color:var(--txt);}
.helpgrid{display:grid;grid-template-columns:auto 1fr;gap:8px 16px;align-items:center;}

/* TOASTS */
.toasts{position:fixed;right:18px;top:18px;z-index:200;display:flex;flex-direction:column;gap:10px;pointer-events:none;}
.toast{pointer-events:auto;min-width:240px;max-width:340px;padding:12px 16px;border-radius:11px;background:var(--panel-2);border:1px solid var(--border-hi);border-left:3px solid var(--a);box-shadow:0 14px 40px -12px #000;font-weight:600;display:flex;gap:10px;align-items:flex-start;animation:tin .35s cubic-bezier(.2,.9,.3,1.2);}
.toast.ok{border-left-color:var(--ok);}.toast.err{border-left-color:var(--bad);}.toast.warn{border-left-color:var(--warn);}
.toast i{margin-top:3px;}
.toast.out{animation:tout .3s forwards;}
@keyframes tin{from{opacity:0;transform:translateX(40px);}}
@keyframes tout{to{opacity:0;transform:translateX(40px);}}

/* BOOT */
#boot{position:fixed;inset:0;z-index:300;background:var(--void);display:flex;align-items:center;justify-content:center;padding:24px;cursor:pointer;transition:opacity .5s,visibility .5s;}
#boot.done{opacity:0;visibility:hidden;}
#boot pre{font-family:var(--mono);font-size:13px;color:var(--ok);line-height:1.7;min-width:min(520px,100%);text-shadow:0 0 8px rgba(var(--ok-rgb),.6);white-space:pre-wrap;}
#boot .big{font-family:var(--display);font-weight:900;font-size:clamp(30px,8vw,64px);letter-spacing:.1em;margin-bottom:18px;background:linear-gradient(90deg,var(--a),var(--b));-webkit-background-clip:text;background-clip:text;color:transparent;filter:drop-shadow(0 0 20px rgba(var(--a-rgb),.7));}
#confetti{position:fixed;inset:0;z-index:250;pointer-events:none;width:100%;height:100%;}

/* TICKER + WM */
.ticker{position:fixed;left:0;right:0;bottom:0;z-index:40;height:34px;background:linear-gradient(90deg,var(--panel),var(--void));border-top:1px solid var(--border-hi);overflow:hidden;display:flex;align-items:center;}
.ticker-track{display:flex;gap:56px;white-space:nowrap;animation:tick 40s linear infinite;font-family:var(--mono);font-size:12px;color:var(--txt-3);padding-left:100%;}
.ticker-track b{color:var(--a);}
@keyframes tick{to{transform:translateX(-100%);}}
.wm{position:fixed;bottom:44px;right:18px;font-family:var(--display);font-size:11px;letter-spacing:.2em;color:var(--txt-3);pointer-events:none;user-select:none;opacity:.8;}
.wm b{color:var(--a);margin-left:4px;text-shadow:0 0 10px rgba(var(--a-rgb),.8);}

@media(max-width:640px){body{padding:12px 12px 64px;}.glitch{font-size:20px;}.topbar{padding:14px;}.actions{width:100%;}.actions .btn{flex:1;justify-content:center;}.wm{display:none;}}
@media(prefers-reduced-motion:reduce){*,*::before,*::after{animation-duration:.01ms!important;animation-iteration-count:1!important;transition-duration:.01ms!important;}.ticker-track{animation:none;}}
</style>
</head>
<body>
<canvas id="bg-canvas"></canvas>
<div class="cursor-glow" id="cursor-glow"></div>
<canvas id="confetti"></canvas>
<div class="toasts" id="toasts"></div>

<div id="boot" title="Click to skip"><div><div class="big">CODEXGOJO</div><pre id="boot-text"></pre></div></div>

<div class="container">
  <div class="topbar">
    <div class="brand">
      <div class="logo"><span><b>C</b></span></div>
      <div class="brand-info">
        <div class="glitch" data-text="CODEXGOJO">CODEXGOJO</div>
        <div class="tagline">
          <span>Level Up Bot</span>
          <span class="pill live" id="conn-pill"><i class="fa-solid fa-circle"></i><span id="conn-text">LIVE</span></span>
          <span class="clock" id="clock">--:--:--</span>
          <span class="clock" id="ping">ping —</span>
        </div>
      </div>
    </div>
    <div class="actions">
      <button class="btn btn-ghost" onclick="openPalette()" title="Command palette"><i class="fa-solid fa-terminal"></i> Commands <span class="kbd">Ctrl K</span></button>
      <button class="btn btn-ghost" id="btn-theme" onclick="cycleTheme()" title="Theme (T)"><i class="fa-solid fa-palette"></i></button>
      <button class="btn btn-ghost" id="btn-fx" onclick="toggleFx()" title="Effects (F)"><i class="fa-solid fa-wand-magic-sparkles"></i></button>
      <button class="btn btn-ghost" id="btn-sound" onclick="toggleSound()" title="Sound (M)"><i class="fa-solid fa-volume-xmark"></i></button>
      <button class="btn btn-ghost" id="btn-refresh" onclick="fetchStats(true)"><i class="fa-solid fa-rotate"></i> Refresh</button>
      <button class="btn btn-primary" onclick="openAddModal()"><i class="fa-solid fa-plus"></i> Add Account</button>
    </div>
  </div>

  <div class="stats" id="stats">
    <div class="stat"><div class="stat-head"><span class="stat-label">Active accounts</span><span class="stat-icon"><i class="fa-solid fa-users"></i></span></div><div class="stat-value" id="stat-total-accounts">0</div><div class="stat-foot">Currently monitored</div></div>
    <div class="stat"><div class="stat-head"><span class="stat-label">Total EXP gained</span><span class="stat-icon ok"><i class="fa-solid fa-arrow-trend-up"></i></span></div><div class="stat-value" id="stat-total-exp">0</div><div class="stat-foot">Across all accounts</div></div>
    <div class="stat"><div class="stat-head"><span class="stat-label">Matches completed</span><span class="stat-icon warn"><i class="fa-solid fa-gamepad"></i></span></div><div class="stat-value" id="stat-total-matches">0</div><div class="stat-foot">Since session start</div></div>
    <div class="stat"><div class="stat-head"><span class="stat-label">Uptime</span><span class="stat-icon b"><i class="fa-solid fa-clock"></i></span></div><div class="stat-value mono" id="stat-uptime">00:00:00</div><div class="stat-foot">Bot session runtime</div></div>
    <div class="stat"><div class="stat-head"><span class="stat-label">EXP per hour</span><span class="stat-icon ok"><i class="fa-solid fa-bolt"></i></span></div><div class="stat-value" id="stat-xph">0</div><div class="stat-foot">Measured over the last few minutes</div></div>
    <div class="stat"><div class="stat-head"><span class="stat-label">Avg EXP / match</span><span class="stat-icon b"><i class="fa-solid fa-calculator"></i></span></div><div class="stat-value" id="stat-avg">0</div><div class="stat-foot">Gained ÷ matches</div></div>
    <div class="stat"><div class="stat-head"><span class="stat-label">In match now</span><span class="stat-icon"><i class="fa-solid fa-crosshairs"></i></span></div><div class="stat-value" id="stat-live">0</div><div class="stat-foot" id="stat-live-foot">Accounts fighting</div></div>
    <div class="stat"><div class="stat-head"><span class="stat-label">Top grinder</span><span class="stat-icon warn"><i class="fa-solid fa-crown"></i></span></div><div class="stat-value mono" id="stat-top">—</div><div class="stat-foot" id="stat-top-foot">Highest EXP gained</div></div>
  </div>

  <div class="panel mb">
    <div class="panel-head">
      <div class="panel-title"><i class="fa-solid fa-chart-line"></i><span>EXP GAIN TIMELINE</span></div>
      <div class="panel-hint"><span id="chart-range">waiting for data…</span></div>
    </div>
    <div class="chart-wrap"><canvas id="chart"></canvas></div>
    <div class="chart-meta"><span>peak <b id="ch-peak">0</b></span><span>last <b id="ch-last">0</b></span><span>points <b id="ch-pts">0</b></span></div>
  </div>

  <div class="layout">
    <div class="panel">
      <div class="panel-head">
        <div class="panel-title"><i class="fa-solid fa-list-ul"></i><span>MONITORED ACCOUNTS</span></div>
        <div class="panel-hint" id="acc-count-hint">—</div>
      </div>
      <div class="toolbar">
        <div class="search"><i class="fa-solid fa-magnifying-glass"></i><input class="input" id="acc-search" placeholder="Search name or UID  ( / )" autocomplete="off"></div>
        <div class="chips" id="status-chips">
          <button class="chip on" data-s="ALL">ALL</button>
          <button class="chip" data-s="IN_MATCH">IN MATCH</button>
          <button class="chip" data-s="SEARCHING">SEARCHING</button>
          <button class="chip" data-s="ERROR">ERROR</button>
        </div>
        <select class="input" id="acc-sort" title="Sort">
          <option value="gained">Sort: EXP gained</option>
          <option value="level">Sort: Level</option>
          <option value="matches">Sort: Matches</option>
          <option value="name">Sort: Name</option>
        </select>
        <div class="seg"><button id="v-grid" title="Grid"><i class="fa-solid fa-table-cells-large"></i></button><button id="v-list" title="List"><i class="fa-solid fa-bars"></i></button></div>
      </div>
      <div class="accounts" id="accounts-container">
        <div class="empty"><i class="fa-solid fa-circle-notch fa-spin"></i><p>Loading accounts…</p></div>
      </div>
    </div>

    <div class="panel">
      <div class="panel-head">
        <div class="panel-title"><i class="fa-solid fa-terminal"></i><span>ACTIVITY LOG</span></div>
        <div class="panel-hint"><span id="log-count">0</span> lines</div>
      </div>
      <div class="logs-tools">
        <div class="chips" id="log-chips">
          <button class="chip on" data-l="all">ALL</button>
          <button class="chip" data-l="info">INFO</button>
          <button class="chip" data-l="success">OK</button>
          <button class="chip" data-l="warning">WARN</button>
          <button class="chip" data-l="error">ERR</button>
        </div>
        <div class="search"><i class="fa-solid fa-filter"></i><input class="input" id="log-search" placeholder="Filter logs" autocomplete="off"></div>
        <button class="icon-btn" id="log-pause" title="Pause autoscroll"><i class="fa-solid fa-pause"></i></button>
        <button class="icon-btn" onclick="exportLogs()" title="Export logs"><i class="fa-solid fa-download"></i></button>
        <button class="icon-btn danger" onclick="clearLogs()" title="Clear view"><i class="fa-regular fa-trash-can"></i></button>
      </div>
      <div class="logs-stream" id="log-stream"></div>
    </div>
  </div>
</div>

<!-- ADD MODAL -->
<div class="overlay" id="add-modal">
  <div class="modal">
    <div class="modal-head"><h3><i class="fa-solid fa-user-plus"></i> ADD ACCOUNT</h3><button class="icon-btn" onclick="closeAddModal()"><i class="fa-solid fa-xmark"></i></button></div>
    <div class="modal-body">
      <div class="tabs"><button class="chip on" id="tab-single" type="button">Single</button><button class="chip" id="tab-bulk" type="button">Bulk import</button></div>
      <div class="field"><label>কোন Squad / Terminal-এ যোগ করবেন?</label>
        <select class="input" id="account-squad" style="width:100%">
          <option value="0">Terminal 1 / Squad 1</option><option value="1">Terminal 2 / Squad 2</option>
          <option value="2">Terminal 3 / Squad 3</option><option value="3">Terminal 4 / Squad 4</option>
          <option value="4">Terminal 5 / Squad 5</option><option value="5">Terminal 6 / Squad 6</option>
          <option value="6">Terminal 7 / Squad 7</option><option value="7">Terminal 8 / Squad 8</option>
          <option value="8">Terminal 9 / Squad 9</option><option value="9">Terminal 10 / Squad 10</option>
        </select>
        <div class="hint">নিচের ছোট বাটনে চাপ দিয়ে নির্দিষ্ট Squad-এর আলাদা লগ দেখতে পারবেন।</div>
        <div class="chips" style="margin-top:8px"><button type="button" class="chip" onclick="viewSquadLog(0)">Terminal 1</button><button type="button" class="chip" onclick="viewSquadLog(1)">Terminal 2</button><button type="button" class="chip" onclick="viewSquadLog(2)">Terminal 3</button><button type="button" class="chip" onclick="viewSquadLog(3)">Terminal 4</button><button type="button" class="chip" onclick="viewSquadLog(4)">Terminal 5</button><button type="button" class="chip" onclick="viewSquadLog(5)">Terminal 6</button><button type="button" class="chip" onclick="viewSquadLog(6)">Terminal 7</button><button type="button" class="chip" onclick="viewSquadLog(7)">Terminal 8</button><button type="button" class="chip" onclick="viewSquadLog(8)">Terminal 9</button><button type="button" class="chip" onclick="viewSquadLog(9)">Terminal 10</button></div>
      </div>
      <form id="add-acc-form" onsubmit="submitAddAccount(event)">
        <div id="single-pane">
          <div class="field"><label>Account type</label>
            <select class="input" id="acc-type" style="width:100%" onchange="toggleFormType()">
              <option value="guest">Guest — UID &amp; password</option>
              <option value="token">Access token</option>
            </select>
          </div>
          <div id="guest-fields">
            <div class="field"><label>Guest UID</label><input type="text" class="input" id="acc-uid" placeholder="7644913583" autocomplete="off"></div>
            <div class="field"><label>Password / Secret</label><input type="text" class="input" id="acc-password" placeholder="ZERO_GRAVITY_4NM38" autocomplete="off"></div>
          </div>
          <div id="token-fields" style="display:none;">
            <div class="field"><label>Access token</label><textarea class="input" id="acc-token" placeholder="Paste token here…"></textarea></div>
          </div>
        </div>
        <div id="bulk-pane" style="display:none;">
          <div class="field"><label>One account per line</label>
            <textarea class="input" id="bulk-text" style="min-height:150px" placeholder="uid:password&#10;uid:password&#10;long_access_token_here"></textarea>
            <div class="hint">Use <span class="kbd">uid:password</span> or <span class="kbd">uid password</span>. A single long string is treated as a token.</div>
          </div>
        </div>
        <div class="modal-foot">
          <button type="button" class="btn btn-ghost" onclick="closeAddModal()">Cancel</button>
          <button type="submit" class="btn btn-primary" id="btn-save"><i class="fa-solid fa-check"></i> Save &amp; start</button>
        </div>
      </form>
    </div>
  </div>
</div>

<!-- PALETTE -->
<div class="overlay" id="palette-modal">
  <div class="modal palette">
    <input class="input" id="cmd-input" placeholder="Type a command…" autocomplete="off">
    <div class="cmd-list" id="cmd-list"></div>
  </div>
</div>

<!-- HELP -->
<div class="overlay" id="help-modal">
  <div class="modal">
    <div class="modal-head"><h3><i class="fa-solid fa-keyboard"></i> SHORTCUTS</h3><button class="icon-btn" onclick="closeAll()"><i class="fa-solid fa-xmark"></i></button></div>
    <div class="modal-body"><div class="helpgrid">
      <span class="kbd">Ctrl K</span><span>Command palette</span>
      <span class="kbd">A</span><span>Add account</span>
      <span class="kbd">R</span><span>Refresh data</span>
      <span class="kbd">/</span><span>Search accounts</span>
      <span class="kbd">T</span><span>Cycle theme</span>
      <span class="kbd">F</span><span>Toggle effects</span>
      <span class="kbd">M</span><span>Toggle sound</span>
      <span class="kbd">G</span><span>Grid / list view</span>
      <span class="kbd">?</span><span>This help</span>
      <span class="kbd">Esc</span><span>Close any window</span>
    </div><p class="hint" style="margin-top:16px">Hint: some old-school cheat codes still work here.</p></div>
  </div>
</div>

<div class="ticker"><div class="ticker-track" id="ticker"></div></div>
<div class="wm">DESIGNED BY<b>CODEXGOJO</b></div>

<script>
/* ---------- helpers ---------- */
const $ = s => document.querySelector(s), $$ = s => [...document.querySelectorAll(s)];
const store = {
  get(k,d){ try{ const v = localStorage.getItem('cgj_'+k); return v===null ? d : JSON.parse(v); }catch(e){ return d; } },
  set(k,v){ try{ localStorage.setItem('cgj_'+k, JSON.stringify(v)); }catch(e){} }
};
const esc = t => t==null ? '' : String(t).replace(/&/g,'&amp;').replace(/</g,'&lt;').replace(/>/g,'&gt;').replace(/"/g,'&quot;');
const fmt = n => Math.round(n||0).toLocaleString();
const pad = n => String(n).padStart(2,'0');
const reduceMotion = window.matchMedia('(prefers-reduced-motion: reduce)').matches;

const S = {
  theme: store.get('theme','neon'), fx: store.get('fx',true), sound: store.get('sound',false),
  view: store.get('view','grid'), sort: store.get('sort','gained'), status:'ALL', q:'',
  demo:false, fails:0, accounts:[], levels:{}, history:[], buf:[], lastLogCount:0, logsInit:false,
  logLevel:'all', logQ:'', logPaused:false, start:Date.now(), isFetching:false, totals:{matches:0,gained:0}
};

/* ---------- toasts ---------- */
function toast(msg, kind='info', ms=3200){
  const icons = {ok:'fa-circle-check',err:'fa-triangle-exclamation',warn:'fa-circle-exclamation',info:'fa-bolt'};
  const el = document.createElement('div');
  el.className = 'toast ' + kind;
  el.innerHTML = `<i class="fa-solid ${icons[kind]||icons.info}"></i><span>${esc(msg)}</span>`;
  $('#toasts').appendChild(el);
  setTimeout(()=>{ el.classList.add('out'); setTimeout(()=>el.remove(),300); }, ms);
}

/* ---------- sound ---------- */
let actx = null;
function beep(freq=660, dur=.12, type='square', vol=.05){
  if(!S.sound) return;
  try{
    actx = actx || new (window.AudioContext||window.webkitAudioContext)();
    const o = actx.createOscillator(), g = actx.createGain();
    o.type = type; o.frequency.value = freq; g.gain.value = vol;
    o.connect(g); g.connect(actx.destination);
    g.gain.exponentialRampToValueAtTime(.0001, actx.currentTime + dur);
    o.start(); o.stop(actx.currentTime + dur);
  }catch(e){}
}
const jingle = () => [523,659,784,1047].forEach((f,i)=>setTimeout(()=>beep(f,.14,'triangle',.07), i*90));

/* ---------- theme / fx / sound ---------- */
const THEMES = ['neon','blood','matrix','ice'];
function applyTheme(){
  document.documentElement.setAttribute('data-theme', S.theme);
  store.set('theme', S.theme);
  rainInit(); drawChart();
}
function cycleTheme(){ S.theme = THEMES[(THEMES.indexOf(S.theme)+1)%THEMES.length]; applyTheme(); toast('Theme: ' + S.theme.toUpperCase(),'info',1600); beep(880,.08); }
function applyFx(){ document.body.classList.toggle('nofx', !S.fx); store.set('fx',S.fx); $('#btn-fx').style.color = S.fx ? 'var(--a)' : ''; }
function toggleFx(){ S.fx = !S.fx; applyFx(); toast('Effects ' + (S.fx?'ON':'OFF'),'info',1400); }
function applySound(){ $('#btn-sound').innerHTML = `<i class="fa-solid ${S.sound?'fa-volume-high':'fa-volume-xmark'}"></i>`; $('#btn-sound').style.color = S.sound ? 'var(--ok)' : ''; store.set('sound',S.sound); }
function toggleSound(){ S.sound = !S.sound; applySound(); toast('Sound ' + (S.sound?'ON':'OFF'),'info',1400); beep(990,.1); }
function setView(v){
  S.view = v; store.set('view',v);
  $('#accounts-container').classList.toggle('list', v==='list');
  $('#v-grid').classList.toggle('on', v==='grid'); $('#v-list').classList.toggle('on', v==='list');
}
function toggleView(){ setView(S.view==='grid'?'list':'grid'); }

/* ---------- background: matrix rain ---------- */
const bg = $('#bg-canvas'), bgx = bg.getContext('2d');
let drops = [], cols = 0, rainTimer = null;
function rainInit(){
  bg.width = innerWidth; bg.height = innerHeight;
  cols = Math.ceil(bg.width/18); drops = Array.from({length:cols}, () => Math.random()*bg.height/18);
}
function rainDraw(){
  if(!S.fx || document.hidden) return;
  const cs = getComputedStyle(document.documentElement);
  const rgb = cs.getPropertyValue(Math.random()<.2 ? '--b-rgb' : '--a-rgb').trim();
  bgx.fillStyle = 'rgba(5,2,10,.12)'; bgx.fillRect(0,0,bg.width,bg.height);
  bgx.font = '15px JetBrains Mono, monospace';
  const chars = '01CODEXGOJO<>/{}#$';
  for(let i=0;i<cols;i++){
    bgx.fillStyle = `rgba(${rgb},.9)`;
    bgx.fillText(chars[Math.floor(Math.random()*chars.length)], i*18, drops[i]*18);
    if(drops[i]*18 > bg.height && Math.random() > .975) drops[i] = 0;
    drops[i] += .6;
  }
}
addEventListener('resize', () => { rainInit(); drawChart(); });
if(!reduceMotion) setInterval(rainDraw, 55);
addEventListener('pointermove', e => { const g = $('#cursor-glow'); g.style.left = e.clientX+'px'; g.style.top = e.clientY+'px'; });
document.addEventListener('pointermove', e => {
  const c = e.target.closest && e.target.closest('.stat,.account');
  if(!c) return; const r = c.getBoundingClientRect();
  c.style.setProperty('--mx', (e.clientX-r.left)+'px'); c.style.setProperty('--my', (e.clientY-r.top)+'px');
});

/* ---------- confetti ---------- */
const cf = $('#confetti'), cfx = cf.getContext('2d'); let parts = [], cfRun = false;
function confetti(n=140){
  if(!S.fx || reduceMotion) return;
  cf.width = innerWidth; cf.height = innerHeight;
  const cs = getComputedStyle(document.documentElement);
  const colors = ['--a-rgb','--b-rgb','--ok-rgb','--warn-rgb'].map(v => `rgb(${cs.getPropertyValue(v).trim()})`);
  for(let i=0;i<n;i++) parts.push({x:innerWidth/2+(Math.random()-.5)*200,y:innerHeight*.35,vx:(Math.random()-.5)*16,vy:-Math.random()*14-4,s:Math.random()*7+3,c:colors[i%4],r:Math.random()*6,vr:(Math.random()-.5)*.4,l:1});
  if(!cfRun){ cfRun = true; requestAnimationFrame(cfStep); }
}
function cfStep(){
  cfx.clearRect(0,0,cf.width,cf.height);
  parts.forEach(p => { p.vy += .35; p.x += p.vx; p.y += p.vy; p.r += p.vr; p.l -= .008; cfx.save(); cfx.globalAlpha = Math.max(p.l,0); cfx.translate(p.x,p.y); cfx.rotate(p.r); cfx.fillStyle = p.c; cfx.fillRect(-p.s/2,-p.s/2,p.s,p.s*.6); cfx.restore(); });
  parts = parts.filter(p => p.l > 0 && p.y < cf.height+40);
  if(parts.length) requestAnimationFrame(cfStep); else { cfRun = false; cfx.clearRect(0,0,cf.width,cf.height); }
}

/* ---------- count-up ---------- */
function tween(el, to, render){
  const from = el._v || 0; el._v = to;
  if(from === to || reduceMotion){ el.innerHTML = render(to); return; }
  const t0 = performance.now(), dur = 700;
  (function step(t){
    const k = Math.min(1,(t-t0)/dur), e = 1-Math.pow(1-k,3);
    el.innerHTML = render(from + (to-from)*e);
    if(k<1 && el._v === to) requestAnimationFrame(step);
  })(t0);
}

/* ---------- ranks ---------- */
function tier(level){
  if(level >= 80) return {n:'HEROIC', c:'#ff4d6d'};
  if(level >= 65) return {n:'DIAMOND', c:'#38bdf8'};
  if(level >= 50) return {n:'GOLD', c:'#ffc400'};
  if(level >= 30) return {n:'SILVER', c:'#cfd8e3'};
  if(level >= 10) return {n:'BRONZE', c:'#d98a4e'};
  return {n:'ROOKIE', c:'#9a8fc4'};
}

/* ---------- demo engine (used when the backend API is unreachable) ---------- */
const demo = {
  accounts:[], logs:[], matches:0, n:0,
  init(){
    const names = [['GOJO_X','BD'],['NeonViper','IND'],['ShadowByte','SG'],['PhantomZ','BD'],['VoidWalker','ID']];
    this.accounts = names.map((p,i) => {
      const exp = 12000 + Math.floor(Math.random()*90000);
      return {uid:String(7640000000+Math.floor(Math.random()*9999999)), nickname:p[0], region:p[1], status:'ONLINE', active_matches:0,
        initial_exp:exp, current_exp:exp, gained_exp:0, level:25+i*9, matches_played:0, last_match_time:'running…', _next:1200+Math.random()*900};
    });
    this.log('info','Demo engine online — backend not reachable, showing simulated data');
  },
  log(level,msg){ const d = new Date(); this.logs.push({time:`${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`, level, message:msg}); if(this.logs.length>600) this.logs.shift(); },
  tick(){
    this.accounts.forEach(a => {
      const r = Math.random();
      if(a.status==='ONLINE' && r<.35){ a.status='SEARCHING'; this.log('info',`[${a.nickname}] searching for a match…`); }
      else if(a.status==='SEARCHING' && r<.5){ a.status='IN_MATCH'; a.active_matches = 1+Math.floor(Math.random()*3); this.log('info',`[${a.nickname}] match found, ${a.active_matches} active`); }
      else if(a.status==='IN_MATCH' && r<.45){
        const g = 80+Math.floor(Math.random()*240);
        a.current_exp += g; a.gained_exp += g; a.matches_played++; this.matches++; a.active_matches = 0; a.status='ONLINE';
        const d = new Date(); a.last_match_time = `last ${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
        this.log('success',`[${a.nickname}] match complete  +${g} EXP`);
        if(a.gained_exp > a._next){ a.level++; a._next += 1400 + a.level*18; this.log('success',`[${a.nickname}] LEVEL UP -> ${a.level}`); }
      } else if(r > .985){ a.status='ERROR'; this.log('error',`[${a.nickname}] socket reset, reconnecting`); }
      else if(a.status==='ERROR' && r<.6){ a.status='CONNECTING'; }
      else if(a.status==='CONNECTING' && r<.6){ a.status='ONLINE'; this.log('warning',`[${a.nickname}] reconnected`); }
    });
    return this.snapshot();
  },
  snapshot(){
    return {total_accounts:this.accounts.length, total_gained_exp:this.accounts.reduce((s,a)=>s+a.gained_exp,0), total_matches:this.matches,
      accounts:this.accounts.map(a=>({...a})), logs:this.logs.slice()};
  }
};

/* ---------- API layer ---------- */
async function api(path, body){
  const res = await fetch(path, {method:'POST', headers:{'Content-Type':'application/json'}, body:JSON.stringify(body)});
  const data = await res.json().catch(()=>({}));
  return {ok:res.ok, data};
}

function setConn(state){
  const p = $('#conn-pill'), t = $('#conn-text');
  p.className = 'pill ' + (state==='live'?'live':state==='demo'?'demo':'off');
  t.textContent = state==='live'?'LIVE':state==='demo'?'DEMO MODE':'OFFLINE';
}

/* ---------- modal logic ---------- */
function openAddModal(){ closeAll(); $('#add-modal').classList.add('on'); setTimeout(()=>($('#acc-uid')||{}).focus&&$('#acc-uid').focus(),50); }
function closeAddModal(){ $('#add-modal').classList.remove('on'); }
function closeAll(){ $$('.overlay').forEach(o=>o.classList.remove('on')); }
function toggleFormType(){
  const t = $('#acc-type').value;
  $('#guest-fields').style.display = t==='guest' ? 'block':'none';
  $('#token-fields').style.display = t==='token' ? 'block':'none';
}
let bulkMode = false;
function setBulk(b){
  bulkMode = b;
  $('#single-pane').style.display = b?'none':'block'; $('#bulk-pane').style.display = b?'block':'none';
  $('#tab-single').classList.toggle('on', !b); $('#tab-bulk').classList.toggle('on', b);
}
$('#tab-single').onclick = () => setBulk(false);
$('#tab-bulk').onclick = () => setBulk(true);

function parseBulk(text){
  return text.split(/\r?\n/).map(l=>l.trim()).filter(Boolean).map(l=>{
    const m = l.match(/^(\S+?)[:\s,;|]+(\S+)$/);
    if(m) return {uid:m[1], password:m[2]};
    if(l.length > 30) return {token:l};
    return null;
  }).filter(Boolean);
}

async function addOne(payload){
  if(S.demo){
    demo.accounts.push({uid:payload.uid||String(7600000000+Math.floor(Math.random()*99999999)), nickname:'NewRecruit'+(++demo.n), region:'BD', status:'CONNECTING', active_matches:0, initial_exp:5000, current_exp:5000, gained_exp:0, level:12, matches_played:0, last_match_time:'running…', _next:1500});
    demo.log('info','[demo] account added'); return {status:'ok'};
  }
  const {data, ok} = await api('/api/account/add', payload);
  return ok ? data : {status:'error', error:data.error||'HTTP error'};
}

function viewSquadLog(sid){
  const url = `/api/squad-log/${sid}`;
  window.open(url, `squad_terminal_${sid+1}`, 'noopener');
}

async function submitAddAccount(e){
  e.preventDefault();
  const squadId = Number($('#account-squad')?.value || 0);
  const btn = $('#btn-save');
  let list = [];
  if(bulkMode){
    list = parseBulk($('#bulk-text').value);
    if(!list.length) return toast('No valid lines found','err');
  } else if($('#acc-type').value === 'guest'){
    const uid = $('#acc-uid').value.trim(), password = $('#acc-password').value.trim();
    if(!uid || !password) return toast('Enter both UID and password','err');
    list = [{uid,password}];
  } else {
    const token = $('#acc-token').value.trim();
    if(!token) return toast('Enter an access token','err');
    list = [{token}];
  }
  list = list.map(p => ({...p, squad_id: squadId}));
  btn.disabled = true; btn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Saving…';
  let okc = 0, bad = 0;
  for(const p of list){
    try{ const r = await addOne(p); if(r.status==='ok') okc++; else { bad++; toast('Error: '+(r.error||'Unknown'),'err'); } }
    catch(err){ bad++; toast('Request failed: '+err,'err'); }
  }
  btn.disabled = false; btn.innerHTML = '<i class="fa-solid fa-check"></i> Save &amp; start';
  if(okc){ toast(`${okc} account${okc>1?'s':''} added`,'ok'); jingle(); closeAddModal(); $('#add-acc-form').reset(); toggleFormType(); await fetchStats(true); }
}

async function deleteAccount(uid){
  if(!confirm('আপনি কি নিশ্চিত? অ্যাকাউন্ট ' + uid + ' স্থায়ীভাবে ডিলিট হবে (ফাইল থেকেও রিমুভ)।')) return;
  const card = document.querySelector(`.account[data-uid="${CSS.escape(uid)}"]`);
  if(card){ card.style.transition='all .3s ease'; card.style.opacity='0'; card.style.transform='translateX(-20px) scale(.95)'; }
  try{
    if(S.demo){ demo.accounts = demo.accounts.filter(a=>a.uid!==uid); demo.log('warning',`[demo] account ${uid} removed`); }
    else {
      const {ok,data} = await api('/api/account/delete',{uid, permanent:true});
      if(!ok || data.status!=='ok'){ toast('Delete failed: '+(data.error||'Unknown'),'err'); if(card){card.style.opacity='1';card.style.transform='none';} return; }
    }
    toast('Account deleted','warn'); beep(220,.2,'sawtooth');
    await fetchStats(true);
  }catch(err){ toast('Delete failed: '+err,'err'); if(card){card.style.opacity='1';card.style.transform='none';} }
}

async function refreshAccountInfo(uid, quiet){
  try{ if(!S.demo) await api('/api/account/refresh',{uid}); if(!quiet){ toast('Refreshed '+uid,'ok',1400); } await fetchStats(true); }
  catch(err){ console.error(err); }
}
async function refreshAll(){
  if(!S.accounts.length) return toast('No accounts to refresh','warn');
  toast(`Refreshing ${S.accounts.length} accounts…`);
  for(const a of S.accounts){ await refreshAccountInfo(String(a.uid), true); }
  toast('All accounts refreshed','ok'); beep(740,.1);
}

/* ---------- rendering ---------- */
function statusClass(s){ s = String(s||'ONLINE').toUpperCase(); return s==='IN_MATCH'?'match':s==='SEARCHING'?'searching':s==='ERROR'?'error':s==='CONNECTING'?'connecting':'online'; }
function statusText(a){ const s = String(a.status||'ONLINE').toUpperCase(); return s==='IN_MATCH' ? `In match · ${a.active_matches||0}` : s.charAt(0)+s.slice(1).toLowerCase(); }
function xphFor(a){ const hrs = Math.max((Date.now()-S.start)/3.6e6, 1/120); return (a.gained_exp||0)/hrs; }

function renderCard(a){
  const uid = esc(String(a.uid)), t = tier(a.level||1);
  const pct = Math.min(100, Math.max(4, (a.current_exp % 1000)/10));
  return `<div class="account new" data-uid="${uid}" style="--tier:${t.c}">
    <div class="acc-row">
      <div class="acc-id">
        <div class="acc-avatar"><i class="fa-solid fa-user-astronaut"></i></div>
        <div class="acc-meta">
          <div class="acc-name">${esc(a.nickname||'Unknown')} <span class="badge">${esc(a.region||'BD')}</span> <span class="badge tier">${t.n}</span></div>
          <div class="acc-uid" data-copy="${uid}" title="Click to copy UID">UID ${uid}</div>
        </div>
      </div>
      <span class="status ${statusClass(a.status)}">${esc(statusText(a))}</span>
    </div>
    <div class="exp-grid">
      <div class="exp-cell"><div class="exp-label">Initial</div><div class="exp-value">${fmt(a.initial_exp)}</div></div>
      <div class="exp-cell"><div class="exp-label">Current</div><div class="exp-value">${fmt(a.current_exp)}</div></div>
      <div class="exp-cell"><div class="exp-label">Gained</div><div class="exp-value green">+${fmt(a.gained_exp)}</div></div>
      <div class="exp-cell"><div class="exp-label">EXP/hr</div><div class="exp-value cyan">${fmt(xphFor(a))}</div></div>
    </div>
    <div class="progress">
      <div class="progress-head"><span class="lv">Level ${a.level||1}</span><span>${a.matches_played||0} matches</span></div>
      <div class="progress-track"><div class="progress-fill" style="width:${pct}%"></div></div>
    </div>
    <div class="acc-foot">
      <span class="acc-note"><i class="fa-regular fa-clock"></i> ${esc(a.last_match_time||'running…')}</span>
      <div class="icon-actions">
        <button class="icon-btn" data-act="copy" data-uid="${uid}" title="Copy UID"><i class="fa-regular fa-copy"></i></button>
        <button class="icon-btn" data-act="refresh" data-uid="${uid}" title="Refresh"><i class="fa-solid fa-rotate"></i></button>
        <button class="icon-btn danger" data-act="delete" data-uid="${uid}" title="Delete"><i class="fa-regular fa-trash-can"></i></button>
      </div>
    </div>
  </div>`;
}

let lastSig = '';
function renderAccounts(force){
  let list = S.accounts.slice();
  const q = S.q.toLowerCase();
  if(q) list = list.filter(a => String(a.uid).toLowerCase().includes(q) || String(a.nickname||'').toLowerCase().includes(q));
  if(S.status !== 'ALL') list = list.filter(a => String(a.status||'ONLINE').toUpperCase() === S.status);
  const sorters = {gained:(a,b)=>(b.gained_exp||0)-(a.gained_exp||0), level:(a,b)=>(b.level||0)-(a.level||0), matches:(a,b)=>(b.matches_played||0)-(a.matches_played||0), name:(a,b)=>String(a.nickname||'').localeCompare(String(b.nickname||''))};
  list.sort(sorters[S.sort]);
  const sig = JSON.stringify([list, S.view, S.sort, S.status, q]);
  if(!force && sig === lastSig) return;
  lastSig = sig;
  const box = $('#accounts-container');
  const known = new Set([...box.querySelectorAll('.account')].map(c=>c.dataset.uid));
  $('#acc-count-hint').textContent = `${list.length}/${S.accounts.length} accounts`;
  if(!list.length){
    box.innerHTML = `<div class="empty"><i class="fa-regular fa-folder-open"></i><p>${S.accounts.length ? 'No accounts match your filters.' : 'No accounts yet. Click “Add Account” to begin.'}</p></div>`;
    return;
  }
  box.innerHTML = list.map(renderCard).join('');
  box.querySelectorAll('.account').forEach(c => { if(known.has(c.dataset.uid)) c.classList.remove('new'); if(S.levelUps && S.levelUps.has(c.dataset.uid)) c.classList.add('lvup'); });
  S.levelUps = null;
}

function updateStats(data){
  const accs = data.accounts;
  tween($('#stat-total-accounts'), data.total_accounts, v => fmt(v));
  tween($('#stat-total-exp'), data.total_gained_exp, v => '+' + fmt(v) + '<span class="unit">EXP</span>');
  tween($('#stat-total-matches'), data.total_matches, v => fmt(v));
  const live = accs.filter(a => String(a.status).toUpperCase()==='IN_MATCH');
  tween($('#stat-live'), live.length, v => fmt(v));
  $('#stat-live-foot').textContent = live.length ? `${live.reduce((s,a)=>s+(a.active_matches||0),0)} matches running` : 'Accounts fighting';
  tween($('#stat-avg'), data.total_matches ? data.total_gained_exp/data.total_matches : 0, v => fmt(v) + '<span class="unit">EXP</span>');
  // EXP/hour from the last ~5 minutes of samples
  const h = S.history, last = h[h.length-1];
  let xph = 0;
  if(h.length > 1){
    const ref = h.find(p => last.t - p.t <= 300000) || h[0];
    const dt = (last.t - ref.t)/3.6e6;
    xph = dt > 0 ? (last.v - ref.v)/dt : 0;
  }
  tween($('#stat-xph'), xph, v => fmt(v) + '<span class="unit">/h</span>');
  const top = accs.slice().sort((a,b)=>(b.gained_exp||0)-(a.gained_exp||0))[0];
  $('#stat-top').textContent = top && top.gained_exp ? top.nickname : '—';
  $('#stat-top-foot').textContent = top && top.gained_exp ? `+${fmt(top.gained_exp)} EXP` : 'Highest EXP gained';
}

/* ---------- chart ---------- */
function drawChart(){
  const c = $('#chart'); if(!c) return;
  const dpr = window.devicePixelRatio||1, w = c.clientWidth, h = c.clientHeight;
  c.width = w*dpr; c.height = h*dpr;
  const x = c.getContext('2d'); x.scale(dpr,dpr); x.clearRect(0,0,w,h);
  const cs = getComputedStyle(document.documentElement);
  const A = cs.getPropertyValue('--a-rgb').trim(), B = cs.getPropertyValue('--b-rgb').trim();
  const pts = S.history; const pad_ = 8;
  x.strokeStyle = 'rgba(255,255,255,.05)'; x.lineWidth = 1;
  for(let i=1;i<4;i++){ x.beginPath(); x.moveTo(0,h*i/4); x.lineTo(w,h*i/4); x.stroke(); }
  if(pts.length < 2){ x.fillStyle = `rgba(${B},.6)`; x.font = '13px JetBrains Mono, monospace'; x.fillText('collecting samples…', 12, h/2); return; }
  const max = Math.max(...pts.map(p=>p.v), 1), min = Math.min(...pts.map(p=>p.v));
  const span = Math.max(max-min, 1);
  const X = i => pad_ + (w-pad_*2) * i/(pts.length-1), Y = v => h-pad_-(h-pad_*2) * (v-min)/span;
  const grad = x.createLinearGradient(0,0,0,h); grad.addColorStop(0,`rgba(${A},.45)`); grad.addColorStop(1,`rgba(${A},0)`);
  x.beginPath(); pts.forEach((p,i)=> i ? x.lineTo(X(i),Y(p.v)) : x.moveTo(X(i),Y(p.v)));
  x.lineTo(X(pts.length-1),h); x.lineTo(X(0),h); x.closePath(); x.fillStyle = grad; x.fill();
  const lg = x.createLinearGradient(0,0,w,0); lg.addColorStop(0,`rgb(${A})`); lg.addColorStop(1,`rgb(${B})`);
  x.beginPath(); pts.forEach((p,i)=> i ? x.lineTo(X(i),Y(p.v)) : x.moveTo(X(i),Y(p.v)));
  x.strokeStyle = lg; x.lineWidth = 2.4; x.shadowColor = `rgb(${A})`; x.shadowBlur = 12; x.lineJoin = 'round'; x.stroke(); x.shadowBlur = 0;
  const lx = X(pts.length-1), ly = Y(pts[pts.length-1].v);
  x.beginPath(); x.arc(lx,ly,4.5,0,7); x.fillStyle = `rgb(${B})`; x.shadowColor = `rgb(${B})`; x.shadowBlur = 14; x.fill(); x.shadowBlur = 0;
  $('#ch-peak').textContent = '+' + fmt(max); $('#ch-last').textContent = '+' + fmt(pts[pts.length-1].v); $('#ch-pts').textContent = pts.length;
  const mins = Math.round((pts[pts.length-1].t - pts[0].t)/60000);
  $('#chart-range').textContent = mins < 1 ? 'last minute' : `last ${mins} min`;
}

/* ---------- logs ---------- */
function logEl(l){
  const d = document.createElement('div'); d.className = 'log-line';
  d.innerHTML = `<span class="log-ts">${esc(l.time)}</span><span class="log-msg ${esc(l.level)}">${esc(l.message)}</span>`;
  return d;
}
function logPass(l){
  if(S.logLevel !== 'all' && l.level !== S.logLevel) return false;
  if(S.logQ && !(String(l.message)+' '+l.time).toLowerCase().includes(S.logQ)) return false;
  return true;
}
function rebuildLogs(){
  const box = $('#log-stream'); box.innerHTML = '';
  const frag = document.createDocumentFragment();
  S.buf.filter(logPass).forEach(l => frag.appendChild(logEl(l)));
  box.appendChild(frag); box.scrollTop = box.scrollHeight;
  $('#log-count').textContent = S.buf.length;
}
function ingestLogs(logs){
  const box = $('#log-stream'), total = logs.length;
  if(total < S.lastLogCount || !S.logsInit){
    S.buf = logs.slice(); S.logsInit = true; S.lastLogCount = total; rebuildLogs(); return;
  }
  if(total > S.lastLogCount){
    const fresh = logs.slice(S.lastLogCount);
    S.buf.push(...fresh); S.lastLogCount = total;
    const frag = document.createDocumentFragment();
    fresh.filter(logPass).forEach(l => frag.appendChild(logEl(l)));
    box.appendChild(frag);
    if(!S.logPaused) box.scrollTop = box.scrollHeight;
    while(box.children.length > 600) box.removeChild(box.firstChild);
    $('#log-count').textContent = S.buf.length;
    if(fresh.some(l => l.level==='error')) beep(160,.18,'sawtooth',.06);
  }
}
function clearLogs(){ S.buf = []; $('#log-stream').innerHTML=''; $('#log-count').textContent = 0; toast('Log view cleared','info',1400); }
function exportLogs(){
  if(!S.buf.length) return toast('Nothing to export','warn');
  const txt = S.buf.map(l => `[${l.time}] ${String(l.level).toUpperCase().padEnd(7)} ${l.message}`).join('\n');
  const a = document.createElement('a');
  a.href = URL.createObjectURL(new Blob([txt],{type:'text/plain'}));
  a.download = `codexgojo-logs-${Date.now()}.txt`; document.body.appendChild(a); a.click(); a.remove();
  toast('Logs exported','ok');
}

/* ---------- polling ---------- */
async function fetchStats(force){
  if(S.isFetching && !force) return;
  S.isFetching = true;
  const btn = $('#btn-refresh');
  if(force) btn.innerHTML = '<i class="fa-solid fa-circle-notch fa-spin"></i> Refreshing';
  let data = null;
  try{
    if(S.demo && S.fails > -1){
      data = demo.tick();
      // keep probing the real backend; if it answers, drop demo mode
      if(S.demoAuto && Date.now() - (S.lastProbe||0) > 15000){
        S.lastProbe = Date.now();
        try{ const r = await fetch('/api/stats',{cache:'no-store'}); if(r.ok){ data = await r.json(); S.demo = false; S.fails = 0; S.logsInit = false; setConn('live'); toast('Backend connected','ok'); } }catch(e){}
      }
    } else {
      const t0 = performance.now();
      const res = await fetch('/api/stats',{cache:'no-store'});
      if(!res.ok) throw new Error('HTTP '+res.status);
      data = await res.json();
      $('#ping').textContent = 'ping ' + Math.round(performance.now()-t0) + 'ms';
      S.fails = 0; setConn('live');
    }
  }catch(err){
    S.fails++;
    console.error('Failed to fetch stats:', err);
    if(S.fails >= 2 && !S.demo){
      S.demo = true; S.demoAuto = true; S.logsInit = false; S.lastLogCount = 0; demo.init(); setConn('demo');
      toast('Backend not reachable — running in DEMO mode','warn',4500);
      data = demo.snapshot();
    } else setConn('off');
  }
  if(data){
    if(S.demo) $('#ping').textContent = 'ping sim';
    S.accounts = data.accounts;
    S.history.push({t:Date.now(), v:data.total_gained_exp}); if(S.history.length > 240) S.history.shift();
    // level-up detection
    const ups = new Set();
    data.accounts.forEach(a => { const k = String(a.uid), prev = S.levels[k]; if(prev !== undefined && a.level > prev) ups.add(k); S.levels[k] = a.level; });
    if(ups.size){
      S.levelUps = ups; jingle(); confetti(160);
      data.accounts.filter(a => ups.has(String(a.uid))).forEach(a => toast(`${a.nickname} reached level ${a.level}!`,'ok',4200));
    }
    updateStats(data); renderAccounts(ups.size>0); drawChart(); ingestLogs(data.logs || []);
  }
  S.isFetching = false;
  if(force) btn.innerHTML = '<i class="fa-solid fa-rotate"></i> Refresh';
}
(function loop(){ fetchStats(false).finally(() => setTimeout(loop, S.demo ? 2500 : 5000)); })();

/* ---------- uptime / clock ---------- */
setInterval(() => {
  const sec = Math.floor((Date.now()-S.start)/1000);
  $('#stat-uptime').textContent = `${pad(Math.floor(sec/3600))}:${pad(Math.floor(sec%3600/60))}:${pad(sec%60)}`;
  const d = new Date(); $('#clock').textContent = `${pad(d.getHours())}:${pad(d.getMinutes())}:${pad(d.getSeconds())}`;
}, 1000);

/* ---------- ticker ---------- */
(function(){
  const items = ['<b>CODEXGOJO</b> // multi-match engine armed','auto level-up loop running','press <b>Ctrl K</b> for the command palette','try the Konami code','themes: neon · blood · matrix · ice','<b>CODEXGOJO</b> never sleeps'];
  $('#ticker').innerHTML = items.concat(items).map(t => `<span>${t}</span>`).join('');
})();

/* ---------- events ---------- */
$('#acc-search').addEventListener('input', e => { S.q = e.target.value.trim(); renderAccounts(true); });
$('#acc-sort').value = S.sort;
$('#acc-sort').addEventListener('change', e => { S.sort = e.target.value; store.set('sort',S.sort); renderAccounts(true); });
$('#status-chips').addEventListener('click', e => { const b = e.target.closest('.chip'); if(!b) return; S.status = b.dataset.s; $$('#status-chips .chip').forEach(c=>c.classList.toggle('on',c===b)); renderAccounts(true); });
$('#log-chips').addEventListener('click', e => { const b = e.target.closest('.chip'); if(!b) return; S.logLevel = b.dataset.l; $$('#log-chips .chip').forEach(c=>c.classList.toggle('on',c===b)); rebuildLogs(); });
$('#log-search').addEventListener('input', e => { S.logQ = e.target.value.trim().toLowerCase(); rebuildLogs(); });
$('#log-pause').addEventListener('click', e => { S.logPaused = !S.logPaused; const b = e.currentTarget; b.classList.toggle('on', S.logPaused); b.innerHTML = `<i class="fa-solid ${S.logPaused?'fa-play':'fa-pause'}"></i>`; });
$('#v-grid').onclick = () => setView('grid'); $('#v-list').onclick = () => setView('list');
$('#accounts-container').addEventListener('click', e => {
  const copyEl = e.target.closest('[data-copy]');
  if(copyEl){ copyText(copyEl.dataset.copy); return; }
  const b = e.target.closest('[data-act]'); if(!b) return;
  const uid = b.dataset.uid, act = b.dataset.act;
  if(act==='copy') copyText(uid);
  else if(act==='refresh'){ b.querySelector('i').classList.add('fa-spin'); refreshAccountInfo(uid); }
  else if(act==='delete') deleteAccount(uid);
});
function copyText(t){
  const done = () => { toast('Copied '+t,'ok',1400); beep(1200,.05); };
  if(navigator.clipboard && navigator.clipboard.writeText) navigator.clipboard.writeText(t).then(done).catch(()=>fallbackCopy(t,done));
  else fallbackCopy(t,done);
}
function fallbackCopy(t,done){ const ta = document.createElement('textarea'); ta.value = t; document.body.appendChild(ta); ta.select(); try{ document.execCommand('copy'); done(); }catch(e){ toast('Copy failed','err'); } ta.remove(); }
$$('.overlay').forEach(o => o.addEventListener('mousedown', e => { if(e.target === o) o.classList.remove('on'); }));

/* ---------- command palette ---------- */
const CMDS = [
  {i:'fa-plus',t:'Add account',k:'A',f:openAddModal},
  {i:'fa-file-import',t:'Bulk import accounts',k:'',f:()=>{openAddModal();setBulk(true);}},
  {i:'fa-rotate',t:'Refresh data',k:'R',f:()=>fetchStats(true)},
  {i:'fa-arrows-rotate',t:'Refresh ALL accounts',k:'',f:refreshAll},
  {i:'fa-palette',t:'Cycle theme',k:'T',f:cycleTheme},
  {i:'fa-wand-magic-sparkles',t:'Toggle effects',k:'F',f:toggleFx},
  {i:'fa-volume-high',t:'Toggle sound',k:'M',f:toggleSound},
  {i:'fa-table-cells-large',t:'Switch grid / list view',k:'G',f:toggleView},
  {i:'fa-download',t:'Export logs',k:'',f:exportLogs},
  {i:'fa-broom',t:'Clear log view',k:'',f:clearLogs},
  {i:'fa-up-right-and-down-left-from-center',t:'Toggle fullscreen',k:'',f:()=>{ if(document.fullscreenElement) document.exitFullscreen(); else document.documentElement.requestFullscreen&&document.documentElement.requestFullscreen(); }},
  {i:'fa-champagne-glasses',t:'Fire confetti',k:'',f:()=>{confetti(220);jingle();}},
  {i:'fa-rainbow',t:'Toggle rainbow mode',k:'',f:toggleRainbow},
  {i:'fa-keyboard',t:'Show shortcuts',k:'?',f:()=>{closeAll();$('#help-modal').classList.add('on');}},
];
let cmdSel = 0, cmdShown = CMDS;
function renderCmds(){
  $('#cmd-list').innerHTML = cmdShown.map((c,i)=>`<div class="cmd ${i===cmdSel?'sel':''}" data-i="${i}"><i class="fa-solid ${c.i}"></i><span>${c.t}</span>${c.k?`<span class="kbd">${c.k}</span>`:''}</div>`).join('') || '<div class="empty" style="padding:24px">No command found</div>';
  const s = $('#cmd-list .sel'); if(s) s.scrollIntoView({block:'nearest'});
}
function openPalette(){ closeAll(); $('#palette-modal').classList.add('on'); const i = $('#cmd-input'); i.value=''; cmdShown = CMDS; cmdSel = 0; renderCmds(); setTimeout(()=>i.focus(),30); }
function runCmd(i){ const c = cmdShown[i]; if(!c) return; closeAll(); setTimeout(c.f, 30); }
$('#cmd-input').addEventListener('input', e => { const q = e.target.value.toLowerCase(); cmdShown = CMDS.filter(c=>c.t.toLowerCase().includes(q)); cmdSel = 0; renderCmds(); });
$('#cmd-input').addEventListener('keydown', e => {
  if(e.key==='ArrowDown'){ e.preventDefault(); cmdSel = Math.min(cmdShown.length-1, cmdSel+1); renderCmds(); }
  else if(e.key==='ArrowUp'){ e.preventDefault(); cmdSel = Math.max(0, cmdSel-1); renderCmds(); }
  else if(e.key==='Enter'){ e.preventDefault(); runCmd(cmdSel); }
});
$('#cmd-list').addEventListener('click', e => { const c = e.target.closest('.cmd'); if(c) runCmd(+c.dataset.i); });

/* ---------- keyboard + easter egg ---------- */
function toggleRainbow(){ document.documentElement.classList.toggle('rainbow'); }
const KONAMI = ['ArrowUp','ArrowUp','ArrowDown','ArrowDown','ArrowLeft','ArrowRight','ArrowLeft','ArrowRight','b','a']; let kpos = 0;
document.addEventListener('keydown', e => {
  const typing = /INPUT|TEXTAREA|SELECT/.test((e.target.tagName||''));
  if((e.ctrlKey||e.metaKey) && e.key.toLowerCase()==='k'){ e.preventDefault(); openPalette(); return; }
  if(e.key==='Escape'){ closeAll(); return; }
  if(typing) return;
  kpos = (e.key.toLowerCase() === KONAMI[kpos].toLowerCase()) ? kpos+1 : (e.key===KONAMI[0] ? 1 : 0);
  if(kpos === KONAMI.length){ kpos = 0; toggleRainbow(); confetti(300); jingle(); toast('GOJO MODE UNLOCKED — Infinite Void','ok',4500); return; }
  if(e.ctrlKey||e.metaKey||e.altKey) return;
  const k = e.key.toLowerCase();
  if(k==='a'){ e.preventDefault(); openAddModal(); }
  else if(k==='r') fetchStats(true);
  else if(k==='t') cycleTheme();
  else if(k==='f') toggleFx();
  else if(k==='m') toggleSound();
  else if(k==='g') toggleView();
  else if(k==='/'){ e.preventDefault(); $('#acc-search').focus(); }
  else if(e.key==='?'){ closeAll(); $('#help-modal').classList.add('on'); }
});

/* ---------- boot sequence ---------- */
(function boot(){
  const el = $('#boot'), pre = $('#boot-text');
  const finish = () => { el.classList.add('done'); setTimeout(()=>el.remove(), 600); };
  if(reduceMotion || store.get('bootSeen_'+new Date().toDateString(), false) === true){ finish(); return; }
  store.set('bootSeen_'+new Date().toDateString(), true);
  const lines = ['> initializing CODEXGOJO core …','> loading multi-match engine ........ OK','> arming level-up loop ............. OK','> linking dashboard to backend ..... OK','> all systems GO'];
  let i = 0;
  const next = () => { if(!document.body.contains(el)) return; if(i < lines.length){ pre.textContent += lines[i++] + '\n'; setTimeout(next, 260); } else setTimeout(finish, 450); };
  next(); el.onclick = finish;
})();

/* ---------- init ---------- */
applyTheme(); applyFx(); applySound(); setView(S.view); rainInit(); drawChart();
</script>
</body>
</html>
"""

class EmbeddedBotState:
    def __init__(self):
        self.accounts = {}
        self.account_credentials = {}
        self.account_workers = {}
        self.refresh_callbacks = {}
        self.logs = []
        self._paused = set()
        self._stored_accounts = {}
        self.started_at = time.time()
        self._load_accounts()

    def _load_accounts(self):
        try:
            accounts_path = globals().get("ACCOUNTS_FILE", "accounts.json")
            if os.path.exists(accounts_path):
                data = json.loads(open(accounts_path, encoding="utf-8").read() or "[]")
                if isinstance(data, list):
                    for a in data:
                        uid = str(a.get("uid") or a.get("account_id") or "")
                        if uid:
                            self._stored_accounts[uid] = dict(a)
                            self.accounts[uid] = self._normal_account(uid, a)
                            self.account_credentials[uid] = dict(a)
        except Exception as e:
            print(f"[dashboard] accounts load error: {e}")

    def _normal_account(self, uid, data=None):
        data = data or {}
        exp = int(data.get("exp", data.get("current_exp", 0)) or 0)
        return {
            "uid": str(uid), "nickname": data.get("nickname", f"Player_{uid}"),
            "region": data.get("region", "BD"), "status": data.get("status", "ONLINE"),
            "active_matches": int(data.get("active_matches", 0) or 0),
            "initial_exp": int(data.get("initial_exp", exp) or 0),
            "current_exp": exp, "gained_exp": int(data.get("gained_exp", 0) or 0),
            "level": int(data.get("level", 1) or 1),
            "matches_played": int(data.get("matches_played", 0) or 0),
            "last_match_time": data.get("last_match_time", ""),
            "likes": int(data.get("likes", 0) or 0),
        }

    def _save_accounts(self):
        try:
            rows = list(self._stored_accounts.values())
            accounts_path = globals().get("ACCOUNTS_FILE", "accounts.json")
            tmp = accounts_path + ".tmp"
            with open(tmp, "w", encoding="utf-8") as f: json.dump(rows, f, indent=2)
            os.replace(tmp, accounts_path)
        except Exception as e:
            self.log(f"Could not save accounts: {e}", "error")

    def log(self, message, level="info"):
        self.logs.append({"time": datetime.now().strftime("%H:%M:%S"), "message": str(message), "level": str(level).lower()})
        self.logs = self.logs[-500:]

    def register_account(self, uid, nickname="Unknown", region="BD", level=1, exp=0, likes=0, **kwargs):
        uid = str(uid)
        old = self.accounts.get(uid, {})
        initial = int(old.get("initial_exp", exp) or 0)
        self.accounts[uid] = self._normal_account(uid, {
            **old, "nickname": nickname or old.get("nickname", "Unknown"),
            "region": region or old.get("region", "BD"), "level": level, "exp": exp,
            "initial_exp": initial, "gained_exp": max(0, int(exp or 0)-initial), "likes": likes,
            "status": old.get("status", "CONNECTING")
        })
        self.log(f"Account profile updated: {uid}", "success")

    def update_status(self, uid, status, active_matches=0):
        uid = str(uid)
        if uid not in self.accounts: self.accounts[uid] = self._normal_account(uid)
        self.accounts[uid]["status"] = str(status).upper()
        self.accounts[uid]["active_matches"] = int(active_matches or 0)

    def update_exp(self, uid, exp, level=None):
        uid = str(uid)
        if uid not in self.accounts: self.accounts[uid] = self._normal_account(uid)
        a = self.accounts[uid]
        a["current_exp"] = int(exp or 0)
        a["exp"] = int(exp or 0)
        a["gained_exp"] = max(0, a["current_exp"] - int(a.get("initial_exp", 0) or 0))
        if level is not None: a["level"] = int(level or 1)

    def increment_match(self, uid):
        uid = str(uid)
        if uid not in self.accounts: self.accounts[uid] = self._normal_account(uid)
        self.accounts[uid]["matches_played"] += 1
        self.accounts[uid]["last_match_time"] = datetime.now().strftime("%Y-%m-%d %H:%M:%S")

    def is_paused(self, uid): return str(uid) in self._paused

    def snapshot(self):
        accs = list(self.accounts.values())
        return {
            "accounts": accs, "total_accounts": len(accs),
            "total_gained_exp": sum(a.get("gained_exp", 0) for a in accs),
            "total_matches": sum(a.get("matches_played", 0) for a in accs),
            "uptime": int(time.time()-self.started_at), "logs": list(self.logs[-200:])
        }

bot_state = EmbeddedBotState()

async def _dashboard_squad_log(request):
    try:
        sid = int(request.match_info.get("sid", "0"))
        if sid < 0 or sid > 99:
            raise ValueError("invalid squad")
    except Exception:
        return web.Response(text="Invalid Squad number", status=400, content_type="text/plain")
    path = os.path.join("squad_logs", f"squad_{sid + 1:02d}.log")
    try:
        with open(path, "r", encoding="utf-8", errors="replace") as f:
            content = f.read()[-100000:]
    except FileNotFoundError:
        content = f"Terminal {sid + 1} / Squad {sid + 1} এর লগ এখনো তৈরি হয়নি। এই Squad-এ account যোগ করে আবার দেখুন।"
    html = "<!doctype html><meta charset='utf-8'><meta name='viewport' content='width=device-width,initial-scale=1'><title>Squad Terminal</title><style>body{background:#10131a;color:#e8edf5;font:14px monospace;padding:16px}h2{font: bold 18px sans-serif}pre{white-space:pre-wrap;overflow-wrap:anywhere;line-height:1.55}</style><h2>Terminal " + str(sid + 1) + " / Squad " + str(sid + 1) + "</h2><pre>" + content.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;") + "</pre><script>setTimeout(()=>location.reload(),5000)</script>"
    return web.Response(text=html, content_type="text/html")

async def _dashboard_stats(request):
    return web.json_response(bot_state.snapshot())

async def _dashboard_add(request):
    try: data = await request.json()
    except Exception: return web.json_response({"status":"error","error":"Invalid JSON"}, status=400)
    uid = str(data.get("uid", "")).strip()
    password = str(data.get("password", "")).strip()
    token = str(data.get("token", "")).strip()
    if not token and (not uid or not password):
        return web.json_response({"status":"error","error":"UID/password or token required"}, status=400)
    key = uid if uid else "tok_" + token[:20]
    if key in bot_state.account_workers and not bot_state.account_workers[key].done():
        return web.json_response({"status":"error","error":"Account already running"}, status=409)
    bot_state.account_credentials[key] = {"uid": uid, "password": password, "token": token}
    bot_state._stored_accounts[key] = ({"uid": uid, "password": password} if uid else {"token": token})
    # Do not create a dashboard account card using the login UID/token key.
    # The authenticated in-game account_id is registered after successful login;
    # creating a placeholder here caused one real account to appear as two IDs.
    bot_state._save_accounts()
    cb = bot_state.refresh_callbacks.get("on_account_added")
    if cb:
        try: await cb(data)
        except Exception as e:
            bot_state.log(f"Account start failed: {e}", "error")
            return web.json_response({"status":"error","error":str(e)}, status=500)
    bot_state.log(f"Account added: {key}", "success")
    return web.json_response({"status":"ok"})

async def _dashboard_delete(request):
    try: data = await request.json()
    except Exception: data = {}
    uid = str(data.get("uid", "")).strip()
    if not uid: return web.json_response({"status":"error","error":"UID required"}, status=400)
    task = bot_state.account_workers.pop(uid, None)
    if task and not task.done(): task.cancel()
    bot_state.accounts.pop(uid, None)
    bot_state.account_credentials.pop(uid, None)
    bot_state._stored_accounts.pop(uid, None)
    bot_state._save_accounts()
    bot_state.log(f"Account deleted: {uid}", "warning")
    return web.json_response({"status":"ok"})

async def _dashboard_refresh(request):
    try: data = await request.json()
    except Exception: data = {}
    uid = str(data.get("uid", "")).strip()
    cb = bot_state.refresh_callbacks.get("on_refresh_account")
    if uid and cb:
        try: await cb(uid)
        except Exception as e: return web.json_response({"status":"error","error":str(e)}, status=500)
    return web.json_response({"status":"ok"})

async def start_web_dashboard(host=None, port=None):
    host = host or globals().get("WEB_HOST", "0.0.0.0")
    port = port or globals().get("WEB_PORT", 20333)
    app = web.Application()
    app.router.add_get("/", lambda request: web.Response(text=INDEX_HTML, content_type="text/html"))
    app.router.add_get("/index.html", lambda request: web.Response(text=INDEX_HTML, content_type="text/html"))
    app.router.add_get("/api/stats", _dashboard_stats)
    app.router.add_get("/api/squad-log/{sid}", _dashboard_squad_log)
    app.router.add_post("/api/account/add", _dashboard_add)
    app.router.add_post("/api/account/delete", _dashboard_delete)
    app.router.add_post("/api/account/refresh", _dashboard_refresh)
    runner = web.AppRunner(app)
    await runner.setup()
    site = web.TCPSite(runner, host, port)
    await site.start()
    print(f"[dashboard] Running at http://{host}:{port}")
    return runner

# ═════════════════════ END EMBEDDED DASHBOARD ═════════════════════


# ═══════════════════════════ CONFIG ═══════════════════════════
WEB_HOST = "0.0.0.0"
WEB_PORT = 20333
ACCOUNTS_FILE = "accounts.json"
TOKEN_CACHE_FILE = "token_cache.json"
DEVICES_FILE = "devices.json"
TOKEN_CACHE_TTL = 4500

START_MATCH_INTERVAL    = 4.0
NEW_MATCH_DELAY         = 6.0
MAX_MATCH_DURATION      = 3000
MATCH_IDLE_TIMEOUT      = 90.0
EXP_REFRESH_INTERVAL    = 20.0
EXP_REFRESH_AFTER_MATCH_DELAY = 9.0
MAX_CONSECUTIVE_PARSE_FAILURES = 5
NON_MATCH_RECONNECT_DELAY      = 1.0

# ⭐ Only Battle Royale
BR_MODE_ID             = 1
BR_MAP_ID              = 1

ANTI_AFK_MIN_INTERVAL  = 1.8
ANTI_AFK_MAX_INTERVAL  = 3.5

MATCH_SEARCH_TIMEOUT   = 90.0
MATCH_WATCHDOG_CHECK   = 30.0
REGION_ROTATION_LIST   = ["ID", "SG", "TH", "MY", "VN", "PH"]
REGION_ROTATE_EVERY_N  = 2
MAX_SEARCH_ATTEMPTS    = 25

SAFE_PLAY_MODE        = True
BYPASS_TIMING_JITTER  = True
BYPASS_PACKET_JITTER  = True
BYPASS_HELLO_DELAY    = True
BYPASS_KA_JITTER      = True

ENABLE_SPEED_MOVEMENT       = True
MOVEMENT_SPEED_MIN          = 1.0
MOVEMENT_SPEED_MAX          = 1.4
MOVEMENT_PATTERN            = "circle"
MOVEMENT_TICK_MS            = 240
MOVEMENT_RADIUS             = 180
MOVEMENT_UPDATE_SPEED_EVERY = 4.0
MOVEMENT_STATE_IDLE_CHANCE   = 0.10
MOVEMENT_STATE_WALK_CHANCE   = 0.28
MOVEMENT_STATE_RUN_CHANCE    = 0.32
MOVEMENT_STATE_SPRINT_CHANCE = 0.10
MOVEMENT_STATE_JUMP_CHANCE   = 0.08
MOVEMENT_STATE_CROUCH_CHANCE = 0.06
MOVEMENT_STATE_PRONE_CHANCE  = 0.06

ENABLE_HTTP_PING = True
PING_INTERVAL    = 20.0
PING_TIMEOUT     = 8.0
PING_URL         = "https://loginbp.ppmainecoonghj.com/Ping"
PING_REAL_IP     = "103.109.214.211"

FALLBACK_UID = ""
FALLBACK_PASSWORD = ""

# ═══════════════════════════ SQUAD CONFIG ═══════════════════════════
TEAM_MODE               = True
TEAM_SIZE               = 4
TEAM_PEER_WAIT_TIMEOUT  = 90.0
TEAM_CREATE_WAIT        = 4.0
TEAM_INVITE_CYCLE_WAIT  = 4.0
TEAM_INVITE_MAX_TIME    = 120.0
TEAM_HEARTBEAT_INTERVAL = 3.0
TEAM_IDLE_ITERS_TEAM    = 1800
TEAM_MEMBER_START_DELAY = 20.0
TEAM_FINAL_WAIT         = 8.0
TEAM_SIZE = 4
TEAM_READY_DELAY = 5.0
_accept_friend_request = True
DEBUG_TEAM_PACKETS      = True

# ═══════════════════════════ ANTI-BAN ═══════════════════════════
def bypass_jitter(base, spread=0.35):
    if not (SAFE_PLAY_MODE and BYPASS_TIMING_JITTER): return base
    return max(0.05, base + random.uniform(-spread, spread))

def bypass_packet_jitter(base, spread_ratio=0.35):
    if not (SAFE_PLAY_MODE and BYPASS_PACKET_JITTER): return base
    return max(0.1, base + random.uniform(-base * spread_ratio, base * spread_ratio))

def bypass_hello_delay():
    if not (SAFE_PLAY_MODE and BYPASS_HELLO_DELAY): return 0.0
    return random.uniform(0.05, 0.45)

def bypass_ka_jitter(base=5.0):
    if not (SAFE_PLAY_MODE and BYPASS_KA_JITTER): return base
    return max(3.0, base + random.uniform(-0.8, 1.2))

def bypass_human_reconnect_delay(attempt):
    if not (SAFE_PLAY_MODE and BYPASS_TIMING_JITTER): return min(attempt * 0.5, 2.0)
    return max(0.05, min(attempt * 0.5, 2.0) + random.uniform(-0.4, 0.7))

# ═══════════════════════════ DEVICE ═══════════════════════════
def get_device_for_account(account_identifier):
    devices = {}
    if os.path.exists(DEVICES_FILE):
        try:
            with open(DEVICES_FILE, "r", encoding="utf-8") as f:
                devices = json.load(f)
        except Exception: pass
    key = str(account_identifier)
    if key in devices: return devices[key]
    dev_list = [
        ("Samsung", "SM-G998B", "Adreno (TM) 660", "Android OS 12 / API-31"),
        ("Xiaomi", "2201122G", "Adreno (TM) 730", "Android OS 13 / API-33"),
        ("Realme", "RMX3700", "Mali-G710", "Android OS 14 / API-34"),
        ("OnePlus", "CPH2451", "Adreno (TM) 740", "Android OS 13 / API-33"),
        ("OPPO", "CPH2611", "Adreno (TM) 720", "Android OS 14 / API-34"),
    ]
    brand, model, gpu, os_ver = random.choice(dev_list)
    dev = {
        "unique_device_id": f"Google|{uuid.uuid4()}",
        "brand": brand, "model": model, "gpu_renderer": gpu, "system_software": os_ver,
        "screen_width": random.choice([1080, 1440, 720]),
        "screen_height": random.choice([2400, 3200, 1600]),
        "screen_dpi": str(random.randint(300, 420)),
        "memory": random.randint(2800, 6500),
        "processor_details": f"ARM64 FP ASIMD AES | {random.randint(2200, 3200)} | {random.randint(6, 12)}",
        "client_ip": f"{random.randint(103, 223)}.{random.randint(10, 250)}.{random.randint(10, 250)}.{random.randint(10, 250)}",
    }
    devices[key] = dev
    try:
        with open(DEVICES_FILE, "w", encoding="utf-8") as f:
            json.dump(devices, f, indent=2)
    except Exception: pass
    return dev

# ═══════════════════════════ DNS ═══════════════════════════
_DNS_CACHE: Dict[str, Tuple[str, float]] = {}
_DNS_CACHE_TTL = 300.0

async def resolve_host_cloudflare(hostname):
    if not hostname: return hostname
    parts = hostname.split('.')
    if len(parts) == 4 and all(p.isdigit() for p in parts): return hostname
    now = time.time()
    if hostname in _DNS_CACHE:
        ip, exp = _DNS_CACHE[hostname]
        if now < exp: return ip
    try:
        loop = asyncio.get_running_loop()
        info = await loop.getaddrinfo(hostname, None, family=socket.AF_INET)
        if info:
            ip = info[0][4][0]
            _DNS_CACHE[hostname] = (ip, now + _DNS_CACHE_TTL)
            return ip
    except Exception: pass
    return hostname

def optimize_tcp_socket(sock):
    try:
        sock.setsockopt(socket.IPPROTO_TCP, socket.TCP_NODELAY, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_KEEPALIVE, 1)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 65536)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 65536)
    except Exception: pass

def optimize_udp_socket(sock):
    try:
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_RCVBUF, 131072)
        sock.setsockopt(socket.SOL_SOCKET, socket.SO_SNDBUF, 131072)
    except Exception: pass

# ═══════════════════════════ HTTP CLIENT ═══════════════════════════
client = httpx.AsyncClient(verify=False, timeout=10.0,
    limits=httpx.Limits(max_connections=100, max_keepalive_connections=50))
headers = {
    'User-Agent': 'UnityPlayer/2018.4.12f1 (UnityWebRequest/1.0, libcurl/8.5.0-DEV)',
    'Connection': 'Keep-Alive', 'Accept-Encoding': 'gzip',
    'Content-Type': 'application/x-www-form-urlencoded',
    'X-Unity-Version': '2018.4.12f1', 'X-GA-SV': '1789535859',
    'X-GA': 'v1 1', 'ReleaseVersion': 'OB55'
}

AES_KEY = b'Yg&tc%DEuh6%Zc^8'
AES_IV  = b'6oyZDr22E3ychjM%'

CRC7_TABLE = bytes([
    0,9,18,27,36,45,54,63,72,65,90,83,108,101,126,119,25,16,11,2,61,52,47,38,
    81,88,67,74,117,124,103,110,50,59,32,41,22,31,4,13,122,115,104,97,94,87,76,69,
    43,34,57,48,15,6,29,20,99,106,113,120,71,78,85,92,100,109,118,127,64,73,82,91,
    44,37,62,55,8,1,26,19,125,116,111,102,89,80,75,66,53,60,39,46,17,24,3,10,
    86,95,68,77,114,123,96,105,30,23,12,5,58,51,40,33,79,70,93,84,107,98,121,112,
    7,14,21,28,35,42,49,56,65,72,83,90,101,108,119,126,9,0,27,18,45,36,63,54,
    88,81,74,67,124,117,110,103,16,25,2,11,52,61,38,47,115,122,97,104,87,94,69,76,
    59,50,41,32,31,22,13,4,106,99,120,113,78,71,92,85,34,43,48,57,6,15,20,29,
    37,44,55,62,1,8,19,26,109,100,127,118,73,64,91,82,60,53,46,39,24,17,10,3,
    116,125,102,111,80,89,66,75,23,30,5,12,51,58,33,40,95,86,77,68,123,114,105,96,
    14,7,28,21,42,35,56,49,70,79,84,93,98,107,112,121,
])
_DELTA = 0x9E3779B9
_ROUNDS = 16
_FIELD_SIZES = {0:1, 1:2, 2:2, 3:1, 4:2}
_FIELD_NAMES = {0:"sendOption", 1:"cmd", 2:"orderId", 3:"flags", 4:"length"}

# ═══════════════════════════ LOG ═══════════════════════════
class Colors:
    GREEN='\033[92m'; FAIL='\033[91m'; WARNING='\033[93m'
    CYAN='\033[96m'; MAGENTA='\033[95m'; WHITE='\033[97m'; ENDC='\033[0m'

def _write_squad_log(message):
    """Write worker output to a per-squad log file without breaking console output."""
    sid = _squad_log_id_context.get()
    if sid is None:
        return
    try:
        os.makedirs("squad_logs", exist_ok=True)
        path = os.path.join("squad_logs", f"squad_{int(sid)+1:02d}.log")
        stamp = datetime.now().strftime("%H:%M:%S")
        with open(path, "a", encoding="utf-8") as f:
            f.write(f"[{stamp}] {message}\n")
    except Exception:
        pass

def print_colored(t, c=Colors.WHITE):
    try:
        sid = _squad_log_id_context.get()
        shown = f"[SQUAD-{int(sid)+1:02d}] {t}" if sid is not None else t
        print(f"{c}{shown}{Colors.ENDC}")
        _write_squad_log(t)
    except Exception:
        try: print(f"{c}{t}{Colors.ENDC}")
        except Exception: pass

def print_success(t):
    print_colored(f"[+] {t}", Colors.GREEN)
    try: bot_state.log(t, "success")
    except Exception: pass

def print_error(t):
    print_colored(f"[-] {t}", Colors.FAIL)
    try: bot_state.log(t, "error")
    except Exception: pass

def print_warning(t):
    print_colored(f"[!] {t}", Colors.WARNING)
    try: bot_state.log(t, "warning")
    except Exception: pass

def print_info(t):
    print_colored(f"[i] {t}", Colors.CYAN)
    try: bot_state.log(t, "info")
    except Exception: pass

def get_proto_field(d, key, default=None):
    if not d or not isinstance(d, dict): return default
    if key in d:
        v = d[key].get('data'); return v if v is not None else default
    if str(key) in d:
        v = d[str(key)].get('data'); return v if v is not None else default
    return default

# ═══════════════════════════ MATCH COUNTER ═══════════════════════════
_match_counters: Dict[str, int] = {}
_match_counter_lock = asyncio.Lock()

async def _inc_match(uid):
    async with _match_counter_lock:
        _match_counters[uid] = _match_counters.get(uid, 0) + 1
        return _match_counters[uid]

async def _dec_match(uid):
    async with _match_counter_lock:
        if uid in _match_counters and _match_counters[uid] > 0:
            _match_counters[uid] -= 1
        return _match_counters.get(uid, 0)

async def _get_match_count(uid):
    async with _match_counter_lock:
        return _match_counters.get(uid, 0)

async def _get_total_match_count():
    async with _match_counter_lock:
        return sum(_match_counters.values())

# ═══════════════════════════ ISOLATED SQUAD STATES ═══════════════════════════
def _new_team_state():
    return {
        "peers": {}, "leader_uid": None, "team_code": None, "pk_code": None,
        "members": set(), "members_lock": asyncio.Lock(), "lock": asyncio.Lock(),
    }

_default_team_state = _new_team_state()
_squad_state_context = ContextVar("squad_state_context", default=_default_team_state)

class _SquadStateProxy:
    """Resolve reads and writes against the squad assigned to the current account task."""
    def __getitem__(self, key):
        return _squad_state_context.get()[key]
    def __setitem__(self, key, value):
        # Team code paths update individual keys (for example team_code/pk_code).
        # Route those writes to the active squad's own state, not a shared global.
        _squad_state_context.get()[key] = value
    def __delitem__(self, key):
        del _squad_state_context.get()[key]
    def get(self, key, default=None):
        return _squad_state_context.get().get(key, default)

_team_state = _SquadStateProxy()
_squad_slots = []  # each item tracks up to TEAM_SIZE account identities
_squad_identity_map = {}

def _assign_squad(identity):
    identity = str(identity)
    if identity in _squad_identity_map:
        return _squad_identity_map[identity]
    for index, members in enumerate(_squad_slots):
        if len(members) < TEAM_SIZE:
            members.add(identity)
            _squad_identity_map[identity] = index
            return index
    _squad_slots.append({identity})
    index = len(_squad_slots) - 1
    _squad_identity_map[identity] = index
    return index

async def _run_account_in_squad(squad_id, worker, *args):
    squad_id = max(0, int(squad_id))
    # Keep one stable, isolated state per squad. Context is inherited by child tasks.
    while len(_squad_states) <= squad_id:
        _squad_states.append(_new_team_state())
    state = _squad_states[squad_id]
    state_token = _squad_state_context.set(state)
    log_token = _squad_log_id_context.set(squad_id)
    try:
        print_info(f"Worker started; squad members assigned={len(_squad_slots[squad_id]) if squad_id < len(_squad_slots) else 0}")
        await worker(*args)
    except asyncio.CancelledError:
        print_warning("Worker cancelled")
        raise
    except Exception as exc:
        print_error(f"Worker crashed: {type(exc).__name__}: {exc}")
        raise
    finally:
        _squad_log_id_context.reset(log_token)
        _squad_state_context.reset(state_token)

_squad_states = [_default_team_state]

async def _team_member_join(uid):
    uid = str(uid)
    async with _team_state["members_lock"]:
        before = len(_team_state["members"])
        _team_state["members"].add(uid)
        after = len(_team_state["members"])
    if after != before:
        print_success(f"[TEAM] 👥 In team ({after}/{TEAM_SIZE}) | joined: {uid}")
        try:
            for p_uid in list(_team_state["peers"].keys()):
                role = "LEADER" if _team_state["leader_uid"] == p_uid else "MEMBER"
                joined = p_uid in _team_state["members"]
                tag = f"IN_TEAM ({after}/{TEAM_SIZE}) [{role}]" if joined else f"JOINING ({after}/{TEAM_SIZE}) [{role}]"
                bot_state.update_status(p_uid, tag, 0)
        except Exception: pass
    return after

async def _team_member_leave(uid):
    async with _team_state["members_lock"]:
        _team_state["members"].discard(str(uid))

async def _team_member_count():
    async with _team_state["members_lock"]:
        return len(_team_state["members"])

async def _team_member_reset(keep_leader=True):
    async with _team_state["members_lock"]:
        _team_state["members"].clear()
        if keep_leader and _team_state["leader_uid"]:
            _team_state["members"].add(_team_state["leader_uid"])

# ═══════════════════════════ TOKEN CACHE ═══════════════════════════
_token_cache_memo = {}
_token_cache_memo_time = 0.0
_TOKEN_CACHE_MEMO_TTL = 5.0

def _json_serializer(obj):
    if isinstance(obj, (bytes, bytearray)): return {"__bytes_hex__": bytes(obj).hex()}
    raise TypeError(f"not serializable: {type(obj)}")

def _json_deserializer(obj):
    if isinstance(obj, dict):
        if "__bytes_hex__" in obj and len(obj) == 1:
            try: return bytes.fromhex(obj["__bytes_hex__"])
            except Exception: return b""
        return {k: _json_deserializer(v) for k, v in obj.items()}
    if isinstance(obj, list): return [_json_deserializer(x) for x in obj]
    return obj

def _load_token_cache():
    global _token_cache_memo, _token_cache_memo_time
    now = time.time()
    if _token_cache_memo and (now - _token_cache_memo_time) < _TOKEN_CACHE_MEMO_TTL:
        return _token_cache_memo
    if not os.path.exists(TOKEN_CACHE_FILE): return {}
    try:
        with open(TOKEN_CACHE_FILE, "r", encoding="utf-8") as f:
            content = f.read().strip()
        if not content: return {}
        data = json.loads(content)
        if not isinstance(data, dict): raise ValueError("root must be dict")
        parsed = _json_deserializer(data)
        _token_cache_memo = parsed; _token_cache_memo_time = now
        return parsed
    except Exception as e:
        print_error(f"Token cache corrupt -> delete: {e}")
        try: os.remove(TOKEN_CACHE_FILE)
        except Exception: pass
        return {}

def _save_token_cache(cache):
    global _token_cache_memo, _token_cache_memo_time
    try:
        tmp = TOKEN_CACHE_FILE + ".tmp"
        with open(tmp, "w", encoding="utf-8") as f:
            json.dump(cache, f, indent=2, default=_json_serializer)
        os.replace(tmp, TOKEN_CACHE_FILE)
        _token_cache_memo = cache; _token_cache_memo_time = time.time()
    except Exception as e: print_error(f"Cache save: {e}")

def cache_get(uid):
    cache = _load_token_cache()
    e = cache.get(str(uid))
    if not e: return None
    if time.time() - e.get("cached_at", 0) > TOKEN_CACHE_TTL:
        cache_invalidate(uid); return None
    if str(e.get("account_id", "")).isdigit(): e["account_id"] = int(e["account_id"])
    if not isinstance(e.get("login_payload_data"), (bytes, bytearray)):
        cache_invalidate(uid); return None
    return e

def cache_set(uid, data):
    cache = _load_token_cache()
    e = dict(data); e["cached_at"] = time.time()
    cache[str(uid)] = e; _save_token_cache(cache)
    print_success(f"[CACHE] Saved UID {uid}")

def cache_invalidate(uid):
    cache = _load_token_cache()
    if str(uid) in cache:
        del cache[str(uid)]; _save_token_cache(cache)

def _update_cache_profile(data, level, exp):
    try:
        keys = []
        if data.get('auth_uid'): keys.append(str(data['auth_uid']))
        if data.get('auth_token'): keys.append(f"tok_{data['auth_token'][:20]}")
        if not keys: return
        cache = _load_token_cache(); ch = False
        for k in keys:
            if k in cache and isinstance(cache[k], dict):
                cache[k]['level'] = level; cache[k]['exp'] = exp; ch = True
        if ch: _save_token_cache(cache)
    except Exception: pass

# ═══════════════════════════ ENCRYPTION ═══════════════════════════
async def aes_encrypt(payload, key, iv):
    return AES.new(key, AES.MODE_CBC, iv).encrypt(pad(payload, AES.block_size))

async def get_playstore_version():
    loop = asyncio.get_event_loop()
    res = await loop.run_in_executor(None, lambda: play_scraper('com.dts.freefireth', lang='hi', country='id'))
    return res.get("version")

async def version_config():
    app_version = await get_playstore_version()
    url = ("https://version.ggwhitehawk.com/live/ver.php"
           f"?version={app_version}&lang=hi&device=android&channel=android"
           "&appstore=googleplay&region=ID&whitelist_version=1.3.0&whitelist_sp_version=1.0.0")
    try:
        r = await client.get(url); r.raise_for_status()
        d = r.json()
        su = d.get("server_url"); rv = d.get("remote_version"); lr = d.get("latest_release_version")
        if not su or not rv or not lr: return None
        return lr, rv, su
    except Exception: return None

async def get_access_token(uid, password):
    url = "https://100067.connect.garena.com/oauth/guest/token/grant"
    hdrs = {
        "Host": "100067.connect.garena.com",
        "User-Agent": "Dalvik/2.1.0 (Linux; U; Android 12; SM-G998B)",
        "Content-Type": "application/x-www-form-urlencoded",
        "Accept-Encoding": "gzip, deflate, br", "Connection": "close"
    }
    data = {
        "uid": uid, "password": password, "response_type": "token", "client_type": "2",
        "client_secret": "2ee44819e9b4598845141067b281621874d0d5d7af9d8f7e00c1e54715b7d1e3",
        "client_id": "100067"
    }
    for attempt in range(5):
        try:
            r = await client.post(url, headers=hdrs, data=data)
            if r.status_code == 200:
                d = r.json()
                oid = d.get("open_id"); at = d.get("access_token"); pf = d.get("platform", 4)
                if oid and at: return oid, at, pf
            if r.status_code == 429: await asyncio.sleep(1); continue
        except Exception: pass
        await asyncio.sleep(0.5)
    return None

async def parse_results(parsed):
    out = {}
    for r in parsed:
        fd = {"wire_type": r.wire_type}
        if r.wire_type in ("varint", "string", "bytes"): fd["data"] = r.data
        elif r.wire_type == "length_delimited":
            fd["data"] = await parse_results(r.data.results)
        out[r.field] = fd
    return out

async def decode_protobuf(data):
    parsed = Parser().parse(data)
    return json.dumps(await parse_results(parsed))

def decode_protobuf_dict_safe(data):
    try:
        parsed = Parser().parse(data)
        return _recursive_dict(parsed)
    except Exception: return {}

def _recursive_dict(results):
    out = {}
    for r in results:
        fd = {"wire_type": r.wire_type}
        if r.wire_type in ("varint", "string", "bytes"): fd["data"] = r.data
        elif r.wire_type == "length_delimited":
            if hasattr(r.data, "results"): fd["data"] = _recursive_dict(r.data.results)
            elif isinstance(r.data, list): fd["data"] = _recursive_dict(r.data)
            else: fd["data"] = str(r.data)
        out[str(r.field)] = fd
    return out

def _decode_proto_manual(data):
    """Manual protobuf decode (fallback)."""
    result = {}; offset = 0; data_len = len(data)
    while offset < data_len:
        header = 0; shift = 0
        while offset < data_len:
            b = data[offset]; offset += 1
            header |= (b & 0x7F) << shift
            if not (b & 0x80): break
            shift += 7
            if shift > 28: break
        if header == 0: break
        fn = header >> 3; wt = header & 0x7
        if fn == 0: break
        if wt == 0:
            v = 0; shift = 0
            while offset < data_len:
                b = data[offset]; offset += 1
                v |= (b & 0x7F) << shift
                if not (b & 0x80): break
                shift += 7
                if shift > 63: break
            result[fn] = v
        elif wt == 2:
            length = 0; shift = 0
            while offset < data_len:
                b = data[offset]; offset += 1
                length |= (b & 0x7F) << shift
                if not (b & 0x80): break
                shift += 7
                if shift > 28: break
            if length > data_len - offset: break
            value = data[offset:offset+length]; offset += length
            try:
                s = value.decode('utf-8')
                if s and all(31 < ord(c) < 127 or ord(c) in (9,10,13) for c in s):
                    result[fn] = s
                else:
                    nested = _decode_proto_manual(value)
                    result[fn] = nested if nested else value.hex()
            except UnicodeDecodeError:
                nested = _decode_proto_manual(value)
                result[fn] = nested if nested else value.hex()
        elif wt == 5: offset += 4
        elif wt == 1: offset += 8
        else: break
    return result

# ═══════════════════════════ MANUAL PROTOBUF ENCODE ═══════════════════════════
def encode_varint(n):
    if n < 0: return b''
    out = bytearray()
    while True:
        b = n & 0x7F; n >>= 7
        if n: b |= 0x80
        out.append(b)
        if not n: break
    return bytes(out)

def build_proto(fields):
    parts = []
    for k, v in fields.items():
        if isinstance(v, dict):
            nested = build_proto(v)
            parts.append(encode_varint((k << 3) | 2) + encode_varint(len(nested)) + nested)
        elif isinstance(v, int):
            parts.append(encode_varint((k << 3) | 0) + encode_varint(v))
        elif isinstance(v, (str, bytes)):
            ev = v.encode() if isinstance(v, str) else v
            parts.append(encode_varint((k << 3) | 2) + encode_varint(len(ev)) + ev)
    return b''.join(parts)

def encrypt_api(plain_hex):
    return AES.new(AES_KEY, AES.MODE_CBC, AES_IV).encrypt(
        pad(bytes.fromhex(plain_hex), AES.block_size)).hex()

def encrypt_api_bytes(plain_bytes):
    return AES.new(AES_KEY, AES.MODE_CBC, AES_IV).encrypt(pad(plain_bytes, AES.block_size))

# ═══════════════════════════ SQUAD PROTOBUF BUILDERS ═══════════════════════════
def _pb_varint(fn, val): return encode_varint((fn << 3) | 0) + encode_varint(val)
def _pb_length(fn, val):
    enc = val.encode('utf-8') if isinstance(val, str) else val
    return encode_varint((fn << 3) | 2) + encode_varint(len(enc)) + enc

def create_proto(fields):
    packet = bytearray()
    for field, value in fields.items():
        if isinstance(field, str): field = int(field)
        if isinstance(value, dict):
            packet.extend(_pb_length(field, bytes(create_proto(value))))
        elif isinstance(value, list):
            for item in value:
                if isinstance(item, dict):
                    packet.extend(_pb_length(field, bytes(create_proto(item))))
                elif isinstance(item, str): packet.extend(_pb_length(field, item))
                elif isinstance(item, (bytes, bytearray)): packet.extend(_pb_length(field, bytes(item)))
                elif isinstance(item, bool): packet.extend(_pb_varint(field, 1 if item else 0))
                elif isinstance(item, int): packet.extend(_pb_varint(field, item))
        elif isinstance(value, bool): packet.extend(_pb_varint(field, 1 if value else 0))
        elif isinstance(value, int): packet.extend(_pb_varint(field, value))
        elif isinstance(value, str): packet.extend(_pb_length(field, value))
        elif isinstance(value, (bytes, bytearray)): packet.extend(_pb_length(field, bytes(value)))
    return bytes(packet)

def create_packet(Pk, N, K, V):
    if isinstance(K, str): K = bytes.fromhex(K) if len(K) == 32 else K.encode()
    if isinstance(V, str): V = bytes.fromhex(V) if len(V) == 32 else V.encode()
    PkEnc = AES.new(K, AES.MODE_CBC, V).encrypt(pad(bytes.fromhex(Pk), 16)).hex()
    L = len(PkEnc) // 2
    hexlen = hex(L)[2:]
    if len(hexlen) % 2 != 0: hexlen = '0' + hexlen
    pad_len = 12 - len(N) - len(hexlen)
    if pad_len < 0: pad_len = 0
    return bytes.fromhex(N + ('0' * pad_len) + hexlen + PkEnc)

# ═══════════ SQUAD PACKETS ═══════════
def create_team(key, iv, game_version="1.132.9"):
    fields = {
        1: 1, 2: {2: bytes.fromhex("01"), 3: 1, 4: 3, 5: "en",
            8: {1: "IDC3", 2: 123, 3: "ID"}, 9: 1,
            10: bytes.fromhex("01090a0b1219202729"), 11: 2, 13: 1,
            14: {1: "08FBA33B4BABE2790205390333330000009700050092005F72697EB2134DCBB2467625142201040e38e848dc0e748c3f6aa04d81000000ff1113090dcacfa16d",
                 2: 478, 3: "7e585d55", 4: "y[Z]", 6: 12, 7: "15686677735a7506101c",
                 8: str(game_version), 9: 3, 10: 1, 11: "03626253513637754174"},
            19: 329, 21: bytes.fromhex("374f521955"), 24: {1: 21},
            27: "a_6534489873065906362"}}
    return create_packet(create_proto(fields).hex(), "0515", key, iv)

def team_fresh(account_id, key, iv):
    return create_packet(create_proto({1: 72, 2: {1: int(account_id)}}).hex(), "0515", key, iv)

def invite_player_in_team(target_uid, key, iv, region="ID"):
    return create_packet(create_proto({1: 2, 2: {1: int(target_uid), 2: region, 4: 1}}).hex(),
                         "0515", key, iv)

def accept_team_invite(target_uid, group_id, key, iv):
    fields = {1: 4, 2: {1: int(target_uid), 3: int(target_uid),
        4: bytes.fromhex("0107090a0b120f19202729"), 8: 1,
        9: {1: "08FBA33B0522052002041B0222220007000C00010004000547E265AE1080779546762514110104076fa2e8770e748c3f6a68ed75000000ff08080500cacfa16d",
            2: 235, 3: {14: 80, 11: 86}, 4: "{Y\\R", 6: 13, 7: {2: 4},
            8: "1.132.9", 9: 2, 10: 1, 11: "0362625351"},
        10: str(group_id),
        11: {"1": "IDC3", "2": 107, "3": "ID"}, 13: "en", 16: "374f5219",
        20: {1: 21}, 23: "a_6534489873065906362",
        24: "https://dl-sg-production.freefiremobile.com/",
        27: {1: 2, 2: 4}}}
    return create_packet(create_proto(fields).hex(), "0515", key, iv)

def start_match_team(account_id, key, iv, region="ID"):
    fields = {1: 9, 2: {1: int(account_id), 7: {1: "IDC3", 2: 410, 3: region}}}
    return create_packet(create_proto(fields).hex(), "0515", key, iv)

def ready_for_game(uid, key, iv):
    return create_packet(create_proto({1: 15, 2: {1: uid, 2: 1}}).hex(), "0519", key, iv)

# ═══════════════════════════ MAJORLOGIN / GETLOGIN ═══════════════════════════
async def build_majorlogin_payload(open_id, access_token, platform, client_version, dev):
    try:
        p = {
            3: str(datetime.now())[:-7], 4: "free fire", 5: "1",
            7: str(client_version) if client_version else "1.132.8",
            8: str(dev.get("system_software", "Android OS 14 / API-34")),
            9: "Handheld", 10: "Telkomsel", 11: "CarrierDataNetwork",
            12: str(dev.get("screen_width", 1639)),
            13: str(dev.get("screen_height", 720)),
            14: str(dev.get("screen_dpi", 320)),
            15: str(dev.get("processor_details", "ARM64 FP ASIMD AES | 2000 | 8")),
            16: str(dev.get("memory", 5653)),
            17: str(dev.get("gpu_renderer", "Mali-G52 MC2")),
            18: "OpenGL ES 3.2 v1.r49p1-03bet0",
            19: str(dev.get("unique_device_id", f"Google|{uuid.uuid4()}")),
            20: str(dev.get("client_ip", "182.5.135.225")),
            21: "en", 22: str(open_id), 23: str(platform), 24: "Handheld",
            25: str(dev.get("model", "Xiaomi")), 26: "ID",
            29: str(access_token), 30: "1", 41: "Telkomsel", 42: "4G",
            57: "7428b253defc164018c604a1ebbfebdf", 60: "109278", 61: "55402",
            62: "868", 64: "55927", 65: "109278", 66: "55927", 67: "109278",
            73: 2,
            74: "/data/app/~~6Cw028g_ld-8Z0z2qhrOLA==/com.dts.freefireth-i3wiaEmpx8CbiRVhUMx_ag==/lib/arm64",
            76: 1,
            77: "b8e0cd5e295eee42f5860d3c86e483dd|/data/app/~~6Cw028g_ld-8Z0z2qhrOLA==/com.dts.freefireth-i3wiaEmpx8CbiRVhUMx_ag==/base.apk",
            78: 6, 79: 1, 81: "32", 83: "2019121229", 85: 3,
            86: "OpenGLES2", 87: 3071, 88: 4, 89: 14466, 93: "3rd_party",
            94: "KqsHTyb7yHjsAiyNWUUZa0DSOD6U0AhDQ76smAo1WeHHHpSmJ8KMRyRrxb2ttgJqO9YOqO/K6AORAvDMAX/qBS8+JahIkrM7kHfzlfULbgRAoZ9r",
            95: "111207", 96: "{\"cur_rate\":[60,90,120],\"support_etc2\":true}", 97: "1",
            98: "1", 99: str(platform), 100: str(platform),
            103: "1", 104: "52837", 105: "1",
            106: "https://dl.gmc.freefiremobile.com/live/ABHotUpdates/|211c933168f55902c7dfbfd8c4e2957d",
            107: "1.3fb8adbf45f44ce9",
        }
        return encrypt_api_bytes(build_proto(p))
    except Exception as e:
        print_error(f"build_majorlogin_payload: {e}"); return None

async def send_majorlogin(data, release_version, server_url):
    try:
        url = f"{server_url}MajorLogin" if server_url.endswith('/') else f"{server_url}/MajorLogin"
        hdrs = headers.copy(); hdrs["ReleaseVersion"] = str(release_version)
        r = await client.post(url, headers=hdrs, data=data)
        if r.status_code != 200:
            print_error(f"[MAJORLOGIN] HTTP {r.status_code}"); return None
        c = r.content
        if len(c) < 40: return None
        for off in [0, 64] + list(range(128)):
            try:
                m = thunderFF_pb2.MajorLoginRes(); m.ParseFromString(c[off:])
                if m.region and m.token: return m
            except Exception: continue
        return None
    except Exception as e:
        print_error(f"[MAJORLOGIN] {e}"); return None

async def send_getlogin(data, base_url, token, release_version):
    try:
        url = f"{base_url.rstrip('/')}/GetLoginData"
        hdrs = headers.copy()
        hdrs["ReleaseVersion"] = release_version
        hdrs['Authorization'] = f"Bearer {token}"
        hdrs['Host'] = "clientbp.ppmainecoonghj.com"
        r = await client.post(url, headers=hdrs, data=data)
        if r.status_code != 200: return None
        c = r.content
        rp = thunderFF_pb2.GetLoginDataRes()
        ok = False
        try:
            rp.ParseFromString(c)
            if rp.functional_addrs or rp.informational_addrs: ok = True
        except Exception: pass
        if not ok:
            for off in range(min(128, len(c))):
                try:
                    cand = thunderFF_pb2.GetLoginDataRes(); cand.ParseFromString(c[off:])
                    if cand.functional_addrs or cand.informational_addrs:
                        rp = cand; break
                except Exception: continue
        dd = {}
        try:
            parsed = Parser().parse(c.hex())
            dd = await parse_results(parsed)
        except Exception: pass
        return rp, dd
    except Exception: return None

# ═══════════════════════════ HTTP PING ═══════════════════════════
async def send_ping(account_id, token, release_version):
    try:
        try: acc = int(account_id)
        except Exception: acc = 0
        now_ms = int(time.time() * 1000)
        payload = struct.pack("<Q", acc & 0xFFFFFFFFFFFFFFFF) + struct.pack("<Q", now_ms & 0xFFFFFFFFFFFFFFFF)
        req_id = secrets.token_urlsafe(18)[:22]
        hdrs = {
            'accept': '*/*', 'accept-encoding': 'deflate, gzip',
            'authorization': f'Bearer {token}',
            'content-type': 'application/x-www-form-urlencoded',
            'releaseversion': release_version,
            'user-agent': 'UnityPlayer/2018.4.12f1',
            'x-ga': 'v1 1', 'x-ga-sv': str(int(time.time())),
            'x-railway-edge': 'sin1', 'x-railway-request-id': req_id,
            'x-real-ip': PING_REAL_IP, 'x-request-start': str(now_ms),
            'x-unity-version': '2018.4.12f1',
        }
        r = await client.post(PING_URL, headers=hdrs, content=payload, timeout=PING_TIMEOUT)
        return r.status_code == 200
    except Exception: return False

async def ping_worker(account_id, token, release_version, region="ID"):
    if not ENABLE_HTTP_PING: return
    uid_str = str(account_id); ok_count = 0; fails = 0
    try:
        await asyncio.sleep(5.0 + random.uniform(0, 2.0))
        while True:
            ok = await send_ping(uid_str, token, release_version)
            if ok:
                ok_count += 1; fails = 0
                if ok_count % 10 == 0: print_info(f"[PING] {uid_str} OK total={ok_count}")
            else:
                fails += 1
                if fails <= 3: print_warning(f"[PING] {uid_str} fail #{fails}")
            await asyncio.sleep(max(5.0, PING_INTERVAL + random.uniform(-3.0, 3.0)))
    except asyncio.CancelledError: pass
    finally: print_info(f"[PING] Stopped {uid_str} OK={ok_count}")

# ═══════════════════════════ TCP STARTUP ═══════════════════════════
async def build_tcp_startup_packet(account_id, token, server_time, key, iv, region="ID", typ='OnLine'):
    uid_hex = f"{int(account_id):016x}"
    ts_hex = f"{int(server_time):08x}"
    enc = (await aes_encrypt(token.encode(), key, iv)).hex()
    enc_len = f"{len(enc)//2:08x}"
    reg = str(region).upper() if region else "ID"
    if typ == 'OnLine':
        pfx = '7119' if reg == 'ID' else ('7114' if reg == 'IND' else '7115')
        return f"{pfx}{uid_hex}{ts_hex}00000000{enc_len}{enc}"
    pfx = '9219' if reg == 'ID' else ('9214' if reg == 'IND' else '9215')
    return f"{pfx}{uid_hex}{ts_hex}{enc_len}{enc}"

async def send_keep_alive(region="ID"):
    try:
        reg = str(region).upper() if region else "ID"
        return bytes.fromhex("0219" if reg == "ID" else ("0214" if reg == "IND" else "0215"))
    except Exception:
        return bytes.fromhex("0219")

# ═══════════════════════════ MATCH SEARCH PACKETS ═══════════════════════════
BR_HEX = (
    "080112800a0a010110013a110a044944433110aa011a064555524f50453a100a044944433210311a064555524f5045"
    "40014a0801090a0b1219202758016291090a80013038384638324246303241393637363730323031303130303030"
    "30303030303030303031363030303130303135303030323232463937454545304630303030303034363736323531"
    "34303030303030303030303030303030303030303030303030303030303030303030303030306666303030303030"
    "3030636163666131366410241afb02735d5e571400024a775d45414d1a041b1c001f11010449715f4243481a001e"
    "1d071c1703004b1a4066785c524570735c51486775421b5c5a4c07504042685a63610816054e19025e7519600147"
    "7c015165406370195f5547404e4550640103020f1304064863754268676c755f65576e40467e5f0a417a4701026d"
    "675d6e73670b1108495a4c6a0b78470b740065645e525a057258425f584a447d4e6759440c11044e7c596d7f4b62"
    "5f7d04055a47505c4e1d6b5b4107447d7201057d7f0f14084e430457674f7e517d72015172415d027473577c4d61"
    "5f79535256780911030f4d5e027a797f614165067806505d53777750475e75064257076500460817014e741e7e50"
    "78487e7a7c465e7669767153497064605a7376677773550d160148037e18675966787f4c42607a645f577e7b44"
    "1b460776026b18685d0b110205490060020f70676175654674706671797f41067346677c4e06585e780f15074c57"
    "047b40517075415f6364027259674b5b0166407f7340600407770a22047a5d5c52300b3a0a167305067162727516"
    "134208312e3133302e3232480350015ae90403626253513635686e556f4e36416456324b796f566c636f47777648"
    "4f624e56526c4d727073504b4f43654177616848494176795556497273743752737149734a7a786b324752526837"
    "7a2f637664626d504f6a73552f79626d38547a4c69586d2f474351696d494b53486833447955726f39515152756c"
    "34545350626d6d624b7949565937545671577059455372323646572f59624578507338514f706d317372785455736c"
    "30796a434144444d4f34616a654b615753366361496c554b4963797a494e396d52516f715277687939797257476d"
    "337a644345337a6a61436f492f5a585233656f65365a42647a64677654636b6b665733356e4d4c6a6a56507256"
    "4b6433523172756174394e50514150724a5546627859696c4c5a3859707336654d5447666b6649793574666a526c"
    "314d4648706b51774c6373374439656378566c41636f374e664f6d2b30654756466c443474447870677138553359"
    "5973587645384842502f70666c767a737138316a32524f4d7857437556445442492f684735625462773166456e42"
    "49725162762b636144775147696f74554e316d4c4b77734379456f4766706746614251457645672b736a764c4c78"
    "704743334c304a5344532f74526169504354553344374e6249306547516651622f5a466f4c36455630775a324d6f"
    "583932414c572f5049752f56634663584e70596b356f7966326151416a536971486a2f363276354843644f525551"
    "303578754e6171795251625653704654303137655237675255636b4966366c6f447476342b514e4a4670766d7475"
    "7077707774396a5a5974437a4b56743657726d6e36785837706658456251555434684f3758a201050803108703a2"
    "01050804108103a20105080510c001a20105081d10cc01a2010408161078a20105080e10af01a201020815"
)

async def start_game_battle_royale(region, client_version, writer, key, iv):
    packet = bytes.fromhex(BR_HEX)
    try:
        proto = CguFF_pb2.StartMatch(); proto.ParseFromString(packet)
        if hasattr(proto.main, 'region_list') and len(proto.main.region_list) > 0:
            proto.main.region_list[0].region = region
            if len(proto.main.region_list) > 1: proto.main.region_list[1].region = region
        if hasattr(proto.main, 'client_version'):
            proto.main.client_version.remote_version = client_version
        packet = proto.SerializeToString()
    except Exception: pass
    enc = (await aes_encrypt(packet, key, iv)).hex()
    plen = len(enc) // 2
    hl = hex(plen)[2:]
    hl = hl if len(hl) > 1 else "0" + hl
    reg = str(region).upper() if region else "BD"
    pfx = "031500" if reg == "ID" else ("031400" if reg == "IND" else "031500")
    final = pfx + "0" * (6 - len(hl)) + hl + enc
    writer.write(bytes.fromhex(final)); await writer.drain()
    print_info(f"[BR] search sent ({plen}B) R={reg}")

# ═══════════════════════════ UDP HELPERS ═══════════════════════════
async def has_ssan_zig(n):
    z = (n << 1) & 0xFFFFFFFFFFFFFFFF
    out = bytearray()
    while z >= 0x80: out.append((z & 0x7F) | 0x80); z >>= 7
    out.append(z); return bytes(out)

async def uleb_encode(n):
    out = bytearray()
    while True:
        b = n & 0x7F; n >>= 7
        if n: b |= 0x80
        out.append(b)
        if not n: break
    return bytes(out)

async def zigzag_encode_signed(n):
    try: n = int(n)
    except Exception: n = 0
    zz = (n << 1) ^ (n >> 63)
    if zz < 0: zz = -zz
    out = bytearray()
    while True:
        b = zz & 0x7F; zz >>= 7
        if zz: b |= 0x80
        out.append(b)
        if not zz: break
    return bytes(out)

async def tea_enc(v0, v1, k0, k1, k2, k3):
    s = 0
    for _ in range(_ROUNDS):
        s = (s + _DELTA) & 0xFFFFFFFF
        v0 = (v0 + (((((v1<<4)&0xFFFFFFFF)+k0)&0xFFFFFFFF ^ ((v1+s)&0xFFFFFFFF) ^ (((v1>>5)+k1)&0xFFFFFFFF)))) & 0xFFFFFFFF
        v1 = (v1 + (((((v0<<4)&0xFFFFFFFF)+k2)&0xFFFFFFFF ^ ((v0+s)&0xFFFFFFFF) ^ (((v0>>5)+k3)&0xFFFFFFFF)))) & 0xFFFFFFFF
    return v0, v1

async def tea_dec(v0, v1, k0, k1, k2, k3):
    s = (_DELTA * _ROUNDS) & 0xFFFFFFFF
    for _ in range(_ROUNDS):
        v1 = (v1 - (((((v0<<4)&0xFFFFFFFF)+k2)&0xFFFFFFFF ^ ((v0+s)&0xFFFFFFFF) ^ (((v0>>5)+k3)&0xFFFFFFFF)))) & 0xFFFFFFFF
        v0 = (v0 - (((((v1<<4)&0xFFFFFFFF)+k0)&0xFFFFFFFF ^ ((v1+s)&0xFFFFFFFF) ^ (((v1>>5)+k1)&0xFFFFFFFF)))) & 0xFFFFFFFF
        s = (s - _DELTA) & 0xFFFFFFFF
    return v0, v1

async def tea_cbc_encrypt(padded, key_bytes):
    k0,k1,k2,k3 = (struct.unpack_from("<I", key_bytes, o)[0] for o in (0,4,8,12))
    out = bytearray(len(padded)); pc = bytearray(8); pi = bytearray(8)
    for i in range(0, len(padded), 8):
        x = bytearray(8)
        for j in range(8): x[j] = padded[i+j] ^ pc[j]
        e0,e1 = await tea_enc(struct.unpack_from("<I", x, 0)[0],
                              struct.unpack_from("<I", x, 4)[0], k0,k1,k2,k3)
        enc = bytearray(8)
        struct.pack_into("<I", enc, 0, e0); struct.pack_into("<I", enc, 4, e1)
        for j in range(8): out[i+j] = enc[j] ^ pi[j]
        pc[:] = out[i:i+8]; pi[:] = x
    return bytes(out)

async def tea_cbc_decrypt(body, key_bytes):
    k0,k1,k2,k3 = (struct.unpack_from("<I", key_bytes, o)[0] for o in (0,4,8,12))
    out = bytearray(len(body)); pi = bytearray(8); pc = bytearray(8)
    x = bytearray(8); dec = bytearray(8)
    for i in range(0, len(body), 8):
        for j in range(8): x[j] = body[i+j] ^ pi[j]
        d0,d1 = await tea_dec(struct.unpack_from("<I", x, 0)[0],
                              struct.unpack_from("<I", x, 4)[0], k0,k1,k2,k3)
        struct.pack_into("<I", dec, 0, d0); struct.pack_into("<I", dec, 4, d1)
        for j in range(8): out[i+j] = dec[j] ^ pc[j]
        pc[:] = body[i:i+8]; pi[:] = dec
    return bytes(out)

async def build_padded(content):
    pad_len = (8 - (len(content) + 10) % 8) % 8
    return bytes([pad_len, 0, 0]) + b"\x00" * pad_len + content + b"\x00" * 7

async def encode_header(layout, so, cmd, oid, flags, length, k, v80):
    out = bytearray()
    for code in layout:
        val = {0:so, 1:cmd, 2:oid, 3:flags, 4:length}[code]
        if _FIELD_SIZES[code] == 1: out.append((val & 0xFF) ^ k)
        else:
            v = ((val & 0xFFFF) ^ v80) & 0xFFFF
            out.append(v & 0xFF); out.append((v >> 8) & 0xFF)
    return bytes(out)

async def crc7_buff(crc, buf):
    c = crc & 0x7F
    for b in buf: c = CRC7_TABLE[((2*(c & 0xFF)) ^ (b & 0xFF)) & 0xFF] & 0x7F
    return c & 0x7F

async def sv_frame(msg_key, layout, so, cmd, oid, flags, content, key, encrypted=True):
    k = key[0]; v80 = ((k << 8) | k) & 0xFFFF
    body = await tea_cbc_encrypt(await build_padded(content), key) if encrypted else content
    hdr = bytearray([msg_key, 0]) + await encode_header(layout, so, cmd, oid, flags, len(body), k, v80)
    pkt = bytearray(hdr + body)
    pkt[1] = await crc7_buff(0, bytes(pkt[2:])) & 0x7F
    return bytes(pkt)

async def build_packet(msg_key, layout, so, cmd, oid, flags, content, key, encrypted=True):
    k = key[0]; v80 = ((k << 8) | k) & 0xFFFF
    body = await tea_cbc_encrypt(await build_padded(content), key) if encrypted else content
    hdr = bytearray([msg_key, 0])
    for code in layout:
        val = {0:so, 1:cmd, 2:oid, 3:flags, 4:len(body)}[code]
        if _FIELD_SIZES[code] == 1: hdr.append((val & 0xFF) ^ k)
        else:
            v = ((val & 0xFFFF) ^ v80) & 0xFFFF
            hdr.append(v & 0xFF); hdr.append((v >> 8) & 0xFF)
    pkt = bytearray(hdr + body)
    pkt[1] = await crc7_buff(0, bytes(pkt[2:])) & 0x7F
    return bytes(pkt)

async def layouts_from_mask(mask):
    ru = [int(c) for c in str(mask).strip()]
    nr = [c for c in ru if c != 2]
    return ru, nr

async def build_hello_packet(text, key, layout):
    data = text.encode("utf-8")
    if len(data) > 25: raise ValueError("too long")
    content = b"\x10\x00\x00\x00" + data + b"\x00" * (29 - 4 - len(data))
    k = key[0] if key else 10
    v80 = ((k << 8) | k) & 0xFFFF
    layout = [int(c) for c in str(layout).strip()] if isinstance(layout, str) else list(layout)
    padded = await build_padded(content)
    enc_body = await tea_cbc_encrypt(padded, key)
    hdr = await encode_header(layout, 1, 1, 0, 1, len(enc_body), k, v80)
    pkt = bytearray([0x63, 0x00]) + hdr + enc_body
    pkt[1] = await crc7_buff(0, pkt[2:]) & 0x7F
    return bytes(pkt).hex()

async def classify(frame):
    cmd = frame["cmd"]
    name = MESSAGE_ID_TO_NAME.get(cmd, f"UNKNOWN_{cmd}")
    if name == "UDP_HELLO": return "HELLO"
    if name == "UDP_ACK": return "ACK"
    if name == "UDP_PING": return "PING"
    if name == "RUDP_JOIN_MATCH": return "JOIN_MATCH"
    if name.startswith("RUDP_"): return name
    if name.startswith("UDP_"): return name
    return "DATA"

async def reply_for(frame, key, mask, ack_key=0x68, ping_key=0x6D, hello_key=0x5B, ack_style="short"):
    _, nr = await layouts_from_mask(mask)
    typ = await classify(frame)
    if typ == "HELLO":
        if ack_style == "echo":
            content = frame["content"] if frame["content"] else b"\x10\x00\x00\x00"
            return typ, await build_packet(hello_key, nr, 1, 1, None, 1, content, key)
        return typ, await build_packet(ack_key, nr, 0, 2, None, 1, b"\x01\x00", key)
    if typ == "ACK":
        content = frame["content"] if frame["content"] else b"\x01\x00"
        return typ, await build_packet(ack_key, nr, 0, 2, None, 1, content, key)
    if typ == "PING":
        c = frame["content"]
        counter = c[:4] if len(c) >= 4 else c
        return typ, await build_packet(ping_key, nr, 0, 3, None, 0, counter + b"\x00\x00\x00", key, encrypted=False)
    if typ == "JOIN_MATCH":
        return typ, await build_packet(ack_key, nr, 0, 2, None, 1, b"\x02\x00", key)
    return typ, None

async def keepalive_ping(sock, ip, port, key_bytes, mask, stop_event):
    nr = (await layouts_from_mask(mask))[1]
    ping_keys = [0x66, 0x6D, 0x69, 0x6C, 0x6B, 0x6E, 0x6F, 0x70]
    loop = asyncio.get_event_loop(); i = 0
    while not stop_event.is_set():
        pk = ping_keys[i % len(ping_keys)]
        counter = int(time.time() * 1000) & 0xFFFFFFFF
        pkt = await build_packet(pk, nr, 0, 3, None, 0, struct.pack("<I", counter) + b"\x00\x00\x00",
                                 key_bytes, encrypted=False)
        try: await loop.sock_sendto(sock, pkt, (ip, port))
        except Exception: pass
        i += 1
        try: await asyncio.wait_for(stop_event.wait(), timeout=bypass_packet_jitter(3.0, 0.4))
        except asyncio.TimeoutError: pass

async def try_header(buf, layout, k, v80):
    off = 2; out = {}
    for code in layout:
        size = _FIELD_SIZES[code]
        if off + size > len(buf): return None
        out[_FIELD_NAMES[code]] = ((buf[off] ^ k) if size == 1
                                    else ((buf[off] | (buf[off+1] << 8)) ^ v80) & 0xFFFF)
        off += size
    out["headerLen"] = off
    return out

async def oicq_unpad(padded):
    if not padded or len(padded) < 8: return None
    if not all(padded[-1-i] == 0 for i in range(7)): return None
    pad_len = padded[0] & 0x07
    s = 3 + pad_len; e = len(padded) - 7
    return padded[s:e] if s < e else b""

async def decode_packet(packet, key, mask=None):
    data = bytes(packet) if isinstance(packet, bytes) else bytes.fromhex(packet)
    if len(data) < 8: return None
    k = key[0]; v80 = ((k << 8) | k) & 0xFFFF
    crc_ok = (data[1] & 0x7F) == await crc7_buff(0, data[2:])
    candidates = []
    if mask:
        ru, nr = await layouts_from_mask(mask)
        layouts = [("RUDP", ru), ("nonRUDP", nr)]
    else:
        layouts = [("RUDP", list(p)) for p in itertools.permutations([0,1,2,3,4])]
        layouts += [("nonRUDP", list(p)) for p in itertools.permutations([0,1,3,4])]
    for kind, layout in layouts:
        f = await try_header(data, layout, k, v80)
        if not f: continue
        if f["flags"] > 7 or f["sendOption"] > 7: continue
        if f["length"] != len(data) - f["headerLen"]: continue
        body = data[f["headerLen"]:f["headerLen"]+f["length"]]
        content = None
        if f["flags"] & 1:
            if len(body) < 8 or len(body) % 8 != 0: continue
            padded = await tea_cbc_decrypt(body, key)
            content = await oicq_unpad(padded)
            if content is None: continue
        else: content = body
        score = (1 if crc_ok else 0) + (1 if content is not None else 0)
        candidates.append({"kind":kind, "layout":layout, "headerLen":f["headerLen"],
            "msgKey":data[0], "cmd":f["cmd"], "flags":f["flags"],
            "sendOption":f["sendOption"], "orderId":f.get("orderId"),
            "length":f["length"], "content":content, "crcOk":crc_ok,
            "score":score, "total":len(data)})
    if not candidates: return None
    candidates.sort(key=lambda c: c["score"], reverse=True)
    return candidates[0]

async def build_match_startup_packets(token, udp_key, match_code, account_id, block_val,
                                      server_ip="", region="ID", client_version="1.132.6",
                                      client_version_code="2019121229", access_token="",
                                      mode_id=BR_MODE_ID, map_id=BR_MAP_ID):
    token = token.strip()
    udp_key = bytes.fromhex(udp_key)
    match_code = [int(ch) for ch in str(match_code).strip()]
    thunder_jwt = token[:660] if len(token) > 660 else token
    sharma_jwt = token[660:] if len(token) > 660 else ""
    eth = thunder_jwt.encode() if isinstance(thunder_jwt, str) else thunder_jwt
    esh = sharma_jwt.encode() if isinstance(sharma_jwt, str) else sharma_jwt
    garena420 = await has_ssan_zig(len(eth)) + eth
    reg = str(region).upper() if region else "ID"
    csoversea_block = bytes.fromhex(
        "ca0163736f7665727365612e7374726f6e67686f6c642e66726565666972656d6f62696c652e636f6d"
        "3b302e302e302e303b33342e3132362e37362e34353b33342e38372e3137372e31343b33342e38372e"
        "3137302e3233303b33352e3138352e3138332e35370000000000000100000000000000000000000001"
        "00000800000100000000000100a8a2d7bebd8d8bdf110200")
    mid = bytes.fromhex('0000000001000102030101') + await has_ssan_zig(len(reg)) + reg.encode()
    mid += bytes.fromhex('0001030003000004')
    mid += await has_ssan_zig(len(client_version)) + client_version.encode()
    mid += await has_ssan_zig(len(client_version_code)) + client_version_code.encode()
    mid += csoversea_block
    clean_ip = server_ip.split(':')[0] if server_ip else "0.0.0.0"
    mid += await has_ssan_zig(len(clean_ip)) + clean_ip.encode()
    if access_token:
        clean_acc = access_token.strip()
        mid += await has_ssan_zig(len(clean_acc)) + clean_acc.encode()
    mid += await has_ssan_zig(len(esh)) + esh
    tg = (await uleb_encode(int(account_id)) + await uleb_encode(int(block_val)) +
          await uleb_encode(1) + await uleb_encode(int(mode_id)) +
          await uleb_encode(int(block_val)) + await uleb_encode(int(map_id)) + mid)
    process = await sv_frame(0x5E, match_code, 2, 447, 0, 1, garena420, udp_key)
    loading = await sv_frame(0x5A, match_code, 2, 448, 1, 1, tg, udp_key)
    return process.hex(), loading.hex()

# ═══════════════════════════ MOVEMENT 2001 ═══════════════════════════
async def build_movement_packet_2001(key_bytes, msg_key, player_state, x, y, z,
                                     tick, counter, move_state, account_uid,
                                     room_code, phase="arena"):
    if phase == "game":
        TAIL = (b"\x00"*7 + b"\x93\xca\xd5\xf9\x0b" + b"\x8e\xfe\xfc\xf7\x0b"
                + b"\xf4\xe0\xfe\xf7\x03" + b"\x00\x00")
    else:
        TAIL = (b"\x00"*7 + b"\xbd\xb6\xe1\xf3\x03" + b"\x00"
                + b"\xc4\xb6\xe1\xfb\x0b" + b"\x00\x00")
    body = bytearray()
    body += await uleb_encode(int(account_uid))
    body += await uleb_encode(int(player_state))
    body += await zigzag_encode_signed(int(x))
    body += await zigzag_encode_signed(int(y))
    body += await zigzag_encode_signed(int(z))
    body += b"\x00"
    body += await uleb_encode(int(move_state))
    body += TAIL
    body += await uleb_encode(int(tick))
    body += b"\x00\x00\x00"
    body += await uleb_encode(int(counter))
    body = bytes(body)
    k = key_bytes[0]; v80 = ((k << 8) | k) & 0xFFFF
    h = bytearray()
    h.append(msg_key & 0xFF); h.append(0x00); h.append(0x00 ^ k)
    h += ((2001 ^ v80) & 0xFFFF).to_bytes(2, "little")
    h += ((len(body) ^ v80) & 0xFFFF).to_bytes(2, "little")
    h.append(0x00 ^ k)
    h[1] = (await crc7_buff(0, bytes(h[2:]) + body)) & 0x7F
    return bytes(h) + body

class MovementTracker:
    PLAYER_STATE = {"idle":0, "walk":1, "run":2, "sprint":3, "jump":4, "crouch":5, "prone":6}
    def __init__(self, pattern="circle", radius=180):
        self.pattern = pattern; self.radius = int(radius)
        self.tick = 0; self.counter = 0
        self.angle = random.uniform(0, 6.2832)
        self.speed_multiplier = 1.0; self.dir_flip = 1
        self._next_speed_roll = time.time()
        self.state = "walk"; self.state_start = time.time()
        self.state_duration = random.uniform(2.0, 4.0)
        self._roll_new_speed()
    def _roll_new_speed(self):
        try:
            lo, hi = float(MOVEMENT_SPEED_MIN), float(MOVEMENT_SPEED_MAX)
            if hi < lo: lo, hi = hi, lo
            self.speed_multiplier = round(random.uniform(lo, hi), 2)
        except Exception: self.speed_multiplier = 1.0
        self._next_speed_roll = time.time() + MOVEMENT_UPDATE_SPEED_EVERY
    def _pick_next_state(self):
        r = random.random()
        ci = MOVEMENT_STATE_IDLE_CHANCE
        cw = ci + MOVEMENT_STATE_WALK_CHANCE
        cr = cw + MOVEMENT_STATE_RUN_CHANCE
        cs = cr + MOVEMENT_STATE_SPRINT_CHANCE
        cj = cs + MOVEMENT_STATE_JUMP_CHANCE
        cc = cj + MOVEMENT_STATE_CROUCH_CHANCE
        if r < ci: return "idle", random.uniform(0.6, 1.6)
        elif r < cw: return "walk", random.uniform(1.6, 3.0)
        elif r < cr: return "run", random.uniform(2.0, 4.0)
        elif r < cs: return "sprint", random.uniform(1.2, 2.5)
        elif r < cj: return "jump", random.uniform(0.35, 0.65)
        elif r < cc: return "crouch", random.uniform(1.2, 2.5)
        else: return "prone", random.uniform(1.5, 3.5)
    def _generate_movement(self):
        p = (self.pattern or "circle").lower()
        x = y = z = 0; ms = 0
        if p == "circle":
            self.angle += 0.35 * self.dir_flip
            if self.angle > 6.2832: self.angle -= 6.2832
            elif self.angle < 0: self.angle += 6.2832
            x = int(self.radius * random.uniform(0.9, 1.1) * (1.0 if self.angle % 3.14 < 1.57 else -1.0))
            y = int(self.radius * random.uniform(0.4, 0.6))
            z = int(self.radius * random.uniform(0.9, 1.1) * (1.0 if self.angle % 6.28 < 3.14 else -1.0))
            ms = 0x0F
        else:
            x = random.randint(-self.radius, self.radius)
            y = random.randint(-40, 40)
            z = random.randint(-self.radius, self.radius)
            ms = random.choice([0x01, 0x02, 0x04, 0x08, 0x0F])
        return x, y, z, ms
    def next(self):
        now = time.time()
        if now >= self._next_speed_roll: self._roll_new_speed()
        if now - self.state_start > self.state_duration:
            old = self.state
            self.state, self.state_duration = self._pick_next_state()
            self.state_start = now
            if old != self.state:
                print_info(f"[MOVE] {old} -> {self.state} ({self.state_duration:.2f}s)")
        self.tick = (self.tick + 1) & 0xFFFFFFFF
        self.counter = (self.counter + 1) & 0xFFFFFFFF
        ps = self.PLAYER_STATE.get(self.state, 1)
        if self.state in ("idle", "crouch", "prone"): x = y = z = 0; move_state = 0
        else: x, y, z, move_state = self._generate_movement()
        return ps, x, y, z, move_state, self.tick, self.counter, self.speed_multiplier, self.state

async def movement_worker(sock, ip, port, udp_key_bytes, match_code, account_id, stop_event, match_index):
    loop = asyncio.get_event_loop(); addr = (ip, port)
    tracker = MovementTracker(pattern=MOVEMENT_PATTERN, radius=MOVEMENT_RADIUS)
    sent = 0
    try:
        await asyncio.sleep(bypass_jitter(3.0, 0.5))
        while not stop_event.is_set():
            try:
                ps, x, y, z, ms, tick, cnt, sm, st = tracker.next()
                pkt = await build_movement_packet_2001(udp_key_bytes, 0x6B, ps, x, y, z, tick, cnt, ms,
                                                       account_id, match_code, phase="arena")
                await loop.sock_sendto(sock, pkt, addr); sent += 1
                if sent % 30 == 0: print_info(f"[MOVE] #{match_index} sent={sent} {st}({ps}) rate={sm}x")
                base = MOVEMENT_TICK_MS / 1000.0
                try: smx = max(0.7, min(float(sm), 1.6))
                except Exception: smx = 1.0
                wait = max(0.10, min(base / smx, 0.40))
                wait = bypass_packet_jitter(wait, 0.20)
                try: await asyncio.wait_for(stop_event.wait(), timeout=wait); break
                except asyncio.TimeoutError: pass
            except asyncio.CancelledError: break
            except Exception: await asyncio.sleep(0.5)
    except asyncio.CancelledError: pass
    finally: print_info(f"[MOVE] #{match_index} stopped sent={sent}")

async def send_anti_afk_fire(sock, addr, udp_key_bytes, match_code, account_id):
    try:
        _, nr = await layouts_from_mask(match_code)
        try: pid = int(account_id)
        except Exception: pid = 0
        ts = int(time.time() * 1000) & 0xFFFFFFFF
        wid = random.choice([101, 102, 103, 201, 202])
        fire = struct.pack("<IIHB", pid & 0xFFFFFFFF, ts, wid, 1)
        fp = await build_packet(0x68, nr, 0, 104, None, 0, fire, udp_key_bytes, encrypted=False)
        loop = asyncio.get_event_loop()
        await loop.sock_sendto(sock, fp, addr)
        await asyncio.sleep(bypass_jitter(random.uniform(0.15, 0.30), 0.05))
        stop = struct.pack("<IIHB", pid & 0xFFFFFFFF, ts + 200, wid, 0)
        sp = await build_packet(0x68, nr, 0, 105, None, 0, stop, udp_key_bytes, encrypted=False)
        await loop.sock_sendto(sock, sp, addr)
        return True
    except Exception: return False

async def anti_afk_worker(sock, ip, port, udp_key_bytes, match_code, account_id, stop_event, match_index):
    addr = (ip, port); fires = 0
    try:
        await asyncio.sleep(bypass_jitter(2.5, 0.5))
        while not stop_event.is_set():
            try:
                if await send_anti_afk_fire(sock, addr, udp_key_bytes, match_code, account_id): fires += 1
                w = random.uniform(ANTI_AFK_MIN_INTERVAL, ANTI_AFK_MAX_INTERVAL)
                w = bypass_packet_jitter(w, 0.25)
                try: await asyncio.wait_for(stop_event.wait(), timeout=w); break
                except asyncio.TimeoutError: pass
            except asyncio.CancelledError: break
            except Exception: await asyncio.sleep(1.0)
    except asyncio.CancelledError: pass
    finally:
        if fires > 0: print_info(f"[AFK] #{match_index} Fires={fires}")

# ═══════════════════════════ PLAY GAME ═══════════════════════════
async def play_game(server_ip_port, thunder, sharma, udp_key, match_code,
                    account_id, player_region, client_version, key, iv,
                    match_index, on_match_complete=None):
    t0 = time.time()
    ping_task = anti_task = move_task = None
    sock = None
    ping_stop = asyncio.Event(); anti_stop = asyncio.Event(); move_stop = asyncio.Event()
    uid_str = str(account_id); completed = False
    try:
        ip, port = server_ip_port.split(":"); port = int(port)
        rip = await resolve_host_cloudflare(ip)
        loop = asyncio.get_event_loop()
        sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
        try: sock.bind(('0.0.0.0', 0))
        except Exception: pass
        optimize_udp_socket(sock); sock.setblocking(False)
        udp_key_bytes = bytes.fromhex(udp_key)
        await asyncio.sleep(bypass_hello_delay())
        hello = await build_hello_packet(f"{account_id}_2585", udp_key_bytes, match_code)
        await loop.sock_sendto(sock, bytes.fromhex(hello), (rip, port))
        ack_state = "waiting_for_hello_reply"
        thunder_sent = False; join_match_rcv = False; local_closed = False
        send_lock = asyncio.Lock(); anti_started = False
        ping_task = asyncio.create_task(keepalive_ping(sock, rip, port, udp_key_bytes, match_code, ping_stop))
        last_activity = time.time()
        print_colored(f"[MATCH #{match_index}] UDP -> {server_ip_port} (DNS:{rip})", Colors.MAGENTA)

        async def start_workers():
            nonlocal anti_task, move_task, anti_started
            if anti_started: return
            anti_started = True
            anti_task = asyncio.create_task(anti_afk_worker(sock, rip, port, udp_key_bytes, match_code,
                                                            account_id, anti_stop, match_index))
            print_success(f"[AFK] Worker #{match_index}")
            if ENABLE_SPEED_MOVEMENT:
                move_task = asyncio.create_task(movement_worker(sock, rip, port, udp_key_bytes, match_code,
                                                                account_id, move_stop, match_index))
                print_success(f"[MOVE] Worker #{match_index} | {MOVEMENT_PATTERN}")

        async def send_startup():
            nonlocal ack_state, thunder_sent
            if thunder_sent: return
            async with send_lock:
                if thunder_sent: return
                try:
                    await loop.sock_sendto(sock, bytes.fromhex(thunder), (rip, port))
                    thunder_sent = True
                    await asyncio.sleep(bypass_jitter(0.1, 0.05))
                    _, nr = await layouts_from_mask(match_code)
                    ack = await build_packet(0x68, nr, 0, 2, None, 1, b"\x01\x00", udp_key_bytes)
                    await loop.sock_sendto(sock, ack, (rip, port))
                    await asyncio.sleep(bypass_jitter(0.2, 0.05))
                    await loop.sock_sendto(sock, bytes.fromhex(sharma), (rip, port))
                    ack_state = "thunder_sharma_sent"
                    print_success(f"[MATCH #{match_index}] Startup delivered")
                    await start_workers()
                except Exception as e: print_error(f"[MATCH #{match_index}] startup: {e}")

        while not local_closed:
            if time.time() - t0 > MAX_MATCH_DURATION: break
            try:
                resp, saddr = await asyncio.wait_for(loop.sock_recvfrom(sock, 65535), timeout=1.5)
                if resp:
                    last_activity = time.time()
                    frame = await decode_packet(resp, udp_key_bytes, match_code)
                    if frame:
                        pt = await classify(frame)
                        if frame['cmd'] in [103, 107]:
                            print_success(f"[MATCH #{match_index}] END cmd={frame['cmd']}")
                            completed = True; local_closed = True; continue
                        if frame['cmd'] == 101:
                            try:
                                _, nr = await layouts_from_mask(match_code)
                                a = await build_packet(0x68, nr, 0, 2, None, 1, b"\x01\x00", udp_key_bytes)
                                await loop.sock_sendto(sock, a, saddr)
                            except Exception: pass
                            continue
                        if pt in ["ACK", "PING", "HELLO", "JOIN_MATCH"]:
                            if pt == "HELLO" and ack_state == "waiting_for_hello_reply":
                                _, r = await reply_for(frame, udp_key_bytes, match_code, ack_style="short")
                                if r: await loop.sock_sendto(sock, r, saddr)
                                ack_state = "ack_sent_waiting"
                            elif pt == "ACK":
                                if ack_state == "waiting_for_hello_reply":
                                    _, r = await reply_for(frame, udp_key_bytes, match_code)
                                    if r: await loop.sock_sendto(sock, r, saddr)
                                    ack_state = "ready_to_send_thunder"
                                elif ack_state == "ack_sent_waiting":
                                    ack_state = "ready_to_send_thunder"
                                else:
                                    _, r = await reply_for(frame, udp_key_bytes, match_code)
                                    if r: await loop.sock_sendto(sock, r, saddr)
                            elif pt == "PING":
                                _, r = await reply_for(frame, udp_key_bytes, match_code)
                                if r: await loop.sock_sendto(sock, r, saddr)
                            elif pt == "JOIN_MATCH" and not join_match_rcv:
                                _, r = await reply_for(frame, udp_key_bytes, match_code)
                                if r: await loop.sock_sendto(sock, r, saddr); join_match_rcv = True
            except asyncio.TimeoutError:
                if ack_state == "ready_to_send_thunder" and not thunder_sent:
                    await send_startup()
                elif ack_state == "waiting_for_hello_reply":
                    if (time.time() - last_activity) > 7.0:
                        try:
                            hp = await build_hello_packet(f"{account_id}_2585", udp_key_bytes, match_code)
                            await loop.sock_sendto(sock, bytes.fromhex(hp), (rip, port))
                        except Exception: pass
                        last_activity = time.time()
                    if (time.time() - t0) > 25.0:
                        print_warning(f"[MATCH #{match_index}] Handshake timeout"); break
                elif ack_state == "thunder_sharma_sent":
                    if (time.time() - last_activity) > MATCH_IDLE_TIMEOUT:
                        print_success(f"[MATCH #{match_index}] Finished naturally")
                        completed = True; break
                continue
            except BlockingIOError: await asyncio.sleep(0.05)
            except OSError: await asyncio.sleep(0.5); continue
            except Exception: await asyncio.sleep(0.5); continue
            if ack_state == "ready_to_send_thunder" and not thunder_sent:
                await start_startup_safe(send_startup)
        return f"match #{match_index} finished"
    except Exception as e:
        print_error(f"[MATCH #{match_index}] {e}"); return f"match #{match_index} error"
    finally:
        if completed:
            try: bot_state.increment_match(uid_str)
            except Exception: pass
            if on_match_complete:
                try: asyncio.create_task(on_match_complete())
                except Exception: pass
        anti_stop.set(); move_stop.set()
        for t in (anti_task, move_task):
            if t:
                try: await asyncio.wait_for(t, timeout=2.0)
                except Exception:
                    t.cancel()
                    try: await t
                    except Exception: pass
        ping_stop.set()
        if ping_task:
            ping_task.cancel()
            try: await ping_task
            except asyncio.CancelledError: pass
        if sock:
            try: sock.close()
            except Exception: pass
        rem = await _dec_match(uid_str)
        total = await _get_total_match_count()
        print_info(f"[MATCH #{match_index}] Closed. UID:{rem} Total:{total}")
        try: bot_state.update_status(uid_str, "IN_MATCH" if rem > 0 else "ONLINE", rem)
        except Exception: pass

async def start_startup_safe(fn):
    try: await fn()
    except Exception: pass

# ═══════════════════════════ FRIEND REQUEST ═══════════════════════════
async def _process_social_packet(raw_bytes, account_data, tag="MAIN"):
    try:
        hex_data = raw_bytes.hex()
        candidates = []
        if len(raw_bytes) >= 6:
            plen = raw_bytes[4]
            if 0 < plen <= (len(raw_bytes) - 5):
                try:
                    inner = bytes(raw_bytes[5:5 + plen])
                    d0 = decode_protobuf_dict_safe(inner) or _wrap_manual(inner)
                    if d0: candidates.append((5, d0))
                except Exception: pass
        for off in [5, 6, 10, 8, 12, 4, 0]:
            if off >= len(hex_data): continue
            try: inner = bytes.fromhex(hex_data[off:])
            except Exception: continue
            decoded = decode_protobuf_dict_safe(inner) or _wrap_manual(inner)
            if decoded: candidates.append((off, decoded))
        if not candidates: return
        candidates.sort(key=lambda x: len(x[1]) if isinstance(x[1], dict) else 0, reverse=True)
        best_off, decoded = candidates[0]
        def _v(c, k):
            if not isinstance(c, dict): return None
            v = c.get(k) if k in c else c.get(str(k))
            if isinstance(v, dict) and "data" in v: return v["data"]
            return v
        f5w = decoded.get("5") or decoded.get(5) if isinstance(decoded, dict) else None
        f5 = f5w["data"] if isinstance(f5w, dict) and "data" in f5w else f5w
        target = None
        if isinstance(f5, dict):
            for fk in [1, 2, 3, 4, 6]:
                c = _v(f5, fk)
                if c and str(c).isdigit() and 6 <= len(str(c)) <= 15:
                    target = str(c); break
        if not target: return
        own = str(account_data.get('account_id', '')) if account_data else ''
        if own and target == own: return
        if not _accept_friend_request or not account_data: return
        jwt = account_data.get('token'); srv = account_data.get('server_url')
        rel = account_data.get('release_version'); own_id = account_data.get('account_id')
        if not (jwt and srv and rel and own_id): return
        url = f"{srv.rstrip('/')}/ConfirmFriendRequest"
        fields = {"1": int(target), "2": int(own_id)}
        try:
            payload = bytes.fromhex(encrypt_api(create_proto(fields).hex()))
            hdrs = {
                "authorization": f"Bearer {jwt}",
                "host": srv.replace("https://", "").replace("http://", "").split("/")[0],
                "x-ga": "v1 1", "content-type": "application/x-www-form-urlencoded",
                "accept-encoding": "deflate, gzip", "releaseversion": f"{rel}",
                "user-agent": "UnityPlayer/2022.3.47f1", "accept": "*/*",
                "x-unity-version": "2022.3.47f1",
            }
            async with httpx.AsyncClient(verify=False, timeout=8.0) as s:
                r = await s.post(url, headers=hdrs, content=payload)
                if r.status_code == 200 and len(r.content) > 0:
                    print_success(f"[FRIEND-{tag}] ✅ {target}")
        except Exception: pass
    except Exception: pass

def _wrap_manual(inner):
    try:
        alt = _decode_proto_manual(inner)
        if alt and len(alt) > 0:
            return {str(k): {"data": v} for k, v in alt.items()}
    except Exception: pass
    return None

# ═══════════════════════════ TEAM INVITE HANDLER ═══════════════════════════
async def _handle_team_invite(hex_data, pl, uid_str, current_account_data,
                              current_key, current_iv, writer):
    try:
        if DEBUG_TEAM_PACKETS:
            print_info(f"[TEAM-IN {uid_str}] len={pl} hex={hex_data[:80]}")

        candidates = []
        for off in [10, 8, 6, 12, 14, 4, 16, 0, 20, 2]:
            if off >= len(hex_data) or len(hex_data) - off < 4: continue
            try: inner = bytes.fromhex(hex_data[off:])
            except Exception: continue

            dec = decode_protobuf_dict_safe(inner)
            if dec and isinstance(dec, dict) and len(dec) > 0:
                candidates.append((off, "parser", dec)); continue

            alt = _decode_proto_manual(inner)
            if alt and len(alt) > 0:
                candidates.append((off, "manual", {str(k): {"data": v} for k, v in alt.items()}))

        if not candidates:
            return False

        candidates.sort(key=lambda x: len(x[2]) if isinstance(x[2], dict) else 0, reverse=True)
        best_off, decoder, dec = candidates[0]
        print_info(f"[TEAM-IN {uid_str}] decoded@{best_off}/{decoder} fields={list(dec.keys())[:20]}")

        def _unwrap(d, keys):
            if not isinstance(d, dict): return None
            for k in keys:
                v = d.get(k) if k in d else d.get(str(k))
                if isinstance(v, dict) and "data" in v: return v["data"]
                if isinstance(v, dict): return v
            return None

        target_dict = None
        for kp in [["5"], ["4"], ["6"], ["2"], ["1"]]:
            u = _unwrap(dec, kp)
            if isinstance(u, dict) and len(u) >= 3:
                target_dict = u
                print_info(f"[TEAM-IN {uid_str}] nested@{kp[0]}")
                break
        if target_dict is None: target_dict = dec

        def _g(d, k):
            if not isinstance(d, dict): return None
            v = d.get(k) if k in d else d.get(str(k))
            if isinstance(v, dict) and "data" in v: return v["data"]
            if isinstance(v, dict):
                for kk in ["1","2","3","4","5","6","7","8"]:
                    vv = v.get(kk) if kk in v else v.get(int(kk))
                    if isinstance(vv, dict) and "data" in vv: return vv["data"]
            return v

        group_id = None
        for k in list(target_dict.keys()):
            c = _g(target_dict, k)
            if isinstance(c, str) and 20 <= len(c) <= 40:
                group_id = c
                print_success(f"[TEAM-IN {uid_str}] 📋 group_id@f{k}: {c[:24]}...")
                break
        if not group_id:
            for k in list(dec.keys()):
                c = _g(dec, k)
                if isinstance(c, str) and 20 <= len(c) <= 40:
                    group_id = c
                    print_success(f"[TEAM-IN {uid_str}] 📋 group_id@root.f{k}: {c[:24]}...")
                    break

        own_acc = str(current_account_data.get('account_id')) if current_account_data else None
        inviter = None
        all_f = list(target_dict.keys()) + list(dec.keys())
        for k in all_f:
            c = _g(target_dict, k) or _g(dec, k)
            if c and str(c).isdigit() and 6 <= len(str(c)) <= 15:
                if str(c) != uid_str and str(c) != own_acc:
                    inviter = str(c)
                    print_success(f"[TEAM-IN {uid_str}] 👤 inviter@f{k}: {c}")
                    break

        tc = None
        for k in all_f:
            c = _g(target_dict, k) or _g(dec, k)
            if c and str(c).isdigit() and len(str(c)) == 7:
                tc = str(c); break
        if tc:
            async with _team_state["lock"]:
                _team_state["team_code"] = tc
            print_success(f"[TEAM-IN {uid_str}] 📢 Team Code: {tc}")

        is_member = (_team_state["leader_uid"] != uid_str)
        if inviter and group_id and is_member:
            async with _team_state["members_lock"]:
                already = uid_str in _team_state["members"]
            if already:
                return True
            print_success(f"[TEAM-IN {uid_str}] 📨 ACCEPT: inviter={inviter} group={group_id[:16]}...")
            accepted = False
            for attempt in range(3):
                try:
                    acc = accept_team_invite(int(inviter), group_id, current_key, current_iv)
                    if writer and not writer.is_closing():
                        writer.write(acc); await writer.drain()
                        print_success(f"[TEAM-IN {uid_str}] ✅ accept #{attempt+1} ({len(acc)}B)")
                        accepted = True; break
                except Exception as e:
                    print_warning(f"[TEAM-IN {uid_str}] accept err #{attempt+1}: {e}")
                await asyncio.sleep(0.8)
            if accepted:
                await _team_member_join(uid_str)
            return True
        return False
    except Exception as e:
        print_warning(f"[TEAM-IN {uid_str}] error: {e}")
        return False

# ═══════════════════════════ FUNCTIONAL (MAIN) — BATTLE ROYALE ONLY ═══════════════════════════
async def functional_battle_royale(addrs, starter_packet, account_region, client_version,
                                    key, iv, account_id="", account_data=None,
                                    account_level=2, max_reconnects=10):
    reconnects = 0
    ip, port = addrs.split(":")
    play_matches: List[asyncio.Task] = []
    no_response_count = 0
    search_attempts = 0
    last_start_time = 0.0
    uid_str = str(account_id)
    current_level = int(account_level or 2)
    consecutive_parse_failures = 0
    current_token = starter_packet
    current_key = key; current_iv = iv
    current_account_data = account_data
    reconnect_count_total = 0
    region_index = 0
    current_search_region = REGION_ROTATION_LIST[0]
    _writer_ref = {"w": None}
    _team_active = {"flag": True}

    async def trigger_post_match_refresh():
        # Profile EXP may update a little after the match finishes; retry at 9, 15 and 30 seconds.
        for wait_seconds in (9.0, 6.0, 15.0):
            try:
                await asyncio.sleep(wait_seconds)
                cd = bot_state.account_credentials.get(uid_str)
                if cd:
                    await refresh_account_profile(cd)
            except asyncio.CancelledError:
                raise
            except Exception as e:
                print_warning(f"[EXP-REFRESH] post-match refresh failed for {uid_str}: {e}")

    # ═══════════ LEADER: create → invite-loop → ready → start ═══════════
    async def _team_coordinator():
        try:
            deadline = time.time() + TEAM_PEER_WAIT_TIMEOUT
            while time.time() < deadline:
                async with _team_state["lock"]:
                    n = len(_team_state["peers"])
                if n >= TEAM_SIZE: break
                if bot_state.is_paused(uid_str): return
                await asyncio.sleep(0.5)

            async with _team_state["lock"]:
                n = len(_team_state["peers"])
                is_leader = (_team_state["leader_uid"] == uid_str)
                peers_snapshot = dict(_team_state["peers"])

            if not is_leader:
                print_info(f"[TEAM] {uid_str} waiting as member...")
                return
            if n < TEAM_SIZE:
                print_warning(f"[TEAM] Only {n}/{TEAM_SIZE} peers")
            else:
                print_success(f"[TEAM] ✅ All {n} peers online")

            await asyncio.sleep(TEAM_READY_DELAY)
            print_success(f"[TEAM] 👑 {uid_str} creating team...")

            async with _team_state["lock"]:
                _team_state["team_code"] = None
                _team_state["pk_code"] = None

            own_id_num = None
            if current_account_data: own_id_num = current_account_data.get('account_id')
            if not own_id_num:
                try: own_id_num = int(uid_str)
                except Exception: own_id_num = 0

            try:
                pkt = create_team(current_key, current_iv, client_version)
                if _writer_ref["w"] and not _writer_ref["w"].is_closing():
                    _writer_ref["w"].write(pkt); await _writer_ref["w"].drain()
                    print_info(f"[TEAM] create_team sent ({len(pkt)}B)")
                    await _team_member_reset(keep_leader=False)
                    await _team_member_join(uid_str)
            except Exception as e:
                print_error(f"[TEAM] create_team: {e}")

            await asyncio.sleep(TEAM_CREATE_WAIT)

            peer_uids = []
            for peer_uid, info in peers_snapshot.items():
                if peer_uid == uid_str: continue
                pa = None
                try: pa = info["data"].get("account_id")
                except Exception: pass
                if not pa: pa = peer_uid
                peer_uids.append(int(pa))
            print_info(f"[TEAM] Will invite {len(peer_uids)} peers: {peer_uids}")

            heartbeat_stop = asyncio.Event()
            async def heartbeat_loop():
                while not heartbeat_stop.is_set():
                    try:
                        if _writer_ref["w"] and not _writer_ref["w"].is_closing():
                            pkt = team_fresh(int(own_id_num), current_key, current_iv)
                            _writer_ref["w"].write(pkt); await _writer_ref["w"].drain()
                    except Exception: pass
                    try: await asyncio.wait_for(heartbeat_stop.wait(), timeout=TEAM_HEARTBEAT_INTERVAL)
                    except asyncio.TimeoutError: pass
            hb_task = asyncio.create_task(heartbeat_loop())

            print_success(f"[TEAM] 🎯 Invite-loop start (max {int(TEAM_INVITE_MAX_TIME)}s)")
            invite_start = time.time()
            cycle = 0
            while time.time() - invite_start < TEAM_INVITE_MAX_TIME:
                if not _team_active["flag"]: break
                if bot_state.is_paused(uid_str): break
                cnt = await _team_member_count()
                if cnt >= TEAM_SIZE:
                    print_success(f"[TEAM] 🎉 Full team ({cnt}/{TEAM_SIZE})!")
                    break
                cycle += 1
                for i, tuid in enumerate(peer_uids):
                    async with _team_state["members_lock"]:
                        joined = str(tuid) in _team_state["members"]
                    if joined: continue
                    try:
                        inv = invite_player_in_team(tuid, current_key, current_iv, region=account_region)
                        if _writer_ref["w"] and not _writer_ref["w"].is_closing():
                            _writer_ref["w"].write(inv); await _writer_ref["w"].drain()
                            print_success(f"[TEAM] 📨 invite {tuid} cycle#{cycle}")
                    except Exception as e:
                        print_warning(f"[TEAM] invite err: {e}")
                    await asyncio.sleep(0.5)
                try: await asyncio.wait_for(heartbeat_stop.wait(), timeout=TEAM_INVITE_CYCLE_WAIT)
                except asyncio.TimeoutError: pass

            final_cnt = await _team_member_count()
            print_colored(f"[TEAM] ══ FINAL: In team ({final_cnt}/{TEAM_SIZE}) ══", Colors.MAGENTA)

            if final_cnt < TEAM_SIZE:
                print_error(f"[TEAM] Only {final_cnt}/{TEAM_SIZE} joined — abort, retry")
                heartbeat_stop.set()
                try: hb_task.cancel(); await hb_task
                except Exception: pass
                return

            await asyncio.sleep(TEAM_FINAL_WAIT)
            heartbeat_stop.set()
            try: hb_task.cancel(); await hb_task
            except Exception: pass

            print_success(f"[TEAM] 🚀 {uid_str} loop: ready → 1s → start (every 5s)")
            while _team_active["flag"]:
                try:
                    if bot_state.is_paused(uid_str): break
                    async with _team_state["lock"]:
                        if _team_state["leader_uid"] != uid_str: break
                    oid = current_account_data.get('account_id', own_id_num) if current_account_data else own_id_num
                    try:
                        rdy = ready_for_game(int(oid), current_key, current_iv)
                        if _writer_ref["w"] and not _writer_ref["w"].is_closing():
                            _writer_ref["w"].write(rdy); await _writer_ref["w"].drain()
                    except Exception as e: print_warning(f"[TEAM] ready err: {e}")
                    await asyncio.sleep(1.0)
                    sm = start_match_team(int(oid), current_key, current_iv, region=account_region)
                    if _writer_ref["w"] and not _writer_ref["w"].is_closing():
                        _writer_ref["w"].write(sm); await _writer_ref["w"].drain()
                except Exception as e: print_warning(f"[TEAM] start err: {e}")
                try: await asyncio.wait_for(asyncio.sleep(5.0), timeout=5.5)
                except asyncio.TimeoutError: pass
        except asyncio.CancelledError: raise
        except Exception as e:
            print_error(f"[TEAM] coordinator: {e}")
            traceback.print_exc()

    async def _member_match_trigger():
        try:
            await asyncio.sleep(TEAM_READY_DELAY + TEAM_MEMBER_START_DELAY)
            async with _team_state["lock"]:
                if _team_state["leader_uid"] == uid_str: return
            print_success(f"[TEAM] 🚀 Member {uid_str}: ready → 1s → start (every 5s)")
            my_id = current_account_data.get('account_id', uid_str) if current_account_data else uid_str
            while _team_active["flag"]:
                try:
                    if bot_state.is_paused(uid_str): break
                    if _writer_ref["w"] and not _writer_ref["w"].is_closing():
                        try:
                            rdy = ready_for_game(int(my_id), current_key, current_iv)
                            _writer_ref["w"].write(rdy); await _writer_ref["w"].drain()
                        except Exception as e: print_warning(f"[TEAM] member ready err: {e}")
                        await asyncio.sleep(1.0)
                        sm = start_match_team(int(my_id), current_key, current_iv, region=account_region)
                        _writer_ref["w"].write(sm); await _writer_ref["w"].drain()
                except Exception as e: print_warning(f"[TEAM] member trigger: {e}")
                try: await asyncio.wait_for(asyncio.sleep(5.0), timeout=5.5)
                except asyncio.TimeoutError: pass
        except asyncio.CancelledError: raise
        except Exception as e: print_warning(f"[TEAM] member outer: {e}")

    try:
        while True:
            writer = None; gateway_ping_task = None
            team_coord_task = None; member_trigger_task = None
            try:
                if current_account_data:
                    fresh = None
                    if current_account_data.get('auth_type') == 'guest' and current_account_data.get('auth_uid'):
                        fresh = cache_get(str(current_account_data['auth_uid']))
                    elif current_account_data.get('auth_type') == 'token' and current_account_data.get('auth_token'):
                        fresh = cache_get(f"tok_{current_account_data['auth_token'][:20]}")
                    if fresh:
                        current_account_data = fresh
                        current_key = fresh['aes_ak']; current_iv = fresh['iv_i']
                        current_token = await build_tcp_startup_packet(
                            fresh['account_id'], fresh['token'], fresh['server_time'],
                            current_key, current_iv,
                            region=fresh.get('region', account_region), typ='OnLine')
                        try:
                            lv = int(fresh.get('level', current_level) or current_level)
                            if lv != current_level: current_level = lv
                        except Exception: pass
                    else:
                        print_warning(f"[FUNC] Cache miss {uid_str} -> re-login")
                        try:
                            if current_account_data.get('auth_uid'):
                                cache_invalidate(str(current_account_data['auth_uid']))
                            if current_account_data.get('auth_token'):
                                cache_invalidate(f"tok_{current_account_data['auth_token'][:20]}")
                        except Exception: pass
                        raise ConnectionError("Cache expired")

                try:
                    if uid_str in bot_state.accounts:
                        ll = int(bot_state.accounts[uid_str].get('level', current_level) or current_level)
                        if ll != current_level:
                            print_info(f"[LEVEL] {uid_str}: {current_level} -> {ll}")
                            current_level = ll
                except Exception: pass

                rip = await resolve_host_cloudflare(ip)
                reader, writer = await asyncio.open_connection(rip, int(port))
                _writer_ref["w"] = writer
                raw_sock = writer.get_extra_info('socket')
                if raw_sock: optimize_tcp_socket(raw_sock)
                await asyncio.sleep(bypass_hello_delay())
                writer.write(bytes.fromhex(current_token)); await writer.drain()
                try:
                    ka = await send_keep_alive(account_region)
                    if ka and not writer.is_closing():
                        writer.write(ka); await asyncio.wait_for(writer.drain(), timeout=3)
                except Exception: pass

                async def func_gateway_keepalive():
                    ka_bytes = await send_keep_alive(account_region)
                    while True:
                        await asyncio.sleep(bypass_ka_jitter(5.0))
                        try:
                            if writer and not writer.is_closing():
                                writer.write(ka_bytes); await writer.drain()
                        except Exception: break
                gateway_ping_task = asyncio.create_task(func_gateway_keepalive())

                connection_start_time = asyncio.get_running_loop().time()
                last_watchdog_check = connection_start_time
                search_attempts = 0
                if reconnect_count_total > 0 and (reconnect_count_total % REGION_ROTATE_EVERY_N == 0):
                    region_index = (region_index + 1) % len(REGION_ROTATION_LIST)
                    current_search_region = REGION_ROTATION_LIST[region_index]
                    print_warning(f"[REGION ROTATE] {uid_str} -> {current_search_region}")
                else:
                    current_search_region = REGION_ROTATION_LIST[region_index]

                print_success(f"[FUNC] TCP connected {uid_str} (DNS:{rip} Lvl:{current_level} R:{current_search_region})")
                reconnects = 0; no_response_count = 0; last_start_time = 0.0

                async with _team_state["lock"]:
                    _team_state["peers"][uid_str] = {
                        "writer": writer, "data": current_account_data,
                        "key": current_key, "iv": current_iv}
                    if _team_state["leader_uid"] is None:
                        _team_state["leader_uid"] = uid_str
                        print_success(f"[TEAM] 👑 {uid_str} is leader")

                if TEAM_MODE:
                    team_coord_task = asyncio.create_task(_team_coordinator())
                    member_trigger_task = asyncio.create_task(_member_match_trigger())
                else:
                    # ⭐ Always Battle Royale
                    await start_game_battle_royale(current_search_region, client_version, writer, current_key, current_iv)

                while True:
                    play_matches[:] = [m for m in play_matches if not m.done()]
                    active = await _get_match_count(uid_str)
                    try: bot_state.update_status(uid_str, "ONLINE" if active == 0 else "IN_MATCH", active)
                    except Exception: pass

                    now = asyncio.get_running_loop().time()
                    if now - last_watchdog_check >= MATCH_WATCHDOG_CHECK:
                        last_watchdog_check = now
                        sd = now - connection_start_time
                        if sd > 30: print_warning(f"[WATCHDOG] {uid_str} searching {int(sd)}s att={search_attempts}")
                        if sd > MATCH_SEARCH_TIMEOUT:
                            raise ConnectionError("Search watchdog")
                    if search_attempts >= MAX_SEARCH_ATTEMPTS:
                        raise ConnectionError("Max attempts")

                    try:
                        data = await asyncio.wait_for(reader.read(8192), timeout=0.5)
                    except asyncio.TimeoutError:
                        no_response_count += 1
                        if TEAM_MODE:
                            if no_response_count > TEAM_IDLE_ITERS_TEAM:
                                raise ConnectionError("Team idle timeout")
                        else:
                            if no_response_count > 80: raise ConnectionError("idle")
                        continue

                    if not data: raise ConnectionError("closed")
                    hex_data = data.hex()
                    pl = len(data)
                    no_response_count = 0

                    if DEBUG_TEAM_PACKETS and not hex_data.startswith("0300") and not hex_data.startswith("0600"):
                        print_info(f"[RAW-IN {uid_str}] len={pl} prefix={hex_data[:24]}")

                    if hex_data.startswith("0600") and pl > 20:
                        await _process_social_packet(data, current_account_data, tag="MAIN")
                        continue

                    if hex_data.startswith("05") and pl > 10:
                        await _handle_team_invite(hex_data, pl, uid_str, current_account_data,
                                                  current_key, current_iv, writer)
                        continue

                    if hex_data.startswith("0300") and 10 < pl < 30:
                        continue

                    if hex_data.startswith("0300") and pl >= 300:
                        print_colored("=" * 60, Colors.GREEN)
                        print_colored("MATCH FOUND! Loading...", Colors.GREEN)
                        print_colored("=" * 60, Colors.GREEN)

                        for tk in (team_coord_task, member_trigger_task):
                            if tk and not tk.done():
                                tk.cancel()
                                try: await tk
                                except asyncio.CancelledError: pass
                        team_coord_task = None; member_trigger_task = None
                        _team_active["flag"] = False

                        try:
                            res = json.loads(await decode_protobuf(hex_data[10:]))
                            token = udp_key = match_code = server_ip_port = None
                            match_account_id = block_val = None
                            if '42' in res and 'data' in res['42']:
                                match_code = res['42']['data']
                            if '5' in res and 'data' in res['5']:
                                r5 = res['5']['data']
                                server_ip_port = r5.get('2', {}).get('data')
                                udp_key = r5.get('3', {}).get('data')
                                token = r5.get('4', {}).get('data')
                                if '42' in r5: match_code = r5['42']['data']
                            if '1' in res and 'data' in res['1']:
                                match_account_id = res['1']['data']
                            if '5' in res and 'data' in res['5']:
                                block_val = res['5']['data'].get('1', {}).get('data')

                            effective = match_account_id or account_id or "BD_BOT"
                            if token and udp_key and match_code and server_ip_port:
                                try:
                                    async with _team_state["lock"]:
                                        _team_state["pk_code"] = str(match_code)
                                        _team_state["team_code"] = str(match_code)
                                    print_colored(f"[PK] 🎯 Room Code: {match_code}", Colors.MAGENTA)
                                    print_colored(f"[PK] 🌐 Server: {server_ip_port}", Colors.MAGENTA)
                                    print_colored(f"[PK] 🔑 UDP Key: {udp_key}", Colors.MAGENTA)
                                except Exception: pass

                                acc_tok = current_account_data.get('access_token', '') if current_account_data else ""
                                # ⭐ Always Battle Royale
                                mid, mp = BR_MODE_ID, BR_MAP_ID
                                tag = "BATTLE_ROYALE"
                                print_info(f"[TARGET] {tag} mid={mid} mp={mp}")
                                thunder, sharma = await build_match_startup_packets(
                                    token, udp_key, match_code, effective, block_val or 0,
                                    server_ip=server_ip_port, region=account_region,
                                    client_version=client_version, access_token=acc_tok,
                                    mode_id=mid, map_id=mp)
                                match_index = await _inc_match(uid_str)
                                total = await _get_total_match_count()
                                print_colored(f"[MATCH #{match_index}] UDP -> {server_ip_port} ({tag})", Colors.CYAN)

                                new_match = asyncio.create_task(play_game(
                                    server_ip_port, thunder, sharma, udp_key, match_code,
                                    effective, current_search_region, client_version,
                                    current_key, current_iv,
                                    match_index=match_index, on_match_complete=trigger_post_match_refresh))
                                play_matches.append(new_match)
                                consecutive_parse_failures = 0

                                async def drain_gw():
                                    while not new_match.done():
                                        try:
                                            dg = await asyncio.wait_for(reader.read(4096), timeout=1.0)
                                            if not dg: break
                                            gh = dg.hex()
                                            if gh.startswith("0600") and len(dg) > 20:
                                                await _process_social_packet(dg, current_account_data, tag="DRAIN")
                                        except asyncio.TimeoutError: continue
                                        except Exception: break
                                drain_task = asyncio.create_task(drain_gw())
                                try: await new_match
                                except Exception as e: print_error(f"[MATCH #{match_index}] {e}")
                                finally:
                                    drain_task.cancel()
                                    try: await drain_task
                                    except asyncio.CancelledError: pass
                                play_matches[:] = [m for m in play_matches if not m.done()]

                                async with _team_state["lock"]:
                                    _team_state["peers"].pop(uid_str, None)
                                    if _team_state["leader_uid"] == uid_str:
                                        _team_state["leader_uid"] = None
                                    _team_state["pk_code"] = None
                                await _team_member_leave(uid_str)
                                _team_active["flag"] = True
                                try: writer.close(); await writer.wait_closed()
                                except Exception: pass
                                print_info(f"[FUNC] {uid_str} reconnect in {NEW_MATCH_DELAY}s...")
                                await asyncio.sleep(NEW_MATCH_DELAY)
                                reconnect_count_total += 1
                                break
                            else:
                                consecutive_parse_failures += 1
                                print_warning(f"[FUNC] Non-match big pkt #{consecutive_parse_failures}")
                                if consecutive_parse_failures >= MAX_CONSECUTIVE_PARSE_FAILURES:
                                    consecutive_parse_failures = 0
                                try: writer.close(); await writer.wait_closed()
                                except Exception: pass
                                await asyncio.sleep(NON_MATCH_RECONNECT_DELAY)
                                break
                        except Exception as e:
                            print_error(f"[FUNC] Match parse: {e}")
                            consecutive_parse_failures += 1
                            try: writer.close(); await writer.wait_closed()
                            except Exception: pass
                            await asyncio.sleep(NON_MATCH_RECONNECT_DELAY)
                            break

                    if 30 <= pl <= 40: continue

            except asyncio.CancelledError:
                print_warning(f"[FUNC] Cancelled — cancel {len(play_matches)} UDP")
                for m in play_matches:
                    if not m.done(): m.cancel()
                if play_matches:
                    await asyncio.gather(*play_matches, return_exceptions=True)
                play_matches.clear()
                if gateway_ping_task: gateway_ping_task.cancel()
                async with _team_state["lock"]:
                    _team_state["peers"].pop(uid_str, None)
                    if _team_state["leader_uid"] == uid_str:
                        _team_state["leader_uid"] = None
                await _team_member_leave(uid_str)
                raise
            except Exception as e:
                if gateway_ping_task: gateway_ping_task.cancel()
                print_error(f"[FUNC] TCP state {uid_str}: {e}")
                play_matches[:] = [m for m in play_matches if not m.done()]
                if writer:
                    try: writer.close(); await writer.wait_closed()
                    except Exception: pass
                if "Cache expired" in str(e):
                    print_warning(f"[FUNC] re-login {uid_str}")
                    break
                reconnect_count_total += 1
                reconnects += 1
                if reconnects > max_reconnects:
                    reconnects = 0
                    await asyncio.sleep(3)
                    continue
                await asyncio.sleep(bypass_human_reconnect_delay(reconnects))
            finally:
                _team_active["flag"] = False
                for tk in (team_coord_task, member_trigger_task):
                    if tk and not tk.done():
                        tk.cancel()
                        try: await tk
                        except (asyncio.CancelledError, Exception): pass
                if gateway_ping_task: gateway_ping_task.cancel()
                if writer:
                    try: writer.close(); await writer.wait_closed()
                    except Exception: pass
                async with _team_state["lock"]:
                    _team_state["peers"].pop(uid_str, None)
                    if _team_state["leader_uid"] == uid_str:
                        _team_state["leader_uid"] = None
                await _team_member_leave(uid_str)
                _team_active["flag"] = True
    except asyncio.CancelledError:
        for m in play_matches:
            if not m.done(): m.cancel()
        if play_matches: await asyncio.gather(*play_matches, return_exceptions=True)
        play_matches.clear()
        raise

# ═══════════════════════════ INFORMATIONAL ═══════════════════════════
async def informational(addrs, starter_packet, key, iv, region="ID", max_reconnects=3):
    reconnects = 0
    ip, port = addrs.split(":")
    while True:
        writer = None; ping_task = None
        try:
            rip = await resolve_host_cloudflare(ip)
            reader, writer = await asyncio.open_connection(rip, int(port))
            rs = writer.get_extra_info('socket')
            if rs: optimize_tcp_socket(rs)
            writer.write(bytes.fromhex(starter_packet)); await writer.drain()
            reconnects = 0
            try:
                ka = await send_keep_alive(region)
                if ka and not writer.is_closing():
                    writer.write(ka); await asyncio.wait_for(writer.drain(), timeout=3)
            except Exception: pass
            async def info_ka():
                ka = await send_keep_alive(region)
                while True:
                    await asyncio.sleep(bypass_ka_jitter(5.0))
                    try:
                        if writer and not writer.is_closing():
                            writer.write(ka); await writer.drain()
                    except Exception: break
            ping_task = asyncio.create_task(info_ka())
            while True:
                data = await reader.read(8192)
                if not data: raise ConnectionError("closed")
        except asyncio.CancelledError:
            if ping_task: ping_task.cancel()
            if writer:
                try: writer.close(); await writer.wait_closed()
                except Exception: pass
            raise
        except Exception:
            if ping_task: ping_task.cancel()
            if writer:
                try: writer.close(); await writer.wait_closed()
                except Exception: pass
            reconnects += 1
            if reconnects > max_reconnects:
                await asyncio.sleep(3); reconnects = 0
            else: await asyncio.sleep(1)

# ═══════════════════════════ ACCOUNT HELPERS ═══════════════════════════
def _register_credentials(ad):
    try:
        acc_id = str(ad['account_id'])
        bot_state.account_credentials[acc_id] = ad
        if ad.get('auth_uid'): bot_state.account_credentials[str(ad['auth_uid'])] = ad
        if ad.get('auth_token'): bot_state.account_credentials[f"tok_{ad['auth_token'][:20]}"] = ad
    except Exception: pass

async def refresh_account_profile(ad_or_uid):
    """Refresh server profile data; preserve known EXP when a reply is partial."""
    try:
        if isinstance(ad_or_uid, str):
            uid = str(ad_or_uid)
            ad = bot_state.account_credentials.get(uid)
        else:
            ad = ad_or_uid
            uid = str(ad.get('account_id')) if ad else "?"
        if not ad:
            return
        url = ad.get('server_url'); token = ad.get('token')
        rel = ad.get('release_version'); payload = ad.get('login_payload_data')
        if not (url and token and rel and payload):
            return
        res = await send_getlogin(payload, url, token, rel)
        if not res:
            print_warning(f"[EXP-REFRESH] UID {uid}: profile request returned no data")
            return
        rp, dd = res
        def _si(v):
            try:
                if v is None or v == "": return None
                return int(v)
            except Exception:
                return None
        level = _si(get_proto_field(dd, 6, None))
        exp = _si(get_proto_field(dd, 7, None))
        likes = _si(get_proto_field(dd, 8, None))
        try: nick = rp.nickname or get_proto_field(dd, 4, "") or ""
        except Exception: nick = ""
        if level is None and exp is None and likes is None and not nick:
            print_warning(f"[EXP-REFRESH] UID {uid}: response has no usable profile fields")
            return
        acc_id = str(ad.get('account_id', uid))
        current = bot_state.accounts.get(acc_id, {}) if hasattr(bot_state, 'accounts') else {}
        try: old_lv = int(current.get('level', ad.get('level', 0)) or 0)
        except Exception: old_lv = 0
        try: old_ex = int(current.get('exp', ad.get('exp', 0)) or 0)
        except Exception: old_ex = 0
        # A missing/partial response must not erase previously confirmed EXP.
        # Ignore zero when positive EXP is already known; don't fabricate any new EXP.
        if exp is None or (exp == 0 and old_ex > 0):
            exp_to_apply = old_ex
        else:
            exp_to_apply = exp
        level_to_apply = level if level is not None else (old_lv or 1)
        try:
            bot_state.update_exp(acc_id, exp_to_apply, level_to_apply)
        except Exception as e:
            print_warning(f"[EXP-REFRESH] update_exp failed for {acc_id}: {e}")
        if likes is not None and likes > 0 and acc_id in bot_state.accounts:
            bot_state.accounts[acc_id]["likes"] = likes
        if nick and acc_id in bot_state.accounts:
            bot_state.accounts[acc_id]["nickname"] = nick
        _update_cache_profile(ad, level_to_apply, exp_to_apply)
        ad['level'] = level_to_apply; ad['exp'] = exp_to_apply
        if likes is not None and likes > 0: ad['likes'] = likes
        if nick: ad['nickname'] = nick
        if old_lv > 0 and level_to_apply > old_lv:
            print_success(f"[LEVEL UP] {acc_id}: {old_lv} -> {level_to_apply} (EXP {old_ex} -> {exp_to_apply})")
        elif exp_to_apply > old_ex:
            print_success(f"[EXP-GAIN] UID {acc_id}: +{exp_to_apply - old_ex} (total={exp_to_apply}, level={level_to_apply})")
        else:
            print_info(f"[EXP-TRACE] UID {acc_id}: server_level={level if level is not None else 'missing'} server_exp={exp if exp is not None else 'missing'} applied_level={level_to_apply} applied_exp={exp_to_apply} delta={exp_to_apply-old_ex}")
    except asyncio.CancelledError:
        raise
    except Exception as e:
        print_error(f"refresh_account_profile error: {e}")

async def process_account_uid_pass(uid, password):
    cached = cache_get(uid)
    if cached:
        print_success(f"[CACHE] {uid} loaded")
        acc_id = str(cached['account_id'])
        bot_state.register_account(uid=acc_id,
            nickname=cached.get('nickname', f"Player_{acc_id}"),
            region=cached.get('region', 'ID'),
            level=cached.get('level', 1), exp=cached.get('exp', 0),
            likes=cached.get('likes', 0))
        _register_credentials(cached); return cached
    print_info(f"[LOGIN] UID {uid}...")
    try:
        vc = await version_config()
        if not vc: return None
        rel, cv, su = vc
        tg = await get_access_token(uid, password)
        if not tg: return None
        oid, at, pf = tg
        dev = get_device_for_account(uid)
        lpd = await build_majorlogin_payload(oid, at, pf, cv, dev)
        if not lpd: return None
        mresp = await send_majorlogin(lpd, rel, su)
        if mresp is None: return None
        gl = await send_getlogin(lpd, mresp.url, mresp.token, rel)
        if gl is None: return None
        rp, dd = gl
        acc_id = str(mresp.account_id)
        level = int(get_proto_field(dd, 6, 1) or 1)
        exp = int(get_proto_field(dd, 7, 0) or 0)
        likes = int(get_proto_field(dd, 8, 0) or 0)
        nick = rp.nickname or get_proto_field(dd, 4, f"Player_{acc_id}")
        region = mresp.region or get_proto_field(dd, 3, "ID")
        bot_state.register_account(uid=acc_id, nickname=nick, region=region,
                                    level=level, exp=exp, likes=likes)
        print_success(f"[OK] {acc_id} | {nick} | Lvl{level} | BATTLE ROYALE")
        ad = {
            'account_id': mresp.account_id, 'nickname': nick, 'region': region,
            'level': level, 'exp': exp, 'likes': likes,
            'open_id': oid, 'access_token': at, 'platform': str(pf),
            'token': mresp.token, 'server_time': mresp.server_time,
            'aes_ak': mresp.aes_ak, 'iv_i': mresp.iv_i,
            'functional_addrs': rp.functional_addrs or get_proto_field(dd, 14),
            'informational_addrs': rp.informational_addrs or get_proto_field(dd, 32),
            'release_version': rel, 'client_version': cv, 'server_url': mresp.url,
            'login_payload_data': lpd,
            'auth_type': 'guest', 'auth_uid': uid, 'auth_password': password,
        }
        _register_credentials(ad); cache_set(uid, ad); return ad
    except Exception as e:
        print_error(f"process_account_uid_pass: {e}")
        traceback.print_exc(); return None

async def process_account_token(access_token):
    cache_key = f"tok_{access_token[:20]}"
    cached = cache_get(cache_key)
    if cached:
        acc_id = str(cached['account_id'])
        bot_state.register_account(uid=acc_id,
            nickname=cached.get('nickname', f"Player_{acc_id}"),
            region=cached.get('region', 'ID'),
            level=cached.get('level', 1), exp=cached.get('exp', 0),
            likes=cached.get('likes', 0))
        _register_credentials(cached); return cached
    print_info("[LOGIN] Token...")
    try:
        vc = await version_config()
        if not vc: return None
        rel, cv, su = vc
        import requests
        url = f"https://100067.connect.garena.com/oauth/token/inspect?token={access_token}"
        hdrs = {"User-Agent": "GarenaMSDK/4.0.19P4(G011A ;Android 9;en;US;)"}
        resp = await asyncio.to_thread(requests.get, url, headers=hdrs, timeout=10)
        d = resp.json()
        if 'error' in d: return None
        oid = d.get('open_id'); pf = d.get('platform', 4)
        if not oid: return None
        dev = get_device_for_account(oid)
        lpd = await build_majorlogin_payload(oid, access_token, str(pf), cv, dev)
        if not lpd: return None
        mresp = await send_majorlogin(lpd, rel, su)
        if mresp is None: return None
        gl = await send_getlogin(lpd, mresp.url, mresp.token, rel)
        if gl is None: return None
        rp, dd = gl
        acc_id = str(mresp.account_id)
        level = int(get_proto_field(dd, 6, 1) or 1)
        exp = int(get_proto_field(dd, 7, 0) or 0)
        likes = int(get_proto_field(dd, 8, 0) or 0)
        nick = rp.nickname or get_proto_field(dd, 4, f"Player_{acc_id}")
        region = mresp.region or get_proto_field(dd, 3, "ID")
        bot_state.register_account(uid=acc_id, nickname=nick, region=region,
                                    level=level, exp=exp, likes=likes)
        ad = {
            'account_id': mresp.account_id, 'nickname': nick, 'region': region,
            'level': level, 'exp': exp, 'likes': likes,
            'open_id': oid, 'access_token': access_token, 'platform': str(pf),
            'token': mresp.token, 'server_time': mresp.server_time,
            'aes_ak': mresp.aes_ak, 'iv_i': mresp.iv_i,
            'functional_addrs': rp.functional_addrs or get_proto_field(dd, 14),
            'informational_addrs': rp.informational_addrs or get_proto_field(dd, 32),
            'release_version': rel, 'client_version': cv, 'server_url': mresp.url,
            'login_payload_data': lpd,
            'auth_type': 'token', 'auth_token': access_token,
        }
        _register_credentials(ad); cache_set(cache_key, ad); return ad
    except Exception as e:
        print_error(f"process_account_token: {e}"); return None

async def run_account_worker(ad, label):
    acc_id = str(ad['account_id'])
    info_task = None; exp_task = None; ping_task = None
    try:
        reg = ad.get('region', 'ID')
        tcp_online = await build_tcp_startup_packet(
            ad['account_id'], ad['token'], ad['server_time'],
            ad['aes_ak'], ad['iv_i'], region=reg, typ='OnLine')
        tcp_chat = await build_tcp_startup_packet(
            ad['account_id'], ad['token'], ad['server_time'],
            ad['aes_ak'], ad['iv_i'], region=reg, typ='ChaT')
        info_task = asyncio.create_task(informational(ad['informational_addrs'], tcp_chat,
                                                      ad['aes_ak'], ad['iv_i'], region=reg))
        if ENABLE_HTTP_PING:
            ping_task = asyncio.create_task(ping_worker(acc_id, ad['token'], ad['release_version'], region=reg))
            print_success(f"[PING] Started {acc_id}")

        async def exp_refresher():
            try:
                f = bot_state.account_credentials.get(acc_id)
                if f: await refresh_account_profile(f)
            except Exception: pass
            while True:
                await asyncio.sleep(EXP_REFRESH_INTERVAL + random.uniform(-3.0, 3.0))
                try:
                    f = bot_state.account_credentials.get(acc_id)
                    if f: await refresh_account_profile(f)
                except Exception: pass
        exp_task = asyncio.create_task(exp_refresher())
        # ⭐ Always Battle Royale
        await functional_battle_royale(ad['functional_addrs'], tcp_online, ad['region'], ad['client_version'],
            ad['aes_ak'], ad['iv_i'], account_id=acc_id, account_data=ad,
            account_level=int(ad.get('level', 2) or 2))
    except asyncio.CancelledError: raise
    except Exception as e: print_error(f"run_account_worker {label}: {e}")
    finally:
        for t in (info_task, exp_task, ping_task):
            if t and not t.done(): t.cancel()
        for t in (info_task, exp_task, ping_task):
            if t:
                try: await t
                except Exception: pass

async def account_loop_guest(uid, password):
    while True:
        try:
            print_info(f"[LOGIN] Guest {uid}...")
            # Avoid creating a fake dashboard row keyed by the login UID.
            # The real account row is added only after login returns account_id.
            ad = await process_account_uid_pass(uid, password)
            if not ad:
                print_error(f"Login failed {uid}, retry 15s")
                await asyncio.sleep(15); continue
            await run_account_worker(ad, uid)
            print_warning(f"Session end {uid}, reconnect 3s")
            await asyncio.sleep(3)
        except asyncio.CancelledError:
            print_warning(f"Worker {uid} stopped")
            try: bot_state.update_status(str(uid), "OFFLINE")
            except Exception: pass
            break
        except Exception as e:
            print_error(f"Error {uid}: {e}, retry 10s")
            await asyncio.sleep(10)

async def account_loop_token(token):
    label = token[:10]
    while True:
        try:
            ad = await process_account_token(token)
            if not ad:
                print_error("Login token fail, retry 15s")
                await asyncio.sleep(15); continue
            acc_id = str(ad['account_id'])
            await run_account_worker(ad, acc_id)
            await asyncio.sleep(3)
        except asyncio.CancelledError:
            print_warning(f"Token {label} stopped"); break
        except Exception as e:
            print_error(f"Token error: {e}, retry 10s")
            await asyncio.sleep(10)

def load_accounts():
    accounts = []
    if os.path.exists(ACCOUNTS_FILE):
        try:
            with open(ACCOUNTS_FILE, "r", encoding="utf-8") as f:
                data = json.load(f)
                if isinstance(data, list): accounts = data
        except Exception as e: print_error(f"load: {e}")
    if not accounts and FALLBACK_UID and FALLBACK_PASSWORD:
        accounts.append({"uid": FALLBACK_UID, "password": FALLBACK_PASSWORD})
    return accounts

# ═══════════════════════════ MAIN ═══════════════════════════
async def main():
    print_colored("=" * 60, Colors.CYAN)
    print_colored("  TEAM RBC — Squad Bot (Create/Invite/Accept/PK)", Colors.GREEN)
    print_colored("=" * 60, Colors.CYAN)
    print_info(f"Match interval: {START_MATCH_INTERVAL}s | Offline: {NEW_MATCH_DELAY}s")
    print_info("Mode: BATTLE ROYALE ONLY")
    if TEAM_MODE:
        print_success(f"[SQUAD] size={TEAM_SIZE} peer_wait={TEAM_PEER_WAIT_TIMEOUT}s")
        print_info(f"  invite_cycle={TEAM_INVITE_CYCLE_WAIT}s | max_time={TEAM_INVITE_MAX_TIME}s")
        print_info(f"  heartbeat={TEAM_HEARTBEAT_INTERVAL}s | final_wait={TEAM_FINAL_WAIT}s")
    print_colored("=" * 60, Colors.CYAN)

    try:
        await start_web_dashboard(host=WEB_HOST, port=WEB_PORT)
        print_success(f"Dashboard: http://localhost:{WEB_PORT}")
    except Exception as e: print_error(f"Dashboard: {e}")

    async def on_account_added(data):
        token_value = str(data.get("token", "")).strip()
        u = str(data.get("uid", "")).strip()
        p = str(data.get("password", "")).strip()
        if token_value:
            worker_key = "tok_" + token_value[:20]
            identity = "token:" + token_value[:24]
            args = (account_loop_token, (token_value,))
        elif u and p:
            worker_key = u
            identity = "uid:" + u
            args = (account_loop_guest, (u, p))
        else:
            raise ValueError("Enter UID and password, or an access token")

        existing = bot_state.account_workers.get(worker_key)
        if existing is not None and not existing.done():
            raise ValueError(f"Account worker already running: {worker_key}")

        requested_squad = data.get("squad_id")
        if requested_squad is None:
            squad_id = _assign_squad(identity)
        else:
            squad_id = max(0, min(99, int(requested_squad)))
            while len(_squad_slots) <= squad_id:
                _squad_slots.append(set())
            # Keep explicitly selected accounts grouped together, but warn if more than TEAM_SIZE are selected.
            _squad_slots[squad_id].add(identity)
            _squad_identity_map[identity] = squad_id
            if len(_squad_slots[squad_id]) > TEAM_SIZE:
                bot_state.log(f"Squad {squad_id + 1} has {len(_squad_slots[squad_id])} assigned accounts (team size is {TEAM_SIZE})", "warning")
        worker, worker_args = args
        task = asyncio.create_task(_run_account_in_squad(squad_id, worker, *worker_args))
        bot_state.account_workers[worker_key] = task
        bot_state.log(f"Account worker queued in Squad {squad_id + 1}: {worker_key}", "success")
        print_success(f"[SQUAD-{squad_id + 1:02d}] account worker queued: {worker_key}")

    async def on_refresh_account(uid):
        await refresh_account_profile(uid)

    try:
        bot_state.refresh_callbacks["on_account_added"] = on_account_added
        bot_state.refresh_callbacks["on_refresh_account"] = on_refresh_account
    except Exception: pass

    accounts = load_accounts()
    if not accounts:
        print_warning(f"No accounts in {ACCOUNTS_FILE}. Add via dashboard.")
    for acc in accounts:
        if acc.get("token"):
            token_value = str(acc["token"])
            squad_id = _assign_squad("token:" + token_value[:24])
            t = asyncio.create_task(_run_account_in_squad(squad_id, account_loop_token, token_value))
            bot_state.account_workers["tok_" + token_value[:20]] = t
        elif acc.get("uid") and acc.get("password"):
            u = str(acc["uid"])
            squad_id = _assign_squad("uid:" + u)
            t = asyncio.create_task(_run_account_in_squad(squad_id, account_loop_guest, u, acc["password"]))
            bot_state.account_workers[u] = t

    try:
        while True: await asyncio.sleep(1)
    except (KeyboardInterrupt, asyncio.CancelledError):
        print_warning("Shutting down...")
        for t in list(bot_state.account_workers.values()): t.cancel()
        await asyncio.gather(*bot_state.account_workers.values(), return_exceptions=True)
        print_success("Closed.")

if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print_warning("stopped")