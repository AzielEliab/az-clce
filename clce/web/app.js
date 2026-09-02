/* AZ-CLCE UI. No CDN. No telemetry. Advisory scores only. */
(function () {
  const form = document.getElementById("clce-form");
  const typesEl = document.getElementById("types");
  const bandEl = document.getElementById("band");
  const gateLine = document.getElementById("gate-line");
  const giant = document.getElementById("giant-score");
  const kid = document.getElementById("kid-plain");
  const shaLine = document.getElementById("sha-line");
  const advancedPanel = document.getElementById("advanced-panel");
  const viewSimple = document.getElementById("view-simple");
  const viewAdvanced = document.getElementById("view-advanced");
  const importFile = document.getElementById("import-file");

  const SAMPLE = {
    r: "a blue login button that says submit",
    d: "the login form submits your name and password",
    p: "the login button submits your name and password",
    n: "forgot password link"
  };

  let advanced = false;
  document.body.classList.add("simple");

  function setView(next) {
    advanced = next;
    document.body.classList.toggle("simple", !advanced);
    viewSimple.classList.toggle("on", !advanced);
    viewAdvanced.classList.toggle("on", advanced);
    viewSimple.setAttribute("aria-pressed", String(!advanced));
    viewAdvanced.setAttribute("aria-pressed", String(advanced));
    advancedPanel.hidden = !advanced;
  }

  function layers() {
    return {
      r: document.getElementById("r").value,
      d: document.getElementById("d").value,
      p: document.getElementById("p").value,
      n: document.getElementById("n").value
    };
  }

  function fill(obj) {
    document.getElementById("r").value = obj.r || "";
    document.getElementById("d").value = obj.d || "";
    document.getElementById("p").value = obj.p || "";
    document.getElementById("n").value = obj.n || "";
  }

  function fmt(n) {
    if (typeof n !== "number" || !isFinite(n)) return "—";
    return n.toFixed(4);
  }

  function pct(n) {
    if (typeof n !== "number" || !isFinite(n)) return "—";
    return Math.round(n * 100) + "";
  }

  function paint(report) {
    document.getElementById("m-triple").textContent = fmt(report.triple);
    document.getElementById("m-rd").textContent = fmt(report.pairwise && report.pairwise.rd);
    document.getElementById("m-dp").textContent = fmt(report.pairwise && report.pairwise.dp);
    document.getElementById("m-rp").textContent = fmt(report.pairwise && report.pairwise.rp);
    document.getElementById("m-avg").textContent = fmt(report.pairwise_avg);
    document.getElementById("m-plus").textContent = fmt(report.plus);

    const b = report.band || "idle";
    giant.className = "giant " + b;
    giant.textContent = pct(report.triple);
    kid.textContent = report.kid_plain || "";
    shaLine.textContent = report.input_sha256 ? ("input_sha256 " + report.input_sha256) : "";

    bandEl.className = "band " + b;
    const labels = {
      perfect: "perfect alignment (1.0)",
      acceptable: "acceptable (≥0.7) — paper's line, not a pass/fail of truth",
      structural_inconsistency: "structural inconsistency (<0.7)"
    };
    bandEl.textContent = "Band: " + (labels[b] || b);

    typesEl.innerHTML = "";
    const types = report.types || [];
    if (!types.length) {
      const li = document.createElement("li");
      li.textContent = "No mismatch type matched. Alignment may still need human validation.";
      typesEl.appendChild(li);
    } else {
      types.forEach(function (code) {
        const li = document.createElement("li");
        const title = document.createElement("div");
        const c = document.createElement("span");
        c.className = "code";
        c.textContent = "Type " + code;
        title.appendChild(c);
        title.appendChild(document.createTextNode((report.type_labels && report.type_labels[code]) || ""));
        if (code === report.primary) {
          const tag = document.createElement("span");
          tag.className = "primary-tag";
          tag.textContent = "primary";
          title.appendChild(tag);
        }
        li.appendChild(title);
        const note = document.createElement("p");
        note.className = "note";
        note.textContent = (report.type_notes && report.type_notes[code]) || "";
        li.appendChild(note);
        const kidNote = (report.kid_plain_types && report.kid_plain_types[code]) || "";
        if (kidNote) {
          const kp = document.createElement("p");
          kp.className = "note";
          kp.textContent = kidNote;
          li.appendChild(kp);
        }
        typesEl.appendChild(li);
      });
    }

    if (report.gate) {
      gateLine.textContent = report.gate.passed
        ? "Gate PASS — triple ≥ " + report.gate.min
        : "Gate FAIL — triple < " + report.gate.min;
    } else {
      gateLine.textContent = "";
    }
  }

  function run(mode) {
    const body = layers();
    if (mode === "gate") body.min = 0.7;
    fetch("/api/" + mode, {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(body)
    })
      .then(function (r) { return r.json().then(function (j) { return { ok: r.ok, j: j }; }); })
      .then(function (pair) {
        if (!pair.ok) {
          bandEl.className = "band structural_inconsistency";
          bandEl.textContent = "Request failed: " + (pair.j && pair.j.error ? pair.j.error : "error");
          kid.textContent = "That did not work. Check the boxes and try again.";
          return;
        }
        paint(pair.j);
      })
      .catch(function (err) {
        bandEl.className = "band structural_inconsistency";
        bandEl.textContent = "Request failed: " + err;
        kid.textContent = "That did not work. This UI only runs on 127.0.0.1.";
      });
  }

  function download(filename, text, mime) {
    const blob = new Blob([text], { type: mime || "text/plain;charset=utf-8" });
    const url = URL.createObjectURL(blob);
    const a = document.createElement("a");
    a.href = url;
    a.download = filename;
    document.body.appendChild(a);
    a.click();
    a.remove();
    setTimeout(function () { URL.revokeObjectURL(url); }, 1000);
  }

  form.addEventListener("submit", function (ev) {
    ev.preventDefault();
    run("score");
  });
  document.getElementById("classify").addEventListener("click", function () { run("classify"); });
  document.getElementById("gate").addEventListener("click", function () { run("gate"); });
  document.getElementById("sample").addEventListener("click", function () {
    fill(SAMPLE);
    run("score");
  });
  viewSimple.addEventListener("click", function () { setView(false); });
  viewAdvanced.addEventListener("click", function () { setView(true); });

  document.getElementById("import-btn").addEventListener("click", function () {
    importFile.click();
  });
  importFile.addEventListener("change", function () {
    const file = importFile.files && importFile.files[0];
    importFile.value = "";
    if (!file) return;
    file.text().then(function (text) {
      return fetch("/api/import", {
        method: "POST",
        headers: { "Content-Type": "text/plain; charset=utf-8" },
        body: text
      }).then(function (r) { return r.json(); });
    }).then(function (layersIn) {
      if (layersIn && layersIn.error) {
        kid.textContent = "Import failed: " + layersIn.error;
        return;
      }
      fill(layersIn);
      run("score");
    }).catch(function (err) {
      kid.textContent = "Import failed: " + err;
    });
  });

  document.getElementById("export-btn").addEventListener("click", function () {
    fetch("/api/export", {
      method: "POST",
      headers: { "Content-Type": "application/json" },
      body: JSON.stringify(layers())
    })
      .then(function (r) { return r.json(); })
      .then(function (payload) {
        if (payload.error) {
          kid.textContent = "Export failed: " + payload.error;
          return;
        }
        if (payload.report) paint(payload.report);
        download(payload.filename_json || "az-clce-report.json", payload.json, "application/json");
        download(payload.filename_txt || "az-clce-receipt.txt", payload.txt, "text/plain");
      })
      .catch(function (err) {
        kid.textContent = "Export failed: " + err;
      });
  });

  setView(false);
})();
