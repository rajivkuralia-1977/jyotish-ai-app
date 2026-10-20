import streamlit as st
import datetime
import json
import swisseph as swe
from geopy.geocoders import Nominatim
from timezonefinder import TimezoneFinder
import pytz
from google import genai

# --- PAGE CONFIGURATION (Mobile Friendly) ---
st.set_page_config(
    page_title="Vedic & KP AI Astrologer",
    page_icon="🪐",
    layout="centered",
    initial_sidebar_state="collapsed"
)

# --- ASTROLOGICAL CONSTANTS ---
ZODIAC_SIGNS = [
    "Aries", "Taurus", "Gemini", "Cancer", "Leo", "Virgo",
    "Libra", "Scorpio", "Sagittarius", "Capricorn", "Aquarius", "Pisces"
]
SIGN_LORDS = [
    "Mars", "Venus", "Mercury", "Moon", "Sun", "Mercury",
    "Venus", "Mars", "Jupiter", "Saturn", "Saturn", "Jupiter"
]
NAKSHATRAS = [
    "Ashwini", "Bharani", "Krittika", "Rohini", "Mrigashira", "Ardra",
    "Punarvasu", "Pushya", "Ashlesha", "Magha", "Purva Phalguni", "Uttara Phalguni",
    "Hasta", "Chitra", "Swati", "Vishakha", "Anuradha", "Jyeshtha",
    "Moola", "Purva Ashadha", "Uttara Ashadha", "Shravana", "Dhanishta", "Shatabhisha",
    "Purva Bhadrapada", "Uttara Bhadrapada", "Revati"
]
VIMSHOTTARI_LORDS = ["Ketu", "Venus", "Sun", "Moon", "Mars", "Rahu", "Jupiter", "Saturn", "Mercury"]
VIMSHOTTARI_YEARS = [7, 20, 6, 10, 7, 18, 16, 19, 17]  # Total = 120 years
PLANET_SHORT = {
    "Sun": "Su", "Moon": "Mo", "Mars": "Ma", "Mercury": "Me",
    "Jupiter": "Ju", "Venus": "Ve", "Saturn": "Sa", "Rahu": "Ra", "Ketu": "Ke"
}

