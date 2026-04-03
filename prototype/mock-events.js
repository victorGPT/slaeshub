// 系统事件模拟数据初始化
// 仅在 localStorage 中 follow_up_events 为空时注入，避免覆盖用户操作
(function() {
  var KEY = 'follow_up_events';
  try {
    var existing = JSON.parse(localStorage.getItem(KEY) || '[]');
    if (existing.length > 0) return; // 已有数据，不覆盖
  } catch(e) {}

  // 10条系统发起事件，UID 挂钩现有客户
  var events = [
    {
      id: 'sys_001',
      client_uid: '52339391',
      client_name: '胡军',
      type: '大额充值',
      title: '充值 $126万，占资产 30%',
      source: 'system',
      status: 'active',
      created_at: '2026-04-03T09:15:00Z',
      meta: { amount: 1260000, amountDisplay: '$126万', assetRatio: 0.30 },
      activities: [{ type: '创建', occurred_at: '2026-04-03T09:15:00Z' }]
    },
    {
      id: 'sys_002',
      client_uid: '33978249',
      client_name: '何敏',
      type: '大额充值',
      title: '充值 $19万，占资产 30%',
      source: 'system',
      status: 'active',
      created_at: '2026-04-03T10:02:00Z',
      meta: { amount: 190000, amountDisplay: '$19万', assetRatio: 0.30 },
      activities: [{ type: '创建', occurred_at: '2026-04-03T10:02:00Z' }]
    },
    {
      id: 'sys_003',
      client_uid: '19528530',
      client_name: '李勇',
      type: '大额提现',
      title: '提现 $109万，占资产 20%',
      source: 'system',
      status: 'active',
      created_at: '2026-04-03T10:45:00Z',
      meta: { amount: 1090000, amountDisplay: '$109万', assetRatio: 0.20 },
      activities: [{ type: '创建', occurred_at: '2026-04-03T10:45:00Z' }]
    },
    {
      id: 'sys_004',
      client_uid: '10289289',
      client_name: '胡军',
      type: '大额盈利',
      title: '7日盈利 $23万，占资产 7%',
      source: 'system',
      status: 'active',
      created_at: '2026-04-03T11:00:00Z',
      meta: { amount: 230000, amountDisplay: '$23万', assetRatio: 0.07 },
      activities: [{ type: '创建', occurred_at: '2026-04-03T11:00:00Z' }]
    },
    {
      id: 'sys_005',
      client_uid: '82160068',
      client_name: '赵静',
      type: '大额充值',
      title: '充值 $357万，占资产 30%',
      source: 'system',
      status: 'active',
      created_at: '2026-04-03T11:30:00Z',
      meta: { amount: 3570000, amountDisplay: '$357万', assetRatio: 0.30 },
      activities: [{ type: '创建', occurred_at: '2026-04-03T11:30:00Z' }]
    },
    {
      id: 'sys_006',
      client_uid: '51373735',
      client_name: '孙芳',
      type: '大额亏损',
      title: '7日亏损 $58万，占资产 5%',
      source: 'system',
      status: 'active',
      created_at: '2026-04-03T13:10:00Z',
      meta: { amount: -580000, amountDisplay: '-$58万', assetRatio: 0.05 },
      activities: [{ type: '创建', occurred_at: '2026-04-03T13:10:00Z' }]
    },
    {
      id: 'sys_007',
      client_uid: '33966966',
      client_name: '马军',
      type: '大额提现',
      title: '提现 $427万，占资产 20%',
      source: 'system',
      status: 'active',
      created_at: '2026-04-03T14:05:00Z',
      meta: { amount: 4270000, amountDisplay: '$427万', assetRatio: 0.20 },
      activities: [{ type: '创建', occurred_at: '2026-04-03T14:05:00Z' }]
    },
    {
      id: 'sys_008',
      client_uid: '78608612',
      client_name: '林磊',
      type: '大额充值',
      title: '充值 $4.2万，占资产 30%',
      source: 'system',
      status: 'active',
      created_at: '2026-04-03T14:50:00Z',
      meta: { amount: 42000, amountDisplay: '$4.2万', assetRatio: 0.30 },
      activities: [{ type: '创建', occurred_at: '2026-04-03T14:50:00Z' }]
    },
    {
      id: 'sys_009',
      client_uid: '69849511',
      client_name: '杨丽',
      type: '大额提现',
      title: '提现 $42万，占资产 30%',
      source: 'system',
      status: 'active',
      created_at: '2026-04-03T15:20:00Z',
      meta: { amount: 420000, amountDisplay: '$42万', assetRatio: 0.30 },
      activities: [{ type: '创建', occurred_at: '2026-04-03T15:20:00Z' }]
    },
    {
      id: 'sys_010',
      client_uid: '27129912',
      client_name: '罗建国',
      type: '大额充值',
      title: '充值 $477万，占资产 30%',
      source: 'system',
      status: 'active',
      created_at: '2026-04-03T16:00:00Z',
      meta: { amount: 4770000, amountDisplay: '$477万', assetRatio: 0.30 },
      activities: [{ type: '创建', occurred_at: '2026-04-03T16:00:00Z' }]
    }
  ];

  try {
    localStorage.setItem(KEY, JSON.stringify(events));
  } catch(e) {}
})();
