(function(root, factory) {
  var api = factory(root);
  if (typeof module !== 'undefined' && module.exports) {
    module.exports = api;
  }
  root.EventCenterShared = api;
})(typeof globalThis !== 'undefined' ? globalThis : this, function(root) {
  var FLAGGED_KEY = 'slaesh_flagged';
  var CLOSED_KEY = 'slaesh_closed';
  var EVENTS_KEY = 'follow_up_events';
  var FILTER_OPTIONS = ['全部', '主动联系', '客户反馈', '大额充值', '大额提现', '大额盈利', '大额亏损', '账户封禁', '其他'];
  function safeArray(value) {
    return Array.isArray(value) ? value : [];
  }

  function asString(value) {
    return value == null ? '' : String(value);
  }

  function timeMs(value) {
    var date = new Date(value || 0);
    return isNaN(date.getTime()) ? 0 : date.getTime();
  }

  function escapeHtml(value) {
    return asString(value)
      .replace(/&/g, '&amp;')
      .replace(/</g, '&lt;')
      .replace(/>/g, '&gt;')
      .replace(/"/g, '&quot;')
      .replace(/'/g, '&#39;');
  }

  function findCreatedAtFromActivities(event) {
    var activities = safeArray(event && event.activities);
    for (var index = 0; index < activities.length; index += 1) {
      if (activities[index] && activities[index].type === '创建' && activities[index].occurred_at) {
        return String(activities[index].occurred_at);
      }
    }
    return '';
  }

  function normalizeEvent(event) {
    var normalized = event || {};
    return {
      raw: normalized,
      id: asString(normalized.id),
      clientUid: asString(normalized.client_uid),
      clientName: asString(normalized.client_name),
      title: asString(normalized.title) || '—',
      type: asString(normalized.type),
      status: asString(normalized.status) || '跟进中',
      createdAt: asString(normalized.createdAt || normalized.created_at || findCreatedAtFromActivities(normalized)),
      activities: safeArray(normalized.activities)
    };
  }

  function getFlaggedBadgeMeta(flaggedEntries) {
    var count = safeArray(flaggedEntries).length;
    return {
      count: count,
      visible: count > 0,
      text: String(count)
    };
  }

  function upsertFlaggedEntry(flaggedEntries, fuId, flaggedAt) {
    var cleanId = asString(fuId);
    var next = safeArray(flaggedEntries).filter(function(entry) {
      return asString(entry && entry.fuId) !== cleanId;
    });
    next.push({
      fuId: cleanId,
      flaggedAt: asString(flaggedAt)
    });
    return next;
  }

  function removeFlaggedEntry(flaggedEntries, fuId) {
    var cleanId = asString(fuId);
    return safeArray(flaggedEntries).filter(function(entry) {
      return asString(entry && entry.fuId) !== cleanId;
    });
  }

  function closeEventIds(closedIds, fuId) {
    var cleanId = asString(fuId);
    var next = safeArray(closedIds).map(asString).filter(Boolean);
    if (next.indexOf(cleanId) === -1) {
      next.push(cleanId);
    }
    return next;
  }

  function reopenEventIds(closedIds, fuId) {
    var cleanId = asString(fuId);
    return safeArray(closedIds).map(asString).filter(function(id) {
      return id && id !== cleanId;
    });
  }

  function toClosedSet(closedIds) {
    return new Set(safeArray(closedIds).map(asString).filter(Boolean));
  }

  function toFlaggedMap(flaggedEntries) {
    var map = new Map();
    safeArray(flaggedEntries).forEach(function(entry) {
      var cleanId = asString(entry && entry.fuId);
      if (!cleanId) return;
      map.set(cleanId, {
        fuId: cleanId,
        flaggedAt: asString(entry && entry.flaggedAt)
      });
    });
    return map;
  }

  function buildDerivedItem(event, flaggedMap, closedSet) {
    var entry = flaggedMap.get(event.id) || null;
    return {
      id: event.id,
      clientUid: event.clientUid,
      clientName: event.clientName,
      title: event.title,
      type: event.type,
      status: event.status,
      createdAt: event.createdAt,
      createdAtMs: timeMs(event.createdAt),
      isFlagged: !!entry,
      isClosed: closedSet.has(event.id) || event.status === '已结束',
      flaggedAt: entry ? entry.flaggedAt : ''
    };
  }

  function sortByCreatedDesc(left, right) {
    return right.createdAtMs - left.createdAtMs;
  }

  function sortFlaggedItems(a, b) {
    return b.createdAtMs - a.createdAtMs;
  }

  function computeFlaggedView(events, flaggedEntries, closedIds) {
    var normalizedEvents = safeArray(events).map(normalizeEvent);
    var eventMap = new Map();
    normalizedEvents.forEach(function(event) {
      if (event.id) eventMap.set(event.id, event);
    });
    var flaggedMap = toFlaggedMap(flaggedEntries);
    var closedSet = toClosedSet(closedIds);
    var items = Array.from(flaggedMap.keys())
      .map(function(fuId) { return eventMap.get(fuId); })
      .filter(Boolean)
      .map(function(event) { return buildDerivedItem(event, flaggedMap, closedSet); })
      .sort(sortFlaggedItems);

    return {
      items: items,
      flaggedCount: items.length,
      flaggedBadgeVisible: items.length > 0
    };
  }

  function computeAllView(events, flaggedEntries, closedIds, currentFilter) {
    var normalizedEvents = safeArray(events).map(normalizeEvent);
    var flaggedMap = toFlaggedMap(flaggedEntries);
    var closedSet = toClosedSet(closedIds);
    var filterValue = asString(currentFilter) || '全部';
    var items = normalizedEvents
      .map(function(event) { return buildDerivedItem(event, flaggedMap, closedSet); })
      .filter(function(item) {
        return filterValue === '全部' ? true : item.type === filterValue;
      })
      .sort(sortByCreatedDesc);
    var badge = getFlaggedBadgeMeta(flaggedEntries);

    return {
      items: items,
      flaggedCount: badge.count,
      flaggedBadgeVisible: badge.visible,
      filter: filterValue
    };
  }

  function safeReadJson(storage, key, fallback) {
    try {
      var raw = storage.getItem(key);
      if (!raw) return fallback;
      var parsed = JSON.parse(raw);
      return Array.isArray(parsed) ? parsed : fallback;
    } catch (error) {
      return fallback;
    }
  }

  function safeWriteJson(storage, key, value) {
    storage.setItem(key, JSON.stringify(value));
  }

  function loadFlagged(storage) {
    return safeReadJson(storage, FLAGGED_KEY, []);
  }

  function saveFlagged(storage, flaggedEntries) {
    safeWriteJson(storage, FLAGGED_KEY, safeArray(flaggedEntries));
  }

  function loadClosed(storage) {
    return safeReadJson(storage, CLOSED_KEY, []);
  }

  function saveClosed(storage, closedIds) {
    safeWriteJson(storage, CLOSED_KEY, safeArray(closedIds).map(asString).filter(Boolean));
  }

  function loadEvents(storage) {
    return safeReadJson(storage, EVENTS_KEY, []);
  }

  function formatCreatedAt(isoString) {
    var date = new Date(isoString || 0);
    if (isNaN(date.getTime())) return '创建时间未知';
    var month = date.getMonth() + 1;
    var day = date.getDate();
    var hours = date.getHours();
    var minutes = date.getMinutes();
    var minuteText = minutes < 10 ? '0' + minutes : '' + minutes;
    return month + '月' + day + '日 ' + hours + ':' + minuteText;
  }

  function renderFilterPills(currentFilter) {
    return '<div class="event-filter-shell event-filter-fade"><div class="event-filter-scroll">'
      + FILTER_OPTIONS.map(function(option) {
        var active = option === currentFilter;
        return '<button type="button" class="event-filter-pill' + (active ? ' active' : '') + '" data-filter="' + escapeHtml(option) + '">' + escapeHtml(option) + '</button>';
      }).join('')
      + '</div></div>';
  }

  function renderEmbeddedTabs(currentTab, badge) {
    return '<div class="event-embedded-tabs">'
      + '<button type="button" class="event-embedded-tab' + (currentTab === 'flagged' ? ' active' : '') + '" data-tab="flagged">'
      + '<span>特别关注</span>'
      + (badge.visible ? '<span class="event-tab-badge">●' + escapeHtml(badge.text) + '</span>' : '')
      + '</button>'
      + '<button type="button" class="event-embedded-tab' + (currentTab === 'all' ? ' active' : '') + '" data-tab="all">'
      + '<span>全部事件</span>'
      + '</button>'
      + '</div>';
  }

  function renderTypeBadge(type) {
    if (!type) return '';
    return '<span class="event-type-badge">' + escapeHtml(type) + '</span>';
  }

  function renderStarButton(item) {
    var iconClass = item.isFlagged ? 'fa-solid' : 'fa-regular';
    var color = item.isFlagged ? '#F0B90B' : '#474D57';
    return '<button type="button" class="event-star-btn" data-action="toggle-star" data-fu-id="' + escapeHtml(item.id) + '" aria-label="关注事件">'
      + '<i class="' + iconClass + ' fa-star" style="color:' + color + '"></i>'
      + '</button>';
  }

  function renderCard(item) {
    var _uid = item.clientUid || '';
    var _name = item.clientName || '';
    var clientLabel = escapeHtml(_uid + (_name ? ' · ' + _name : '') || '未命名客户');
    var timeLabel = escapeHtml(formatCreatedAt(item.createdAt));
    var titleColor = item.isClosed ? '#474D57' : '#EAECEF';
    var titleDecor = item.isClosed ? 'line-through' : 'none';

    // 行1：事件内容（主体）
    var line1 = '<div style="display:flex;align-items:center;gap:6px">'
      + '<a href="follow-up-thread.html?fuId=' + encodeURIComponent(item.id) + '" style="flex:1;font-size:14px;font-weight:500;color:' + titleColor + ';text-decoration:' + titleDecor + ';overflow:hidden;white-space:nowrap;text-overflow:ellipsis">' + escapeHtml(item.title) + '</a>'
      + '</div>';

    // 行2：类型 badge + 客户信息（弱化）+ 创建时间
    var line2 = '<div style="display:flex;align-items:center;gap:6px;margin-top:6px">'
      + (item.type ? '<span class="event-type-badge">' + escapeHtml(item.type) + '</span>' : '')
      + '<span style="flex:1;font-size:11px;color:#474D57;overflow:hidden;white-space:nowrap;text-overflow:ellipsis">' + clientLabel + '</span>'
      + '<span style="font-size:10px;color:#474D57;flex-shrink:0">' + timeLabel + '</span>'
      + '</div>';

    return '<div class="event-card' + (item.isClosed ? ' closed' : '') + '">'
      + line1 + line2
      + '</div>';
  }

  function renderFlaggedCard(item) {
    return renderCard(item);
  }

  function renderAllCard(item) {
    return renderCard(item);
  }

  function renderEmptyState(pageMode) {
    var icon = pageMode === 'star' || pageMode === 'flagged' ? 'fa-star' : 'fa-inbox';
    var title = pageMode === 'star' || pageMode === 'flagged' ? '暂无特别关注事件' : '暂无事件';
    var desc = pageMode === 'star' || pageMode === 'flagged'
      ? '在全部事件里点亮星标后会出现在这里'
      : '在客户详情中创建事件后会显示在这里';
    return '<div class="event-empty-state">'
      + '<i class="fa-solid ' + icon + ' event-empty-icon"></i>'
      + '<div class="event-empty-title">' + escapeHtml(title) + '</div>'
      + '<div class="event-empty-desc">' + escapeHtml(desc) + '</div>'
      + '</div>';
  }

  function mountEventCenter(config) {
    if (typeof document === 'undefined') return null;
    var storage = config && config.storage ? config.storage : root.localStorage;
    var pageMode = config && config.pageMode ? config.pageMode : 'all';
    var tabsEl = config && config.tabsId ? document.getElementById(config.tabsId) : null;
    var filtersEl = config && config.filtersId ? document.getElementById(config.filtersId) : null;
    var listEl = config && config.listId ? document.getElementById(config.listId) : null;
    var state = {
      currentTab: pageMode === 'embedded' ? 'flagged' : 'all',
      currentFilter: '全部'
    };

    function getSnapshot() {
      return {
        events: loadEvents(storage),
        flagged: loadFlagged(storage),
        closed: loadClosed(storage)
      };
    }

    function render() {
      if (!listEl) return;
      var snapshot = getSnapshot();
      var badge = getFlaggedBadgeMeta(snapshot.flagged);
      if (tabsEl) {
        tabsEl.innerHTML = pageMode === 'embedded' ? renderEmbeddedTabs(state.currentTab, badge) : '';
      }
      if (filtersEl) {
        var showFilters = pageMode === 'all' || (pageMode === 'embedded' && state.currentTab === 'all');
        filtersEl.innerHTML = showFilters ? renderFilterPills(state.currentFilter) : '';
        filtersEl.style.display = showFilters ? 'block' : 'none';
      }

      var view = (pageMode === 'star' || (pageMode === 'embedded' && state.currentTab === 'flagged'))
        ? computeFlaggedView(snapshot.events, snapshot.flagged, snapshot.closed)
        : computeAllView(snapshot.events, snapshot.flagged, snapshot.closed, state.currentFilter);

      if (!view.items.length) {
        listEl.innerHTML = renderEmptyState(pageMode === 'embedded' ? state.currentTab : pageMode);
        return;
      }

      listEl.innerHTML = '<div class="event-list-inner">'
        + view.items.map(function(item) {
          return pageMode === 'star' || (pageMode === 'embedded' && state.currentTab === 'flagged')
            ? renderFlaggedCard(item)
            : renderAllCard(item);
        }).join('')
        + '</div>';
    }

    function setFlagged(fuId) {
      var next = upsertFlaggedEntry(loadFlagged(storage), fuId, new Date().toISOString());
      saveFlagged(storage, next);
      render();
    }

    function unsetFlagged(fuId) {
      saveFlagged(storage, removeFlaggedEntry(loadFlagged(storage), fuId));
      render();
    }

    function closeEvent(fuId) {
      var next = closeEventIds(loadClosed(storage), fuId);
      saveClosed(storage, next);
      render();
    }

    if (tabsEl) {
      tabsEl.addEventListener('click', function(event) {
        var button = event.target.closest('[data-tab]');
        if (!button) return;
        state.currentTab = button.getAttribute('data-tab') || 'flagged';
        state.openChooserId = '';
        render();
      });
    }

    if (filtersEl) {
      filtersEl.addEventListener('click', function(event) {
        var button = event.target.closest('[data-filter]');
        if (!button) return;
        state.currentFilter = button.getAttribute('data-filter') || '全部';
        render();
      });
    }

    if (listEl) {
      listEl.addEventListener('click', function(event) {
        var actionEl = event.target.closest('[data-action]');
        if (!actionEl) return;
        var action = actionEl.getAttribute('data-action');
        var fuId = actionEl.getAttribute('data-fu-id') || '';
        if (!action || !fuId) return;
        event.preventDefault();
        event.stopPropagation();

        if (action === 'toggle-star') {
          var flaggedMap = toFlaggedMap(loadFlagged(storage));
          if (flaggedMap.has(fuId)) {
            unsetFlagged(fuId);
          } else {
            setFlagged(fuId);
          }
          return;
        }

        if (action === 'unflag-event') {
          unsetFlagged(fuId);
          return;
        }

        if (action === 'close-event') {
          closeEvent(fuId);
        }
      });
    }

    if (root && root.addEventListener) {
      root.addEventListener('storage', function(event) {
        if (!event || [EVENTS_KEY, FLAGGED_KEY, CLOSED_KEY].indexOf(event.key) === -1) return;
        render();
      });
    }

    render();
    return {
      render: render,
      closeEvent: closeEvent
    };
  }

  return {
    CLOSED_KEY: CLOSED_KEY,
    EVENTS_KEY: EVENTS_KEY,
    FILTER_OPTIONS: FILTER_OPTIONS,
    FLAGGED_KEY: FLAGGED_KEY,
    closeEventIds: closeEventIds,
    computeAllView: computeAllView,
    computeFlaggedView: computeFlaggedView,
    escapeHtml: escapeHtml,
    getFlaggedBadgeMeta: getFlaggedBadgeMeta,
    loadClosed: loadClosed,
    loadEvents: loadEvents,
    loadFlagged: loadFlagged,
    mountEventCenter: mountEventCenter,
    normalizeEvent: normalizeEvent,
    renderCard: renderCard,
    removeFlaggedEntry: removeFlaggedEntry,
    reopenEventIds: reopenEventIds,
    saveClosed: saveClosed,
    saveFlagged: saveFlagged,
    upsertFlaggedEntry: upsertFlaggedEntry
  };
});
