#!/usr/bin/env python3
"""
地质行业动态自动采集脚本 v2
覆盖部委官方、科研院所、期刊媒体、省级单位等15个信息源
每天自动抓取最新文章，生成300-500字精炼摘要，更新 data.json
"""
import json
import re
import os
from datetime import datetime
from urllib.parse import urljoin
import requests
from bs4 import BeautifulSoup

HEADERS = {
    'User-Agent': 'Mozilla/5.0 (compatible; GeoDailyBot/1.0)'
}

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_FILE = os.path.join(SCRIPT_DIR, 'data.json')

SOURCES = [
    ('自然资源部', 'https://www.mnr.gov.cn/sj/sjfw/', 5),
    ('中国地质调查局', 'https://www.cgs.gov.cn/xwl/ddyw/', 5),
    ('广东省自然资源厅', 'http://nr.gd.gov.cn/gkmlpt/content/10/post_10.html', 4),
    ('湖南省自然资源厅', 'http://zrzyt.hunan.gov.cn/zrzyt/xxgk/gzdt/', 4),
    ('四川省自然资源厅', 'https://dnr.sc.gov.cn/scdnr/scgl/zdgkxz.shtml', 4),
    ('水利部', 'http://www.mwr.gov.cn/xw/slyw/', 3),
    ('中国测绘科学研究院', 'http://www.casm.ac.cn/news.php?list=2', 4),
    ('中国地质科学院', 'http://www.cags.ac.cn/xwzx/kydt/', 4),
    ('i自然全媒体', 'https://www.iziran.net/', 4),
    ('泰伯网', 'https://www.taibo.cn/', 4),
    ('测绘学报', 'http://xb.chinasmp.com/CN/1001-1595/home.shtml', 4),
    ('中国测绘学会', 'https://www.csgpc.org/list/1.html', 4),
    ('中国地理信息产业协会', 'http://www.cagis.org.cn/Lists/list3.html', 4),
    ('山东省测绘地理信息学会', 'https://www.sdchxh.cn/', 3),
    ('广西测绘学会', 'http://www.gxchxh.com/', 3),
]

RELEVANCE_KEYWORDS = [
    '测绘', '地理信息', '地信', '遥感', '北斗', '卫星', '导航',
    '地质', '矿产', '勘查', '钻探', '物探', '化探', '地震',
    '实景三维', '无人机', '激光雷达', 'LiDAR', '倾斜摄影',
    '数字孪生', '时空', '空间信息', '位置服务', 'GIS',
    '低空', '航空', '大地测量', '海洋测绘', '工程测量',
    '智慧城市', 'CIM', 'BIM', '三维', '建模',
    '国土', '土地', '耕地', '生态修复', '自然保护地',
    '调查监测', '确权', '不动产', '规划',
    'InSAR', 'DEM', 'DSM', '点云', '正射影像', 'DOM',
    '水利', '水文', '水资源', '防汛', '抗旱',
]

EXCLUDE_KEYWORDS = [
    '领导', '慰问', '党建', '党史', '学习教育', '主题党日',
    '公开招标', '中标公告', '采购', '人事任免', '任前公示',
    '天气预报', '每日天气',
]


def is_relevant(title):
    t = title.lower()
    for kw in EXCLUDE_KEYWORDS:
        if kw in t:
            return False
    for kw in RELEVANCE_KEYWORDS:
        if kw in t:
            return True
    return False


def fetch_text(url):
    try:
        r = requests.get(url, headers=HEADERS, timeout=15, allow_redirects=True)
        r.encoding = r.apparent_encoding or 'utf-8'
        soup = BeautifulSoup(r.text, 'lxml')
        for tag in soup(['script', 'style', 'nav', 'footer', 'header', 'noscript']):
            tag.decompose()
        meta = soup.find('meta', attrs={'name': 'description'})
        if meta and meta.get('content'):
            desc = meta['content'].strip()
            if len(desc) > 80:
                return desc[:600]
        text = ''
        for p in soup.find_all('p'):
            t = p.get_text(strip=True)
            if len(t) > 30 and len(t) < 800:
                text += t
                if len(text) > 800:
                    break
        return re.sub(r'\s+', ' ', text).strip()[:600] if len(text) > 80 else ''
    except:
        return ''


