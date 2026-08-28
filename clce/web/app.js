/* AZ-CLCE UI. No CDN. No telemetry. Advisory scores only. */
(function () {
  const form = document.getElementById("clce-form");
  const typesEl = document.getElementById("types");
  const bandEl = document.getElementById("band");
  const gateLine = document.getElementById("gate-line");

  function layers() {
    return {
      r: document.getElementById("r").value,
      d: document.getElementById("d").value,
      p: document.getElementById("p").value,
      n: document.getElementById("n").value,
    };
  }

  function fmt(n) {
    if (typeof n !== "number" || !isFinite(n)) return "—";
    return n.toFixed(4);
  }

  function paint(report) {
    document.getElementById("m-triple").textContent = fmt(report.triple);
    document.getElementById("m-rd").textContent = fmt(report.pairwise && report.pairwise.rd);
    document.getElementById("m-dp").textContent = fmt(report.pairwise && report.pairwise.dp);
    document.getElementById("m-rp").textContent = fmt(report.pairwise && report.pairwise.rp);
    document.getElementById("m-avg").textContent = fmt(report.pairwise_avg);
    document.getElementById("m-plus").textContent = fmt(report.plus);

    const b = report.band || "idle";
    bandEl.className = "band " + b;
    const labels = {
      perfect: "perfect alignment (1.0)",
      acceptable: "acceptable (≥0.7) — paper's line, not a pass/fail of truth",
      structural_inconsistency: "structural inconsistency (<0.7)",
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
      body: JSON.stringify(body),
    })
      .then(function (r) { return r.json(); })
      .then(paint)
      .catch(function (err) {
        bandEl.className = "band structural_inconsistency";
        bandEl.textContent = "Request failed: " + err;
      });
  }

  form.addEventListener("submit", function (ev) {
    ev.preventDefault();
    run("score");
  });
  document.getElementById("classify").addEventListener("click", function () { run("classify"); });
  document.getElementById("gate").addEventListener("click", function () { run("gate"); });
})();
