# 0005 — Local bilingual web and US overlays / 本机双语网页与美国叠加

Date: 2026-10-08. Status: accepted for research preview, not a production release.
日期：2026-10-08；状态：研究预览采用，非正式发布。

The CLI and web both invoke the Python route/explanation kernel. Static HTML/CSS/JS
assets are served by a loopback-only standard-library development server; form
submissions are processed on the user's computer. A purely static hosted web app
would need a separately ported engine or a downloaded runtime. Week 5 chooses one
kernel and zero paid/cloud dependencies; a hosted static build remains deferred.
This changes the delivery mechanism from PLAN's proposed static-only web, not its
free/offline budget or result semantics. The server is not exposed publicly.

CLI与网页调用同一Python路径／解释内核。HTML／CSS／JS由仅监听回环地址的标准库开发服务提供，
表单在用户电脑处理。纯静态托管需移植内核或下载运行时；第5周选择单一内核、无付费／云依赖，
纯静态托管构建顺延。相对PLAN静态网页设想，这是交付方式取舍，免费离线预算与判定语义不变；服务不公开暴露。

Language changes only labels, messages and printable summaries; fields, dataset,
status, reason codes and segment identity stay identical. Synthetic examples are
explicitly marked. Missing classification never defaults to ordinary travel. State
inventories contain source reading states, not review signatures. NY is unavailable,
CA/TX are read pending independent review; no state is fully cleared.

语言仅改变标签、提示和打印摘要；输入、数据版本、状态、原因码和分段身份保持一致。
合成示例明确标注，分类缺失不默认普通旅行。州清单记录查阅状态，不冒充复核签名；无州整体获准。

US domestic rules have a separate `domestic_pet` scope. International-import rules
are not applied to a known same-region domestic journey. The CA health draft runs
only on graph legs crossing into CA, and the cargo certificate-presence draft only
on that source-identified cargo product. A certificate boolean does not validate
issuance, examination, content or exception branches. State and actual operating
carrier packages, transit states, facilities, weather, caretaker and pickup windows
remain uncovered; the graph cannot authorize travel.

美国国内使用独立`domestic_pet`范围，已知同地区国内行程不套国际入境草稿。
CA健康草稿仅在图中跨州进入CA的分段比较；货运健康证存在草稿仅对应来源标识的货运产品。
布尔值不验证签发检查日期、内容或例外；完整州／实际承运包及途经、设施、天气、照护和接收窗口未覆盖。

The input form has no contact, certificate upload, private address or identifiers.
Requests are not stored or logged; exports contain result evidence and opaque IDs,
not the profile. Host/origin, body size, duplicate fields, booleans and civil dates
are checked. The browser uses no remote scripts, cookies, analytics or map APIs.
JSON exports and print views visibly retain no booking/order and pending custody.
No providers are favored or offered an order flow. Dependency installation and
GitHub CI require network; running the preview after installation does not.

表单无联系方式、证书上传、私址和私人标识。不存储／记录请求，导出不含原始档案。
校验Host／Origin、大小、重复字段、布尔值和民用日期。浏览器无远程脚本、cookie、统计或地图API。
JSON与打印保留未订舱／未接单及待安排保管责任；无下单或偏向商家。安装与CI需网络，运行预览无需网络。
