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
    # Safely format text without breaking Hindi utf-8 characters
    return str(txt).replace("\u2013", "-").replace("\u2014", "-")

class KundaliPDF(FPDF):
    def __init__(self, name, dob, tob, pob, language):
        super().__init__("P", "mm", "A4")
        self.c_name = name
        self.c_dob = dob
        self.c_tob = tob
        self.c_pob = pob
        self.language = language
        self.set_auto_page_break(False)
        
        # Load fonts and register for all styles to prevent crash
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

    def chart(self, x, y, s, title, data):
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
        pts = {
            1:(0.5,0.25), 2:(0.25,0.1), 3:(0.1,0.25), 4:(0.25,0.5),
            5:(0.1,0.75), 6:(0.25,0.88), 7:(0.5,0.75), 8:(0.75,0.88),
            9:(0.88,0.75), 10:(0.75,0.5), 11:(0.88,0.25), 12:(0.75,0.1)
        }
        self.use_font("B", 7.5)
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
        self.cell(174, 6, cln(f"CHAPTER {num}: {title}"), 0, 0, "L")
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

# ================= EN/HI DICTIONARIES =================
EN_PAGES = [
    ("02", "AVAKAHADA CHAKRA & PANCHANG", "Foundational Astronomical & Natal Alignment",
     (["Parameter", "Natal Value", "Parameter", "Natal Value"], [
         ["Lagna (Ascendant)", "Taurus 14d 52m", "Lagna Lord", "Venus (Shukra)"],
         ["Moon Sign (Rashi)", "Taurus 06d 18m", "Rashi Lord", "Venus (Shukra)"],
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
         ["Atmakaraka (AK)", "Mars (29d 18m)", "Soul King & Primary Lesson", "Courage, mastering patience"],
         ["Amatyakaraka (AmK)", "Venus (14d 10m)", "Career & Professional Rise", "Diplomatic leadership, luxury"],
         ["Bhratrukaraka (BK)", "Saturn (14d 02m)", "Siblings, Mentors & Execution", "Structured perseverance"],
         ["Matrukaraka (MK)", "Sun (12d 06m)", "Mother, Sanctuary & Property", "Dignified domestic values"],
         ["Putrakaraka (PK)", "Moon (06d 18m)", "Creativity & Future Progeny", "Empathetic mentorship"],
         ["Gnatikaraka (GK)", "Mercury (02d 14m)", "Competition & Problem-Solving", "Defeating rivals via logic"],
         ["Darakaraka (DK)", "Jupiter (01d 52m)", "Spouse & Partner Nature", "Wise, ethical, protective spouse"]
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
         ["लग्न (Ascendant)", "वृषभ (Taurus) 14d 52m", "लग्न स्वामी", "शुक्र (Venus)"],
         ["चंद्र राशि (Rashi)", "वृषभ (Taurus) 06d 18m", "राशि स्वामी", "शुक्र (Venus)"],
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
         ["लग्न", "वृषभ", "14d 52m", "रोहिणी-2", "शुक्र", "चंद्रमा", "गुरु", "वर्गोत्तम"],
         ["सूर्य", "कन्या", "12d 06m", "हस्त-1", "बुध", "चंद्रमा", "चंद्रमा", "मित्र"],
         ["चंद्र", "वृषभ", "06d 18m", "कृतिका-3", "शुक्र", "सूर्य", "शुक्र", "उच्च (Exalted)"],
         ["मंगल", "तुला", "29d 18m", "विशाखा-3", "शुक्र", "गुरु", "मंगल", "आत्मकारक"],
         ["बुध", "कन्या", "02d 14m", "उ.फाल्गुनी", "बुध", "सूर्य", "शनि", "उच्च (Exalted)"],
         ["गुरु(R)", "मीन", "01d 52m", "पू.भाद्र-4", "गुरु", "गुरु", "शुक्र", "स्वराशि"],
         ["शुक्र", "तुला", "14d 10m", "स्वाति-3", "शुक्र", "राहु", "बुध", "मूलत्रिकोण"],
         ["शनि", "कन्या", "14d 02m", "हस्त-2", "बुध", "चंद्रमा", "राहु", "योगकारक"],
         ["राहु", "धनु", "09d 11m", "मूल-3", "गुरु", "केतु", "शुक्र", "8H शोध"],
         ["केतु", "मिथुन", "09d 11m", "आर्द्रा-1", "बुध", "राहु", "राहु", "2H विरक्ति"]
     ], [22, 20, 18, 24, 20, 20, 20, 36]), [
        ("सर्वाष्टकवर्ग सारांश (प्रति भाव बिंदु बल)", "H1: 31 | H2: 27 | H3: 30 | H4: 29 | H5: 26 | H6: 32 | H7: 25 | H8: 22 | H9: 29 | H10: 33 | H11: 35 | H12: 20. कारण: 10वें भाव में 33 बिंदु और 11वें भाव में 35 बिंदु (फलदीपिका नियम) यह गारंटी देते हैं कि करियर के प्रयास उच्च वित्तीय लाभ देते हैं।")
    ]),
    ("06", "व्यक्तिगत ग्रहीय प्रोफाइल (सूर्य से गुरु तक)", "प्रत्येक ग्रह स्थिति, स्वामित्व और दृष्टि के अनुसार कैसे कार्य करता है", None, [
        ("1. सूर्य (पंचम भाव में चतुर्थेश - कन्या)", "सूर्य आपके घर के चौथे भाव पर शासन करता है और 5वें भाव में बैठता है। आपकी भावनात्मक सुरक्षा बौद्धिक उपलब्धि से जुड़ी है। 11वें भाव पर सूर्य की 7वीं दृष्टि अचल संपत्ति और शिक्षा को उच्च वित्तीय लाभ से जोड़ती है।"),
        ("2. चंद्रमा (लग्न में उच्च का तृतीयेश - वृषभ)", "चंद्रमा पहले भाव में वृषभ राशि में उच्च का है। असाधारण भावनात्मक आकर्षण, स्मृति प्रतिधारण और अंतर्ज्ञान प्रदान करता है। 7वें भाव पर चंद्रमा की 7वीं दृष्टि एक समर्पित जीवनसाथी लाती है।"),
        ("3. मंगल (छठे/सातवें कस्प में 7वां और 12वां स्वामी)", "मंगल साझेदारी (7वें) और दूर के देशों (12वें) को नियंत्रित करता है। आप रिश्तों में भयंकर वफादारी और सुरक्षात्मक आग लाते हैं। आप व्यापार या विवाह में बेईमानी बर्दाश्त नहीं करते हैं।"),
        ("4. बुध (5वें भाव में उच्च का द्वितीयेश और पंचमेश - कन्या)", "बुध उच्च अवस्था में धन (2रे) और बुद्धि (5वें) पर शासन करता है। एक शीर्ष स्तर का धन-सह-बुधादित्य योग बनाता है। आपके गणितीय और विश्लेषणात्मक कौशल सीधे मूर्त धन में परिवर्तित होते हैं।"),
        ("5. गुरु (11वें भाव में 8वां और 11वां स्वामी - मीन)", "गुरु 11वें भाव में अपनी ही राशि मीन में विराजमान है। गुरु की 5वीं दृष्टि संचार (3H) को आशीर्वाद देती है
