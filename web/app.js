const farm = document.getElementById("farm");
const meta = document.getElementById("meta");
const overlay = document.getElementById("overlay");
const addBtn = document.getElementById("addBtn");
const cancelBtn = document.getElementById("cancelBtn");
const addForm = document.getElementById("addForm");
const urlInput = document.getElementById("urlInput");
const submitBtn = document.getElementById("submitBtn");
const formError = document.getElementById("formError");
const serviceOverlay = document.getElementById("serviceOverlay");
const serviceForm = document.getElementById("serviceForm");
const serviceTitle = document.getElementById("serviceTitle");
const serviceHint = document.getElementById("serviceHint");
const serviceName = document.getElementById("serviceName");
const serviceIp = document.getElementById("serviceIp");
const serviceNote = document.getElementById("serviceNote");
const startBat = document.getElementById("startBat");
const startArgs = document.getElementById("startArgs");
const pickStartBat = document.getElementById("pickStartBat");
const stopBat = document.getElementById("stopBat");
const stopArgs = document.getElementById("stopArgs");
const pickStopBat = document.getElementById("pickStopBat");
const serviceRunRow = document.getElementById("serviceRunRow");
const startBatBtn = document.getElementById("startBatBtn");
const stopBatBtn = document.getElementById("stopBatBtn");
const serviceRunHint = document.getElementById("serviceRunHint");
const serviceError = document.getElementById("serviceError");
const serviceCancelBtn = document.getElementById("serviceCancelBtn");
const serviceSubmitBtn = document.getElementById("serviceSubmitBtn");
const serviceDeleteBtn = document.getElementById("serviceDeleteBtn");
const fileOverlay = document.getElementById("fileOverlay");
const fileTitle = document.getElementById("fileTitle");
const fileCwd = document.getElementById("fileCwd");
const fileDrives = document.getElementById("fileDrives");
const fileList = document.getElementById("fileList");
const fileCancelBtn = document.getElementById("fileCancelBtn");
const agentOverlay = document.getElementById("agentOverlay");
const agentForm = document.getElementById("agentForm");
const agentHint = document.getElementById("agentHint");
const agentPortInput = document.getElementById("agentPortInput");
const agentUpdateBtn = document.getElementById("agentUpdateBtn");
const agentError = document.getElementById("agentError");
const agentCancelBtn = document.getElementById("agentCancelBtn");
const langZh = document.getElementById("langZh");
const langEn = document.getElementById("langEn");
const groupBtn = document.getElementById("groupBtn");
const groupOverlay = document.getElementById("groupOverlay");
const groupForm = document.getElementById("groupForm");
const groupNameInput = document.getElementById("groupNameInput");
const groupAddBtn = document.getElementById("groupAddBtn");
const groupTree = document.getElementById("groupTree");
const groupError = document.getElementById("groupError");
const groupCancelBtn = document.getElementById("groupCancelBtn");

const POLL_MS = 2000;
const LANG_KEY = "gpu-farm-lang";
const FARM_GROUP_COLLAPSE_KEY = "gpu-farm-group-collapsed";
const WRENCH_ICON = `
  <svg class="wrench-icon" viewBox="0 0 24 24" aria-hidden="true">
    <path fill="currentColor" d="M22.7 19.1 13.6 10a6.5 6.5 0 0 0-8.9-8.3L8.6 5.6 5.6 8.6 1.7 4.7A6.5 6.5 0 0 0 10 13.6l9.1 9.1c.4.4 1 .4 1.4 0l2.2-2.2c.4-.4.4-1 0-1.4Z"/>
  </svg>
`;

