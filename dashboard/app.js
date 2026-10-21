// UIT Forum Sentiment Dashboard Logic
document.addEventListener("DOMContentLoaded", () => {
  const data = window.UIT_DATA || [];

  let filteredData = [...data];
  let currentPage = 1;
  const pageSize = 12;

  // Initialize KPI cards
  initKPIs(data);

  // Initialize Charts
  initCharts(data);

  // Initialize Aspect Filter dropdown
  initAspectFilter(data);

  // Render Table
  renderTable();

  // Expose helpers to window
  window.filterData = () => {
    const searchText = document.getElementById("filter-search").value.toLowerCase();
    const sentiment = document.getElementById("filter-sentiment").value;
    const aspect = document.getElementById("filter-aspect").value;

    filteredData = data.filter(item => {
      const matchSearch = !searchText ||
        (item.title && item.title.toLowerCase().includes(searchText)) ||
        (item.author && item.author.toLowerCase().includes(searchText)) ||
        (item.content && item.content.toLowerCase().includes(searchText));

      const matchSentiment = sentiment === "ALL" || item.label === sentiment;
      const matchAspect = aspect === "ALL" || item.primary_aspect === aspect;

      return matchSearch && matchSentiment && matchAspect;
    });

    currentPage = 1;
    renderTable();
  };

  window.openDetail = (id) => {
    const item = data.find(d => d.id === id);
    if (!item) return;

    document.getElementById("modal-title").textContent = item.title;
    document.getElementById("modal-author").textContent = item.author || "Chưa rõ";
    document.getElementById("modal-aspect").textContent = item.primary_aspect || "Chung";
    document.getElementById("modal-score").textContent = item.sentiment_score !== undefined ? item.sentiment_score : "0";
    document.getElementById("modal-confidence").textContent = Math.round((item.confidence || 0.8) * 100) + "%";
    document.getElementById("modal-reason").textContent = item.reason || "Phân tích tự động dựa trên sắc thái từ ngữ và ngữ cảnh.";
    document.getElementById("modal-content").textContent = item.content || item.first_post || "Không có nội dung chi tiết.";

    const urlElem = document.getElementById("modal-url");
    if (item.url) {
      urlElem.href = item.url;
      urlElem.style.display = "inline-flex";
    } else {
      urlElem.style.display = "none";
    }

    const badge = document.getElementById("modal-label");
    badge.className = "badge";
    if (item.label === "POSITIVE") {
      badge.classList.add("badge-pos");
      badge.textContent = "TỐT (TÍCH CỰC)";
    } else if (item.label === "NEGATIVE") {
      badge.classList.add("badge-neg");
      badge.textContent = "XẤU (PHÀN NÀN)";
    } else {
      badge.classList.add("badge-neu");
      badge.textContent = "TRUNG LẬP";
    }

    document.getElementById("detail-modal").classList.remove("hidden");
  };

  window.closeModal = (e) => {
    if (e && e.target && e.target !== e.currentTarget && !e.target.classList.contains("modal-close")) return;
    document.getElementById("detail-modal").classList.add("hidden");
  };

  window.fillSample = (text) => {
    const input = document.getElementById("tester-input");
    input.value = text;
    window.testCustomText();
  };

  window.testCustomText = () => {
    const text = document.getElementById("tester-input").value.trim();
    if (!text) return;

    const resultBox = document.getElementById("tester-result");
    resultBox.classList.remove("hidden", "pos", "neg", "neu");

    const analysis = analyzeClientSide(text);

    let badgeClass = "badge-neu";
    let boxClass = "neu";
    let labelVi = "Trung lập (Hỏi đáp / Thông tin)";

    if (analysis.label === "POSITIVE") {
      badgeClass = "badge-pos";
      boxClass = "pos";
      labelVi = "Tốt (Tích cực / Khen ngợi)";
    } else if (analysis.label === "NEGATIVE") {
      badgeClass = "badge-neg";
      boxClass = "neg";
      labelVi = "Xấu (Tiêu cực / Phàn nàn)";
    }

    resultBox.classList.add(boxClass);
    resultBox.innerHTML = `
      <div style="display: flex; justify-content: space-between; align-items: center; margin-bottom: 0.5rem;">
        <div style="display: flex; align-items: center; gap: 0.5rem;">
          <span class="badge ${badgeClass}">${analysis.label}</span>
          <strong style="color: #fff; font-size: 1rem;">${labelVi}</strong>
        </div>
        <span style="font-size: 0.85rem; color: #94a3b8;">Độ tin cậy: <strong>${Math.round(analysis.confidence * 100)}%</strong> | Điểm: <strong>${analysis.score}</strong></span>
      </div>
      <p style="font-size: 0.875rem; color: #e2e8f0; margin-bottom: 0.5rem;"><strong>Khía cạnh UIT:</strong> <span class="badge badge-aspect">${analysis.aspect}</span></p>
      <p style="font-size: 0.875rem; color: #cbd5e1; line-height: 1.5;">${analysis.reason}</p>
    `;
  };

  function initKPIs(data) {
    const total = data.length;
    const pos = data.filter(d => d.label === "POSITIVE").length;
    const neg = data.filter(d => d.label === "NEGATIVE").length;
    const neu = data.filter(d => d.label === "NEUTRAL").length;

    document.getElementById("kpi-total").textContent = total;
    document.getElementById("kpi-pos").textContent = pos;
    document.getElementById("kpi-pos-pct").textContent = `${((pos / total) * 100).toFixed(1)}% tổng thảo luận`;

    document.getElementById("kpi-neg").textContent = neg;
    document.getElementById("kpi-neg-pct").textContent = `${((neg / total) * 100).toFixed(1)}% tổng thảo luận`;

    document.getElementById("kpi-neu").textContent = neu;
    document.getElementById("kpi-neu-pct").textContent = `${((neu / total) * 100).toFixed(1)}% tổng thảo luận`;
  }

  function initCharts(data) {
    const pos = data.filter(d => d.label === "POSITIVE").length;
    const neg = data.filter(d => d.label === "NEGATIVE").length;
    const neu = data.filter(d => d.label === "NEUTRAL").length;

    // 1. Sentiment Donut Chart
    const ctxSentiment = document.getElementById("sentimentChart").getContext("2d");
    new Chart(ctxSentiment, {
      type: "doughnut",
      data: {
        labels: ["Tốt (Tích cực)", "Xấu (Phàn nàn)", "Trung lập"],
        datasets: [{
          data: [pos, neg, neu],
          backgroundColor: ["#10b981", "#ef4444", "#64748b"],
          borderColor: "#111827",
          borderWidth: 3,
          hoverOffset: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        plugins: {
          legend: {
            position: "bottom",
            labels: { color: "#cbd5e1", font: { family: "Plus Jakarta Sans", size: 12 } }
          }
        },
        cutout: "68%"
      }
    });

    // 2. Aspect Bar Chart
    const aspectCounts = {};
    data.forEach(d => {
      const asp = d.primary_aspect || "Chung / Khác";
      aspectCounts[asp] = (aspectCounts[asp] || 0) + 1;
    });

    const sortedAspects = Object.entries(aspectCounts).sort((a, b) => b[1] - a[1]);
    const aspectLabels = sortedAspects.map(a => a[0]);
    const aspectValues = sortedAspects.map(a => a[1]);

    const ctxAspect = document.getElementById("aspectChart").getContext("2d");
    new Chart(ctxAspect, {
      type: "bar",
      data: {
        labels: aspectLabels,
        datasets: [{
          label: "Số bài viết",
          data: aspectValues,
          backgroundColor: "rgba(56, 189, 248, 0.75)",
          borderColor: "#38bdf8",
          borderWidth: 1,
          borderRadius: 6
        }]
      },
      options: {
        responsive: true,
        maintainAspectRatio: false,
        indexAxis: "y",
        scales: {
          x: {
            ticks: { color: "#94a3b8" },
            grid: { color: "#1f293d" }
          },
          y: {
            ticks: { color: "#e2e8f0", font: { family: "Plus Jakarta Sans" } },
            grid: { display: false }
          }
        },
        plugins: {
          legend: { display: false }
        }
      }
    });
  }

  function initAspectFilter(data) {
    const select = document.getElementById("filter-aspect");
    const aspects = Array.from(new Set(data.map(d => d.primary_aspect || "Chung / Khác"))).sort();
    aspects.forEach(asp => {
      const opt = document.createElement("option");
      opt.value = asp;
      opt.textContent = asp;
      select.appendChild(opt);
    });
  }

  function renderTable() {
    const tbody = document.getElementById("table-body");
    tbody.innerHTML = "";

    const totalRecords = filteredData.length;
    const totalPages = Math.ceil(totalRecords / pageSize) || 1;
    if (currentPage > totalPages) currentPage = totalPages;

    const startIdx = (currentPage - 1) * pageSize;
    const pageItems = filteredData.slice(startIdx, startIdx + pageSize);

    document.getElementById("record-count").textContent = `Hiển thị ${Math.min(startIdx + 1, totalRecords)}-${Math.min(startIdx + pageSize, totalRecords)} trong tổng số ${totalRecords} bài viết`;

    pageItems.forEach(item => {
      const tr = document.createElement("tr");

      let badgeHtml = "";
      if (item.label === "POSITIVE") {
        badgeHtml = `<span class="badge badge-pos">Tốt</span>`;
      } else if (item.label === "NEGATIVE") {
        badgeHtml = `<span class="badge badge-neg">Xấu</span>`;
      } else {
        badgeHtml = `<span class="badge badge-neu">Trung lập</span>`;
      }

      const score = item.sentiment_score !== undefined ? item.sentiment_score : 0;
      const scoreColor = score > 0 ? "var(--color-pos)" : (score < 0 ? "var(--color-neg)" : "var(--text-muted)");

      const evidences = item.positive_evidences || item.negative_evidences || "—";

      tr.innerHTML = `
        <td style="color: var(--text-muted); font-family: var(--font-mono); font-size: 0.8rem;">#${item.id || "—"}</td>
        <td>
          <a href="javascript:void(0)" onclick="openDetail(${item.id})" class="topic-title-link" title="${escapeHtml(item.title)}">
            ${escapeHtml(item.title || "Không có tiêu đề")}
          </a>
        </td>
        <td style="color: #cbd5e1;">${escapeHtml(item.author || "Ẩn danh")}</td>
        <td><span class="badge-aspect">${escapeHtml(item.primary_aspect || "Chung")}</span></td>
        <td>${badgeHtml}</td>
        <td style="color: ${scoreColor}; font-weight: 700; font-family: var(--font-mono);">${score > 0 ? "+" + score : score}</td>
        <td style="color: #94a3b8; font-size: 0.775rem;">${escapeHtml(evidences)}</td>
        <td style="text-align: center;">
          <button class="btn btn-secondary" style="padding: 0.25rem 0.5rem; font-size: 0.75rem;" onclick="openDetail(${item.id})">Xem</button>
        </td>
      `;
      tbody.appendChild(tr);
    });

    renderPagination(totalPages);
  }

  function renderPagination(totalPages) {
    const pag = document.getElementById("pagination");
    pag.innerHTML = "";

    if (totalPages <= 1) return;

    const prevBtn = document.createElement("button");
    prevBtn.className = "page-btn";
    prevBtn.textContent = "«";
    prevBtn.disabled = currentPage === 1;
    prevBtn.onclick = () => { if (currentPage > 1) { currentPage--; renderTable(); } };
    pag.appendChild(prevBtn);

    for (let p = 1; p <= totalPages; p++) {
      if (totalPages > 7 && Math.abs(p - currentPage) > 2 && p !== 1 && p !== totalPages) {
        if (p === 2 || p === totalPages - 1) {
          const dots = document.createElement("span");
          dots.textContent = "...";
          dots.style.color = "#64748b";
          dots.style.padding = "0.2rem";
          pag.appendChild(dots);
        }
        continue;
      }
      const btn = document.createElement("button");
      btn.className = "page-btn" + (p === currentPage ? " active" : "");
      btn.textContent = p;
      btn.onclick = () => { currentPage = p; renderTable(); };
      pag.appendChild(btn);
    }

    const nextBtn = document.createElement("button");
    nextBtn.className = "page-btn";
    nextBtn.textContent = "»";
    nextBtn.disabled = currentPage === totalPages;
    nextBtn.onclick = () => { if (currentPage < totalPages) { currentPage++; renderTable(); } };
    pag.appendChild(nextBtn);
  }

  function escapeHtml(str) {
    if (!str) return "";
    return String(str).replace(/[&<>"']/g, m => ({
      "&": "&amp;", "<": "&lt;", ">": "&gt;", '"': "&quot;", "'": "&#39;"
    })[m]);
  }

  // Client-side rule engine mimicking processor/sentiment_analyzer.py
  function analyzeClientSide(text) {
    const lower = text.toLowerCase();

    // Aspects
    const aspectMap = {
      "Cơ sở vật chất": ["máy lạnh", "điều hòa", "wifi", "mạng", "thang máy", "nhà xe", "gửi xe", "nhà vệ sinh", "wc", "phòng học", "lab", "quạt", "loa", "tòa nhà", "csvc"],
      "Học phí & Học bổng": ["học phí", "tiền học", "đóng tiền", "tăng học phí", "học bổng", "ngân hàng"],
      "Đăng ký môn học & Hệ thống": ["đăng ký môn học", "dkmh", "sập web", "nghẽn mạng", "hủy môn", "portal", "moodle", "quá tải"],
      "Giảng viên & Đào tạo": ["giảng viên", "thầy", "cô", "gv", "chấm điểm", "nhiệt tình", "tận tâm", "dạy hay", "đồ án", "môn học"],
      "Phòng ban & Dịch vụ SV": ["phòng đào tạo", "pđt", "ctsv", "công tác sinh viên", "căn tin", "khám sức khỏe", "thủ tục", "ktx"]
    };

    let detectedAspect = "Chung / Khác";
    for (const [asp, kws] of Object.entries(aspectMap)) {
      if (kws.some(kw => lower.includes(kw))) {
        detectedAspect = asp;
        break;
      }
    }

    const negPhrases = ["không hoạt động", "không chạy", "không bật", "không mát", "sập web", "bị lỗi", "hư rồi", "hỏng rồi", "chờ quá lâu", "thái độ kém", "tăng học phí", "quá nóng", "mất mạng", "rớt mạng"];
    const posPhrases = ["rất tốt", "rất nhiệt tình", "rất xịn", "quá xịn", "cảm ơn thầy cô", "cảm ơn trường", "hỗ trợ rất nhanh", "giải quyết nhanh", "rất hài lòng", "hoạt động ổn định"];

    const posWords = ["tốt", "tuyệt", "xịn", "nhanh", "nhiệt tình", "chu đáo", "tận tâm", "cảm ơn", "mát", "đẹp", "khen", "ổn", "thích"];
    const negWords = ["hỏng", "hư", "lỗi", "sập", "chán", "kém", "tệ", "bực", "nóng", "yếu", "chậm", "thất vọng", "đắt", "lag", "nghẽn", "khó chịu"];
    const negations = ["không", "chẳng", "chả", "chưa", "kém"];

    let posScore = 0;
    let negScore = 0;
    const evPos = [];
    const evNeg = [];

    negPhrases.forEach(p => {
      if (lower.includes(p)) { negScore += 2.5; evNeg.push(p); }
    });
    posPhrases.forEach(p => {
      if (lower.includes(p)) { posScore += 2.5; evPos.push(p); }
    });

    const tokens = lower.split(/\s+/);
    tokens.forEach((w, i) => {
      const hasNegation = (i > 0 && negations.includes(tokens[i-1])) || (i > 1 && negations.includes(tokens[i-2]));
      if (posWords.some(pw => w.includes(pw))) {
        if (hasNegation) { negScore += 1.5; evNeg.push(tokens[i-1] + " " + w); }
        else { posScore += 1.0; evPos.push(w); }
      } else if (negWords.some(nw => w.includes(nw))) {
        if (hasNegation) { posScore += 0.5; }
        else { negScore += 1.2; evNeg.push(w); }
      }
    });

    let label = "NEUTRAL";
    let reason = `Bài viết trao đổi hoặc hỏi đáp liên quan đến ${detectedAspect} (sắc thái trung tính).`;
    let confidence = 0.85;

    if (negScore >= 1.0 && negScore > posScore) {
      label = "NEGATIVE";
      confidence = Math.min(0.98, 0.70 + (negScore / (posScore + negScore + 1.0)) * 0.25);
      reason = `Phản ánh/phàn nàn tiêu cực về ${detectedAspect}: phát hiện các từ '${[...new Set(evNeg)].slice(0, 4).join(", ")}'`;
    } else if (posScore >= 1.0 && posScore > negScore) {
      label = "POSITIVE";
      confidence = Math.min(0.98, 0.70 + (posScore / (posScore + negScore + 1.0)) * 0.25);
      reason = `Đánh giá tích cực/khen ngợi về ${detectedAspect}: phát hiện các từ '${[...new Set(evPos)].slice(0, 4).join(", ")}'`;
    }

    return {
      label,
      aspect: detectedAspect,
      score: +(posScore - negScore).toFixed(1),
      confidence,
      reason
    };
  }
});
