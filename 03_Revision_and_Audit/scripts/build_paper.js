// Builds the revised paper (DOCX) from paper_content.js.
// Run with NODE_PATH pointing at a folder that has the `docx` package installed.
const fs = require("fs");
const path = require("path");
const d = require("docx");
const CONTENT = process.argv[3] || "./paper_content.js";
const { AUTHORS, REFS, B, TITLE } = require(CONTENT);

const ROOT = path.resolve(__dirname, "..");
const FIG = path.join(ROOT, "figures");
const OUTFILE = process.argv[2] || path.join(ROOT, "Amani_Azimi_Manafzadeh_Narehei_Revised_Paper.docx");
const BODY = "Times New Roman", HEAD = "Arial";
const TEXT_W = 9072; // A4 width 11906 - 2 x 1417 margins (DXA)

// ---- citation numbering in order of first appearance ----
const order = [];
const allText = B.flatMap((b) => [b.text || "", b.caption || ""]).join(" ");
for (const m of allText.matchAll(/\[@([^\]]+)\]/g))
  for (const k of m[1].split(";").map((x) => x.trim().replace(/^@/, "")))
    if (!order.includes(k)) order.push(k);
for (const k of order) if (!REFS[k]) throw new Error("missing ref " + k);
const num = (k) => order.indexOf(k) + 1;

// ---- inline markup -> TextRuns ----
function runs(text, base = {}) {
  text = text.replace(/\[@([^\]]+)\]/g, (_, ks) => "[" + ks.split(";").map((x) => num(x.trim().replace(/^@/, ""))).join(", ") + "]");
  const out = [];
  const re = /(\*[^*]+\*)|(_\{[^}]+\})|(\^\{[^}]+\})/g;
  let last = 0, m;
  const push = (t, o = {}) => t && out.push(new d.TextRun({ text: t, font: base.font || BODY, size: base.size || 22, ...base.run, ...o }));
  while ((m = re.exec(text))) {
    push(text.slice(last, m.index));
    const tok = m[0];
    if (tok.startsWith("*")) push(tok.slice(1, -1), { italics: true });
    else if (tok.startsWith("_")) push(tok.slice(2, -1), { subScript: true });
    else push(tok.slice(2, -1), { superScript: true });
    last = m.index + tok.length;
  }
  push(text.slice(last));
  return out;
}

const para = (text, opts = {}) => new d.Paragraph({
  children: runs(text, opts), alignment: opts.align || d.AlignmentType.JUSTIFIED,
  spacing: { after: opts.after ?? 120, line: 276, before: opts.before ?? 0 }, keepNext: opts.keepNext,
});

// ---- equations ----
const MR = (t) => new d.MathRun(t);
const sub = (b, s) => new d.MathSubScript({ children: [MR(b)], subScript: [MR(s)] });
const EQ = {
  participation: [sub("P", "i"), MR("=1−"), new d.MathSum({ children: [new d.MathSuperScript({ children: [new d.MathRoundBrackets({ children: [new d.MathFraction({ numerator: [sub("k", "ic")], denominator: [sub("k", "i")] })] })], superScript: [MR("2")] })], subScript: [MR("c")] })],
  efficiency: [MR("E="), new d.MathFraction({ numerator: [MR("1")], denominator: [MR("N(N−1)")] }), new d.MathSum({ children: [new d.MathFraction({ numerator: [MR("1")], denominator: [sub("d", "ij")] })], subScript: [MR("i≠j")] })],
  // Equation (3): single-airport loss = own term (harmonic) + survivor damage term.
  decomposition: [MR("Δ"), sub("E", "i"), MR("="), new d.MathFraction({ numerator: [sub("H", "i")], denominator: [MR("N(N−1)")] }), MR("+"),
    new d.MathFraction({ numerator: [MR("N−2")], denominator: [MR("N")] }), sub("D", "i")],
  robustness: [sub("R", "E"), MR("="), new d.MathFraction({ numerator: [MR("1")], denominator: [MR("N")] }), new d.MathSum({ children: [new d.MathFraction({ numerator: [MR("E(q)")], denominator: [sub("E", "0")] })], subScript: [MR("q=1")], superScript: [MR("N")] })],
};
const eqPara = (id, n) => new d.Paragraph({
  tabStops: [{ type: d.TabStopType.CENTER, position: TEXT_W / 2 }, { type: d.TabStopType.RIGHT, position: TEXT_W }],
  spacing: { before: 60, after: 120 },
  children: [new d.TextRun({ text: "\t", font: BODY }), new d.Math({ children: EQ[id] }), new d.TextRun({ text: `\t(${n})`, font: BODY, size: 22 })],
});

