<!-- ═══════════════════════════════════════════════════════
     SHARED NAV COMPONENT — include in every page via JS
     Canadian Accountability Project — ABCXYZ.github.io
     ═══════════════════════════════════════════════════════ -->
<script>
(function() {
  // LIRIL NPU baked analysis results — no API, pure local inference
  window.LIRIL_SITE_DATA = {
    seed: 118400,
    tick_hz: 118.4,
    sator_row: 3,
    sator_word: "OPERA",
    last_classify_ts: 1775762162,
    total_samples_trained: 1727,
    gpu0_util: 44,
    gpu1_util: 26,
    nats_status: "connected",
    domains: {
      "MAID Accountability":    { domain: "ETHICS",     confidence: 0.99, device: "NPU",  method: "keyword-decisive" },
      "Political Failure":      { domain: "ETHICS",     confidence: 0.75, device: "CPU",  method: "keyword_override", npu_original: "REASONING" },
      "Disability/Ethics":      { domain: "ETHICS",     confidence: 0.99, device: "NPU",  method: "keyword-decisive" },
      "Legal/Criminal":         { domain: "ETHICS",     confidence: 0.80, device: "NPU",  method: "keyword-decisive" },
      "ArriveCAN/AG Findings":  { domain: "ETHICS",     confidence: 0.99, device: "NPU",  method: "keyword-decisive" },
      "CERB Pandemic Spending": { domain: "ETHICS",     confidence: 0.99, device: "NPU",  method: "keyword-decisive" },
      "Zaccardelli/Arar":       { domain: "ETHICS",     confidence: 0.99, device: "NPU",  method: "keyword-decisive" },
    },
    route: { agent: "nemoclaw", domain: "ETHICS", fallback_from: "kyre" }
  };

  // Inject header HTML
  const headerHTML = `
<header class="site-header" id="site-header">
  <div class="header-inner">
    <a href="/index.html" class="site-logo">
      🍁 <span>CAP</span>
      <span class="logo-sub">Canadian Accountability Project</span>
    </a>
    <nav class="site-nav" id="site-nav">
      <a href="/index.html"                id="nav-home">Home</a>
      <a href="/records.html"              id="nav-records">Records DB</a>
      <a href="/maid-accountability.html"  id="nav-maid">MAID Report</a>
      <a href="/rcmp-commissioners.html"   id="nav-rcmp">RCMP</a>
      <a href="/liril-analysis.html"       id="nav-liril">LIRIL Analysis</a>
      <a href="/cicd-status.html"          id="nav-cicd">CI/CD</a>
    </nav>
    <div class="liril-status-pill" title="LIRIL NPU — Local inference, no external API">
      <div class="dot"></div>
      LIRIL·NPU &nbsp;|&nbsp; SEED:118400 &nbsp;|&nbsp; NATS:4223
    </div>
    <button class="menu-toggle" id="menu-toggle" aria-label="Menu">☰</button>
  </div>
</header>`;

  const footerHTML = `
<footer class="site-footer">
  <div class="footer-inner">
    <div>
      <h4>Canadian Accountability Project</h4>
      <ul>
        <li><a href="/index.html">Home</a></li>
        <li><a href="/records.html">Records Database</a></li>
        <li><a href="/maid-accountability.html">MAID Report</a></li>
        <li><a href="/rcmp-commissioners.html">RCMP Commissioners</a></li>
      </ul>
    </div>
    <div>
      <h4>AI Analysis</h4>
      <ul>
        <li><a href="/liril-analysis.html">LIRIL NPU Analysis</a></li>
        <li><a href="/cicd-status.html">CI/CD Status</a></li>
        <li><a href="/about.html">About This Project</a></li>
      </ul>
    </div>
    <div>
      <h4>Primary Sources</h4>
      <ul>
        <li><a href="https://www.canada.ca/en/health-canada/services/medical-assistance-dying.html" rel="noopener">Health Canada — MAID</a></li>
        <li><a href="https://www.parl.ca" rel="noopener">Parliament of Canada</a></li>
        <li><a href="https://www.ohchr.org" rel="noopener">UN OHCHR</a></li>
        <li><a href="https://masscasualtycommission.ca" rel="noopener">Mass Casualty Commission</a></li>
      </ul>
    </div>
    <div>
      <h4>Infrastructure</h4>
      <ul>
        <li><span style="color:#444">LIRIL NPU — Local, no API</span></li>
        <li><span style="color:#444">NemoClaw GPU0/GPU1 RTX 5070 Ti</span></li>
        <li><span style="color:#444">NATS mesh — 127.0.0.1:4223</span></li>
        <li><span style="color:#444">SEED: 118400 | TICK: 118.4Hz</span></li>
      </ul>
    </div>
  </div>
  <div class="footer-bottom">
    <span>© 2025 Canadian Accountability Project. All records sourced from official government, parliamentary, and court documents.</span>
    <span class="footer-liril-sig">
      <span class="dot"></span>
      LIRIL·NPU·SATOR·OPERA·SEED:118400 — local inference only, no external data
    </span>
  </div>
</footer>`;

  // Insert on DOMContentLoaded
  document.addEventListener('DOMContentLoaded', function() {
    // Header
    const ph = document.getElementById('page-header-placeholder');
    if (ph) ph.outerHTML = headerHTML;
    else document.body.insertAdjacentHTML('afterbegin', headerHTML);

    // Footer
    const pf = document.getElementById('page-footer-placeholder');
    if (pf) pf.outerHTML = footerHTML;
    else document.body.insertAdjacentHTML('beforeend', footerHTML);

    // Active nav
    const path = window.location.pathname.split('/').pop() || 'index.html';
    document.querySelectorAll('.site-nav a').forEach(a => {
      if (a.getAttribute('href').includes(path)) a.classList.add('active');
    });

    // Mobile menu
    const toggle = document.getElementById('menu-toggle');
    const nav    = document.getElementById('site-nav');
    if (toggle && nav) {
      toggle.addEventListener('click', () => nav.classList.toggle('open'));
    }
  });
})();
</script>
