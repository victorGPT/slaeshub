#!/usr/bin/env python3
"""
Sales Hub — 客户分层模拟脚本 V1
基于《A交易所_高价值与高潜客户计算公式_V1》

生成 100 个模拟客户，计算 N90 / F90 / E90，
按公式跑分类决策树，输出 CSV + 控制台汇总。

纯标准库，无需安装任何依赖。
"""

import random
import math
import csv
import statistics
from collections import Counter

# ── 随机种子（固定可复现）
random.seed(42)
ε = 1e-8


# ──────────────────────────────────────────
# 1. 数据生成
# ──────────────────────────────────────────

def lognormal(mu, sigma):
    """对数正态分布随机数"""
    return math.exp(random.gauss(mu, sigma))

# 客户类型及权重
# heavy_trader : 高频交易，F 中等，E 高
# balanced     : 交易+资产均衡，F 高，E 健康
# asset_heavy  : 纯资产型，F 高，E 低 → 高潜典型
# moderate     : 中等规模，各维度一般
# small        : 小客户，F/N 都低 → 非主榜典型
CLIENT_TYPES = ['heavy_trader', 'balanced', 'asset_heavy', 'moderate', 'small']
CLIENT_WEIGHTS = [12, 18, 20, 25, 25]

# 中文名生成（姓 + 名，避免重复）
SURNAMES = list("王李张刘陈杨黄赵吴周徐孙马胡朱郭何林罗高郑梁谢宋唐")
GIVEN = list("伟芳娜秀英敏静冰玲欢晨阳明志强磊勇超俊峰涛浩鹏飞琳雅")

def gen_name(used):
    for _ in range(200):
        n = random.choice(SURNAMES) + random.choice(GIVEN) + random.choice(GIVEN)
        if n not in used:
            used.add(n)
            return n
    return f"客户{len(used)+1:03d}"

def gen_uid(used):
    for _ in range(500):
        uid = str(random.randint(10000000, 99999999))
        if uid not in used:
            used.add(uid)
            return uid

def generate_clients(n=100):
    clients = []
    used_names, used_uids = set(), set()

    for i in range(n):
        ctype = random.choices(CLIENT_TYPES, weights=CLIENT_WEIGHTS)[0]
        name  = gen_name(used_names)
        uid   = gen_uid(used_uids)

        # ── F90：日均总资金沉淀（单位 USD）
        if ctype == 'heavy_trader':
            f90 = lognormal(12.8, 0.9)    # 中等资沉，约 $360K 中位
        elif ctype == 'balanced':
            f90 = lognormal(14.2, 0.7)    # 高资沉，约 $15M 中位
        elif ctype == 'asset_heavy':
            f90 = lognormal(14.5, 0.6)    # 高资沉，约 $20M 中位
        elif ctype == 'moderate':
            f90 = lognormal(12.5, 1.0)    # 约 $270K 中位
        else:  # small
            f90 = lognormal(11.2, 1.1)    # 约 $73K 中位

        # ── E90：资金变现效率
        if ctype == 'heavy_trader':
            e90 = lognormal(-3.0, 0.5)    # 约 5% 中位
        elif ctype == 'balanced':
            e90 = lognormal(-3.8, 0.4)    # 约 2.2% 中位
        elif ctype == 'asset_heavy':
            e90 = lognormal(-5.8, 0.6)    # 约 0.3% 中位（低变现）
        elif ctype == 'moderate':
            e90 = lognormal(-4.5, 0.7)    # 约 1.1% 中位
        else:  # small
            e90 = lognormal(-5.0, 1.0)    # 约 0.67% 中位，波动大

        # ── N90 = F90 × E90
        n90 = f90 * e90

        # ── 业务净贡献拆分（N_j）
        # 根据客户类型分配各业务比例
        biz = split_business_n(n90, ctype)

        # ── 业务参与度信号（X_j）
        xsig = gen_participation(ctype, f90)

        clients.append({
            'uid':          uid,
            'name':         name,
            'type':         ctype,
            'N90':          round(n90, 2),
            'F90':          round(f90, 2),
            'E90':          round(e90, 6),
            # 业务净贡献
            'N_futures':    biz['futures'],
            'N_leverage':   biz['leverage'],
            'N_mini':       biz['mini'],
            'N_card':       biz['card'],
            'N_cloud':      biz['cloud'],
            'N_savings':    biz['savings'],    # 负值
            'N_rebate':     biz['rebate'],     # 负值
            # 参与度信号
            'X_futures_days':   xsig['futures_days'],
            'X_leverage_days':  xsig['leverage_days'],
            'X_savings_bal':    xsig['savings_bal'],
            'X_card_spend':     xsig['card_spend'],
        })

    return clients