const I18N = {
  zh: {
    pageTitle: "PZ GPU FARM",
    addGpu: "ADD GPU",
    addNodeTitle: "加入 GPU 節點",
    addNodeHint: "輸入電腦上 DCGM Exporter 的 metrics 網址。",
    metricsUrl: "Metrics URL",
    cancel: "取消",
    add: "加入",
    adding: "加入中…",
    serviceName: "服務名稱",
    serviceNamePh: "例如 Ollama / vLLM",
    serviceIp: "服務 IP",
    note: "說明",
    notePh: "這台在跑什麼、給誰用",
    startFile: "啟動檔案",
    filePh: "這台電腦的 .bat / .cmd / .exe",
    choose: "選擇",
    startArgs: "啟動參數",
    startArgsPh: "選填，例如 --port 8188",
    stopFile: "終止檔案",
    stopArgs: "終止參數",
    stopArgsPh: "選填，例如 /f",
    start: "啟動",
    stop: "終止",
    runHint: "掉線可啟動；終止會在該電腦執行關閉檔案。",
    delete: "刪除",
    update: "更新",
    addService: "添加服務",
    editService: "修改服務",
    save: "儲存",
    saving: "儲存中…",
    serviceHint: "這個服務只會出現在這台電腦的儀表板。",
    addServiceHint: "這個服務只會出現在 {host} 的儀表板。",
    agentHintDefault: "設定這台 GPU 電腦的 exe-link Port。",
    editServiceHint: "修改 {host} 上的「{name}」。",
    runLocal: "啟動 / 終止會在這台 GPU Farm 服務電腦（{host}）執行 BAT。",
    runRemote: "啟動 / 終止會在 {host} 本機執行 BAT。",
    runOffline: "{host} 尚未啟動 exe-link。請在那台電腦執行 exe-link.exe。",
    agentLocal: "exe-link 本機",
    agentOnline: "exe-link 在線",
    agentOffline: "exe-link 未上線",
    agentPortTitle: "設定 exe-link Port（目前 {port}）",
    agentOfflineDetail: "請在該電腦執行 exe-link.exe",
    openUrl: "點擊開啟網址",
    editServiceAria: "修改服務",
    editOrDelete: "修改或刪除",
    remove: "移除",
    metaLine: "{n} 台 · 每 {sec} 秒更新",
    emptyTitle: "尚未加入任何 GPU 節點",
    emptyHint: "點右上角 ADD GPU，輸入例如 http://192.168.1.69:9400/metrics",
    fetchFail: "無法讀取儀表板資料",
    refreshFail: "更新失敗",
    pickFile: "選擇 BAT / EXE",
    pickFileOn: "選擇 {host} 上的 BAT / EXE",
    loading: "讀取中…",
    readDirFail: "無法讀取資料夾",
    emptyDir: "這個資料夾沒有 BAT 或 EXE",
    saveFail: "儲存失敗",
    needStartFile: "請先選擇啟動檔案",
    needStopFile: "請先選擇終止檔案",
    runFail: "執行失敗",
    ranAt: "已在 {where} 執行{verb}（PID {pid}）",
    localHost: "本機",
    targetHost: "目標電腦",
    agentHint: "設定 {host} 的 exe-link Port。",
    updateFail: "更新失敗",
    addFail: "加入失敗",
    deleteFail: "刪除失敗",
    pinFail: "PIN 失敗",
    removeFail: "移除失敗",
    groupBtn: "GROUP",
    groupTitle: "管理 Group",
    groupHint: "新增 Group 後可展開、拖拉調整層級或排序。可把 GPU 電腦拖進 Group。刪除 Group 後，裡面的項目會回到上一層。",
    groupName: "Group 名稱",
    groupNamePh: "例如 Studio / Rack",
    addGroup: "新增 Group",
    addingGroup: "新增中…",
    done: "完成",
    ungrouped: "未分組",
    groupEmpty: "尚未建立 Group。先在上方新增。",
    groupDrop: "拖到這裡",
  },
  en: {
    pageTitle: "PZ GPU FARM",
    addGpu: "ADD GPU",
    addNodeTitle: "Add GPU node",
    addNodeHint: "Enter the DCGM Exporter metrics URL on that PC.",
    metricsUrl: "Metrics URL",
    cancel: "Cancel",
    add: "Add",
    adding: "Adding…",
    serviceName: "Service name",
    serviceNamePh: "e.g. Ollama / vLLM",
    serviceIp: "Service IP",
    note: "Notes",
    notePh: "What this runs, and who uses it",
    startFile: "Start file",
    filePh: ".bat / .cmd / .exe on this PC",
    choose: "Browse",
    startArgs: "Start arguments",
    startArgsPh: "Optional, e.g. --port 8188",
    stopFile: "Stop file",
    stopArgs: "Stop arguments",
    stopArgsPh: "Optional, e.g. /f",
    start: "Start",
    stop: "Stop",
    runHint: "Start when offline; Stop runs the close file on that PC.",
    delete: "Delete",
    update: "Update",
    addService: "Add service",
    editService: "Edit service",
    save: "Save",
    saving: "Saving…",
    serviceHint: "This service only appears on this PC's dashboard.",
    addServiceHint: "This service only appears on the {host} dashboard.",
    agentHintDefault: "Set the exe-link port for this GPU PC.",
    editServiceHint: "Edit “{name}” on {host}.",
    runLocal: "Start / Stop will run on this GPU Farm host ({host}).",
    runRemote: "Start / Stop will run locally on {host}.",
    runOffline: "{host} has not started exe-link. Run exe-link.exe on that PC.",
    agentLocal: "exe-link local",
    agentOnline: "exe-link online",
    agentOffline: "exe-link offline",
    agentPortTitle: "Set exe-link port (currently {port})",
    agentOfflineDetail: "Run exe-link.exe on that PC",
    openUrl: "Open URL",
    editServiceAria: "Edit service",
    editOrDelete: "Edit or delete",
    remove: "Remove",
    metaLine: "{n} hosts · refresh every {sec}s",
    emptyTitle: "No GPU nodes yet",
    emptyHint: "Click ADD GPU and enter a URL such as http://192.168.1.69:9400/metrics",
    fetchFail: "Could not load dashboard data",
    refreshFail: "Refresh failed",
    pickFile: "Choose BAT / EXE",
    pickFileOn: "Choose BAT / EXE on {host}",
    loading: "Loading…",
    readDirFail: "Could not read folder",
    emptyDir: "No BAT or EXE in this folder",
    saveFail: "Save failed",
    needStartFile: "Choose a start file first",
    needStopFile: "Choose a stop file first",
    runFail: "Run failed",
    ranAt: "Ran {verb} on {where} (PID {pid})",
    localHost: "this host",
    targetHost: "the target PC",
    agentHint: "Set the exe-link port for {host}.",
    updateFail: "Update failed",
    addFail: "Add failed",
    deleteFail: "Delete failed",
    pinFail: "PIN failed",
    removeFail: "Remove failed",
    groupBtn: "GROUP",
    groupTitle: "Manage groups",
    groupHint: "Add a group, then expand and drag to nest or reorder. Drop GPU hosts into a group. Deleting a group moves its items up one level.",
    groupName: "Group name",
    groupNamePh: "e.g. Studio / Rack",
    addGroup: "Add group",
    addingGroup: "Adding…",
    done: "Done",
    ungrouped: "Ungrouped",
    groupEmpty: "No groups yet. Add one above.",
    groupDrop: "Drop here",
  },
};

let lang = localStorage.getItem(LANG_KEY) === "zh" ? "zh" : "en";
let timer = null;
let adding = false;
let savingService = false;
let runningBat = false;
let lastSnapshot = { nodes: [], groups: [] };
let serviceNodeId = "";
let editingServiceId = "";
let pickingBat = "";
let agentNodeId = "";
let savingAgentPort = false;
let renamingFarmGroup = false;
let collapsedFarmGroups = loadCollapsedFarmGroups();
let savingGroups = false;
let groupState = { groups: [], nodes: [] };
let expandedGroups = new Set();
let treeDrag = null;

function t(key, vars) {
  let text = (I18N[lang] && I18N[lang][key]) || I18N.zh[key] || key;
  if (vars) {
    for (const [name, value] of Object.entries(vars)) {
      text = text.replaceAll(`{${name}}`, String(value ?? ""));
    }
  }
  return text;
}

function applyStaticI18n() {
  document.documentElement.lang = lang === "en" ? "en" : "zh-Hant";
  document.title = t("pageTitle");
  document.querySelectorAll("[data-i18n]").forEach((el) => {
    el.textContent = t(el.getAttribute("data-i18n"));
  });
  document.querySelectorAll("[data-i18n-placeholder]").forEach((el) => {
    el.placeholder = t(el.getAttribute("data-i18n-placeholder"));
  });
  if (langZh) langZh.classList.toggle("active", lang === "zh");
  if (langEn) langEn.classList.toggle("active", lang === "en");
}

function refreshOpenModals() {
  if (!overlay.hidden) {
    submitBtn.textContent = adding ? t("adding") : t("add");
  }
  if (!serviceOverlay.hidden && serviceNodeId) {
    const node = findNode(serviceNodeId);
    if (node && editingServiceId) {
      const service = findService(serviceNodeId, editingServiceId);
      serviceTitle.textContent = t("editService");
      serviceHint.textContent = t("editServiceHint", { host: node.hostname, name: service?.name || "" });
      serviceRunHint.textContent = nodeAgentHint(node);
      if (!savingService) serviceSubmitBtn.textContent = t("save");
    } else if (node) {
      serviceTitle.textContent = t("addService");
      serviceHint.textContent = t("addServiceHint", { host: node.hostname });
      serviceRunHint.textContent = nodeAgentHint(node);
      if (!savingService) serviceSubmitBtn.textContent = t("add");
    }
  }
  if (!fileOverlay.hidden) {
    const node = findNode(serviceNodeId);
    fileTitle.textContent = node ? t("pickFileOn", { host: node.hostname }) : t("pickFile");
  }
  if (!agentOverlay.hidden && agentNodeId) {
    const node = findNode(agentNodeId);
    if (node) agentHint.textContent = t("agentHint", { host: node.hostname });
  }
  if (!groupOverlay.hidden) renderGroupTree();
}

function setLang(next) {
  lang = next === "en" ? "en" : "zh";
  localStorage.setItem(LANG_KEY, lang);
  applyStaticI18n();
  render(lastSnapshot);
  refreshOpenModals();
}

function clamp(value, min, max) {
  return Math.min(max, Math.max(min, value));
}

function fmtNumber(value, digits = 0) {
  if (value == null || Number.isNaN(Number(value))) return "--";
  return Number(value).toFixed(digits);
}

function mibToGb(mib) {
  return Number(mib || 0) / 1024;
}

function barClass(pct) {
  if (pct >= 90) return "hot";
  if (pct >= 70) return "warn";
  return "ok";
}

