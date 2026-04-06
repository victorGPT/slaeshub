// 统一 mock 数据种子
// 所有页面共用，仅在对应 key 为空时注入，不覆盖用户操作
(function() {

  function tryGet(key) {
    try { return JSON.parse(localStorage.getItem(key) || 'null'); } catch(e) { return null; }
  }
  function trySet(key, val) {
    try { localStorage.setItem(key, JSON.stringify(val)); } catch(e) {}
  }

  // ── 1. follow_up_events ──────────────────────────────────────────
  if (!tryGet('follow_up_events') || tryGet('follow_up_events').length === 0) {
    trySet('follow_up_events', [
      { id: 'sys_001', client_uid: '52339391', client_name: '胡军',   type: '大额充值', title: '充值 $126万，占资产 30%',      source: 'system', status: 'active',   created_at: '2026-04-03T09:15:00Z', meta: { amount: 1260000, amountDisplay: '$126万', assetRatio: 0.30 } },
      { id: 'sys_002', client_uid: '33978249', client_name: '何敏',   type: '大额充值', title: '充值 $19万，占资产 30%',       source: 'system', status: 'active',   created_at: '2026-04-03T10:02:00Z', meta: { amount: 190000,  amountDisplay: '$19万',  assetRatio: 0.30 } },
      { id: 'sys_003', client_uid: '19528530', client_name: '李勇',   type: '大额提现', title: '提现 $109万，占资产 20%',      source: 'system', status: 'active',   created_at: '2026-04-03T10:45:00Z', meta: { amount: 1090000, amountDisplay: '$109万', assetRatio: 0.20 } },
      { id: 'sys_004', client_uid: '10289289', client_name: '陈伟',   type: '大额盈利', title: '7日盈利 $23万，占资产 7%',     source: 'system', status: 'active',   created_at: '2026-04-03T11:00:00Z', meta: { amount: 230000,  amountDisplay: '$23万',  assetRatio: 0.07 } },
      { id: 'sys_005', client_uid: '82160068', client_name: '赵静',   type: '大额充值', title: '充值 $357万，占资产 30%',      source: 'system', status: 'active',   created_at: '2026-04-03T11:30:00Z', meta: { amount: 3570000, amountDisplay: '$357万', assetRatio: 0.30 } },
      { id: 'sys_006', client_uid: '51373735', client_name: '孙芳',   type: '大额亏损', title: '7日亏损 $58万，占资产 5%',     source: 'system', status: 'active',   created_at: '2026-04-03T13:10:00Z', meta: { amount: -580000, amountDisplay: '-$58万', assetRatio: 0.05 } },
      { id: 'sys_007', client_uid: '33966966', client_name: '马军',   type: '大额提现', title: '提现 $427万，占资产 20%',      source: 'system', status: 'active',   created_at: '2026-04-03T14:05:00Z', meta: { amount: 4270000, amountDisplay: '$427万', assetRatio: 0.20 } },
      { id: 'sys_008', client_uid: '78608612', client_name: '林磊',   type: '大额充值', title: '充值 $4.2万，占资产 30%',      source: 'system', status: 'active',   created_at: '2026-04-03T14:50:00Z', meta: { amount: 42000,   amountDisplay: '$4.2万', assetRatio: 0.30 } },
      { id: 'sys_009', client_uid: '69849511', client_name: '杨丽',   type: '大额提现', title: '提现 $42万，占资产 30%',       source: 'system', status: 'active',   created_at: '2026-04-03T15:20:00Z', meta: { amount: 420000,  amountDisplay: '$42万',  assetRatio: 0.30 } },
      { id: 'sys_010', client_uid: '27129912', client_name: '罗建国', type: '大额充值', title: '充值 $477万，占资产 30%',      source: 'system', status: 'active',   created_at: '2026-04-03T16:00:00Z', meta: { amount: 4770000, amountDisplay: '$477万', assetRatio: 0.30 } },
    ]);
  }

  // ── 2. slaesh_flagged（特别关注）────────────────────────────────
  if (!tryGet('slaesh_flagged') || tryGet('slaesh_flagged').length === 0) {
    trySet('slaesh_flagged', [
      { fuId: 'sys_001', deadline: '2026-04-08' },
      { fuId: 'sys_003', deadline: '2026-04-10' },
      { fuId: 'sys_006', deadline: 'pending'    },
      { fuId: 'sys_005', deadline: '2026-04-15' },
    ]);
  }

  // ── 3. fu_records_* （每个事件的跟进记录）────────────────────────
  // sys_001：胡军·充值 $126万
  if (!tryGet('fu_records_sys_001') || tryGet('fu_records_sys_001').length === 0) {
    trySet('fu_records_sys_001', [
      { text: '【发放礼金】500U 现金  · 入金激励礼遇',                                                                  at: '2026-04-06T10:00:00Z' },
      { text: 'Telegram：客户表示近期会追加投入，等待市场回调时机。情绪积极，有意向升级 VIP，建议下周跟进 VIP 权益。', at: '2026-04-06T14:30:00Z' },
    ]);
  }

  // sys_003：李勇·提现 $109万
  if (!tryGet('fu_records_sys_003') || tryGet('fu_records_sys_003').length === 0) {
    trySet('fu_records_sys_003', [
      { text: '电话：客户资金需周转，非流失意向，预计两周后回款。已安抚，承诺回款后优先追加仓位。',                     at: '2026-04-03T16:00:00Z' },
      { text: '微信跟进：客户确认资金已到位，本周内会回充。已提醒近期入金优惠活动。',                                   at: '2026-04-05T11:00:00Z' },
    ]);
  }

  // sys_005：赵静·充值 $357万
  if (!tryGet('fu_records_sys_005') || tryGet('fu_records_sys_005').length === 0) {
    trySet('fu_records_sys_005', [
      { text: '【发放礼金】1000U 现金  · 大额入金专属礼遇',                                                             at: '2026-04-03T12:00:00Z' },
      { text: 'Telegram：致谢入金，介绍 VIP5 专属权益，客户对云算力产品感兴趣，安排专项介绍。',                         at: '2026-04-04T09:30:00Z' },
    ]);
  }

  // sys_006：孙芳·大额亏损
  if (!tryGet('fu_records_sys_006') || tryGet('fu_records_sys_006').length === 0) {
    trySet('fu_records_sys_006', [
      { text: '微信：主动关怀，客户情绪低落，对市场行情表示不满。建议暂缓仓位，以稳健理财产品为主，客户表示考虑。',     at: '2026-04-04T15:00:00Z' },
    ]);
  }

})();
