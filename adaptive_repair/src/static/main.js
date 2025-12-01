async function callApi(path, payload) {
  const statusEl = document.getElementById("status");
  statusEl.textContent = "Working...";

  try {
    const response = await fetch(path, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(payload),
    });

    const data = await response.json();

    if (!response.ok) {
      statusEl.textContent = data.error || "Request failed.";
      return null;
    }

    statusEl.textContent = "Done.";
    return data;
  } catch (err) {
    console.error(err);
    statusEl.textContent = "Error calling API. See console for details.";
    return null;
  }
}

function renderIssues(issues) {
  const listEl = document.getElementById("issues-list");
  const noIssuesEl = document.getElementById("no-issues");
  listEl.innerHTML = "";

  if (!issues || issues.length === 0) {
    noIssuesEl.classList.remove("d-none");
    return;
  }

  noIssuesEl.classList.add("d-none");

  issues.forEach((issue) => {
    const li = document.createElement("li");
    li.className = "list-group-item d-flex flex-column";

    const header = document.createElement("div");
    header.className = "d-flex justify-content-between align-items-center mb-1";

    const title = document.createElement("span");
    title.textContent = `#${issue.id} ${issue.location_hint || ""}`;

    const tag = document.createElement("span");
    tag.className = `issue-tag issue-tag-${issue.type}`;
    tag.textContent = issue.type;

    header.appendChild(title);
    header.appendChild(tag);

    const desc = document.createElement("div");
    desc.textContent = issue.description;

    li.appendChild(header);
    li.appendChild(desc);
    listEl.appendChild(li);
  });
}

function renderRepairs(data) {
  const repairedCodeEl = document.getElementById("repaired-code");
  const explanationsEl = document.getElementById("repair-explanations");

  repairedCodeEl.textContent = data.final_code || "";

  explanationsEl.innerHTML = "";
  if (!data.repairs || data.repairs.length === 0) {
    explanationsEl.textContent = "No repairs were applied.";
    return;
  }

  data.repairs.forEach((r) => {
    const block = document.createElement("div");
    block.className = "mb-3";

    const title = document.createElement("div");
    title.className = "fw-semibold";
    title.textContent = `Issue #${r.issue_id} (${r.type})`;

    const desc = document.createElement("div");
    desc.className = "text-muted";
    desc.textContent = r.description;

    const expl = document.createElement("div");
    expl.textContent = r.explanation;

    block.appendChild(title);
    block.appendChild(desc);
    block.appendChild(expl);

    explanationsEl.appendChild(block);
  });
}

function renderPlanAndTranslation(plan, translation) {
  const planSummaryEl = document.getElementById("plan-summary");
  const translatedCodeEl = document.getElementById("translated-code");

  if (!plan) {
    planSummaryEl.textContent = "No plan yet.";
  } else if (plan.translate && plan.target_language) {
    planSummaryEl.textContent = `Main agent decided to translate code to ${plan.target_language} before repair.`;
  } else {
    planSummaryEl.textContent = "Main agent decided to repair in the original language.";
  }

  if (!translation || !translation.used) {
    translatedCodeEl.textContent = "";
    return;
  }

  translatedCodeEl.textContent =
    translation.forward_translated_code || "[Translation not available]";
}

window.addEventListener("DOMContentLoaded", () => {
  const codeInput = document.getElementById("code-input");
  const langInput = document.getElementById("language-input");
  const analyzeBtn = document.getElementById("analyze-btn");
  const repairBtn = document.getElementById("repair-btn");

  analyzeBtn.addEventListener("click", async () => {
    const code = codeInput.value;
    const language = langInput.value || "Python";
    const data = await callApi("/api/analyze", { code, language });
    if (data) {
      renderIssues(data.issues || []);
      renderPlanAndTranslation(data.plan, null);
    }
  });

  repairBtn.addEventListener("click", async () => {
    const code = codeInput.value;
    const language = langInput.value || "Python";
    const data = await callApi("/api/repair", { code, language });
    if (data) {
      renderIssues(
        (data.repairs || []).map((r) => ({
          id: r.issue_id,
          type: r.type,
          description: r.description,
          location_hint: r.location_hint,
        }))
      );
      renderRepairs(data);
      renderPlanAndTranslation(data.plan, data.translation);
    }
  });
});