function barColor(kind) {
  if (kind === "hot") return "var(--bar-hot)";
  if (kind === "warn") return "var(--bar-warn)";
  return "var(--bar)";
}

function metricPct(value, max) {
  if (value == null || !max) return 0;
  return clamp((Number(value) / Number(max)) * 100, 0, 100);
}

function escapeHtml(value) {
  return String(value ?? "")
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;");
}

function findNode(nodeId) {
  return (lastSnapshot.nodes || []).find((node) => node.id === nodeId);
}

function findService(nodeId, serviceId) {
  const node = findNode(nodeId);
  return (node?.services || []).find((service) => service.id === serviceId);
}

function serviceHref(service) {
  const raw = String(service.ip || "").trim();
  if (!raw) return "";
  if (/^https?:\/\//i.test(raw)) return raw;
  return `http://${raw}`;
}

function nodeHost(node) {
  try {
    return new URL(node.url).hostname || "";
  } catch {
    return "";
  }
}

function nodeAgentHint(node) {
  if (!node) return t("runHint");
  if (node.agent_local) return t("runLocal", { host: node.hostname });
  if (node.agent_status === "online") return t("runRemote", { host: node.hostname });
  return t("runOffline", { host: node.hostname });
}

function renderAgentStatus(node) {
  const port = node.agent_port || 9091;
  const title = t("agentPortTitle", { port });
  if (node.agent_local) {
    return `<button class="status agent local" type="button" data-agent-port="${escapeHtml(node.id)}" title="${escapeHtml(title)}"><i class="dot"></i>${t("agentLocal")}</button>`;
  }
  if (node.agent_status === "online") {
    return `<button class="status agent ready" type="button" data-agent-port="${escapeHtml(node.id)}" title="${escapeHtml(title)}"><i class="dot"></i>${t("agentOnline")}</button>`;
  }
  const detail = node.agent_error || t("agentOfflineDetail");
  return `<button class="status agent offline" type="button" data-agent-port="${escapeHtml(node.id)}" title="${escapeHtml(detail)}"><i class="dot"></i>${t("agentOffline")}</button>`;
}

function metricCard(valueHtml, pct, label) {
  const kind = barClass(pct);
  return `
    <div class="metric">
      <div class="metric-value">${valueHtml}</div>
      <div class="bar">
        <i style="width:${pct.toFixed(1)}%;background:${barColor(kind)}"></i>
        <span>${Math.round(pct)}%</span>
      </div>
      <div class="metric-label">${label}</div>
    </div>
  `;
}

function renderGpu(gpu) {
  const util = Number(gpu.util ?? 0);
  const temp = Number(gpu.temp ?? 0);
  const power = Number(gpu.power ?? 0);
  const usedGb = mibToGb(gpu.mem_used_mib);
  const totalGb = mibToGb(gpu.mem_total_mib);
  const memPct = metricPct(gpu.mem_used_mib, gpu.mem_total_mib);
  const powerPct = metricPct(power, gpu.power_limit);
  const smPct = metricPct(gpu.sm_clock, gpu.max_sm_clock);
  return `
    <section class="gpu">
      <div class="gpu-head">
        <span class="gpu-index">GPU ${escapeHtml(gpu.index)}</span>
        <span class="gpu-model">${escapeHtml(gpu.model)}</span>
        <span class="gpu-uuid">${escapeHtml(gpu.uuid)}</span>
      </div>
      <div class="metrics">
        ${metricCard(`${fmtNumber(util, util % 1 ? 1 : 0)}%`, clamp(util, 0, 100), "GPU util")}
        ${metricCard(`${fmtNumber(temp, 0)}°C`, clamp(temp, 0, 100), "Temperature")}
        ${metricCard(`${fmtNumber(power, 1)}W`, powerPct, "Power")}
        ${metricCard(`${fmtNumber(usedGb, 1)}/${fmtNumber(totalGb, 1)}G`, memPct, "Memory")}
        ${metricCard(`${fmtNumber(gpu.sm_clock, 0)}MHz`, smPct, "SM clock")}
      </div>
    </section>
  `;
}

function renderServiceChip(service, node) {
  const pinned = (node.pinned_service_ids || []).includes(service.id);
  const online = service.status === "online";
  const href = serviceHref(service);
  const title = [service.note, service.ip, href ? t("openUrl") : ""].filter(Boolean).join("\n");
  return `
    <div class="service-bundle">
      <a
        class="service-chip ${online ? "online" : "offline"} ${pinned ? "pinned" : ""}"
        href="${escapeHtml(href)}"
        target="_blank"
        rel="noreferrer"
        title="${escapeHtml(title)}"
        data-node="${escapeHtml(node.id)}"
        data-service="${escapeHtml(service.id)}"
      >
        <i class="service-lamp"></i>
        <span class="service-name">${escapeHtml(service.name)}</span>
        <span class="pin-mark" data-pin-service="${escapeHtml(service.id)}" data-node="${escapeHtml(node.id)}">PIN</span>
      </a>
      <button
        class="wrench-btn"
        type="button"
        aria-label="${escapeHtml(t("editServiceAria"))}"
        title="${escapeHtml(t("editOrDelete"))}"
        data-edit-service="${escapeHtml(service.id)}"
        data-node="${escapeHtml(node.id)}"
      >${WRENCH_ICON}</button>
    </div>
  `;
}

function renderServiceRow(node) {
  const pinned = new Set(node.pinned_service_ids || []);
  const locale = lang === "en" ? "en" : "zh-Hant";
  const services = [...(node.services || [])].sort((a, b) => {
    const pa = pinned.has(a.id) ? 0 : 1;
    const pb = pinned.has(b.id) ? 0 : 1;
    if (pa !== pb) return pa - pb;
    return String(a.name).localeCompare(String(b.name), locale);
  });
  return `
    <div class="service-row">
      ${services.map((service) => renderServiceChip(service, node)).join("")}
      <button class="add-service-btn" type="button" data-add-service="${escapeHtml(node.id)}">${t("addService")}</button>
    </div>
  `;
}

function sortByOrder(items) {
  return [...items].sort((a, b) => {
    const sa = Number(a.sort) || 0;
    const sb = Number(b.sort) || 0;
    if (sa !== sb) return sa - sb;
    return String(a.name || a.hostname || "").localeCompare(String(b.name || b.hostname || ""), lang === "en" ? "en" : "zh-Hant");
  });
}

function childGroupsOf(parentId, groups) {
  return sortByOrder((groups || []).filter((group) => (group.parent_id || "") === (parentId || "")));
}

function childNodesOf(groupId, nodes) {
  return sortByOrder((nodes || []).filter((node) => (node.group_id || "") === (groupId || "")));
}

function descendantGroupIds(groupId, groups) {
  const ids = new Set();
  const walk = (parentId) => {
    for (const group of groups || []) {
      if ((group.parent_id || "") === parentId) {
        ids.add(group.id);
        walk(group.id);
      }
    }
  };
  walk(groupId);
  return ids;
}

function loadCollapsedFarmGroups() {
  try {
    const raw = JSON.parse(localStorage.getItem(FARM_GROUP_COLLAPSE_KEY) || "[]");
    return new Set(Array.isArray(raw) ? raw.map(String) : []);
  } catch {
    return new Set();
  }
}

function saveCollapsedFarmGroups() {
  localStorage.setItem(FARM_GROUP_COLLAPSE_KEY, JSON.stringify([...collapsedFarmGroups]));
}

function beginGroupRename(label) {
  if (!label || label.getAttribute("contenteditable") === "true") return;
  renamingFarmGroup = true;
  label.contentEditable = "true";
  label.spellcheck = false;
  label.focus();
  const selection = window.getSelection();
  const range = document.createRange();
  range.selectNodeContents(label);
  selection.removeAllRanges();
  selection.addRange(range);
}

async function commitGroupRename(label) {
  if (!label || label.getAttribute("contenteditable") !== "true") return;
  label.contentEditable = "false";
  renamingFarmGroup = false;
  const id = label.getAttribute("data-rename") || "";
  const name = label.textContent.trim();
  const snap = (lastSnapshot.groups || []).find((item) => item.id === id);
  const stateGroup = groupState.groups.find((item) => item.id === id);
  const original = snap?.name || stateGroup?.name || "";
  if (!id || !name || name === original) {
    label.textContent = original || name;
    return;
  }
  try {
    const response = await fetch(`/api/groups/${id}`, {
      method: "PUT",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name }),
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || t("saveFail"));
    const next = payload.group.name;
    if (snap) snap.name = next;
    if (stateGroup) stateGroup.name = next;
    label.textContent = next;
  } catch (error) {
    label.textContent = original;
    if (!groupOverlay.hidden) showGroupError(error.message || t("saveFail"));
    else meta.textContent = error.message || t("saveFail");
  }
}

