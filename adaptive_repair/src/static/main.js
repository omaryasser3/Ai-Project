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
  } else {
    const detected = plan.detected_language || "unknown language";
    const matchText =
      plan.language_match === false
        ? `Declared language differs; detected ${detected}.`
        : `Detected language: ${detected}.`;
    const translateText =
      plan.translate && plan.target_language
        ? `Plan will translate to ${plan.target_language} before repair.`
        : "Plan will repair in the detected language.";
    planSummaryEl.textContent = `${matchText} ${translateText}`.trim();
  }

  if (!translation || !translation.used) {
    const finalLang =
      (translation && translation.final_language) ||
      (plan && plan.detected_language) ||
      "original language";
    translatedCodeEl.textContent = `Final code language: ${finalLang}`;
    return;
  }

  const forwardLang = translation.to_language || "target language";
  const forwardSnippet =
    translation.forward_translated_code || "[Translation not available]";
  const finalLang =
    translation.final_language ||
    forwardLang ||
    (plan && plan.detected_language) ||
    "original language";
  translatedCodeEl.textContent = `Forward translation (${forwardLang}):\n${forwardSnippet}\n\nFinal code language: ${finalLang}`;
}

window.addEventListener("DOMContentLoaded", () => {
  const codeInput = document.getElementById("code-input");
  const langInput = document.getElementById("language-input");
  const analyzeBtn = document.getElementById("analyze-btn");
  const repairBtn = document.getElementById("repair-btn");

  // Plan Review Elements
  const planReviewCard = document.getElementById("plan-review-card");
  const planTranslateCheck = document.getElementById("plan-translate-check");
  const planTargetLang = document.getElementById("plan-target-lang");
  const planDetectedLang = document.getElementById("plan-detected-lang");
  const proceedBtn = document.getElementById("proceed-btn");

  // Feedback Elements
  const feedbackCard = document.getElementById("feedback-card");
  const userFeedbackInput = document.getElementById("user-feedback");
  const acceptBtn = document.getElementById("accept-btn");
  const refuseGenerateBtn = document.getElementById("refuse-generate-btn");
  const refuseStopBtn = document.getElementById("refuse-stop-btn");

  // State to hold analysis results before repair
  let currentAnalysis = null;
  // State
  let lastRepairedCode = "";

  // Helper to show feedback card
  function showFeedbackCard(repairedCode) {
    if (!repairedCode) return;
    lastRepairedCode = repairedCode;
    feedbackCard.classList.remove("d-none");
    userFeedbackInput.value = ""; // Clear previous feedback
  }

  analyzeBtn.addEventListener("click", async () => {
    const code = codeInput.value;
    const language = langInput.value || "Python";

    // Clear previous results
    document.getElementById("repaired-code").textContent = "";
    document.getElementById("repair-explanations").innerHTML = "";
    document.getElementById("plan-summary").textContent = "Analyzing...";
    document.getElementById("translated-code").textContent = "";
    planReviewCard.classList.add("d-none");
    feedbackCard.classList.add("d-none"); // Hide feedback on new analysis

    const data = await callApi("/api/analyze", { code, language });
    if (data) {
      currentAnalysis = data;
      renderIssues(data.issues || []);

      // Populate Plan Review UI
      const p = data.plan || {};
      planTranslateCheck.checked = !!p.translate;
      planTargetLang.value = p.target_language || "";
      planDetectedLang.textContent = p.detected_language || "unknown";

      // Render Execution Steps
      const stepsListEx = document.getElementById("execution-steps-list");
      stepsListEx.innerHTML = "";
      (data.execution_steps || []).forEach(step => {
        const li = document.createElement("li");
        li.className = "list-group-item bg-transparent";
        li.textContent = step.description; // or `Step ${step.step}: ${step.description}` but list is numbered

        // Optional: Add type badge
        if (step.type) {
          const badge = document.createElement("span");
          badge.className = "badge bg-secondary ms-2 rounded-pill";
          badge.textContent = step.type;
          badge.style.fontSize = "0.7em";
          li.appendChild(badge);
        }
        stepsListEx.appendChild(li);
      });
      if (!data.execution_steps || data.execution_steps.length === 0) {
        const li = document.createElement("li");
        li.className = "list-group-item bg-transparent text-muted italic";
        li.textContent = "No steps planned (no issues found?).";
        stepsListEx.appendChild(li);
      }

      // Show Review Card
      planReviewCard.classList.remove("d-none");

      // Also show plan summary in bottom card just for info
      renderPlanAndTranslation(data.plan, null);
    }
  });

  // "Analyze & Repair" - Direct flow (legacy/shortcut)
  repairBtn.addEventListener("click", async () => {
    // We can also route this through the review flow if we want,
    // but the button implies one-click. We'll leave it as direct for now,
    // or we could just hide it if we want to force review.
    // Let's effectively simulate "Analyze" then "Proceed" automatically?
    // Or just keep the existing behavior which is "Trust the AI".
    // I'll keep existing behavior but clear the review card.
    feedbackCard.classList.add("d-none");
    planReviewCard.classList.add("d-none");

    const code = codeInput.value;
    const language = langInput.value || "Python";
    const data = await callApi("/api/repair", { code, language });
    if (data) {
      // ... same rendering ...
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

      // Show feedback card
      showFeedbackCard(data.final_code);
    }
  });

  // "Proceed" - The new flow
  proceedBtn.addEventListener("click", async () => {
    if (!currentAnalysis) {
      alert("Please analyze issues first.");
      return;
    }
    feedbackCard.classList.add("d-none");

    const code = codeInput.value;
    const language = langInput.value || "Python";

    // Construct overridden plan
    const overriddenPlan = {
      ...currentAnalysis.plan,
      translate: planTranslateCheck.checked,
      target_language: planTargetLang.value.trim() || null
    };

    // Call repair with plan override
    const data = await callApi("/api/repair", {
      code,
      language,
      issues: currentAnalysis.issues,
      plan: overriddenPlan
    });

    if (data) {
      // Hide review card after starting? Or keep it?
      // Let's keep it visible so they see what they chose, but maybe disable input?
      // For now just render results.

      renderRepairs(data);
      renderPlanAndTranslation(data.plan, data.translation);
      showFeedbackCard(data.final_code);

      // Note: The backend might return refined issues if it re-ran analysis,
      // but our current logic bypasses analysis if plan provided.
      // So issues should be same as we sent, or enriched with results.
    }
  });

  // Feedback Handlers

  acceptBtn.addEventListener("click", () => {
    // Just hide the card and say thanks?
    feedbackCard.classList.add("d-none");
    alert("Repair accepted!");
  });

  refuseGenerateBtn.addEventListener("click", async () => {
    const feedback = userFeedbackInput.value.trim();
    if (!feedback) {
      alert("Please provide some feedback explanation.");
      return;
    }

    const code = lastRepairedCode || codeInput.value;
    const language = langInput.value || "Python";

    feedbackCard.classList.add("d-none");
    codeInput.value = code; // Update input to show current state
    document.getElementById("status").textContent = "Regenerating with feedback...";

    const data = await callApi("/api/repair", {
      code,
      language,
      user_feedback: feedback
    });
    if (data) {
      renderIssues((data.repairs || []).map(r => ({
        id: r.issue_id,
        type: r.type,
        description: r.description,
        location_hint: r.location_hint
      })));
      renderRepairs(data);
      renderPlanAndTranslation(data.plan, data.translation);
      showFeedbackCard(data.final_code);
    }
  });

  refuseStopBtn.addEventListener("click", () => {
     feedbackCard.classList.add("d-none");
     planReviewCard.classList.add("d-none");
     document.getElementById("repaired-code").textContent = "";
     document.getElementById("repair-explanations").innerHTML = "";
     document.getElementById("status").textContent = "Process stopped.";
     document.getElementById("issues-list").innerHTML = "";
     document.getElementById("no-issues").classList.add("d-none");
     
     // Optionally clear input?
     // codeInput.value = "";
     alert("Process stopped. You can enter new code to start over.");
  });
});
