// FixRoute — Client Presentation
// Palette: Ocean Gradient (deep blue + teal) — fits AI / enterprise / PropTech
// Layout: 16x9 widescreen
// Typography: Georgia (header, personality) + Calibri (body, clean)

const pptxgen = require("pptxgenjs");

const pres = new pptxgen();
pres.layout = "LAYOUT_WIDE"; // 13.3" x 7.5"
pres.author = "FixRoute Engineering";
pres.title = "FixRoute — AI-Powered Maintenance Triage";
pres.company = "FixRoute";

// ---------- Palette ----------
const COLORS = {
  primary: "065A82",   // deep blue
  secondary: "1C7293", // teal
  accent: "F9A03F",    // amber (high-contrast for callouts)
  midnight: "21295C",  // midnight
  ice: "E8F1F5",       // ice background
  white: "FFFFFF",
  ink: "1A2332",       // body text
  muted: "64748B",     // muted/captions
  lightLine: "CBD5E1", // dividers
};

// ---------- Typography ----------
const FONT = {
  header: "Georgia",
  body: "Calibri",
};

// ---------- Reusable helpers ----------
const addFooter = (slide, pageNum, total) => {
  // bottom-left small mark
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 7.1, w: 0.15, h: 0.15,
    fill: { color: COLORS.accent }, line: { type: "none" },
  });
  slide.addText("FixRoute", {
    x: 0.75, y: 7.05, w: 3, h: 0.25,
    fontFace: FONT.body, fontSize: 9, color: COLORS.muted, margin: 0,
  });
  slide.addText(`${pageNum} / ${total}`, {
    x: 12.0, y: 7.05, w: 1.0, h: 0.25,
    fontFace: FONT.body, fontSize: 9, color: COLORS.muted, align: "right", margin: 0,
  });
};

const addSlideTitle = (slide, eyebrow, title) => {
  // small accent bar
  slide.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 0.55, w: 0.5, h: 0.05,
    fill: { color: COLORS.accent }, line: { type: "none" },
  });
  slide.addText(eyebrow, {
    x: 0.5, y: 0.7, w: 12, h: 0.3,
    fontFace: FONT.body, fontSize: 11, color: COLORS.secondary,
    bold: true, charSpacing: 4, margin: 0,
  });
  slide.addText(title, {
    x: 0.5, y: 1.05, w: 12, h: 0.9,
    fontFace: FONT.header, fontSize: 32, color: COLORS.midnight, bold: true, margin: 0,
  });
};

const TOTAL_SLIDES = 14;

// =====================================================================
// SLIDE 1 — Title (dark hero)
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: COLORS.midnight };

  // Decorative geometric motif: large offset circle
  s.addShape(pres.shapes.OVAL, {
    x: 9.5, y: -3, w: 8, h: 8,
    fill: { color: COLORS.primary, transparency: 30 }, line: { type: "none" },
  });
  s.addShape(pres.shapes.OVAL, {
    x: 11, y: 4, w: 5, h: 5,
    fill: { color: COLORS.secondary, transparency: 50 }, line: { type: "none" },
  });

  // Accent bar
  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.7, y: 2.6, w: 0.6, h: 0.06,
    fill: { color: COLORS.accent }, line: { type: "none" },
  });

  s.addText("FIXROUTE", {
    x: 0.7, y: 2.75, w: 12, h: 0.5,
    fontFace: FONT.body, fontSize: 14, color: COLORS.accent,
    bold: true, charSpacing: 8, margin: 0,
  });
  s.addText("AI-Powered Maintenance Triage", {
    x: 0.7, y: 3.3, w: 12, h: 1.2,
    fontFace: FONT.header, fontSize: 54, color: COLORS.white, bold: true, margin: 0,
  });
  s.addText("for Property Management", {
    x: 0.7, y: 4.45, w: 12, h: 0.6,
    fontFace: FONT.header, fontSize: 28, color: "CADCFC", italic: true, margin: 0,
  });
  s.addText("Tenant submission → AI classification → right vendor in under 5 minutes.", {
    x: 0.7, y: 5.4, w: 11, h: 0.5,
    fontFace: FONT.body, fontSize: 16, color: "CADCFC", margin: 0,
  });
  s.addText("Client Presentation  |  2026", {
    x: 0.7, y: 6.6, w: 12, h: 0.3,
    fontFace: FONT.body, fontSize: 10, color: COLORS.muted,
    bold: true, charSpacing: 4, margin: 0,
  });
}

