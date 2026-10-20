import streamlit as st
import datetime
import json
import requests
import swisseph as swe
from geopy.geocoders import Nominatim, ArcGIS
from timezonefinder import TimezoneFinder
import pytz
from google import genai
from fpdf import FPDF
import io
base64
# --- PAGE CONFIGURATION (Mobile Friendly) ---
st.set_page_config(
    page_title="KP & Bhava Jyotish | Rajiv Kumar",
    page_icon="🪐",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- 🌟 YOUR BRAND & SHEET SETTINGS ---
MY_BRAND_NAME = "KP & Bhava Jyotish"
MY_FULL_NAME = "Rajiv Kumar"
MY_TITLE = "Vedic"
MY_CONTACT_PHONE = "+91 9914465143"  
MY_EMAIL = "rajiv.kuralia@gmail.com"     
MY_LOCATION = "Jalandhar, Punjab, India"

# ⚠️ PASTE YOUR GOOGLE APPS SCRIPT WEB APP URL HERE:
GOOGLE_SHEET_WEBAPP_URL = "" 

# --- ASTROLOGICAL CONSTANTS ---
ZODIAC_SIGNS = ["Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo", "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"]
SIGN_LORDS = ["Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury", "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"]
NAKSHATRAS = ["Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra", "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni", "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha", "Moola", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha", "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"]
VIMSHOTTARI_LORDS = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
VIMSHOTTARI_YEARS = [7, 20, 6, 10, 7, 18, 16, 19, 17] 
PLANET_SHORT = {"Sun": "Su", "Moon": "Mo", "Mars": "Ma", "Mercury": "Me", "Jupiter": "Ju", "Venus": "Ve", "Saturn": "Sa", "Rahu": "Ra", "Ketu": "Ke"}

# --- PDF GENERATOR HELPER ---
def create_pdf_report(client_name, reading_text, report_type="Individual Horoscope"):
    pdf = FPDF()
    pdf.add_page()
    pdf.set_auto_page_break(auto=True, margin=15)
    pdf.set_font("Arial", "B", 16)
    pdf.cell(0, 10, txt=f"{MY_BRAND_NAME} - {report_type}", ln=True, align='C')
    pdf.set_font("Arial", "I", 12)
    pdf.cell(0, 10, txt=f"Consultation by: {MY_FULL_NAME} ({MY_TITLE})", ln=True, align='C')
    pdf.cell(0, 10, txt=f"Contact: {MY_CONTACT_PHONE} | {MY_LOCATION}", ln=True, align='C')
    pdf.line(10, 40, 200, 40)
    pdf.ln(10)
    pdf.set_font("Arial", "B", 14)
    pdf.cell(0, 10, txt=f"Prepared For: {client_name}", ln=True, align='L')
    pdf.ln(5)
    pdf.set_font("Arial", "", 11)
    clean_text = reading_text.replace("**", "").replace("* ", "- ").encode('latin-1', 'replace').decode('latin-1')
    pdf.multi_cell(0, 7, txt=clean_text)
    return bytes(pdf.output())

# --- NORTH INDIAN KUNDALI SVG GENERATOR ---
def render_north_indian_chart_svg(title, lagna_sign_idx, house_planets_dict):
    house_coords = {1: (200, 175, 200, 105), 2: (100, 78, 100, 38), 3: (75, 100, 35, 100), 4: (170, 205, 100, 205), 5: (75, 300, 35, 300), 6: (100, 325, 100, 368), 7: (200, 232, 200, 305), 8: (300, 325, 300, 368), 9: (325, 300, 365, 300), 10: (230, 205, 300, 205), 11: (325, 100, 365, 100), 12: (300, 78, 300, 38)}
    svg_elements = []
    for h in range(1, 13):
        rashi_num = ((lagna_sign_idx + h - 1) % 12) + 1
        rx, ry, px, py = house_coords[h]
        svg_elements.append(f'<text x="{rx}" y="{ry}" fill="#c0392b" font-size="13" font-weight="bold" text-anchor="middle" dominant-baseline="middle">{rashi_num}</text>')
        p_list = house_planets_dict.get(h, [])
        if p_list:
            if len(p_list) <= 2:
                svg_elements.append(f'<text x="{px}" y="{py}" fill="#1a252f" font-size="14" font-weight="bold" text-anchor="middle" dominant-baseline="middle">{" ".join(p_list)}</text>')
            else:
                svg_elements.append(f'<text x="{px}" y="{py - 9}" fill="#1a252f" font-size="13" font-weight="bold" text-anchor="middle" dominant-baseline="middle">{" ".join(p_list[:2])}</text>')
                svg_elements.append(f'<text x="{px}" y="{py + 9}" fill="#1a252f" font-size="13" font-weight="bold" text-anchor="middle" dominant-baseline="middle">{" ".join(p_list[2:])}</text>')
    inner_svg = "\n".join(svg_elements)
    return f"""<div style="text-align:center; margin-bottom: 12px;"><div style="font-weight:700; font-size:16px; margin-bottom:6px; color:#b85d19;">{title}</div><svg viewBox="0 0 400 400" width="100%" style="max-width:340px; background:#fffdf7; border: 2.5px solid #b85d19; border-radius: 6px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);"><rect x="2" y="2" width="396" height="396" fill="none" stroke="#b85d19" stroke-width="2.5"/><line x1="0" y1="0" x2="400" y2="400" stroke="#b85d19" stroke-width="2"/><line x1="400" y1="0" x2="0" y2="400" stroke="#b85d19" stroke-width="2"/><line x1="200" y1="0" x2="0" y2="200" stroke="#b85d19" stroke-width="2"/><line x1="0" y1="200" x2="200" y2="400" stroke="#b85d19" stroke-width="2"/><line x1="200" y1="400" x2="400" y2="200" stroke="#b85d19" stroke-width="2"/><line x1="400" y1="200" x2="200" y2="0" stroke="#b85d19" stroke-width="2"/>{inner_svg}</svg></div>"""

# --- ASTRO MATHS ---
def format_dms(deg_float):
    d = int(deg_float); m_float = (deg_float - d) * 60; m = int(m_float); s = int(round((m_float - m) * 60))
    if s == 60: s = 0; m += 1
    if m == 60: m = 0; d += 1
    return f"{d}° {m}′ {s}″"

def get_kp_star_sub_lord(longitude_deg):
    lon = longitude_deg % 360.0; nak_span = 360.0 / 27.0; nak_index = int(lon // nak_span); deg_in_nak = lon % nak_span; pada = int(deg_in_nak // (nak_span / 4.0)) + 1
    star_lord_idx = nak_index % 9; star_lord = VIMSHOTTARI_LORDS[star_lord_idx]
    accumulated = 0.0; sub_lord = star_lord; sub_lord_idx = star_lord_idx; sub_sub_lord = star_lord
    for i in range(9):
        curr_idx = (star_lord_idx + i) % 9; sub_span = nak_span * (VIMSHOTTARI_YEARS[curr_idx] / 120.0)
        if deg_in_nak <= (accumulated + sub_span):
            sub_lord = VIMSHOTTARI_LORDS[curr_idx]; sub_lord_idx = curr_idx; deg_in_sub = deg_in_nak - accumulated
            sub_accum = 0.0
            for j in range(9):
                ss_idx = (sub_lord_idx + j) % 9; ss_span = sub_span * (VIMSHOTTARI_YEARS[ss_idx] / 120.0)
                if deg_in_sub <= (sub_accum + ss_span): sub_sub_lord = VIMSHOTTARI_LORDS[ss_idx]; break
                sub_accum += ss_span
            break
        accumulated += sub_span
    return {"nakshatra": NAKSHATRAS[nak_index], "pada": pada, "star_lord": star_lord, "sub_lord": sub_lord, "sub_sub_lord": sub_sub_lord}

def get_d9_sign_idx(lon_deg): return int((lon_deg % 360.0) // (30.0 / 9.0)) % 12
def get_kp_bhava_house(p_lon, cusps):
    p_lon %= 360.0
    for i in range(12):
        s, e = cusps[i], cusps[(i + 1) % 12]
        if (s < e and s <= p_lon < e) or (s >= e and (p_lon >= s or p_lon < e)): return i + 1
    return 1

def calculate_vimshottari_dasha(moon_lon_deg, birth_dt_naive):
    nak_span = 360.0 / 27.0; nak_index = int((moon_lon_deg % 360.0) // nak_span)
    fraction_remaining = 1.0 - (((moon_lon_deg % 360.0) % nak_span) / nak_span)
    start_lord_idx = nak_index % 9; first_dasha_years = VIMSHOTTARI_YEARS[start_lord_idx] * fraction_remaining
    now = datetime.datetime.now(); dasha_timeline = []; current_date = birth_dt_naive
    active_md = {"lord": "Unknown", "start": "", "end": ""}; active_ad = {"lord": "Unknown", "start": "", "end": ""}
    for i in range(9):
        idx = (start_lord_idx + i) % 9; lord = VIMSHOTTARI_LORDS[idx]; years = first_dasha_years if i == 0 else float(VIMSHOTTARI_YEARS[idx])
        end_date = current_date + datetime.timedelta(days=years * 365.2425)
        if current_date <= now <= end_date:
            active_md = {"lord": lord, "start": current_date.strftime("%Y-%m-%d"), "end": end_date.strftime("%Y-%m-%d")}
            ad_cursor = end_date - datetime.timedelta(days=VIMSHOTTARI_YEARS[idx] * 365.2425)
            for j in range(9):
                ad_idx = (idx + j) % 9; ad_lord = VIMSHOTTARI_LORDS[ad_idx]
                ad_end = ad_cursor + datetime.timedelta(days=((VIMSHOTTARI_YEARS[idx] * VIMSHOTTARI_YEARS[ad_idx]) / 120.0) * 365.2425)
                if ad_cursor <= now <= ad_end:
                    active_ad = {"lord": ad_lord, "start": ad_cursor.strftime("%Y-%m-%d"), "end": ad_end.strftime("%Y-%m-%d")}; break
                ad_cursor = ad_end
        dasha_timeline.append({"mahadasha": lord, "start": current_date.strftime("%Y-%m-%d"), "end": end_date.strftime("%Y-%m-%d")})
        current_date = end_date
    return {"current_mahadasha": active_md, "current_antardasha": active_ad, "mahadasha_sequence": dasha_timeline}

# --- TIMEOUT-PROOF CITY COORDINATES ENGINE ---
@st.cache_data(show_spinner=False)
def get_city_coordinates(place_query):
    clean_q = place_query.strip().lower()
    fast_cities = {"jalandhar": (31.3260, 75.5762, "Jalandhar"), "amritsar": (31.6340, 74.8723, "Amritsar"), "ludhiana": (30.9010, 75.8573, "Ludhiana"), "chandigarh": (30.7333, 76.7794, "Chandigarh"), "delhi": (28.6139, 77.2090, "Delhi")}
    for key, (lat, lon, addr) in fast_cities.items():
        if key in clean_q: return lat, lon, addr
    try:
        arcgis_geo = ArcGIS(timeout=10)
        loc = arcgis_geo.geocode(place_query, timeout=10)
        if loc: return loc.latitude, loc.longitude, loc.address
    except Exception: pass
    try:
        geolocator = Nominatim(user_agent="kp_bhava_jyotish_rajiv_2026", timeout=10)
        loc = geolocator.geocode(place_query, timeout=10)
        if loc: return loc.latitude, loc.longitude, loc.address
    except Exception: pass
    raise ValueError(f"Could not find coordinates for '{place_query}'. Please check city spelling.")

# --- CHART BUILDER ---
def build_complete_kundali(name, dob_date, tob_time, place_query, ayanamsa_choice="Lahiri"):
    lat, lon, resolved_address = get_city_coordinates(place_query)
    tf = TimezoneFinder(); tz_name = tf.timezone_at(lng=lon, lat=lat) or "Asia/Kolkata"; local_tz = pytz.timezone(tz_name)
    dt_naive = datetime.datetime.combine(dob_date, tob_time); dt_utc = local_tz.localize(dt_naive).astimezone(pytz.utc)
    jd_ut = swe.julday(dt_utc.year, dt_utc.month, dt_utc.day, dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0)
    swe.set_sid_mode(swe.SIDM_KRISHNAMURTI if ayanamsa_choice == "KP New / Krishnamurti" else swe.SIDM_LAHIRI)
    ayanamsa_val = swe.get_ayanamsa_ut(jd_ut)
    cusps_trop, ascmc = swe.houses(jd_ut, lat, lon, b'P')
    lagna_sid = (ascmc[0] - ayanamsa_val) % 360.0; lagna_sign_idx = int(lagna_sid // 30); d9_lagna_sign_idx = get_d9_sign_idx(lagna_sid)
    
    cusp_sid_list = []; kp_cusps = {}
    for i in range(12):
        c_sid = (cusps_trop[i] - ayanamsa_val) % 360.0; cusp_sid_list.append(c_sid); c_sign_idx = int(c_sid // 30); kp_meta = get_kp_star_sub_lord(c_sid)
        kp_cusps[f"Cusp_{i+1}"] = {"sign": ZODIAC_SIGNS[c_sign_idx], "degree": format_dms(c_sid % 30), "sign_lord": SIGN_LORDS[c_sign_idx], "nakshatra": kp_meta["nakshatra"], "star_lord": kp_meta["star_lord"], "sub_lord": kp_meta["sub_lord"]}

    planet_ids = {"Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS, "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER, "Venus": swe.VENUS, "Saturn": swe.SATURN, "Rahu": swe.MEAN_NODE}
    planets_data = {}; moon_sid_lon = 0.0

    for p_name, p_id in planet_ids.items():
        res, _ = swe.calc_ut(jd_ut, p_id, swe.FLG_SIDEREAL | swe.FLG_SWIEPH | swe.FLG_SPEED); p_lon = res[0] % 360.0; p_speed = res[3]
        if p_name == "Moon": moon_sid_lon = p_lon
        s_idx = int(p_lon // 30); d1_house = ((s_idx - lagna_sign_idx) % 12) + 1; d9_s_idx = get_d9_sign_idx(p_lon); kp_meta = get_kp_star_sub_lord(p_lon)
        planets_data[p_name] = {"d1_sign": ZODIAC_SIGNS[s_idx], "degree_dms": format_dms(p_lon % 30), "sign_lord": SIGN_LORDS[s_idx], "d1_rashi_house": d1_house, "kp_bhava_chalit_house": get_kp_bhava_house(p_lon, cusp_sid_list), "d9_house": ((d9_s_idx - d9_lagna_sign_idx) % 12) + 1, "vargottama": (s_idx == d9_s_idx), "nakshatra": f"{kp_meta['nakshatra']} (Pada {kp_meta['pada']})", "star_lord": kp_meta["star_lord"], "sub_lord": kp_meta["sub_lord"], "retrograde": True if p_name == "Rahu" else (p_speed < 0)}

    rahu_res, _ = swe.calc_ut(jd_ut, swe.MEAN_NODE, swe.FLG_SIDEREAL | swe.FLG_SWIEPH); ketu_lon = (rahu_res[0] + 180.0) % 360.0; k_s_idx = int(ketu_lon // 30); k_d9_idx = get_d9_sign_idx(ketu_lon); k_kp_meta = get_kp_star_sub_lord(ketu_lon)
    planets_data["Ketu"] = {"d1_sign": ZODIAC_SIGNS[k_s_idx], "degree_dms": format_dms(ketu_lon % 30), "sign_lord": SIGN_LORDS[k_s_idx], "d1_rashi_house": ((k_s_idx - lagna_sign_idx) % 12) + 1, "kp_bhava_chalit_house": get_kp_bhava_house(ketu_lon, cusp_sid_list), "d9_house": ((k_d9_idx - d9_lagna_sign_idx) % 12) + 1, "vargottama": (k_s_idx == k_d9_idx), "nakshatra": f"{k_kp_meta['nakshatra']} (Pada {k_kp_meta['pada']})", "star_lord": k_kp_meta["star_lord"], "sub_lord": k_kp_meta["sub_lord"], "retrograde": True}

    return {"birth_details": {"name": name, "date": dob_date.strftime("%Y-%m-%d"), "time": tob_time.strftime("%H:%M:%S"), "place": resolved_address}, "lagna": {"d1_sign": ZODIAC_SIGNS[lagna_sign_idx], "d1_sign_idx": lagna_sign_idx, "d9_sign_idx": d9_lagna_sign_idx}, "vimshottari_dasha": calculate_vimshottari_dasha(moon_sid_lon, dt_naive), "planets": planets_data, "kp_12_cusps": kp_cusps}

# --- AI ENGINES ---
def get_astrology_reading(api_key, chart_json, user_question, language):
    client = genai.Client(api_key=api_key)
    sys_inst = f"You are a KP Master Astrologer. Analyze this JSON birth chart for the user's question in {language}. Conclude by reminding them to contact {MY_FULL_NAME} at {MY_CONTACT_PHONE} for detailed advisory."
    for model_name in ["gemini-3.1-pro-preview", "gemini-3-flash-preview", "gemini-2.5-flash"]:
        try:
            return client.models.generate_content(model=model_name, contents=f"Chart: {json.dumps(chart_json)}\n\nQ: {user_question}", config={"system_instruction": sys_inst}).text
        except Exception: continue
    raise RuntimeError("Could not connect to Gemini models.")

def get_milan_reading(api_key, chart_boy, chart_girl, language):
    client = genai.Client(api_key=api_key)
    sys_inst = f"You are an expert Vedic Astrologer performing Kundali Milan. Evaluate Ashtakoot Guna Milan and KP 7th House for both charts. Conclude by recommending consultation with {MY_FULL_NAME} at {MY_CONTACT_PHONE}."
    prompt = f"Partner 1 Chart:\n{json.dumps(chart_boy)}\n\nPartner 2 Chart:\n{json.dumps(chart_girl)}"
    for model_name in ["gemini-3.1-pro-preview", "gemini-3-flash-preview", "gemini-2.5-flash"]:
        try:
            return client.models.generate_content(model=model_name, contents=prompt, config={"system_instruction": sys_inst}).text
        except Exception: continue
    raise RuntimeError("Could not connect to Gemini models.")

# --- STREAMLIT UI ---
st.title(f"🪐 {MY_BRAND_NAME}")
st.markdown(f"**Curated & Presented by:** {MY_FULL_NAME} *({MY_TITLE})*")
st.markdown("---")

if "GEMINI_API_KEY" in st.secrets: st.session_state["api_key"] = st.secrets["GEMINI_API_KEY"]

with st.expander("⚙️ Settings & Consultant Info"):
    if not st.session_state.get("api_key"): st.session_state["api_key"] = st.text_input("Enter Gemini API Key:", type="password")
    output_lang = st.selectbox("Reading Language:", ["English", "Hinglish (Hindi + English)", "Hindi", "Punjabi"])
    st.info(f"**Contact Info:** {MY_CONTACT_PHONE} | {MY_EMAIL}")

tab_indiv, tab_milan = st.tabs(["👤 Individual Horoscope", "💞 Kundali Milan (Match)"])

# --- TAB 1: INDIVIDUAL READING ---
with tab_indiv:
    with st.form("birth_details_form"):
        st.subheader("📋 Enter Client Details")
        
        st.markdown("**Contact Information (Required):**")
        contact_col1, contact_col2 = st.columns(2)
        with contact_col1:
            mobile = st.text_input("Mobile Number (WhatsApp) *", placeholder="+91 98765...")
        with contact_col2:
            email = st.text_input("Email ID *", placeholder="client@email.com")
            
        st.markdown("**Birth Details:**")
        c1, c2 = st.columns(2)
        with c1:
            name = st.text_input("Full Name *", value="")
            dob = st.date_input("Date of Birth *", value=None, min_value=datetime.date(1920, 1, 1), max_value=datetime.date.today())
        with c2:
            tob = st.time_input("Exact Time (24-hr) *", value=None, step=60)
            place = st.text_input("City & State *", value="", placeholder="e.g., Jalandhar")
        
        question = st.text_area("Ask the Astrologer:", value="", placeholder="e.g., Give a complete life reading.")
        submit_btn = st.form_submit_button("✨ Generate Kundali & Reading", use_container_width=True)

    if submit_btn:
        if not all([name, mobile, email, dob, tob, place]): 
            st.error("⚠️ Please fill in all required fields (including Mobile and Email).")
        elif not st.session_state.get("api_key"): 
            st.error("Missing API Key.")
        else:
            # ---> SEND LEAD DATA TO GOOGLE SHEETS
            if GOOGLE_SHEET_WEBAPP_URL:
                try:
                    lead_data = {"name": name, "mobile": mobile, "email": email, "dob": str(dob), "tob": str(tob), "place": place, "question": question}
                    requests.post(GOOGLE_SHEET_WEBAPP_URL, json=lead_data, timeout=5)
                except Exception:
                    pass # Continue generating chart even if sheet saves slowly
                    
            with st.spinner("Calculating Chart..."):
                chart_data = build_complete_kundali(name, dob, tob, place)
                st.session_state["chart_data"] = chart_data
            with st.spinner("Analyzing Yogas & KP Sub-Lords..."):
                st.session_state["last_reading"] = get_astrology_reading(st.session_state["api_key"], chart_data, question, output_lang)
                st.session_state["client_name"] = name

    if "chart_data" in st.session_state and "last_reading" in st.session_state:
        st.success("Chart & Reading Generated Successfully!")
        pdf_bytes = create_pdf_report(st.session_state["client_name"], st.session_state["last_reading"], "Individual Horoscope")
        =True
        st.markdown(st.session_state["last_reading"])
        
        d1_houses = {i: [] for i in range(1, 13)}
        for p_name, p_info in st.session_state["chart_data"]["planets"].items():
            d1_houses[p_info["d1_rashi_house"]].append(PLANET_SHORT[p_name] + ("(R)" if p_info["retrograde"] else ""))
        st.markdown(render_north_indian_chart_svg("Lagna Chart (D1)", st.session_state["chart_data"]["lagna"]["d1_sign_idx"], d1_houses), unsafe_allow_html=True)

b64_pdf = base64.b64encode(pdf_bytes).decode('utf-8')
pdf_filename = f"{st.session_state['client_name']}_Kundali_Report.pdf"
html_button = f'''
    <a href="data:application/pdf;base64,{b64_pdf}" download="{pdf_filename}" 
       style="display: block; width: 100%; text-align: center; padding: 12px; 
              background-color: #b85d19; color: white; text-decoration: none; 
              border-radius: 6px; font-weight: bold; margin-bottom: 15px;">
        📥 Download Reading as PDF
    </a>
'''
st.markdown(html_button, unsafe_allow_html=True)
# --- TAB 2: KUNDALI MILAN ---
with tab_milan:
    with st.form("milan_form"):
        st.subheader("💞 Matchmaking Details")
        st.markdown("**Person 1 Details:**")
        mc1, mc2, mc3, mc4 = st.columns(4)
        m_name1 = mc1.text_input("Name 1")
        m_dob1 = mc2.date_input("DOB 1", value=None, min_value=datetime.date(1920,1,1))
        m_tob1 = mc3.time_input("Time 1", value=None)
        m_place1 = mc4.text_input("City 1")
        
        st.markdown("**Person 2 Details:**")
        fc1, fc2, fc3, fc4 = st.columns(4)
        m_name2 = fc1.text_input("Name 2")
        m_dob2 = fc2.date_input("DOB 2", value=None, min_value=datetime.date(1920,1,1))
        m_tob2 = fc3.time_input("Time 2", value=None)
        m_place2 = fc4.text_input("City 2")
        
        milan_submit = st.form_submit_button("⚖️ Check 36-Point Compatibility", use_container_width=True)

    if milan_submit:
        if not all([m_name1, m_dob1, m_tob1, m_place1, m_name2, m_dob2, m_tob2, m_place2]): st.error("⚠️ Fill all fields.")
        elif not st.session_state.get("api_key"): st.error("Missing API Key.")
        else:
            with st.spinner(f"Calculating Charts..."):
                chart1 = build_complete_kundali(m_name1, m_dob1, m_tob1, m_place1)
                chart2 = build_complete_kundali(m_name2, m_dob2, m_tob2, m_place2)
            with st.spinner("AI performing Ashtakoot Guna Milan..."):
                st.session_state["milan_reading"] = get_milan_reading(st.session_state["api_key"], chart1, chart2, output_lang)
                st.session_state["milan_names"] = f"{m_name1} & {m_name2}"

    if "milan_reading" in st.session_state:
        milan_pdf = create_pdf_report(st.session_state["milan_names"], st.session_state["milan_reading"], "Kundali Milan Report")
        st.download_button(label="📥 Download Matchmaking PDF", data=milan_pdf, file_name=f"Compatibility.pdf", mime="application/pdf", use_container_width=True)
        st.markdown(st.session_state["milan_reading"])

st.markdown("---")
st.markdown(f"<div style='text-align: center; color: #666; font-size: 14px;'><b>{MY_BRAND_NAME}</b><br>Consultations by <b>{MY_FULL_NAME}</b> ({MY_TITLE})<br>📞 WhatsApp/Call: {MY_CONTACT_PHONE}</div>", unsafe_allow_html=True)
