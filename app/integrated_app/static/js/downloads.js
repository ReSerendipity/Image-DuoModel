/* downloads.js — 「下载管理」页交互
 *
 * CSP 收紧（script-src 'self'）后不允许内联脚本，因此文案通过 data-i18n 属性
 * 以 JSON 传入，本文件启动时解析成 window.__I18N__（与家族仓约定一致）。
 *
 * 数据流：
 *   GET  /api/downloads/status    → 运行形态 / 环境就位 / 模型就位
 *   GET  /api/downloads/catalog   → 环境包分卷与模型文件清单
 *   GET  /api/downloads/progress  → 任务进度（1s 轮询）
 *   POST /api/downloads/start|cancel|uninstall → 重操作（回环 + CSRF 双校验）
 */
(function () {
  'use strict';

  var root = document.getElementById('dlRoot');
  if (!root) { return; }

  try {
    window.__I18N__ = JSON.parse(root.dataset.i18n || '{}');
  } catch (e) {
    window.__I18N__ = {};
  }
  var I18N = window.__I18N__ || {};
  function T(key, fallback) {
    var v = I18N[key];
    return (v === undefined || v === null || v === '') ? (fallback || key) : v;
  }

  // ---------------------------------------------------------------- 工具 ----
  var CSRF_HEADER = 'X-CSRF-Token';
  var csrfToken = null;

  function apiFetch(path, options) {
    var opts = options || {};
    opts.headers = opts.headers || {};
    if (csrfToken) { opts.headers[CSRF_HEADER] = csrfToken; }
    opts.credentials = 'same-origin';
    return fetch(path, opts).then(function (resp) {
      // CSRF 中间件在每个 GET 响应里下发（复用已有 cookie 值），这里顺手缓存
      var token = resp.headers.get(CSRF_HEADER);
      if (token) { csrfToken = token; }
      return resp.text().then(function (body) {
        var data = null;
        if (body) {
          try { data = JSON.parse(body); } catch (e) { data = null; }
        }
        if (!resp.ok) {
          var msg = (data && (data.detail || data.message)) || resp.status + ' ' + resp.statusText;
          var err = new Error(msg);
          err.status = resp.status;
          throw err;
        }
        return data;
      });
    });
  }

  function postJSON(path, payload) {
    return apiFetch(path, {
      method: 'POST',
      headers: { 'Content-Type': 'application/json' },
      body: JSON.stringify(payload)
    });
  }

  function fmtBytes(bytes) {
    var n = Number(bytes) || 0;
    if (n <= 0) { return '—'; }
    var units = ['B', 'KB', 'MB', 'GB', 'TB'];
    var i = 0;
    while (n >= 1024 && i < units.length - 1) { n = n / 1024; i += 1; }
    return (n >= 100 ? n.toFixed(0) : n.toFixed(1)) + ' ' + units[i];
  }

  function el(tag, cls, text) {
    var node = document.createElement(tag);
    if (cls) { node.className = cls; }
    if (text !== undefined && text !== null) { node.textContent = text; }
    return node;
  }

  function setChip(node, text, kind) {
    if (!node) { return; }
    node.textContent = text;
    node.className = 'dl-chip' + (kind ? ' ' + kind : '');
  }

  // ---------------------------------------------------------------- 状态 ----
  var state = {
    status: null,
    catalog: null,
    tasks: [],
    busies: {}
  };

  var els = {
    modeChip: document.getElementById('dlModeChip'),
    envChip: document.getElementById('dlEnvChip'),
    readyChip: document.getElementById('dlReadyChip'),
    runtimeState: document.getElementById('dlRuntimeState'),
    runtimeNote: document.getElementById('dlRuntimeNote'),
    runtimePath: document.getElementById('dlRuntimePath'),
    runtimeBar: document.getElementById('dlRuntimeBar'),
    runtimeInstall: document.getElementById('dlRuntimeInstall'),
    runtimeCancel: document.getElementById('dlRuntimeCancel'),
    runtimeUninstall: document.getElementById('dlRuntimeUninstall'),
    modelList: document.getElementById('dlModelList')
  };

  function taskOf(component) {
    for (var i = 0; i < state.tasks.length; i += 1) {
      if (state.tasks[i].component === component) { return state.tasks[i]; }
    }
    return null;
  }

  function isBusy(task) {
    return !!(task && !task.finished);
  }

  function modeLabel(mode) {
    if (mode === 'bootstrap') { return T('dl_mode_bootstrap', 'bootstrap'); }
    if (mode === 'full') { return T('dl_mode_full', 'full'); }
    return T('dl_mode_system', 'system');
  }

  // ------------------------------------------------------------ 环境卡片 ----
  function renderRuntime() {
    var status = state.status;
    if (!status) { return; }
    var rt = status.runtime || {};
    var task = taskOf('runtime');
    var busy = isBusy(task);

    var installed = !!rt.installed;
    var present = !!rt.present;
    var compatible = rt.compatible !== false;

    els.runtimeState.textContent = installed
      ? T('dl_state_installed', '已安装')
      : (present ? T('dl_state_guide', '未安装') : T('dl_state_missing', '缺失'));
    els.runtimeState.className = 'dl-tag' + (installed ? ' ok' : (present ? '' : ' err'));

    var lines = [];
    if (installed) {
      lines.push(T('dl_env_installed_line', '')
        .replace('{python}', rt.python_version || '—')
        .replace('{torch}', rt.torch_version || '—')
        .replace('{cuda}', rt.cuda || '—'));
      if (rt.installed_at) {
        lines.push(T('dl_env_installed_at', '').replace('{when}', rt.installed_at));
      }
      if (!compatible) {
        lines.push(T('dl_env_incompatible', '')
          .replace('{required}', rt.min_app_version || '—')
          .replace('{current}', status.app_version || '—'));
      }
    } else if (present) {
      lines.push(T('dl_env_bootstrap_line', ''));
    } else {
      lines.push(T('dl_env_missing_line', ''));
    }
    if (busy) {
      var pct = Math.round((task.ratio || 0) * 100);
      lines.push((task.message || T('dl_working', '')) + ' · ' + pct + '%');
      els.runtimeBar.style.width = pct + '%';
    } else if (task && task.finished) {
      if (task.stage === 'error') {
        lines.push(T('dl_error_prefix', '') + ' ' + (task.error || ''));
      } else if (task.stage === 'cancelled') {
        lines.push(T('dl_cancelled', ''));
      } else {
        lines.push(T('dl_restart_hint', ''));
      }
      els.runtimeBar.style.width = task.stage === 'done' ? '100%' : '0%';
    } else {
      els.runtimeBar.style.width = installed ? '100%' : '0%';
    }
    els.runtimeNote.textContent = lines.join('\n');
    els.runtimePath.textContent = rt.path || '';

    els.runtimeInstall.disabled = busy || !state.catalog || !state.catalog.runtime;
    els.runtimeInstall.textContent = installed ? T('dl_reinstall', '重新安装') : T('dl_install', '安装');
    els.runtimeCancel.disabled = !busy;
    els.runtimeUninstall.disabled = busy || !installed;
  }

  // ------------------------------------------------------------ 模型列表 ----
  var modelNodes = {};

  function renderModels() {
    var status = state.status;
    if (!status) { return; }
    var models = status.models || [];
    if (!models.length) {
      els.modelList.textContent = '';
      els.modelList.appendChild(el('p', 'dl-note', T('dl_no_models', '')));
      return;
    }
    if (els.modelList.firstElementChild && els.modelList.firstElementChild.tagName === 'P') {
      els.modelList.textContent = '';
    }

    models.forEach(function (m) {
      var key = m.name;
      var node = modelNodes[key];
      if (!node) {
        node = el('div', 'dl-model');
        node.dataset.name = key;

        var head = el('div', 'dl-card-head');
        head.appendChild(el('h3', '', m.display_name || key));
        var tag = el('span', 'dl-tag', '');
        tag.dataset.role = 'tag';
        head.appendChild(tag);
        node.appendChild(head);

        var meta = el('div', 'dl-meta');
        meta.dataset.role = 'meta';
        node.appendChild(meta);

        var note = el('p', 'dl-note');
        note.dataset.role = 'note';
        node.appendChild(note);

        var meter = el('div', 'dl-meter');
        var bar = el('div', 'dl-meter-bar');
        bar.dataset.role = 'bar';
        meter.appendChild(bar);
        node.appendChild(meter);

        var actions = el('div', 'dl-actions');
        var btnInstall = el('button', 'dl-btn primary', T('dl_download', '下载'));
        btnInstall.type = 'button';
        btnInstall.dataset.role = 'install';
        actions.appendChild(btnInstall);
        var btnCancel = el('button', 'dl-btn', T('dl_cancel', '取消'));
        btnCancel.type = 'button';
        btnCancel.dataset.role = 'cancel';
        actions.appendChild(btnCancel);
        var btnRemove = el('button', 'dl-btn danger', T('dl_uninstall', '卸载'));
        btnRemove.type = 'button';
        btnRemove.dataset.role = 'remove';
        actions.appendChild(btnRemove);
        node.appendChild(actions);

        els.modelList.appendChild(node);
        modelNodes[key] = node;
      }

      var task = taskOf('model:' + key);
      var busy = isBusy(task);
      var tagNode = node.querySelector('[data-role="tag"]');
      tagNode.textContent = m.present ? T('dl_state_present', '已就位') : T('dl_state_absent', '未就位');
      tagNode.className = 'dl-tag' + (m.present ? ' ok' : '');

      var metaNode = node.querySelector('[data-role="meta"]');
      metaNode.textContent = '';
      function addMeta(labelKey, value) {
        var span = el('span');
        span.appendChild(document.createTextNode(T(labelKey, '') + ' '));
        var b = el('b', '', value);
        span.appendChild(b);
        metaNode.appendChild(span);
      }
      addMeta('dl_meta_backend', m.backend || '—');
      addMeta('dl_meta_vram', (m.min_vram_gb ? m.min_vram_gb + ' GB' : '—'));
      addMeta('dl_meta_size', m.present ? fmtBytes(m.size_bytes) : fmtBytes(m.download_bytes));
      if (m.is_default) { addMeta('dl_meta_default', T('dl_yes', '是')); }

      var noteNode = node.querySelector('[data-role="note"]');
      var barNode = node.querySelector('[data-role="bar"]');
      if (busy) {
        noteNode.textContent = (task.message || T('dl_working', '')) + ' · ' + Math.round((task.ratio || 0) * 100) + '%';
        barNode.style.width = Math.round((task.ratio || 0) * 100) + '%';
      } else if (task && task.stage === 'error') {
        noteNode.textContent = T('dl_error_prefix', '') + ' ' + (task.error || '');
        barNode.style.width = '0%';
      } else if (task && task.stage === 'cancelled') {
        noteNode.textContent = T('dl_cancelled', '');
        barNode.style.width = '0%';
      } else if (m.present) {
        noteNode.textContent = T('dl_model_present_note', '');
        barNode.style.width = '100%';
      } else if (!m.downloadable) {
        noteNode.textContent = T('dl_model_no_source', '');
        barNode.style.width = '0%';
      } else {
        noteNode.textContent = T('dl_model_ready_note', '');
        barNode.style.width = '0%';
      }

      var btnI = node.querySelector('[data-role="install"]');
      var btnC = node.querySelector('[data-role="cancel"]');
      var btnR = node.querySelector('[data-role="remove"]');
      btnI.disabled = busy || m.present || !m.downloadable;
      btnC.disabled = !busy;
      btnR.disabled = busy || !m.present;
    });
  }

  function renderHeader() {
    var status = state.status;
    if (!status) { return; }
    var rt = status.runtime || {};
    setChip(els.modeChip, T('dl_mode_prefix', '') + modeLabel(status.mode), status.mode === 'full' ? 'ok' : 'warn');
    setChip(
      els.envChip,
      rt.installed ? T('dl_state_installed', '') : T('dl_state_guide', ''),
      rt.installed ? 'ok' : (rt.present ? 'warn' : 'err')
    );
    setChip(els.readyChip, T('dl_ready_prefix', '') + (status.ready ? T('dl_ready_yes', '') : T('dl_ready_no', '')), status.ready ? 'ok' : '');
  }

  function renderAll() {
    renderHeader();
    renderRuntime();
    renderModels();
  }

  // ---------------------------------------------------------------- 请求 ----
  function refreshStatus() {
    return apiFetch('/api/downloads/status').then(function (data) {
      state.status = data;
      renderAll();
      return data;
    });
  }

  function refreshCatalog() {
    return apiFetch('/api/downloads/catalog').then(function (data) {
      state.catalog = data;
      renderAll();
      return data;
    });
  }

  function refreshProgress() {
    return apiFetch('/api/downloads/progress').then(function (data) {
      var before = JSON.stringify(state.tasks);
      state.tasks = (data && data.tasks) || [];
      var changed = JSON.stringify(state.tasks) !== before;
      if (changed) { renderAll(); }
      // 任务刚结束时状态（是否已装/就位）会变，补拉一次权威状态
      for (var i = 0; i < state.tasks.length; i += 1) {
        var t = state.tasks[i];
        if (t.finished && !t._seen) {
          t._seen = true;
          refreshStatus().catch(function () {});
        }
      }
      return data;
    });
  }

  function flashError(err) {
    var msg = (err && err.message) ? err.message : String(err);
    window.alert(T('dl_action_failed', '') + '\n' + msg);
  }

  function startTask(kind, target) {
    return postJSON('/api/downloads/start', { kind: kind, target: target || '' })
      .then(function () {
        return Promise.all([refreshProgress(), refreshStatus()]);
      })
      .catch(flashError);
  }

  function cancelTask(kind, target) {
    return postJSON('/api/downloads/cancel', { kind: kind, target: target || '' })
      .then(refreshProgress)
      .catch(flashError);
  }

  function uninstall(kind, target) {
    if (!window.confirm(T('dl_confirm_uninstall', ''))) { return Promise.resolve(); }
    return postJSON('/api/downloads/uninstall', { kind: kind, target: target || '' })
      .then(function () { return Promise.all([refreshStatus(), refreshStatus()]); })
      .catch(flashError);
  }

  // ---------------------------------------------------------------- 绑定 ----
  els.runtimeInstall.addEventListener('click', function () { startTask('runtime', ''); });
  els.runtimeCancel.addEventListener('click', function () { cancelTask('runtime', ''); });
  els.runtimeUninstall.addEventListener('click', function () { uninstall('runtime', ''); });

  els.modelList.addEventListener('click', function (event) {
    var btn = event.target.closest ? event.target.closest('button[data-role]') : null;
    if (!btn) { return; }
    var card = btn.closest('.dl-model');
    if (!card) { return; }
    var name = card.dataset.name;
    var role = btn.dataset.role;
    if (role === 'install') { startTask('model', name); }
    if (role === 'cancel') { cancelTask('model', name); }
    if (role === 'remove') { uninstall('model', name); }
  });

  // ------------------------------------------------------------ 轮询 ----
  var timer = null;
  function tick() {
    if (document.hidden) { return; }
    refreshProgress().catch(function () {});
  }

  refreshStatus().catch(flashError);
  refreshCatalog().catch(function () {});
  timer = window.setInterval(tick, 1000);
  window.addEventListener('beforeunload', function () {
    if (timer) { window.clearInterval(timer); }
  });
})();
