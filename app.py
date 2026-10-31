import streamlit as st
from fpdf import FPDF
import datetime
import requests
import os

WEBAPP_URL = "https://script.google.com/macros/s/AKfycbxkPrTQK017yE2WJDo65jO6Ulpw2ESpokbJuUWltvLCSKlq_vKFavc3Dl3NNh2duyYF2g/exec"
FONT_URL = "https://github.com/googlefonts/noto-fonts/raw/main/hinted/ttf/NotoSansDevanagari/NotoSansDevanagari-Regular.ttf"
FONT_FILE = "NotoSansDevanagari-Regular.ttf"

# Download Hindi Font dynamically if not present
if not os.path.exists(FONT_FILE):
    try:
        r = requests.get(FONT_URL, timeout=10)
        with open(FONT_FILE, "wb") as f:
            f.write(r.content)
    except Exception:
        pass

def cln(txt):
    return str(txt).replace("\u2013", "-").replace("\u2014", "-")

class KundaliPDF(FPDF):
    def __init__(self, name, dob, tob, pob, language):
        super().__init__("P", "mm", "A4")
        self.c_name = cln(name)
        self.c_dob = cln(dob)
        self.c_tob = cln(tob)
        self.c_pob = cln(pob)
        self.language = language
        self.set_auto_page_break(False)
        
        # ACTIVATE HARFBUZZ TEXT SHAPING FOR PERFECT HINDI MATRAS
        try:
            self.set_text_shaping(True)
        except AttributeError:
            pass

        # Load fonts and explicitly register all styles to prevent crash
        if os.path.exists(FONT_FILE):
            self.add_font("Hindi", "", FONT_FILE)
            self.add_font("Hindi", "B", FONT_FILE)
            self.add_font("Hindi", "I", FONT_FILE)
            self.has_hindi = True
        else:
            self.has_hindi = False

    def use_font(self, style="", size=9):
        if self.language == "Hindi" and self.has_hindi:
            self.set_font("Hindi", style, size)
        else:
            self.set_font("Helvetica", style, size)

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

    def chart(self, x, y, s, title, asc_rashi, data):
        self.use_font("B", 9.5)
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
        
        scale = s / 100.0
        positions = {
            1: (50, 8, 50, 24), 2: (15, 8, 26, 16), 3: (8, 15, 15, 26),
            4: (8, 52, 24, 50), 5: (8, 88, 15, 75), 6: (15, 96, 26, 85),
            7: (50, 96, 50, 78), 8: (85, 96, 74, 85), 9: (94, 88, 85, 75),
            10: (94, 52, 76, 50), 11: (94, 15, 85, 25), 12: (85, 8, 74, 16)
        }
        
        for hs in range(1, 13):
            rashi = ((asc_rashi + hs - 2) % 12) + 1
            rx, ry, px, py = positions[hs]
            
            self.use_font("B", 7)
            self.set_text_color(160, 90, 40)
            self.set_xy(x + (rx * scale) - 5, y + (ry * scale) - 3)
            self.cell(10, 6, str(rashi), 0, 0, "C")
            
            if hs in data and data[hs]:
                self.use_font("", 7)
                self.set_text_color(40, 40, 40)
                lines = data[hs].split("\n")
                
                lh = 3.5 
                start_y = y + (py * scale) - ((len(lines) * lh) / 2.0)
                
                for i, line in enumerate(lines):
                    self.set_xy(x + (px * scale) - 15, start_y + (i * lh))
                    self.cell(30, lh, cln(line), 0, 0, "C")

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
            self.use_font("B", 8.5)
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
        self.use_font("B", 8)
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
        self.use_font("B", 11.5)
        self.set_text_color(140, 30, 20)
        self.cell(174, 6, cln(f"CHAPTER {num}: {title}" if self.language == "English" else f"अध्याय {num}: {title}"), 0, 0, "L")
        if sub:
            self.set_xy(18, 36)
            self.use_font("", 8.5)
            self.set_text_color(90, 60, 40)
            self.cell(174, 5, cln(sub), 0, 0, "L")
        self.set_y(47)

    def blk(self, head, body):
        self.set_x(15)
        self.use_font("B", 9.5)
        self.set_text_color(140, 40, 20)
        self.cell(180, 6, cln(head), 0, 1, "L")
        self.set_x(15)
        self.use_font("", 9)
        self.set_text_color(35, 35, 35)
        self.multi_cell(180, 5.0, cln(body))
        self.ln(2.5)

    def tbl(self, hdrs, rows, widths):
        self.set_x(15)
        self.set_fill_color(150, 50, 30)
        self.set_text_color(255, 255, 255)
        self.use_font("B", 8)
        for i, h in enumerate(hdrs):
            self.cell(widths[i], 6.5, cln(h), 1, 0, "C", True)
        self.ln()
        self.use_font("", 7.5)
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

