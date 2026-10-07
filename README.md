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

## 部署

推送到 `main` 后，GitHub Actions（`.github/workflows/pages.yml`）会把 `index.html` 发布到 GitHub Pages，当前访问地址：

https://denymosh.github.io/flame-ndx100/

网站上只有 `index.html` 这一个文件（logo 和数据都已内嵌）；`build/`、`data/`、`logos/` 不会发布到网站。如果以后页面需要引用新的文件，要在工作流的 `Stage site` 步骤里一并复制。注意这只决定网站上能访问什么，仓库本身公开时，这些文件在 GitHub 上仍然可见。

首次使用需在仓库 Settings → Pages → Build and deployment 里把 Source 设为「GitHub Actions」。也可以在 Actions 页手动运行该工作流。

### 以后绑定自定义域名

1. 在仓库根目录加 `CNAME` 文件，内容只有一行域名，例如 `ndx100.example.com`。用 Actions 部署时，生效的是 Settings → Pages → Custom domain 里的设置，`CNAME` 文件只作记录，两处保持一致即可。
2. 在域名 DNS 服务商处加记录：
   - 子域名（如 `ndx100.example.com`）：加 `CNAME` 记录指向 `denymosh.github.io`。
   - 根域名（如 `example.com`）：加 4 条 `A` 记录指向 `185.199.108.153`、`185.199.109.153`、`185.199.110.153`、`185.199.111.153`（IPv6 可另加 `AAAA` 记录 `2606:50c0:8000::153` 至 `2606:50c0:8003::153`）。
3. 在 Settings → Pages → Custom domain 填入域名并保存，等 DNS 检查通过、证书签发后（可能需要几分钟到 24 小时），勾选「Enforce HTTPS」。