# --- NORTH INDIAN KUNDALI SVG GENERATOR ---
def render_north_indian_chart_svg(title, lagna_sign_idx, house_planets_dict):
    """
    Generates a clean, mobile-responsive North Indian Diamond Kundali SVG.
    lagna_sign_idx: 0 for Aries .. 11 for Pisces
    house_planets_dict: {1: ["Ma"], 2: ["Ve", "Sa"], ...}
    """
    # Coordinates for Rashi numbers (1-12) and Planet text in each of the 12 houses (400x400 viewBox)
    house_coords = {
        1:  {"rashi": (200, 175), "planets": (200, 105)},
        2:  {"rashi": (100, 78),  "planets": (100, 38)},
        3:  {"rashi": (75, 100),  "planets": (35, 100)},
        4:  {"rashi": (170, 205), "planets": (100, 205)},
        5:  {"rashi": (75, 300),  "planets": (35, 300)},
        6:  {"rashi": (100, 325), "planets": (100, 368)},
        7:  {"rashi": (200, 232), "planets": (200, 305)},
        8:  {"rashi": (300, 325), "planets": (300, 368)},
        9:  {"rashi": (325, 300), "planets": (365, 300)},
        10: {"rashi": (230, 205), "planets": (300, 205)},
        11: {"rashi": (325, 100), "planets": (365, 100)},
        12: {"rashi": (300, 78),  "planets": (300, 38)},
    }

    svg_elements = []
    for h in range(1, 13):
        rashi_num = ((lagna_sign_idx + h - 1) % 12) + 1
        rx, ry = house_coords[h]["rashi"]
        px, py = house_coords[h]["planets"]

        # Rashi Number (Reddish-Orange)
        svg_elements.append(
            f'<text x="{rx}" y="{ry}" fill="#c0392b" font-size="13" font-weight="bold" '
            f'text-anchor="middle" dominant-baseline="middle">{rashi_num}</text>'
        )

        # Planets in this house
        p_list = house_planets_dict.get(h, [])
        if p_list:
            # Split into 2 lines if more than 2 planets sit in the same house
            if len(p_list) <= 2:
                p_str = " ".join(p_list)
                svg_elements.append(
                    f'<text x="{px}" y="{py}" fill="#1a252f" font-size="14" font-weight="bold" '
                    f'text-anchor="middle" dominant-baseline="middle">{p_str}</text>'
                )
            else:
                line1 = " ".join(p_list[:2])
                line2 = " ".join(p_list[2:])
                svg_elements.append(
                    f'<text x="{px}" y="{py - 9}" fill="#1a252f" font-size="13" font-weight="bold" '
                    f'text-anchor="middle" dominant-baseline="middle">{line1}</text>'
                )
                svg_elements.append(
                    f'<text x="{px}" y="{py + 9}" fill="#1a252f" font-size="13" font-weight="bold" '
                    f'text-anchor="middle" dominant-baseline="middle">{line2}</text>'
                )

    inner_svg = "\n".join(svg_elements)
    svg_code = f"""
    <div style="text-align:center; margin-bottom: 12px;">
        <div style="font-weight:700; font-size:16px; margin-bottom:6px; color:#b85d19;">{title}</div>
        <svg viewBox="0 0 400 400" width="100%" style="max-width:340px; background:#fffdf7; border: 2.5px solid #b85d19; border-radius: 6px; box-shadow: 0 2px 6px rgba(0,0,0,0.08);">
            <!-- Outer Box -->
            <rect x="2" y="2" width="396" height="396" fill="none" stroke="#b85d19" stroke-width="2.5"/>
            <!-- Diagonal Cross Lines -->
            <line x1="0" y1="0" x2="400" y2="400" stroke="#b85d19" stroke-width="2"/>
            <line x1="400" y1="0" x2="0" y2="400" stroke="#b85d19" stroke-width="2"/>
            <!-- Inner Diamond Lines -->
            <line x1="200" y1="0" x2="0" y2="200" stroke="#b85d19" stroke-width="2"/>
            <line x1="0" y1="200" x2="200" y2="400" stroke="#b85d19" stroke-width="2"/>
            <line x1="200" y1="400" x2="400" y2="200" stroke="#b85d19" stroke-width="2"/>
            <line x1="400" y1="200" x2="200" y2="0" stroke="#b85d19" stroke-width="2"/>
            <!-- Rashi Numbers & Planets -->
            {inner_svg}
        </svg>
    </div>
    """
    return svg_code

# --- MATHEMATICAL & KP HELPER FUNCTIONS ---
def format_dms(deg_float):
    d = int(deg_float)
    m_float = (deg_float - d) * 60
    m = int(m_float)
    s = int(round((m_float - m) * 60))
    if s == 60:
        s = 0
        m += 1
    if m == 60:
        m = 0
        d += 1
    return f"{d}° {m}′ {s}″"

