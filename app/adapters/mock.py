import logging
from typing import Optional

from app.schemas.case import CaseBrief, CaseDetail

from .base import BaseCaseAdapter

logger = logging.getLogger(__name__)

MOCK_CASES: dict[int, CaseDetail] = {
    1001: CaseDetail(
        id=1001,
        doc_id="wenshu_001",
        case_id="(2023)京01民终1234号",
        case_name="张三与李四房屋买卖合同纠纷案",
        court="北京市第一中级人民法院",
        case_type="民事",
        procedure="二审",
        judgment_date="2023-06-15",
        public_date="2023-07-01",
        parties="张三，李四",
        cause="房屋买卖合同纠纷",
        legal_basis="《中华人民共和国民法典》第五百七十七条，第五百八十四条",
        full_text=(
            "北京市第一中级人民法院\n民事判决书\n(2023)京01民终1234号\n\n"
            "上诉人（原审原告）：张三，男，1975年3月12日出生，汉族，住北京市海淀区。\n"
            "被上诉人（原审被告）：李四，男，1980年7月8日出生，汉族，住北京市朝阳区。\n\n"
            "上诉人张三因与被上诉人李四房屋买卖合同纠纷一案，不服北京市海淀区人民法院"
            "(2022)京0108民初5678号民事判决，向本院提起上诉。\n\n"
            "经审理查明：2022年1月，张三与李四签订《房屋买卖合同》，约定李四将其位于"
            "北京市朝阳区某小区的房屋以总价350万元出售给张三。合同约定，李四应在2022年"
            "6月30日前完成过户手续。张三已支付定金35万元。\n\n"
            "李四在约定期限届满后未能完成过户手续，经张三多次催告仍未履行。张三遂诉至法院，"
            "请求解除合同、返还定金并赔偿损失。\n\n"
            "本院认为：李四未按约定履行过户义务，构成违约。依据《中华人民共和国民法典》"
            "第五百七十七条，违约方应承担继续履行、采取补救措施或者赔偿损失等违约责任。"
            "依据第五百八十四条，损失赔偿额应当相当于因违约所造成的损失。\n\n"
            "综上，本院判决如下：\n"
            "一、解除张三与李四签订的《房屋买卖合同》；\n"
            "二、李四于本判决生效之日起十五日内返还张三定金35万元；\n"
            "三、李四赔偿张三损失15万元。\n\n"
            "审判长 王法官\n审判员 赵法官\n审判员 刘法官\n"
            "二〇二三年六月十五日\n书记员 陈某"
        ),
    ),
    1002: CaseDetail(
        id=1002,
        doc_id="wenshu_002",
        case_id="(2023)沪02刑终456号",
        case_name="王五盗窃案",
        court="上海市第二中级人民法院",
        case_type="刑事",
        procedure="二审",
        judgment_date="2023-08-20",
        public_date="2023-09-10",
        parties="王五",
        cause="盗窃罪",
        legal_basis="《中华人民共和国刑法》第二百六十四条",
        full_text=(
            "上海市第二中级人民法院\n刑事判决书\n(2023)沪02刑终456号\n\n"
            "上诉人（原审被告人）：王五，男，1990年5月20日出生，汉族，无固定职业，"
            "住上海市浦东新区。\n\n"
            "上海市浦东新区人民检察院指控被告人王五犯盗窃罪一案，浦东新区人民法院作出"
            "(2023)沪0115刑初789号刑事判决。王五不服，提出上诉。\n\n"
            "经审理查明：2023年1月至3月间，被告人王五先后三次在上海市浦东新区某商场内"
            "盗窃商品，共计价值人民币12,800元。具体犯罪事实如下：\n"
            "1. 2023年1月15日，盗窃手机一部，价值3,500元；\n"
            "2. 2023年2月20日，盗窃笔记本电脑一台，价值6,800元；\n"
            "3. 2023年3月10日，盗窃平板电脑一台，价值2,500元。\n\n"
            "本院认为：上诉人王五以非法占有为目的，多次盗窃公私财物，数额较大，其行为已"
            "构成盗窃罪。原判认定事实清楚，证据确实、充分，定罪准确，量刑适当。\n\n"
            "依据《中华人民共和国刑法》第二百六十四条之规定，判决如下：\n"
            "驳回上诉，维持原判。\n"
            "即被告人王五犯盗窃罪，判处有期徒刑一年六个月，并处罚金人民币五千元。\n\n"
            "审判长 孙法官\n审判员 周法官\n审判员 吴法官\n"
            "二〇二三年八月二十日\n书记员 郑某"
        ),
    ),
    1003: CaseDetail(
        id=1003,
        doc_id="wenshu_003",
        case_id="(2024)粤03行终78号",
        case_name="某公司与深圳市市场监督管理局行政处罚纠纷案",
        court="深圳市中级人民法院",
        case_type="行政",
        procedure="二审",
        judgment_date="2024-01-10",
        public_date="2024-02-01",
        parties="某科技有限公司，深圳市市场监督管理局",
        cause="行政处罚",
        legal_basis="《中华人民共和国行政处罚法》第三十二条，第三十三条",
        full_text=(
            "深圳市中级人民法院\n行政判决书\n(2024)粤03行终78号\n\n"
            "上诉人（原审原告）：某科技有限公司，住所地深圳市南山区。\n"
            "被上诉人（原审被告）：深圳市市场监督管理局。\n\n"
            "上诉人某科技有限公司因与被上诉人深圳市市场监督管理局行政处罚纠纷一案，不服"
            "深圳市南山区人民法院(2023)粤0305行初123号行政判决，向本院提起上诉。\n\n"
            "经审理查明：2023年5月，深圳市市场监督管理局在检查中发现某科技有限公司销售"
            "的电子产品未取得3C认证，违反了《中华人民共和国产品质量法》相关规定。市场监督"
            "管理局作出行政处罚决定，责令停止销售并罚款人民币20万元。\n\n"
            "某科技有限公司不服该处罚决定，认为其产品属于豁免类别，无需3C认证。\n\n"
            "本院认为：根据相关法律规定及证据审查，涉案产品确属强制认证目录范围内，不属于"
            "豁免类别。被上诉人作出的行政处罚决定事实清楚、程序合法、适用法律正确。但考虑"
            "到上诉人系初次违法且积极整改，依据《中华人民共和国行政处罚法》第三十二条、"
            "第三十三条，可以从轻处罚。\n\n"
            "判决如下：\n"
            "一、撤销原审判决；\n"
            "二、变更罚款金额为人民币10万元，其余处罚内容维持不变。\n\n"
            "审判长 黄法官\n审判员 林法官\n审判员 何法官\n"
            "二〇二四年一月十日\n书记员 曾某"
        ),
    ),
    1004: CaseDetail(
        id=1004,
        doc_id="wenshu_004",
        case_id="(2023)苏05民初2345号",
        case_name="赵六与钱七房屋买卖合同纠纷案",
        court="苏州市中级人民法院",
        case_type="民事",
        procedure="一审",
        judgment_date="2023-11-28",
        public_date="2023-12-15",
        parties="赵六，钱七",
        cause="房屋买卖合同纠纷",
        legal_basis="《中华人民共和国民法典》第五百六十三条，第五百六十六条",
        full_text=(
            "苏州市中级人民法院\n民事判决书\n(2023)苏05民初2345号\n\n"
            "原告：赵六，男，1985年9月3日出生，汉族，住苏州市吴中区。\n"
            "被告：钱七，女，1988年11月15日出生，汉族，住苏州市工业园区。\n\n"
            "原告赵六诉被告钱七房屋买卖合同纠纷一案，本院受理后依法进行了审理。\n\n"
            "经审理查明：2023年3月，赵六与钱七签订房屋买卖合同，约定钱七将其位于苏州市"
            "工业园区的房屋以280万元出售给赵六。赵六已支付首付款84万元。合同签订后，"
            "钱七以房价上涨为由拒绝继续履行合同。\n\n"
            "本院认为：钱七以房价上涨为由拒绝履行合同，属于根本违约。根据《中华人民共和国"
            "民法典》第五百六十三条，当事人一方迟延履行债务或者有其他违约行为致使不能实现"
            "合同目的，当事人可以解除合同。依据第五百六十六条，合同解除后，尚未履行的，终止"
            "履行；已经履行的，根据履行情况和合同性质，当事人可以请求恢复原状或者采取其他"
            "补救措施，并有权请求赔偿损失。\n\n"
            "判决如下：\n"
            "一、解除赵六与钱七签订的《房屋买卖合同》；\n"
            "二、钱七返还赵六首付款84万元；\n"
            "三、钱七赔偿赵六损失30万元（含房屋差价损失）。\n\n"
            "审判长 杨法官\n审判员 许法官\n人民陪审员 沈某\n"
            "二〇二三年十一月二十八日\n书记员 朱某"
        ),
    ),
}


class MockAdapter(BaseCaseAdapter):
    def __init__(self) -> None:
        logger.info("Using MockAdapter with %d sample cases", len(MOCK_CASES))

    async def search(self, query: str, offset: int = 0, limit: int = 20) -> tuple[int, list[CaseBrief]]:
        results = []
        for case in MOCK_CASES.values():
            if (
                query in case.case_name
                or query in case.cause
                or query in case.full_text
                or query in case.court
                or query in case.case_type
                or query in case.parties
                or query in case.legal_basis
            ):
                brief = CaseBrief(
                    id=case.id,
                    case_id=case.case_id,
                    case_name=case.case_name,
                    court=case.court,
                    case_type=case.case_type,
                    procedure=case.procedure,
                    judgment_date=case.judgment_date,
                    cause=case.cause,
                    preview=case.full_text[:200],
                )
                results.append(brief)

        total = len(results)
        paginated = results[offset : offset + limit]
        return total, paginated

    async def get_case(self, case_id: int) -> CaseDetail | None:
        return MOCK_CASES.get(case_id)

    async def close(self) -> None:
        pass
