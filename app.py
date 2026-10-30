import streamlit as st
from fpdf import FPDF
import datetime
import requests

GOOGLE_SHEET_WEBAPP_URL = "https://script.google.com/macros/s/AKfycbxkPrTQK017yE2WJDo65jO6Ulpw2ESpokbJuUWltvLCSKlq_vKFavc3Dl3NNh2duyYF2g/exec"

def clean(text):
    text = str(text)
    replacements = {
        "°": " deg ", "•": "- ", "–": "-", "—": "-",
        "’": "'", "‘": "'", "“": '"', "”": '"'
    }
    for k, v in replacements.items():
        text = text.replace(k, v)
    return text.encode('latin-1', 'replace').decode('latin-1')


class MasterKundaliPDF(FPDF):
    def __init__(self, client_name, dob, tob, pob):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.client_name = clean(client_name)
        self.dob = clean(dob)
        self.tob = clean(tob)
        self.pob = clean(pob)
        self.set_auto_page_break(auto=False)

    def draw_swastik(self, x, y, size, color, line_width):
        self.set_draw_color(*color)
        self.set_line_width(line_width)
        half = size / 2.0
        self.line(x - half, y, x + half, y)
        self.line(x, y - half, x, y + half)
        self.line(x, y - half, x + half, y - half)
        self.line(x + half, y, x + half, y + half)
        self.line(x, y + half, x - half, y + half)
        self.line(x - half, y, x - half, y - half)
        q = half / 2.0
        dot_r = line_width * 0.8
        self.set_fill_color(*color)
        for dx, dy in [(-q, -q), (q, -q), (-q, q), (q, q)]:
            self.ellipse(x + dx - dot_r/2, y + dy - dot_r/2, dot_r, dot_r, style='F')

    def draw_ganesha_motif(self, x, y, size):
        self.set_draw_color(180, 40, 20)
        self.set_fill_color(255, 240, 215)
        self.set_line_width(1.2)
        self.ellipse(x - size/2, y - size/2, size, size, style='DF')
        self.set_line_width(0.6)
        self.ellipse(x - size/2 + 3, y - size/2 + 3, size - 6, size - 6, style='D')
        self.set_line_width(1.5)
        self.line(x - 10, y - 8, x + 10, y - 8)
        self.line(x - 12, y - 3, x + 12, y - 3)
        self.line(x - 10, y + 2, x + 10, y + 2)
        self.line(x, y - 14, x, y + 12)
        self.line(x, y + 12, x + 6, y + 15)
        self.set_fill_color(180, 40, 20)
        self.ellipse(x - 2, y - 20, 4, 4, style='F')

    def draw_north_indian_chart(self, x, y, size, title, house_data):
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(120, 30, 20)
        self.set_xy(x, y - 7)
        self.cell(size, 6, clean(title), align='C')
        self.set_draw_color(140, 50, 30)
        self.set_line_width(0.6)
        self.rect(x, y, size, size)
        self.line(x, y, x + size, y + size)
        self.line(x + size, y, x, y + size)
        half = size / 2.0
        self.line(x + half, y, x + size, y + half)
        self.line(x + size, y + half, x + half, y + size)
        self.line(x + half, y + size, x, y + half)
        self.line(x, y + half, x + half, y)
        coords = {
            1: (0.50, 0.25), 2: (0.25, 0.10), 3: (0.10, 0.25),
            4: (0.25, 0.50), 5: (0.10, 0.75), 6: (0.25, 0.88),
            7: (0.50, 0.75), 8: (0.75, 0.88), 9: (0.88, 0.75),
            10: (0.75, 0.50), 11: (0.88, 0.25), 12: (0.75, 0.10)
        }
        self.set_font("Helvetica", "B", 7.5)
        self.set_text_color(40, 40, 40)
        for h_num, text in house_data.items():
            cx = x + size * coords[h_num][0] - 12
            cy = y + size * coords[h_num][1] - 3
            self.set_xy(cx, cy)
            self.cell(24, 5, clean(text), align='C')

    def header(self):
        self.set_draw_color(180, 130, 70)
        self.set_line_width(0.5)
        self.rect(8, 8, 194, 281)
        self.set_line_width(0.2)
        self.rect(10, 10, 190, 277)
        self.draw_swastik(105, 148.5, 105, color=(246, 236, 222), line_width=5.0)
        self.draw_swastik(20, 20, 10, color=(180, 45, 25), line_width=0.9)
        self.draw_swastik(190, 20, 10, color=(180, 45, 25), line_width=0.9)
        if self.page_no() > 1:
            self.set_xy(30, 14)
            self.set_font("Helvetica", "B", 8.5)
            self.set_text_color(130, 50, 30)
            hdr = f"KP BHAVA JYOTISH | ADVANCED KUNDALI HELP BOOK | {self.client_name.upper()}"
            self.cell(150, 5, clean(hdr), align='C')
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
        self.cell(90, 8, "Created by Rajiv Kumar | Contact: 9914465143", align='L')
        self.cell(90, 8, f"Page {self.page_no()} of 23", align='R')

    def section_title(self, chapter_num, title, subtitle=""):
        self.set_xy(15, 28)
        self.set_fill_color(248, 238, 225)
        self.set_draw_color(160, 60, 30)
        self.set_line_width(0.4)
        self.rect(15, 28, 180, 15, style='DF')
        self.set_xy(18, 29.5)
        self.set_font("Helvetica", "B", 12)
        self.set_text_color(140, 30, 20)
        self.cell(174, 6, clean(f"CHAPTER {chapter_num}: {title}"), align='L')
        if subtitle:
            self.set_xy(18, 36)
            self.set_font("Helvetica", "I", 8.5)
            self.set_text_color(90, 60, 40)
            self.cell(174, 5, clean(subtitle), align='L')
        self.set_y(47)

    def write_block(self, heading, lines):
        self.set_x(15)
        self.set_font("Helvetica", "B", 9.5)
        self.set_text_color(140, 40, 20)
        self.cell(180, 6, clean(heading), ln=True)
        self.set_x(15)
        self.set_font("Helvetica", "", 9)
        self.set_text_color(35, 35, 35)
        body = " ".join(lines) if isinstance(lines, list) else str(lines)
        self.multi_cell(180, 5.0, clean(body))
        self.ln(2.5)

    def write_table(self, headers, rows, col_widths):
        self.set_x(15)
        self.set_fill_color(150, 50, 30)
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 8)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 6.5, clean(h), border=1, fill=True, align='C')
        self.ln()
        self.set_font("Helvetica", "", 7.5)
        self.set_text_color(30, 30, 30)
        fill = False
        for row in rows:
            self.set_x(15)
            if fill:
                self.set_fill_color(252, 246, 238)
            else:
                self.set_fill_color(255, 255, 255)
            for i, val in enumerate(row):
                self.cell(col_widths[i], 6.0, clean(val), border=1, fill=True, align='C')
            self.ln()
            fill = not fill
        self.ln(3)


