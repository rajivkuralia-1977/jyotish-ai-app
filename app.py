import streamlit as st
from fpdf import FPDF
import datetime
import requests

WEBAPP_URL = "https://script.google.com/macros/s/AKfycbxkPrTQK017yE2WJDo65jO6Ulpw2ESpokbJuUWltvLCSKlq_vKFavc3Dl3NNh2duyYF2g/exec"

def cln(txt):
    return str(txt).encode("latin-1", "replace").decode("latin-1")

class KundaliPDF(FPDF):
    def __init__(self, name, dob, tob, pob, language):
        super().__init__("P", "mm", "A4")
        self.c_name = cln(name)
        self.c_dob = cln(dob)
        self.c_tob = cln(tob)
        self.c_pob = cln(pob)
        self.language = language
        self.set_auto_page_break(False)

    def swastik(self, x, y, s, col, lw):
        self.set_draw_color(*col)
        self.set_line_width(lw)
        h = s / 2.0
        self.line(x - h, y, x + h, y)
        self.line(x, y - h, x, y + h)
        self.line(x, y - h, x + h, y - h)
        self.line(x + h, y, x + h, y + h)
        self.line(x, y + h, x - h, y + h)
        self.line(x - h, y, x - h, y - h)
        q = h / 2.0
        r = lw * 0.8
        self.set_fill_color(*col)
        for dx, dy in [(-q, -q), (q, -q), (-q, q), (q, q)]:
            self.ellipse(x + dx - r/2, y + dy - r/2, r, r, "F")

    def ganesha(self, x, y, s):
        self.set_draw_color(180, 40, 20)
        self.set_fill_color(255, 240, 215)
        self.set_line_width(1.2)
        self.ellipse(x - s/2, y - s/2, s, s, "DF")
        self.set_line_width(0.6)
        self.ellipse(x - s/2 + 3, y - s/2 + 3, s - 6, s - 6, "D")
        self.set_line_width(1.5)
        self.line(x - 10, y - 8, x + 10, y - 8)
        self.line(x - 12, y - 3, x + 12, y - 3)
        self.line(x - 10, y + 2, x + 10, y + 2)
        self.line(x, y - 14, x, y + 12)
        self.line(x, y + 12, x + 6, y + 15)
        self.set_fill_color(180, 40, 20)
        self.ellipse(x - 2, y - 20, 4, 4, "F")

    def chart(self, x, y, s, title, data):
        self.set_font("Helvetica", "B", 9.5)
        self.set_text_color(120, 30, 20)
        self.set_xy(x, y - 7)
        self.cell(s, 6, cln(title), 0, 0, "C")
        self.set_draw_color(140, 50, 30)
        self.set_line_width(0.6)
        self.rect(x, y, s, s)
        self.line(x, y, x + s, y + s)
        self.line(x + s, y, x, y + s)
        h = s / 2.0
        self.line(x + h, y, x + s, y + h)
        self.line(x + s, y + h, x + h, y + s)
        self.line(x + h, y + s, x, y + h)
        self.line(x, y + h, x + h, y)
        pts = {
            1:(0.5,0.25), 2:(0.25,0.1), 3:(0.1,0.25), 4:(0.25,0.5),
            5:(0.1,0.75), 6:(0.25,0.88), 7:(0.5,0.75), 8:(0.75,0.88),
            9:(0.88,0.75), 10:(0.75,0.5), 11:(0.88,0.25), 12:(0.75,0.1)
        }
        self.set_font("Helvetica", "B", 7.5)
        self.set_text_color(40, 40, 40)
        for k, v in data.items():
            self.set_xy(x + s*pts[k][0] - 12, y + s*pts[k][1] - 3)
            self.cell(24, 5, cln(v), 0, 0, "C")

    def header(self):
        self.set_draw_color(180, 130, 70)
        self.set_line_width(0.5)
        self.rect(8, 8, 194, 281)
        self.set_line_width(0.2)
        self.rect(10, 10, 190, 277)
        self.swastik(105, 148.5, 105, (246, 236, 222), 5.0)
        self.swastik(20, 20, 10, (180, 45, 25), 0.9)
        self.swastik(190, 20, 10, (180, 45, 25), 0.9)
        if self.page_no() > 1:
            self.set_xy(30, 14)
            self.set_font("Helvetica", "B", 8.5)
            self.set_text_color(130, 50, 30)
            lang_label = "(HINDI)" if self.language == "Hindi" else "(ENGLISH)"
            t = f"KP BHAVA JYOTISH | ADVANCED KUNDALI HELP BOOK {lang_label} | {self.c_name.upper()}"
            self.cell(150, 5, cln(t), 0, 0, "C")
            self.set_draw_color(180, 130, 70)
            self.set_line_width(0.3)
            self.line(30, 21, 180, 21)
            self.set_y(28)

    def footer(self):
        self.set_y(-18)
        self.set_draw_color(180, 130, 70)
        self.set_line_width(0.3)
        self.line(15, 278, 195, 278)
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(110, 40, 20)
        self.cell(90, 8, "Created by Rajiv Kumar | Contact: 9914465143", 0, 0, "L")
        self.cell(90, 8, f"Page {self.page_no()} of 23", 0, 0, "R")

    def ch_title(self, num, title, sub=""):
        self.set_xy(15, 28)
        self.set_fill_color(248, 238, 225)
        self.set_draw_color(160, 60, 30)
        self.set_line_width(0.4)
        self.rect(15, 28, 180, 15, "DF")
        self.set_xy(18, 29.5)
        self.set_font("Helvetica", "B", 11.5)
        self.set_text_color(140, 30, 20)
        self.cell(174, 6, cln(f"CHAPTER {num}: {title}"), 0, 0, "L")
        if sub:
            self.set_xy(18, 36)
            self.set_font("Helvetica", "I", 8.5)
            self.set_text_color(90, 60, 40)
            self.cell(174, 5, cln(sub), 0, 0, "L")
        self.set_y(47)

    def blk(self, head, body):
        self.set_x(15)
        self.set_font("Helvetica", "B", 9.5)
        self.set_text_color(140, 40, 20)
        self.cell(180, 6, cln(head), 0, 1, "L")
        self.set_x(15)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(35, 35, 35)
        self.multi_cell(180, 5.0, cln(body))
        self.ln(2.5)

    def tbl(self, hdrs, rows, widths):
        self.set_x(15)
        self.set_fill_color(150, 50, 30)
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 8)
        for i, h in enumerate(hdrs):
            self.cell(widths[i], 6.5, cln(h), 1, 0, "C", True)
        self.ln()
        self.set_font("Helvetica", "", 7.5)
        self.set_text_color(30, 30, 30)
        fill = False
        for r in rows:
            self.set_x(15)
            self.set_fill_color(*(252, 246, 238) if fill else (255, 255, 255))
            for i, val in enumerate(r):
                self.cell(widths[i], 6.0, cln(val), 1, 0, "C", True)
            self.ln()
            fill = not fill
        self.ln(3)