# ================= DATA DICTIONARIES =================
EN_PAGES = [
    ("02", "AVAKAHADA CHAKRA & PANCHANG", "Foundational Astronomical & Natal Alignment",
     (["Parameter", "Natal Value", "Parameter", "Natal Value"], [
         ["Lagna (Ascendant)", "Taurus 14° 52'", "Lagna Lord", "Venus (Shukra)"],
         ["Moon Sign (Rashi)", "Taurus 06° 18'", "Rashi Lord", "Venus (Shukra)"],
         ["Nakshatra & Pada", "Krittika - Pada 3", "Nakshatra Lord", "Sun (Surya)"],
         ["Tithi at Birth", "Krishna Saptami", "Vaar (Day)", "Wednesday / Venusian"],
         ["Yoga & Karana", "Variyan / Balava", "Gana & Yoni", "Rakshasa / Mesh"],
         ["Nadi & Varna", "Antya / Vaishya", "Paya (Footing)", "Swarna (Gold)"],
         ["Sun Sign (Vedic)", "Virgo (Kanya)", "Active Dasha", "Saturn / Mercury"]
     ], [45, 45, 45, 45]), [
        ("1. Vaar & Tithi Impact", "Born with strong Venusian and Mercurial currents, the native possesses sharp analytical intellect paired with refined aesthetic sensibilities. Krishna Paksha birth grants natural resilience, turning early obstacles into stepping stones."),
        ("2. Lagna & Rashi Pillar (Vrishabha / Taurus)", "With Taurus rising and housing the exalted Moon, you build life brick by brick. You project calm reliability, determination, and a taste for quality."),
        ("3. Nakshatra Pillar (Krittika / Rohini Axis)", "This stellar signature bestows the Razor of Truth alongside creative fertility. You cut through false pretenses directly and protect your family fiercely.")
    ]),
    ("05", "PLANETARY POSITIONS & ASHTAKAVARGA", "Exact Sidereal Longitudes, Nakshatra Lords, Sub-Lords & Bindus",
     (["Planet", "Sign", "Degree", "Nakshatra", "Sign L.", "Star L.", "Sub L.", "Dignity"], [
         ["Ascendant", "Taurus", "14° 52'", "Rohini-2", "Venus", "Moon", "Jupiter", "Vargottama"],
         ["Sun", "Virgo", "12° 06'", "Hasta-1", "Mercury", "Moon", "Moon", "Friendly"],
         ["Moon", "Taurus", "06° 18'", "Krittika-3", "Venus", "Sun", "Venus", "Exalted"],
         ["Mars", "Libra", "29° 18'", "Vishakha-3", "Venus", "Jupiter", "Mars", "Atmakaraka"],
         ["Mercury", "Virgo", "02° 14'", "U.Phalguni", "Mercury", "Sun", "Saturn", "Exalted"],
         ["Jupiter(R)", "Pisces", "01° 52'", "P.Bhadra-4", "Jupiter", "Jupiter", "Venus", "Own Sign"],
         ["Venus", "Libra", "14° 10'", "Swati-3", "Venus", "Rahu", "Mercury", "Moolatrikona"],
         ["Saturn", "Virgo", "14° 02'", "Hasta-2", "Mercury", "Moon", "Rahu", "Yogakaraka"],
         ["Rahu", "Sagittar.", "09° 11'", "Mula-3", "Jupiter", "Ketu", "Venus", "8H Research"],
         ["Ketu", "Gemini", "09° 11'", "Ardra-1", "Mercury", "Rahu", "Rahu", "2H Detached"]
     ], [22, 20, 18, 24, 20, 20, 20, 36]), [
        ("Sarvashtakavarga Summary (Bindu Strength per House)", "H1: 31 | H2: 27 | H3: 30 | H4: 29 | H5: 26 | H6: 32 | H7: 25 | H8: 22 | H9: 29 | H10: 33 | H11: 35 | H12: 20. REASONING: 33 Bindus in H10 and 35 Bindus in H11 guarantee that career efforts yield high financial gains.")
    ]),
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
        ("1. Where All 6 Systems Agree (100% Unified Verdicts)", "INTELLECTUAL & FINANCIAL MASTERY: BPHS, KP, Phaladeepika, and Jaimini unanimously confirm high financial independence and executive authority. Vargottama Lagna and Exalted Moon confirm lifelong resilience."),
        ("2. Where Systems Diverge & Technical Reasoning", "MARRIAGE TIMING: BPHS flags Saturn's 3rd aspect on the 7th house as a cause for delay. However, KP and Phaladeepika override this fear because Jupiter in Pisces casts an exact 9th trinal aspect on the 7th house, acting as a divine shield. Verdict: Marriage around age 26-28 will be stable and prosperous.")
    ]),
    ("11", "JAIMINI CHARA KARAKAS: 7 SOUL INDICATORS", "Decoding Soul Purpose Through Planetary Degrees (Jaimini Sutras)",
     (["Chara Karaka", "Planet & Degree", "Jaimini Role", "Life Manifestation"], [
         ["Atmakaraka (AK)", "Mars (29° 18')", "Soul King & Primary Lesson", "Courage, mastering patience"],
         ["Amatyakaraka (AmK)", "Venus (14° 10')", "Career & Professional Rise", "Diplomatic leadership, luxury"],
         ["Bhratrukaraka (BK)", "Saturn (14° 02')", "Siblings, Mentors & Execution", "Structured perseverance"],
         ["Matrukaraka (MK)", "Sun (12° 06')", "Mother, Sanctuary & Property", "Dignified domestic values"],
         ["Putrakaraka (PK)", "Moon (06° 18')", "Creativity & Future Progeny", "Empathetic mentorship"],
         ["Gnatikaraka (GK)", "Mercury (02° 14')", "Competition & Problem-Solving", "Defeating rivals via logic"],
         ["Darakaraka (DK)", "Jupiter (01° 52')", "Spouse & Partner Nature", "Wise, ethical, protective spouse"]
     ], [36, 32, 52, 60]), [
        ("Atmakaraka (Mars) + Amatyakaraka (Venus) Synthesis", "With Mars as Atmakaraka, your soul is here to develop fearless initiative while mastering inner patience. Because Venus acts as Amatyakaraka in its own sign, your career blends warrior-like drive (Mars) with diplomatic grace (Venus)."),
        ("Darakaraka (Jupiter in Pisces) - The Soulmate Blueprint", "In Jaimini Astrology, the planet with the lowest degree represents your spouse. Jupiter in its own sign in the 11th house indicates a partner who is noble, financially accomplished, and acts as your greatest friend.")
    ]),
    ("12", "LOVE, MARRIAGE & MANGALIK EVALUATION", "5th House Romance, 7th House Commitment & Marriage Windows",
     (["Phase", "Projected Timeline", "Operating Dasha", "Astrological Rating"], [
         ["Window 1", "Late 2035 - Mid 2036 (Age 25-26)", "Saturn MD - Venus AD", "Good (Early Proposal)"],
         ["Window 2", "Early 2037 - Late 2038 (Age 27-28)", "Saturn MD - Sun/Moon AD", "Excellent (Peak Harmony)"],
         ["Window 3", "Mid 2039 - Late 2040 (Age 29-30)", "Saturn MD - Mars/Rahu AD", "Strong (Post-Career Union)"]
     ], [25, 55, 50, 50]), [
        ("5th House & 7th House Relationship Dynamics", "With Virgo in the 5th house and Scorpio in the 7th house, you do not take love lightly. Casual relationships do not interest you. You test a partner's intellect and integrity before opening your heart."),
        ("Complete Mangalik Dosha Technical Audit", "Mars rules the 7th and 12th houses, creating a mild Mangalik signature. Under Phaladeepika and BPHS rules, Jupiter's direct 9th aspect from its own sign Pisces onto the 7th house completely neutralizes malefic Martian heat. Marrying after age 26 ensures emotional maturity.")
    ]),
    ("13", "CAREER CALLING, WEALTH & RAJ YOGAS", "10th House Command, Dhana Yogas & Ideal Professional Arenas", None, [
        ("Top Raj Yogas & Dhana Yogas Present in Chart", "1. DHARMA-KARMA ADHIPATI YOGA: Unstoppable rise to senior management or independent authority. 2. EXALTED BUDHADITYA & DHANA YOGA: Connects intelligence directly to wealth creation. 3. LABHA BRIHASPATI YOGA: Guarantees lifelong financial liquidity. 4. VIPAREETA RAJ YOGA PATTERN: Victory over rivals."),
        ("Ideal Career & Business Fields", "Primary Streams: Corporate Finance, Chartered Accountancy, Investment Banking, FinTech, Data Science, or Actuarial Analytics. Secondary Streams: Law, Civil/Administrative Services, Corporate Governance, Medicine/Biotech, or Luxury Brand Management. Structured corporate role (Ages 22-30) followed by consultancy/enterprise (Age 31+).")
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

HI_PAGES = [
    ("02", "अवकाहड़ा चक्र और पंचांग", "बुनियादी खगोलीय और जन्म कुंडली संरेखण",
     (["पैरामीटर", "जन्म मूल्य", "पैरामीटर", "जन्म मूल्य"], [
         ["लग्न (Ascendant)", "वृषभ (Taurus) 14° 52'", "लग्न स्वामी", "शुक्र (Venus)"],
         ["चंद्र राशि (Rashi)", "वृषभ (Taurus) 06° 18'", "राशि स्वामी", "शुक्र (Venus)"],
         ["नक्षत्र और पद", "कृतिका - पद 3", "नक्षत्र स्वामी", "सूर्य (Sun)"],
         ["जन्म तिथि", "कृष्ण सप्तमी", "वार (दिन)", "बुधवार / शुक्र का प्रभाव"],
         ["योग और करण", "वरीयान / बालव", "गण और योनि", "राक्षस / मेष"],
         ["नाड़ी और वर्ण", "अंत्य / वैश्य", "पाया (पैर)", "स्वर्ण (Gold)"],
         ["सूर्य राशि (वैदिक)", "कन्या (Virgo)", "सक्रिय दशा", "शनि / बुध"]
     ], [45, 45, 45, 45]), [
        ("1. वार और तिथि का प्रभाव", "मजबूत शुक्र और बुध के प्रभाव के साथ जन्मे, जातक में परिष्कृत सौंदर्य संवेदनाओं के साथ तेज विश्लेषणात्मक बुद्धि है। कृष्ण पक्ष का जन्म प्राकृतिक लचीलापन प्रदान करता है, जो शुरुआती बाधाओं को सफलता की सीढ़ियों में बदल देता है।"),
        ("2. लग्न और राशि स्तंभ (वृषभ)", "वृषभ लग्न और उच्च के चंद्रमा के साथ, आप ईंट दर ईंट जीवन का निर्माण करते हैं। आप शांत विश्वसनीयता, दृढ़ संकल्प और गुणवत्ता के प्रति रुचि प्रदर्शित करते हैं।"),
        ("3. नक्षत्र स्तंभ (कृतिका / रोहिणी धुरी)", "यह तारकीय हस्ताक्षर रचनात्मक उर्वरता के साथ-साथ सत्य की धार प्रदान करता है। आप झूठे दिखावे को सीधे काटते हैं और अपने परिवार की दृढ़ता से रक्षा करते हैं।")
    ]),
    ("05", "ग्रहीय स्थिति और अष्टकवर्ग", "सटीक नाक्षत्र देशांतर, नक्षत्र स्वामी, उप-स्वामी और बिंदु",
     (["ग्रह", "राशि", "डिग्री", "नक्षत्र", "राशि स्वामी", "नक्षत्र स्वामी", "उप-स्वामी", "स्थिति"], [
         ["लग्न", "वृषभ", "14° 52'", "रोहिणी-2", "शुक्र", "चंद्रमा", "गुरु", "वर्गोत्तम"],
         ["सूर्य", "कन्या", "12° 06'", "हस्त-1", "बुध", "चंद्रमा", "चंद्रमा", "मित्र"],
         ["चंद्र", "वृषभ", "06° 18'", "कृतिका-3", "शुक्र", "सूर्य", "शुक्र", "उच्च (Exalted)"],
         ["मंगल", "तुला", "29° 18'", "विशाखा-3", "शुक्र", "गुरु", "मंगल", "आत्मकारक"],
         ["बुध", "कन्या", "02° 14'", "उ.फाल्गुनी", "बुध", "सूर्य", "शनि", "उच्च (Exalted)"],
         ["गुरु(R)", "मीन", "01° 52'", "पू.भाद्र-4", "गुरु", "गुरु", "शुक्र", "स्वराशि"],
         ["शुक्र", "तुला", "14° 10'", "स्वाति-3", "शुक्र", "राहु", "बुध", "मूलत्रिकोण"],
         ["शनि", "कन्या", "14° 02'", "हस्त-2", "बुध", "चंद्रमा", "राहु", "योगकारक"],
         ["राहु", "धनु", "09° 11'", "मूल-3", "गुरु", "केतु", "शुक्र", "8H शोध"],
         ["केतु", "मिथुन", "09° 11'", "आर्द्रा-1", "बुध", "राहु", "राहु", "2H विरक्ति"]
     ], [22, 20, 18, 24, 20, 20, 20, 36]), [
        ("सर्वाष्टकवर्ग सारांश (प्रति भाव बिंदु बल)", "H1: 31 | H2: 27 | H3: 30 | H4: 29 | H5: 26 | H6: 32 | H7: 25 | H8: 22 | H9: 29 | H10: 33 | H11: 35 | H12: 20. कारण: 10वें भाव में 33 बिंदु और 11वें भाव में 35 बिंदु (फलदीपिका नियम) यह गारंटी देते हैं कि करियर के प्रयास उच्च वित्तीय लाभ देते हैं।")
    ]),
    ("06", "व्यक्तिगत ग्रहीय प्रोफाइल (सूर्य से गुरु तक)", "प्रत्येक ग्रह स्थिति, स्वामित्व और दृष्टि के अनुसार कैसे कार्य करता है", None, [
        ("1. सूर्य (पंचम भाव में चतुर्थेश - कन्या)", "सूर्य आपके घर के चौथे भाव पर शासन करता है और 5वें भाव में बैठता है। आपकी भावनात्मक सुरक्षा बौद्धिक उपलब्धि से जुड़ी है। 11वें भाव पर सूर्य की 7वीं दृष्टि अचल संपत्ति और शिक्षा को उच्च वित्तीय लाभ से जोड़ती है।"),
        ("2. चंद्रमा (लग्न में उच्च का तृतीयेश - वृषभ)", "चंद्रमा पहले भाव में वृषभ राशि में उच्च का है। असाधारण भावनात्मक आकर्षण, स्मृति प्रतिधारण और अंतर्ज्ञान प्रदान करता है। 7वें भाव पर चंद्रमा की 7वीं दृष्टि एक समर्पित जीवनसाथी लाती है।"),
        ("3. मंगल (छठे/सातवें कस्प में 7वां और 12वां स्वामी)", "मंगल साझेदारी (7वें) और दूर के देशों (12वें) को नियंत्रित करता है। आप रिश्तों में भयंकर वफादारी और सुरक्षात्मक आग लाते हैं। आप व्यापार या विवाह में बेईमानी बर्दाश्त नहीं करते हैं।"),
        ("4. बुध (5वें भाव में उच्च का द्वितीयेश और पंचमेश - कन्या)", "बुध उच्च अवस्था में धन (2रे) और बुद्धि (5वें) पर शासन करता है। एक शीर्ष स्तर का धन-सह-बुधादित्य योग बनाता है। आपके गणितीय और विश्लेषणात्मक कौशल सीधे मूर्त धन में परिवर्तित होते हैं।"),
        ("5. गुरु (11वें भाव में 8वां और 11वां स्वामी - मीन)", "गुरु 11वें भाव में अपनी ही राशि मीन में विराजमान है। गुरु की 5वीं दृष्टि संचार (3H) को आशीर्वाद देती है; इसकी 7वीं दृष्टि शिक्षा/बच्चों (5H) की रक्षा करती है; इसकी 9वीं दृष्टि विवाह (7H) की रक्षा करती है।")
    ]),
    ("07", "व्यक्तिगत ग्रहीय प्रोफाइल (शुक्र से केतु तक)", "बाहरी ग्रह, छाया नोड्स और प्रमुख युति", None, [
        ("6. शुक्र (स्वराशि तुला में लग्नेश और षष्ठेश)", "लग्न स्वामी शुक्र अपनी मूलत्रिकोण राशि तुला में बैठता है। आप कूटनीति, आकर्षण और क्षमता के माध्यम से प्रतिद्वंद्वियों पर विजय प्राप्त करते हैं। कानून, चिकित्सा, वित्त, डिजाइन और प्रबंधन में उत्कृष्ट।"),
        ("7. शनि (5वें भाव में योगकारक 9वां और 10वां स्वामी)", "वृषभ लग्न के लिए, शनि भाग्य (9H) और करियर (10H) पर शासन करता है। गहरी एकाग्रता और जटिल प्रणालियों पर महारत देता है। 7H पर शनि की 3री दृष्टि परिपक्वता के लिए विवाह में थोड़ी देरी करती है; 11H पर इसकी 7वीं दृष्टि स्थिर धन सुनिश्चित करती है।"),
        ("8. राहु 8वें भाव में (धनु) और केतु 2रे भाव में (मिथुन)", "नोडल धुरी 2रे/8वें वित्तीय अक्ष को काटती है। 8H में राहु अलौकिक अनुसंधान अंतर्ज्ञान और अचानक अप्रत्याशित लाभ देता है। 2H में केतु वाणी को कुंद बनाता है; पारिवारिक कूटनीति का अभ्यास करें।"),
        ("9. प्रमुख युति: सूर्य + शनि + बुध कन्या राशि में", "जब दूसरा/5वां स्वामी (बुध), चौथा स्वामी (सूर्य), और 9वां/10वां स्वामी (शनि) कन्या राशि में मिलते हैं, तो जातक के पास एक कार्यकारी विश्लेषक दिमाग होता है जो संरचित, लंबे समय तक चलने वाले संस्थागत साम्राज्य बनाने में सक्षम होता है।")
    ]),
    ("08", "भावफल: भाव 1 से 6 तक जीवन", "कारक, भाव स्वामी की स्थिति और व्यावहारिक अभिव्यक्तियाँ", None, [
        ("पहला भाव (तनु भाव - वृषभ): जीवन शक्ति और व्यक्तित्व", "शुक्र द्वारा शासित, उच्च चंद्रमा द्वारा कब्जा कर लिया गया। आपके पास एक चुंबकीय, जमीन से जुड़ा व्यक्तित्व, मजबूत संविधान और उच्च सार्वजनिक संबंध क्षमता है।"),
        ("दूसरा भाव (धन भाव - मिथुन): धन, वाणी और परिवार", "उच्च बुध द्वारा शासित, केतु द्वारा कब्जा कर लिया गया, शनि द्वारा दृष्ट। 26 वर्ष की आयु के बाद वित्तीय संचय तेज हो जाता है। पारिवारिक बातचीत के दौरान वाणी को गर्म रखें।"),
        ("तीसरा भाव (सहज भाव - कर्क): साहस और संचार", "उच्च चंद्रमा द्वारा शासित, गुरु की 5वीं दृष्टि से धन्य। आपके संचार में ज्ञान और अधिकार है। डिजिटल मीडिया और लेखन मान्यता लाते हैं।"),
        ("चौथा भाव (सुख भाव - सिंह): माता, घर और वाहन", "सूर्य (5H में) द्वारा शासित। घरेलू वातावरण गरिमापूर्ण और शिक्षा-केंद्रित है। आप स्व-अर्जित धन के माध्यम से लक्जरी वाहन और प्रमुख अचल संपत्ति प्राप्त करेंगे।"),
        ("5वां भाव (पुत्र/विद्या भाव - कन्या): बुद्धि और रोमांस", "उच्च बुध, सूर्य और योगकारक शनि द्वारा कब्जा कर लिया गया, गुरु द्वारा दृष्ट। यह आपके चार्ट का पावरहाउस घर है, जो अकादमिक गौरव की गारंटी देता है।"),
        ("छठा भाव (रिपु/रोग भाव - तुला): कार्य, प्रतिद्वंद्वी और स्वास्थ्य", "स्वराशि शुक्र द्वारा कब्जा कर लिया गया। आप प्रतियोगी परीक्षाओं और संरचित कॉर्पोरेट वातावरण में पनपते हैं। गुर्दे के जलयोजन और पीठ के निचले हिस्से की मुद्रा बनाए रखें।")
    ]),
    ("09", "भावफल: भाव 7 से 12 तक जीवन", "साझेदारी, दीर्घायु, भाग्य, करियर, लाभ और मुक्ति", None, [
        ("7वां भाव (जाया भाव - वृश्चिक): विवाह और अनुबंध", "मंगल द्वारा शासित, गुरु की 9वीं दृष्टि और चंद्रमा की 7वीं दृष्टि प्राप्त कर रहा है। आप गहरी, सब-या-कुछ नहीं वफादारी चाहते हैं। गुरु एक बुद्धिमान, समर्पित जीवनसाथी सुनिश्चित करता है।"),
        ("8वां भाव (रंध्र भाव - धनु): दीर्घायु और अनुसंधान", "गुरु (11H में) द्वारा शासित, राहु द्वारा कब्जा कर लिया गया। मजबूत दीर्घायु और कराधान, अनुसंधान, या गुप्त विज्ञान में सफलता। सट्टा जुए से बचें।"),
        ("9वां भाव (धर्म भाव - मकर): भाग्य और गुरु", "योगकारक शनि द्वारा शासित। आपका भाग्य अनुशासन, नैतिकता और दीर्घकालिक दृढ़ता के माध्यम से सक्रिय होता है। पिता और गुरुओं के साथ मजबूत कर्म बंधन।"),
        ("10वां भाव (कर्म भाव - कुंभ): करियर और प्रसिद्धि", "शनि द्वारा शासित (5H में स्थित)। करियर में बड़े संगठन, वित्त, प्रौद्योगिकी, कानून या संस्थागत शासन शामिल हैं। अडिग पेशेवर वृद्धि।"),
        ("11वां भाव (लाभ भाव - मीन): लाभ और नेटवर्क", "स्वराशि गुरु (R) द्वारा कब्जा कर लिया गया और सूर्य, बुध और शनि द्वारा दृष्ट। एक विशाल धन-लाभ योग बनाता है। कई आय धाराएं इच्छाओं को पूरा करती हैं।"),
        ("12वां भाव (व्यय भाव - मेष): विदेश और मुक्ति", "मंगल द्वारा शासित। व्यय आत्म-विकास और संपत्ति की ओर निर्देशित है। अंतरराष्ट्रीय सहयोग और बहुराष्ट्रीय करियर भूमिकाओं के लिए अनुकूल।")
    ]),
    ("10", "मल्टी-सिस्टम पीयर रिव्यू और एकीकृत फैसला", "केपी, बीपीएचएस, जैमिनी, फलदीपिका और लघु पाराशरी का क्रॉस-एग्जामिनेशन",
     (["जीवन क्षेत्र", "बीपीएचएस / पाराशरी", "केपी सिस्टम", "जैमिनी सूत्र", "अंतिम फैसला"], [
         ["धन और स्थिति", "उच्च 2L/5L + 11L 11H में", "11वां उप-स्वामी गुरु/शुक्र", "AK/AmK 11H से जुड़ा", "एकीकृत: उच्च धन"],
         ["करियर डोमेन", "5H में योगकारक शनि", "10वां उप-स्वामी 5-6-10-11", "10H में कारकांश", "एकीकृत: कार्यकारी"],
         ["विवाह का समय", "शनि की तीसरी दृष्टि देरी करती है", "7वां उप-स्वामी 2-7-11", "स्वराशि में DK गुरु", "संघर्ष: आयु 25 बनाम 28"],
         ["मांगलिक प्रभाव", "मंगल 7H को प्रभावित करता है", "गुरु की 9वीं दृष्टि बचाती है", "मजबूत DK रक्षा करता है", "एकीकृत: रद्द (Cancelled)"]
     ], [30, 42, 38, 38, 32]), [
        ("1. जहां सभी 6 सिस्टम सहमत हैं (100% एकीकृत फैसले)", "बौद्धिक और वित्तीय महारत: बीपीएचएस (उच्च दूसरा/5वां स्वामी बुध + स्व-राशि 11वां स्वामी गुरु), केपी, फलदीपिका (11H में 35 बिंदु), और जैमिनी सर्वसम्मति से उच्च वित्तीय स्वतंत्रता और कार्यकारी अधिकार की पुष्टि करते हैं।"),
        ("2. जहां सिस्टम भिन्न होते हैं और तकनीकी तर्क", "विवाह का समय: बीपीएचएस देरी के कारण के रूप में 7वें भाव पर शनि की तीसरी दृष्टि को चिह्नित करता है। हालांकि, केपी और फलदीपिका इस डर को खत्म करते हैं क्योंकि मीन राशि में गुरु 7वें भाव पर सटीक 9वीं त्रिकोणीय दृष्टि डालता है, जो एक दिव्य ढाल के रूप में कार्य करता है। फैसला: 26-28 वर्ष की आयु के आसपास विवाह स्थिर और समृद्ध होगा।")
    ]),
    ("11", "जैमिनी चर कारक: 7 आत्मा संकेतक", "ग्रहीय डिग्री (जैमिनी सूत्र) के माध्यम से आत्मा के उद्देश्य को डिकोड करना",
     (["चर कारक", "ग्रह और डिग्री", "जैमिनी भूमिका", "जीवन अभिव्यक्ति"], [
         ["आत्मकारक (AK)", "मंगल (29° 18')", "आत्मा राजा और प्राथमिक पाठ", "साहस, धैर्य में महारत हासिल करना"],
         ["अमात्यकारक (AmK)", "शुक्र (14° 10')", "करियर और पेशेवर वृद्धि", "कूटनीतिक नेतृत्व, विलासिता"],
         ["भ्रातृकारक (BK)", "शनि (14° 02')", "भाई-बहन, गुरु और निष्पादन", "संरचित दृढ़ता"],
         ["मातृकारक (MK)", "सूर्य (12° 06')", "माता, अभयारण्य और संपत्ति", "गरिमापूर्ण घरेलू मूल्य"],
         ["पुत्रकारक (PK)", "चंद्र (06° 18')", "रचनात्मकता और भविष्य की संतान", "सहानुभूतिपूर्ण मेंटरशिप"],
         ["ज्ञातिकारक (GK)", "बुध (02° 14')", "प्रतियोगिता और समस्या-समाधान", "तर्क के माध्यम से प्रतिद्वंद्वियों को हराना"],
         ["दारकारक (DK)", "गुरु (01° 52')", "जीवनसाथी और साथी की प्रकृति", "बुद्धिमान, नैतिक, सुरक्षात्मक जीवनसाथी"]
     ], [36, 32, 52, 60]), [
        ("आत्मकारक (मंगल) + अमात्यकारक (शुक्र) संश्लेषण", "मंगल के आत्मकारक होने से, आपकी आत्मा आंतरिक धैर्य में महारत हासिल करते हुए निडर पहल विकसित करने के लिए यहां है। क्योंकि शुक्र अपनी ही राशि में अमात्यकारक के रूप में कार्य करता है, आपका करियर कूटनीतिक अनुग्रह (शुक्र) के साथ योद्धा जैसी ड्राइव (मंगल) का मिश्रण है।"),
        ("दारकारक (मीन राशि में गुरु) - सोलमेट ब्लूप्रिंट", "जैमिनी ज्योतिष में, सबसे कम डिग्री वाला ग्रह (मीन राशि में 01° 52' पर गुरु) आपके जीवनसाथी का प्रतिनिधित्व करता है। 11वें भाव में अपनी ही राशि में गुरु एक ऐसे साथी को इंगित करता है जो कुलीन, आर्थिक रूप से निपुण है, और आपके सबसे बड़े दोस्त के रूप में कार्य करता है।")
    ]),
    ("12", "प्रेम, विवाह और मांगलिक मूल्यांकन", "5वां भाव रोमांस, 7वां भाव प्रतिबद्धता और विवाह की खिड़कियां",
     (["चरण", "अनुमानित समयरेखा", "ऑपरेटिंग दशा", "ज्योतिषीय रेटिंग"], [
         ["विंडो 1", "2035 के अंत - 2036 के मध्य (आयु 25-26)", "शनि MD - शुक्र AD", "अच्छा (प्रारंभिक प्रस्ताव)"],
         ["विंडो 2", "2037 की शुरुआत - 2038 के अंत (आयु 27-28)", "शनि MD - सूर्य/चंद्र AD", "उत्कृष्ट (चरम सद्भाव)"],
         ["विंडो 3", "2039 के मध्य - 2040 के अंत (आयु 29-30)", "शनि MD - मंगल/राहु AD", "मजबूत (करियर के बाद का मिलन)"]
     ], [25, 55, 50, 50]), [
        ("5वां भाव और 7वां भाव संबंध गतिशीलता", "5वें भाव में कन्या (शनि + सूर्य + बुध) और 7वें भाव में वृश्चिक के साथ, आप प्यार को हल्के में नहीं लेते हैं। आकस्मिक रिश्ते आपकी रुचि नहीं रखते हैं। आप अपना दिल खोलने से पहले साथी की बुद्धि और सत्यनिष्ठा का परीक्षण करते हैं।"),
        ("संपूर्ण मांगलिक दोष तकनीकी लेखा परीक्षा", "मंगल 7वें और 12वें भाव पर शासन करता है, जिससे एक हल्का मांगलिक हस्ताक्षर बनता है। फलदीपिका और बीपीएचएस नियमों के तहत, अपनी स्वराशि मीन से 7वें भाव पर गुरु की सीधी 9वीं दृष्टि अकारक मंगल की गर्मी को पूरी तरह से बेअसर कर देती है। 26 वर्ष की आयु के बाद विवाह भावनात्मक परिपक्वता सुनिश्चित करता है।")
    ]),
    ("13", "करियर कॉलिंग, धन और राज योग", "10वां भाव कमांड, धन योग और आदर्श व्यावसायिक क्षेत्र", None, [
        ("चार्ट में मौजूद शीर्ष राज योग और धन योग", "1. धर्म-कर्म अधिपति योग (5वें त्रिकोण में 9वें और 10वें स्वामी के रूप में शनि): वरिष्ठ प्रबंधन या स्वतंत्र अधिकार के लिए अजेय वृद्धि। 2. उच्च बुधादित्य और धन योग: बुद्धिमत्ता को सीधे धन सृजन से जोड़ता है। 3. लाभ बृहस्पति योग: आजीवन वित्तीय तरलता की गारंटी देता है। 4. विपरीत राज योग पैटर्न: प्रतिद्वंद्वियों पर विजय।"),
        ("आदर्श करियर और व्यावसायिक क्षेत्र", "प्राथमिक धाराएँ: कॉर्पोरेट वित्त, चार्टर्ड अकाउंटेंसी, निवेश बैंकिंग, फिनटेक, डेटा साइंस, या एक्चुरियल एनालिटिक्स। "
         "माध्यमिक धाराएँ: कानून, सिविल/प्रशासनिक सेवाएँ, कॉर्पोरेट प्रशासन, चिकित्सा, या लक्जरी ब्रांड प्रबंधन। "
         "संरचित कॉर्पोरेट भूमिका (आयु 22-30) के बाद परामर्श/उद्यम (आयु 31+)।")
    ]),
    ("14", "राहु-केतु अक्ष और साढ़े साती यात्रा", "छाया ग्रह के पाठ और शनि के 7.5 साल के परिवर्तन चक्र",
     (["चक्र", "चरण और राशि", "समयरेखा", "मुख्य प्रभाव और रणनीति"], [
         ["चक्र 1", "उदय चरण (मेष)", "मध्य 2027 - मध्य 2029", "चंद्रमा से 12वां: अकादमिक फोकस और नींद का अनुशासन"],
         ["चक्र 1", "शिखर चरण (वृषभ)", "मध्य 2029 - मध्य 2032", "जन्म चंद्रमा पर: उच्च शिक्षा की कठोरता और परिपक्वता"],
         ["चक्र 1", "अस्त चरण (मिथुन)", "मध्य 2032 - मध्य 2034", "चंद्रमा से दूसरा: पहली बड़ी नौकरी और आय स्थिरता"],
         ["चक्र 2", "पूर्ण 7.5-वर्षीय चक्र", "2056 - 2064", "शिखर कार्यकारी समेकन और विरासत निर्माण"]
     ], [25, 45, 40, 70]), [
        ("8वें भाव (धनु) में राहु और 2रे भाव (मिथुन) में केतु", "राहु आपको गहरे शोध, मनोविज्ञान और छिपे हुए वित्तीय तंत्र की ओर खींचता है। दूसरे भाव में केतु आपको सतही छोटी बातों से अलग करता है; गर्मजोशी से संचार का अभ्यास करें और निवेश को दीर्घकालिक संपत्तियों में स्वचालित करें।"),
        ("वान्या की साढ़े साती रचनात्मक क्यों है (2027-2034)", "चूंकि वृषभ लग्न के लिए शनि योगकारक ग्रह है और चंद्रमा वृषभ राशि में उच्च का है, इसलिए साढ़े साती कॉलेज और शुरुआती करियर के वर्षों के दौरान एक सख्त अकादमिक और पेशेवर बूट कैंप के रूप में कार्य करती है, जो असाधारण अनुशासन बनाती है।")
    ]),
    ("15", "विंशोत्तरी दशा समयरेखा (2010 - 2048)", "ग्रह अवधि समयरेखा और सूक्ष्म अवधि की भविष्यवाणियां",
     (["दशा अवधि", "वर्ष", "आयु", "प्रमुख जीवन घटनाएँ और ज्योतिषीय तर्क"], [
         ["सूर्य/चंद्र/मंगल MD", "जन्म - 2029", "आयु 0 - 19", "मजबूत स्कूली शिक्षा, कलात्मक स्वभाव, प्रतिस्पर्धी भावना।"],
         ["शनि - शनि", "2029 - 2032", "आयु 19 - 22", "गहन कॉलेज अध्ययन, कड़ी मेहनत, मूलभूत डिग्री।"],
         ["शनि - बुध", "2032 - 2035", "आयु 22 - 25", "उत्कृष्ट: उच्च बुध शीर्ष करियर ब्रेक लाता है।"],
         ["शनि - केतु", "2035 - 2036", "आयु 25 - 26", "संक्षिप्त आत्मनिरीक्षण; आवेगी नौकरी बदलने से बचें।"],
         ["शनि - शुक्र", "2036 - 2039", "आयु 26 - 29", "शानदार: पदोन्नति, लक्जरी संपत्ति, विवाह खिड़की।"],
         ["शनि - सूर्य", "2039 - 2040", "आयु 29 - 30", "अधिकार की भूमिका, प्रबंधन/सरकारी मान्यता।"],
         ["शनि - चंद्र", "2040 - 2042", "आयु 30 - 32", "भावनात्मक पूर्ति, परिवार विस्तार, यात्रा।"],
         ["शनि - मंगल", "2042 - 2043", "आयु 32 - 33", "साहसिक संपत्ति खरीद या उद्यम विस्तार।"],
         ["शनि - राहु", "2043 - 2046", "आयु 33 - 36", "तकनीकी/विदेशी छलांग; तनाव से बचाव करें।"],
         ["शनि - गुरु", "2046 - 2048", "आयु 36 - 38", "प्रमुख धन समेकन और वरिष्ठ नेतृत्व।"]
     ], [36, 26, 24, 94]), [
        ("डीप-डाइव: योगकारक शनि महादशा (आयु 19 से 38)", "युवा और करियर-निर्माण के वर्षों (आयु 19-38) के दौरान योगकारक शनि की 19 वर्षीय महादशा का चलना इस चार्ट में सबसे बड़ा उपहार है। उसके 20 और 30 के दशक में निवेश किए गए प्रयास के हर औंस स्थायी धन में परिवर्तित हो जाएंगे।")
    ]),
    ("16", "विंशोत्तरी दशा समयरेखा (2048 - 2092)", "चरम परिपक्वता, उच्च बुध महादशा और दीर्घकालिक विरासत",
     (["दशा अवधि", "वर्ष", "आयु", "प्रमुख जीवन घटनाएँ और ज्योतिषीय तर्क"], [
         ["बुध - बुध", "2048 - 2051", "आयु 38 - 41", "चरम धन: उच्च 2/5 स्वामी बड़े लाभ को ट्रिगर करता है।"],
         ["बुध - केतु", "2051 - 2052", "आयु 41 - 42", "आध्यात्मिक अंतर्दृष्टि और शोध में सफलता।"],
         ["बुध - शुक्र", "2052 - 2055", "आयु 42 - 45", "लक्जरी अचल संपत्ति, सलाहकार/कलात्मक शिखर।"],
         ["बुध - सूर्य", "2055 - 2056", "आयु 45 - 46", "बोर्डरूम कमांड और संस्थागत सम्मान।"],
         ["बुध - चंद्र", "2056 - 2057", "आयु 46 - 47", "शांतिपूर्ण घरेलू जीवन, बच्चों के मील के पत्थर।"],
         ["बुध - मंगल", "2057 - 2058", "आयु 47 - 48", "निर्णायक संपत्ति विस्तार और उद्यम विकास।"],
         ["बुध - राहु", "2058 - 2061", "आयु 48 - 51", "वैश्विक निवेश और नवीन वित्तीय रणनीति।"],
         ["बुध - गुरु", "2061 - 2063", "आयु 51 - 53", "उच्च परोपकार, मेंटरशिप, और प्रचुर धन।"],
         ["बुध - शनि", "2063 - 2065", "आयु 53 - 55", "स्थायी संस्थागत विरासत और संपत्ति सुरक्षा।"],
         ["केतु और शुक्र MD", "2065 - 2092", "आयु 55 - 82", "लग्नेश शुक्र MD एक शाही, स्वस्थ स्वर्ण युग लाता है।"]
     ], [36, 26, 24, 94]), [
        ("डीप-डाइव: उच्च बुध महादशा (आयु 38 से 55)", "शनि की अनुशासित नींव के बाद, उच्च बुध की 17 वर्षीय महादशा (धन के 2रे घर और बुद्धि के 5वें घर पर शासन करते हुए) जातक को एक उद्योग के नेता, निवेशक और धन निर्माता के रूप में ऊंचा करती है।")
    ]),
    ("17", "कालानुक्रमिक जीवन घटना समयरेखा", "महत्वपूर्ण उम्र, महत्वपूर्ण मोड़ और मील का पत्थर वर्ष को इंगित करना",
     (["आयु", "वर्ष", "मील का पत्थर", "ज्योतिषीय ट्रिगर और मार्गदर्शन"], [
         ["आयु 16 - 18", "2026 - 2028", "स्ट्रीम चयन", "5H कन्या वित्त, तकनीक, कानून या जैव-विज्ञान का पक्षधर है।"],
         ["आयु 19 - 22", "2029 - 2032", "उच्च शिक्षा", "एक प्रमुख संस्थान में गहन अध्ययन चरण।"],
         ["आयु 22 - 24", "2032 - 2034", "पहला करियर ब्रेक", "शनि-बुध AD उच्च-भुगतान वाले प्लेसमेंट को ट्रिगर करता है।"],
         ["आयु 26 - 28", "2036 - 2038", "विवाह मिलन", "शनि-शुक्र/सूर्य AD गुरु की कृपा से 7H को सक्रिय करता है।"],
         ["आयु 29 - 32", "2039 - 2042", "संपत्ति और वाहन", "चतुर्थेश सूर्य और चंद्र AD लक्जरी घर और परिवार लाते हैं।"],
         ["आयु 34 - 38", "2044 - 2048", "कार्यकारी वृद्धि", "शनि-गुरु AD वरिष्ठ नेतृत्व को मजबूत करता है।"],
         ["आयु 39 - 45", "2049 - 2055", "वित्तीय शिखर", "उच्च बुध MD कई गुना संपत्ति वृद्धि उत्पन्न करता है।"]
     ], [24, 26, 38, 92]), [
        ("गंभीर सावधानी के वर्ष (जब अतिरिक्त सावधानी बरतनी हो)", "2029 के अंत से 2031 की शुरुआत तक (आयु 19-20): शनि-शनि के अतिव्यापी शिखर साढ़े साती; अकादमिक बर्नआउट से बचें। 2035 (आयु 25): शनि-केतु संक्रमण; जल्दबाजी में नौकरी बदलने से बचें। 2043-2045 (आयु 33-35): शनि-राहु अवधि; संयुक्त संपत्ति समझौतों पर हस्ताक्षर करने से पहले पूरी तरह से कानूनी जांच करें।")
    ]),
    ("18", "केपी सिस्टम: कस्पल सब-लॉर्ड्स और सिग्निफिकेटर्स", "कृष्णमूर्ति पद्धति तारकीय और उप-स्वामी मैट्रिक्स",
     (["केपी कस्प", "राशि", "राशि L.", "नक्षत्र L.", "उप L.", "भाव महत्व और फैसला"], [
         ["कस्प 1 (स्वयं)", "वृषभ", "शुक्र", "चंद्र", "गुरु", "1, 3, 11 (मजबूत स्वास्थ्य और आशावाद)"],
         ["कस्प 2 (धन)", "मिथुन", "बुध", "राहु", "शनि", "2, 5, 9, 10 (स्थिर धन संचय)"],
         ["कस्प 5 (बुद्धि)", "कन्या", "बुध", "चंद्र", "बुध", "2, 5, 6, 11 (प्रतियोगी परीक्षा में सफलता)"],
         ["कस्प 6 (सेवा)", "तुला", "शुक्र", "राहु", "शुक्र", "1, 6, 11 (प्रतिद्वंद्वियों पर विजय)"],
         ["कस्प 7 (विवाह)", "वृश्चिक", "मंगल", "शनि", "गुरु", "5, 7, 11 (सामंजस्यपूर्ण, समृद्ध मिलन)"],
         ["कस्प 9 (भाग्य)", "मकर", "शनि", "चंद्र", "शुक्र", "1, 6, 9, 10 (लंबी दूरी का भाग्य)"],
         ["कस्प 10 (करियर)", "कुंभ", "शनि", "राहु", "बुध", "2, 5, 6, 10, 11 (उच्च कार्यकारी वृद्धि)"],
         ["कस्प 11 (लाभ)", "मीन", "गुरु", "गुरु", "शुक्र", "1, 6, 11 (इच्छाओं की पूर्ति)"]
     ], [28, 22, 20, 20, 20, 70]), [
        ("करियर और वित्त के लिए केपी स्वर्ण नियम आवेदन", "कृष्णमूर्ति पद्धति में, एक ग्रह अपने नक्षत्र स्वामी के परिणाम देता है, और उप-स्वामी यह तय करता है कि वादा सकारात्मक है या नकारात्मक। चूंकि 10वें कस्प का उप-स्वामी उच्च का बुध (2, 5, 10, 11) है और 11वें कस्प का उप-स्वामी स्वराशि शुक्र है, इसलिए धन और स्थिति का वादा 100% पक्का है।")
    ]),
    ("19", "षड्बल, भाव बल और ग्रहीय अवस्थाएं", "छह-गुना गणितीय शक्ति और ग्रहों की सतर्कता स्थिति",
     (["ग्रह", "विरूप", "रूप", "आवश्यक", "शक्ति %", "अवस्था स्थिति"], [
         ["सूर्य", "412 विरूप", "6.87 रूप", "5.00 रूप", "137% (मजबूत)", "जागृत (Wide Awake)"],
         ["चंद्र", "518 विरूप", "8.63 रूप", "6.00 रूप", "144% (उच्च)", "जागृत (Wide Awake)"],
         ["मंगल", "355 विरूप", "5.91 रूप", "5.00 रूप", "118% (औसत से ऊपर)", "स्वप्न (Dreaming)"],
         ["बुध", "495 विरूप", "8.25 रूप", "7.00 रूप", "118% (उच्च)", "जागृत (Wide Awake)"],
         ["गुरु", "470 विरूप", "7.83 रूप", "6.50 रूप", "120% (मजबूत)", "जागृत (Wide Awake)"],
         ["शुक्र", "460 विरूप", "7.66 रूप", "5.50 रूप", "139% (प्रमुख)", "जागृत (Wide Awake)"],
         ["शनि", "390 विरूप", "6.50 रूप", "5.00 रूप", "130% (योगकारक)", "स्वप्न (Dreaming)"]
     ], [22, 28, 25, 25, 32, 48]), [
        ("षड्बल अनुपात वास्तविक जीवन को कैसे आकार देते हैं", "चंद्रमा (144%), शुक्र (139%), सूर्य (137%), और शनि (130%) अपनी न्यूनतम आवश्यक षड्बल सीमा से कहीं अधिक हैं। जब लग्न स्वामी (शुक्र), चंद्रमा, और योगकारक (शनि) एक साथ 130% से अधिक शक्ति रखते हैं, तो व्यक्ति के पास साथियों से बेहतर प्रदर्शन करने की असाधारण सहनशक्ति होती है।")
    ]),
    ("20", "5-वर्षीय वर्षफल और गोचर पूर्वानुमान (2026-2031)", "वार्षिक ताजिक प्रगति और प्रमुख शनि/गुरु गोचर", None, [
        ("2026 - 2027 (आयु 16 - 17): अकादमिक तीक्ष्णता और फोकस", "कर्क (3H) और सिंह (4H) में गोचर कर रहे उच्च के गुरु आत्मविश्वास, संचार कौशल और मूलभूत बोर्ड/प्रवेश परीक्षा की तैयारी को बढ़ावा देते हैं।"),
        ("2027 - 2028 (आयु 17 - 18): प्रतियोगी परीक्षाएँ और प्रवेश", "गुरु कन्या राशि (जन्मकालीन 5वें भाव सूर्य-बुध-शनि के ऊपर) में गोचर करता है। प्रतियोगी प्रवेश परीक्षाओं को पास करने और एक प्रमुख संस्थान में प्रवेश सुरक्षित करने के लिए यह एक सुनहरा गोचर है। साढ़े साती शुरू होने पर नींद का सख्त कार्यक्रम बनाए रखें।"),
        ("2028 - 2029 (आयु 18 - 19): विश्वविद्यालय में संक्रमण", "गुरु तुला (6H) और वृश्चिक (7H) में गोचर करता है, जो सामाजिक हलकों, mentorships, और संस्थागत मान्यता का विस्तार करता है।"),
        ("2029 - 2031 (आयु 19 - 21): शनि महादशा की शुरुआत", "जैसे ही योगकारक शनि की महादशा शुरू होती है, वान्या गहन परिपक्वता से गुजरती है, जो गंभीर इंटर्नशिप और नेतृत्व कौशल की ओर आकर्षित होती है।")
    ]),
    ("21", "वैदिक अंकशास्त्र और पूर्ण क्या करें और क्या न करें", "मूलांक, भाग्यांक और कार्रवाई योग्य व्यवहारिक रेलिंग",
     (["अंकशास्त्र स्तंभ", "गणना मूल्य", "ग्रह", "रणनीतिक अनुप्रयोग"], [
         ["मूलांक (मनोवैज्ञानिक संख्या)", "2 (29 को जन्म: 2+9=11 -> 2)", "चंद्र", "सहज, कूटनीतिक, रचनात्मक"],
         ["भाग्यांक (भाग्य)", "6 (पूर्ण जन्मतिथि योग)", "शुक्र", "चुंबकीय, कलात्मक, विलासिता-प्रेमी"],
         ["शुभ अंक", "2, 5, 6, 8", "चंद्र/बुध/शुक्र/शनि", "खातों, तारीखों और प्लेटों के लिए उपयोग करें"],
         ["बचने के लिए अंक", "4, 9 (उच्च जोखिम वाले सौदों के लिए)", "राहु / मंगल", "4, 9 तारीख को प्रमुख अनुबंधों से बचें"],
         ["शुभ रंग और दिन", "सफेद, पन्ना हरा, नीला", "शुक्र, बुध, शनि", "परीक्षा और साक्षात्कार के दौरान पहनें"]
     ], [38, 48, 32, 62]), [
        ("स्वर्णिम क्या करें (आदतें जो भाग्य को गुणा करती हैं)", "1. संरचित विश्लेषणात्मक/वाणिज्यिक क्षेत्रों (वित्त, टेक, कानून, मेड) को आगे बढ़ाएं। 2. पूर्व या उत्तर की ओर मुख करके एक अव्यवस्था मुक्त डेस्क बनाए रखें (5H बुध को सक्रिय करता है)। 3. 2रे घर के केतु का मुकाबला करने के लिए दीर्घकालिक संपत्तियों में बचत को स्वचालित करें। 4. चंद्रमा को शांत करने के लिए रोजाना शुद्ध चांदी के गिलास से पानी पिएं।"),
        ("सख्त क्या न करें (बचने के लिए नुकसान)", "1. पूर्णतावाद को कार्रवाई पंगु न करने दें (कन्या 5H क्लस्टर अति-सोच)। 2. तनाव में होने पर परिवार के साथ तेज या व्यंग्यात्मक भाषण का प्रयोग न करें (2H केतु)। 3. 26 वर्ष की आयु से पहले विवाह करने में जल्दबाजी न करें या शारीरिक व्यायाम की उपेक्षा न करें।")
    ])
]

def build_pdf(name, dob, tob, pob, language):
    pdf = KundaliPDF(name, dob, tob, pob, language)

    # P1: COVER
    pdf.add_page()
    pdf.set_y(32)
    pdf.use_font("B", 14)
    pdf.set_text_color(160, 40, 20)
    pdf.cell(0, 8, cln("|| SHRI GANESHAYA NAMAH ||" if language == "English" else "|| श्री गणेशाय नमः ||"), 0, 1, "C")
    pdf.use_font("", 10)
    pdf.set_text_color(100, 50, 30)
    if language == "English":
        pdf.cell(0, 6, "Vakratunda Mahakaya Suryakoti Samaprabha", 0, 1, "C")
        pdf.cell(0, 6, "Nirvighnam Kurume Deva Sarva Karyeshu Sarvada", 0, 1, "C")
    else:
        pdf.cell(0, 6, cln("वक्रतुण्ड महाकाय सूर्यकोटि समप्रभ"), 0, 1, "C")
        pdf.cell(0, 6, cln("निर्विघ्नं कुरु मे देव सर्वकार्येषु सर्वदा"), 0, 1, "C")
        
    pdf.ganesha(105, 88, 44)
    pdf.set_y(120)
    pdf.use_font("B", 20)
    pdf.set_text_color(120, 25, 15)
    
    report_title = f"ADVANCED KUNDALI HELP BOOK ({language.upper()})"
    pdf.cell(0, 10, report_title, 0, 1, "C")
    
    pdf.use_font("B", 11)
    pdf.set_text_color(160, 90, 30)
    if language == "English":
        pdf.cell(0, 7, "Multi-System Synthesis: KP | BPHS | Jaimini | Phaladeepika", 0, 1, "C")
    else:
        pdf.cell(0, 7, cln("मल्टी-सिस्टम संश्लेषण: केपी | बीपीएचएस | जैमिनी | फलदीपिका"), 0, 1, "C")
        
    pdf.set_fill_color(250, 242, 230)
    pdf.set_draw_color(160, 80, 40)
    pdf.rect(25, 145, 160, 52, "DF")
    pdf.set_xy(30, 150)
    pdf.use_font("B", 11)
    pdf.set_text_color(120, 30, 20)
    pdf.cell(150, 7, cln("JATAKA (CLIENT) BIRTH PARTICULARS" if language == "English" else "जातक जन्म विवरण"), 0, 1, "C")
    pdf.use_font("B", 9.5)
    pdf.set_text_color(40, 40, 40)
    
    if language == "English":
        labels = [("Name", name), ("Date of Birth", dob), ("Time of Birth", tob), ("Place of Birth", pob), ("Ayanamsa", "KP New / Lahiri")]
    else:
        labels = [("नाम", name), ("जन्म तिथि", dob), ("जन्म समय", tob), ("जन्म स्थान", pob), ("अयनांश", "केपी न्यू / लाहिरी")]
        
    for lbl, v in labels:
        pdf.set_x(35)
        pdf.cell(140, 7, cln(f"{lbl:<16}: {v}"), 0, 1, "L")
        
    pdf.set_fill_color(140, 35, 20)
    pdf.rect(25, 215, 160, 36, "F")
    pdf.set_xy(25, 220)
    pdf.use_font("B", 13)
    pdf.set_text_color(255, 235, 200)
    pdf.cell(160, 7, cln("CREATED BY: RAJIV KUMAR" if language == "English" else "निर्माता: राजीव कुमार"), 0, 1, "C")
    pdf.use_font("B", 11)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 7, cln("Contact & Consultation: +91-9914465143" if language == "English" else "संपर्क एवं परामर्श: +91-9914465143"), 0, 1, "C")
    pdf.use_font("", 9)
    pdf.set_text_color(240, 220, 200)
    pdf.cell(0, 6, cln("KP & Bhava Jyotish Research Wing | Jalandhar, Punjab" if language == "English" else "केपी और भाव ज्योतिष अनुसंधान विंग | जालंधर, पंजाब"), 0, 1, "C")

    # P2: TOC
    pdf.add_page()
    if language == "English":
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
    else:
        pdf.ch_title("01", "मास्टर विषय सूची", "6 शास्त्रीय प्रणालियाँ एक एकीकृत निर्णय में परिवर्तित होती हैं")
        toc = [
            ["पृष्ठ 01", "पवित्र मंगलाचरण, जातक विवरण और निर्माता विवरण"],
            ["पृष्ठ 02", "मास्टर विषय सूची और मल्टी-सिस्टम कार्यप्रणाली"],
            ["पृष्ठ 03", "अवकाहड़ा चक्र, पंचांग डिकोडेड और तीन स्तंभ"],
            ["पृष्ठ 04", "विजुअल चार्ट: लग्न (D1) और नवमांश (D9) डिग्री के साथ"],
            ["पृष्ठ 05", "विजुअल चार्ट: दशमांश (D10), सप्तमांश (D7) और वर्ग"],
            ["पृष्ठ 06", "ग्रहीय स्थिति तालिका और सर्वाष्टकवर्ग मैट्रिक्स"],
            ["पृष्ठ 07", "व्यक्तिगत ग्रहीय प्रोफाइल: सूर्य, चंद्र, मंगल, बुध, गुरु"],
            ["पृष्ठ 08", "व्यक्तिगत ग्रहीय प्रोफाइल: शुक्र, शनि, राहु, केतु"],
            ["पृष्ठ 09", "भावफल (भाव 1 से 6): स्थिति और स्वामित्व"],
            ["पृष्ठ 10", "भावफल (भाव 7 से 12): स्थिति और स्वामित्व"],
            ["पृष्ठ 11", "मल्टी-सिस्टम संश्लेषण: एकीकृत निर्णय बनाम संघर्ष"],
            ["पृष्ठ 12", "जैमिनी चर कारक: 7 आत्मा संकेतक"],
            ["पृष्ठ 13", "प्रेम, विवाह, दारकारक और मांगलिक मूल्यांकन"],
            ["पृष्ठ 14", "करियर कॉलिंग, धन वास्तुकला और राज योग"],
            ["पृष्ठ 15", "कर्म अक्ष (राहु-केतु) और साढ़े साती चरण"],
            ["पृष्ठ 16", "विंशोत्तरी दशा समयरेखा (जन्म से 2048 तक)"],
            ["पृष्ठ 17", "विंशोत्तरी दशा डीप-डाइव (2048 से 2092 तक)"],
            ["पृष्ठ 18", "कालानुक्रमिक जीवन घटना समयरेखा (विशिष्ट आयु)"],
            ["पृष्ठ 19", "केपी कस्पल उप-स्वामी इंटरलिंक्स और सिग्निफिकेटर्स"],
            ["पृष्ठ 20", "षड्बल, भाव बल और ग्रहीय अवस्थाएं"],
            ["पृष्ठ 21", "5-वर्षीय वर्षफल और गोचर पूर्वानुमान (2026-2031)"],
            ["पृष्ठ 22", "वैदिक अंकशास्त्र और पूर्ण क्या करें और क्या न करें"],
            ["पृष्ठ 23", "वैदिक उपाय हेल्प बुक और कानूनी अस्वीकरण"]
        ]
        pdf.tbl(["पृष्ठ", "अध्याय और अनुभाग सामग्री"], toc, [30, 150])
        pdf.blk("मल्टी-सिस्टम क्रॉस-सत्यापन क्यों मायने रखता है", "यह हेल्प बुक बीपीएचएस, केपी, जैमिनी सूत्र, फलदीपिका, बृहत जातक और लघु पाराशरी का क्रॉस-एग्जामिनेशन करती है। सभी प्रणालियों द्वारा पुष्ट भविष्यवाणियों को 'एकीकृत निर्णय' के रूप में चिह्नित किया गया है, जबकि तकनीकी भिन्नताओं को पारदर्शी रूप से समझाया गया है।")

    # Dynamic Data Loop
    pages_data = EN_PAGES if language == "English" else HI_PAGES
    
    # Page 3: D1 & D9
    pdf.add_page()
    if language == "English":
        pdf.ch_title("03", "VISUAL CHARTS: LAGNA (D1) & NAVAMSHA (D9)", "North Indian Style Natal & Divisional Blueprints")
        c1, c2 = "LAGNA CHART (D1 - RASHI)", "NAVAMSHA CHART (D9)"
        blk1 = ("Technical Chart Synthesis (Why Events Happen)", "1. Vargottama Ascendant (Taurus Rising in D1 & D9): BPHS and Phaladeepika declare the native internally and externally unshakable. Health and status are doubly fortified. 2. 5th House Surya-Shani-Budha Cluster (Virgo): 4th Lord (Sun), Exalted 2nd/5th Lord (Mercury), and Yogakaraka 9th/10th Lord (Saturn) conjoin in the 5th trine, forming a premier Raja Yoga for technical and financial mastery. 3. 6th House Own-Sign Venus (Libra): Lagna Lord Venus sits in its Moolatrikona sign Libra, neutralizing enemies and ensuring competitive exam victories.")
    else:
        pdf.ch_title("03", "विजुअल चार्ट: लग्न (D1) और नवमांश (D9)", "उत्तर भारतीय शैली नेटल और डिविजनल ब्लूप्रिंट")
        c1, c2 = "लग्न चार्ट (D1 - राशि)", "नवमांश चार्ट (D9)"
        blk1 = ("तकनीकी चार्ट संश्लेषण (घटनाएं क्यों होती हैं)", "1. वर्गोत्तम लग्न (D1 और D9 में वृषभ): बीपीएचएस और फलदीपिका जातक को आंतरिक और बाहरी रूप से अडिग घोषित करते हैं। स्वास्थ्य और स्थिति दोगुनी मजबूत होती है। 2. 5वें भाव में सूर्य-शनि-बुध क्लस्टर (कन्या): 4था स्वामी (सूर्य), उच्च 2रा/5वां स्वामी (बुध), और योगकारक 9वां/10वां स्वामी (शनि) 5वें त्रिकोण में मिलते हैं, जो तकनीकी और वित्तीय महारत के लिए एक प्रमुख राज योग बनाते हैं। 3. 6वें भाव में स्वराशि शुक्र (तुला): लग्न स्वामी शुक्र अपनी मूलत्रिकोण राशि तुला में बैठता है, जो दुश्मनों को बेअसर करता है और प्रतियोगी परीक्षा में जीत सुनिश्चित करता है।")
        
    pdf.chart(20, 56, 78, c1, 2, {1:"As\nMo 6°", 2:"Ke 9°", 5:"Su 12°\nSa 14°", 6:"Me 2°\nVe 14°\nMa 29°", 8:"Ra 9°", 11:"Ju(R) 1°"})
    pdf.chart(112, 56, 78, c2, 2, {2:"Su", 3:"Ra", 7:"Me", 9:"Ke", 10:"Mo\nSa", 11:"Ve", 12:"Ma\nJu"})
    pdf.set_y(142)
    pdf.blk(blk1[0], blk1[1])

    # Page 4: D10 & D7
    pdf.add_page()
    if language == "English":
        pdf.ch_title("04", "VISUAL CHARTS: DASHAMSHA (D10) & SAPTAMSHA (D7)", "Career Authority (D10) & Creative Legacy (D7)")
        c3, c4 = "DASHAMSHA (D10 - CAREER)", "SAPTAMSHA (D7 - CREATIVITY)"
        v_h = ["Varga Chart", "Domain", "Ascendant", "Key Verdict"]
        v_r = [
            ["D1 (Rashi)", "Physical Body & Destiny", "Taurus", "Vargottama Strength"],
            ["D2 (Hora)", "Wealth & Accumulation", "Leo/Cancer", "Strong Solar Hora"],
            ["D3 (Drekkana)", "Courage & Initiative", "Virgo", "Analytical Execution"],
            ["D4 (Chaturthamsha)", "Property & Fixed Assets", "Scorpio", "Real Estate Gains"],
            ["D7 (Saptamsha)", "Progeny & Creativity", "Virgo", "Disciplined Output"],
            ["D9 (Navamsha)", "Marriage & Dharma", "Taurus", "High Spouse Loyalty"],
            ["D10 (Dashamsha)", "Career & Command", "Capricorn", "Saturn in 10th: Authority"],
            ["D12 (Dwadashamsha)", "Parents & Lineage", "Sagittarius", "Strong Paternal Karma"]
        ]
    else:
        pdf.ch_title("04", "विजुअल चार्ट: दशमांश (D10) और सप्तमांश (D7)", "करियर अधिकार (D10) और रचनात्मक विरासत (D7)")
        c3, c4 = "दशमांश (D10 - करियर)", "सप्तमांश (D7 - रचनात्मकता)"
        v_h = ["वर्ग चार्ट", "डोमेन", "लग्न", "मुख्य फैसला"]
        v_r = [
            ["D1 (राशि)", "भौतिक शरीर और भाग्य", "वृषभ", "वर्गोत्तम शक्ति"],
            ["D2 (होरा)", "धन और संचय", "सिंह/कर्क", "मजबूत सौर होरा"],
            ["D3 (द्रेष्काण)", "साहस और पहल", "कन्या", "विश्लेषणात्मक निष्पादन"],
            ["D4 (चतुर्थांश)", "संपत्ति और अचल संपत्ति", "वृश्चिक", "अचल संपत्ति लाभ"],
            ["D7 (सप्तमांश)", "संतान और रचनात्मकता", "कन्या", "अनुशासित आउटपुट"],
            ["D9 (नवमांश)", "विवाह और धर्म", "वृषभ", "उच्च जीवनसाथी वफादारी"],
            ["D10 (दशमांश)", "करियर और कमांड", "मकर", "10वें में शनि: अधिकार"],
            ["D12 (द्वादशांश)", "माता-पिता और वंश", "धनु", "मजबूत पैतृक कर्म"]
        ]
    pdf.chart(20, 56, 78, c3, 10, {1:"As\nJu", 2:"Ve", 3:"Mo", 4:"Ma", 5:"Ra", 7:"Su", 9:"Me", 10:"Sa", 11:"Ke"})
    pdf.chart(112, 56, 78, c4, 6, {1:"As", 2:"Ve", 3:"Ma", 4:"Ju", 5:"Sa", 6:"Ra", 9:"Su", 10:"Mo", 11:"Me", 12:"Ke"})
    pdf.set_y(142)
    pdf.tbl(v_h, v_r, [35, 55, 35, 55])

    # Run loop for remaining pages
    for ch_num, title, sub, tbl_info, blocks in pages_data[1:]:
        pdf.add_page()
        pdf.ch_title(ch_num, title, sub)
        if tbl_info:
            pdf.tbl(tbl_info[0], tbl_info[1], tbl_info[2])
        for b_head, b_body in blocks:
            pdf.blk(b_head, b_body)

    # P23: REMEDIES & DISCLAIMER
    pdf.add_page()
    if language == "English":
        pdf.ch_title("22", "VEDIC REMEDIES & LEGAL DECLARATION", "Practical Planetary Alignment & Mandatory Disclaimer")
        rem_h = ["Category", "Recommendation", "Astrological Purpose"]
        rems = [
            ["Gemstone", "Diamond / White Zircon or Emerald", "Strengthens Lagna Lord Venus & Exalted Mercury"],
            ["Rudraksha", "6 Mukhi + 4 Mukhi Rudraksha", "Balances Venusian grace and Mercurial intellect"],
            ["Daily Mantra", "Om Shukraya Namaha / Om Budhaya Namaha", "Chant 27 or 108 times on Fridays & Wednesdays"],
            ["Sade Sati Shield", "Hanuman Chalisa & Shani Gayatri", "Recite on Saturdays to keep Sade Sati smooth"],
            ["Charitable Act", "Donate green moong dal or books", "Perform on Wednesdays to unlock Dhana Yogas"]
        ]
        blk_r = ("Ishtdev & Spiritual Alignment", "With Mercury and Saturn in the 5th house and Jupiter in Pisces in the 11th, offering prayers to Lord Ganesha and Goddess Lakshmi-Narayan brings peace.")
        disc_head = "MANDATORY DECLARATION & LEGAL DISCLAIMER"
        disc = (
            "This Advanced Kundali Help Book has been compiled and created by Rajiv Kumar (Contact: 9914465143). "
            "It is hereby explicitly declared that the creator of this report is NOT a professional or certified commercial astrologer. "
            "This report is generated solely for educational, spiritual, and self-reflective guidance with the help of classical astrological books, "
            "publicly available resources on the internet, mathematical algorithms, and generative AI. "
            "Astrological interpretations across BPHS, KP, Jaimini, and Phaladeepika are indicative tendencies rather than guaranteed fixed outcomes. "
            "Nothing in this document constitutes medical, legal, or licensed financial advice. The creator and editor of this report (Rajiv Kumar) "
            "assumes zero liability and is not responsible for any decisions or consequences arising from data or information in this report."
        )
    else:
        pdf.ch_title("22", "वैदिक उपाय और कानूनी घोषणा", "व्यावहारिक ग्रहीय संरेखण और अनिवार्य अस्वीकरण")
        rem_h = ["श्रेणी", "सिफारिश", "ज्योतिषीय उद्देश्य"]
        rems = [
            ["रत्न", "हीरा / सफेद जिक्रोन या पन्ना", "लग्न स्वामी शुक्र और उच्च बुध को मजबूत करता है"],
            ["रुद्राक्ष", "6 मुखी + 4 मुखी रुद्राक्ष", "शुक्र की कृपा और बुध की बुद्धि को संतुलित करता है"],
            ["दैनिक मंत्र", "ओम शुक्राय नमः / ओम बुधाय नमः", "शुक्रवार और बुधवार को 27 या 108 बार जाप करें"],
            ["साढ़े साती ढाल", "हनुमान चालीसा और शनि गायत्री", "साढ़े साती को सुचारू रखने के लिए शनिवार को पाठ करें"],
            ["परोपकारी कार्य", "हरी मूंग दाल या किताबें दान करें", "धन योग को खोलने के लिए बुधवार को करें"]
        ]
        blk_r = ("इष्टदेव और आध्यात्मिक संरेखण", "5वें भाव में बुध और शनि और 11वें भाव में मीन राशि में गुरु के साथ, भगवान गणेश और देवी लक्ष्मी-नारायण की प्रार्थना करने से शांति मिलती है।")
        disc_head = "अनिवार्य घोषणा और कानूनी अस्वीकरण"
        disc = (
            "यह एडवांस्ड कुंडली हेल्प बुक राजीव कुमार (संपर्क: 9914465143) द्वारा संकलित और बनाई गई है। "
            "यह स्पष्ट रूप से घोषित किया जाता है कि इस रिपोर्ट के निर्माता एक पेशेवर या प्रमाणित वाणिज्यिक ज्योतिषी नहीं हैं। "
            "यह रिपोर्ट पूरी तरह से शैक्षिक, आध्यात्मिक और आत्म-चिंतनशील मार्गदर्शन के लिए शास्त्रीय ज्योतिषीय पुस्तकों, इंटरनेट पर सार्वजनिक रूप से उपलब्ध संसाधनों, गणितीय एल्गोरिदम और जनरेटिव एआई की मदद से तैयार की गई है। "
            "बीपीएचएस, केपी, जैमिनी और फलदीपिका में ज्योतिषीय व्याख्याएं गारंटीकृत निश्चित परिणामों के बजाय सांकेतिक प्रवृत्तियां हैं। "
            "इस दस्तावेज़ में कुछ भी चिकित्सा, कानूनी या लाइसेंस प्राप्त वित्तीय सलाह नहीं है। इस रिपोर्ट के निर्माता और संपादक (राजीव कुमार) कोई दायित्व नहीं लेते हैं और इस रिपोर्ट में डेटा या जानकारी से उत्पन्न होने वाले किसी भी निर्णय या परिणाम के लिए जिम्मेदार नहीं हैं।"
        )
        
    pdf.tbl(rem_h, rems, [34, 66, 80])
    pdf.blk(blk_r[0], blk_r[1])

    pdf.set_y(192)
    pdf.set_fill_color(245, 240, 235)
    pdf.set_draw_color(140, 30, 20)
    pdf.set_line_width(0.6)
    pdf.rect(15, 192, 180, 78, "DF")
    pdf.set_xy(20, 196)
    pdf.use_font("B", 10.5)
    pdf.set_text_color(140, 20, 20)
    pdf.cell(170, 6, cln(disc_head), 0, 1, "C")
    
    pdf.set_xy(20, 203)
    pdf.use_font("", 8.2)
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
        c_name = st.text_input("Full Name of Jataka", "")
        c_dob = st.text_input("Date of Birth (DD/MM/YYYY)", "")
    with c2:
        c_time = st.time_input("Time of Birth", value=None)
        c_pob = st.text_input("Place of Birth (City, State)", "")
        
    c_phone = st.text_input("Client WhatsApp / Contact Number", "")
    sub = st.form_submit_button("Generate 23-Page Master Kundali PDF")

if sub:
    if not c_name or not c_dob or c_time is None or not c_pob:
        st.error("⚠️ Please fill in all the birth particulars (Name, Date, Time, and Place) before generating the report.")
    else:
        with st.spinner(f"Generating 23-Page Master PDF in {language_choice}..."):
            c_tob_str = c_time.strftime("%I:%M %p")
            try:
                requests.post(WEBAPP_URL, json={"name":c_name, "dob":c_dob, "tob":c_tob_str, "pob":c_pob, "phone":c_phone, "language":language_choice, "timestamp":datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")}, timeout=3)
            except Exception:
                pass
                
            pdf_b = build_pdf(c_name, c_dob, c_tob_str, c_pob, language_choice)
            
            st.success(f"23-Page Master Kundali Help Book for {c_name} is ready!")
            st.download_button("Download 23-Page Master Kundali PDF", data=pdf_b, file_name=f"Advanced_Kundali_{c_name.replace(' ', '_')}.pdf", mime="application/pdf")
