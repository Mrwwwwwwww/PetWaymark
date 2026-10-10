# 地名来源、许可与覆盖

版本 `2026-10-10-geonames-global.2`，查阅及下载日期 2026-10-10。250 个国家 / 地区源条目、3,868 个省州级选择项（含中国的三个关联辖区入口）、6,853 个城市条目。国家条目遵循 GeoNames 分类，不是主权国家数量，也不保证行政区划在 2026 年仍完整。

GeoNames [公开下载](https://download.geonames.org/export/dump/)：`countryInfo.txt`、`admin1CodesASCII.txt`、`cities15000.zip`、`CN.zip`、`readme.txt`。[许可](https://creativecommons.org/licenses/by/4.0/)为 CC BY 4.0，归属 GeoNames；中文名及选择、映射修改由 PetWaymark contributors 整理。各下载 SHA-256 保存在 `locations.json`。本次读取的上游说明在 `licenses/GEONAMES-README.txt`。countryInfo 中已撤销的 CS、AN 两条历史辖区不作为可选地点；252 条原始国家记录仍保留作来源证据。原国家、省州、城市条目分别保存在 `geonames-country-subset.tsv`、`geonames-admin1-subset.tsv`、`geonames-subset.tsv`。

中国内地导入GeoNames 的 360 个 ADM2 条目，以北京、上海既有城市点位替代其重复行政条目，共 360 个城市选择条目。其中包含 333 个地级区划（293 个地级市、其余为州、盟、地区），以及直辖市和源数据的部分县级管理条目，不可把 360 当作地级市数量。31 个内地省级行政区全部覆盖；中国省级选择器另有香港、澳门、台湾三个入口，选中后切换到对应源辖区，避免套用内地运输规则。港澳台主要城市按各自 GeoNames 编码收录。

对照源是 [modood/Administrative-divisions-of-China](https://github.com/modood/Administrative-divisions-of-China/tree/c49d495b40ac73eb1a66f6eeae5f8fd10696f035) 的 `dist/provinces.json`、`dist/cities.json`，固定提交 `c49d495b40ac73eb1a66f6eeae5f8fd10696f035`。源声明数据截至 2023-06-30，源许可为 WTFPL 2.0，完整许可保留在 `licenses/CHINA-ADMIN-WTFPL.txt`。这里只使用公开名称和代码事实，未复制政府网页正文；上游许可声明不代表政府授予整库许可。原始快照为 `china-provinces.json` 和 `china-cities.json`，来源 URL、SHA-256、截止日期及许可在 supplementaryInputs 中。导入器按明确行政编码核对全部 333 个地级区划，修正 GeoNames 的部分旧显示名，并保留原名与源 ID。代码仍用 GeoNames 原值，不用坐标推测父级。

其他国家导入源中全部一级行政区；每个行政区从 `cities15000` 选人口最多的三个城市（不足三个则全收）。该文件本身包含人口超过 15,000 的城市和各级行政首府，不能据此声称覆盖全部城市。没有一级行政区的国家 / 地区仍可选国家和手填城市；源缺少父级时不猜关系。部分海外名称使用源语言，不保证中文译名完整。

原有五个区县保留；其他区乡镇继续手填，或只选城市。完整性与规则可信度分别维护。所有地点仅按公开源编码关联，未完成政府逐项复核。2023 年快照已停止更新；不保证 2026 年改名、撤并或省直辖县级城市全部正确。找不到可手填并标记未核实。地名能选中不代表当地接收宠物或有已核实规则。

重建（本地输入，不自动联网）：

```sh
python scripts/import_places.py --dump-dir /path/to/geonames-dumps --global-places
python scripts/build_pages.py --write-source
```

固定旧条目保存在 `scripts/places-seed.json`，避免导入结果反过来成为输入。全球行政区每月查阅更新；变更时显式更新版本、下载日期及快照，重新检查父级和现有链接。原版三国小切片导入功能仍保留，省州联动的 v2 构建应使用 `--global-places`。

`testing-points.json` 按国家、城市 ID 和显示名保存检测点结构，包含机构、地址、电话、来源、核实日期及状态。本轮全部为 null / pending，页面显示“待补充”，不生成机构名、电话或地址。

欧盟成员标记仅用于候选范围筛选，按 [欧盟官方成员页面](https://european-union.europa.eu/principles-countries-history/eu-countries_en) 于 2026-10-10 核对 27 国。欧盟内部行程缺少已覆盖资料时不套用从非欧盟入境的要求。