// ---- figures ----
function pngSize(file) {
  const b = fs.readFileSync(file);
  return [b.readUInt32BE(16), b.readUInt32BE(20)];
}
function figure(file, caption, widthIn = 6.3) {
  const f = path.join(FIG, file);
  const [w, h] = pngSize(f);
  const wpx = Math.round(widthIn * 96);
  return [
    new d.Paragraph({ alignment: d.AlignmentType.CENTER, spacing: { before: 120, after: 60 }, keepNext: true,
      children: [new d.ImageRun({ type: "png", data: fs.readFileSync(f), transformation: { width: wpx, height: Math.round((wpx * h) / w) },
        altText: { title: caption.split(".")[0], description: caption, name: file } })] }),
    capPara(caption),
  ];
}
function capPara(caption, after = 200) {
  const i = caption.indexOf(". ");
  return new d.Paragraph({ alignment: d.AlignmentType.LEFT, spacing: { after, line: 252 },
    children: [...runs(caption.slice(0, i + 1), { size: 19, run: { bold: true } }), ...runs(caption.slice(i + 1), { size: 19 })] });
}

// ---- tables ----
const border = { style: d.BorderStyle.SINGLE, size: 4, color: "999999" };
const none = { style: d.BorderStyle.NONE, size: 0, color: "FFFFFF" };
function cell(text, w, opts = {}) {
  return new d.TableCell({
    width: { size: w, type: d.WidthType.DXA },
    margins: { top: 40, bottom: 40, left: 80, right: 80 },
    shading: opts.head ? { fill: "EDEDEA", type: d.ShadingType.CLEAR, color: "auto" } : undefined,
    borders: { top: opts.top ? border : none, bottom: opts.bottom ? border : none, left: none, right: none },
    children: [new d.Paragraph({ alignment: opts.first ? d.AlignmentType.LEFT : d.AlignmentType.CENTER,
      children: runs(text.replace(/K50/g, "K_{50}").replace(/RE\b/g, "R_{E}"), { font: HEAD, size: 17, run: opts.head ? { bold: true } : {} }) })],
  });
}
function makeTable(t) {
  const total = t.widths.reduce((a, b) => a + b, 0);
  const rows = [new d.TableRow({ tableHeader: true, children: t.header.map((h, j) => cell(h, t.widths[j], { head: true, first: j === 0, top: true, bottom: true })) })];
  t.rows.forEach((r, i) => rows.push(new d.TableRow({ cantSplit: true, children: r.map((c, j) => cell(c, t.widths[j], { first: j === 0, bottom: i === t.rows.length - 1 })) })));
  return [
    capPara(t.caption.replace(/K50/g, "K_{50}").replace(/RE is/g, "R_{E} is"), 80),
    new d.Table({ width: { size: total, type: d.WidthType.DXA }, columnWidths: t.widths, rows, alignment: d.AlignmentType.CENTER }),
    new d.Paragraph({ spacing: { after: 160 }, children: [] }),
  ];
}

// ---- assemble ----
const children = [];
children.push(new d.Paragraph({ heading: d.HeadingLevel.TITLE, alignment: d.AlignmentType.CENTER, spacing: { after: 200 },
  children: [new d.TextRun({ text: TITLE || "Structural Resilience and Hub Dependence in US Airline Networks", font: HEAD, size: 34, bold: true })] }));
AUTHORS.forEach((a, i) => children.push(new d.Paragraph({ alignment: d.AlignmentType.CENTER, spacing: { after: i === AUTHORS.length - 1 ? 240 : 0 },
  children: [new d.TextRun({ text: a, font: BODY, size: 21 })] })));
