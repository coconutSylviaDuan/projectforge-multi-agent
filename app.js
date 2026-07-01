const fields = {
  userRequest: document.querySelector("#userRequest"),
  industry: document.querySelector("#industry"),
  projectType: document.querySelector("#projectType"),
  techStack: document.querySelector("#techStack"),
  needsDatabase: document.querySelector("#needsDatabase"),
  needsExternalApi: document.querySelector("#needsExternalApi"),
  needsAuth: document.querySelector("#needsAuth"),
  constraints: document.querySelector("#constraints"),
  slug: document.querySelector("#slug"),
  revisionFeedback: document.querySelector("#revisionFeedback"),
};

const state = {
  plan: null,
  execution: null,
  projectContext: null,
  revisionHistory: [],
  activeTab: "requirement",
  isGenerating: false,
  isRevising: false,
  isExecuting: false,
  isLoadingProject: false,
};

const API_BASE =
  window.location.origin === "http://127.0.0.1:8770" || window.location.origin === "http://localhost:8770"
    ? ""
    : "http://127.0.0.1:8770";

const exampleRequest =
  "请帮我实现一个 AI 策略系统，包括 AI 多轮对话生成策略、策略回测、绩效分析。要求本地可演示，支持策略草稿、回测任务、绩效指标和回测报告。";

function collectRequest() {
  return {
    user_request: fields.userRequest.value.trim(),
    industry: fields.industry.value.trim(),
    project_type: fields.projectType.value.trim(),
    tech_stack: fields.techStack.value,
    needs_auth: fields.needsAuth.checked,
    needs_database: fields.needsDatabase.checked,
    needs_external_api: fields.needsExternalApi.checked,
    constraints: fields.constraints.value
      .split(",")
      .map((item) => item.trim())
      .filter(Boolean),
  };
}

async function runPlan() {
  const request = collectRequest();
  if (!request.user_request) {
    setContractView("请先输入项目需求。");
    return;
  }

  state.isGenerating = true;
  state.plan = null;
  state.execution = null;
  state.projectContext = null;
  state.revisionHistory = [];
  setStage("多 Agent 运行中");
  setBusy(true);
  selectTab(state.activeTab);

  try {
    const payload = await postJson("/api/plan", request);
    state.plan = payload;
    renderPlan("方案已生成");
  } catch (error) {
    setStage("运行失败");
    setContractView(`方案生成失败\n\n${error.message}`);
  } finally {
    state.isGenerating = false;
    setBusy(false);
  }
}

async function loadExistingProject() {
  const slug = getSlug();
  if (!slug) return;

  state.isLoadingProject = true;
  setStage("载入已有项目中");
  setBusy(true);
  setContractView(`正在读取 generated_projects/${slug}/contracts/plan.json 和相关代码...`);

  try {
    const payload = await postJson("/api/load-project", { slug });
    state.plan = payload.plan;
    state.projectContext = payload.context;
    state.execution = null;
    state.revisionHistory = [];
    document.querySelector("#generatedDir").textContent = payload.context.project_dir;
    renderPlan("已有项目已载入");
    selectTab("projectContext");
  } catch (error) {
    setStage("载入失败");
    setContractView(`载入已有项目失败\n\n${error.message}`);
  } finally {
    state.isLoadingProject = false;
    setBusy(false);
  }
}

async function revisePlan() {
  if (!state.plan) return;
  const feedback = fields.revisionFeedback.value.trim();
  if (!feedback) {
    setContractView("请先输入修改意见。");
    return;
  }

  const slug = fields.slug.value.trim();
  const useProjectRevision = Boolean(state.projectContext && slug);
  state.isRevising = true;
  state.execution = null;
  setStage(useProjectRevision ? "基于本地项目修订中" : "方案修订中");
  setBusy(true);
  selectTab("revision");

  try {
    const payload = useProjectRevision
      ? await postJson("/api/revise-project", { slug, feedback, history: state.revisionHistory })
      : await postJson("/api/revise", { plan: state.plan, feedback, history: state.revisionHistory });
    state.plan = payload.plan;
    if (payload.context) state.projectContext = payload.context;
    state.revisionHistory.push({ feedback, change_summary: payload.change_summary });
    fields.revisionFeedback.value = "";
    renderTraces(state.plan.traces);
    setStage("方案已修订");
    selectTab("revision");
  } catch (error) {
    setStage("修订失败");
    setContractView(`方案修订失败\n\n${error.message}`);
  } finally {
    state.isRevising = false;
    setBusy(false);
  }
}

async function scaffold() {
  if (!state.plan) return;
  const slug = getSlug();
  if (!slug) return;

  setStage("生成骨架中");
  setBusy(true);

  try {
    const payload = await postJson("/api/scaffold", { plan: state.plan, slug });
    document.querySelector("#generatedDir").textContent = payload.project_dir;
    setStage("骨架已生成");
    setContractView(JSON.stringify(payload, null, 2));
  } catch (error) {
    setStage("生成失败");
    setContractView(`项目骨架生成失败\n\n${error.message}`);
  } finally {
    setBusy(false);
  }
}

async function executeContracts() {
  if (!state.plan) return;
  const slug = getSlug();
  if (!slug) return;

  state.isExecuting = true;
  setStage("执行契约中");
  setBusy(true);
  selectTab("execution");

  try {
    const payload = await postJson("/api/execute", { plan: state.plan, slug, target: "all" });
    state.execution = payload;
    document.querySelector("#generatedDir").textContent = payload.project_dir;
    setStage("代码已生成");
    renderTraces(payload.traces);
    selectTab("execution");
  } catch (error) {
    setStage("执行失败");
    setContractView(`执行契约失败\n\n${error.message}`);
  } finally {
    state.isExecuting = false;
    setBusy(false);
  }
}