// =====================================================================
// SLIDE 2 — The problem
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: COLORS.white };
  addSlideTitle(s, "THE PROBLEM", "Maintenance triage is broken.");

  s.addText(
    "Property managers spend over 40% of their day reading maintenance requests, " +
    "routing them by urgency, and coordinating vendor dispatch by phone. The result " +
    "is slow, error-prone, and doesn't scale.",
    {
      x: 0.5, y: 2.2, w: 8.5, h: 1.4,
      fontFace: FONT.body, fontSize: 16, color: COLORS.ink, margin: 0, paraSpaceAfter: 8,
    }
  );

  // Three stat callouts
  const stats = [
    { num: "40%+", label: "of a PM's day\nspent on triage" },
    { num: "60min", label: "avg time to\ndispatch urgent issues" },
    { num: "1 in 50", label: "emergencies\nmis-routed today" },
  ];
  stats.forEach((stat, i) => {
    const x = 0.5 + i * 4.2;
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: 4.1, w: 3.9, h: 2.4,
      fill: { color: COLORS.ice }, line: { type: "none" },
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: 4.1, w: 3.9, h: 0.08,
      fill: { color: COLORS.secondary }, line: { type: "none" },
    });
    s.addText(stat.num, {
      x, y: 4.3, w: 3.9, h: 1.1,
      fontFace: FONT.header, fontSize: 60, color: COLORS.primary, bold: true,
      align: "center", valign: "middle", margin: 0,
    });
    s.addText(stat.label, {
      x, y: 5.4, w: 3.9, h: 1.0,
      fontFace: FONT.body, fontSize: 13, color: COLORS.muted,
      align: "center", valign: "top", margin: 0,
    });
  });
  addFooter(s, 2, TOTAL_SLIDES);
}

// =====================================================================
// SLIDE 3 — What FixRoute does
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: COLORS.white };
  addSlideTitle(s, "THE SOLUTION", "What FixRoute does.");

  const features = [
    {
      icon: "→",
      title: "Ingests every request",
      body: "Text, photos, voice — from any device. Tenants get immediate acknowledgment.",
    },
    {
      icon: "◇",
      title: "AI classifies & triages",
      body: "Category, urgency, and confidence score in under 5 seconds. Self-serve steps for common issues.",
    },
    {
      icon: "★",
      title: "Dispatches the right vendor",
      body: "Weighted matching by trade, proximity, availability, rating, and cost. Emergency rotation on no-response.",
    },
    {
      icon: "✓",
      title: "Closes the loop",
      body: "Cost estimates with PM approval, status updates, spend analytics, and audit trail.",
    },
  ];

  features.forEach((f, i) => {
    const col = i % 2;
    const row = Math.floor(i / 2);
    const x = 0.5 + col * 6.3;
    const y = 2.3 + row * 2.1;
    // Icon circle
    s.addShape(pres.shapes.OVAL, {
      x, y: y + 0.15, w: 0.9, h: 0.9,
      fill: { color: COLORS.primary }, line: { type: "none" },
    });
    s.addText(f.icon, {
      x, y: y + 0.15, w: 0.9, h: 0.9,
      fontFace: FONT.body, fontSize: 28, color: COLORS.white, bold: true,
      align: "center", valign: "middle", margin: 0,
    });
    s.addText(f.title, {
      x: x + 1.1, y: y + 0.1, w: 5, h: 0.5,
      fontFace: FONT.header, fontSize: 18, color: COLORS.midnight, bold: true, margin: 0,
    });
    s.addText(f.body, {
      x: x + 1.1, y: y + 0.6, w: 5, h: 1.3,
      fontFace: FONT.body, fontSize: 13, color: COLORS.ink, margin: 0,
    });
  });
  addFooter(s, 3, TOTAL_SLIDES);
}