function renderGroupSection(group, groups, nodes) {
  const nested = childGroupsOf(group.id, groups).map((child) => renderGroupSection(child, groups, nodes)).join("");
  const hosts = childNodesOf(group.id, nodes).map(renderNode).join("");
  const collapsed = collapsedFarmGroups.has(group.id);
  return `
    <section class="node-group ${collapsed ? "collapsed" : ""}" data-group="${escapeHtml(group.id)}">
      <h3 class="node-group-title">
        <button
          class="group-fold"
          type="button"
          data-fold-group="${escapeHtml(group.id)}"
          aria-expanded="${collapsed ? "false" : "true"}"
          aria-label="${collapsed ? "Expand" : "Collapse"}"
        >${collapsed ? "▸" : "▾"}</button>
        <span class="node-group-name" data-rename="${escapeHtml(group.id)}">${escapeHtml(group.name)}</span>
      </h3>
      <div class="node-group-body">
        ${nested}${hosts}
      </div>
    </section>
  `;
}

function renderGroupedFarm(groups, nodes) {
  const groupIds = new Set(groups.map((group) => group.id));
  const roots = childGroupsOf("", groups);
  const ungrouped = nodes.filter((node) => !node.group_id || !groupIds.has(node.group_id));
  return roots.map((group) => renderGroupSection(group, groups, nodes)).join("") + ungrouped.map(renderNode).join("");
}

function syncGroupStateFromSnapshot(snapshot) {
  const nodes = snapshot.nodes || [];
  groupState = {
    groups: (snapshot.groups || []).map((group) => ({
      id: group.id,
      name: group.name,
      parent_id: group.parent_id || "",
      sort: Number(group.sort) || 0,
    })),
    nodes: nodes.map((node) => ({
      id: node.id,
      hostname: node.hostname || node.url || node.id,
      group_id: node.group_id || "",
      sort: Number(node.sort) || 0,
    })),
  };
  if (!expandedGroups.size) {
    for (const group of groupState.groups) expandedGroups.add(group.id);
  }
}

function layoutPayload() {
  return {
    groups: groupState.groups.map((group) => ({
      id: group.id,
      parent_id: group.parent_id || "",
      sort: Number(group.sort) || 0,
    })),
    nodes: groupState.nodes.map((node) => ({
      id: node.id,
      group_id: node.group_id || "",
      sort: Number(node.sort) || 0,
    })),
  };
}

function reindexSiblings(kind, parentId) {
  const items = kind === "group" ? childGroupsOf(parentId, groupState.groups) : childNodesOf(parentId, groupState.nodes);
  items.forEach((item, index) => {
    item.sort = index;
  });
}

function clearTreeDropMarks() {
  groupTree.querySelectorAll(".drag-over-into, .drag-over-before, .drag-over-after").forEach((el) => {
    el.classList.remove("drag-over-into", "drag-over-before", "drag-over-after");
  });
}

function dropModeFor(row, clientY) {
  const rect = row.getBoundingClientRect();
  const ratio = (clientY - rect.top) / Math.max(rect.height, 1);
  if (row.dataset.kind === "group") {
    if (ratio < 0.28) return "before";
    if (ratio > 0.72) return "after";
    return "into";
  }
  if (row.dataset.kind === "ungrouped") return "into";
  return ratio < 0.5 ? "before" : "after";
}

function renderTreeBranch(parentId) {
  const groups = childGroupsOf(parentId, groupState.groups);
  const nodes = parentId ? childNodesOf(parentId, groupState.nodes) : [];
  if (!groups.length && !nodes.length) return "";
  return groups.map((group) => {
    const expanded = expandedGroups.has(group.id);
    const kids = renderTreeBranch(group.id);
    return `
      <div class="tree-row group" draggable="true" data-kind="group" data-id="${escapeHtml(group.id)}">
        <button class="tree-toggle" type="button" data-toggle="${escapeHtml(group.id)}" aria-expanded="${expanded}">${expanded ? "▾" : "▸"}</button>
        <span class="tree-grip" aria-hidden="true">⋮⋮</span>
        <span class="tree-label" data-rename="${escapeHtml(group.id)}">${escapeHtml(group.name)}</span>
        <button class="tree-del" type="button" data-del-group="${escapeHtml(group.id)}" title="${escapeHtml(t("delete"))}">✕</button>
      </div>
      <div class="tree-children" ${expanded ? "" : "hidden"}>${kids || `<div class="tree-empty">${t("groupDrop")}</div>`}</div>
    `;
  }).join("") + nodes.map((node) => `
    <div class="tree-row node" draggable="true" data-kind="node" data-id="${escapeHtml(node.id)}">
      <span class="tree-toggle spacer"></span>
      <span class="tree-grip" aria-hidden="true">⋮⋮</span>
      <span class="tree-label">${escapeHtml(node.hostname)}</span>
    </div>
  `).join("");
}

function renderGroupTree() {
  const roots = renderTreeBranch("");
  const ungrouped = childNodesOf("", groupState.nodes);
  const empty = !groupState.groups.length
    ? `<div class="tree-empty">${t("groupEmpty")}</div>`
    : "";
  groupTree.innerHTML = `
    ${empty || roots}
    <div class="tree-row ungrouped" data-kind="ungrouped" data-id="">
      <span class="tree-toggle spacer"></span>
      <span class="tree-label">${t("ungrouped")}</span>
    </div>
    <div class="tree-children">${ungrouped.map((node) => `
      <div class="tree-row node" draggable="true" data-kind="node" data-id="${escapeHtml(node.id)}">
        <span class="tree-toggle spacer"></span>
        <span class="tree-grip" aria-hidden="true">⋮⋮</span>
        <span class="tree-label">${escapeHtml(node.hostname)}</span>
      </div>
    `).join("")}</div>
  `;
}