def get_kp_star_sub_lord(longitude_deg):
    lon = longitude_deg % 360.0
    nak_span = 360.0 / 27.0
    nak_index = int(lon // nak_span)
    deg_in_nak = lon % nak_span
    pada = int(deg_in_nak // (nak_span / 4.0)) + 1

    star_lord_idx = nak_index % 9
    star_lord = VIMSHOTTARI_LORDS[star_lord_idx]

    accumulated = 0.0
    sub_lord = star_lord
    sub_lord_idx = star_lord_idx
    sub_sub_lord = star_lord

    for i in range(9):
        curr_idx = (star_lord_idx + i) % 9
        sub_span = nak_span * (VIMSHOTTARI_YEARS[curr_idx] / 120.0)
        if deg_in_nak <= (accumulated + sub_span):
            sub_lord = VIMSHOTTARI_LORDS[curr_idx]
            sub_lord_idx = curr_idx
            deg_in_sub = deg_in_nak - accumulated

            sub_accum = 0.0
            for j in range(9):
                ss_idx = (sub_lord_idx + j) % 9
                ss_span = sub_span * (VIMSHOTTARI_YEARS[ss_idx] / 120.0)
                if deg_in_sub <= (sub_accum + ss_span):
                    sub_sub_lord = VIMSHOTTARI_LORDS[ss_idx]
                    break
                sub_accum += ss_span
            break
        accumulated += sub_span

    return {
        "nakshatra": NAKSHATRAS[nak_index],
        "pada": pada,
        "star_lord": star_lord,
        "sub_lord": sub_lord,
        "sub_sub_lord": sub_sub_lord
    }

def get_d9_sign_idx(lon_deg):
    navamsha_span = 30.0 / 9.0
    total_navamshas = int((lon_deg % 360.0) // navamsha_span)
    return total_navamshas % 12

def get_kp_bhava_house(planet_lon, cusp_longitudes):
    p_lon = planet_lon % 360.0
    for i in range(12):
        c_start = cusp_longitudes[i]
        c_end = cusp_longitudes[(i + 1) % 12]
        if c_start < c_end:
            if c_start <= p_lon < c_end:
                return i + 1
        else:
            if p_lon >= c_start or p_lon < c_end:
                return i + 1
    return 1

def calculate_vimshottari_dasha(moon_lon_deg, birth_dt_naive):
    nak_span = 360.0 / 27.0
    nak_index = int((moon_lon_deg % 360.0) // nak_span)
    deg_in_nak = (moon_lon_deg % 360.0) % nak_span
    fraction_remaining = 1.0 - (deg_in_nak / nak_span)

    start_lord_idx = nak_index % 9
    first_dasha_years = VIMSHOTTARI_YEARS[start_lord_idx] * fraction_remaining

    now = datetime.datetime.now()
    dasha_timeline = []
    current_date = birth_dt_naive
    active_md = None
    active_ad = None

    for i in range(9):
        idx = (start_lord_idx + i) % 9
        lord = VIMSHOTTARI_LORDS[idx]
        years = first_dasha_years if i == 0 else float(VIMSHOTTARI_YEARS[idx])
        days = years * 365.2425
        end_date = current_date + datetime.timedelta(days=days)

        if current_date <= now <= end_date:
            active_md = {
                "lord": lord,
                "start": current_date.strftime("%Y-%m-%d"),
                "end": end_date.strftime("%Y-%m-%d")
            }
            full_md_start = end_date - datetime.timedelta(days=VIMSHOTTARI_YEARS[idx] * 365.2425)
            ad_cursor = full_md_start
            for j in range(9):
                ad_idx = (idx + j) % 9
                ad_lord = VIMSHOTTARI_LORDS[ad_idx]
                ad_years = (VIMSHOTTARI_YEARS[idx] * VIMSHOTTARI_YEARS[ad_idx]) / 120.0
                ad_end = ad_cursor + datetime.timedelta(days=ad_years * 365.2425)
                if ad_cursor <= now <= ad_end:
                    active_ad = {
                        "lord": ad_lord,
                        "start": ad_cursor.strftime("%Y-%m-%d"),
                        "end": ad_end.strftime("%Y-%m-%d")
                    }
                    break
                ad_cursor = ad_end

        dasha_timeline.append({
            "mahadasha": lord,
            "start": current_date.strftime("%Y-%m-%d"),
            "end": end_date.strftime("%Y-%m-%d")
        })
        current_date = end_date

    return {
        "current_mahadasha": active_md,
        "current_antardasha": active_ad,
        "mahadasha_sequence": dasha_timeline
    }

# --- MAIN KUNDALI & KP GENERATOR ---
def build_complete_kundali(name, dob_date, tob_time, place_query, ayanamsa_choice="Lahiri"):
    geolocator = Nominatim(user_agent="vedic_kp_jyotish_app_2026")
    location = geolocator.geocode(place_query)
    if not location:
        raise ValueError(f"Could not find coordinates for '{place_query}'. Try adding state/country.")

    lat, lon = location.latitude, location.longitude
    tf = TimezoneFinder()
    tz_name = tf.timezone_at(lng=lon, lat=lat) or "Asia/Kolkata"
    local_tz = pytz.timezone(tz_name)

    dt_naive = datetime.datetime.combine(dob_date, tob_time)
    dt_local = local_tz.localize(dt_naive)
    dt_utc = dt_local.astimezone(pytz.utc)

    jd_ut = swe.julday(
        dt_utc.year, dt_utc.month, dt_utc.day,
        dt_utc.hour + dt_utc.minute / 60.0 + dt_utc.second / 3600.0
    )

    if ayanamsa_choice == "KP New / Krishnamurti":
        swe.set_sid_mode(swe.SIDM_KRISHNAMURTI)
    else:
        swe.set_sid_mode(swe.SIDM_LAHIRI)
    ayanamsa_val = swe.get_ayanamsa_ut(jd_ut)

    cusps_trop, ascmc = swe.houses(jd_ut, lat, lon, b'P')
    lagna_sid = (ascmc[0] - ayanamsa_val) % 360.0
    lagna_sign_idx = int(lagna_sid // 30)
    d9_lagna_sign_idx = get_d9_sign_idx(lagna_sid)

    cusp_sid_list = []
    kp_cusps = {}
    for i in range(12):
        c_sid = (cusps_trop[i] - ayanamsa_val) % 360.0
        cusp_sid_list.append(c_sid)
        c_sign_idx = int(c_sid // 30)
        kp_meta = get_kp_star_sub_lord(c_sid)
        kp_cusps[f"Cusp_{i+1}"] = {
            "sign": ZODIAC_SIGNS[c_sign_idx],
            "degree": format_dms(c_sid % 30),
            "sign_lord": SIGN_LORDS[c_sign_idx],
            "nakshatra": kp_meta["nakshatra"],
            "star_lord": kp_meta["star_lord"],
            "sub_lord": kp_meta["sub_lord"],
            "sub_sub_lord": kp_meta["sub_sub_lord"]
        }

    planet_ids = {
        "Sun": swe.SUN, "Moon": swe.MOON, "Mars": swe.MARS,
        "Mercury": swe.MERCURY, "Jupiter": swe.JUPITER,
        "Venus": swe.VENUS, "Saturn": swe.SATURN, "Rahu": swe.MEAN_NODE
    }

    planets_data = {}
    moon_sid_lon = 0.0

    for p_name, p_id in planet_ids.items():
        res, _ = swe.calc_ut(jd_ut, p_id, swe.FLG_SIDEREAL | swe.FLG_SWIEPH | swe.FLG_SPEED)
        p_lon = res[0] % 360.0
        p_speed = res[3]
        if p_name == "Moon":
            moon_sid_lon = p_lon

        s_idx = int(p_lon // 30)
        d1_house = ((s_idx - lagna_sign_idx) % 12) + 1
        kp_bhava = get_kp_bhava_house(p_lon, cusp_sid_list)
        d9_s_idx = get_d9_sign_idx(p_lon)
        d9_house = ((d9_s_idx - d9_lagna_sign_idx) % 12) + 1
        kp_meta = get_kp_star_sub_lord(p_lon)

        planets_data[p_name] = {
            "d1_sign": ZODIAC_SIGNS[s_idx],
            "degree_dms": format_dms(p_lon % 30),
            "sign_lord": SIGN_LORDS[s_idx],
            "d1_rashi_house": d1_house,
            "kp_bhava_chalit_house": kp_bhava,
            "d9_navamsha_sign": ZODIAC_SIGNS[d9_s_idx],
            "d9_house": d9_house,
            "vargottama": (s_idx == d9_s_idx),
            "nakshatra": f"{kp_meta['nakshatra']} (Pada {kp_meta['pada']})",
            "star_lord": kp_meta["star_lord"],
            "sub_lord": kp_meta["sub_lord"],
            "sub_sub_lord": kp_meta["sub_sub_lord"],
            "retrograde": True if p_name == "Rahu" else (p_speed < 0)
        }

    # Add Ketu
    rahu_res, _ = swe.calc_ut(jd_ut, swe.MEAN_NODE, swe.FLG_SIDEREAL | swe.FLG_SWIEPH)
    ketu_lon = (rahu_res[0] + 180.0) % 360.0
    k_s_idx = int(ketu_lon // 30)
    k_d9_idx = get_d9_sign_idx(ketu_lon)
    k_kp_meta = get_kp_star_sub_lord(ketu_lon)

    planets_data["Ketu"] = {
        "d1_sign": ZODIAC_SIGNS[k_s_idx],
        "degree_dms": format_dms(ketu_lon % 30),
        "sign_lord": SIGN_LORDS[k_s_idx],
        "d1_rashi_house": ((k_s_idx - lagna_sign_idx) % 12) + 1,
        "kp_bhava_chalit_house": get_kp_bhava_house(ketu_lon, cusp_sid_list),
        "d9_navamsha_sign": ZODIAC_SIGNS[k_d9_idx],
        "d9_house": ((k_d9_idx - d9_lagna_sign_idx) % 12) + 1,
        "vargottama": (k_s_idx == k_d9_idx),
        "nakshatra": f"{k_kp_meta['nakshatra']} (Pada {k_kp_meta['pada']})",
        "star_lord": k_kp_meta["star_lord"],
        "sub_lord": k_kp_meta["sub_lord"],
        "sub_sub_lord": k_kp_meta["sub_sub_lord"],
        "retrograde": True
    }

    dasha_info = calculate_vimshottari_dasha(moon_sid_lon, dt_naive)

    return {
        "birth_details": {
            "name": name,
            "date": dob_date.strftime("%Y-%m-%d"),
            "time": tob_time.strftime("%H:%M:%S"),
            "place": location.address,
            "latitude": round(lat, 5),
            "longitude": round(lon, 5),
            "timezone": tz_name,
            "ayanamsa_used": ayanamsa_choice,
            "ayanamsa_deg": format_dms(ayanamsa_val)
        },
        "lagna": {
            "d1_sign": ZODIAC_SIGNS[lagna_sign_idx],
            "d1_sign_idx": lagna_sign_idx,
            "degree_dms": format_dms(lagna_sid % 30),
            "d9_navamsha_lagna": ZODIAC_SIGNS[d9_lagna_sign_idx],
            "d9_sign_idx": d9_lagna_sign_idx,
            "star_lord": get_kp_star_sub_lord(lagna_sid)["star_lord"],
            "sub_lord": get_kp_star_sub_lord(lagna_sid)["sub_lord"]
        },
        "vimshottari_dasha": dasha_info,
        "planets": planets_data,
        "kp_12_cusps": kp_cusps
    }

# --- GEMINI AI MASTER ASTROLOGER ENGINE ---
def get_astrology_reading(api_key, chart_json, user_question, language):
    client = genai.Client(api_key=api_key)

    system_instruction = f"""
    You are a veteran Indian Jyotish Acharya and Krishnamurti Paddhati (KP) Master Astrologer.
    You are given an exact, NASA Swiss-Ephemeris calculated JSON birth chart containing:
    - D1 Lagna & Rashi placements
    - D9 Navamsha placements & Vargottama status
    - KP Placidus 12 Cuspal Sub-Lords (CSL) and KP Bhava Chalit shifts
    - Each planet's Nakshatra, Star Lord, Sub-Lord, and Sub-Sub-Lord
    - Current running Vimshottari Mahadasha and Antardasha

    Perform a deep, authentic astrological synthesis in {language}:
    1. **Parashari Synthesis:** Evaluate Lagna lord strength, key Raja/Dhana Yogas, planetary dignities (Exalted/Debilitated/Own sign in D1 & D9), and mutual aspects.
    2. **KP Precision Analysis:** Explicitly examine the relevant Cuspal Sub-Lords (CSL) for the user's question, check if planets shifted houses in `kp_bhava_chalit_house`, and evaluate the active Mahadasha & Antardasha lords via their Star Lords and Sub-Lords.
    3. **Direct, Concrete Predictions:** Give clear timelines, practical life patterns, and candid guidance without vague generalizations.
    4. **Practical Remedies:** Suggest 2-3 simple, traditional Vedic/lifestyle remedies tailored to the active Dasha.
    """

    prompt = (
        f"Here is the complete calculated Kundali & KP Chart JSON:\n"
        f"```json\n{json.dumps(chart_json, indent=2)}\n```\n\n"
        f"User's Question / Focus Area: {user_question}"
    )

    response = client.models.generate_content(
        model="gemini-2.5-pro",
        contents=prompt,
        config={"system_instruction": system_instruction}
    )
    return response.text

# --- STREAMLIT MOBILE UI ---
st.title("🪐 Vedic & KP AI Astrologer")
st.caption("North Indian Kundali (D1 & D9) + KP Sub-Lords + AI Jyotish Predictions")

if "GEMINI_API_KEY" in st.secrets:
    st.session_state["api_key"] = st.secrets["GEMINI_API_KEY"]
with st.expander("⚙️ Language & Ayanamsa Settings"):
    if not st.session_state.get("api_key"):
        api_key_input = st.text_input("Enter Gemini API Key:", type="password")
        if api_key_input:
            st.session_state["api_key"] = api_key_input
    ayanamsa_mode = st.selectbox("Ayanamsa System:", ["Lahiri", "KP New / Krishnamurti"])
    output_lang = st.selectbox("Reading Language:", ["English", "Hinglish (Hindi + English)", "Hindi (हिंदी)", "Punjabi (ਪੰਜਾਬੀ)"])

with st.form("birth_details_form"):
    st.subheader("📋 Enter Birth Details")
    col1, col2 = st.columns(2)
    with col1:
        name = st.text_input("Full Name", value="Anchal")
        dob = st.date_input(
            "Date of Birth",
            value=datetime.date(1983, 12, 13),
            min_value=datetime.date(1920, 1, 1),
            max_value=datetime.date.today()
        )
    with col2:
        tob = st.time_input("Exact Time of Birth (24-hr)", value=datetime.time(0, 45), step=60)
        place = st.text_input("City & State of Birth", value="Jalandhar, Punjab, India")

    question = st.text_area(
        "What would you like to ask the Astrologer?",
        value="Give a complete life reading covering personality, wealth, family, health, and predictions for the current Dasha period."
    )
    submit_btn = st.form_submit_button("✨ Generate Kundali & Get Prediction", use_container_width=True)

if submit_btn:
    if not st.session_state.get("api_key"):
        st.error("Please enter your Google Gemini API Key in the settings box above.")
    else:
        with st.spinner("Calculating Swiss Ephemeris Planetary Degrees, D9 Navamsha & KP Cusps..."):
            try:
                chart_data = build_complete_kundali(name, dob, tob, place, ayanamsa_mode)
                st.session_state["chart_data"] = chart_data
                md = chart_data['vimshottari_dasha']['current_mahadasha']['lord']
                ad = chart_data['vimshottari_dasha']['current_antardasha']['lord']
                st.success(f"Chart generated for **{name}** ({chart_data['lagna']['d1_sign']} Ascendant | Active Dasha: **{md} - {ad}**)")
            except Exception as e:
                st.error(f"Error calculating chart: {e}")
                st.stop()

        with st.spinner("Analyzing Parashari Yogas & KP Sub-Lords..."):
            try:
                reading = get_astrology_reading(st.session_state["api_key"], st.session_state["chart_data"], question, output_lang)
                st.session_state["last_reading"] = reading
            except Exception as e:
                st.error(f"Gemini API Error: {e}")

# --- DISPLAY VISUAL KUNDALI CHARTS & PREDICTIONS ---
if "chart_data" in st.session_state:
    cd = st.session_state["chart_data"]

    # Build house-wise planet dictionaries for D1, KP Bhava, and D9
    d1_houses = {i: [] for i in range(1, 13)}
    kp_houses = {i: [] for i in range(1, 13)}
    d9_houses 