// =====================================================================
// SLIDE 4 — User journey (tenant flow)
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: COLORS.ice };
  addSlideTitle(s, "USER JOURNEY — TENANT", "From problem to resolution.");

  const steps = [
    { num: "1", title: "Submit", body: "Text, photo,\nor voice" },
    { num: "2", title: "Acknowledge", body: "AI classification\nin < 5 sec" },
    { num: "3", title: "Self-serve", body: "Troubleshooting\nfor simple issues" },
    { num: "4", title: "Dispatch", body: "Right vendor\n+ ETA" },
    { num: "5", title: "Track", body: "Status to\ncompletion" },
  ];

  const startX = 0.5;
  const stepW = 2.45;
  const gap = 0.05;

  steps.forEach((step, i) => {
    const x = startX + i * (stepW + gap);
    // Card
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: 2.6, w: stepW, h: 2.6,
      fill: { color: COLORS.white }, line: { type: "none" },
      shadow: { type: "outer", color: "000000", blur: 8, offset: 2, angle: 90, opacity: 0.08 },
    });
    // Number circle
    s.addShape(pres.shapes.OVAL, {
      x: x + 0.25, y: 2.85, w: 0.65, h: 0.65,
      fill: { color: COLORS.accent }, line: { type: "none" },
    });
    s.addText(step.num, {
      x: x + 0.25, y: 2.85, w: 0.65, h: 0.65,
      fontFace: FONT.header, fontSize: 22, color: COLORS.midnight, bold: true,
      align: "center", valign: "middle", margin: 0,
    });
    s.addText(step.title, {
      x, y: 3.7, w: stepW, h: 0.5,
      fontFace: FONT.header, fontSize: 18, color: COLORS.midnight, bold: true,
      align: "center", margin: 0,
    });
    s.addText(step.body, {
      x: x + 0.1, y: 4.25, w: stepW - 0.2, h: 0.9,
      fontFace: FONT.body, fontSize: 12, color: COLORS.muted,
      align: "center", margin: 0,
    });
  });

  // Connecting arrows between cards
  for (let i = 0; i < steps.length - 1; i++) {
    const x = startX + i * (stepW + gap) + stepW - 0.02;
    s.addText("›", {
      x, y: 3.6, w: 0.1, h: 0.5,
      fontFace: FONT.body, fontSize: 24, color: COLORS.secondary, bold: true,
      align: "center", valign: "middle", margin: 0,
    });
  }

  s.addText("Average end-to-end: under 5 minutes for urgent, under 30 minutes for routine.", {
    x: 0.5, y: 5.6, w: 12.3, h: 0.4,
    fontFace: FONT.body, fontSize: 13, color: COLORS.secondary, italic: true,
    align: "center", margin: 0,
  });
  addFooter(s, 4, TOTAL_SLIDES);
}

// =====================================================================
// SLIDE 5 — Property manager flow
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: COLORS.white };
  addSlideTitle(s, "USER JOURNEY — PROPERTY MANAGER", "Focus on exceptions, not every request.");

  const cols = [
    {
      title: "Before FixRoute",
      color: "B91C1C",
      bg: "FEE2E2",
      items: [
        "Read every request manually",
        "Phone vendors to confirm availability",
        "Track status in spreadsheets",
        "Approve estimates by email",
        "Compile spend reports by hand",
      ],
    },
    {
      title: "After FixRoute",
      color: COLORS.primary,
      bg: COLORS.ice,
      items: [
        "AI pre-classifies every request",
        "Ranked vendor matches in seconds",
        "Single dashboard with real-time status",
        "One-click estimate approval",
        "Live spend analytics by trade / property",
      ],
    },
  ];

  cols.forEach((col, i) => {
    const x = 0.5 + i * 6.3;
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: 2.3, w: 6, h: 4.4,
      fill: { color: col.bg }, line: { type: "none" },
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: 2.3, w: 0.1, h: 4.4,
      fill: { color: col.color }, line: { type: "none" },
    });
    s.addText(col.title, {
      x: x + 0.3, y: 2.45, w: 5.5, h: 0.5,
      fontFace: FONT.header, fontSize: 20, color: col.color, bold: true, margin: 0,
    });
    s.addText(
      col.items.map((item, idx) => ({
        text: item,
        options: { bullet: { code: "25A0" }, breakLine: idx < col.items.length - 1 },
      })),
      {
        x: x + 0.3, y: 3.1, w: 5.5, h: 3.4,
        fontFace: FONT.body, fontSize: 14, color: COLORS.ink,
        paraSpaceAfter: 8, margin: 0,
      }
    );
  });
  addFooter(s, 5, TOTAL_SLIDES);
}