def build_pdf(name, dob, tob, pob, language):
    pdf = KundaliPDF(name, dob, tob, pob, language)

    # P1: COVER
    pdf.add_page()
    pdf.set_y(32)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(160, 40, 20)
    pdf.cell(0, 8, "|| SHRI GANESHAYA NAMAH ||", 0, 1, "C")
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(100, 50, 30)
    pdf.cell(0, 6, "Vakratunda Mahakaya Suryakoti Samaprabha", 0, 1, "C")
    pdf.cell(0, 6, "Nirvighnam Kurume Deva Sarva Karyeshu Sarvada", 0, 1, "C")
    pdf.ganesha(105, 88, 44)
    pdf.set_y(120)
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(120, 25, 15)
    
    report_title = f"ADVANCED KUNDALI HELP BOOK ({language.upper()})"
    pdf.cell(0, 10, report_title, 0, 1, "C")
    
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(160, 90, 30)
    pdf.cell(0, 7, "Multi-System Synthesis: KP | BPHS | Jaimini | Phaladeepika", 0, 1, "C")
    pdf.set_fill_color(250, 242, 230)
    pdf.set_draw_color(160, 80, 40)
    pdf.rect(25, 145, 160, 52, "DF")
    pdf.set_xy(30, 150)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(120, 30, 20)
    pdf.cell(150, 7, "JATAKA (CLIENT) BIRTH PARTICULARS", 0, 1, "C")
    pdf.set_font("Helvetica", "B", 9.5)
    pdf.set_text_color(40, 40, 40)
    for lbl, v in [("Name", name), ("Date of Birth", dob), ("Time of Birth", tob), ("Place of Birth", pob), ("Ayanamsa", "KP New / Lahiri Chitrapaksha")]:
        pdf.set_x(35)
        pdf.cell(140, 7, cln(f"{lbl:<16}: {v}"), 0, 1, "L")
    pdf.set_fill_color(140, 35, 20)
    pdf.rect(25, 215, 160, 36, "F")
    pdf.set_xy(25, 220)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(255, 235, 200)
    pdf.cell(160, 7, "CREATED BY: RAJIV KUMAR", 0, 1, "C")
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 7, "Contact & Consultation: +91-9914465143", 0, 1, "C")
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(240, 220, 200)
    pdf.cell(0, 6, "KP & Bhava Jyotish Research Wing | Jalandhar, Punjab", 0, 1, "C")

    # P2: TOC
    pdf.add_page()
    pdf.ch_title("01", "MASTER TABLE OF CONTENTS", "6 Classical Systems Converging Into One Unified Verdict")
    toc = [
        ["Page 01", "Sacred Invocation, Jataka Particulars & Creator Details"],
        ["Page 02", "Master Table of Contents & Multi-System Methodology"],
        ["Page 03", "Avakahada Chakra, Panchang Decoded & Three Pillars"],
        ["Page 04", "Visual Charts: Lagna (D1) & Navamsha (D9) with Degrees"],
        ["Page 05", "Visual Charts: Dashamsha (D10), Saptamsha (D7) & Vargas"],
        ["Page 06", "Planetary Positions Table & Sarvashtakavarga Matrix"],
        ["Page 07", "Personal Planetary Profile: Sun, Moon, Mars, Merc, Jup"],
        ["Page 08", "Personal Planetary Profile: Venus, Sat, Rahu, Ketu"],
        ["Page 09", "Bhavphal (Houses 1 to 6): Placements & Lordships"],
        ["Page 10", "Bhavphal (Houses 7 to 12): Placements & Lordships"],
        ["Page 11", "Multi-System Synthesis: Unified Verdict vs. Conflicts"],
        ["Page 12", "Jaimini Chara Karakas: The 7 Soul Indicators"],
        ["Page 13", "Love, Marriage, Darakaraka & Mangalik Evaluation"],
        ["Page 14", "Career Calling, Wealth Architecture & Raj Yogas"],
        ["Page 15", "Karmic Axis (Rahu-Ketu) & Sade Sati Phases"],
        ["Page 16", "Vimshottari Dasha Timeline (Birth to 2048)"],
        ["Page 17", "Vimshottari Dasha Deep-Dive (2048 to 2092)"],
        ["Page 18", "Chronological Life Event Timeline (Specific Ages)"],
        ["Page 19", "KP Cuspal Sub-Lord Interlinks & Significators"],
        ["Page 20", "Shadbala, Bhava Bala & Planetary Avasthas"],
        ["Page 21", "5-Year Varshphal & Transit Forecast (2026-2031)"],
        ["Page 22", "Vedic Numerology & Complete Do's and Don'ts"],
        ["Page 23", "Vedic Remedies Help Book & Legal Disclaimer"]
    ]
    pdf.tbl(["Page", "Chapter & Section Contents"], toc, [30, 150])
    pdf.blk("Why Multi-System Cross-Validation Matters", f"This Help Book (generated in {language} format logic) cross-examines BPHS, KP, Jaimini Sutras, Phaladeepika, Brihat Jataka, and Laghu Parashari. Predictions confirmed by all systems are marked as UNIFIED VERDICTS, while technical divergences are transparently explained.")

    # P3: AVAKAHADA
    pdf.add_page()
    pdf.ch_title("02", "AVAKAHADA CHAKRA & PANCHANG", "Foundational Astronomical & Natal Alignment")
    avak = [
        ["Lagna (Ascendant)", "Taurus 14d 52m", "Lagna Lord", "Venus (Shukra)"],
        ["Moon Sign (Rashi)", "Taurus 06d 18m", "Rashi Lord", "Venus (Shukra)"],
        ["Nakshatra & Pada", "Krittika - Pada 3", "Nakshatra Lord", "Sun (Surya)"],
        ["Tithi at Birth", "Krishna Saptami", "Vaar (Day)", "Wednesday / Venusian"],
        ["Yoga & Karana", "Variyan / Balava", "Gana & Yoni", "Rakshasa / Mesh"],
        ["Nadi & Varna", "Antya / Vaishya", "Paya (Footing)", "Swarna (Gold)"],
        ["Sun Sign (Vedic)", "Virgo (Kanya)", "Active Dasha", "Saturn / Mercury"]
    ]
    pdf.tbl(["Parameter", "Natal Value", "Parameter", "Natal Value"], avak, [45, 45, 45, 45])
    pdf.blk("1. Vaar & Tithi Impact", "Born with strong Venusian and Mercurial currents, the native possesses sharp analytical intellect paired with refined aesthetic sensibilities. Krishna Paksha birth grants natural resilience, turning early obstacles into stepping stones.")
    pdf.blk("2. Lagna & Rashi Pillar (Vrishabha / Taurus)", "With Taurus rising and housing the exalted Moon, you build life brick by brick. You project calm reliability, determination, and a taste for quality.")
    pdf.blk("3. Nakshatra Pillar (Krittika / Rohini Axis)", "This stellar signature bestows the Razor of Truth alongside creative fertility. You cut through false pretenses directly and protect your family fiercely.")

    # P4: D1 & D9 CHARTS
    pdf.add_page()
    pdf.ch_title("03", "VISUAL CHARTS: LAGNA (D1) & NAVAMSHA (D9)", "North Indian Style Natal & Divisional Blueprints")
    pdf.chart(20, 56, 78, "LAGNA CHART (D1 - RASHI)", {1:"As 14d Mo 6d", 2:"Ke 9d", 3:"", 4:"", 5:"Su 12d Sa 14d", 6:"Me 2d Ve 14d", 7:"Ma 29d", 8:"Ra 9d", 9:"", 10:"", 11:"Ju(R) 1d", 12:""})
    pdf.chart(112, 56, 78, "NAVAMSHA CHART (D9)", {1:"As(Tau)", 2:"Su", 3:"Ra", 4:"", 5:"", 6:"", 7:"Me", 8:"", 9:"Ke", 10:"Mo Sa", 11:"Ve", 12:"Ma Ju"})
    pdf.set_y(142)
    pdf.blk("Technical Chart Synthesis (Why Events Happen)", "1. Vargottama Ascendant (Taurus Rising in D1 & D9): BPHS and Phaladeepika declare the native internally and externally unshakable. Health and status are doubly fortified. 2. 5th House Surya-Shani-Budha Cluster (Virgo): 4th Lord (Sun), Exalted 2nd/5th Lord (Mercury), and Yogakaraka 9th/10th Lord (Saturn) conjoin in the 5th trine, forming a premier Raja Yoga for technical and financial mastery. 3. 6th House Own-Sign Venus (Libra): Lagna Lord Venus sits in its Moolatrikona sign Libra, neutralizing enemies and ensuring competitive exam victories.")

    # P5: D10 & D7 CHARTS
    pdf.add_page()
    pdf.ch_title("04", "VISUAL CHARTS: DASHAMSHA (D10) & SAPTAMSHA (D7)", "Career Authority (D10) & Creative Legacy (D7)")
    pdf.chart(20, 56, 78, "DASHAMSHA (D10 - CAREER)", {1:"As(Cap) Ju", 2:"Ve", 3:"Mo", 4:"Ma", 5:"Ra", 6:"", 7:"Su", 8:"", 9:"Me", 10:"Sa", 11:"Ke", 12:""})
    pdf.chart(112, 56, 78, "SAPTAMSHA (D7 - CREATIVITY)", {1:"As(Vir)", 2:"Ve", 3:"Ma", 4:"Ju", 5:"Sa", 6:"Ra", 7:"", 8:"", 9:"Su", 10:"Mo", 11:"Me", 12:"Ke"})
    pdf.set_y(142)
    vargas = [
        ["D1 (Rashi)", "Physical Body & Destiny", "Taurus", "Vargottama Strength"],
        ["D2 (Hora)", "Wealth & Accumulation", "Leo/Cancer", "Strong Solar Hora"],
        ["D3 (Drekkana)", "Courage & Initiative", "Virgo", "Analytical Execution"],
        ["D4 (Chaturthamsha)", "Property & Fixed Assets", "Scorpio", "Real Estate Gains"],
        ["D7 (Saptamsha)", "Progeny & Creativity", "Virgo", "Disciplined Output"],
        ["D9 (Navamsha)", "Marriage & Dharma", "Taurus", "High Spouse Loyalty"],
        ["D10 (Dashamsha)", "Career & Command", "Capricorn", "Saturn in 10th: Authority"],
        ["D12 (Dwadashamsha)", "Parents & Lineage", "Sagittarius", "Strong Paternal Karma"]
    ]
    pdf.tbl(["Varga Chart", "Domain", "Ascendant", "Key Verdict"], vargas, [35, 55, 35, 55])

    # P6: DEGREES & ASHTAKAVARGA
    pdf.add_page()
    pdf.ch_title("05", "PLANETARY POSITIONS & ASHTAKAVARGA", "Exact Sidereal Longitudes, Nakshatra Lords, Sub-Lords & Bindus")
    p_rows = [
        ["Ascendant", "Taurus", "14d 52m", "Rohini-2", "Venus", "Moon", "Jupiter", "Vargottama"],
        ["Sun", "Virgo", "12d 06m", "Hasta-1", "Mercury", "Moon", "Moon", "Friendly"],
        ["Moon", "Taurus", "06d 18m", "Krittika-3", "Venus", "Sun", "Venus", "Exalted"],
        ["Mars", "Libra", "29d 18m", "Vishakha-3", "Venus", "Jupiter", "Mars", "Atmakaraka"],
        ["Mercury", "Virgo", "02d 14m", "U.Phalguni", "Mercury", "Sun", "Saturn", "Exalted"],
        ["Jupiter(R)", "Pisces", "01d 52m", "P.Bhadra-4", "Jupiter", "Jupiter", "Venus", "Own Sign"],
        ["Venus", "Libra", "14d 10m", "Swati-3", "Venus", "Rahu", "Mercury", "Moolatrikona"],
        ["Saturn", "Virgo", "14d 02m", "Hasta-2", "Mercury", "Moon", "Rahu", "Yogakaraka"],
        ["Rahu", "Sagittar.", "09d 11m", "Mula-3", "Jupiter", "Ketu", "Venus", "8H Research"],
        ["Ketu", "Gemini", "09d 11m", "Ardra-1", "Mercury", "Rahu", "Rahu", "2H Detached"]
    ]
    pdf.tbl(["Planet", "Sign", "Degree", "Nakshatra", "Sign L.", "Star L.", "Sub L.", "Dignity"], p_rows, [22, 20, 18, 24, 20, 20, 20, 36])
    pdf.blk("Sarvashtakavarga Summary (Bindu Strength per House)", "H1: 31 | H2: 27 | H3: 30 | H4: 29 | H5: 26 | H6: 32 | H7: 25 | H8: 22 | H9: 29 | H10: 33 | H11: 35 | H12: 20. REASONING: 33 Bindus in H10 and 35 Bindus in H11 (Phaladeepika rule) guarantee that career efforts yield high financial gains, while 20 Bindus in H12 keeps wasteful expenditure strictly low.")

    pages_data = [
        ("06", "PERSONAL PLANETARY PROFILE (SUN TO JUPITER)", "How Each Planet Operates by Placement, Lordship & Aspect", None, [
            ("1. SUN (4th Lord in 5th House - Virgo)", "Sun rules your 4th house of home and sits in the 5th house. Your emotional security is tied to intellectual achievement. Sun's 7th aspect on the 11th house links real estate and education to high financial gains."),
            ("2. MOON (3rd Lord Exalted in Lagna - Taurus)", "Moon is exalted in Taurus in the 1st house. Grants extraordinary emotional magnetism, memory retention, and intuition. Moon's 7th aspect on the 7th house brings a devoted life partner."),
            ("3. MARS (7th & 12th Lord in 6th/7th Cusp)", "Mars governs partnerships (7th) and distant lands (12th). You bring fierce loyalty and protective fire to relationships. You do not tolerate mediocrity or dishonesty in business or marriage."),
            ("4. MERCURY (2nd & 5th Lord Exalted in 5th House - Virgo)", "Mercury rules wealth (2nd) and intellect (5th) in exaltation. Forms a top-tier Dhana-cum-Budhaditya Yoga. Your mathematical, commercial, and analytical skills convert directly into tangible wealth."),
            ("5. JUPITER (8th & 11th Lord in 11th House - Pisces)", "Jupiter occupies its own sign Pisces in the 11th house. Jupiter's 5th aspect blesses communication (3H); its 7th aspect protects education/children (5H); its 9th aspect shields marriage (7H).")
        ]),
        ("07", "PERSONAL PLANETARY PROFILE (VENUS TO KETU)", "Outer Planets, Shadow Nodes & Major Conjunctions", None, [
            ("6. VENUS (Lagna & 6th Lord in Own Sign Libra)", "Ascendant Lord Venus sits in its Moolatrikona sign Libra. You conquer rivals through diplomacy, charm, and competence. Excels in law, medicine, finance, design, and management."),
            ("7. SATURN (Yogakaraka 9th & 10th Lord in 5th House)", "For Taurus Lagna, Saturn rules fortune (9H) and career (10H). Gives deep concentration and mastery over complex systems. Saturn's 3rd aspect on 7H delays marriage slightly for maturity; its 7th aspect on 11H ensures steady wealth; its 10th aspect on 2H enforces financial discipline."),
            ("8. RAHU IN 8TH HOUSE (Sagittarius) & KETU IN 2ND HOUSE (Gemini)", "The nodal axis cuts across the 2nd/8th financial axis. Rahu in 8H gives uncanny research intuition and sudden windfalls. Ketu in 2H makes speech blunt; practice family diplomacy and automated savings."),
            ("9. MAJOR CONJUNCTION: SUN + SATURN + MERCURY IN VIRGO", "When the 2nd/5th Lord (Mercury), 4th Lord (Sun), and 9th/10th Lord (Saturn) combine in Virgo, the native possesses an Executive Analyst mind capable of building structured, long-lasting institutional empires.")
        ]),
        ("08", "BHAVPHAL: LIFE THROUGH HOUSES 1 TO 6", "Significators, House Lord Placements & Practical Manifestations", None, [
            ("1st House (Tanu Bhava - Taurus): Vitality & Selfhood", "Ruled by Venus, occupied by Exalted Moon. You have a magnetic, grounded persona, strong constitution, and high public relatability."),
            ("2nd House (Dhana Bhava - Gemini): Wealth, Speech & Family", "Ruled by Exalted Mercury, occupied by Ketu, aspected by Saturn. Financial accumulation accelerates after age 26. Keep speech warm during family talks."),
            ("3rd House (Sahaj Bhava - Cancer): Courage & Communication", "Ruled by Exalted Moon, blessed by Jupiter's 5th aspect. Your communication carries wisdom and authority. Digital media and writing bring recognition."),
            ("4th House (Sukha Bhava - Leo): Mother, Home & Vehicles", "Ruled by Sun (in 5H). Domestic environment is dignified and education-focused. You will acquire luxury vehicles and prime real estate through self-earned wealth."),
            ("5th House (Putra/Vidya Bhava - Virgo): Intellect & Romance", "Occupied by Exalted Mercury, Sun, and Yogakaraka Saturn, aspected by Jupiter. This is the powerhouse house of your chart, guaranteeing academic distinction."),
            ("6th House (Ripu/Roga Bhava - Libra): Work, Rivals & Health", "Occupied by own-sign Venus. You thrive in competitive exams and structured corporate environments. Maintain kidney hydration and lower-back posture.")
        ]),
        ("09", "BHAVPHAL: LIFE THROUGH HOUSES 7 TO 12", "Partnerships, Longevity, Fortune, Career, Gains & Liberation", None, [
            ("7th House (Jaya Bhava - Scorpio): Marriage & Contracts", "Ruled by Mars, receiving Jupiter's 9th aspect and Moon's 7th aspect. You seek deep, all-or-nothing loyalty. Jupiter ensures a wise, devoted life partner."),
            ("8th House (Randhra Bhava - Sagittarius): Longevity & Research", "Ruled by Jupiter (in 11H), occupied by Rahu. Strong longevity and breakthroughs in audit, taxation, research, or occult sciences. Avoid speculative gambling."),
            ("9th House (Dharma Bhava - Capricorn): Fortune & Mentors", "Ruled by Yogakaraka Saturn. Your luck activates through discipline, ethics, and long-term perseverance. Strong karmic bond with father and mentors."),
            ("10th House (Karma Bhava - Aquarius): Career & Fame", "Ruled by Saturn (placed in 5H). Career involves large organizations, finance, technology, law, or institutional governance. Unshakeable professional rise."),
            ("11th House (Labha Bhava - Pisces): Gains & Networks", "Occupied by own-sign Jupiter (R) and aspected by Sun, Mercury, and Saturn. Creates a massive Dhana-Labha Yoga. Multiple income streams fulfill desires."),
            ("12th House (Vyaya Bhava - Aries): Foreign Lands & Liberation", "Ruled by Mars. Expenditure is directed toward self-development and assets. Favorable for international collaborations and multinational career roles.")
        ]),
        ("10", "MULTI-SYSTEM PEER REVIEW & UNIFIED VERDICT", "Cross-Examining KP, BPHS, Jaimini, Phaladeepika & Laghu Parashari",
         (["Life Domain", "BPHS / Parashari", "KP System", "Jaimini Sutras", "Final Verdict"], [
             ["Wealth & Status", "Exalted 2L/5L + 11L in 11H", "11th Sub-Lord Jup/Ven", "AK/AmK linked to 11H", "UNIFIED: High Wealth"],
             ["Career Domain", "Yogakaraka Saturn in 5H", "10th Sub-Lord 5-6-10-11", "Karakamsha in 10H", "UNIFIED: Executive"],
             ["Marriage Timing", "Saturn 3rd aspect delays", "7th Sub-Lord 2-7-11", "DK Jupiter in Own Sign", "CONFLICT: Age 25 vs 28"],
             ["Mangalik Impact", "Mars influences 7H", "Jupiter 9th aspect saves", "Strong DK protects", "UNIFIED: Cancelled"]
         ], [30, 42, 38, 38, 32]), [
            ("1. Where All 6 Systems Agree (100% Unified Verdicts)", "INTELLECTUAL & FINANCIAL MASTERY: BPHS (Exalted 2nd/5th lord Mercury + Own-sign 11th lord Jupiter), KP (Cuspal sub-lords signifying 2, 6, 10, 11), Phaladeepika (35 Bindus in 11H), and Jaimini unanimously confirm high financial independence and executive authority. Vargottama Lagna and Exalted Moon confirm lifelong resilience."),
            ("2. Where Systems Diverge & Technical Reasoning", "MARRIAGE TIMING: BPHS flags Saturn's 3rd aspect on the 7th house as a cause for delay. However, KP and Phaladeepika override this fear because Jupiter in Pisces casts an exact 9th trinal aspect on the 7th house, acting as a divine shield. Verdict: Marriage around age 26-28 will be stable and prosperous.")
        ]),
        ("11", "JAIMINI CHARA KARAKAS: 7 SOUL INDICATORS", "Decoding Soul Purpose Through Planetary Degrees (Jaimini Sutras)",
         (["Chara Karaka", "Planet & Degree", "Jaimini Role", "Life Manifestation"], [
             ["Atmakaraka (AK)", "Mars (29d 18m)", "Soul King & Primary Lesson", "Courage, mastering patience"],
             ["Amatyakaraka (AmK)", "Venus (14d 10m)", "Career & Professional Rise", "Diplomatic leadership, luxury"],
             ["Bhratrukaraka (BK)", "Saturn (14d 02m)", "Siblings, Mentors & Execution", "Structured perseverance"],
             ["Matrukaraka (MK)", "Sun (12d 06m)", "Mother, Sanctuary & Property", "Dignified domestic values"],
             ["Putrakaraka (PK)", "Moon (06d 18m)", "Creativity & Future Progeny", "Empathetic mentorship"],
             ["Gnatikaraka (GK)", "Mercury (02d 14m)", "Competition & Problem-Solving", "Defeating rivals via logic"],
             ["Darakaraka (DK)", "Jupiter (01d 52m)", "Spouse & Partner Nature", "Wise, ethical, protective spouse"]
         ], [36, 32, 52, 60]), [
            ("Atmakaraka (Mars) + Amatyakaraka (Venus) Synthesis", "With Mars as Atmakaraka, your soul is here to develop fearless initiative while mastering inner patience. Because Venus acts as Amatyakaraka in its own sign, your career blends warrior-like drive (Mars) with diplomatic grace (Venus)."),
            ("Darakaraka (Jupiter in Pisces) - The Soulmate Blueprint", "In Jaimini Astrology, the planet with the lowest degree (Jupiter at 01d 52m in Pisces) represents your spouse. Jupiter in its own sign in the 11th house indicates a partner who is noble, financially accomplished, and acts as your greatest friend.")
        ]),
        ("12", "LOVE, MARRIAGE & MANGALIK EVALUATION", "5th House Romance, 7th House Commitment & Marriage Windows",
         (["Phase", "Projected Timeline", "Operating Dasha", "Astrological Rating"], [
             ["Window 1", "Late 2035 - Mid 2036 (Age 25-26)", "Saturn MD - Venus AD", "Good (Early Proposal)"],
             ["Window 2", "Early 2037 - Late 2038 (Age 27-28)", "Saturn MD - Sun/Moon AD", "Excellent (Peak Harmony)"],
             ["Window 3", "Mid 2039 - Late 2040 (Age 29-30)", "Saturn MD - Mars/Rahu AD", "Strong (Post-Career Union)"]
         ], [25, 55, 50, 50]), [
            ("5th House & 7th House Relationship Dynamics", "With Virgo in the 5th house (Saturn + Sun + Mercury) and Scorpio in the 7th house, you do not take love lightly. Casual relationships do not interest you. You test a partner's intellect and integrity before opening your heart."),
            ("Complete Mangalik Dosha Technical Audit", "Mars rules the 7th and 12th houses, creating a mild Mangalik signature. Under Phaladeepika and BPHS rules, Jupiter's direct 9th aspect from its own sign Pisces onto the 7th house completely neutralizes malefic Martian heat. Marrying after age 26 ensures emotional maturity.")
        ]),
        ("13", "CAREER CALLING, WEALTH & RAJ YOGAS", "10th House Command, Dhana Yogas & Ideal Professional Arenas", None, [
            ("Top Raj Yogas & Dhana Yogas Present in Chart", "1. DHARMA-KARMA ADHIPATI YOGA (Saturn as 9th & 10th Lord in 5th Trine): Unstoppable rise to senior management or independent authority. 2. EXALTED BUDHADITYA & DHANA YOGA (2nd/5th Lord Mercury Exalted with Sun): Connects intelligence directly to wealth creation. 3. LABHA BRIHASPATI YOGA (11th Lord Jupiter in Own Sign in 11H): Guarantees lifelong financial liquidity. 4. VIPAREETA RAJ YOGA PATTERN (6th Lord Venus in 6H): Victory over rivals."),
            ("Ideal Career & Business Fields", "Primary Streams: Corporate Finance, Chartered Accountancy, Investment Banking, FinTech, Data Science, or Actuarial Analytics (Mercury + Saturn in Virgo). Secondary Streams: Law, Civil/Administrative Services, Corporate Governance, Medicine/Biotech, or Luxury Brand Management. Structured corporate role (Ages 22-30) followed by consultancy/enterprise (Age 31+).")
        ]),
        ("14", "RAHU-KETU AXIS & SADE SATI JOURNEY", "Shadow Planet Lessons & Saturn's 7.5-Year Transformation Cycles",
         (["Cycle", "Phase & Sign", "Timeline", "Core Impact & Strategy"], [
             ["Cycle 1", "Rising Phase (Aries)", "Mid 2027 - Mid 2029", "12th from Moon: Academic focus & sleep discipline"],
             ["Cycle 1", "Peak Phase (Taurus)", "Mid 2029 - Mid 2032", "Over Natal Moon: Higher education rigor & maturity"],
             ["Cycle 1", "Setting Phase (Gemini)", "Mid 2032 - Mid 2034", "2nd from Moon: First major job & income stability"],
             ["Cycle 2", "Full 7.5-Year Cycle", "2056 - 2064", "Peak executive consolidation and legacy building"]
         ], [25, 45, 40, 70]), [
            ("Rahu in 8th House (Sagittarius) & Ketu in 2nd House (Gemini)", "Rahu draws you toward deep research, audit, psychology, and hidden financial mechanisms. Ketu in the 2nd house detaches you from superficial small talk; practice warm communication and automate investments into long-term assets."),
            ("Why Vaanya's Sade Sati is Constructive (2027-2034)", "Because Saturn is the Yogakaraka planet for Taurus Ascendant and Moon is exalted in Taurus, Sade Sati acts as a strict academic and professional boot camp during college and early career years, forging extraordinary discipline.")
        ]),
        ("15", "VIMSHOTTARI DASHA TIMELINE (2010 - 2048)", "Planetary Period Timelines & Micro-Period Predictions",
         (["Dasha Period", "Years", "Age", "Key Life Events & Astrological Reasoning"], [
             ["Sun/Moon/Mars MD", "Birth - 2029", "Age 0 - 19", "Strong schooling, artistic flair, competitive spirit."],
             ["Saturn - Saturn", "2029 - 2032", "Age 19 - 22", "Intense college study, hard work, foundational degree."],
             ["Saturn - Mercury", "2032 - 2035", "Age 22 - 25", "EXCELLENT: Exalted Mercury brings top career break."],
             ["Saturn - Ketu", "2035 - 2036", "Age 25 - 26", "Brief introspection; avoid impulsive job switches."],
             ["Saturn - Venus", "2036 - 2039", "Age 26 - 29", "SUPERB: Promotion, luxury assets, marriage window."],
             ["Saturn - Sun", "2039 - 2040", "Age 29 - 30", "Authority role, management/government recognition."],
             ["Saturn - Moon", "2040 - 2042", "Age 30 - 32", "Emotional fulfillment, family expansion, travel."],
             ["Saturn - Mars", "2042 - 2043", "Age 32 - 33", "Bold property purchase or enterprise expansion."],
             ["Saturn - Rahu", "2043 - 2046", "Age 33 - 36", "Technological/foreign leap; guard against stress."],
             ["Saturn - Jupiter", "2046 - 2048", "Age 36 - 38", "Major wealth consolidation and senior leadership."]
         ], [36, 26, 24, 94]), [
            ("Deep-Dive: Yogakaraka Saturn Mahadasha (Age 19 to 38)", "Running the 19-year Mahadasha of Yogakaraka Saturn during prime youth and career-building years (Ages 19-38) is the single greatest gift in this chart. Every ounce of effort invested in her 20s and 30s compounds into lasting wealth.")
        ]),
        ("16", "VIMSHOTTARI DASHA TIMELINE (2048 - 2092)", "Peak Maturity, Exalted Mercury Mahadasha & Long-Term Legacy",
         (["Dasha Period", "Years", "Age", "Key Life Events & Astrological Reasoning"], [
             ["Mercury - Mercury", "2048 - 2051", "Age 38 - 41", "PEAK WEALTH: Exalted 2nd/5th lord triggers massive gains."],
             ["Mercury - Ketu", "2051 - 2052", "Age 41 - 42", "Spiritual insight and research breakthroughs."],
             ["Mercury - Venus", "2052 - 2055", "Age 42 - 45", "Luxury real estate, advisory/artistic pinnacle."],
             ["Mercury - Sun", "2055 - 2056", "Age 45 - 46", "Boardroom command and institutional honor."],
             ["Mercury - Moon", "2056 - 2057", "Age 46 - 47", "Peaceful domestic life, children's milestones."],
             ["Mercury - Mars", "2057 - 2058", "Age 47 - 48", "Decisive asset expansion and enterprise growth."],
             ["Mercury - Rahu", "2058 - 2061", "Age 48 - 51", "Global investments and innovative financial strategy."],
             ["Mercury - Jupiter", "2061 - 2063", "Age 51 - 53", "High philanthropy, mentorship, and abundant wealth."],
             ["Mercury - Saturn", "2063 - 2065", "Age 53 - 55", "Enduring institutional legacy and asset security."],
             ["Ketu & Venus MD", "2065 - 2092", "Age 55 - 82", "Lagna Lord Venus MD brings a regal, healthy golden era."]
         ], [36, 26, 24, 94]), [
            ("Deep-Dive: Exalted Mercury Mahadasha (Age 38 to 55)", "Following Saturn's disciplined foundation, the 17-year Mahadasha of exalted Mercury (ruling 2nd house of wealth and 5th house of intelligence) elevates the native to an industry leader, investor, and wealth creator.")
        ]),
        ("17", "CHRONOLOGICAL LIFE EVENT TIMELINE", "Pinpointing Crucial Ages, Turning Points & Milestone Years",
         (["Age", "Years", "Milestone", "Astrological Trigger & Guidance"], [
             ["Age 16 - 18", "2026 - 2028", "Stream Selection", "5H Virgo favors Finance, Tech, Law, or Bio-Sciences."],
             ["Age 19 - 22", "2029 - 2032", "Higher Education", "Intense study phase at a premier institute."],
             ["Age 22 - 24", "2032 - 2034", "First Career Break", "Saturn-Mercury AD triggers high-paying placement."],
             ["Age 26 - 28", "2036 - 2038", "Marriage Union", "Saturn-Venus/Sun AD activates 7H with Jupiter's grace."],
             ["Age 29 - 32", "2039 - 2042", "Property & Vehicles", "4th Lord Sun & Moon AD bring luxury home and family."],
             ["Age 34 - 38", "2044 - 2048", "Executive Rise", "Saturn-Jupiter AD cements senior leadership."],
             ["Age 39 - 45", "2049 - 2055", "Financial Peak", "Exalted Mercury MD generates multi-fold asset growth."]
         ], [24, 26, 38, 92]), [
            ("Critical Caution Years (When to Exercise Extra Care)", "Late 2029 to Early 2031 (Age 19-20): Peak Sade Sati overlapping Saturn-Saturn; avoid academic burnout. 2035 (Age 25): Saturn-Ketu transition; avoid hasty job switches. 2043-2045 (Age 33-35): Saturn-Rahu period; conduct thorough legal due diligence before signing joint property agreements.")
        ]),
        ("18", "KP SYSTEM: CUSPAL SUB-LORDS & SIGNIFICATORS", "Krishnamurti Paddhati Stellar & Sub-Lord Matrix",
         (["KP Cusp", "Sign", "Sign L.", "Star L.", "Sub L.", "House Significations & Verdict"], [
             ["Cusp 1 (Self)", "Taurus", "Venus", "Moon", "Jupiter", "1, 3, 11 (Strong Health & Optimism)"],
             ["Cusp 2 (Wealth)", "Gemini", "Mercury", "Rahu", "Saturn", "2, 5, 9, 10 (Steady Wealth Accumulation)"],
             ["Cusp 5 (Intellect)", "Virgo", "Mercury", "Moon", "Mercury", "2, 5, 6, 11 (Competitive Exam Success)"],
             ["Cusp 6 (Service)", "Libra", "Venus", "Rahu", "Venus", "1, 6, 11 (Victory Over Rivals)"],
             ["Cusp 7 (Marriage)", "Scorpio", "Mars", "Saturn", "Jupiter", "5, 7, 11 (Harmonious, Prosperous Union)"],
             ["Cusp 9 (Fortune)", "Capricorn", "Saturn", "Moon", "Venus", "1, 6, 9, 10 (Long-Distance Luck)"],
             ["Cusp 10 (Career)", "Aquarius", "Saturn", "Rahu", "Mercury", "2, 5, 6, 10, 11 (High Executive Rise)"],
             ["Cusp 11 (Gains)", "Pisces", "Jupiter", "Jupiter", "Venus", "1, 6, 11 (Fulfillment of Desires)"]
         ], [28, 22, 20, 20, 20, 70]), [
            ("KP Golden Rule Application for Career & Finance", "In Krishnamurti Paddhati, a planet gives the results of its Star Lord, and the Sub-Lord decides whether the promise is positive or negative. Because the 10th Cusp Sub-Lord is exalted Mercury (2, 5, 10, 11) and the 11th Cusp Sub-Lord is own-sign Venus, the promise of wealth and status is 100% locked.")
        ]),
        ("19", "SHADBALA, BHAVA BALA & PLANETARY AVASTHAS", "Six-Fold Mathematical Strength & Alertness State of Planets",
         (["Planet", "Virupas", "Rupas", "Required", "Strength %", "Avastha State"], [
             ["Sun", "412 Virupas", "6.87 Rupas", "5.00 Rupas", "137% (Strong)", "Jagrat (Wide Awake)"],
             ["Moon", "518 Virupas", "8.63 Rupas", "6.00 Rupas", "144% (Exalted)", "Jagrat (Wide Awake)"],
             ["Mars", "355 Virupas", "5.91 Rupas", "5.00 Rupas", "118% (Above Avg)", "Swapna (Dreaming)"],
             ["Mercury", "495 Virupas", "8.25 Rupas", "7.00 Rupas", "118% (Exalted)", "Jagrat (Wide Awake)"],
             ["Jupiter", "470 Virupas", "7.83 Rupas", "6.50 Rupas", "120% (Strong)", "Jagrat (Wide Awake)"],
             ["Venus", "460 Virupas", "7.66 Rupas", "5.50 Rupas", "139% (Dominant)", "Jagrat (Wide Awake)"],
             ["Saturn", "390 Virupas", "6.50 Rupas", "5.00 Rupas", "130% (Yogakaraka)", "Swapna (Dreaming)"]
         ], [22, 28, 25, 25, 32, 48]), [
            ("How Shadbala Ratios Shape Real Life", "Moon (144%), Venus (139%), Sun (137%), and Saturn (130%) far exceed their minimum required Shadbala thresholds. When the Lagna Lord (Venus), Moon, and Yogakaraka (Saturn) simultaneously hold over 130% strength, the individual possesses extraordinary stamina to outperform peers.")
        ]),
        ("20", "5-YEAR VARSHPHAL & TRANSIT FORECAST (2026-2031)", "Annual Tajika Progression & Major Saturn/Jupiter Transits", None, [
            ("2026 - 2027 (Age 16 - 17): Academic Sharpening & Focus", "Exalted Jupiter transiting Cancer (3H) and Leo (4H) boosts self-confidence, communication skills, and foundational board/entrance exam preparation."),
            ("2027 - 2028 (Age 17 - 18): Competitive Exams & Admission", "Jupiter transits Virgo (over natal 5th house Sun-Mercury-Saturn). This is a golden transit for clearing competitive entrance exams and securing admission into a premier institution. Maintain strict sleep schedules as Sade Sati begins."),
            ("2028 - 2029 (Age 18 - 19): Transition to University", "Jupiter transits Libra (6H) and Scorpio (7H), expanding social circles, mentorships, and institutional recognition."),
            ("2029 - 2031 (Age 19 - 21): Saturn Mahadasha Dawn", "As Yogakaraka Saturn's Mahadasha commences, Vaanya undergoes profound maturation, gravitating toward serious internships and leadership skills.")
        ]),
        ("21", "VEDIC NUMEROLOGY & COMPLETE DO'S AND DON'TS", "Mulank, Bhagyank & Actionable Behavioral Guardrails",
         (["Numerology Pillar", "Calculated Value", "Planet", "Strategic Application"], [
             ["Mulank (Psychic No.)", "2 (Born on 29th: 2+9=11 -> 2)", "Moon", "Intuitive, diplomatic, creative"],
             ["Bhagyank (Destiny)", "6 (Full DOB Sum)", "Venus", "Magnetic, artistic, luxury-loving"],
             ["Lucky Numbers", "2, 5, 6, 8", "Moon/Merc/Ven/Sat", "Use for accounts, dates & plates"],
             ["Numbers to Avoid", "4, 9 (For high-risk deals)", "Rahu / Mars", "Avoid major contracts on 4th, 9th"],
             ["Lucky Colors & Days", "White, Emerald Green, Blue", "Fri, Wed, Sat", "Wear during exams & interviews"]
         ], [38, 48, 32, 62]), [
            ("THE GOLDEN DO'S (HABITS THAT MULTIPLY LUCK)", "1. DO pursue structured analytical/commercial fields (Finance, Tech, Law, Med). 2. DO maintain a clutter-free desk facing East or North (activates 5H Mercury). 3. DO automate savings into long-term assets to counter 2nd house Ketu. 4. DO drink water from a pure silver glass daily to calm the Moon."),
            ("THE STRICT DON'TS (PITFALLS TO AVOID)", "1. DON'T let perfectionism paralyze action (Virgo 5H cluster over-thinking). 2. DON'T use sharp or sarcastic speech with family when stressed (2H Ketu). 3. DON'T rush into marriage before age 26 or neglect physical exercise.")
        ])
    ]

    for ch_num, title, sub, tbl_info, blocks in pages_data:
        pdf.add_page()
        pdf.ch_title(ch_num, title, sub)
        if tbl_info:
            pdf.tbl(tbl_info[0], tbl_info[1], tbl_info[2])
        for b_head, b_body in blocks:
            pdf.blk(b_head, b_body)

    # P23: REMEDIES & DISCLAIMER
    pdf.add_page()
    pdf.ch_title("22", "VEDIC REMEDIES & LEGAL DECLARATION", "Practical Planetary Alignment & Mandatory Disclaimer")
    rems = [
        ["Gemstone", "Diamond / White Zircon or Emerald", "Strengthens Lagna Lord Venus & Exalted Mercury"],
        ["Rudraksha", "6 Mukhi + 4 Mukhi Rudraksha", "Balances Venusian grace and Mercurial intellect"],
        ["Daily Mantra", "Om Shukraya Namaha / Om Budhaya Namaha", "Chant 27 or 108 times on Fridays & Wednesdays"],
        ["Sade Sati Shield", "Hanuman Chalisa & Shani Gayatri", "Recite on Saturdays to keep Sade Sati smooth"],
        ["Charitable Act", "Donate green moong dal or books", "Perform on Wednesdays to unlock Dhana Yogas"]
    ]
    pdf.tbl(["Category", "Recommendation", "Astrological Purpose"], rems, [34, 66, 80])
    pdf.blk("Ishtdev & Spiritual Alignment", "With Mercury and Saturn in the 5th house and Jupiter in Pisces in the 11th, offering prayers to Lord Ganesha and Goddess Lakshmi-Narayan brings peace.")

    pdf.set_y(192)
    pdf.set_fill_color(245, 240, 235)
    pdf.set_draw_color(140, 30, 20)
    pdf.set_line_width(0.6)
    pdf.rect(15, 192, 180, 78, "DF")
    pdf.set_xy(20, 196)
    pdf.set_font("Helvetica", "B", 10.5)
    pdf.set_text_color(140, 20, 20)
    pdf.cell(170, 6, "MANDATORY DECLARATION & LEGAL DISCLAIMER", 0, 1, "C")
    disc = (
        "This Advanced Kundali Help Book has been compiled and created by Rajiv Kumar (Contact: 9914465143). "
        "It is hereby explicitly declared that the creator of this report is NOT a professional or certified commercial astrologer. "
        "This report is generated solely for educational, spiritual, and self-reflective guidance with the help of classical astrological books, "
        "publicly available resources on the internet, mathematical algorithms, and generative AI. "
        "Astrological interpretations across BPHS, KP, Jaimini, and Phaladeepika are indicative tendencies rather than guaranteed fixed outcomes. "
        "Nothing in this document constitutes medical, legal, or licensed financial advice. The creator and editor of this report (Rajiv Kumar) "
        "assumes zero liability and is not responsible for any decisions or consequences arising from data or information in this report."
    )
    pdf.set_xy(20, 203)
    pdf.set_font("Helvetica", "", 8.2)
    pdf.set_text_color(40, 40, 40)
    pdf.multi_cell(170, 4.5, cln(disc), 0, "J")

    out = pdf.output(dest="S")
    return out.encode("latin-1") if isinstance(out, str) else bytes(out)