function showGroupError(message) {
  groupError.textContent = message || "";
  groupError.hidden = !message;
}

async function persistGroupLayout() {
  const response = await fetch("/api/groups/layout", {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(layoutPayload()),
  });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || t("saveFail"));
  if (lastSnapshot) {
    lastSnapshot.groups = payload.groups || groupState.groups;
    const byId = new Map((payload.nodes || []).map((node) => [node.id, node]));
    for (const node of lastSnapshot.nodes || []) {
      const next = byId.get(node.id);
      if (!next) continue;
      node.group_id = next.group_id || "";
      node.sort = Number(next.sort) || 0;
    }
  }
}

function moveTreeItem(kind, id, parentId, index) {
  if (kind === "group") {
    if (id === parentId || descendantGroupIds(id, groupState.groups).has(parentId)) return false;
    const item = groupState.groups.find((group) => group.id === id);
    if (!item) return false;
    const fromParent = item.parent_id || "";
    item.parent_id = parentId || "";
    const siblings = childGroupsOf(parentId, groupState.groups).filter((group) => group.id !== id);
    const at = Math.max(0, Math.min(index, siblings.length));
    siblings.splice(at, 0, item);
    siblings.forEach((group, sort) => {
      group.sort = sort;
    });
    if (fromParent !== (parentId || "")) reindexSiblings("group", fromParent);
    expandedGroups.add(parentId);
    return true;
  }
  const item = groupState.nodes.find((node) => node.id === id);
  if (!item) return false;
  const fromParent = item.group_id || "";
  item.group_id = parentId || "";
  const siblings = childNodesOf(parentId, groupState.nodes).filter((node) => node.id !== id);
  const at = Math.max(0, Math.min(index, siblings.length));
  siblings.splice(at, 0, item);
  siblings.forEach((node, sort) => {
    node.sort = sort;
  });
  if (fromParent !== (parentId || "")) reindexSiblings("node", fromParent);
  if (parentId) expandedGroups.add(parentId);
  return true;
}

function applyTreeDrop(target, mode) {
  if (!treeDrag || !target) return false;
  const kind = target.dataset.kind;
  const targetId = target.dataset.id || "";
  if (treeDrag.kind === kind && treeDrag.id === targetId) return false;
  if (kind === "ungrouped") {
    const count = treeDrag.kind === "group"
      ? childGroupsOf("", groupState.groups).length
      : childNodesOf("", groupState.nodes).length;
    return moveTreeItem(treeDrag.kind, treeDrag.id, "", count);
  }
  if (kind === "group") {
    const group = groupState.groups.find((item) => item.id === targetId);
    if (!group) return false;
    if (mode === "into") {
      const siblings = treeDrag.kind === "group" ? childGroupsOf(targetId, groupState.groups) : childNodesOf(targetId, groupState.nodes);
      return moveTreeItem(treeDrag.kind, treeDrag.id, targetId, siblings.length);
    }
    const parentId = group.parent_id || "";
    const siblings = childGroupsOf(parentId, groupState.groups);
    let index = siblings.findIndex((item) => item.id === targetId);
    if (index < 0) index = siblings.length;
    if (mode === "after") index += 1;
    if (treeDrag.kind === "node") {
      const nodes = childNodesOf(parentId, groupState.nodes);
      return moveTreeItem("node", treeDrag.id, parentId, mode === "before" ? 0 : nodes.length);
    }
    return moveTreeItem("group", treeDrag.id, parentId, index);
  }
  if (kind === "node") {
    const node = groupState.nodes.find((item) => item.id === targetId);
    if (!node) return false;
    const parentId = node.group_id || "";
    if (treeDrag.kind === "group") {
      return moveTreeItem("group", treeDrag.id, parentId, childGroupsOf(parentId, groupState.groups).length);
    }
    const siblings = childNodesOf(parentId, groupState.nodes);
    let index = siblings.findIndex((item) => item.id === targetId);
    if (index < 0) index = siblings.length;
    if (mode === "after") index += 1;
    return moveTreeItem("node", treeDrag.id, parentId, index);
  }
  return false;
}

async function openGroupModal() {
  showGroupError("");
  syncGroupStateFromSnapshot(lastSnapshot);
  renderGroupTree();
  groupAddBtn.disabled = false;
  groupAddBtn.textContent = t("addGroup");
  groupOverlay.hidden = false;
  groupOverlay.setAttribute("aria-hidden", "false");
  groupNameInput.value = "";
  groupNameInput.focus();
}

function closeGroupModal() {
  groupOverlay.hidden = true;
  groupOverlay.setAttribute("aria-hidden", "true");
  savingGroups = false;
  treeDrag = null;
  showGroupError("");
}

function renderNode(node) {
  const statusClass = node.status === "ready" ? "ready" : "offline";
  const statusText = node.status === "ready" ? "Ready" : "Offline";
  const driver = node.driver ? `Driver ${escapeHtml(node.driver)}` : "";
  const gpus = (node.gpus || []).map(renderGpu).join("");
  const error = node.error && node.status !== "ready"
    ? `<div class="error-line">${escapeHtml(node.error)}</div>`
    : "";
  return `
    <article class="node" data-id="${escapeHtml(node.id)}">
      <div class="node-head">
        <span class="host">${escapeHtml(node.hostname)}</span>
        <span class="exporter">${escapeHtml(node.exporter)}</span>
        <span class="status ${statusClass}"><i class="dot"></i>${statusText}</span>
        ${renderAgentStatus(node)}
        <a class="metrics-url" href="${escapeHtml(node.url)}" target="_blank" rel="noreferrer">${escapeHtml(node.url)}</a>
        <span class="driver">${driver}</span>
        <div class="node-actions">
          <button class="remove-btn" type="button" data-remove="${escapeHtml(node.id)}">${t("remove")}</button>
        </div>
      </div>
      ${gpus || error}
      ${renderServiceRow(node)}
    </article>
  `;
}

function render(snapshot) {
  lastSnapshot = snapshot;
  const nodes = snapshot.nodes || [];
  const groups = snapshot.groups || [];
  meta.textContent = nodes.length
    ? t("metaLine", { n: nodes.length, sec: POLL_MS / 1000 })
    : "";
  if (!nodes.length && !groups.length) {
    farm.innerHTML = `
      <div class="empty">
        <strong>${t("emptyTitle")}</strong>
        ${t("emptyHint")}
      </div>
    `;
    return;
  }
  farm.innerHTML = groups.length ? renderGroupedFarm(groups, nodes) : nodes.map(renderNode).join("");
}

async function fetchSnapshot() {
  const response = await fetch("/api/snapshot", { cache: "no-store" });
  if (!response.ok) throw new Error(t("fetchFail"));
  return response.json();
}

async function refresh() {
  try {
    const snapshot = await fetchSnapshot();
    if (!serviceOverlay.hidden || !overlay.hidden || !agentOverlay.hidden || !groupOverlay.hidden || renamingFarmGroup) {
      lastSnapshot = snapshot;
      return;
    }
    render(snapshot);
  } catch (error) {
    meta.textContent = error.message || t("refreshFail");
  }
}