// =====================================================================
// SLIDE 6 — Architecture overview
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: COLORS.white };
  addSlideTitle(s, "ARCHITECTURE", "Built for scale, security, and resilience.");

  // 4 horizontal layers
  const layers = [
    { title: "Frontend", color: COLORS.midnight, body: "Vue.js 3 + Vite + Pinia — responsive web, mobile-ready" },
    { title: "API", color: COLORS.primary, body: "Django 5 + DRF + OpenAPI — versioned, rate-limited, audited" },
    { title: "Domain", color: COLORS.secondary, body: "5 bounded contexts — Intake · Triage · Dispatch · Vendors · Analytics" },
    { title: "Data & AI", color: "028090", body: "Postgres + pgvector · Redis · Celery · Azure OpenAI · LangChain" },
  ];

  layers.forEach((layer, i) => {
    const y = 2.3 + i * 0.85;
    s.addShape(pres.shapes.RECTANGLE, {
      x: 0.5, y, w: 12.3, h: 0.7,
      fill: { color: layer.color }, line: { type: "none" },
    });
    s.addText(layer.title, {
      x: 0.7, y, w: 2.5, h: 0.7,
      fontFace: FONT.header, fontSize: 16, color: COLORS.white, bold: true,
      valign: "middle", margin: 0,
    });
    s.addText(layer.body, {
      x: 3.3, y, w: 9.4, h: 0.7,
      fontFace: FONT.body, fontSize: 13, color: COLORS.white,
      valign: "middle", margin: 0,
    });
  });

  s.addText("Multi-tenant isolation · Row-level security · OAuth 2 / OIDC · End-to-end observability · 7-year retention", {
    x: 0.5, y: 6.4, w: 12.3, h: 0.4,
    fontFace: FONT.body, fontSize: 12, color: COLORS.muted, italic: true, align: "center", margin: 0,
  });
  addFooter(s, 6, TOTAL_SLIDES);
}

// =====================================================================
// SLIDE 7 — Tech stack table
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: COLORS.ice };
  addSlideTitle(s, "TECH STACK", "Modern, mature, enterprise-grade.");

  const rows = [
    ["Layer", "Technology", "Why"],
    ["Backend", "Python 3.12 · Django 5 · DRF", "Mature, async-capable, large ecosystem"],
    ["Frontend", "Vue.js 3 · Vite · Pinia", "Reactive, performant, easy onboarding"],
    ["Database", "PostgreSQL 16 + pgvector", "Operational + vector embeddings in one store"],
    ["AI", "LangChain + Azure OpenAI", "Pluggable provider, RAG, agent tooling"],
    ["Notifications", "ACS · APNs · FCM · Email", "Multi-channel reach with safety guardrails"],
    ["Storage", "Azure Blob + SAS tokens", "Photo/voice with lifecycle tiering"],
    ["Auth", "Microsoft Entra ID (OIDC)", "Enterprise SSO, MFA, SCIM"],
    ["Infra", "AKS · Terraform · GitHub Actions", "Multi-region DR, reproducible, automated"],
  ];

  const tableData = rows.map((row, i) => {
    if (i === 0) {
      return row.map((c) => ({
        text: c,
        options: { bold: true, color: COLORS.white, fill: { color: COLORS.midnight }, fontSize: 12, fontFace: FONT.body },
      }));
    }
    return row.map((c, j) => ({
      text: c,
      options: {
        bold: j === 0,
        color: j === 0 ? COLORS.primary : COLORS.ink,
        fontSize: 11,
        fontFace: FONT.body,
        fill: { color: i % 2 === 0 ? COLORS.white : "F1F5F9" },
      },
    }));
  });

  s.addTable(tableData, {
    x: 0.5, y: 2.3, w: 12.3, h: 4.3,
    colW: [2.0, 3.8, 6.5],
    rowH: 0.48,
    border: { type: "solid", pt: 0.5, color: COLORS.lightLine },
    valign: "middle",
  });
  addFooter(s, 7, TOTAL_SLIDES);
}

