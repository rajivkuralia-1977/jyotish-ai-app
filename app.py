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
            ("6th House (Ripu/Roga Bhava - Libra): Work, Rivals & Health", "Occupied by own-sign Venus. You thrive in competitive exams an
