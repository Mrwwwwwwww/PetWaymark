# 地名切片来源、许可与范围

版本：2026-10-10-geonames-slice.1；下载日期：2026-10-10。

来源是 [GeoNames 公开下载](https://download.geonames.org/export/dump/) 的 CN.zip、US.zip、FR.zip 与 countryInfo.txt。上游 [字段及许可说明](https://download.geonames.org/export/dump/readme.txt) 明示 [CC BY 4.0](https://creativecommons.org/licenses/by/4.0/)，数据按现状提供，不保证准确、及时、完整。归属：GeoNames。中文显示名、切片及 UI 层级映射由 PetWaymark contributors 整理修改，沿用 CC BY 4.0。没有复制政府整库、无许可 GitHub 城市表或地图 API。

`locations.json` 保存原文、中文名、地名 ID、实际类型、行政编码、省州及父级路径、条目修改日期、源链接、许可和核对状态。每个国家压缩包的 SHA-256 保存在 archives 中；`geonames-subset.tsv` 保存被采用的原始条目，便于离线检查。中文不是官方统一译名。`geonames-country-subset.tsv` 保存三个国家的原始条目；`licenses/GEONAMES-README.txt` 保存本次读取的上游说明。

| 国家 | 城市 | 区县 / 乡镇 |
|---|---|---|
| 中国 | 上海市、北京市、黄山市（安徽省） | 徐汇区；朝阳区、海淀区；屯溪区、黟县（县） |
| 美国 | 纽约市（纽约州） | 未收录，不用县级或坐标邻近自动代填纽约市辖区 |
| 法国 | 巴黎（法兰西岛） | 未收录，不造统一的“区”层级 |

中国直辖市的 GeoNames 城市点位和行政条目分开保留，区县按相同 admin1/admin2 编码关联。黄山市采用市级行政条目 ADM2，而不是同名景点；黟县显示实际县级类型，未收录宏村镇，不推断镇隶属。巴黎保留大区、省、行政区和市镇路径；纽约保留州父级。城市之间不能只凭同名或经纬度拼规则。

这些条目只是按 GeoNames 编码核对的有限地名，不属于“政府已核对”集合；未完成官方行政区划逐项复核。父级关系仍有数据误差可能，不构成当地办理点或运输规则覆盖。完整乡镇范围缺失；找不到可以手填，选过城市可以停到城市，结果仍标“区 / 乡镇未填”或“手填，地点未核实”。

维护者下载上述文件至专用临时目录后，可运行：

```sh
python scripts/import_places.py --dump-dir /path/to/geonames-dumps
python scripts/build_pages.py --write-source
```

导入脚本只读取本地文件、按固定 ID 取小切片，不按人口过滤，不从行政邻近推断。版本日期应在来源更新审阅时显式更新；每月检查上游更新，改名、撤并和父级变化需复核子级，旧版本留在 Git 历史。此更新频率是维护约定，本次没有设置外部联系或自动定时任务。
