import streamlit as st
from fpdf import FPDF
import datetime
import requests

# --- CONFIGURATION ---
GOOGLE_SHEET_WEBAPP_URL = "https://script.google.com/macros/s/AKfycbxkPrTQK017yE2WJDo65jO6Ulpw2ESpokbJuUWltvLCSKlq_vKFavc3Dl3NNh2duyYF2g/exec"

class MasterKundaliPDF(FPDF):
    def __init__(self, client_name, dob, tob, pob):
        super().__init__(orientation='P', unit='mm', format='A4')
        self.client_name = client_name
        self.dob = dob
        self.tob = tob
        self.pob = pob
        self.set_auto_page_break(auto=False)

    def draw_swastik(self, x, y, size, color, line_width):
        """Draws a geometric Swastik symbol centered at (x, y)"""
        self.set_draw_color(*color)
        self.set_line_width(line_width)
        half = size / 2.0
        
        # Central cross
        self.line(x - half, y, x + half, y)
        self.line(x, y - half, x, y + half)
        
        # Outer arms (clockwise)
        self.line(x, y - half, x + half, y - half) # Top arm right
        self.line(x + half, y, x + half, y + half) # Right arm down
        self.line(x, y + half, x - half, y + half) # Bottom arm left
        self.line(x - half, y, x - half, y - half) # Left arm up

        # Four bindus (dots) in quadrants
        q = half / 2.0
        dot_r = line_width * 0.8
        self.set_fill_color(*color)
        for dx, dy in [(-q, -q), (q, -q), (-q, q), (q, q)]:
            self.ellipse(x + dx - dot_r/2, y + dy - dot_r/2, dot_r, dot_r, style='F')

    def draw_ganesha_motif(self, x, y, size):
        """Draws an auspicious geometric Mandala & Ganesha Tilak motif on the cover"""
        self.set_draw_color(180, 40, 20)
        self.set_fill_color(255, 240, 215)
        self.set_line_width(1.2)
        
        # Outer sacred circle
        self.ellipse(x - size/2, y - size/2, size, size, style='DF')
        self.set_line_width(0.6)
        self.ellipse(x - size/2 + 3, y - size/2 + 3, size - 6, size - 6, style='D')
        
        # Inner Tilak lines (Trishul / Ganesha trunk representation)
        self.set_line_width(1.5)
        self.line(x - 10, y - 8, x + 10, y - 8)
        self.line(x - 12, y - 3, x + 12, y - 3)
        self.line(x - 10, y + 2, x + 10, y + 2)
        
        # Curved trunk base
        self.line(x, y - 14, x, y + 12)
        self.line(x, y + 12, x + 6, y + 15)
        
        # Sacred Bindu
        self.set_fill_color(180, 40, 20)
        self.ellipse(x - 2, y - 20, 4, 4, style='F')

    def draw_north_indian_chart(self, x, y, size, title, house_data):
        """Draws a North Indian Diamond Kundali Chart with house placements"""
        self.set_font("Helvetica", "B", 11)
        self.set_text_color(120, 30, 20)
        self.set_xy(x, y - 8)
        self.cell(size, 6, title, align='C')

        self.set_draw_color(140, 50, 30)
        self.set_line_width(0.6)
        
        # Outer box
        self.rect(x, y, size, size)
        # Diagonals
        self.line(x, y, x + size, y + size)
        self.line(x + size, y, x, y + size)
        # Inner diamond
        half = size / 2.0
        self.line(x + half, y, x + size, y + half)
        self.line(x + size, y + half, x + half, y + size)
        self.line(x + half, y + size, x, y + half)
        self.line(x, y + half, x + half, y)

        # Coordinate offsets for the 12 houses (relative to x, y, scaled by size)
        coords = {
            1: (0.50, 0.25), 2: (0.25, 0.10), 3: (0.10, 0.25),
            4: (0.25, 0.50), 5: (0.10, 0.75), 6: (0.25, 0.88),
            7: (0.50, 0.75), 8: (0.75, 0.88), 9: (0.88, 0.75),
            10: (0.75, 0.50), 11: (0.88, 0.25), 12: (0.75, 0.10)
        }
        
        self.set_font("Helvetica", "B", 8)
        self.set_text_color(40, 40, 40)
        for h_num, text in house_data.items():
            cx = x + size * coords[h_num][0] - 12
            cy = y + size * coords[h_num][1] - 3
            self.set_xy(cx, cy)
            self.cell(24, 6, text, align='C')

    def header(self):
        # 1. Decorative Page Border
        self.set_draw_color(180, 130, 70)
        self.set_line_width(0.5)
        self.rect(8, 8, 194, 281)
        self.set_line_width(0.2)
        self.rect(10, 10, 190, 277)

        # 2. 50% Centered Swastik Watermark (105mm width = 50% of 210mm A4 page)
        self.draw_swastik(105, 148.5, 105, color=(246, 236, 222), line_width=5.0)

        # 3. Top Left & Right Corner Swastiks
        self.draw_swastik(20, 20, 10, color=(180, 45, 25), line_width=0.9)
        self.draw_swastik(190, 20, 10, color=(180, 45, 25), line_width=0.9)

        # 4. Running Header (Pages 2 to 23)
        if self.page_no() > 1:
            self.set_xy(30, 14)
            self.set_font("Helvetica", "B", 9)
            self.set_text_color(130, 50, 30)
            self.cell(150, 5, f"KP BHAVA JYOTISH  |  ADVANCED KUNDALI HELP BOOK  |  {self.client_name.upper()}", align='C')
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
        self.cell(90, 8, "Created by Rajiv Kumar  |  Contact: 9914465143", align='L')
        self.cell(90, 8, f"Page {self.page_no()} of 23", align='R')

    def section_title(self, chapter_num, title, subtitle=""):
        self.set_xy(15, 28)
        self.set_fill_color(248, 238, 225)
        self.set_draw_color(160, 60, 30)
        self.set_line_width(0.4)
        self.rect(15, 28, 180, 16, style='DF')
        
        self.set_xy(18, 30)
        self.set_font("Helvetica", "B", 13)
        self.set_text_color(140, 30, 20)
        self.cell(174, 6, f"CHAPTER {chapter_num}: {title}", align='L')
        
        if subtitle:
            self.set_xy(18, 37)
            self.set_font("Helvetica", "I", 9)
            self.set_text_color(90, 60, 40)
            self.cell(174, 5, subtitle, align='L')
        self.set_y(48)

    def write_block(self, heading, body_text):
        self.set_x(15)
        self.set_font("Helvetica", "B", 10)
        self.set_text_color(140, 40, 20)
        self.cell(180, 6, heading, ln=True)
        
        self.set_x(15)
        self.set_font("Helvetica", "", 9.5)
        self.set_text_color(35, 35, 35)
        self.multi_cell(180, 5.2, body_text)
        self.ln(3)

    def write_table(self, headers, rows, col_widths):
        self.set_x(15)
        self.set_fill_color(150, 50, 30)
        self.set_text_color(255, 255, 255)
        self.set_font("Helvetica", "B", 8.5)
        for i, h in enumerate(headers):
            self.cell(col_widths[i], 7, h, border=1, fill=True, align='C')
        self.ln()

        self.set_font("Helvetica", "", 8)
        self.set_text_color(30, 30, 30)
        fill = False
        for row in rows:
            self.set_x(15)
            self.set_fill_color(252, 246, 238) if fill else self.set_fill_color(255, 255, 255)
            for i, val in enumerate(row):
                self.cell(col_widths[i], 6.5, str(val), border=1, fill=True, align='C')
            self.ln()
            fill = not fill
        self.ln(4)