for (const b of B) {
  if (b.type === "abstract") {
    children.push(new d.Paragraph({ spacing: { after: 60 }, children: [new d.TextRun({ text: "Abstract", font: HEAD, size: 22, bold: true })] }));
    children.push(new d.Paragraph({ alignment: d.AlignmentType.JUSTIFIED, indent: { left: 400, right: 400 }, spacing: { after: 240, line: 264 }, children: runs(b.text, { size: 20 }) }));
  } else if (b.type === "h1") children.push(new d.Paragraph({ heading: d.HeadingLevel.HEADING_1, children: [new d.TextRun({ text: b.text })] }));
  else if (b.type === "h2") children.push(new d.Paragraph({ heading: d.HeadingLevel.HEADING_2, children: [new d.TextRun({ text: b.text })] }));
  else if (b.type === "p") children.push(para(b.text));
  else if (b.type === "bullet") children.push(new d.Paragraph({ numbering: { reference: "bul", level: 0 }, alignment: d.AlignmentType.LEFT, spacing: { after: 60, line: 264 }, children: runs(b.text) }));
  else if (b.type === "eq") children.push(eqPara(b.id, b.n));
  else if (b.type === "fig") children.push(...figure(b.file, b.caption, b.width));
  else if (b.type === "table") children.push(...makeTable(b));
}
if (order.length) children.push(new d.Paragraph({ heading: d.HeadingLevel.HEADING_1, children: [new d.TextRun({ text: "References" })] }));
order.forEach((k, i) => children.push(new d.Paragraph({ alignment: d.AlignmentType.LEFT, indent: { left: 440, hanging: 440 }, spacing: { after: 80, line: 252 },
  children: [new d.TextRun({ text: `[${i + 1}]\t${REFS[k]}`, font: BODY, size: 19 })], tabStops: [{ type: d.TabStopType.LEFT, position: 440 }] })));

const doc = new d.Document({
  numbering: { config: [{ reference: "bul", levels: [{ level: 0, format: d.LevelFormat.BULLET, text: "•", alignment: d.AlignmentType.LEFT, style: { paragraph: { indent: { left: 400, hanging: 260 } } } }] }] },
  creator: "Amani, Azimi, Manafzadeh, Narehei",
  title: "Structural Resilience and Hub Dependence in US Airline Networks",
  styles: {
    default: { document: { run: { font: BODY, size: 22 } } },
    paragraphStyles: [
      { id: "Title", name: "Title", basedOn: "Normal", run: { font: HEAD, size: 34, bold: true }, paragraph: { spacing: { before: 0, after: 200 }, keepNext: true } },
      { id: "Heading1", name: "Heading 1", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: HEAD, size: 26, bold: true, color: "1F1F1F" }, paragraph: { spacing: { before: 280, after: 120 }, keepNext: true, outlineLevel: 0 } },
      { id: "Heading2", name: "Heading 2", basedOn: "Normal", next: "Normal", quickFormat: true, run: { font: HEAD, size: 22, bold: true, color: "333333" }, paragraph: { spacing: { before: 200, after: 80 }, keepNext: true, outlineLevel: 1 } },
    ],
  },
  sections: [{
    properties: { page: { size: { width: 11906, height: 16838 }, margin: { top: 1417, bottom: 1417, left: 1417, right: 1417 } } },
    footers: { default: new d.Footer({ children: [new d.Paragraph({ alignment: d.AlignmentType.CENTER, children: [new d.TextRun({ children: [d.PageNumber.CURRENT], font: BODY, size: 18 })] })] }) },
    children,
  }],
});

d.Packer.toBuffer(doc).then((buf) => {
  fs.writeFileSync(OUTFILE, buf);
  const words = B.filter((b) => ["p", "abstract"].includes(b.type)).map((b) => b.text.replace(/\[@[^\]]+\]/g, "[1]").split(/\s+/).filter(Boolean).length);
  console.log("written", OUTFILE, "| refs", order.length, "| body words (abstract + text)", words.reduce((a, b) => a + b, 0), "| abstract", words[0]);
});