// =====================================================================
// SLIDE 8 — Workflow / flowchart (Triage decision flow)
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: COLORS.white };
  addSlideTitle(s, "WORKFLOW", "How the AI triages a request.");

  // Vertical decision flow
  const nodes = [
    { type: "start", y: 2.3, label: "Tenant submits request\n(text, photo, voice)" },
    { type: "process", y: 3.2, label: "Compute embeddings\n(text + image)" },
    { type: "process", y: 4.1, label: "AI classification\n(category · urgency · confidence)" },
    { type: "decision", y: 5.0, label: "Confidence\n≥ threshold?" },
    { type: "branch", y: 5.9, label: "No → Human dispatcher\nYes → Continue" },
    { type: "end", y: 6.8, label: "Self-serve steps OR\nvendor dispatch" },
  ];

  // Center x
  const cx = 6.5;
  const boxW = 4.2;
  const boxH = 0.7;

  nodes.forEach((node, i) => {
    let fill = COLORS.ice;
    let border = COLORS.secondary;
    let textColor = COLORS.ink;
    if (node.type === "start") { fill = COLORS.midnight; textColor = COLORS.white; border = COLORS.midnight; }
    if (node.type === "decision") { fill = COLORS.accent; textColor = COLORS.midnight; border = COLORS.accent; }
    if (node.type === "end") { fill = COLORS.primary; textColor = COLORS.white; border = COLORS.primary; }

    s.addShape(pres.shapes.RECTANGLE, {
      x: cx - boxW / 2, y: node.y, w: boxW, h: boxH,
      fill: { color: fill }, line: { color: border, width: 1.5 },
    });
    s.addText(node.label, {
      x: cx - boxW / 2, y: node.y, w: boxW, h: boxH,
      fontFace: FONT.body, fontSize: 12, color: textColor, bold: true,
      align: "center", valign: "middle", margin: 0,
    });
    // Arrow down
    if (i < nodes.length - 1 && node.type !== "branch") {
      s.addText("↓", {
        x: cx - 0.2, y: node.y + boxH, w: 0.4, h: 0.2,
        fontFace: FONT.body, fontSize: 16, color: COLORS.muted, bold: true,
        align: "center", valign: "top", margin: 0,
      });
    }
  });

  // Side annotation
  s.addText("Per-tenant\nconfidence threshold", {
    x: 10.5, y: 5.0, w: 2.2, h: 0.7,
    fontFace: FONT.body, fontSize: 11, color: COLORS.secondary, italic: true,
    valign: "middle", align: "left", margin: 0,
  });
  s.addShape(pres.shapes.LINE, {
    x: 9.3, y: 5.35, w: 1.1, h: 0,
    line: { color: COLORS.secondary, width: 1.5, dashType: "dash" },
  });

  addFooter(s, 8, TOTAL_SLIDES);
}

