const state = {
  jobId: null,
  job: null,
  units: [],
  pollTimer: null,
};

const submitButton = document.getElementById("submitButton");
const submitStatus = document.getElementById("submitStatus");
const errorMessage = document.getElementById("errorMessage");
const sourceDocx = document.getElementById("sourceDocx");
const reportPdf = document.getElementById("reportPdf");
const acknowledged = document.getElementById("acknowledged");
const jobSection = document.getElementById("jobSection");
const reviewSection = document.getElementById("reviewSection");
const searchInput = document.getElementById("searchInput");
const filterSelect = document.getElementById("filterSelect");

submitButton.addEventListener("click", handleCreateJob);
searchInput.addEventListener("input", renderUnits);
filterSelect.addEventListener("change", renderUnits);

async function handleCreateJob() {
  errorMessage.textContent = "";
  const docxFile = sourceDocx.files[0];
  const pdfFile = reportPdf.files[0];

  if (!docxFile || !pdfFile || !acknowledged.checked) {
    errorMessage.textContent = "Can chon du 2 file va xac nhan se review lai ket qua.";
    return;
  }

  submitButton.disabled = true;
  submitStatus.textContent = "Dang tao job...";

  try {
    const formData = new FormData();
    formData.append("source_docx", docxFile);
    formData.append("report_pdf", pdfFile);

    const response = await fetch("/jobs", {
      method: "POST",
      body: formData,
    });

    if (!response.ok) {
      throw new Error(await response.text());
    }

    const data = await response.json();
    state.jobId = data.job_id;
    jobSection.classList.remove("hidden");
    reviewSection.classList.remove("hidden");
    submitStatus.textContent = `Da tao job ${state.jobId.slice(0, 8)}.`;
    await refreshJob();
    startPolling();
  } catch (error) {
    errorMessage.textContent = error instanceof Error ? error.message : "Khong the tao job.";
  } finally {
    submitButton.disabled = false;
  }
}

function startPolling() {
  stopPolling();
  state.pollTimer = window.setInterval(refreshJob, 3000);
}

function stopPolling() {
  if (state.pollTimer) {
    window.clearInterval(state.pollTimer);
    state.pollTimer = null;
  }
}

async function refreshJob() {
  if (!state.jobId) return;

  const response = await fetch(`/jobs/${state.jobId}`, { cache: "no-store" });
  if (!response.ok) {
    throw new Error("Khong the tai thong tin job.");
  }
  state.job = await response.json();
  renderJob();
  await refreshUnits();

  if (["COMPLETED", "FAILED", "MANUAL_REVIEW"].includes(state.job.status)) {
    stopPolling();
  }
}

async function refreshUnits() {
  if (!state.jobId) return;
  const response = await fetch(`/jobs/${state.jobId}/units`, { cache: "no-store" });
  if (!response.ok) {
    return;
  }
  state.units = await response.json();
  renderUnits();
}

function renderJob() {
  const job = state.job;
  if (!job) return;

  document.getElementById("jobMeta").textContent = `Job ${job.job_id} | status ${job.status}`;
  document.getElementById("jobBadge").textContent = `${job.progress}%`;
  document.getElementById("progressBar").style.width = `${job.progress}%`;
  document.getElementById("totalUnits").textContent = job.total_units;
  document.getElementById("rewrittenUnits").textContent = job.rewritten_units;
  document.getElementById("manualUnits").textContent = job.manual_review_units;
  document.getElementById("providerFails").textContent = job.provider_fail_count;

  const timeline = document.getElementById("timeline");
  timeline.innerHTML = "";
  for (const item of job.timeline) {
    const li = document.createElement("li");
    li.textContent = item;
    timeline.appendChild(li);
  }

  const docxLink = document.getElementById("downloadDocx");
  const reportLink = document.getElementById("downloadReport");
  if (job.output_docx_path) {
    docxLink.href = `/jobs/${job.job_id}/download/docx`;
    docxLink.classList.remove("disabled");
  }
  if (job.change_report_path) {
    reportLink.href = `/jobs/${job.job_id}/download/report`;
    reportLink.classList.remove("disabled");
  }
}

function renderUnits() {
  const unitList = document.getElementById("unitList");
  unitList.innerHTML = "";

  const search = searchInput.value.trim().toLowerCase();
  const filter = filterSelect.value;

  const filtered = state.units.filter((unit) => {
    const text = `${unit.original_text} ${unit.rewritten_text || ""}`.toLowerCase();
    if (search && !text.includes(search)) {
      return false;
    }
    if (filter === "manual") {
      return unit.status === "MANUAL_REVIEW";
    }
    if (filter === "citation") {
      return Boolean(unit.citation_needed);
    }
    return true;
  });

  if (filtered.length === 0) {
    const empty = document.createElement("p");
    empty.className = "muted";
    empty.textContent = "Khong co doan nao khop voi bo loc hien tai.";
    unitList.appendChild(empty);
    return;
  }

  for (const unit of filtered) {
    const card = document.createElement("article");
    card.className = "unit-card";
    card.innerHTML = `
      <div class="unit-header">
        <span class="badge">${escapeHtml(unit.paragraph_ref)}</span>
        <span class="badge">${escapeHtml(unit.risk_type)}</span>
        <span class="badge">${escapeHtml(unit.provider_used || "pending")}</span>
        <span class="badge">confidence ${unit.confidence ?? "-"}</span>
        ${unit.citation_needed ? '<span class="badge">Can xem lai trich dan</span>' : ""}
      </div>
      <div class="unit-columns">
        <section class="unit-block">
          <h3>Original</h3>
          <p>${escapeHtml(unit.original_text)}</p>
        </section>
        <section class="unit-block">
          <h3>Rewritten</h3>
          <p>${escapeHtml(unit.rewritten_text || unit.failure_reason || "Chua co ket qua.")}</p>
        </section>
      </div>
      <section class="unit-block">
        <h3>Summary of changes</h3>
        <p>${escapeHtml(unit.summary_of_changes || "Can review thu cong.")}</p>
      </section>
    `;
    unitList.appendChild(card);
  }
}

function escapeHtml(value) {
  return String(value)
    .replaceAll("&", "&amp;")
    .replaceAll("<", "&lt;")
    .replaceAll(">", "&gt;")
    .replaceAll('"', "&quot;")
    .replaceAll("'", "&#39;");
}