def split_business_n(n90, ctype):
    """把 N90 按客户类型拆分到各业务"""
    # 先估算毛收入（理财/返佣是成本，从毛收入扣掉）
    # 约定：理财成本 ≈ F90 × 0.03% / 90天（年化3%），返佣 ≈ 毛收入的10%
    # 简化：直接按比例随机分配正负
    r = lambda a, b: round(random.uniform(a, b), 2)

    if ctype == 'heavy_trader':
        gross = n90 / 0.85  # 约15%是成本
        futures  = round(gross * r(0.50, 0.75), 2)
        leverage = round(gross * r(0.10, 0.25), 2)
        mini     = round(gross * r(0.02, 0.08), 2)
        card     = round(gross * r(0.01, 0.03), 2)
        cloud    = round(gross * r(0.00, 0.01), 2)
        savings  = round(-gross * r(0.05, 0.10), 2)
        rebate   = round(-gross * r(0.05, 0.10), 2)

    elif ctype == 'balanced':
        gross = n90 / 0.82
        futures  = round(gross * r(0.35, 0.55), 2)
        leverage = round(gross * r(0.08, 0.20), 2)
        mini     = round(gross * r(0.02, 0.06), 2)
        card     = round(gross * r(0.02, 0.05), 2)
        cloud    = round(gross * r(0.01, 0.03), 2)
        savings  = round(-gross * r(0.10, 0.18), 2)
        rebate   = round(-gross * r(0.05, 0.10), 2)

    elif ctype == 'asset_heavy':
        # 大部分资金在理财，贡献少
        gross = abs(n90) / 0.5 if n90 > 0 else abs(n90)
        futures  = round(gross * r(0.05, 0.20), 2)
        leverage = round(gross * r(0.02, 0.08), 2)
        mini     = round(gross * r(0.00, 0.03), 2)
        card     = round(gross * r(0.01, 0.03), 2)
        cloud    = round(gross * r(0.00, 0.02), 2)
        savings  = round(-gross * r(0.20, 0.40), 2)  # 理财成本高
        rebate   = round(-gross * r(0.03, 0.08), 2)

    elif ctype == 'moderate':
        gross = n90 / 0.83
        futures  = round(gross * r(0.30, 0.50), 2)
        leverage = round(gross * r(0.05, 0.15), 2)
        mini     = round(gross * r(0.01, 0.05), 2)
        card     = round(gross * r(0.01, 0.04), 2)
        cloud    = round(gross * r(0.00, 0.02), 2)
        savings  = round(-gross * r(0.08, 0.15), 2)
        rebate   = round(-gross * r(0.04, 0.09), 2)

    else:  # small
        gross = max(n90, 100) / 0.85
        futures  = round(gross * r(0.20, 0.45), 2)
        leverage = round(gross * r(0.03, 0.12), 2)
        mini     = round(gross * r(0.01, 0.04), 2)
        card     = round(gross * r(0.00, 0.02), 2)
        cloud    = round(gross * r(0.00, 0.01), 2)
        savings  = round(-gross * r(0.05, 0.12), 2)
        rebate   = round(-gross * r(0.03, 0.07), 2)

    return dict(futures=futures, leverage=leverage, mini=mini,
                card=card, cloud=cloud, savings=savings, rebate=rebate)


def gen_participation(ctype, f90):
    """生成参与度信号 X_j"""
    r = lambda a, b: random.randint(a, b)
    rf = lambda a, b: round(random.uniform(a, b), 2)

    if ctype == 'heavy_trader':
        return dict(futures_days=r(50,90), leverage_days=r(20,60),
                    savings_bal=round(f90*rf(0.02,0.10),2), card_spend=rf(500,5000))
    elif ctype == 'balanced':
        return dict(futures_days=r(30,70), leverage_days=r(10,40),
                    savings_bal=round(f90*rf(0.15,0.40),2), card_spend=rf(1000,8000))
    elif ctype == 'asset_heavy':
        return dict(futures_days=r(0,15), leverage_days=r(0,5),
                    savings_bal=round(f90*rf(0.50,0.85),2), card_spend=rf(0,500))
    elif ctype == 'moderate':
        return dict(futures_days=r(10,45), leverage_days=r(5,25),
                    savings_bal=round(f90*rf(0.08,0.25),2), card_spend=rf(200,3000))
    else:  # small
        return dict(futures_days=r(0,30), leverage_days=r(0,15),
                    savings_bal=round(f90*rf(0.03,0.15),2), card_spend=rf(0,1000))