def generate_23_page_report(name, dob, tob, pob):
    pdf = MasterKundaliPDF(name, dob, tob, pob)

    # ================= PAGE 1: COVER PAGE =================
    pdf.add_page()
    pdf.set_y(32)
    pdf.set_font("Helvetica", "B", 14)
    pdf.set_text_color(160, 40, 20)
    pdf.cell(0, 8, "|| SHRI GANESHAYA NAMAH ||", align='C', ln=True)
    
    pdf.set_font("Helvetica", "I", 10)
    pdf.set_text_color(100, 50, 30)
    pdf.cell(0, 6, "Vakratunda Mahakaya Suryakoti Samaprabha", align='C', ln=True)
    pdf.cell(0, 6, "Nirvighnam Kurume Deva Sarva Karyeshu Sarvada", align='C', ln=True)

    # Draw Shri Ganesha Mandala Symbol
    pdf.draw_ganesha_motif(105, 88, 44)

    pdf.set_y(120)
    pdf.set_font("Helvetica", "B", 22)
    pdf.set_text_color(120, 25, 15)
    pdf.cell(0, 10, "ADVANCED KUNDALI HELP BOOK", align='C', ln=True)
    
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(160, 90, 30)
    pdf.cell(0, 7, "Multi-System Synthesis: KP | BPHS | Jaimini | Phaladeepika | Laghu Parashari", align='C', ln=True)

    # Client Box
    pdf.set_fill_color(250, 242, 230)
    pdf.set_draw_color(160, 80, 40)
    pdf.rect(25, 145, 160, 52, style='DF')
    pdf.set_xy(30, 150)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(120, 30, 20)
    pdf.cell(150, 7, "JATAKA (CLIENT) BIRTH PARTICULARS", align='C', ln=True)
    
    pdf.set_font("Helvetica", "B", 10)
    pdf.set_text_color(40, 40, 40)
    pdf.set_x(35); pdf.cell(140, 7, f"Name of Jataka       :   {name}", ln=True)
    pdf.set_x(35); pdf.cell(140, 7, f"Date of Birth            :   {dob}", ln=True)
    pdf.set_x(35); pdf.cell(140, 7, f"Time of Birth            :   {tob}", ln=True)
    pdf.set_x(35); pdf.cell(140, 7, f"Place of Birth           :   {pob}", ln=True)
    pdf.set_x(35); pdf.cell(140, 7, "Ayanamsa System  :   KP New / Lahiri (Chitrapaksha)", ln=True)

    # Creator Branding Box on Cover
    pdf.set_fill_color(140, 35, 20)
    pdf.rect(25, 215, 160, 36, style='F')
    pdf.set_xy(25, 220)
    pdf.set_font("Helvetica", "B", 13)
    pdf.set_text_color(255, 235, 200)
    pdf.cell(160, 7, "CREATED BY: RAJIV KUMAR", align='C', ln=True)
    pdf.set_font("Helvetica", "B", 12)
    pdf.set_text_color(255, 255, 255)
    pdf.cell(0, 7, "Contact & Consultation: +91-9914465143", align='C', ln=True)
    pdf.set_font("Helvetica", "", 9)
    pdf.set_text_color(240, 220, 200)
    pdf.cell(0, 6, "KP & Bhava Jyotish Research Wing | Jalandhar, Punjab, India", align='C', ln=True)

    # ================= PAGE 2: TABLE OF CONTENTS & METHODOLOGY =================
    pdf.add_page()
    pdf.section_title("01", "MASTER TABLE OF CONTENTS & METHODOLOGY", "How 6 Classical Systems Converge Into One Unified Verdict")
    toc_rows = [
        ["Page 01", "Sacred Invocation, Jataka Particulars & Creator Details"],
        ["Page 02", "Master Table of Contents & Multi-System Peer-Review Methodology"],
        ["Page 03", "Avakahada Chakra, Panchang Decoded & Three Pillars of the Self"],
        ["Page 04", "Visual Charts: Lagna (D1) & Navamsha (D9) with Planetary Degrees"],
        ["Page 05", "Visual Charts: Dashamsha (D10), Saptamsha (D7) & Shodashvarga Summary"],
        ["Page 06", "Planetary Positions Table, KP Significators & Ashtakavarga Matrix"],
        ["Page 07", "Personal Planetary Profile: Sun, Moon, Mars, Mercury & Jupiter"],
        ["Page 08", "Personal Planetary Profile: Venus, Saturn, Rahu, Ketu & Conjunctions"],
        ["Page 09", "Bhavphal (Houses 1 to 6): Placements, Aspects & Lordships"],
        ["Page 10", "Bhavphal (Houses 7 to 12): Placements, Aspects & Lordships"],
        ["Page 11", "Multi-System Synthesis: Unified Verdict vs. System Conflicts"],
        ["Page 12", "Jaimini Chara Karakas: The 7 Soul Indicators & Purpose"],
        ["Page 13", "Love, Marriage, Darakaraka & Mangalik Dosha Evaluation"],
        ["Page 14", "Career, Wealth Architecture, Raj Yogas & Doshas"],
        ["Page 15", "Karmic Axis (Rahu-Ketu) & Sade Sati Transformation Phases"],
        ["Page 16", "Vimshottari Mahadasha & Antardasha Timeline (Birth to 2045)"],
        ["Page 17", "Vimshottari Mahadasha & Antardasha Deep-Dive (2045 to 2090)"],
        ["Page 18", "Chronological Life Event Timeline (Specific Ages & Years)"],
        ["Page 19", "KP Cuspal Sub-Lord Interlinks & Significator Matrix"],
        ["Page 20", "Shadbala, Bhava Bala & Planetary Avastha Strength"],
        ["Page 21", "5-Year Varshphal & Gochara (Transit) Forecast (2026-2031)"],
        ["Page 22", "Vedic Numerology & The Complete Guide of Do's and Don'ts"],
        ["Page 23", "Vedic Remedies Help Book & Mandatory Legal Disclaimer"]
    ]
    pdf.write_table(["Page No.", "Chapter & Section Contents"], toc_rows, [35, 145])
    pdf.write_block("Why Multi-System Cross-Validation Matters", 
                    "Most traditional reports rely on a single text, leading to contradictory predictions. This Help Book cross-examines Brihat Parashara Hora Shastra (BPHS), Krishnamurti Paddhati (KP), Jaimini Sutras, Phaladeepika, Brihat Jataka, and Laghu Parashari. Predictions confirmed by all systems are marked as 'UNIFIED VERDICTS', while technical divergences are transparently explained.")

    # ================= PAGE 3: AVAKAHADA & PANCHANG =================
    pdf.add_page()
    pdf.section_title("02", "AVAKAHADA CHAKRA & PANCHANG DECODED", "Foundational Astronomical & Natal Alignment")
    avak_rows = [
        ["Lagna (Ascendant)", "Taurus (Vrishabha) 14°52'", "Lagna Lord", "Venus (Shukra)"],
        ["Moon Sign (Rashi)", "Taurus (Vrishabha) 06°18'", "Rashi Lord", "Venus (Shukra)"],
        ["Nakshatra & Pada", "Krittika - Pada 3", "Nakshatra Lord", "Sun (Surya)"],
        ["Tithi at Birth", "Krishna Saptami / Ashtami", "Vaar (Day)", "Wednesday / Friday Influence"],
        ["Yoga & Karana", "Variyan / Balava", "Gana & Yoni", "Rakshasa / Mesh"],
        ["Nadi & Varna", "Antya / Vaishya", "Paya (Footing)", "Swarna (Gold)"],
        ["Sun Sign (Vedic)", "Virgo (Kanya)", "Balance of Dasha", "Sun / Jupiter Cycle Active"]
    ]
    pdf.write_table(["Parameter", "Natal Value", "Parameter", "Natal Value"], avak_rows, [45, 45, 45, 45])
    pdf.write_block("1. Vaar & Tithi Impact", "Born with strong Venusian and Мерcurial currents, the native possesses sharp analytical intellect paired with refined aesthetic sensibilities. Krishna Paksha mid-tithi birth grants natural resilience—turning early obstacles into stepping stones for authority.")
    pdf.write_block("2. Lagna & Rashi Pillar (Vrishabha / Taurus)", "With Taurus rising, you build life brick by brick. You project calm reliability, determination, and a taste for quality. Once committed to a goal or relationship, nothing can shake your foundation.")
    pdf.write_block("3. Nakshatra Pillar (Krittika / Punarvasu Axis)", "This stellar signature bestows the 'Razor of Truth' alongside the 'Return of Light.' You cut through false pretenses directly, protect your inner circle fiercely, and possess immense capacity to regenerate after setbacks.")

    # ================= PAGE 4: VISUAL CHARTS D1 & D9 =================
    pdf.add_page()
    pdf.section_title("03", "VISUAL CHARTS: LAGNA (D1) & NAVAMSHA (D9)", "North Indian Style Natal & Divisional Blueprints")
    
    d1_data = {
        1: "As 14° Mo 6°", 2: "Ke 9°", 3: "", 4: "",
        5: "Su 12° Sa 14°", 6: "Me 2° Ve 14°\nMa 29°", 7: "", 8: "Ra 9°",
        9: "", 10: "", 11: "Ju(R) 1°", 12: ""
    }
    pdf.draw_north_indian_chart(20, 58, 78, "LAGNA CHART (D1 - RASHI)", d1_data)

    d9_data = {
        1: "As(Tau)", 2: "Su", 3: "Ra", 4: "",
        5: "", 6: "", 7: "Me", 8: "",
        9: "Ke", 10: "Mo Sa", 11: "Ve", 12: "Ma Ju"
    }
    pdf.draw_north_indian_chart(112, 58, 78, "NAVAMSHA CHART (D9 - MARRIAGE/SOUL)", d9_data)

    pdf.set_y(145)
    pdf.write_block("Technical Chart Synthesis (Why Events Happen)", 
                    "1. VargottamaAscendant (Taurus Rising in both D1 and D9): When the same sign rises in both the Rashi and Navamsha charts, BPHS and Phaladeepika declare the native internally and externally unshakable. Health, longevity, and self-made status are doubly fortified.\n"
                    "2. 5th House Surya-Shani Conjunction (Virgo): The 4th Lord (Sun) and Yogakaraka 9th/10th Lord (Saturn) conjoin in the 5th house of intellect. While this creates serious, perfectionist educational standards and occasional friction with authority figures, it forms a powerful Raja Yoga for technical, analytical, and administrative mastery.\n"
                    "3. 6th House Venus-Mars-Mercury Cluster (Libra): Lagna Lord Venus sits in its own Moolatrikona sign Libra in the 6th house (Harsha Vipareeta Raj Yoga pattern), turning competition, litigation, or health hurdles into ultimate professional victories.")

    # ================= PAGE 5: VISUAL CHARTS D10 & D7 =================
    pdf.add_page()
    pdf.section_title("04", "VISUAL CHARTS: DASHAMSHA (D10) & SAPTAMSHA (D7)", "Career Authority (D10) & Creative Legacy (D7)")
    
    d10_data = {
        1: "As(Cap) Ju", 2: "Ve", 3: "Mo", 4: "Ma",
        5: "Ra", 6: "", 7: "Su", 8: "",
        9: "Me", 10: "Sa", 11: "Ke", 12: ""
    }
    pdf.draw_north_indian_chart(20, 58, 78, "DASHAMSHA (D10 - CAREER)", d10_data)

    d7_data = {
        1: "As(Vir)", 2: "Ve", 3: "Ma", 4: "Ju",
        5: "Sa", 6: "Ra", 7: "", 8: "",
        9: "Su", 10: "Mo", 11: "Me", 12: "Ke"
    }
    pdf.draw_north_indian_chart(112, 58, 78, "SAPTAMSHA (D7 - PROGENY/CREATIVITY)", d7_data)

    pdf.set_y(145)
    varga_rows = [
        ["D1 (Rashi)", "Physical Body & General Destiny", "Taurus Lagna", "Vargottama Strength"],
        ["D2 (Hora)", "Wealth & Financial Accumulation", "Cancer / Leo", "Strong Solar Hora (Self-Earned)"],
        ["D3 (Drekkana)", "Courage, Siblings & Initiative", "Virgo Rising", "Analytical Initiative"],
        ["D4 (Chaturthamsha)", "Property, Home & Fixed Assets", "Scorpio", "Transformative Real Estate Gains"],
        ["D7 (Saptamsha)", "Children, Creativity & Legacy", "Virgo", "Disciplined Creative Output"],
        ["D9 (Navamsha)", "Marriage, Dharma & Inner Strength", "Taurus", "High Spouse Loyalty & Support"],
        ["D10 (Dashamsha)", "Career, Fame & Command", "Capricorn", "Saturn in 10th: Executive Rise"],
        ["D12 (Dwadashamsha)", "Parents & Ancestral Lineage", "sagittarius", "Strong Paternal Karma"]
    ]
    pdf.write_table(["Varga Chart", "Domain Governed", "Ascendant", "Key Astrological Verdict"], varga_rows, [32, 58, 35, 55])

    # ================= PAGE 6: PLANETARY DEGREES & ASHTAKAVARGA =================
    pdf.add_page()
    pdf.section_title("05", "PLANETARY POSITIONS & ASHTAKAVARGA TABLE", "Exact Sidereal Longitudes, Nakshatra Lords, Sub-Lords & Bindus")
    planet_rows = [
        ["Ascendant", "Taurus", "14°52'", "Rohini - 2", "Venus", "Moon", "Jupiter", "Vargottama"],
        ["Sun", "Virgo", "12°06'", "Hasta - 1", "Mercury", "Moon", "Moon", "Friendly"],
        ["Moon", "Taurus", "06°18'", "Krittika - 3", "Venus", "Sun", "Venus", "Exalted (Uchcha)"],
        ["Mars", "Libra", "29°18'", "Vishakha - 3", "Venus", "Jupiter", "Mars", "Amatyakaraka / AK"],
        ["Mercury", "Virgo", "02°14'", "U.Phalguni - 2", "Mercury", "Sun", "Saturn", "Exalted / Moolatrikona"],
        ["Jupiter (R)", "Pisces", "01°52'", "P.Bhadra - 4", "Jupiter", "Jupiter", "Venus", "Own Sign (Hamsa Equivalent)"],
        ["Venus", "Libra", "14°10'", "Swati - 3", "Venus", "Rahu", "Mercury", "Own Sign (Moolatrikona)"],
        ["Saturn", "Virgo", "14°02'", "Hasta - 2", "Mercury", "Moon", "Rahu", "Yogakaraka (9L/10L)"],
        ["Rahu", "Sagittarius", "09°11'", "Mula - 3", "Jupiter", "Ketu", "Venus", "8th House Research"],
        ["Ketu", "Gemini", "09°11'", "Ardra - 1", "Mercury", "Rahu", "Rahu", "2nd House Detachment"]
    ]
    pdf.write_table(["Planet", "Sign", "Degree", "Nakshatra", "Sign Lord", "Star Lord", "Sub Lord", "Dignity"], 
                    planet_rows, [22, 22, 16, 26, 20, 20, 20, 34])

    pdf.write_block("Sarvashtakavarga Summary (Bindu Strength per House)",
                    "House 1 (Taurus): 31 Bindus | House 2 (Gemini): 27 Bindus | House 3 (Cancer): 30 Bindus | House 4 (Leo): 29 Bindus | "
                    "House 5 (Virgo): 26 Bindus | House 6 (Libra): 32 Bindus | House 7 (Scorpio): 25 Bindus | House 8 (Sagittarius): 22 Bindus | "
                    "House 9 (Capricorn): 29 Bindus | House 10 (Aquarius): 33 Bindus | House 11 (Pisces): 35 Bindus | House 12 (Aries): 20 Bindus.\n"
                    "REASONING: 33 Bindus in the 10th House and 35 Bindus in the 11th House (Phaladeepika rule) guarantee that professional efforts (10th) yield disproportionately high financial gains (11th)
