# ndx100

纳指100（QQQ）前 33 大持仓的滚动市盈率与前瞻市盈率对比图，每月更新一期。根目录 `index.html` 是最新一期，`YYYY-MM/index.html` 是各月存档，页面左侧列出所有期数。

## 数据来源

| 内容 | 来源 | 日期 |
|---|---|---|
| 持仓排序与权重（前 33 名） | moomoo「QQQ 持仓明细」截图 | 2026/10/06 |
| 滚动市盈率（TTM）、前瞻市盈率（下一财年） | finviz 纳指100 筛选器估值页（101 只成分） | 2026/10/06 收盘后 |
| 公司 logo | Financial Modeling Prep 公开 logo；ADI 来自 Parqet；亚马逊字标来自 Wikimedia Commons；SpaceX、闪迪为用户提供 | — |

纳指100 整体市盈率 = 成分股总市值 ÷ 总盈利（各股盈利 = 市值 ÷ 市盈率），市值加权，亏损或无数据的成分不计入。

## 已知口径限制

- 前瞻市盈率用 finviz 的「下一财年」预期 EPS，各公司财年结束月份不同，时间跨度约 1–1.7 年。
- 滚动市盈率为 GAAP 口径，前瞻多为调整后口径。
- 谷歌 2026 年 GAAP 利润含 Anthropic / SpaceX 权益重估收益，滚动市盈率因此偏低。

## 重新生成

```bash
pip install pillow
python build/logos_build.py   # logos/ → build/logos.json（裁边、统一高度、嵌入为 data URI）
python build/build.py         # data/*/ + build/tpl.html + build/logos.json → YYYY-MM/index.html 与 index.html
```

- 每期数据放在 `data/YYYY-MM-DD/`，目录名是取数日期，一个月只能有一期：
  - `holdings.csv`：持仓排序与权重，每行 `名称,代码,权重%`。
  - `finviz.txt`：市盈率数据，每条格式为 `代码,市值,滚动PE,前瞻PE`。注意每个代码的首字母重复了一次，这是抓取时的产物，脚本读入时会去掉。
- `build.py` 每次重建所有期数：每期写到 `YYYY-MM/index.html`，最新一期另写一份到根目录 `index.html`。左侧往期列表也随之更新，所以旧页面会列出后来新增的期数。
- 设环境变量 `KB_VIEWS=<目录>` 时，会给该目录下已有 `{TICKER}.html` 的标的加本地链接。该功能仅供本机使用，公开版不加链接。

### 每月更新

1. 新建 `data/YYYY-MM-DD/`，放入当期的 `holdings.csv` 和 `finviz.txt`。
2. 前 33 名里出现新公司时，把 logo 放进 `logos/`，再运行 `build/logos_build.py`。
3. 运行 `build/build.py`，提交生成的 `index.html` 和新的 `YYYY-MM/` 目录，推送到 `main`。

## 部署

推送到 `main` 后，GitHub Actions（`.github/workflows/pages.yml`）会把根目录 `index.html` 和各月 `YYYY-MM/` 目录发布到 GitHub Pages：

- 最新一期：https://denymosh.github.io/ndx100/
- 某月存档：https://denymosh.github.io/ndx100/2026-10/

`build/`、`data/`、`logos/` 不会发布到网站（页面已内嵌 logo 和数据）。如果以后页面需要引用新的文件，要在工作流的 `Stage site` 步骤里一并复制。注意这只决定网站上能访问什么，仓库本身公开时，这些文件在 GitHub 上仍然可见。

首次使用需在仓库 Settings → Pages → Build and deployment 里把 Source 设为「GitHub Actions」。也可以在 Actions 页手动运行该工作流。

### 自定义域名

计划用 `sicaper.net/ndx100/` 访问。域名绑在用户主页仓库 `denymosh.github.io` 上，而不是本仓库：

1. 在 `denymosh.github.io` 仓库的 Settings → Pages → Custom domain 填 `sicaper.net`。
2. 在域名 DNS 服务商处加 4 条 `A` 记录，主机 `@`，分别指向 `185.199.108.153`、`185.199.109.153`、`185.199.110.153`、`185.199.111.153`；再加一条 `CNAME` 记录，主机 `www`，指向 `denymosh.github.io`。
3. 等 DNS 检查通过、证书签发后（可能需要几分钟到 24 小时），勾选「Enforce HTTPS」。

绑好后，本仓库会自动出现在 `sicaper.net/ndx100/`，旧的 `denymosh.github.io/ndx100/` 会跳转过去。本仓库的 Custom domain 保持留空，也不需要 `CNAME` 文件。