# ──────────────────────────────────────────
# 2. 阈值计算
# ──────────────────────────────────────────

def percentile(data, p):
    """计算第 p 百分位数（0-100）"""
    sorted_data = sorted(data)
    idx = (p / 100) * (len(sorted_data) - 1)
    lo, hi = int(idx), min(int(idx) + 1, len(sorted_data) - 1)
    frac = idx - lo
    return sorted_data[lo] + frac * (sorted_data[hi] - sorted_data[lo])

def calc_thresholds(clients):
    n90s = [c['N90'] for c in clients]
    f90s = [c['F90'] for c in clients]

    T_N = percentile(n90s, 90)   # N90 的 90 分位
    T_F = percentile(f90s, 80)   # F90 的 80 分位

    # T_E（变现均线）：高资沉客户（F90 >= T_F）中 E90 的中位数
    high_f_e90s = [c['E90'] for c in clients if c['F90'] >= T_F]
    T_E = percentile(high_f_e90s, 50)  # 变现均线：高资沉客户 E90 中位数（P50）

    return T_N, T_F, T_E


# ──────────────────────────────────────────
# 3. 分类决策树
# ──────────────────────────────────────────

def classify(client, T_N, T_F, T_E):
    n, f, e = client['N90'], client['F90'], client['E90']

    # 机会缺口（高潜榜排序依据）
    # = 理论贡献（F90 × 变现均线 T_E） − 实际贡献（N90）
    # = F90 × (T_E − E90)
    # 含义：如果把该客户效率提升至变现均线，集团每90天可多赚多少
    opportunity_gap = round(f * max(T_E - e, 0), 2)

    if n >= T_N:
        label  = '高价值客户'
        subtype = '贡献达标型'
        reason  = f'N90={fmt(n)} 达到高贡献阈值（T_N={fmt(T_N)}）'
        # 辅助标签：沉淀强/弱
        tag = '沉淀强' if f >= T_F else '沉淀弱'

    elif f >= T_F and e >= T_E:
        label  = '高价值客户'
        subtype = '沉淀优质型'
        reason  = f'F90={fmt_m(f)} 资沉达标，E90={e:.2%} 变现效率健康'
        tag = '沉淀强'

    elif f >= T_F and e < T_E:
        label  = '高潜客户'
        subtype = '资产待释放型'
        reason  = f'F90={fmt_m(f)} 资沉达标，但 E90={e:.2%} 低于健康线（T_E={T_E:.2%}）'
        tag = ''

    else:
        label  = '非主榜客户'
        subtype = ''
        reason  = f'N90={fmt(n)} 未达高贡献阈值，F90={fmt_m(f)} 未达高资沉阈值'
        tag = ''

    # 当前价值来源（N_j 最大的业务）
    biz_n = {
        '双仓合约': client['N_futures'],
        '超级杠杆': client['N_leverage'],
        'Mini合约': client['N_mini'],
        '金融卡':   client['N_card'],
        '云算力':   client['N_cloud'],
    }
    value_source = max(biz_n, key=biz_n.get)

    # 简化推荐方向：找参与度最低的关键业务
    rec = recommend(client)

    return {
        'label':          label,
        'subtype':        subtype,
        'tag':            tag,
        'opportunity_gap': opportunity_gap,
        'reason':       reason,
        'value_source': value_source,
        'recommend':    rec,
    }


def recommend(client):
    """简化规则版推荐方向（V1）"""
    # 衍生品参与很少 → 推衍生品
    if client['X_futures_days'] < 10 and client['X_leverage_days'] < 5:
        if client['X_savings_bal'] > client['F90'] * 0.3:
            return '衍生品（现有资沉未用于交易）'
        return '衍生品（交易渗透不足）'
    # 理财余额高但没有卡业务 → 推金融卡
    if client['X_savings_bal'] > client['F90'] * 0.3 and client['X_card_spend'] < 500:
        return '金融卡（资产沉淀可转化）'
    # 合约活跃但杠杆很少 → 推超级杠杆
    if client['X_futures_days'] > 30 and client['X_leverage_days'] < 10:
        return '超级杠杆（合约用户自然延伸）'
    # 默认
    return '理财（提升资金粘性）'


