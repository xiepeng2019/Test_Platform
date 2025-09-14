import random
from typing import Any, List
from datetime import datetime, timedelta

from fastapi import APIRouter, Request
from pydantic import BaseModel


router = APIRouter()
source = 'Mock Server'
have_read_ids = []


class ReadMessageRequest(BaseModel):
    ids: List[int] = []


@router.post("/api/message/read")
async def read_message(data: ReadMessageRequest):
    have_read_ids.extend(data.ids)
    return True


@router.get("/api/message/list")
async def list_data() -> Any:
    message_list = [
        {
            "id": 1,
            "type": 'message',
            "title": '郑曦月',
            "subTitle": '的私信',
            "avatar":
                '//p1-arco.byteimg.com/tos-cn-i-uwbnlip3yd/8361eeb82904210b4f55fab888fe8416.png~tplv-uwbnlip3yd-webp.webp',
            "content": '审批请求已发送，请查收',
            "time": '今天 12:30:01',
        },
        {
            "id": 2,
            "type": 'message',
            "title": '宁波',
            "subTitle": '的回复',
            "avatar":
                '//p1-arco.byteimg.com/tos-cn-i-uwbnlip3yd/3ee5f13fb09879ecb5185e440cef6eb9.png~tplv-uwbnlip3yd-webp.webp',
            "content":
                '此处 bug 已经修复，如有问题请查阅文档或者继续 github 提 issue～',
            "time": '今天 12:30:01',
        },
        {
            "id": 3,
            "type": 'message',
            "title": '宁波',
            "subTitle": '的回复',
            "avatar":
                '//p1-arco.byteimg.com/tos-cn-i-uwbnlip3yd/3ee5f13fb09879ecb5185e440cef6eb9.png~tplv-uwbnlip3yd-webp.webp',
            "content": '此处 bug 已经修复',
            "time": '今天 12:20:01',
        },

        {
            "id": 4,
            "type": 'todo',
            "title": '域名服务',
            "content": '内容质检队列于 2021-12-01 19:50:23 进行变更，请重新',
            "tag": {
                "text": '未开始',
                "color": 'gray',
            },
        },
        {
            "id": 5,
            "type": 'todo',
            "title": '内容审批通知',
            "content": '宁静提交于 2021-11-05，需要您在 2011-11-07之前审批',
            "tag": {
                "text": '进行中',
                "color": 'arcoblue',
            },
        },
        {
            "id": 6,
            "type": 'notice',
            "title": '质检队列变更',
            "content": '您的产品使用期限即将截止，如需继续使用产品请前往购…',
            "tag": {
                "text": '即将到期',
                "color": 'red',
            },
        },
        {
            "id": 7,
            "type": 'notice',
            "title": '规则开通成功',
            "subTitle": '',
            "avatar": '',
            "content": '内容屏蔽规则于 2021-12-01 开通成功并生效。',
            "tag": {
                "text": '已开通',
                "color": 'green',
            },
        },
    ]
    for item in message_list:
        if item['id'] in have_read_ids:
            item['status'] = 1
        else:
            item['status'] = 0
    return message_list


@router.get("/api/chatList")
async def get_data() -> Any:
    f"""
    Mock {source}.
    """
    num_items = random.randint(4, 6)
    now = datetime.now()

    chat_list = []
    for i in range(1, num_items + 1):
        chat_list.append({
            "id": i,
            "username": "用户" + str(random.randint(1000000, 9999999)),
            "content": "马上就开始了，好激动！",
            "time": now.strftime("%H:%M:%S"),
            "isCollect": random.choice([True, False]),
        })

    return chat_list


