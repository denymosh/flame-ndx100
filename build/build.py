import json, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *a: os.path.join(ROOT, *a)
raw = open(P('data', 'finviz_2026-10-06.txt'), encoding='utf-8').read().strip().strip('"')
fv = {}
for item in raw.split(';'):
    t, cap, pe, fpe = item.split(',')
    t = t[1:]  # finviz text doubles the first letter
    f = lambda s: None if s == '-' else float(s)
    fv[t] = dict(cap=float(cap.rstrip('B')), pe=f(pe), fpe=f(fpe))

# QQQ 持仓明细 2026/10/06 前 33 名（用户截图）
top = [("英伟达","NVDA",8.50),("苹果","AAPL",7.17),("微软","MSFT",5.79),("美光科技","MU",4.80),
("AMD","AMD",4.31),("亚马逊","AMZN",4.07),("Meta","META",3.24),("谷歌A","GOOGL",3.01),
("SpaceX","SPCX",3.00),("特斯拉","TSLA",2.95),("谷歌C","GOOG",2.81),("博通","AVGO",2.63),
("英特尔","INTC",2.40),("沃尔玛","WMT",2.12),("思科","CSCO",1.89),("Palantir","PLTR",1.80),
("应用材料","AMAT",1.71),("泛林集团","LRCX",1.70),("好市多","COST",1.69),("Palo Alto","PANW",1.39),
("奈飞","NFLX",1.16),("CrowdStrike","CRWD",1.16),("德州仪器","TXN",1.10),("科磊","KLAC",1.05),
("迈威尔","MRVL",1.02),("闪迪","SNDK",0.99),("林德","LIN",0.92),("安进","AMGN",0.89),
("亚德诺","ADI",0.83),("Shopify","SHOP",0.81),("高通","QCOM",0.77),("希捷","STX",0.74),("吉利德","GILD",0.73)]

def agg(tickers, key):
    # 市值 / 盈利 汇总：只计有该指标的成分（亏损或无数据者 finviz 显示 "-"，剔除）
    cap = sum(fv[t]['cap'] for t in tickers if fv[t][key])
    earn = sum(fv[t]['cap'] / fv[t][key] for t in tickers if fv[t][key])
    n_ex = sum(1 for t in tickers if not fv[t][key])
    return round(cap / earn, 1), n_ex

alltk = list(fv)
rest = [t for t in alltk if t not in {x[1] for x in top}]
idx = {k: agg(alltk, k) for k in ('pe', 'fpe')}
oth = {k: agg(rest, k) for k in ('pe', 'fpe')}
rows = [dict(name=n, tk=t, w=w, pe=fv[t]['pe'], fpe=fv[t]['fpe']) for n, t, w in top]
rows.append(dict(name="其他", tk=f"{len(rest)} 只", w=round(100 - sum(x[2] for x in top), 2), pe=oth['pe'][0], fpe=oth['fpe'][0]))
# 研报知识库链接（仅本机）：设 KB_VIEWS=<views 目录> 时，为已有页面的标的加链接；谷歌 C 与谷歌 A 共用 GOOGL 页
VIEWS = os.environ.get('KB_VIEWS', '')
for r in rows:
    page = {'GOOG': 'GOOGL'}.get(r['tk'], r['tk'])
    if VIEWS and os.path.exists(os.path.join(VIEWS, page + '.html')):
        r['href'] = 'file:///' + os.path.join(VIEWS, page + '.html').replace(os.sep, '/')
print('linked:', [r['tk'] for r in rows if 'href' in r])
data = dict(rows=rows, idx_pe=idx['pe'][0], idx_fpe=idx['fpe'][0], n=len(alltk),
            ex_pe=idx['pe'][1], ex_fpe=idx['fpe'][1])
print('index PE', idx, 'others', oth)
tpl = open(P('build', 'tpl.html'), encoding='utf-8').read()
open(P('index.html'), 'w', encoding='utf-8').write(tpl.replace('__DATA__', json.dumps(data, ensure_ascii=False)).replace('__LOGO__', open(P('build', 'logos.json')).read()))