// =====================================================================
// SLIDE 9 — Reliability & DR
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: COLORS.midnight };
  addSlideTitle(s, "RELIABILITY", "Built to stay up. Built to recover.");

  // Three large stat callouts
  const stats = [
    { num: "99.95%", label: "Triage API\nSLO" },
    { num: "4h", label: "Recovery time\nobjective (RTO)" },
    { num: "15min", label: "Recovery point\nobjective (RPO)" },
  ];
  stats.forEach((stat, i) => {
    const x = 0.5 + i * 4.2;
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: 2.3, w: 3.9, h: 2.0,
      fill: { color: "FFFFFF", transparency: 90 }, line: { color: COLORS.secondary, width: 1 },
    });
    s.addText(stat.num, {
      x, y: 2.4, w: 3.9, h: 1.0,
      fontFace: FONT.header, fontSize: 48, color: COLORS.accent, bold: true,
      align: "center", valign: "middle", margin: 0,
    });
    s.addText(stat.label, {
      x, y: 3.5, w: 3.9, h: 0.8,
      fontFace: FONT.body, fontSize: 12, color: "CADCFC",
      align: "center", valign: "top", margin: 0,
    });
  });

  // Lower bullet list
  const bullets = [
    "Multi-region active-passive deployment on Azure Kubernetes Service",
    "Database with cross-region read replica + geo-redundant blob storage",
    "Quarterly failover drills validate RTO and RPO targets",
    "Circuit breakers on every external dependency",
    "SLO-based alerting before any service serves production traffic",
  ];
  s.addText(
    bullets.map((b, i) => ({ text: b, options: { bullet: true, breakLine: i < bullets.length - 1 } })),
    {
      x: 0.5, y: 4.7, w: 12.3, h: 2.2,
      fontFace: FONT.body, fontSize: 14, color: "CADCFC",
      paraSpaceAfter: 6, margin: 0,
    }
  );
  addFooter(s, 9, TOTAL_SLIDES);
}

// =====================================================================
// SLIDE 10 — Security & compliance
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: COLORS.white };
  addSlideTitle(s, "SECURITY & COMPLIANCE", "Enterprise-grade from day one.");

  const items = [
    {
      title: "Multi-tenant isolation",
      body: "Every table carries a tenant_id. PostgreSQL row-level security + application-layer enforcement.",
    },
    {
      title: "Authentication",
      body: "OIDC/OAuth2 via Microsoft Entra ID. Role-based access for tenant, vendor, coordinator, PM.",
    },
    {
      title: "Data retention",
      body: "Operational records kept 7 years (landlord-tenant + tax). Erasure requests honored within 30 days.",
    },
    {
      title: "AI safety",
      body: "All LLM inputs and outputs pass through guardrails: prompt-injection, PII redaction, output moderation.",
    },
    {
      title: "Encryption",
      body: "TLS in transit. Encrypted at rest in Postgres and Blob Storage. Short-lived SAS tokens for media.",
    },
    {
      title: "Audit trail",
      body: "Every state change logged with actor, timestamp, and before/after. SOC 2 Type II ready.",
    },
  ];

  items.forEach((item, i) => {
    const col = i % 3;
    const row = Math.floor(i / 3);
    const x = 0.5 + col * 4.2;
    const y = 2.3 + row * 2.2;
    s.addShape(pres.shapes.RECTANGLE, {
      x, y, w: 3.9, h: 2.0,
      fill: { color: COLORS.ice }, line: { type: "none" },
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x, y, w: 0.08, h: 2.0,
      fill: { color: COLORS.accent }, line: { type: "none" },
    });
    s.addText(item.title, {
      x: x + 0.3, y: y + 0.15, w: 3.5, h: 0.5,
      fontFace: FONT.header, fontSize: 15, color: COLORS.midnight, bold: true, margin: 0,
    });
    s.addText(item.body, {
      x: x + 0.3, y: y + 0.65, w: 3.5, h: 1.3,
      fontFace: FONT.body, fontSize: 12, color: COLORS.ink, margin: 0,
    });
  });
  addFooter(s, 10, TOTAL_SLIDES);
}