@router.get("/api/cardList")
async def get_card_list() -> Any:
    quality_category = ['视频类', '图文类', '纯文本']
    quality_name = ['历史导入', '内容版权', '敏感内容', '商业品牌']

    service_name = [
        '漏斗分析',
        '用户分布',
        '资源分发',
        '用户画像分析',
        '事件分析',
    ]

    service_descriptions = [
        '用户行为分析之漏斗分析模型是企业实现精细化运营、进行用户行为分析的重要数据分析模型。 ',
        '快速诊断用户人群，地域细分情况，了解数据分布的集中度，以及主要的数据分布的区间段是什么。',
        '移动端动态化资源分发解决方案。提供稳定大流量服务支持、灵活定制的分发圈选规则，通过离线化预加载。  ',
        '用户画像就是将典型用户信息标签化，根据用户特征、业务场景和用户行为等信息，构建一个标签化的用户模型。 ',
        '事件分析即可进行筛选、分组、聚合的灵活多维数据分析。详情请点击卡片。',
    ]

    rules_name = [
        '内容屏蔽规则',
        '内容置顶规则',
        '内容加权规则',
        '内容分发规则',
        '多语言文字符号识别',
    ]

    rules_description = [
        '用户在执行特定的内容分发任务时，可使用内容屏蔽规则根据特定标签，过滤内容集合。  ',
        '该规则支持用户在执行特定内容分发任务时，对固定的几条内容置顶。',
        '选定内容加权规则后可自定义从不同内容集合获取内容的概率。',
        '内容分发时，对某些内容需要固定在C端展示的位置。',
        '精准识别英语、维语、藏语、蒙古语、朝鲜语等多种语言以及emoji表情形态的语义识别。',
    ]

    def get_quality_card():
        return [
            {
                "title": f"{random.choice(quality_category)}-{random.choice(quality_name)}",
                "time": (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d %H:%M:%S"),
                "qualityCount": random.randint(100, 500),
                "randomCount": random.randint(0, 100),
                "duration": random.randint(0, 200),
            }
            for _ in range(10)
        ]

    def get_service_card():
        cards = []
        for _ in range(10):
            icon_index = random.randint(0, len(service_name) - 1)
            cards.append({
                "icon": icon_index,
                "title": service_name[icon_index],
                "description": service_descriptions[icon_index],
                "status": random.randint(0, 2),
            })
        return cards

    def get_rules_card():
        cards = []
        for _ in range(10):
            index = random.randint(0, len(rules_name) - 1)
            cards.append({
                "index": index,
                "title": rules_name[index],
                "description": rules_description[index],
                "status": random.randint(0, 1),
            })
        return cards

    return {
        "quality": get_quality_card(),
        "service": get_service_card(),
        "rules": get_rules_card(),
    }


@router.get("/api/workplace/overview-content")
async def get_overview_content() -> Any:
    year = datetime.now().year
    line_data = [
        {
            "date": f"{year}-{i + 1}",
            "count": random.randint(20000, 75000)
        }
        for i in range(12)
    ]
    return {
        "allContents": "373.5w+",
        "liveContents": "368",
        "increaseComments": "8874",
        "growthRate": "2.8%",
        "chartData": line_data,
    }


def get_list():
    return [
        {
            "rank": i + 1,
            "title": random.choice([
                '经济日报：财政政策要精准提升效能',
                '“双12”遇冷消费者厌倦了电商平台的促销“套路”',
                '致敬坚守战“疫”一线的社区工作者',
                '普高还是职高？家长们陷入选校难题',
            ]),
            "pv": 500000 - 3200 * (i + 1),
            "increase": round(random.uniform(-1, 1), 2)
        }
        for i in range(100)
    ]

list_text = get_list()
list_pic = get_list()
list_video = get_list()

@router.get("/api/workplace/popular-contents")
async def get_popular_contents(request: Request) -> Any:
    query_params = request.query_params
    page = int(query_params.get("page", 1))
    pageSize = int(query_params.get("pageSize", 5))
    category = int(query_params.get("category", 0))

    lists = [list_text, list_pic, list_video]
    target_list = lists[category]
    start = (page - 1) * pageSize
    end = start + pageSize
    return {
        "list": target_list[start:end],
        "total": 100,
    }


@router.get("/api/workplace/content-percentage")
async def get_content_percentage() -> Any:
    return [
        {
            "type": '纯文本',
            "count": 148564,
            "percent": 0.16,
        },
        {
            "type": '图文类',
            "count": 334271,
            "percent": 0.36,
        },
        {
            "type": '视频类',
            "count": 445695,
            "percent": 0.48,
        },
    ]


@router.get("/api/workplace/announcement")
async def get_announcement() -> Any:
    return [
        {
            "type": 'activity',
            "key": '1',
            "content": '内容最新优惠活动',
        },
        {
            "type": 'info',
            "key": '2',
            "content": '新增内容尚未通过审核，详情请点击查看。',
        },
        {
            "type": 'notice',
            "key": '3',
            "content": '当前产品试用期即将结束，如需续费请点击查看。',
        },
        {
            "type": 'notice',
            "key": '4',
            "content": '1 月新系统升级计划通知',
        },
        {
            "type": 'info',
            "key": '5',
            "content": '新增内容已经通过审核，详情请点击查看。',
        },
    ]


@router.get("/api/data-analysis/overview")
async def get_data_analysis_overview(request: Request) -> Any:
    query_params = request.query_params
    chart_type = query_params.get("type", "line")

    def mock_line(name):
        return [
            {
                "y": random.randint(20, 100),
                "x": i,
                "name": name,
            }
            for i in range(12)
        ]

    def mock_pie():
        return [
            {
                "name": name,
                "count": random.randint(20, 100),
            }
            for name in ['纯文本', '图文类', '视频类']
        ]

    chart_data = []
    if chart_type == 'pie':
        chart_data = mock_pie()
    elif chart_type == 'line':
        chart_data.extend(mock_line('类目1'))
        chart_data.extend(mock_line('类目2'))
    else:
        chart_data.extend(mock_line('类目1'))

    return {
        "count": random.randint(1000, 10000),
        "increment": random.choice([True, False]),
        "diff": random.randint(100, 1000),
        "chartType": chart_type,
        "chartData": chart_data,
    }


@router.get("/api/data-analysis/content-publishing")
async def get_content_publishing() -> Any:
    def get_time_line(name):
        time_arr = [f"{i * 2:02d}:00" for i in range(12)]
        return [
            {
                "name": name,
                "time": time_arr[i],
                "count": random.randint(1000, 5000),
                "rate": random.randint(0, 100),
            }
            for i in range(12)
        ]

    result = []
    result.extend(get_time_line('纯文本'))
    result.extend(get_time_line('视频类'))
    result.extend(get_time_line('图文类'))
    return result


@router.get("/api/data-analysis/author-list")
async def get_author_list() -> Any:
    authors = [
        '用魔法打败魔法',
        '王多鱼',
        'Christopher',
        '叫我小李好了',
        '陈皮话梅糖',
        '碳烤小肥羊',
    ]
    time_arr = [f"{i * 2:02d}:00" for i in range(12)]
    
    author_list = []
    for i in range(1, 9):
        author_list.append({
            "id": i,
            "author": random.choice(authors),
            "time": time_arr[i % 12],
            "contentCount": random.randint(1000, 5000),
            "clickCount": random.randint(5000, 30000),
        })
    return {"list": author_list}

@router.get("/api/multi-dimension/overview")
async def get_multi_dimension_overview() -> Any:
    legend = ['活跃用户数', '内容生产量', '内容点击量', '内容曝光量']
    count = [0, 600, 1000, 2000, 4000]

    def get_line_data(name, index):
        return [
            {
                "time": (datetime.now() - timedelta(days=i)).strftime("%m-%d"),
                "count": random.randint(count[index], count[index + 1]),
                "name": name,
            }
            for i in range(1, 11)
        ]

    overview_data = [random.randint(0, 10000) for _ in range(4)]
    chart_data = []
    for i, name in enumerate(legend):
        chart_data.extend(get_line_data(name, i))

    return {
        "overviewData": overview_data,
        "chartData": chart_data,
    }


@router.get("/api/multi-dimension/activity")
async def get_multi_dimension_activity() -> Any:
    return [
        {
            "name": name,
            "count": random.randint(1000, 10000),
        }
        for name in ['分享量', '评论量', '点赞量']
    ]


@router.get("/api/multi-dimension/polar")
async def get_multi_dimension_polar() -> Any:
    items = ['国际', '娱乐', '体育', '财经', '科技', '其他']
    category = ['纯文本', '图文类', '视频类']

    def get_category_count():
        return {name: random.randint(0, 100) for name in category}

    return {
        "list": [
            {
                "item": item,
                **get_category_count(),
            }
            for item in items
        ],
        "fields": category,
    }


@router.get("/api/multi-dimension/card")
async def get_multi_dimension_card(request: Request) -> Any:
    query_params = request.query_params
    chart_type = query_params.get("type", "line")

    def mock_line(name):
        result = sorted([random.randint(1000, 10000) for _ in range(12)])
        return [
            {
                "y": y,
                "x": i,
                "name": name,
            }
            for i, y in enumerate(result)
        ]

    return {
        "count": random.randint(1000, 10000),
        "increment": random.choice([True, False]),
        "diff": random.randint(100, 1000),
        "chartType": chart_type,
        "chartData": mock_line('类目1'),
    }


@router.get("/api/multi-dimension/content-source")
async def get_multi_dimension_content_source() -> Any:
    category = ['纯文本', '图文类', '视频类']
    type_list = ['UGC原创', '国外网站', '转载文章', '行业报告', '其他']

    def get_content_source(name):
        result = [
            {
                "type": type_name,
                "value": random.randint(100, 10000),
                "name": name,
            }
            for type_name in type_list
        ]
        total = sum(item['value'] for item in result)
        return [
            {
                **item,
                "value": round(item['value'] / total, 2),
            }
            for item in result
        ]

    all_list = []
    for name in category:
        for item in get_content_source(name):
            all_list.append({
                **item,
                "category": name,
            })
    return all_list

@router.post("/api/groupForm")
async def group_form() -> Any:
    return True

@router.get("/api/basicProfile")
async def get_basic_profile() -> Any:
    return {
        "status": 2,
        "video": {
            "mode": "自定义",
            "acquisition": {
                "resolution": "720*1280",
                "frameRate": 15,
            },
            "encoding": {
                "resolution": "720*1280",
                "rate": {
                    "min": 300,
                    "max": 800,
                    "default": 1500,
                },
                "frameRate": 15,
                "profile": "high",
            },
        },
        "audio": {
            "mode": "自定义",
            "acquisition": {
                "channels": 8,
            },
            "encoding": {
                "channels": 8,
                "rate": 128,
                "profile": "ACC-LC",
            },
        },
    }


@router.get("/api/adjustment")
async def get_adjustment() -> Any:
    return [
        {
            "contentId": f"{random.choice(['视频类', '音频类'])}{random.randint(1000, 9999)}",
            "content": "视频参数变更，音频参数变更",
            "status": random.randint(0, 1),
            "updatedTime": (datetime.now() - timedelta(days=random.randint(0, 30))).strftime("%Y-%m-%d %H:%M:%S"),
        }
        for _ in range(2)
    ]

@router.get("/api/user/projectList")
async def get_user_project_list() -> Any:
    contributors = [
        {
            'name': '秦臻宇',
            'email': 'qingzhenyu@arco.design',
            'avatar':
                '//p1-arco.byteimg.com/tos-cn-i-uwbnlip3yd/a8c8cdb109cb051163646151a4a5083b.png~tplv-uwbnlip3yd-webp.webp',
        },
        {
            'name': '于涛',
            'email': 'yuebao@arco.design',
            'avatar':
                '//p1-arco.byteimg.com/tos-cn-i-uwbnlip3yd/a8c8cdb109cb051163646151a4a5083b.png~tplv-uwbnlip3yd-webp.webp',
        },
        {
            'name': '宁波',
            'email': 'ningbo@arco.design',
            'avatar':
                '//p1-arco.byteimg.com/tos-cn-i-uwbnlip3yd/3ee5f13fb09879ecb5185e440cef6eb9.png~tplv-uwbnlip3yd-webp.webp',
        },
        {
            'name': '郑曦月',
            'email': 'zhengxiyue@arco.design',
            'avatar':
                '//p1-arco.byteimg.com/tos-cn-i-uwbnlip3yd/8361eeb82904210b4f55fab888fe8416.png~tplv-uwbnlip3yd-webp.webp',
        },
        {
            'name': '宁波',
            'email': 'ningbo@arco.design',
            'avatar':
                '//p1-arco.byteimg.com/tos-cn-i-uwbnlip3yd/3ee5f13fb09879ecb5185e440cef6eb9.png~tplv-uwbnlip3yd-webp.webp',
        },
    ]
    en_titles = [
        'TestStation',
        'The Volcano Engine',
        'OCR text recognition',
        'Content resource management',
        'Toutiao content management',
        'Intelligent Robot Project',
    ]
    titles = [
        '企业级产品设计系统',
        '火山引擎智能应用',
        'OCR文本识别',
        '内容资源管理',
        '今日头条内容管理',
        '智能机器人',
    ]
    return [
        {
            'id': index,
            'enTitle': en_titles[index],
            'title': titles[index],
            'contributors': contributors,
            'contributorsLength': random.randint(5, 100),
        }
        for index in range(6)
    ]


@router.get("/api/users/team/list")
async def get_users_team_list() -> Any:
    names = [
        '火山引擎智能应用团队',
        '企业级产品设计团队',
        '前端/UE小分队',
        '内容识别插件小分队',
    ]
    avatars = [
        '//p1-arco.byteimg.com/tos-cn-i-uwbnlip3yd/a8c8cdb109cb051163646151a4a5083b.png~tplv-uwbnlip3yd-webp.webp',
        '//p1-arco.byteimg.com/tos-cn-i-uwbnlip3yd/3ee5f13fb09879ecb5185e440cef6eb9.png~tplv-uwbnlip3yd-webp.webp',
        '//p1-arco.byteimg.com/tos-cn-i-uwbnlip3yd/3ee5f13fb09879ecb5185e440cef6eb9.png~tplv-uwbnlip3yd-webp.webp',
        '//p1-arco.byteimg.com/tos-cn-i-uwbnlip3yd/8361eeb82904210b4f55fab888fe8416.png~tplv-uwbnlip3yd-webp.webp',
    ]
    return [
        {
            'name': names[index],
            'avatar': avatars[index],
            'members': random.randint(1, 1000),
        }
        for index in range(4)
    ]


@router.get("/api/user/latestNews")
async def get_user_latest_news() -> Any:
    return [
        {
            'id': index,
            'title': '王多鱼审核了图文内容： 2021年，你过得怎么样？',
            'description':
                '新华网年终特别策划：《这一年，你过得怎么样？》回访那些你最熟悉的“陌生人”带你重温这难忘的2021年回顾我们共同记忆中的生动故事！',
            'avatar':
                '//p1-arco.byteimg.com/tos-cn-i-uwbnlip3yd/a8c8cdb109cb051163646151a4a5083b.png~tplv-uwbnlip3yd-webp.webp',
        }
        for index in range(8)
    ]


@router.get("/api/user/notice")
async def get_user_notice() -> Any:
    return []

@router.post("/api/user/saveInfo")
async def save_user_info() -> Any:
    return "ok"


@router.get("/api/user/verified/enterprise")
async def get_user_verified_enterprise() -> Any:
    first_names = ['赵', '钱', '孙', '李', '周', '吴', '郑', '王']
    return {
        'accountType': '企业账号',
        'isVerified': True,
        'verifiedTime': (datetime.now() - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d %H:%M:%S'),
        'legalPersonName': f'{random.choice(first_names)}**',
        'certificateType': '中国身份证',
        'certificationNumber': f'{random.randint(100,999)}************{random.randint(100,999)}',
        'enterpriseName': random.choice(['字节跳动科技有限公司', '火山引擎有限公司', '飞书有限公司']),
        'enterpriseCertificateType': '企业营业执照',
        'organizationCode': f'{random.randint(1,9)}*******{random.randint(0,9)}',
    }


@router.get("/api/user/verified/authList")
async def get_user_verified_auth_list() -> Any:
    first_names = ['赵', '钱', '孙', '李', '周', '吴', '郑', '王']
    return [
        {
            'authType': '企业证件认证',
            'authContent': f'企业证件认证，法人姓名{random.choice(first_names)}**',
            'authStatus': random.randint(0, 1),
            'createdTime': (datetime.now() - timedelta(days=random.randint(0, 30))).strftime('%Y-%m-%d %H:%M:%S'),
        }
        for _ in range(3)
    ]

def generate_mock_list():
    return [
        {
            "id": f"{random.randint(10000000, 99999999)}-{random.randint(1000, 9999)}",
            "name": random.choice(['每日推荐视频集', '抖音短视频候选集', '国际新闻集合']),
            "contentType": random.randint(0, 2),
            "filterType": random.randint(0, 1),
            "count": random.randint(0, 2000),
            "createdTime": random.randint(1, 60),
            "status": random.randint(0, 1),
        }
        for _ in range(100)
    ]

mock_list = generate_mock_list()

@router.get("/api/list")
async def get_list_data(request: Request):
    query_params = request.query_params
    page = int(query_params.get("page", 1))
    page_size = int(query_params.get("pageSize", 10))
    
    filtered_data = mock_list

    if 'id' in query_params:
        filtered_data = [item for item in filtered_data if item['id'] == query_params['id']]

    if 'name' in query_params:
        name_query = query_params['name'].lower()
        filtered_data = [item for item in filtered_data if name_query in item['name'].lower()]

    content_type_list = query_params.getlist('contentType[]')
    if content_type_list:
        filtered_data = [item for item in filtered_data if str(item['contentType']) in content_type_list]

    filter_type_list = query_params.getlist('filterType[]')
    if filter_type_list:
        filtered_data = [item for item in filtered_data if str(item['filterType']) in filter_type_list]

    created_time_range = query_params.getlist('createdTime[]')
    if len(created_time_range) == 2:
        start_date_str = created_time_range[0].split('T')[0]
        end_date_str = created_time_range[1].split('T')[0]
        start_date = datetime.strptime(start_date_str, '%Y-%m-%d')
        end_date = datetime.strptime(end_date_str, '%Y-%m-%d')
        
        def is_in_range(item):
            item_time = datetime.now() - timedelta(days=item['createdTime'])
            return start_date <= item_time <= end_date

        filtered_data = [item for item in filtered_data if is_in_range(item)]

    status_list = query_params.getlist('status[]')
    if status_list:
        filtered_data = [item for item in filtered_data if str(item['status']) in status_list]

    total = len(filtered_data)
    start_index = (page - 1) * page_size
    end_index = start_index + page_size
    paginated_data = filtered_data[start_index:end_index]

    return {
        "list": paginated_data,
        "total": total,
    }