# ──────────────────────────────────────────
# 4. 格式化工具
# ──────────────────────────────────────────

def fmt(v):
    if abs(v) >= 1_000_000:
        return f'${v/1_000_000:.2f}M'
    if abs(v) >= 1_000:
        return f'${v/1_000:.1f}K'
    return f'${v:.0f}'

def fmt_m(v):
    if v >= 1_000_000:
        return f'${v/1_000_000:.1f}M'
    return f'${v/1_000:.0f}K'


# ──────────────────────────────────────────
# 5. 主流程
# ──────────────────────────────────────────

def main():
    print("正在生成 100 个模拟客户...")
    clients = generate_clients(100)

    print("计算阈值 T_N / T_F / T_E...")
    T_N, T_F, T_E = calc_thresholds(clients)
    print(f"  T_N  (N90 P90)              = {fmt(T_N)}")
    print(f"  T_F  (F90 P80)              = {fmt_m(T_F)}")
    print(f"  T_E  变现均线（E90 P50 | F90≥T_F）= {T_E:.4%}")
    print()

    print("运行分类决策树...")
    results = []
    for c in clients:
        cls = classify(c, T_N, T_F, T_E)
        results.append({**c, **cls})

    # ── 汇总统计
    label_counts = Counter(r['label'] for r in results)
    print("─" * 50)
    print("分类结果汇总：")
    total = len(results)
    for label in ['高价值客户', '高潜客户', '非主榜客户']:
        cnt = label_counts.get(label, 0)
        print(f"  {label:10s}  {cnt:3d} 人  ({cnt/total*100:.0f}%)")

    hv = [r for r in results if r['label'] == '高价值客户']
    if hv:
        subtypes = Counter(r['subtype'] for r in hv)
        for st, cnt in subtypes.items():
            print(f"    └─ {st}: {cnt} 人")
        tags = Counter(r['tag'] for r in hv if r['tag'])
        for tag, cnt in tags.items():
            print(f"    └─ [{tag}]: {cnt} 人")

    print("─" * 50)

    # N90 / F90 / E90 描述统计
    n90s = [r['N90'] for r in results]
    f90s = [r['F90'] for r in results]
    e90s = [r['E90'] for r in results]
    print(f"N90  中位 {fmt(statistics.median(n90s))}  均值 {fmt(statistics.mean(n90s))}  "
          f"最大 {fmt(max(n90s))}  最小 {fmt(min(n90s))}")
    print(f"F90  中位 {fmt_m(statistics.median(f90s))}  均值 {fmt_m(statistics.mean(f90s))}  "
          f"最大 {fmt_m(max(f90s))}  最小 {fmt_m(min(f90s))}")
    print(f"E90  中位 {statistics.median(e90s):.3%}  均值 {statistics.mean(e90s):.3%}  "
          f"最大 {max(e90s):.3%}  最小 {min(e90s):.3%}")
    print()

    # ── 输出 CSV
    out_path = '/Users/victor/Developer/slaeshub/data/clients_simulation.csv'
    fields = [
        'uid', 'name', 'label', 'subtype', 'tag', 'opportunity_gap',
        'N90', 'F90', 'E90',
        'N_futures', 'N_leverage', 'N_mini', 'N_card', 'N_cloud', 'N_savings', 'N_rebate',
        'X_futures_days', 'X_leverage_days', 'X_savings_bal', 'X_card_spend',
        'value_source', 'recommend', 'reason',
    ]
    with open(out_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.DictWriter(f, fieldnames=fields, extrasaction='ignore')
        writer.writeheader()
        writer.writerows(results)

    print(f"CSV 已输出：{out_path}")
    print()

    # ── 打印部分样例
    print("─" * 50)
    print("样例（每类各展示 3 条）：")
    for label in ['高价值客户', '高潜客户', '非主榜客户']:
        samples = [r for r in results if r['label'] == label][:3]
        for s in samples:
            tag_str = f" [{s['tag']}]" if s['tag'] else ""
            sub_str = f"（{s['subtype']}）" if s['subtype'] else ""
            print(f"  {s['label']}{sub_str}{tag_str}")
            print(f"    {s['name']} UID:{s['uid']}")
            print(f"    N90={fmt(s['N90'])}  F90={fmt_m(s['F90'])}  E90={s['E90']:.3%}")
            print(f"    价值来源：{s['value_source']}  推荐方向：{s['recommend']}")
            print()


if __name__ == '__main__':
    main()
