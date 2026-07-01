const $ = (id) => document.getElementById(id);

let currentFile = null;
let currentViewUrl = null;
let currentFilename = null;
let systemReady = false;

async function api(path, options = {}) {
  const res = await fetch(path, options);
  const data = await res.json().catch(() => ({}));
  if (!res.ok) throw new Error(data.detail || data.message || res.statusText);
  return data;
}

function showAlert(message, type = "info") {
  const el = $("alert");
  el.textContent = message;
  el.className = `alert visible ${type}`;
}

function hideAlert() {
  $("alert").className = "alert";
}

function setLoading(on) {
  $("spinner").classList.toggle("visible", on);
  $("btnReport").disabled = on || !systemReady || !currentFile;
  $("btnProposal").disabled = on || !systemReady || !currentFile;
  $("btnSample").disabled = on || !systemReady;
}

function showPreview(url, title, filename) {
  currentViewUrl = url;
  currentFilename = filename;
  $("emptyPreview").hidden = true;
  const frame = $("previewFrame");
  frame.hidden = false;
  frame.src = url;
  $("previewTitle").textContent = title || "Document preview";
  $("btnPrint").disabled = false;
  $("btnDownload").disabled = false;
  $("btnOpenTab").disabled = false;
}

async function refreshStatus() {
  try {
    const data = await api("/api/status");

    const pill = $("statusPill");
    if (data.ready) {
      pill.textContent = "Ready to generate";
      pill.className = "status-pill ready";
    } else if (!data.api_key_set) {
      pill.textContent = "API key needed";
      pill.className = "status-pill not-ready";
      $("btnReport").disabled = !currentFile;
      $("btnProposal").disabled = !currentFile;
      $("btnSample").disabled = false;
      if ($("apiKeyHint")) {
        $("apiKeyHint").textContent = data.api_key_masked
          ? `Saved key: ${data.api_key_masked} — enter a new key to replace.`
          : "Add your Anthropic API key in Settings below to generate reports.";
      }
    } else if (!data.config_set) {
      pill.textContent = "Setup needed";
      pill.className = "status-pill not-ready";
      showAlert("One-time setup required. Ask your administrator to configure the app.", "error");
    }

    systemReady = data.ready;
    if (data.ready || data.api_key_set) {
      $("btnReport").disabled = !currentFile;
      $("btnProposal").disabled = !currentFile;
      $("btnSample").disabled = false;
    }

    if (data.colors?.teal) $("swatchTeal").style.background = data.colors.teal;
    if (data.colors?.bronze) $("swatchBronze").style.background = data.colors.bronze;

    renderDocList(data.documents || []);

    if (data.inbox_files?.length && !currentFile) {
      currentFile = data.inbox_files[0].name;
      $("fileSelected").textContent = `Ready: ${currentFile}`;
      $("fileSelected").classList.add("visible");
      $("btnReport").disabled = !systemReady;
      $("btnProposal").disabled = !systemReady;
    }
  } catch (e) {
    showAlert(`Cannot connect to app: ${e.message}`, "error");
  }
}

function renderDocList(docs) {
  const list = $("docList");
  if (!docs.length) {
    list.innerHTML = '<li><span class="doc-meta">No documents yet</span></li>';
    return;
  }
  list.innerHTML = docs
    .map((d) => {
      const label = d.is_preview
        ? "Brand & format preview"
        : d.name.replace(/\.html$/, "").replace(/-/g, " ");
      const icon = d.is_preview ? "🎨" : "📋";
      return `
    <li>
      <span class="doc-name" data-file="${d.name}" data-url="/view/${encodeURIComponent(d.name)}">
        ${icon} ${label}
      </span>
      <span class="doc-meta">${d.modified}</span>
    </li>`;
    })
    .join("");

  list.querySelectorAll(".doc-name").forEach((el) => {
    el.addEventListener("click", () => {
      showPreview(el.dataset.url, el.textContent.trim(), el.dataset.file);
    });
  });
}

async function uploadFile(file) {
  const form = new FormData();
  form.append("file", file);
  const res = await fetch("/api/upload", { method: "POST", body: form });
  const data = await res.json();
  if (!res.ok) throw new Error(data.detail || "Upload failed");
  currentFile = data.name;
  $("fileSelected").textContent = `Uploaded: ${data.name}`;
  $("fileSelected").classList.add("visible");
  $("btnReport").disabled = !systemReady;
  $("btnProposal").disabled = !systemReady;
  showAlert(data.message, "success");
  refreshStatus();
}

async function generate(docType, useSample = false) {
  hideAlert();
  setLoading(true);
  try {
    const body = { doc_type: docType, use_sample: useSample };
    if (currentFile && !useSample) body.source_name = currentFile;

    const data = await api("/api/generate", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body),
    });

    showAlert(data.message, "success");
    showPreview(data.view_url, data.message, data.filename);
    refreshStatus();
  } catch (e) {
    showAlert(e.message, "error");
  } finally {
    setLoading(false);
  }
}

async function loadDesignPreview() {
  hideAlert();
  setLoading(true);
  try {
    const data = await api("/api/preview/design", { method: "POST" });
    showPreview(data.view_url, "Brand & format preview", data.filename);
    showAlert("Format preview loaded — compare colors and section layout.", "info");
    refreshStatus();
  } catch (e) {
    showAlert(e.message, "error");
  } finally {
    setLoading(false);
  }
}

// Drop zone
const dropZone = $("dropZone");
const fileInput = $("fileInput");

dropZone.addEventListener("click", () => fileInput.click());
dropZone.addEventListener("dragover", (e) => {
  e.preventDefault();
  dropZone.classList.add("dragover");
});
dropZone.addEventListener("dragleave", () => dropZone.classList.remove("dragover"));
dropZone.addEventListener("drop", (e) => {
  e.preventDefault();
  dropZone.classList.remove("dragover");
  const file = e.dataTransfer.files[0];
  if (file) uploadFile(file).catch((err) => showAlert(err.message, "error"));
});
fileInput.addEventListener("change", () => {
  const file = fileInput.files[0];
  if (file) uploadFile(file).catch((err) => showAlert(err.message, "error"));
});

// Buttons
$("btnReport").addEventListener("click", () => generate("report"));
$("btnProposal").addEventListener("click", () => generate("proposal"));
$("btnSample").addEventListener("click", () => generate("report", true));
$("btnFormatPreview").addEventListener("click", loadDesignPreview);
$("btnReference").addEventListener("click", () => {
  showPreview("/reference", "Northgate reference report (format guide)", "Standard Review - 4600 Northgate.dc.html");
});

$("btnPrint").addEventListener("click", () => {
  const frame = $("previewFrame");
  if (frame.contentWindow) frame.contentWindow.print();
});

$("btnDownload").addEventListener("click", () => {
  if (currentFilename) window.location.href = `/download/${encodeURIComponent(currentFilename)}`;
});

$("btnOpenTab").addEventListener("click", () => {
  if (currentViewUrl) window.open(currentViewUrl, "_blank");
});

$("btnSaveKey").addEventListener("click", async () => {
  const key = $("apiKeyInput").value.trim();
  if (!key) {
    showAlert("Paste your API key first.", "error");
    return;
  }
  try {
    const data = await api("/api/settings/api-key", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify({ api_key: key }),
    });
    $("apiKeyInput").value = "";
    showAlert(data.message + (data.api_key_masked ? ` (${data.api_key_masked})` : ""), "success");
    refreshStatus();
  } catch (e) {
    showAlert(e.message, "error");
  }
});

refreshStatus();