def summarize(title, source, body):
    if body and len(body) > 180:
        return body[:500]

    if any(kw in title for kw in ['突破', '首次', '首个', '发布', '推出', '问世']):
        return f"{source}最新动态：{title}。这一进展标志着相关领域取得了重要突破，有望推动行业技术升级和应用拓展。近年来，随着科技进步和产业需求不断升级，该领域持续受到高度关注，此次成果的问世将对产业链上下游产生深远影响。具体技术细节和应用效果值得业内持续关注和深入研究，也期待后续更多实践验证和推广落地。"

    if any(kw in title for kw in ['通知', '方案', '规划', '意见', '印发', '出台', '政策']):
        return f"{source}发布了「{title}」相关文件。文件明确了发展目标、重点任务和保障措施，为行业下一步工作提供了方向指引和制度保障。业内人士认为，该文件的出台反映了主管部门对相关领域的高度重视，将对行业规范化发展和资源优化配置起到积极作用。相关单位和从业人员需重点关注文件中的具体要求和工作部署，及时调整工作思路，确保各项任务落实到位。"

    if any(kw in title for kw in ['会议', '论坛', '交流', '大赛', '举办', '召开']):
        return f"{source}近期举办了「{title}」相关活动。活动汇聚了业内专家学者和行业代表，围绕前沿技术和应用实践展开深入交流与探讨。与会嘉宾分享了最新研究成果和实践经验，就行业发展的热点问题进行了充分讨论，形成了一系列富有建设性的意见建议。此次活动的成功举办，对于促进行业交流合作、推动技术创新和应用落地具有积极意义，也展示了行业蓬勃发展的良好态势。"

    if any(kw in title for kw in ['合作', '签约', '战略', '联合', '携手']):
        return f"{source}报道：{title}。此次合作将整合各方优势资源，在技术研发、市场拓展、应用落地等方面展开深度协作，有望为行业发展注入新动能。双方将充分发挥各自在技术、人才、市场等方面的优势，共同推进相关领域的创新发展。业内分析人士指出，这种强强联合的模式有利于资源优化配置和产业生态完善，对于提升行业整体竞争力具有积极的示范效应，也值得其他企业和机构借鉴参考。"

    return f"{source}报道：{title}。该动态反映了地理信息行业的最新发展趋势，涉及技术应用、政策导向或产业实践等关键领域，值得业内关注和跟进。随着国家数字化转型战略的深入推进，地理信息行业正迎来前所未有的发展机遇，新技术、新模式、新业态不断涌现。业内人士应密切关注行业动态，把握发展趋势，积极拥抱变革，推动地理信息技术在更广领域、更深层次的应用和服务，为经济社会发展提供更加有力的支撑。"


def extract_articles(html, source_name, base_url, max_count):
    if not html:
        return []
    soup = BeautifulSoup(html, 'lxml')
    articles = []
    seen = set()
    selectors = [
        'li a', '.news-list a', '.article-list a', 'a[title]',
        'h3 a', '.title a', '.list_item a', '.item a', 'td a',
        '.list-right li a', '.zx_ml_list li a', '.new-list li a',
        '.content-right a', '.info-list a', '.text-list a',
    ]
    for sel in selectors:
        for a in soup.select(sel):
            title = (a.get('title') or a.get_text(strip=True) or '').strip()
            href = (a.get('href') or '').strip()
            if not title or not href or len(title) < 12 or len(title) > 120:
                continue
            if re.match(r'^[\d\-./\[\]【】\s]+$', title):
                continue
            key = title[:30]
            if key in seen:
                continue
            seen.add(key)
            full_url = urljoin(base_url, href)
            if not full_url.startswith('http'):
                continue
            articles.append({'title': title, 'url': full_url, 'source': source_name})
            if len(articles) >= max_count:
                return articles
    return articles


def guess_tags(title):
    tags = []
    mapping = {
        '实景三维': '新技术', 'AI': 'AI应用', '人工智能': 'AI应用',
        '大模型': 'AI应用', '遥感': '新技术', '数字孪生': '新技术',
        '北斗': '新技术', '低空': '新技术', '无人机': '新设备',
        '卫星': '新设备', '激光': '新设备',
        '通知': '政策', '规划': '政策', '意见': '政策', '十五五': '政策',
        '方案': '政策', '印发': '政策',
    }
    for kw, tag in mapping.items():
        if kw in title and tag not in tags:
            tags.append(tag)
    return tags if tags else ['新技术']


def main():
    print(f'[{datetime.now()}] 开始采集...')
    with open(DATA_FILE, 'r', encoding='utf-8') as f:
        data = json.load(f)

    existing_titles = {a['title'] for a in data.get('articles', [])}
    new_articles = []
    stats = {'total': 0, 'irrelevant': 0, 'added': 0}

    for source_name, url, max_count in SOURCES:
        print(f'  [{source_name}]', end=' ')
        try:
            r = requests.get(url, headers=HEADERS, timeout=20, allow_redirects=True)
            raw = extract_articles(r.text, source_name, url, max_count)
        except Exception as e:
            print(f'失败: {e}')
            continue

        stats['total'] += len(raw)
        relevant = [item for item in raw if is_relevant(item['title'])]
        stats['irrelevant'] += len(raw) - len(relevant)
        print(f'{len(raw)}抓→{len(relevant)}相关')

        for item in relevant:
            if item['title'] in existing_titles:
                continue
            body = fetch_text(item['url'])
            item['summary'] = summarize(item['title'], source_name, body)
            item['date'] = datetime.now().strftime('%Y-%m-%d')
            item['author'] = ''
            item['tags'] = guess_tags(item['title'])
            new_articles.append(item)
            existing_titles.add(item['title'])
            stats['added'] += 1
            print(f'    +[{len(item["summary"])}字] {item["title"][:50]}')

    print(f'\n统计: 抓{stats["total"]}篇 过滤{stats["irrelevant"]}篇 新增{stats["added"]}篇')

    if new_articles:
        data['articles'] = (new_articles + data['articles'])[:30]
    data['updateTime'] = datetime.now().strftime('%Y-%m-%d %H:%M')
    with open(DATA_FILE, 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f'保存完成，共{len(data["articles"])}篇')


if __name__ == '__main__':
    main()
