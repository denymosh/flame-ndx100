# flame-ndx100

纳指100（QQQ）前 33 大持仓的滚动市盈率与前瞻市盈率对比图，数据日期 2026/10/06。打开 `index.html` 即可查看。

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
python build/build.py         # data/ + build/tpl.html + build/logos.json → index.html
```

- 持仓排序与权重写在 `build/build.py` 的 `top` 列表里。
- 市盈率数据在 `data/finviz_2026-10-06.txt`，每条格式为 `代码,市值,滚动PE,前瞻PE`。注意每个代码的首字母重复了一次，这是抓取时的产物，脚本读入时会去掉。
- 设环境变量 `KB_VIEWS=<目录>` 时，会给该目录下已有 `{TICKER}.html` 的标的加本地链接。该功能仅供本机使用，公开版不加链接。
