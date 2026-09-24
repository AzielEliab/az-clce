/* AZ-CLCE local page. No CDN. No telemetry. */
(function () {
  const form = document.getElementById("clce-form");
  const typesEl = document.getElementById("types");
  const bandEl = document.getElementById("band");
  const gateLine = document.getElementById("gate-line");
  const giant = document.getElementById("giant-score");
  const kid = document.getElementById("kid-plain");
  const shaLine = document.getElementById("sha-line");
  const advanced = document.getElementById("advanced");
  const importFile = document.getElementById("import-file");

  const SAMPLE = {
    r: "a blue login button that says submit",
    d: "the login form submits your name and password",
    p: "the login button submits your name and password",
    n: "forgot password link"
  };

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
    return String(Math.round(n * 100));
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
    var shown = pct(report.triple);
    giant.textContent = shown === "—" ? shown : shown + "%";
    giant.setAttribute("aria-label", "Overlap " + pct(report.triple) + " percent");
    kid.textContent = report.kid_plain || "";
    shaLine.textContent = report.input_sha256 ? ("Input hash " + report.input_sha256) : "";

    bandEl.className = "band " + b;
    const labels = {
      perfect: "Complete overlap (1.0).",
      acceptable: "Overlap is at least 0.7. That is the paper's line, not a verdict.",
      structural_inconsistency: "Overlap is below 0.7."
    };
    bandEl.textContent = labels[b] || b;

    typesEl.innerHTML = "";
    const types = report.types || [];
    if (!types.length) {
      const li = document.createElement("li");
      li.textContent = "No mismatch type matched. A person should still read the three boxes.";
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
        ? "The 0.7 line passed. Overlap is at least " + report.gate.min + "."
        : "The 0.7 line did not pass. Overlap is below " + report.gate.min + ".";
    } else {
      gateLine.textContent = "";
    }
  }

  function fail(reason, next) {
    bandEl.className = "band structural_inconsistency";
    bandEl.textContent = reason;
    kid.textContent = next;
    if (advanced) advanced.open = true;
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
          var why = pair.j && pair.j.error ? pair.j.error : "The request did not succeed.";
          fail(why, "Check the boxes, then press Score again.");
          return;
        }
        paint(pair.j);
      })
      .catch(function () {
        fail(
          "This page could not reach the local program.",
          "Keep this tab on 127.0.0.1 and press Score again."
        );
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
  document.getElementById("classify").addEventListener("click", function () {
    advanced.open = true;
    run("classify");
  });
  document.getElementById("gate").addEventListener("click", function () {
    advanced.open = true;
    run("gate");
  });
  document.getElementById("sample").addEventListener("click", function () {
    fill(SAMPLE);
    run("score");
  });

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
        kid.textContent = "Could not import that file: " + layersIn.error + " Try a JSON or labeled text file.";
        return;
      }
      fill(layersIn);
      run("score");
    }).catch(function () {
      kid.textContent = "Could not import that file. Try a JSON or labeled text file.";
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
          kid.textContent = "Could not export: " + payload.error + " Press Score, then Export again.";
          return;
        }
        if (payload.report) paint(payload.report);
        download(payload.filename_json || "az-clce-report.json", payload.json, "application/json");
        download(payload.filename_txt || "az-clce-receipt.txt", payload.txt, "text/plain");
        shaLine.textContent = (shaLine.textContent ? shaLine.textContent + " · " : "") + "Saved the report and the receipt.";
      })
      .catch(function () {
        kid.textContent = "Could not export. Press Score, then Export again.";
      });
  });
})();
