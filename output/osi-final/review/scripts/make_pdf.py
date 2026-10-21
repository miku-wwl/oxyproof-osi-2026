"""Create a single A4 scientific presentation page from reviewed project evidence."""
from pathlib import Path
from xml.sax.saxutils import escape
from reportlab.pdfgen import canvas
from reportlab.lib.pagesizes import A4
from reportlab.lib.colors import HexColor, white
from reportlab.lib.styles import ParagraphStyle
from reportlab.platypus import Paragraph
from pypdf import PdfReader

OUT = Path(__file__).resolve().parents[2]
pdf = OUT / "submission/oxyproof-one-page-final.pdf"
c = canvas.Canvas(str(pdf), pagesize=A4, pageCompression=1, invariant=1)
c.setTitle("OxyProof - When the Best Material Changes, Can Your AI Explain Why?")
c.setAuthor("OxyProof project")
W, H = A4
ink, teal = HexColor("#173b43"), HexColor("#147977")
def text(x, y, value, size=10, bold=False, color=ink):
    c.setFillColor(color); c.setFont("Helvetica-Bold" if bold else "Helvetica", size)
    c.drawString(x, y, value)
def para(x, top, width, value, size=9.1, leading=12, color=ink):
    style=ParagraphStyle("p",fontName="Helvetica",fontSize=size,leading=leading,textColor=color)
    p=Paragraph(value, style); _, h=p.wrap(width, 1000)
    p.drawOn(c,x,top-h); return top-h
def label(y, value):
    text(32,y,value.upper(),9.2,True,teal)

c.setFillColor(ink); c.rect(0,H-110,W,110,fill=1,stroke=0)
text(32,H-39,"OxyProof",30,True,white)
text(32,H-61,"Temperature-Aware, Evidence-Grounded Materials Decision Agent",12,True,white)
para(32,H-74,W-64,"When the best material changes, can your AI explain why?<br/>"
     "Published evidence + bounded AI tools + deterministic physics + independent auditing.",
     10.1,14,white)
label(H-132,"The research decision")
para(32,H-142,W-64,"A shortlist at one operating temperature can hide a different choice across an operating range. "
     "OxyProof makes the ranking, its fitted model and the missing evidence inspectable.",9.6,13)
label(H-185,"Flagship result | conditional model ranking reversal")
c.drawImage(str(OUT/"review/flagship-conductivity.png"),25,H-412,width=W-50,height=219,mask="auto")
para(32,H-416,W-64,"<b>Same curated source group:</b> bulk, two-probe AC, 600-1100 K; Huang et al. (1998), Table 3 as curated by Jang et al. "
     "Solid branches are fitted-model calculations; dashed lines are curated T* boundaries. Exact T* is withheld.",8.5,11)
para(32,H-452,W-64,"<b>Rows 1 / 2 / 3:</b> La0.95Sr0.05Ga0.95Mg0.05O2.95 / La0.95Sr0.05Ga0.9Mg0.1O2.925 / "
     "La0.95Sr0.05Ga0.85Mg0.15O2.9. Analytical intersections: approximately <b>776, 818, 854 K</b>.",8.2,11)
para(32,H-484,W-64,"<b>Model-derived intersections, not measured crossovers. Uncertainty bounds unavailable.</b>",9,12,teal)
label(H-513,"Four layers that keep AI claims bounded")
para(32,H-524,W-64,"<b>1. Plan:</b> DeepSeek selects an allowlisted scientific tool. "
     "<b>2. Validate:</b> independent guards retain constraints and reject unsupported requirements. "
     "<b>3. Calculate:</b> sigma = A/T exp[-Ea/(kB T)]; Ea meV to eV, A K S/cm, T K, output S/cm. "
     "<b>4. Audit:</b> conditional ordering, source rows, regimes, warnings and code fingerprints survive JSON export.",9,12)
label(H-589,"Evidence | recorded runs, bounded claims")
para(32,H-600,W-64,"<b>3/3 genuine DeepSeek scenarios</b> (21 Oct 2026): screening, interval analysis and constraint abstention. "
     "Video shows labelled replay; no new inference. <b>49/49 targeted integrity cases</b> and <b>21 Chromium E2E tests</b> "
     "reported passed in retained artifacts. These selected checks are not general scientific accuracy. "
     "Full pinned dataset: <b>483 records</b>; offline analysis needs no model service.",9,12)
label(H-666,"Where the evidence stops")
para(32,H-677,W-64,"Original row-specific atmosphere, preparation, density and full methods/Table 3 remain unverified. "
     "No validated fit uncertainties, humidity tolerance or 10,000-hour lifetime. Unsupported conditions cause abstention. "
     "No new material, experiment or industrial performance is claimed.",8.7,11.5)
c.setStrokeColor(HexColor("#d2dddd")); c.line(32,95,W-32,95)
para(32,87,W-64,"<b>Code:</b> <link href='https://github.com/miku-wwl/oxyproof-osi-2026' color='#147977'>github.com/miku-wwl/oxyproof-osi-2026</link><br/>"
     "<b>Data:</b> Jang et al. (2026), Zenodo v1, CC BY 4.0: <link href='https://doi.org/10.5281/zenodo.18947543'>10.5281/zenodo.18947543</link><br/>"
     "<b>Method:</b> <link href='https://www.nature.com/articles/s41597-026-07100-x'>Scientific Data: s41597-026-07100-x</link> | "
     "<b>Original source:</b> <link href='https://doi.org/10.1111/j.1151-2916.1998.tb02662.x'>10.1111/j.1151-2916.1998.tb02662.x</link><br/>"
     "<b>Video:</b> [PUBLIC VIDEO URL - owner upload pending]. Sources verified 20 Oct; review 21 Oct 2026.<br/>"
     "Public repository available. New submission assets are local. Competition entry not submitted.",7.7,10)
c.showPage(); c.save()
reader=PdfReader(pdf)
assert len(reader.pages)==1
assert abs(float(reader.pages[0].mediabox.width)-W)<.1
print(f"PDF=PASS pages=1 A4 bytes={pdf.stat().st_size}; visual review still required")