function openModal() {
  formError.hidden = true;
  formError.textContent = "";
  overlay.hidden = false;
  overlay.setAttribute("aria-hidden", "false");
  urlInput.value = "";
  submitBtn.textContent = t("add");
  urlInput.focus();
}

function closeModal() {
  overlay.hidden = true;
  overlay.setAttribute("aria-hidden", "true");
  adding = false;
  submitBtn.disabled = false;
  submitBtn.textContent = t("add");
}

function resetServiceForm() {
  serviceError.hidden = true;
  serviceError.textContent = "";
  serviceRunHint.textContent = t("runHint");
  savingService = false;
  runningBat = false;
  serviceSubmitBtn.disabled = false;
  serviceDeleteBtn.disabled = false;
  updateRunButtons();
}

function servicePayload() {
  return {
    name: serviceName.value,
    ip: serviceIp.value,
    note: serviceNote.value,
    start_bat: startBat.value,
    stop_bat: stopBat.value,
    start_args: startArgs.value,
    stop_args: stopArgs.value,
  };
}

function updateRunButtons() {
  const editing = Boolean(editingServiceId);
  serviceRunRow.hidden = !editing;
  startBatBtn.disabled = runningBat || savingService || !startBat.value.trim();
  stopBatBtn.disabled = runningBat || savingService || !stopBat.value.trim();
}

function joinDir(cwd, name) {
  if (!cwd) return name;
  if (/^[A-Za-z]:\\?$/.test(cwd)) return `${cwd.replace(/\\$/, "")}\\${name}`;
  const sep = cwd.includes("\\") ? "\\" : "/";
  return `${cwd.replace(/[\\/]$/, "")}${sep}${name}`;
}

function initialBrowseDir(current) {
  const text = (current || "").trim().replaceAll('"', "");
  if (!text) return "";
  const slash = Math.max(text.lastIndexOf("\\"), text.lastIndexOf("/"));
  return slash > 0 ? text.slice(0, slash) : "";
}

async function openFilePicker(field) {
  pickingBat = field;
  const node = findNode(serviceNodeId);
  if (fileTitle) {
    fileTitle.textContent = node ? t("pickFileOn", { host: node.hostname }) : t("pickFile");
  }
  fileOverlay.hidden = false;
  fileOverlay.setAttribute("aria-hidden", "false");
  const current = field === "start" ? startBat.value : stopBat.value;
  await loadFileDir(initialBrowseDir(current));
}

function closeFilePicker() {
  fileOverlay.hidden = true;
  fileOverlay.setAttribute("aria-hidden", "true");
  pickingBat = "";
}

async function loadFileDir(dir) {
  fileList.textContent = t("loading");
  fileCwd.textContent = dir || "";
  try {
    const params = new URLSearchParams();
    if (dir) params.set("dir", dir);
    if (serviceNodeId) params.set("node_id", serviceNodeId);
    const response = await fetch(`/api/files?${params.toString()}`);
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || t("readDirFail"));
    fileCwd.textContent = payload.cwd || "";
    fileDrives.replaceChildren();
    for (const drive of payload.drives || []) {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "drive-btn";
      btn.textContent = drive;
      btn.addEventListener("click", () => {
        loadFileDir(drive);
      });
      fileDrives.append(btn);
    }
    fileList.replaceChildren();
    if (payload.parent) {
      const up = document.createElement("button");
      up.type = "button";
      up.className = "file-item dir";
      up.textContent = "..";
      up.addEventListener("click", () => {
        loadFileDir(payload.parent);
      });
      fileList.append(up);
    }
    for (const name of payload.dirs || []) {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "file-item dir";
      btn.textContent = `${name}\\`;
      btn.addEventListener("click", () => {
        loadFileDir(joinDir(payload.cwd, name));
      });
      fileList.append(btn);
    }
    for (const file of payload.files || []) {
      const btn = document.createElement("button");
      btn.type = "button";
      btn.className = "file-item";
      btn.textContent = file.name;
      btn.addEventListener("click", () => {
        if (pickingBat === "start") startBat.value = file.path;
        else stopBat.value = file.path;
        updateRunButtons();
        closeFilePicker();
      });
      fileList.append(btn);
    }
    if (!(payload.dirs || []).length && !(payload.files || []).length) {
      const empty = document.createElement("div");
      empty.className = "run-hint";
      empty.textContent = t("emptyDir");
      fileList.append(empty);
    }
  } catch (error) {
    fileList.textContent = error.message || t("readDirFail");
  }
}

async function saveService() {
  const response = await fetch(
    editingServiceId ? `/api/services/${editingServiceId}` : `/api/nodes/${serviceNodeId}/services`,
    {
      method: editingServiceId ? "PUT" : "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(servicePayload()),
    },
  );
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.error || t("saveFail"));
  if (payload.service?.id) editingServiceId = payload.service.id;
  return payload.service;
}

async function runServiceBat(action) {
  if (!editingServiceId || runningBat || savingService) return;
  const pathValue = action === "start" ? startBat.value.trim() : stopBat.value.trim();
  if (!pathValue) {
    serviceError.textContent = action === "start" ? t("needStartFile") : t("needStopFile");
    serviceError.hidden = false;
    return;
  }
  runningBat = true;
  serviceError.hidden = true;
  serviceSubmitBtn.disabled = true;
  serviceDeleteBtn.disabled = true;
  updateRunButtons();
  try {
    await saveService();
    const response = await fetch(`/api/services/${editingServiceId}/${action}`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: "{}",
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || t("runFail"));
    const verb = action === "start" ? t("start") : t("stop");
    const where = payload.hostname || (payload.scope === "local" ? t("localHost") : t("targetHost"));
    serviceRunHint.textContent = t("ranAt", { where, verb, pid: payload.pid });
    await refresh();
  } catch (error) {
    serviceError.textContent = error.message || t("runFail");
    serviceError.hidden = false;
  } finally {
    runningBat = false;
    serviceSubmitBtn.disabled = false;
    serviceDeleteBtn.disabled = false;
    serviceSubmitBtn.textContent = t("save");
    updateRunButtons();
  }
}

function openAddServiceModal(nodeId) {
  const node = findNode(nodeId);
  if (!node) return;
  serviceNodeId = nodeId;
  editingServiceId = "";
  resetServiceForm();
  serviceTitle.textContent = t("addService");
  serviceHint.textContent = t("addServiceHint", { host: node.hostname });
  serviceRunHint.textContent = nodeAgentHint(node);
  serviceSubmitBtn.textContent = t("add");
  serviceDeleteBtn.hidden = true;
  serviceName.value = "";
  serviceNote.value = "";
  startBat.value = "";
  startArgs.value = "";
  stopBat.value = "";
  stopArgs.value = "";
  const host = nodeHost(node);
  serviceIp.value = host ? `${host}:` : "";
  serviceIp.placeholder = host ? `${host}:11434` : "192.168.1.69:11434";
  updateRunButtons();
  serviceOverlay.hidden = false;
  serviceOverlay.setAttribute("aria-hidden", "false");
  serviceName.focus();
}

