import csv, json, os, re
ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
P = lambda *a: os.path.join(ROOT, *a)

# 每期一个目录 data/YYYY-MM-DD/（目录名是取数日期），内含 finviz.txt 与 holdings.csv
periods = sorted((d for d in os.listdir(P('data')) if re.fullmatch(r'\d{4}-\d{2}-\d{2}', d)), reverse=True)
months = [d[:7] for d in periods]
dup = {m for m in months if months.count(m) > 1}
assert not dup, f'同一月份只能有一期：{dup}'

tpl = open(P('build', 'tpl.html'), encoding='utf-8').read()
logos = open(P('build', 'logos.json')).read()
# 研报知识库链接（仅本机）：设 KB_VIEWS=<views 目录> 时，为已有页面的标的加链接；谷歌 C 与谷歌 A 共用 GOOGL 页
VIEWS = os.environ.get('KB_VIEWS', '')

def agg(fv, tickers, key):
    # 市值 / 盈利 汇总：只计有该指标的成分（亏损或无数据者 finviz 显示 "-"，剔除）
    cap = sum(fv[t]['cap'] for t in tickers if fv[t][key])
    earn = sum(fv[t]['cap'] / fv[t][key] for t in tickers if fv[t][key])
    n_ex = sum(1 for t in tickers if not fv[t][key])
    return round(cap / earn, 1), n_ex

def build(period):
    raw = open(P('data', period, 'finviz.txt'), encoding='utf-8').read().strip().strip('"')
    fv = {}
    for item in raw.split(';'):
        t, cap, pe, fpe = item.split(',')
        t = t[1:]  # finviz text doubles the first letter
        f = lambda s: None if s == '-' else float(s)
        fv[t] = dict(cap=float(cap.rstrip('B')), pe=f(pe), fpe=f(fpe))
    # QQQ 持仓明细前 N 名：名称,代码,权重%
    with open(P('data', period, 'holdings.csv'), encoding='utf-8') as fh:
        top = [(n, t, float(w)) for n, t, w in list(csv.reader(fh))[1:]]

    alltk = list(fv)
    rest = [t for t in alltk if t not in {x[1] for x in top}]
    idx = {k: agg(fv, alltk, k) for k in ('pe', 'fpe')}
    oth = {k: agg(fv, rest, k) for k in ('pe', 'fpe')}
    rows = [dict(name=n, tk=t, w=w, pe=fv[t]['pe'], fpe=fv[t]['fpe']) for n, t, w in top]
    rows.append(dict(name="其他", tk=f"{len(rest)} 只", w=round(100 - sum(x[2] for x in top), 2), pe=oth['pe'][0], fpe=oth['fpe'][0]))
    for r in rows:
        page = {'GOOG': 'GOOGL'}.get(r['tk'], r['tk'])
        if VIEWS and os.path.exists(os.path.join(VIEWS, page + '.html')):
            r['href'] = 'file:///' + os.path.join(VIEWS, page + '.html').replace(os.sep, '/')
    print(period, 'linked:', [r['tk'] for r in rows if 'href' in r])
    print(period, 'index PE', idx, 'others', oth)
    return dict(rows=rows, idx_pe=idx['pe'][0], idx_fpe=idx['fpe'][0], n=len(alltk),
                ex_pe=idx['pe'][1], ex_fpe=idx['fpe'][1])

def nav(cur, prefix):
    # 左侧往期列表；prefix 是从当前页到站点根的相对路径（根页面为 ''，存档页为 '../'）
    items = ''.join(f'<li><a href="{prefix}{d[:7]}/"{" aria-current=\"page\"" if d == cur else ""}>{d.replace("-", "/")}</a></li>' for d in periods)
    return f'<nav class="hist"><div class="ht">往期</div><ul>{items}</ul></nav>'

def render(period, data, prefix):
    return (tpl.replace('__DATA__', json.dumps(data, ensure_ascii=False)).replace('__LOGO__', logos)
            .replace('__DATE__', period.replace('-', '/')).replace('__NAV__', nav(period, prefix)))

# 每期存档 → YYYY-MM/index.html；最新一期另写到根目录 index.html
for i, period in enumerate(periods):
    data = build(period)
    os.makedirs(P(period[:7]), exist_ok=True)
    open(P(period[:7], 'index.html'), 'w', encoding='utf-8').write(render(period, data, '../'))
    if i == 0:
        open(P('index.html'), 'w', encoding='utf-8').write(render(period, data, ''))