async function postJson(path, body) {
  const response = await fetch(`${API_BASE}${path}`, {
    method: "POST",
    headers: { "Content-Type": "application/json" },
    body: JSON.stringify(body),
  });
  const payload = await response.json();
  if (!response.ok) throw new Error(payload.detail || "请求失败");
  return payload;
}

function renderPlan(stageText) {
  document.querySelector("#projectName").textContent = state.plan.requirement_spec.project_name;
  setStage(stageText);
  renderTraces(state.plan.traces);
  selectTab("requirement");
}

function renderTraces(traces) {
  document.querySelector("#agentStrip").innerHTML = traces
    .map(
      (trace) => `
        <article class="agent-card">
          <strong>${escapeHtml(trace.agent)}</strong>
          <span>${escapeHtml(trace.summary)}</span>
        </article>
      `
    )
    .join("");
}

function selectTab(tab) {
  state.activeTab = tab;
  document.querySelectorAll(".tab").forEach((button) => {
    button.classList.toggle("active", button.dataset.tab === tab);
  });

  if (state.isGenerating) return setContractView(getGeneratingMessage(tab));
  if (state.isLoadingProject) return;
  if (state.isRevising) return setContractView(getRevisingMessage());
  if (state.isExecuting) return setContractView(getExecutingMessage());

  if (tab === "projectContext") {
    return setContractView(
      state.projectContext
        ? JSON.stringify(state.projectContext, null, 2)
        : "载入已有项目后，这里会显示读取到的契约文档和代码文件预览。"
    );
  }
  if (tab === "revision") {
    return setContractView(
      state.revisionHistory.length
        ? JSON.stringify(state.revisionHistory, null, 2)
        : "在左侧输入修改意见后点击“修改当前方案”，这里会显示每轮修改记录。"
    );
  }
  if (tab === "execution") {
    return setContractView(
      state.execution
        ? JSON.stringify(state.execution, null, 2)
        : "执行契约后会在这里显示生成文件、执行 Agent 结果和验证报告。"
    );
  }
  if (!state.plan) return setContractView("请输入需求后运行多 Agent，或先载入已有项目。");

  const mapping = {
    requirement: state.plan.requirement_spec,
    prd: state.plan.requirement_spec.prd_document,
    ui: state.plan.ui_spec,
    uiDesign: state.plan.ui_spec.ui_design_drafts,
    backend: state.plan.backend_spec,
    frontend: state.plan.frontend_spec,
    integration: state.plan.integration_spec,
  };
  setContractView(JSON.stringify(mapping[tab], null, 2));
}

function getGeneratingMessage(tab) {
  const labels = {
    requirement: "需求契约",
    prd: "PRD 文档",
    ui: "UI 契约",
    uiDesign: "UI 设计稿",
    backend: "后端/API 契约",
    frontend: "前端契约",
    integration: "集成契约",
    projectContext: "本地项目上下文",
    revision: "修改记录",
    execution: "执行结果",
  };
  return `${labels[tab] || "契约"}正在生成...\n\n结果返回前可以切换标签页，当前页面会保持生成中状态。`;
}

function getRevisingMessage() {
  return [
    "revision_agent 正在修订当前方案...",
    "",
    state.projectContext
      ? "它会读取本地契约文档、已生成代码预览、当前 plan 和你的修改意见。"
      : "它会读取当前完整 plan、你的修改意见和历史修改记录。",
    "修订完成后，PRD、UI 设计稿、API、前端和集成契约都会更新为新版。",
  ].join("\n");
}

function getExecutingMessage() {
  return [
    "执行契约生成代码中...",
    "",
    "LangGraph 正在调度 backend_executor_agent、frontend_executor_agent、intergration_executor_agent、verification_report_agent。",
    "执行完成后会写入 generated_projects 目录，并在这里展示结果。",
  ].join("\n");
}

function getSlug() {
  const slug = fields.slug.value.trim();
  if (!/^[a-z0-9][a-z0-9-]{1,60}$/.test(slug)) {
    setContractView("生成目录 Slug 只能使用小写字母、数字和短横线。");
    return "";
  }
  return slug;
}

function setBusy(isBusy) {
  document.querySelector("#runPlanBtn").disabled = isBusy;
  document.querySelector("#loadProjectBtn").disabled = isBusy;
  document.querySelector("#reviseBtn").disabled = isBusy || !state.plan;
  document.querySelector("#scaffoldBtn").disabled = isBusy || !state.plan;
  document.querySelector("#executeBtn").disabled = isBusy || !state.plan;
}

function setStage(text) {
  document.querySelector("#stageText").textContent = text;
}

function setContractView(text) {
  document.querySelector("#contractView").textContent = text;
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#039;");
}

document.querySelector("#loadExampleBtn").addEventListener("click", () => {
  fields.userRequest.value = exampleRequest;
  fields.industry.value = "证券金融";
  fields.projectType.value = "AI 策略系统";
  fields.slug.value = "jq-ai-strategy-system";
});
document.querySelector("#runPlanBtn").addEventListener("click", runPlan);
document.querySelector("#loadProjectBtn").addEventListener("click", loadExistingProject);
document.querySelector("#reviseBtn").addEventListener("click", revisePlan);
document.querySelector("#scaffoldBtn").addEventListener("click", scaffold);
document.querySelector("#executeBtn").addEventListener("click", executeContracts);
document.querySelectorAll(".tab").forEach((button) => {
  button.addEventListener("click", () => selectTab(button.dataset.tab));
});