function openEditServiceModal(nodeId, serviceId) {
  const node = findNode(nodeId);
  const service = findService(nodeId, serviceId);
  if (!node || !service) return;
  serviceNodeId = nodeId;
  editingServiceId = serviceId;
  resetServiceForm();
  serviceTitle.textContent = t("editService");
  serviceHint.textContent = t("editServiceHint", { host: node.hostname, name: service.name });
  serviceRunHint.textContent = nodeAgentHint(node);
  serviceSubmitBtn.textContent = t("save");
  serviceDeleteBtn.hidden = false;
  serviceName.value = service.name || "";
  serviceIp.value = service.ip || "";
  serviceNote.value = service.note || "";
  startBat.value = service.start_bat || "";
  startArgs.value = service.start_args || "";
  stopBat.value = service.stop_bat || "";
  stopArgs.value = service.stop_args || "";
  updateRunButtons();
  serviceOverlay.hidden = false;
  serviceOverlay.setAttribute("aria-hidden", "false");
  serviceName.focus();
}

function closeServiceModal() {
  closeFilePicker();
  serviceOverlay.hidden = true;
  serviceOverlay.setAttribute("aria-hidden", "true");
  savingService = false;
  runningBat = false;
  serviceNodeId = "";
  editingServiceId = "";
  serviceSubmitBtn.disabled = false;
  serviceSubmitBtn.textContent = t("add");
  serviceDeleteBtn.hidden = true;
  serviceRunRow.hidden = true;
}

function openAgentModal(nodeId) {
  const node = findNode(nodeId);
  if (!node) return;
  agentNodeId = nodeId;
  savingAgentPort = false;
  agentError.hidden = true;
  agentError.textContent = "";
  agentHint.textContent = t("agentHint", { host: node.hostname });
  agentPortInput.value = String(node.agent_port || 9091);
  agentUpdateBtn.disabled = false;
  agentOverlay.hidden = false;
  agentOverlay.setAttribute("aria-hidden", "false");
  agentPortInput.focus();
  agentPortInput.select();
}

function closeAgentModal() {
  agentOverlay.hidden = true;
  agentOverlay.setAttribute("aria-hidden", "true");
  agentNodeId = "";
  savingAgentPort = false;
  agentUpdateBtn.disabled = false;
}

addBtn.addEventListener("click", openModal);
groupBtn.addEventListener("click", openGroupModal);
groupCancelBtn.addEventListener("click", closeGroupModal);
cancelBtn.addEventListener("click", closeModal);
serviceCancelBtn.addEventListener("click", closeServiceModal);
pickStartBat.addEventListener("click", () => openFilePicker("start"));
pickStopBat.addEventListener("click", () => openFilePicker("stop"));
startBatBtn.addEventListener("click", () => runServiceBat("start"));
stopBatBtn.addEventListener("click", () => runServiceBat("stop"));
startBat.addEventListener("input", updateRunButtons);
stopBat.addEventListener("input", updateRunButtons);
fileCancelBtn.addEventListener("click", closeFilePicker);
agentCancelBtn.addEventListener("click", closeAgentModal);
langZh.addEventListener("click", () => setLang("zh"));
langEn.addEventListener("click", () => setLang("en"));

overlay.addEventListener("click", (event) => {
  if (event.target === overlay) closeModal();
});
serviceOverlay.addEventListener("click", (event) => {
  if (event.target === serviceOverlay) closeServiceModal();
});
fileOverlay.addEventListener("click", (event) => {
  if (event.target === fileOverlay) closeFilePicker();
});
agentOverlay.addEventListener("click", (event) => {
  if (event.target === agentOverlay) closeAgentModal();
});
groupOverlay.addEventListener("click", (event) => {
  if (event.target === groupOverlay) closeGroupModal();
});
document.addEventListener("keydown", (event) => {
  if (event.key !== "Escape") return;
  if (!fileOverlay.hidden) closeFilePicker();
  else if (!agentOverlay.hidden) closeAgentModal();
  else if (!groupOverlay.hidden) closeGroupModal();
  else if (!serviceOverlay.hidden) closeServiceModal();
  else if (!overlay.hidden) closeModal();
});

agentForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (savingAgentPort || !agentNodeId) return;
  savingAgentPort = true;
  agentUpdateBtn.disabled = true;
  agentError.hidden = true;
  try {
    const response = await fetch(`/api/nodes/${agentNodeId}/agent`, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ port: agentPortInput.value }),
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || t("updateFail"));
    closeAgentModal();
    await refresh();
    if (payload.notice) meta.textContent = payload.notice;
  } catch (error) {
    agentError.textContent = error.message || t("updateFail");
    agentError.hidden = false;
    savingAgentPort = false;
    agentUpdateBtn.disabled = false;
  }
});

addForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (adding) return;
  adding = true;
  submitBtn.disabled = true;
  submitBtn.textContent = t("adding");
  formError.hidden = true;
  try {
    const response = await fetch("/api/nodes", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ url: urlInput.value }),
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || t("addFail"));
    closeModal();
    await refresh();
  } catch (error) {
    formError.textContent = error.message || t("addFail");
    formError.hidden = false;
    adding = false;
    submitBtn.disabled = false;
    submitBtn.textContent = t("add");
  }
});

serviceForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (savingService || runningBat || !serviceNodeId) return;
  savingService = true;
  serviceSubmitBtn.disabled = true;
  serviceSubmitBtn.textContent = editingServiceId ? t("saving") : t("adding");
  serviceError.hidden = true;
  try {
    await saveService();
    closeServiceModal();
    await refresh();
  } catch (error) {
    serviceError.textContent = error.message || t("saveFail");
    serviceError.hidden = false;
    savingService = false;
    serviceSubmitBtn.disabled = false;
    serviceSubmitBtn.textContent = editingServiceId ? t("save") : t("add");
  }
});

serviceDeleteBtn.addEventListener("click", async () => {
  if (!editingServiceId || savingService) return;
  savingService = true;
  serviceDeleteBtn.disabled = true;
  try {
    const response = await fetch(`/api/services/${editingServiceId}`, { method: "DELETE" });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || t("deleteFail"));
    closeServiceModal();
    await refresh();
  } catch (error) {
    serviceError.textContent = error.message || t("deleteFail");
    serviceError.hidden = false;
    savingService = false;
    serviceDeleteBtn.disabled = false;
  }
});

farm.addEventListener("dblclick", (event) => {
  const label = event.target.closest(".node-group-name[data-rename]");
  if (!label) return;
  event.preventDefault();
  beginGroupRename(label);
});

farm.addEventListener("keydown", (event) => {
  if (event.key !== "Enter") return;
  const label = event.target.closest?.(".node-group-name[data-rename]");
  if (!label || label.getAttribute("contenteditable") !== "true") return;
  event.preventDefault();
  label.blur();
});

farm.addEventListener("focusout", (event) => {
  const label = event.target.closest?.(".node-group-name[data-rename]");
  if (label) commitGroupRename(label);
});