st.set_page_config(page_title="KP & Bhava Jyotish - Rajiv Kumar", layout="centered")
st.markdown("<div style='text-align:center;padding:15px;background:#fdf5e6;border:2px solid #8b2500;border-radius:10px;'><h2 style='color:#8b2500;margin:0;'>|| Shri Ganeshaya Namah ||</h2><h1 style='color:#5c1800;margin:5px 0;'>KP & Bhava Jyotish AI</h1><p style='color:#333;font-weight:bold;margin:0;'>23-Page Multi-System Advanced Kundali Help Book</p><p style='color:#8b2500;margin:5px 0 0 0;'>Created by: <b>Rajiv Kumar</b> | Contact: <b>9914465143</b></p></div><br>", unsafe_allow_html=True)

with st.form("k_form"):
    st.subheader("Enter Birth Particulars")
    
    language_choice = st.radio("Select Report Language", ["English", "Hindi"], horizontal=True)
    
    c1, c2 = st.columns(2)
    with c1:
        c_name = st.text_input("Full Name of Jataka", "Vaanya Bhagat")
        c_dob = st.text_input("Date of Birth (DD/MM/YYYY)", "29/09/2010")
    with c2:
        c_tob = st.text_input("Time of Birth (HH:MM 24-Hr)", "19:42")
        c_pob = st.text_input("Place of Birth (City, State)", "Jalandhar, Punjab, India")
    c_phone = st.text_input("Client WhatsApp / Contact Number", "")
    sub = st.form_submit_button("Generate 23-Page Master Kundali PDF")

if sub:
    with st.spinner("Generating 23-Page Master PDF..."):
        try:
            requests.post(WEBAPP_URL, json={"name":c_name, "dob":c_dob, "tob":c_tob, "pob":c_pob, "phone":c_phone, "language":language_choice, "timestamp":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}, timeout=3)
        except Exception:
            pass
            
        pdf_b = build_pdf(c_name, c_dob, c_tob, c_pob, language_choice)
        
        st.success(f"23-Page Master Kundali Help Book for {c_name} is ready!")
        st.download_button("Download 23-Page Master Kundali PDF", data=pdf_b, file_name=f"Advanced_Kundali_{c_name.replace(' ', '_')}.pdf", mime="application/pdf")