// =====================================================================
// SLIDE 11 — Success criteria (chart)
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: COLORS.white };
  addSlideTitle(s, "TARGETS", "What success looks like.");

  // Bar chart showing key targets
  s.addChart(
    pres.charts.BAR,
    [
      {
        name: "Target",
        labels: ["PM time saved", "Self-serve resolution", "Triage accuracy"],
        values: [40, 30, 98],
      },
    ],
    {
      x: 0.5, y: 2.3, w: 7.5, h: 4.5,
      barDir: "bar",
      chartColors: [COLORS.primary],
      chartArea: { fill: { color: COLORS.white } },
      catAxisLabelColor: COLORS.ink,
      catAxisLabelFontSize: 12,
      valAxisLabelColor: COLORS.muted,
      valAxisLabelFontSize: 10,
      valGridLine: { color: "E2E8F0", size: 0.5 },
      catGridLine: { style: "none" },
      showValue: true,
      dataLabelPosition: "outEnd",
      dataLabelColor: COLORS.midnight,
      dataLabelFontSize: 12,
      dataLabelFormatCode: "0\"%\"",
      showLegend: false,
      valAxisMinVal: 0,
      valAxisMaxVal: 100,
    }
  );

  // Right side: latency targets
  s.addShape(pres.shapes.RECTANGLE, {
    x: 8.4, y: 2.3, w: 4.4, h: 4.5,
    fill: { color: COLORS.ice }, line: { type: "none" },
  });
  s.addText("Latency targets", {
    x: 8.6, y: 2.45, w: 4.0, h: 0.4,
    fontFace: FONT.header, fontSize: 14, color: COLORS.midnight, bold: true, margin: 0,
  });

  const latencies = [
    { num: "< 5s", label: "AI classification first token" },
    { num: "< 5s", label: "Self-serve troubleshooting" },
    { num: "< 5min", label: "Urgent dispatch decision" },
    { num: "< 30min", label: "Routine dispatch decision" },
    { num: "< 200ms", label: "API read p95" },
  ];
  latencies.forEach((lat, i) => {
    const y = 3.0 + i * 0.7;
    s.addText(lat.num, {
      x: 8.6, y, w: 1.4, h: 0.5,
      fontFace: FONT.header, fontSize: 20, color: COLORS.primary, bold: true, margin: 0,
    });
    s.addText(lat.label, {
      x: 10.1, y: y + 0.05, w: 2.6, h: 0.5,
      fontFace: FONT.body, fontSize: 12, color: COLORS.ink, valign: "middle", margin: 0,
    });
  });

  addFooter(s, 11, TOTAL_SLIDES);
}

// =====================================================================
// SLIDE 12 — Roadmap
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: COLORS.ice };
  addSlideTitle(s, "ROADMAP", "Where we're going next.");

  const phases = [
    { num: "Q4 2026", title: "MVP launch", body: "Full vertical slice live — intake, AI triage, dispatch, estimates, analytics.", status: "current" },
    { num: "Q1 2027", title: "Native mobile apps", body: "iOS and Android apps for tenants. Push-first experience." },
    { num: "Q2 2027", title: "PMS integration", body: "AppFolio + Buildium connectors for tenant roster and unit sync." },
    { num: "Q3 2027", title: "Computer vision", body: "Multimodal damage assessment from photos. Severity scoring." },
    { num: "Q4 2027", title: "Predictive maintenance", body: "Embeddings over historical work orders. Pre-emptive vendor scheduling." },
  ];

  // Vertical timeline
  const lineX = 1.5;
  s.addShape(pres.shapes.LINE, {
    x: lineX, y: 2.4, w: 0, h: 4.2,
    line: { color: COLORS.secondary, width: 2 },
  });

  phases.forEach((phase, i) => {
    const y = 2.4 + i * 1.0;
    const isCurrent = phase.status === "current";
    const dotColor = isCurrent ? COLORS.accent : COLORS.primary;
    // Dot
    s.addShape(pres.shapes.OVAL, {
      x: lineX - 0.15, y: y + 0.15, w: 0.3, h: 0.3,
      fill: { color: dotColor }, line: { type: "none" },
    });
    // Quarter
    s.addText(phase.num, {
      x: 2.0, y, w: 2.0, h: 0.4,
      fontFace: FONT.body, fontSize: 12, color: COLORS.secondary, bold: true,
      charSpacing: 2, margin: 0,
    });
    // Title
    s.addText(phase.title, {
      x: 2.0, y: y + 0.35, w: 5, h: 0.4,
      fontFace: FONT.header, fontSize: 16, color: COLORS.midnight, bold: true, margin: 0,
    });
    // Body
    s.addText(phase.body, {
      x: 4.2, y: y + 0.4, w: 8.5, h: 0.5,
      fontFace: FONT.body, fontSize: 12, color: COLORS.ink, margin: 0,
    });
  });
  addFooter(s, 12, TOTAL_SLIDES);
}