farm.addEventListener("click", async (event) => {
  const foldGroup = event.target.closest("[data-fold-group]");
  if (foldGroup) {
    event.preventDefault();
    const id = foldGroup.getAttribute("data-fold-group") || "";
    if (!id) return;
    if (collapsedFarmGroups.has(id)) collapsedFarmGroups.delete(id);
    else collapsedFarmGroups.add(id);
    saveCollapsedFarmGroups();
    const section = foldGroup.closest(".node-group");
    const collapsed = collapsedFarmGroups.has(id);
    if (section) section.classList.toggle("collapsed", collapsed);
    foldGroup.setAttribute("aria-expanded", collapsed ? "false" : "true");
    foldGroup.textContent = collapsed ? "▸" : "▾";
    return;
  }

  const agentPortBtn = event.target.closest("[data-agent-port]");
  if (agentPortBtn) {
    event.preventDefault();
    openAgentModal(agentPortBtn.getAttribute("data-agent-port") || "");
    return;
  }

  const addService = event.target.closest("[data-add-service]");
  if (addService) {
    openAddServiceModal(addService.getAttribute("data-add-service") || "");
    return;
  }

  const editService = event.target.closest("[data-edit-service]");
  if (editService) {
    event.preventDefault();
    event.stopPropagation();
    openEditServiceModal(
      editService.getAttribute("data-node") || "",
      editService.getAttribute("data-edit-service") || "",
    );
    return;
  }

  const pinMark = event.target.closest("[data-pin-service]");
  if (pinMark) {
    event.preventDefault();
    event.stopPropagation();
    const serviceId = pinMark.getAttribute("data-pin-service");
    const nodeId = pinMark.getAttribute("data-node");
    if (!serviceId || !nodeId) return;
    pinMark.style.pointerEvents = "none";
    try {
      const response = await fetch(`/api/nodes/${nodeId}/pin`, {
        method: "POST",
        headers: { "Content-Type": "application/json" },
        body: JSON.stringify({ service_id: serviceId }),
      });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error || t("pinFail"));
      await refresh();
    } catch (error) {
      pinMark.style.pointerEvents = "";
      meta.textContent = error.message || t("pinFail");
    }
    return;
  }

  const removeNode = event.target.closest("[data-remove]");
  if (removeNode) {
    const id = removeNode.getAttribute("data-remove");
    if (!id) return;
    removeNode.disabled = true;
    try {
      const response = await fetch(`/api/nodes/${id}`, { method: "DELETE" });
      const payload = await response.json();
      if (!response.ok) throw new Error(payload.error || t("removeFail"));
      await refresh();
    } catch (error) {
      removeNode.disabled = false;
      meta.textContent = error.message || t("removeFail");
    }
    return;
  }
});

groupForm.addEventListener("submit", async (event) => {
  event.preventDefault();
  if (savingGroups) return;
  const name = groupNameInput.value.trim();
  if (!name) {
    showGroupError(t("groupNamePh"));
    groupNameInput.focus();
    return;
  }
  savingGroups = true;
  groupAddBtn.disabled = true;
  groupAddBtn.textContent = t("addingGroup");
  showGroupError("");
  try {
    const response = await fetch("/api/groups", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ name }),
    });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || t("addFail"));
    groupState.groups.push({
      id: payload.group.id,
      name: payload.group.name,
      parent_id: payload.group.parent_id || "",
      sort: Number(payload.group.sort) || 0,
    });
    expandedGroups.add(payload.group.id);
    if (lastSnapshot) {
      lastSnapshot.groups = [...(lastSnapshot.groups || []), payload.group];
    }
    groupNameInput.value = "";
    renderGroupTree();
  } catch (error) {
    showGroupError(error.message || t("addFail"));
  } finally {
    savingGroups = false;
    groupAddBtn.disabled = false;
    groupAddBtn.textContent = t("addGroup");
  }
});

groupTree.addEventListener("click", async (event) => {
  const toggle = event.target.closest("[data-toggle]");
  if (toggle) {
    const id = toggle.getAttribute("data-toggle");
    if (expandedGroups.has(id)) expandedGroups.delete(id);
    else expandedGroups.add(id);
    renderGroupTree();
    return;
  }
  const del = event.target.closest("[data-del-group]");
  if (!del || savingGroups) return;
  const id = del.getAttribute("data-del-group");
  savingGroups = true;
  showGroupError("");
  try {
    const response = await fetch(`/api/groups/${id}`, { method: "DELETE" });
    const payload = await response.json();
    if (!response.ok) throw new Error(payload.error || t("deleteFail"));
    const parentId = (groupState.groups.find((group) => group.id === id) || {}).parent_id || "";
    for (const group of groupState.groups) {
      if ((group.parent_id || "") === id) group.parent_id = parentId;
    }
    groupState.groups = groupState.groups.filter((group) => group.id !== id);
    for (const node of groupState.nodes) {
      if ((node.group_id || "") === id) node.group_id = parentId;
    }
    expandedGroups.delete(id);
    if (lastSnapshot) {
      lastSnapshot.groups = groupState.groups;
      for (const node of lastSnapshot.nodes || []) {
        if ((node.group_id || "") === id) node.group_id = parentId;
      }
    }
    renderGroupTree();
  } catch (error) {
    showGroupError(error.message || t("deleteFail"));
  } finally {
    savingGroups = false;
  }
});

groupTree.addEventListener("dblclick", (event) => {
  const label = event.target.closest("[data-rename]");
  if (!label) return;
  beginGroupRename(label);
});

groupTree.addEventListener("keydown", (event) => {
  if (event.key !== "Enter") return;
  const label = event.target.closest("[data-rename]");
  if (!label || label.getAttribute("contenteditable") !== "true") return;
  event.preventDefault();
  label.blur();
});

groupTree.addEventListener("focusout", (event) => {
  const label = event.target.closest("[data-rename]");
  if (label) commitGroupRename(label);
});

groupTree.addEventListener("dragstart", (event) => {
  const row = event.target.closest(".tree-row");
  if (!row || row.dataset.kind === "ungrouped") {
    event.preventDefault();
    return;
  }
  if (event.target.closest("[contenteditable='true']")) {
    event.preventDefault();
    return;
  }
  treeDrag = { kind: row.dataset.kind, id: row.dataset.id };
  row.classList.add("dragging");
  event.dataTransfer.effectAllowed = "move";
  event.dataTransfer.setData("text/plain", `${treeDrag.kind}:${treeDrag.id}`);
});

groupTree.addEventListener("dragend", () => {
  treeDrag = null;
  groupTree.querySelectorAll(".dragging").forEach((el) => el.classList.remove("dragging"));
  clearTreeDropMarks();
});

groupTree.addEventListener("dragover", (event) => {
  if (!treeDrag) return;
  const row = event.target.closest(".tree-row");
  if (!row) return;
  event.preventDefault();
  event.dataTransfer.dropEffect = "move";
  clearTreeDropMarks();
  const mode = dropModeFor(row, event.clientY);
  row.classList.add(mode === "into" ? "drag-over-into" : mode === "before" ? "drag-over-before" : "drag-over-after");
});

groupTree.addEventListener("drop", async (event) => {
  const row = event.target.closest(".tree-row");
  if (!row || !treeDrag) return;
  event.preventDefault();
  const mode = dropModeFor(row, event.clientY);
  const moved = applyTreeDrop(row, mode);
  treeDrag = null;
  clearTreeDropMarks();
  if (!moved) return;
  renderGroupTree();
  try {
    await persistGroupLayout();
  } catch (error) {
    showGroupError(error.message || t("saveFail"));
  }
});

applyStaticI18n();
refresh();
timer = setInterval(refresh, POLL_MS);
