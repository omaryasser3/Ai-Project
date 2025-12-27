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
      // Extract detailed error information
      let errorMsg = `Error ${response.status}: `;

      if (data.detail) {
        // FastAPI returns errors in 'detail' field
        if (typeof data.detail === 'string') {
          errorMsg += data.detail;
        } else {
          errorMsg += JSON.stringify(data.detail);
        }
      } else if (data.error) {
        errorMsg += data.error;
      } else {
        errorMsg += response.statusText || "Request failed";
      }

      statusEl.textContent = errorMsg;
      statusEl.className = "form-text text-danger mt-2";
      return null;
    }

    statusEl.textContent = "Done.";
    statusEl.className = "form-text text-success mt-2";
    return data;
  } catch (err) {
    console.error("API Error:", err);
    statusEl.textContent = `Network error: ${err.message || "Unable to connect to server"}`;
    statusEl.className = "form-text text-danger mt-2";
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

function renderComprehensiveExplanation(comprehensiveExplanation) {
  const card = document.getElementById("comprehensive-explanation-card");
  const summaryEl = document.getElementById("explanation-summary");
  const confidenceScoreEl = document.getElementById("confidence-score");
  const confidenceBarEl = document.getElementById("confidence-bar");
  const detailedEl = document.getElementById("detailed-explanations");
  const risksContainer = document.getElementById("explanation-risks");
  const risksList = document.getElementById("risks-list");
  const notesEl = document.getElementById("transparency-notes");

  if (!comprehensiveExplanation) {
    card.classList.add("d-none");
    return;
  }

  // Show card
  card.classList.remove("d-none");

  // Render summary
  summaryEl.textContent = comprehensiveExplanation.summary || "No summary available.";

  // Render confidence score
  const confidence = comprehensiveExplanation.confidence_score || 0;
  confidenceScoreEl.textContent = `${confidence}%`;
  confidenceBarEl.style.width = `${confidence}%`;

  // Color code based on confidence
  if (confidence >= 80) {
    confidenceBarEl.className = "progress-bar bg-success";
  } else if (confidence >= 50) {
    confidenceBarEl.className = "progress-bar bg-warning";
  } else {
    confidenceBarEl.className = "progress-bar bg-danger";
  }

  // Render detailed explanations
  detailedEl.innerHTML = "";
  const details = comprehensiveExplanation.detailed_explanations || [];

  if (details.length > 0) {
    details.forEach((detail) => {
      const detailBlock = document.createElement("div");
      detailBlock.className = "mb-3 p-3 border rounded bg-dark bg-opacity-25";

      const title = document.createElement("div");
      title.className = "fw-bold mb-2 text-primary";
      title.textContent = `${detail.repair_number}. ${detail.title}`;

      const problemDiv = document.createElement("div");
      problemDiv.className = "small mb-1";
      problemDiv.innerHTML = `<strong>Problem:</strong> ${detail.problem}`;

      const causeDiv = document.createElement("div");
      causeDiv.className = "small mb-1";
      causeDiv.innerHTML = `<strong>Cause:</strong> ${detail.cause}`;

      const solutionDiv = document.createElement("div");
      solutionDiv.className = "small mb-1";
      solutionDiv.innerHTML = `<strong>Solution:</strong> ${detail.solution}`;

      const impactDiv = document.createElement("div");
      impactDiv.className = "small text-success";
      impactDiv.innerHTML = `<strong>Impact:</strong> ${detail.impact}`;

      detailBlock.appendChild(title);
      detailBlock.appendChild(problemDiv);
      detailBlock.appendChild(causeDiv);
      detailBlock.appendChild(solutionDiv);
      detailBlock.appendChild(impactDiv);

      detailedEl.appendChild(detailBlock);
    });
  } else {
    detailedEl.innerHTML = "<em class='text-muted'>No detailed explanations available.</em>";
  }

  // Render risks
  const risks = comprehensiveExplanation.risks || [];
  if (risks.length > 0 && risks[0] !== "None identified" && risks[0] !== "") {
    risksContainer.classList.remove("d-none");
    risksList.innerHTML = "";
    risks.forEach((risk) => {
      const li = document.createElement("li");
      li.textContent = risk;
      risksList.appendChild(li);
    });
  } else {
    risksContainer.classList.add("d-none");
  }

  // Render transparency notes
  const notes = comprehensiveExplanation.transparency_notes || "";
  if (notes) {
    notesEl.textContent = `Notes: ${notes}`;
  } else {
    notesEl.textContent = "";
  }
}

function renderTestValidation(testValidation) {
  const card = document.getElementById("test-validation-card");
  const summaryEl = document.getElementById("test-summary");
  const confidenceScoreEl = document.getElementById("test-confidence-score");
  const confidenceBarEl = document.getElementById("test-confidence-bar");
  const testCodeEl = document.getElementById("test-code");
  const testDescriptionsList = document.getElementById("test-descriptions-list");
  const testCoverageEl = document.getElementById("test-coverage");
  const testConcernsContainer = document.getElementById("test-concerns");
  const testConcernsList = document.getElementById("test-concerns-list");
  const testMissingContainer = document.getElementById("test-missing");
  const testMissingList = document.getElementById("test-missing-list");

  if (!testValidation || !testValidation.tests) {
    card.classList.add("d-none");
    return;
  }

  // Show card
  card.classList.remove("d-none");

  const validation = testValidation.validation || {};
  const tests = testValidation.tests || {};

  // Render validation summary
  summaryEl.textContent = validation.validation_summary || "No validation summary available.";

  // Render confidence score
  const confidence = validation.confidence_score || 0;
  confidenceScoreEl.textContent = `${confidence}%`;
  confidenceBarEl.style.width = `${confidence}%`;

  // Color code based on confidence
  if (confidence >= 80) {
    confidenceBarEl.className = "progress-bar bg-success";
    confidenceScoreEl.className = "badge bg-success";
  } else if (confidence >= 50) {
    confidenceBarEl.className = "progress-bar bg-warning";
    confidenceScoreEl.className = "badge bg-warning";
  } else {
    confidenceBarEl.className = "progress-bar bg-danger";
    confidenceScoreEl.className = "badge bg-danger";
  }

  // Render test code
  testCodeEl.textContent = tests.test_code || "// No tests generated";

  // Render test descriptions
  testDescriptionsList.innerHTML = "";
  const descriptions = tests.test_descriptions || [];
  if (descriptions.length > 0) {
    descriptions.forEach((desc) => {
      const li = document.createElement("li");
      li.className = "mb-2";
      li.innerHTML = `
        <strong>${desc.test_name || "Unnamed Test"}:</strong> ${marked.parse(desc.description || "")}
        ${desc.input ? `<br><span class="text-muted small">Input: ${desc.input}</span>` : ""}
        ${desc.expected ? `<br><span class="text-muted small">Expected: ${desc.expected}</span>` : ""}
      `;
      testDescriptionsList.appendChild(li);
    });
  } else {
    testDescriptionsList.innerHTML = "<li class='text-muted'>No test descriptions available</li>";
  }

  // Render test execution results
  const execution = testValidation.execution || {};
  const executionSummaryEl = document.getElementById("test-execution-summary");
  const executionListEl = document.getElementById("test-execution-list");
  const executionOutputEl = document.getElementById("test-execution-output");

  if (execution.execution_success !== undefined) {
    const summary = execution.summary || {};
    const total = summary.total || 0;
    const passed = summary.passed || 0;
    const failed = summary.failed || 0;
    const errors = summary.errors || 0;

    // Set summary with appropriate styling
    if (execution.execution_success) {
      executionSummaryEl.className = "alert alert-success mb-2 small";
      executionSummaryEl.innerHTML = `<strong>✅ All Tests Passed!</strong> ${passed}/${total} tests successful`;
    } else {
      executionSummaryEl.className = "alert alert-danger mb-2 small";
      executionSummaryEl.innerHTML = `<strong>❌ Some Tests Failed</strong> Passed: ${passed}, Failed: ${failed}, Errors: ${errors}`;
    }

    // Render individual test results
    executionListEl.innerHTML = "";
    const testResults = execution.test_results || [];
    testResults.forEach((test) => {
      const li = document.createElement("li");
      li.className = "mb-1";

      let icon, statusClass;
      if (test.status === "PASSED") {
        icon = "✅";
        statusClass = "text-success";
      } else if (test.status === "FAILED") {
        icon = "❌";
        statusClass = "text-danger";
      } else {
        icon = "⚠️";
        statusClass = "text-warning";
      }

      li.innerHTML = `${icon} <span class="${statusClass}">${test.name}</span> - ${test.status}`;
      if (test.message) {
        li.innerHTML += `<br><span class="text-muted ms-3">${test.message}</span>`;
      }
      executionListEl.appendChild(li);
    });

    // Show full output
    executionOutputEl.textContent = execution.output || "No output available";
  } else {
    executionSummaryEl.className = "alert alert-secondary mb-2 small";
    executionSummaryEl.innerHTML = "⏳ Tests not executed";
  }

  // Render coverage notes
  testCoverageEl.innerHTML = marked.parse(tests.coverage_notes || "No coverage notes");

  // Render concerns
  const concerns = validation.concerns || [];
  if (concerns.length > 0 && concerns[0] !== "None" && concerns[0] !== "") {
    testConcernsContainer.classList.remove("d-none");
    testConcernsList.innerHTML = "";
    concerns.forEach((concern) => {
      const li = document.createElement("li");
      li.innerHTML = marked.parse(concern);
      testConcernsList.appendChild(li);
    });
  } else {
    testConcernsContainer.classList.add("d-none");
  }

  // Render missing tests
  const missing = validation.missing_tests || [];
  if (missing.length > 0 && missing[0] !== "" && missing[0] !== "None") {
    testMissingContainer.classList.remove("d-none");
    testMissingList.innerHTML = "";
    missing.forEach((test) => {
      const li = document.createElement("li");
      li.innerHTML = marked.parse(test);
      testMissingList.appendChild(li);
    });
  } else {
    testMissingContainer.classList.add("d-none");
  }
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

  const planFeedbackInput = document.getElementById("plan-feedback");
  const proceedBtn = document.getElementById("proceed-btn");

  // Feedback Elements
  const feedbackCard = document.getElementById("feedback-card");
  const userFeedbackInput = document.getElementById("user-feedback");
  const acceptBtn = document.getElementById("accept-btn");
  const replanBtn = document.getElementById("replan-btn");
  const autofixBtn = document.getElementById("autofix-btn");

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

  // Helper to switch tabs
  function switchTab(tabId) {
    const tabEl = document.getElementById(tabId + '-tab');
    if (tabEl) {
      const tab = new bootstrap.Tab(tabEl);
      tab.show();
    }
  }

  analyzeBtn.addEventListener("click", async () => {
    const code = codeInput.value;
    const language = langInput.value || "";

    // Clear previous results
    document.getElementById("repaired-code").textContent = "";
    document.getElementById("repair-explanations").innerHTML = "";
    document.getElementById("plan-summary").textContent = "Analyzing...";
    document.getElementById("translated-code").textContent = "";
    document.getElementById("detected-language-display").classList.add("d-none");
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

      // Show detected language and update input field
      if (p.detected_language) {
        const detectedLangDisplay = document.getElementById("detected-language-display");
        const detectedLangName = document.getElementById("detected-language-name");
        detectedLangName.textContent = p.detected_language;
        detectedLangDisplay.classList.remove("d-none");

        // Update the language input to show detected language
        langInput.value = p.detected_language;
      }

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

      // Auto-switch to Plan tab
      switchTab('plan');
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
    const language = langInput.value || "";
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
      renderComprehensiveExplanation(data.comprehensive_explanation);  // Show ExplanationAgent results
      renderTestValidation(data.test_validation);  // Show TestGeneratorAgent results

      // Show feedback card
      showFeedbackCard(data.final_code);

      // Auto-switch to Repair tab to see the code first
      switchTab('repair');
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
    const language = langInput.value || "";
    const feedback = planFeedbackInput.value.trim();

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
      plan: overriddenPlan,
      user_feedback: feedback
    });

    if (data) {
      // Hide review card after starting? Or keep it?
      // Let's keep it visible so they see what they chose, but maybe disable input?
      // For now just render results.

      renderRepairs(data);
      renderPlanAndTranslation(data.plan, data.translation);
      renderComprehensiveExplanation(data.comprehensive_explanation);  // Show ExplanationAgent results
      renderTestValidation(data.test_validation);  // Show TestGeneratorAgent results
      showFeedbackCard(data.final_code);

      // Auto-switch to Repair tab to see the code first
      switchTab('repair');

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

  replanBtn.addEventListener("click", async () => {
    const feedback = userFeedbackInput.value.trim();
    if (!feedback) {
      alert("Please provide some feedback explanation.");
      return;
    }

    // Use the LAST REPAIRED CODE as input??
    // Or the original code?
    // "Iterate" usually means on the current state.
    // But if the repair was bad, we might want to start from scratch?
    // Usually, we iterate on the result.

    const code = lastRepairedCode || codeInput.value;
    const language = langInput.value || "Python"; // Or detect

    // UI Reset
    feedbackCard.classList.add("d-none");
    document.getElementById("status").textContent = "Re-planning with feedback...";

    // Call Analyze with feedback
    // Note: we need to put the new code in the input? Or just use it?
    // Let's update the input box to show what we are working on now.
    codeInput.value = code;

    // Trigger Analyze logic
    // We can just re-use the analyze call logic
    // Manually calling to ensure we pass feedback

    // Clear previous results
    document.getElementById("repaired-code").textContent = "";
    document.getElementById("repair-explanations").innerHTML = "";
    document.getElementById("plan-summary").textContent = "Re-Analyzing...";
    document.getElementById("translated-code").textContent = "";
    planReviewCard.classList.add("d-none");

    const data = await callApi("/api/analyze", {
      code,
      language,
      user_feedback: feedback
    });

    if (data) {
      currentAnalysis = data;
      renderIssues(data.issues || []);

      const p = data.plan || {};
      planTranslateCheck.checked = !!p.translate;
      planTargetLang.value = p.target_language || "";
      planDetectedLang.textContent = p.detected_language || "unknown";

      const stepsListEx = document.getElementById("execution-steps-list");
      stepsListEx.innerHTML = "";
      (data.execution_steps || []).forEach(step => {
        const li = document.createElement("li");
        li.className = "list-group-item bg-transparent";
        li.textContent = step.description;
        if (step.type) {
          const badge = document.createElement("span");
          badge.className = "badge bg-secondary ms-2 rounded-pill";
          badge.textContent = step.type;
          li.appendChild(badge);
        }
        stepsListEx.appendChild(li);
      });

      planReviewCard.classList.remove("d-none");
      renderPlanAndTranslation(data.plan, null);
      switchTab('plan');
    }
  });

  autofixBtn.addEventListener("click", async () => {
    const feedback = userFeedbackInput.value.trim();
    if (!feedback) {
      alert("Please provide some feedback explanation.");
      return;
    }

    const code = lastRepairedCode || codeInput.value;
    const language = langInput.value || "Python";

    feedbackCard.classList.add("d-none");
    codeInput.value = code; // Update input to show current state
    document.getElementById("status").textContent = "Auto-fixing with feedback...";

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
      switchTab('repair');
    }
  });
});