def generate_23_page_report(name, dob, tob, pob):
    pdf = MasterKundaliPDF(name, dob, tob, pob)

    # PAGE 1: COVER
    pdf.add_page()
    pdf.set_y(32)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(160, 40, 20)
    pdf.cell(0, 8, "|| SHRI GANESHAYA NAMAH ||", align='C', ln=True)
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(100, 50, 30)
    pdf.cell(0, 6, "Vakratunda Mahakaya Suryakoti Samaprabha", align='C', ln=True)
    pdf.cell(0, 6, "Nirvighnam Kurume Deva Sarva Karyeshu Sarvada", align='C', ln=True)
    pdf.draw_ganesha_motif(105, 88, 44)
    pdf.set_y(120)
    pdf.set_font("Helvetica", "B", 20)
    pdf.set_text_color(120, 25, 15)
    pdf.cell(0, 10, "ADVANCED KUNDALI HELP BOOK", align='C', ln=True)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(160, 90, 30)
    pdf.cell(0, 7, "Multi-System Synthesis: KP | BPHS | Jaimini | Phaladeepika", align='C', ln=True)

    pdf.set_fill_color(250, 242, 230)
    pdf.set_draw_color(160, 80, 40)
    pdf.rect(25, 145, 160, 52, style='DF')
    pdf.set_xy(30, 150)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(120, 30, 20)
    pdf.cell(150, 7, "JATAKA (CLIENT) BIRTH PARTICULARS", align='C', ln=True)
    pdf.set_font("Helvetica", "B", 9.5)
    pdf.set_text_color(40, 40, 40)
    pdf.set_x(35); pdf.cell(140, 7, clean(f"Name of Jataka : {name}"), ln=True)
    pdf.set_x(35); pdf.cell(140, 7, clean(f"Date of Birth  : {dob}"), ln=True)
    pdf.set_x(35); pdf.cell(140, 7, clean(f"Time of Birth  : {tob}"), ln=True)
    pdf.set_x(35); pdf.cell(140, 7, clean(f"Place of Birth : {pob}"), ln=True)
    pdf.set_x(35); pdf.cell(140, 7, "Ayanamsa       : KP New / Lahiri (Chitrapaksha)", ln=True)

    pdf.set_fill_color(140, 35, 20)
    pdf.rect(25, 215, 160, 36, style='F')
    pdf.set_xy(25, 220)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(255, 235, 200)
    pdf.cell(160, 7, "CREATED BY: RAJIV KUMAR", align='C', ln=True)
    pdf.set_font("Helvetica", "B", 11)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 7, "Contact & Consultation: +91-9914465143", align='C', ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(240, 220, 200)
    pdf.cell(0, 6, "KP & Bhava Jyotish Research Wing | Jalandhar, Punjab", align='C', ln=True)

    # PAGE 2: TOC
    pdf.add_page()
    pdf.section_title("01", "MASTER TABLE OF CONTENTS", "6 Classical Systems Converging Into One Unified Verdict")
    toc_rows = [
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
    pdf.write_table(["Page", "Chapter & Section Contents"], toc_rows, [30, 150])
    pdf.write_block("Why Multi-System Cross-Validation Matters", [
        "Most traditional reports rely on a single text, leading to contradictions.",
        "This Help Book cross-examines BPHS, KP, Jaimini Sutras, Phaladeepika, Brihat Jataka,",
        "and Laghu Parashari. Predictions confirmed by all systems are marked as UNIFIED",
        "VERDICTS, while technical divergences are transparently explained."
    ])

    # PAGE 3: AVAKAHADA
    pdf.add_page()
    pdf.section_title("02", "AVAKAHADA CHAKRA & PANCHANG", "Foundational Astronomical & Natal Alignment")
    avak_rows = [
        ["Lagna (Ascendant)", "Taurus 14 deg 52m", "Lagna Lord", "Venus (Shukra)"],
        ["Moon Sign (Rashi)", "Taurus 06 deg 18m", "Rashi Lord", "Venus (Shukra)"],
        ["Nakshatra & Pada", "Krittika - Pada 3", "Nakshatra Lord", "Sun (Surya)"],
        ["Tithi at Birth", "Krishna Saptami", "Vaar (Day)", "Mid-Week / Venusian"],
        ["Yoga & Karana", "Variyan / Balava", "Gana & Yoni", "Rakshasa / Mesh"],
        ["Nadi & Varna", "Antya / Vaishya", "Paya (Footing)", "Swarna (Gold)"],
        ["Sun Sign (Vedic)", "Virgo (Kanya)", "Active Dasha", "Saturn / Mercury"]
    ]
    pdf.write_table(["Parameter", "Natal Value", "Parameter", "Natal Value"], avak_rows, [45, 45, 45, 45])
    pdf.write_block("1. Vaar & Tithi Impact", [
        "Born with strong Venusian and Mercurial currents, the native possesses sharp",
        "analytical intellect paired with refined aesthetic sensibilities. Krishna Paksha",
        "birth grants natural resilience, turning early obstacles into stepping stones."
    ])
    pdf.write_block("2. Lagna & Rashi Pillar (Vrishabha / Taurus)", [
        "With Taurus rising and housing the exalted Moon, you build life brick by brick.",
        "You project calm reliability, determination, and a taste for quality."
    ])
    pdf.write_block("3. Nakshatra Pillar (Krittika / Rohini Axis)", [
        "This stellar signature bestows the Razor of Truth alongside creative fertility.",
        "You cut through false pretenses directly and protect your family fiercely."
    ])

    # PAGE 4: CHARTS D1 & D9
    pdf.add_page()
    pdf.section_title("03", "VISUAL CHARTS: LAGNA (D1) & NAVAMSHA (D9)", "North Indian Style Natal & Divisional Blueprints")
    d1_data = {
        1: "As 14d Mo 6d", 2: "Ke 9d", 3: "", 4: "",
        5: "Su 12d Sa 14d", 6: "Me 2d Ve 14d", 7: "Ma 29d", 8: "Ra 9d",
        9: "", 10: "", 11: "Ju(R) 1d", 12: ""
    }
    pdf.draw_north_indian_chart(20, 56, 78, "LAGNA CHART (D1 - RASHI)", d1_data)
    d9_data = {
        1: "As(Tau)", 2: "Su", 3: "Ra", 4: "",
        5: "", 6: "", 7: "Me", 8: "",
        9: "Ke", 10: "Mo Sa", 11: "Ve", 12: "Ma Ju"
    }
    pdf.draw_north_indian_chart(112, 56, 78, "NAVAMSHA CHART (D9)", d9_data)
    pdf.set_y(142)
    pdf.write_block("Technical Chart Synthesis (Why Events Happen)", [
        "1. Vargottama Ascendant (Taurus Rising in both D1 and D9): When the same sign",
        "rises in both Rashi and Navamsha, BPHS and Phaladeepika declare the native",
        "internally and externally unshakable. Health and status are doubly fortified.",
        "2. 5th House Surya-Shani-Budha Cluster (Virgo): The 4th Lord (Sun), 2nd/5th",
        "Lord (Exalted Mercury), and Yogakaraka 9th/10th Lord (Saturn) conjoin in the",
        "5th trine. This forms a premier Raja Yoga for technical and financial mastery.",
        "3. 6th House Own-Sign Venus (Libra): Lagna Lord Venus sits in its Moolatrikona",
        "sign Libra, neutralizing enemies and ensuring competitive exam victories."
    ])

    # PAGE 5: CHARTS D10 & D7
    pdf.add_page()
    pdf.section_title("04", "VISUAL CHARTS: DASHAMSHA (D10) & SAPTAMSHA (D7)", "Career Authority (D10) & Creative Legacy (D7)")
    d10_data = {
        1: "As(Cap) Ju", 2: "Ve", 3: "Mo", 4: "Ma",
        5: "Ra", 6: "", 7: "Su", 8: "",
        9: "Me", 10: "Sa", 11: "Ke", 12: ""
    }
    pdf.draw_north_indian_chart(20, 56, 78, "DASHAMSHA (D10 - CAREER)", d10_data)
    d7_data = {
        1: "As(Vir)", 2: "Ve", 3: "Ma", 4: "Ju",
        5: "Sa", 6: "Ra", 7: "", 8: "",
        9: "Su", 10: "Mo", 11: "Me", 12: "Ke"
    }
    pdf.draw_north_indian_chart(112, 56, 78, "SAPTAMSHA (D7 - CREATIVITY)", d7_data)
    pdf.set_y(142)
    varga_rows = [
        ["D1 (Rashi)", "Physical Body & Destiny", "Taurus", "Vargottama Strength"],
        ["D2 (Hora)", "Wealth & Accumulation", "Leo/Cancer", "Strong Solar Hora"],
        ["D3 (Drekkana)", "Courage & Initiative", "Virgo", "Analytical Execution"],
        ["D4 (Chaturthamsha)", "Property & Fixed Assets", "Scorpio", "Real Estate Gains"],
        ["D7 (Saptamsha)", "Progeny & Creativity", "Virgo", "Disciplined Output"],
        ["D9 (Navamsha)", "Marriage & Dharma", "Taurus", "High Spouse Loyalty"],
        ["D10 (Dashamsha)", "Career & Command", "Capricorn", "Saturn in 10th: Authority"],
        ["D12 (Dwadashamsha)", "Parents & Lineage", "Sagittarius", "Strong Paternal Karma"]
    ]
    pdf.write_table(["Varga Chart", "Domain", "Ascendant", "Key Verdict"], varga_rows, [35, 55, 35, 55])

    # PAGE 6: PLANETARY DEGREES & ASHTAKAVARGA
    pdf.add_page()
    pdf.section_title("05", "PLANETARY POSITIONS & ASHTAKAVARGA", "Exact Sidereal Longitudes, Nakshatra Lords, Sub-Lords & Bindus")
    planet_rows = [
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
    pdf.write_table(["Planet", "Sign", "Degree", "Nakshatra", "Sign L.", "Star L.", "Sub L.", "Dignity"], planet_rows, [22, 20, 18, 24, 20, 20, 20, 36])
    pdf.write_block("Sarvashtakavarga Summary (Bindu Strength per House)", [
        "H1 (Taurus): 31 | H2 (Gemini): 27 | H3 (Cancer): 30 | H4 (Leo): 29 |",
        "H5 (Virgo): 26 | H6 (Libra): 32 | H7 (Scorpio): 25 | H8 (Sagittarius): 22 |",
        "H9 (Capricorn): 29 | H10 (Aquarius): 33 | H11 (Pisces): 35 | H12 (Aries): 20.",
        "REASONING: 33 Bindus in the 10th House and 35 Bindus in the 11th House",
        "(Phaladeepika rule) guarantee that professional efforts (10th) yield",
        "disproportionately high financial gains (11th), while 20 Bindus in the 12th",
        "keeps wasteful expenditure strictly under control."
    ])

    # PAGE 7: PLANETARY PROFILE 1
    pdf.add_page()
    pdf.section_title("06", "PERSONAL PLANETARY PROFILE (SUN TO JUPITER)", "How Each Planet Operates by Placement, Lordship & Aspect")
    pdf.write_block("1. SUN (4th Lord in 5th House - Virgo)", [
        "WHY IT HAPPENS: Sun rules your 4th house of home and sits in the 5th house.",
        "EFFECT: Your emotional security is tied to intellectual achievement. Sun's 7th",
        "aspect on the 11th house links real estate and education to high financial gains."
    ])
    pdf.write_block("2. MOON (3rd Lord Exalted in Lagna - Taurus)", [
        "WHY IT HAPPENS: Moon is exalted in Taurus in the 1st house.",
        "EFFECT: Grants extraordinary emotional magnetism, memory retention, and",
        "intuition. Moon's 7th aspect on the 7th house brings a devoted life partner."
    ])
    pdf.write_block("3. MARS (7th & 12th Lord in 6th/7th Cusp)", [
        "WHY IT HAPPENS: Mars governs partnerships (7th) and distant lands (12th).",
        "EFFECT: You bring fierce loyalty and protective fire to relationships.",
        "You do not tolerate mediocrity or dishonesty in business or marriage."
    ])
    pdf.write_block("4. MERCURY (2nd & 5th Lord Exalted in 5th House - Virgo)", [
        "WHY IT HAPPENS: Mercury rules wealth (2nd) and intellect (5th) in exaltation.",
        "EFFECT: Forms a top-tier Dhana-cum-Budhaditya Yoga. Your mathematical,",
        "commercial, and analytical skills convert directly into tangible wealth."
    ])
    pdf.write_block("5. JUPITER (8th & 11th Lord in 11th House - Pisces)", [
        "WHY IT HAPPENS: Jupiter occupies its own sign Pisces in the 11th house.",
        "EFFECT: Jupiter's 5th aspect blesses communication (3H); its 7th aspect",
        "protects education/children (5H); its 9th aspect shields marriage (7H)."
    ])

    # PAGE 8: PLANETARY PROFILE 2
    pdf.add_page()
    pdf.section_title("07", "PERSONAL PLANETARY PROFIL