// =====================================================================
// SLIDE 13 — Investment / call to action
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: COLORS.white };
  addSlideTitle(s, "GET INVOLVED", "Three ways to start.");

  const options = [
    {
      title: "Pilot program",
      body: "10-property, 90-day pilot. We deploy, integrate with your existing PMS, and measure time-to-dispatch improvement.",
    },
    {
      title: "Technical deep-dive",
      body: "Architecture review with your CTO and security team. Walk through the spec, constitution, and SOC 2 controls.",
    },
    {
      title: "Design partner",
      body: "Co-build a custom feature for your portfolio. Lock in founding-customer pricing and influence the roadmap.",
    },
  ];

  options.forEach((opt, i) => {
    const x = 0.5 + i * 4.2;
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: 2.3, w: 3.9, h: 3.5,
      fill: { color: COLORS.white }, line: { color: COLORS.secondary, width: 1.5 },
    });
    s.addShape(pres.shapes.RECTANGLE, {
      x, y: 2.3, w: 3.9, h: 0.6,
      fill: { color: COLORS.primary }, line: { type: "none" },
    });
    s.addText(`OPTION ${i + 1}`, {
      x, y: 2.3, w: 3.9, h: 0.6,
      fontFace: FONT.body, fontSize: 11, color: COLORS.accent, bold: true,
      charSpacing: 6, align: "center", valign: "middle", margin: 0,
    });
    s.addText(opt.title, {
      x: x + 0.3, y: 3.1, w: 3.3, h: 0.5,
      fontFace: FONT.header, fontSize: 20, color: COLORS.midnight, bold: true, margin: 0,
    });
    s.addText(opt.body, {
      x: x + 0.3, y: 3.7, w: 3.3, h: 1.9,
      fontFace: FONT.body, fontSize: 13, color: COLORS.ink, margin: 0,
    });
  });

  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.5, y: 6.1, w: 12.3, h: 0.7,
    fill: { color: COLORS.midnight }, line: { type: "none" },
  });
  s.addText("Contact: hello@fixroute.example.com  ·  fixroute.example.com  ·  +1 (555) 123-4567", {
    x: 0.5, y: 6.1, w: 12.3, h: 0.7,
    fontFace: FONT.body, fontSize: 14, color: COLORS.white,
    align: "center", valign: "middle", margin: 0,
  });
  addFooter(s, 13, TOTAL_SLIDES);
}

// =====================================================================
// SLIDE 14 — Closing
// =====================================================================
{
  const s = pres.addSlide();
  s.background = { color: COLORS.midnight };

  // Decorative motif
  s.addShape(pres.shapes.OVAL, {
    x: -2, y: 4, w: 6, h: 6,
    fill: { color: COLORS.primary, transparency: 50 }, line: { type: "none" },
  });
  s.addShape(pres.shapes.OVAL, {
    x: 10, y: -2, w: 5, h: 5,
    fill: { color: COLORS.secondary, transparency: 50 }, line: { type: "none" },
  });

  s.addShape(pres.shapes.RECTANGLE, {
    x: 0.7, y: 2.5, w: 0.6, h: 0.06,
    fill: { color: COLORS.accent }, line: { type: "none" },
  });
  s.addText("THANK YOU", {
    x: 0.7, y: 2.65, w: 12, h: 0.5,
    fontFace: FONT.body, fontSize: 14, color: COLORS.accent, bold: true,
    charSpacing: 8, margin: 0,
  });
  s.addText("Let's build the future\nof property operations.", {
    x: 0.7, y: 3.3, w: 12, h: 2.2,
    fontFace: FONT.header, fontSize: 52, color: COLORS.white, bold: true, margin: 0,
  });
  s.addText("Questions welcome.", {
    x: 0.7, y: 5.5, w: 12, h: 0.5,
    fontFace: FONT.header, fontSize: 22, color: "CADCFC", italic: true, margin: 0,
  });
}

// ---------- Save ----------
pres.writeFile({
  fileName: "/Users/rcrock1978/Documents/PROJECTS/Portfolio_016/FixRoute/docs/presentations/FixRoute-Client-Presentation.pptx",
}).then((fn) => {
  console.log("Saved:", fn);
});
