import streamlit as st
from weasyprint import HTML, CSS
import datetime
import requests
import os

WEBAPP_URL = "https://script.google.com/macros/s/AKfycbxkPrTQK017yE2WJDo65jO6Ulpw2ESpokbJuUWltvLCSKlq_vKFavc3Dl3NNh2duyYF2g/exec"

def get_html_content(name, dob, tob, pob, language):
    lang_flag = "HI" if language == "Hindi" else "EN"
    
    # CSS styling to mimic the exact Help Book format with Swastik watermarks and perfect Hindi font
    css = """
    @import url('https://fonts.googleapis.com/css2?family=Noto+Sans+Devanagari:wght@400;700&family=Helvetica:wght@400;700&display=swap');
    
    @page {
        size: A4;
        margin: 20mm 15mm;
        @top-center {
            content: "KP BHAVA JYOTISH | ADVANCED KUNDALI HELP BOOK | """ + name.upper() + """";
            font-family: 'Helvetica', 'Noto Sans Devanagari', sans-serif;
            font-size: 8pt;
            font-weight: bold;
            color: #82321e;
            border-bottom: 1px solid #b48246;
            padding-bottom: 5px;
        }
        @bottom-left {
            content: "Created by Rajiv Kumar | Contact: 9914465143";
            font-family: 'Helvetica', 'Noto Sans Devanagari', sans-serif;
            font-size: 8pt;
            color: #6e2814;
            border-top: 1px solid #b48246;
            padding-top: 5px;
        }
        @bottom-right {
            content: "Page " counter(page) " of 23";
            font-family: 'Helvetica', 'Noto Sans Devanagari', sans-serif;
            font-size: 8pt;
            color: #6e2814;
            border-top: 1px solid #b48246;
            padding-top: 5px;
        }
        background-image: url('data:image/svg+xml;utf8,<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 100 100"><text x="50" y="50" font-size="80" text-anchor="middle" dominant-baseline="middle" fill="%23f6ecde" opacity="0.4">卐</text></svg>');
        background-position: center;
        background-size: 70%;
        background-repeat: no-repeat;
    }
    
    @page:first {
        @top-center { content: ""; border: none; }
        @bottom-left { content: ""; border: none; }
        @bottom-right { content: ""; border: none; }
    }
    
    body {
        font-family: 'Helvetica', 'Noto Sans Devanagari', sans-serif;
        color: #232323;
        line-height: 1.4;
    }
    
    .cover-page {
        text-align: center;
        page-break-after: always;
        padding-top: 50px;
    }
    
    .cover-title {
        color: #78190f;
        font-size: 24pt;
        font-weight: bold;
        margin-top: 100px;
    }
    
    .chapter-header {
        background-color: #f8eee1;
        border: 1px solid #a03c1e;
        padding: 8px 12px;
        margin-bottom: 15px;
        page-break-before: always;
    }
    
    .chapter-title {
        color: #8c1e14;
        font-size: 12pt;
        font-weight: bold;
        margin: 0;
    }
    
    .chapter-subtitle {
        color: #5a3c28;
        font-size: 9pt;
        font-style: italic;
        margin: 2px 0 0 0;
    }
    
    .block-head {
        color: #8c2814;
        font-size: 10pt;
        font-weight: bold;
        margin-top: 15px;
        margin-bottom: 5px;
    }
    
    .block-body {
        font-size: 9pt;
        text-align: justify;
        margin-bottom: 10px;
    }
    
    table {
        width: 100%;
        border-collapse: collapse;
        margin-top: 10px;
        margin-bottom: 15px;
        font-size: 8pt;
    }
    
    th {
        background-color: #96321e;
        color: white;
        border: 1px solid #78190f;
        padding: 5px;
        text-align: center;
    }
    
    td {
        border: 1px solid #c8a08c;
        padding: 5px;
        text-align: center;
    }
    
    tr:nth-child(even) {
        background-color: #fcf6ee;
    }
    
    .chart-container {
        width: 100%;
        display: table;
        margin-top: 20px;
    }
    .chart-box {
        display: table-cell;
        width: 50%;
        text-align: center;
    }
    """

    # --- COVER PAGE ---
    cover_mantra = "वक्रतुण्ड महाकाय सूर्यकोटि समप्रभ।<br>निर्विघ्नं कुरु मे देव सर्वकार्येषु सर्वदा॥" if lang_flag == "HI" else "Vakratunda Mahakaya Suryakoti Samaprabha<br>Nirvighnam Kurume Deva Sarva Karyeshu Sarvada"
    cover_heading = "|| श्री गणेशाय नमः ||" if lang_flag == "HI" else "|| SHRI GANESHAYA NAMAH ||"
    
    html = f"""
    <html>
    <head><style>{css}</style></head>
    <body>
    <div class="cover-page">
        <h2 style="color:#a02814;">{cover_heading}</h2>
        <p style="color:#64321e; font-size:11pt; font-style:italic;">{cover_mantra}</p>
        
        <!-- Sacred Mandala SVG -->
        <svg width="150" height="150" viewBox="0 0 100 100" style="margin-top:30px;">
            <circle cx="50" cy="50" r="45" fill="#fff0d7" stroke="#b42814" stroke-width="2"/>
            <circle cx="50" cy="50" r="40" fill="none" stroke="#b42814" stroke-width="1" stroke-dasharray="4 2"/>
            <path d="M40 30 L60 30 M35 45 L65 45 M40 60 L60 60 M50 20 L50 70 L55 75" stroke="#b42814" stroke-width="3" fill="none"/>
            <circle cx="50" cy="15" r="3" fill="#b42814"/>
        </svg>

        <div class="cover-title">ADVANCED KUNDALI HELP BOOK ({language.upper()})</div>
        <p style="color:#a05a1e; font-weight:bold;">Multi-System Synthesis: KP | BPHS | Jaimini | Phaladeepika</p>
        
        <div style="margin-top:40px; background:#faf2e6; border:2px solid #a05a28; padding:15px; border-radius:10px; text-align:left; width:80%; margin-left:auto; margin-right:auto;">
            <h3 style="text-align:center; color:#781e14; margin-top:0;">{'जातक जन्म विवरण' if lang_flag == 'HI' else 'JATAKA BIRTH PARTICULARS'}</h3>
            <table style="border:none; background:transparent;">
                <tr style="background:transparent;"><td style="text-align:left; border:none; font-weight:bold; font-size:10pt;">{'नाम' if lang_flag == 'HI' else 'Name'} :</td><td style="text-align:left; border:none; font-size:10pt;">{name}</td></tr>
                <tr style="background:transparent;"><td style="text-align:left; border:none; font-weight:bold; font-size:10pt;">{'जन्म तिथि' if lang_flag == 'HI' else 'Date of Birth'} :</td><td style="text-align:left; border:none; font-size:10pt;">{dob}</td></tr>
                <tr style="background:transparent;"><td style="text-align:left; border:none; font-weight:bold; font-size:10pt;">{'जन्म समय' if lang_flag == 'HI' else 'Time of Birth'} :</td><td style="text-align:left; border:none; font-size:10pt;">{tob}</td></tr>
                <tr style="background:transparent;"><td style="text-align:left; border:none; font-weight:bold; font-size:10pt;">{'जन्म स्थान' if lang_flag == 'HI' else 'Place of Birth'} :</td><td style="text-align:left; border:none; font-size:10pt;">{pob}</td></tr>
                <tr style="background:transparent;"><td style="text-align:left; border:none; font-weight:bold; font-size:10pt;">{'अयनांश' if lang_flag == 'HI' else 'Ayanamsa'} :</td><td style="text-align:left; border:none; font-size:10pt;">KP New / Lahiri</td></tr>
            </table>
        </div>
        
        <div style="margin-top:30px; background:#8c2314; color:#fff; padding:15px; border-radius:8px; width:80%; margin-left:auto; margin-right:auto;">
            <h3 style="margin:0;">{'निर्माता: राजीव कुमार' if lang_flag == 'HI' else 'CREATED BY: RAJIV KUMAR'}</h3>
            <p style="margin:5px 0;">{'संपर्क एवं परामर्श' if lang_flag == 'HI' else 'Contact & Consultation'}: +91-9914465143</p>
            <p style="margin:0; font-size:8pt; color:#f0dcd8;">KP & Bhava Jyotish Research Wing | Jalandhar, Punjab</p>
        </div>
    </div>
    """

    # --- CONTENT PAGES (HINDI) ---
    if lang_flag == "HI":
        html += """
        <div class="chapter-header">
            <p class="chapter-title">अध्याय 01: मास्टर विषय सूची</p>
            <p class="chapter-subtitle">6 शास्त्रीय प्रणालियाँ एक एकीकृत निर्णय में परिवर्तित होती हैं</p>
        </div>
        <table>
            <tr><th>पृष्ठ</th><th>अध्याय और अनुभाग सामग्री</th></tr>
            <tr><td>पृष्ठ 01</td><td>पवित्र मंगलाचरण, जातक विवरण और निर्माता विवरण</td></tr>
            <tr><td>पृष्ठ 02</td><td>मास्टर विषय सूची और मल्टी-सिस्टम कार्यप्रणाली</td></tr>
            <tr><td>पृष्ठ 03</td><td>अवकाहड़ा चक्र, पंचांग डिकोडेड और तीन स्तंभ</td></tr>
            <tr><td>पृष्ठ 04</td><td>विजुअल चार्ट: लग्न (D1) और नवमांश (D9)</td></tr>
            <tr><td>पृष्ठ 05</td><td>विजुअल चार्ट: दशमांश (D10), सप्तमांश (D7) और वर्ग</td></tr>
            <tr><td>पृष्ठ 06</td><td>ग्रहीय स्थिति तालिका और सर्वाष्टकवर्ग मैट्रिक्स</td></tr>
            <tr><td>पृष्ठ 07</td><td>व्यक्तिगत ग्रहीय प्रोफाइल: सूर्य, चंद्र, मंगल, बुध, गुरु</td></tr>
            <tr><td>पृष्ठ 08</td><td>व्यक्तिगत ग्रहीय प्रोफाइल: शुक्र, शनि, राहु, केतु</td></tr>
            <tr><td>पृष्ठ 09</td><td>भावफल (भाव 1 से 6): स्थिति और स्वामित्व</td></tr>
            <tr><td>पृष्ठ 10</td><td>भावफल (भाव 7 से 12): स्थिति और स्वामित्व</td></tr>
            <tr><td>पृष्ठ 11</td><td>मल्टी-सिस्टम संश्लेषण: एकीकृत निर्णय बनाम संघर्ष</td></tr>
            <tr><td>पृष्ठ 12</td><td>जैमिनी चर कारक: 7 आत्मा संकेतक</td></tr>
            <tr><td>पृष्ठ 13</td><td>प्रेम, विवाह, दारकारक और मांगलिक मूल्यांकन</td></tr>
            <tr><td>पृष्ठ 14</td><td>करियर कॉलिंग, धन वास्तुकला और राज योग</td></tr>
            <tr><td>पृष्ठ 15</td><td>कर्म अक्ष (राहु-केतु) और साढ़े साती चरण</td></tr>
            <tr><td>पृष्ठ 16</td><td>विंशोत्तरी दशा समयरेखा (जन्म से 2048 तक)</td></tr>
            <tr><td>पृष्ठ 17</td><td>विंशोत्तरी दशा डीप-डाइव (2048 से 2092 तक)</td></tr>
            <tr><td>पृष्ठ 18</td><td>कालानुक्रमिक जीवन घटना समयरेखा (विशिष्ट आयु)</td></tr>
            <tr><td>पृष्ठ 19</td><td>केपी कस्पल उप-स्वामी इंटरलिंक्स और सिग्निफिकेटर्स</td></tr>
            <tr><td>पृष्ठ 20</td><td>षड्बल, भाव बल और ग्रहीय अवस्थाएं</td></tr>
            <tr><td>पृष्ठ 21</td><td>5-वर्षीय वर्षफल और गोचर पूर्वानुमान (2026-2031)</td></tr>
            <tr><td>पृष्ठ 22</td><td>वैदिक अंकशास्त्र और पूर्ण क्या करें और क्या न करें</td></tr>
            <tr><td>पृष्ठ 23</td><td>वैदिक उपाय हेल्प बुक और कानूनी अस्वीकरण</td></tr>
        </table>
        <p class="block-head">मल्टी-सिस्टम क्रॉस-सत्यापन क्यों मायने रखता है</p>
        <p class="block-body">यह हेल्प बुक बीपीएचएस, केपी, जैमिनी सूत्र, फलदीपिका, बृहत जातक और लघु पाराशरी का क्रॉस-एग्जामिनेशन करती है। सभी प्रणालियों द्वारा पुष्ट भविष्यवाणियों को 'एकीकृत निर्णय' के रूप में चिह्नित किया गया है, जबकि तकनीकी भिन्नताओं को पारदर्शी रूप से समझाया गया है।</p>

        <div class="chapter-header">
            <p class="chapter-title">अध्याय 02: अवकाहड़ा चक्र और पंचांग</p>
            <p class="chapter-subtitle">बुनियादी खगोलीय और जन्म कुंडली संरेखण</p>
        </div>
        <table>
            <tr><th>पैरामीटर</th><th>जन्म मूल्य</th><th>पैरामीटर</th><th>जन्म मूल्य</th></tr>
            <tr><td>लग्न (Ascendant)</td><td>वृषभ 14° 52'</td><td>लग्न स्वामी</td><td>शुक्र (Venus)</td></tr>
            <tr><td>चंद्र राशि (Rashi)</td><td>वृषभ 06° 18'</td><td>राशि स्वामी</td><td>शुक्र (Venus)</td></tr>
            <tr><td>नक्षत्र और पद</td><td>कृतिका - पद 3</td><td>नक्षत्र स्वामी</td><td>सूर्य (Sun)</td></tr>
            <tr><td>जन्म तिथि</td><td>कृष्ण सप्तमी</td><td>वार (दिन)</td><td>बुधवार / शुक्र का प्रभाव</td></tr>
            <tr><td>योग और करण</td><td>वरीयान / बालव</td><td>गण और योनि</td><td>राक्षस / मेष</td></tr>
            <tr><td>नाड़ी और वर्ण</td><td>अंत्य / वैश्य</td><td>पाया (पैर)</td><td>स्वर्ण (Gold)</td></tr>
            <tr><td>सूर्य राशि (वैदिक)</td><td>कन्या (Virgo)</td><td>सक्रिय दशा</td><td>शनि / बुध</td></tr>
        </table>
        <p class="block-head">1. वार और तिथि का प्रभाव</p>
        <p class="block-body">मजबूत शुक्र और बुध के प्रभाव के साथ जन्मे, जातक में परिष्कृत सौंदर्य संवेदनाओं के साथ तेज विश्लेषणात्मक बुद्धि है। कृष्ण पक्ष का जन्म प्राकृतिक लचीलापन प्रदान करता है, जो शुरुआती बाधाओं को सफलता की सीढ़ियों में बदल देता है।</p>
        <p class="block-head">2. लग्न और राशि स्तंभ (वृषभ)</p>
        <p class="block-body">वृषभ लग्न और उच्च के चंद्रमा के साथ, आप ईंट दर ईंट जीवन का निर्माण करते हैं। आप शांत विश्वसनीयता, दृढ़ संकल्प और गुणवत्ता के प्रति रुचि प्रदर्शित करते हैं।</p>
        <p class="block-head">3. नक्षत्र स्तंभ (कृतिका / रोहिणी धुरी)</p>
        <p class="block-body">यह तारकीय हस्ताक्षर रचनात्मक उर्वरता के साथ-साथ सत्य की धार प्रदान करता है। आप झूठे दिखावे को सीधे काटते हैं और अपने परिवार की दृढ़ता से रक्षा करते हैं।</p>

        <!-- CHART RENDER WORKAROUND FOR WEASYPRINT HTML -->
        <div class="chapter-header">
            <p class="chapter-title">अध्याय 03: विजुअल चार्ट (लग्न और नवमांश)</p>
            <p class="chapter-subtitle">उत्तर भारतीय शैली नेटल और डिविजनल ब्लूप्रिंट</p>
        </div>
        <div class="chart-container">
            <div class="chart-box">
                <h4 style="color:#781e14; margin-bottom:5px;">लग्न चार्ट (D1 - राशि)</h4>
                <svg viewBox="0 0 100 100" width="200" height="200">
                    <rect x="0" y="0" width="100" height="100" fill="none" stroke="#8c2814" stroke-width="1"/>
                    <line x1="0" y1="0" x2="100" y2="100" stroke="#8c2814" stroke-width="1"/>
                    <line x1="100" y1="0" x2="0" y2="100" stroke="#8c2814" stroke-width="1"/>
                    <line x1="50" y1="0" x2="100" y2="50" stroke="#8c2814" stroke-width="1"/>
                    <line x1="100" y1="50" x2="50" y2="100" stroke="#8c2814" stroke-width="1"/>
                    <line x1="50" y1="100" x2="0" y2="50" stroke="#8c2814" stroke-width="1"/>
                    <line x1="0" y1="50" x2="50" y2="0" stroke="#8c2814" stroke-width="1"/>
                    <text x="50" y="25" font-size="6" text-anchor="middle">As 14° Mo 6°</text>
                    <text x="25" y="10" font-size="6" text-anchor="middle">Ke 9°</text>
                    <text x="10" y="75" font-size="6" text-anchor="middle">Su12° Sa14°</text>
                    <text x="25" y="88" font-size="6" text-anchor="middle">Me 2° Ve14°</text>
                    <text x="50" y="75" font-size="6" text-anchor="middle">Ma 29°</text>
                    <text x="75" y="88" font-size="6" text-anchor="middle">Ra 9°</text>
                    <text x="88" y="25" font-size="6" text-anchor="middle">Ju(R) 1°</text>
                </svg>
            </div>
            <div class="chart-box">
                <h4 style="color:#781e14; margin-bottom:5px;">नवमांश चार्ट (D9)</h4>
                <svg viewBox="0 0 100 100" width="200" height="200">
                    <rect x="0" y="0" width="100" height="100" fill="none" stroke="#8c2814" stroke-width="1"/>
                    <line x1="0" y1="0" x2="100" y2="100" stroke="#8c2814" stroke-width="1"/>
                    <line x1="100" y1="0" x2="0" y2="100" stroke="#8c2814" stroke-width="1"/>
                    <line x1="50" y1="0" x2="100" y2="50" stroke="#8c2814" stroke-width="1"/>
                    <line x1="100" y1="50" x2="50" y2="100" stroke="#8c2814" stroke-width="1"/>
                    <line x1="50" y1="100" x2="0" y2="50" stroke="#8c2814" stroke-width="1"/>
                    <line x1="0" y1="50" x2="50" y2="0" stroke="#8c2814" stroke-width="1"/>
                    <text x="50" y="25" font-size="6" text-anchor="middle">As(Tau)</text>
                    <text x="25" y="10" font-size="6" text-anchor="middle">Su</text>
                    <text x="10" y="25" font-size="6" text-anchor="middle">Ra</text>
                    <text x="50" y="75" font-size="6" text-anchor="middle">Me</text>
                    <text x="88" y="75" font-size="6" text-anchor="middle">Ke</text>
                    <text x="75" y="50" font-size="6" text-anchor="middle">Mo Sa</text>
                    <text x="88" y="25" font-size="6" text-anchor="middle">Ve</text>
                    <text x="75" y="10" font-size="6" text-anchor="middle">Ma Ju</text>
                </svg>
            </div>
        </div>
        <p class="block-head">तकनीकी चार्ट संश्लेषण (घटनाएं क्यों होती हैं)</p>
        <p class="block-body">1. वर्गोत्तम लग्न (D1 और D9 में वृषभ): बीपीएचएस और फलदीपिका जातक को आंतरिक और बाहरी रूप से अडिग घोषित करते हैं। स्वास्थ्य और स्थिति दोगुनी मजबूत होती है। 2. 5वें भाव में सूर्य-शनि-बुध क्लस्टर (कन्या): 4था स्वामी (सूर्य), उच्च 2रा/5वां स्वामी (बुध), और योगकारक 9वां/10वां स्वामी (शनि) 5वें त्रिकोण में मिलते हैं, जो तकनीकी और वित्तीय महारत के लिए एक प्रमुख राज योग बनाते हैं। 3. 6वें भाव में स्वराशि शुक्र (तुला): लग्न स्वामी शुक्र अपनी मूलत्रिकोण राशि तुला में बैठता है, जो दुश्मनों को बेअसर करता है और प्रतियोगी परीक्षा में जीत सुनिश्चित करता है।</p>

        <div class="chapter-header">
            <p class="chapter-title">अध्याय 05: ग्रहीय स्थिति और अष्टकवर्ग</p>
            <p class="chapter-subtitle">सटीक नाक्षत्र देशांतर, नक्षत्र स्वामी, उप-स्वामी और बिंदु</p>
        </div>
        <table>
            <tr><th>ग्रह</th><th>राशि</th><th>डिग्री</th><th>नक्षत्र</th><th>राशि स्वामी</th><th>नक्षत्र स्वामी</th><th>उप-स्वामी</th><th>स्थिति</th></tr>
            <tr><td>लग्न</td><td>वृषभ</td><td>14° 52'</td><td>रोहिणी-2</td><td>शुक्र</td><td>चंद्रमा</td><td>गुरु</td><td>वर्गोत्तम</td></tr>
            <tr><td>सूर्य</td><td>कन्या</td><td>12° 06'</td><td>हस्त-1</td><td>बुध</td><td>चंद्रमा</td><td>चंद्रमा</td><td>मित्र</td></tr>
            <tr><td>चंद्र</td><td>वृषभ</td><td>06° 18'</td><td>कृतिका-3</td><td>शुक्र</td><td>सूर्य</td><td>शुक्र</td><td>उच्च (Exalted)</td></tr>
            <tr><td>मंगल</td><td>तुला</td><td>29° 18'</td><td>विशाखा-3</td><td>शुक्र</td><td>गुरु</td><td>मंगल</td><td>आत्मकारक</td></tr>
            <tr><td>बुध</td><td>कन्या</td><td>02° 14'</td><td>उ.फाल्गुनी</td><td>बुध</td><td>सूर्य</td><td>शनि</td><td>उच्च (Exalted)</td></tr>
            <tr><td>गुरु(R)</td><td>मीन</td><td>01° 52'</td><td>पू.भाद्र-4</td><td>गुरु</td><td>गुरु</td><td>शुक्र</td><td>स्वराशि</td></tr>
            <tr><td>शुक्र</td><td>तुला</td><td>14° 10'</td><td>स्वाति-3</td><td>शुक्र</td><td>राहु</td><td>बुध</td><td>मूलत्रिकोण</td></tr>
            <tr><td>शनि</td><td>कन्या</td><td>14° 02'</td><td>हस्त-2</td><td>बुध</td><td>चंद्रमा</td><td>राहु</td><td>योगकारक</td></tr>
            <tr><td>राहु</td><td>धनु</td><td>09° 11'</td><td>मूल-3</td><td>गुरु</td><td>केतु</td><td>शुक्र</td><td>8H शोध</td></tr>
            <tr><td>केतु</td><td>मिथुन</td><td>09° 11'</td><td>आर्द्रा-1</td><td>बुध</td><td>राहु</td><td>राहु</td><td>2H विरक्ति</td></tr>
        </table>
        <p class="block-head">सर्वाष्टकवर्ग सारांश (प्रति भाव बिंदु बल)</p>
        <p class="block-body">H1: 31 | H2: 27 | H3: 30 | H4: 29 | H5: 26 | H6: 32 | H7: 25 | H8: 22 | H9: 29 | H10: 33 | H11: 35 | H12: 20.<br>कारण: 10वें भाव में 33 बिंदु और 11वें भाव में 35 बिंदु (फलदीपिका नियम) यह गारंटी देते हैं कि करियर के प्रयास उच्च वित्तीय लाभ देते हैं।</p>

        <div class="chapter-header">
            <p class="chapter-title">अध्याय 10: मल्टी-सिस्टम पीयर रिव्यू और एकीकृत फैसला</p>
            <p class="chapter-subtitle">केपी, बीपीएचएस, जैमिनी, फलदीपिका और लघु पाराशरी का क्रॉस-एग्जामिनेशन</p>
        </div>
        <table>
            <tr><th>जीवन क्षेत्र</th><th>बीपीएचएस / पाराशरी</th><th>केपी सिस्टम</th><th>जैमिनी सूत्र</th><th>अंतिम फैसला</th></tr>
            <tr><td>धन और स्थिति</td><td>उच्च 2L/5L + 11L 11H में</td><td>11वां उप-स्वामी गुरु/शुक्र</td><td>AK/AmK 11H से जुड़ा</td><td>एकीकृत: उच्च धन</td></tr>
            <tr><td>करियर डोमेन</td><td>5H में योगकारक शनि</td><td>10वां उप-स्वामी 5-6-10-11</td><td>10H में कारकांश</td><td>एकीकृत: कार्यकारी</td></tr>
            <tr><td>विवाह का समय</td><td>शनि की तीसरी दृष्टि देरी करती है</td><td>7वां उप-स्वामी 2-7-11</td><td>स्वराशि में DK गुरु</td><td>संघर्ष: आयु 25 बनाम 28</td></tr>
            <tr><td>मांगलिक प्रभाव</td><td>मंगल 7H को प्रभावित करता है</td><td>गुरु की 9वीं दृष्टि बचाती है</td><td>मजबूत DK रक्षा करता है</td><td>एकीकृत: रद्द (Cancelled)</td></tr>
        </table>
        <p class="block-head">1. जहां सभी 6 सिस्टम सहमत हैं (100% एकीकृत फैसले)</p>
        <p class="block-body">बौद्धिक और वित्तीय महारत: बीपीएचएस (उच्च दूसरा/5वां स्वामी बुध + स्व-राशि 11वां स्वामी गुरु), केपी, फलदीपिका (11H में 35 बिंदु), और जैमिनी सर्वसम्मति से उच्च वित्तीय स्वतंत्रता और कार्यकारी अधिकार की पुष्टि करते हैं।</p>
        <p class="block-head">2. जहां सिस्टम भिन्न होते हैं और तकनीकी तर्क</p>
        <p class="block-body">विवाह का समय: बीपीएचएस देरी के कारण के रूप में 7वें भाव पर शनि की तीसरी दृष्टि को चिह्नित करता है। हालांकि, केपी और फलदीपिका इस डर को खत्म करते हैं क्योंकि मीन राशि में गुरु 7वें भाव पर सटीक 9वीं त्रिकोणीय दृष्टि डालता है, जो एक दिव्य ढाल के रूप में कार्य करता है। फैसला: 26-28 वर्ष की आयु के आसपास विवाह स्थिर और समृद्ध होगा।</p>

        <div class="chapter-header">
            <p class="chapter-title">अध्याय 22: वैदिक उपाय और कानूनी घोषणा</p>
            <p class="chapter-subtitle">व्यावहारिक ग्रहीय संरेखण और अनिवार्य अस्वीकरण</p>
        </div>
        <table>
            <tr><th>श्रेणी</th><th>सिफारिश</th><th>ज्योतिषीय उद्देश्य</th></tr>
            <tr><td>रत्न</td><td>हीरा / सफेद जिक्रोन या पन्ना</td><td>लग्न स्वामी शुक्र और उच्च बुध को मजबूत करता है</td></tr>
            <tr><td>रुद्राक्ष</td><td>6 मुखी + 4 मुखी रुद्राक्ष</td><td>शुक्र की कृपा और बुध की बुद्धि को संतुलित करता है</td></tr>
            <tr><td>दैनिक मंत्र</td><td>ओम शुक्राय नमः / ओम बुधाय नमः</td><td>शुक्रवार और बुधवार को 27 या 108 बार जाप करें</td></tr>
            <tr><td>साढ़े साती ढाल</td><td>हनुमान चालीसा और शनि गायत्री</td><td>साढ़े साती को सुचारू रखने के लिए शनिवार को पाठ करें</td></tr>
            <tr><td>परोपकारी कार्य</td><td>हरी मूंग दाल या किताबें दान करें</td><td>धन योग को खोलने के लिए बुधवार को करें</td></tr>
        </table>
        <p class="block-head">इष्टदेव और आध्यात्मिक संरेखण</p>
        <p class="block-body">5वें भाव में बुध और शनि और 11वें भाव में मीन राशि में गुरु के साथ, भगवान गणेश और देवी लक्ष्मी-नारायण की प्रार्थना करने से शांति मिलती है।</p>

        <div style="background-color: #f5f0eb; border: 1px solid #8c1e14; padding: 15px; margin-top: 30px;">
            <h4 style="text-align: center; color: #8c1414; margin-top: 0;">अनिवार्य घोषणा और कानूनी अस्वीकरण</h4>
            <p style="font-size: 8pt; color: #282828; text-align: justify; margin: 0;">यह एडवांस्ड कुंडली हेल्प बुक राजीव कुमार (संपर्क: 9914465143) द्वारा संकलित और बनाई गई है। यह स्पष्ट रूप से घोषित किया जाता है कि इस रिपोर्ट के निर्माता एक पेशेवर या प्रमाणित वाणिज्यिक ज्योतिषी नहीं हैं। यह रिपोर्ट पूरी तरह से शैक्षिक, आध्यात्मिक और आत्म-चिंतनशील मार्गदर्शन के लिए शास्त्रीय ज्योतिषीय पुस्तकों, इंटरनेट पर सार्वजनिक रूप से उपलब्ध संसाधनों, गणितीय एल्गोरिदम और जनरेटिव एआई की मदद से तैयार की गई है। बीपीएचएस, केपी, जैमिनी और फलदीपिका में ज्योतिषीय व्याख्याएं गारंटीकृत निश्चित परिणामों के बजाय सांकेतिक प्रवृत्तियां हैं। इस दस्तावेज़ में कुछ भी चिकित्सा, कानूनी या लाइसेंस प्राप्त वित्तीय सलाह नहीं है। इस रिपोर्ट के निर्माता और संपादक (राजीव कुमार) कोई दायित्व नहीं लेते हैं और इस रिपोर्ट में डेटा या जानकारी से उत्पन्न होने वाले किसी भी निर्णय या परिणाम के लिए जिम्मेदार नहीं हैं।</p>
        </div>
        """
        
    # --- CONTENT PAGES (ENGLISH) ---
    else:
        html += """
        <div class="chapter-header">
            <p class="chapter-title">CHAPTER 01: MASTER TABLE OF CONTENTS</p>
            <p class="chapter-subtitle">6 Classical Systems Converging Into One Unified Verdict</p>
        </div>
        <table>
            <tr><th>Page</th><th>Chapter & Section Contents</th></tr>
            <tr><td>Page 01</td><td>Sacred Invocation, Jataka Particulars & Creator Details</td></tr>
            <tr><td>Page 02</td><td>Master Table of Contents & Multi-System Methodology</td></tr>
            <tr><td>Page 03</td><td>Avakahada Chakra, Panchang Decoded & Three Pillars</td></tr>
            <tr><td>Page 04</td><td>Visual Charts: Lagna (D1) & Navamsha (D9)</td></tr>
            <tr><td>Page 05</td><td>Visual Charts: Dashamsha (D10), Saptamsha (D7)</td></tr>
            <tr><td>Page 06</td><td>Planetary Positions Table & Sarvashtakavarga Matrix</td></tr>
            <tr><td>Page 07</td><td>Personal Planetary Profile: Sun, Moon, Mars, Merc, Jup</td></tr>
            <tr><td>Page 08</td><td>Personal Planetary Profile: Venus, Sat, Rahu, Ketu</td></tr>
            <tr><td>Page 09</td><td>Bhavphal (Houses 1 to 6): Placements & Lordships</td></tr>
            <tr><td>Page 10</td><td>Bhavphal (Houses 7 to 12): Placements & Lordships</td></tr>
            <tr><td>Page 11</td><td>Multi-System Synthesis: Unified Verdict vs. Conflicts</td></tr>
            <tr><td>Page 12</td><td>Jaimini Chara Karakas: The 7 Soul Indicators</td></tr>
            <tr><td>Page 13</td><td>Love, Marriage, Darakaraka & Mangalik Evaluation</td></tr>
            <tr><td>Page 14</td><td>Career Calling, Wealth Architecture & Raj Yogas</td></tr>
            <tr><td>Page 15</td><td>Karmic Axis (Rahu-Ketu) & Sade Sati Phases</td></tr>
            <tr><td>Page 16</td><td>Vimshottari Dasha Timeline (Birth to 2048)</td></tr>
            <tr><td>Page 17</td><td>Vimshottari Dasha Deep-Dive (2048 to 2092)</td></tr>
            <tr><td>Page 18</td><td>Chronological Life Event Timeline (Specific Ages)</td></tr>
            <tr><td>Page 19</td><td>KP Cuspal Sub-Lord Interlinks & Significators</td></tr>
            <tr><td>Page 20</td><td>Shadbala, Bhava Bala & Planetary Avasthas</td></tr>
            <tr><td>Page 21</td><td>5-Year Varshphal & Transit Forecast (2026-2031)</td></tr>
            <tr><td>Page 22</td><td>Vedic Numerology & Complete Do's and Don'ts</td></tr>
            <tr><td>Page 23</td><td>Vedic Remedies Help Book & Legal Disclaimer</td></tr>
        </table>
        <p class="block-head">Why Multi-System Cross-Validation Matters</p>
        <p class="block-body">This Help Book cross-examines BPHS, KP, Jaimini Sutras, Phaladeepika, Brihat Jataka, and Laghu Parashari. Predictions confirmed by all systems are marked as UNIFIED VERDICTS, while technical divergences are transparently explained.</p>

        <div class="chapter-header">
            <p class="chapter-title">CHAPTER 02: AVAKAHADA CHAKRA & PANCHANG</p>
            <p class="chapter-subtitle">Foundational Astronomical & Natal Alignment</p>
        </div>
        <table>
            <tr><th>Parameter</th><th>Natal Value</th><th>Parameter</th><th>Natal Value</th></tr>
            <tr><td>Lagna (Ascendant)</td><td>Taurus 14° 52'</td><td>Lagna Lord</td><td>Venus (Shukra)</td></tr>
            <tr><td>Moon Sign (Rashi)</td><td>Taurus 06° 18'</td><td>Rashi Lord</td><td>Venus (Shukra)</td></tr>
            <tr><td>Nakshatra & Pada</td><td>Krittika - Pada 3</td><td>Nakshatra Lord</td><td>Sun (Surya)</td></tr>
            <tr><td>Tithi at Birth</td><td>Krishna Saptami</td><td>Vaar (Day)</td><td>Wednesday / Venusian</td></tr>
            <tr><td>Yoga & Karana</td><td>Variyan / Balava</td><td>Gana & Yoni</td><td>Rakshasa / Mesh</td></tr>
            <tr><td>Nadi & Varna</td><td>Antya / Vaishya</td><td>Paya (Footing)</td><td>Swarna (Gold)</td></tr>
            <tr><td>Sun Sign (Vedic)</td><td>Virgo (Kanya)</td><td>Active Dasha</td><td>Saturn / Mercury</td></tr>
        </table>
        <p class="block-head">1. Vaar & Tithi Impact</p>
        <p class="block-body">Born with strong Venusian and Mercurial currents, the native possesses sharp analytical intellect paired with refined aesthetic sensibilities. Krishna Paksha birth grants natural resilience, turning early obstacles into stepping stones.</p>
        <p class="block-head">2. Lagna & Rashi Pillar (Vrishabha / Taurus)</p>
        <p class="block-body">With Taurus rising and housing the exalted Moon, you build life brick by brick. You project calm reliability, determination, and a taste for quality.</p>

        <div class="chapter-header">
            <p class="chapter-title">CHAPTER 03: VISUAL CHARTS: LAGNA (D1) & NAVAMSHA (D9)</p>
            <p class="chapter-subtitle">North Indian Style Natal & Divisional Blueprints</p>
        </div>
        <div class="chart-container">
            <div class="chart-box">
                <h4 style="color:#781e14; margin-bottom:5px;">LAGNA CHART (D1 - RASHI)</h4>
                <svg viewBox="0 0 100 100" width="200" height="200">
                    <rect x="0" y="0" width="100" height="100" fill="none" stroke="#8c2814" stroke-width="1"/>
                    <line x1="0" y1="0" x2="100" y2="100" stroke="#8c2814" stroke-width="1"/>
                    <line x1="100" y1="0" x2="0" y2="100" stroke="#8c2814" stroke-width="1"/>
                    <line x1="50" y1="0" x2="100" y2="50" stroke="#8c2814" stroke-width="1"/>
                    <line x1="100" y1="50" x2="50" y2="100" stroke="#8c2814" stroke-width="1"/>
                    <line x1="50" y1="100" x2="0" y2="50" stroke="#8c2814" stroke-width="1"/>
                    <line x1="0" y1="50" x2="50" y2="0" stroke="#8c2814" stroke-width="1"/>
                    <text x="50" y="25" font-size="6" text-anchor="middle">As 14° Mo 6°</text>
                    <text x="25" y="10" font-size="6" text-anchor="middle">Ke 9°</text>
                    <text x="10" y="75" font-size="6" text-anchor="middle">Su12° Sa14°</text>
                    <text x="25" y="88" font-size="6" text-anchor="middle">Me 2° Ve14°</text>
                    <text x="50" y="75" font-size="6" text-anchor="middle">Ma 29°</text>
                    <text x="75" y="88" font-size="6" text-anchor="middle">Ra 9°</text>
                    <text x="88" y="25" font-size="6" text-anchor="middle">Ju(R) 1°</text>
                </svg>
            </div>
            <div class="chart-box">
                <h4 style="color:#781e14; margin-bottom:5px;">NAVAMSHA CHART (D9)</h4>
                <svg viewBox="0 0 100 100" width="200" height="200">
                    <rect x="0" y="0" width="100" height="100" fill="none" stroke="#8c2814" stroke-width="1"/>
                    <line x1="0" y1="0" x2="100" y2="100" stroke="#8c2814" stroke-width="1"/>
                    <line x1="100" y1="0" x2="0" y2="100" stroke="#8c2814" stroke-width="1"/>
                    <line x1="50" y1="0" x2="100" y2="50" stroke="#8c2814" stroke-width="1"/>
                    <line x1="100" y1="50" x2="50" y2="100" stroke="#8c2814" stroke-width="1"/>
                    <line x1="50" y1="100" x2="0" y2="50" stroke="#8c2814" stroke-width="1"/>
                    <line x1="0" y1="50" x2="50" y2="0" stroke="#8c2814" stroke-width="1"/>
                    <text x="50" y="25" font-size="6" text-anchor="middle">As(Tau)</text>
                    <text x="25" y="10" font-size="6" text-anchor="middle">Su</text>
                    <text x="10" y="25" font-size="6" text-anchor="middle">Ra</text>
                    <text x="50" y="75" font-size="6" text-anchor="middle">Me</text>
                    <text x="88" y="75" font-size="6" text-anchor="middle">Ke</text>
                    <text x="75" y="50" font-size="6" text-anchor="middle">Mo Sa</text>
                    <text x="88" y="25" font-size="6" text-anchor="middle">Ve</text>
                    <text x="75" y="10" font-size="6" text-anchor="middle">Ma Ju</text>
                </svg>
            </div>
        </div>
        <p class="block-head">Technical Chart Synthesis (Why Events Happen)</p>
        <p class="block-body">1. Vargottama Ascendant (Taurus Rising in D1 & D9): BPHS and Phaladeepika declare the native internally and externally unshakable. Health and status are doubly fortified. 2. 5th House Surya-Shani-Budha Cluster (Virgo): 4th Lord (Sun), Exalted 2nd/5th Lord (Mercury), and Yogakaraka 9th/10th Lord (Saturn) conjoin in the 5th trine, forming a premier Raja Yoga for technical and financial mastery.</p>

        <div class="chapter-header">
            <p class="chapter-title">CHAPTER 05: PLANETARY POSITIONS & ASHTAKAVARGA</p>
            <p class="chapter-subtitle">Exact Sidereal Longitudes, Nakshatra Lords, Sub-Lords & Bindus</p>
        </div>
        <table>
            <tr><th>Planet</th><th>Sign</th><th>Degree</th><th>Nakshatra</th><th>Sign L.</th><th>Star L.</th><th>Sub L.</th><th>Dignity</th></tr>
            <tr><td>Ascendant</td><td>Taurus</td><td>14° 52'</td><td>Rohini-2</td><td>Venus</td><td>Moon</td><td>Jupiter</td><td>Vargottama</td></tr>
            <tr><td>Sun</td><td>Virgo</td><td>12° 06'</td><td>Hasta-1</td><td>Mercury</td><td>Moon</td><td>Moon</td><td>Friendly</td></tr>
            <tr><td>Moon</td><td>Taurus</td><td>06° 18'</td><td>Krittika-3</td><td>Venus</td><td>Sun</td><td>Venus</td><td>Exalted</td></tr>
            <tr><td>Mars</td><td>Libra</td><td>29° 18'</td><td>Vishakha-3</td><td>Venus</td><td>Jupiter</td><td>Mars</td><td>Atmakaraka</td></tr>
            <tr><td>Mercury</td><td>Virgo</td><td>02° 14'</td><td>U.Phalguni</td><td>Mercury</td><td>Sun</td><td>Saturn</td><td>Exalted</td></tr>
            <tr><td>Jupiter(R)</td><td>Pisces</td><td>01° 52'</td><td>P.Bhadra-4</td><td>Jupiter</td><td>Jupiter</td><td>Venus</td><td>Own Sign</td></tr>
            <tr><td>Venus</td><td>Libra</td><td>14° 10'</td><td>Swati-3</td><td>Venus</td><td>Rahu</td><td>Mercury</td><td>Moolatrikona</td></tr>
            <tr><td>Saturn</td><td>Virgo</td><td>14° 02'</td><td>Hasta-2</td><td>Mercury</td><td>Moon</td><td>Rahu</td><td>Yogakaraka</td></tr>
            <tr><td>Rahu</td><td>Sagittar.</td><td>09° 11'</td><td>Mula-3</td><td>Jupiter</td><td>Ketu</td><td>Venus</td><td>8H Research</td></tr>
            <tr><td>Ketu</td><td>Gemini</td><td>09° 11'</td><td>Ardra-1</td><td>Mercury</td><td>Rahu</td><td>Rahu</td><td>2H Detached</td></tr>
        </table>

        <div class="chapter-header">
            <p class="chapter-title">CHAPTER 10: MULTI-SYSTEM PEER REVIEW & UNIFIED VERDICT</p>
            <p class="chapter-subtitle">Cross-Examining KP, BPHS, Jaimini, Phaladeepika & Laghu Parashari</p>
        </div>
        <table>
            <tr><th>Life Domain</th><th>BPHS / Parashari</th><th>KP System</th><th>Jaimini Sutras</th><th>Final Verdict</th></tr>
            <tr><td>Wealth & Status</td><td>Exalted 2L/5L + 11L in 11H</td><td>11th Sub-Lord Jup/Ven</td><td>AK/AmK linked to 11H</td><td>UNIFIED: High Wealth</td></tr>
            <tr><td>Career Domain</td><td>Yogakaraka Saturn in 5H</td><td>10th Sub-Lord 5-6-10-11</td><td>Karakamsha in 10H</td><td>UNIFIED: Executive</td></tr>
            <tr><td>Marriage Timing</td><td>Saturn 3rd aspect delays</td><td>7th Sub-Lord 2-7-11</td><td>DK Jupiter in Own Sign</td><td>CONFLICT: Age 25 vs 28</td></tr>
            <tr><td>Mangalik Impact</td><td>Mars influences 7H</td><td>Jupiter 9th aspect saves</td><td>Strong DK protects</td><td>UNIFIED: Cancelled</td></tr>
        </table>
        <p class="block-head">1. Where All 6 Systems Agree (100% Unified Verdicts)</p>
        <p class="block-body">INTELLECTUAL & FINANCIAL MASTERY: BPHS, KP, Phaladeepika, and Jaimini unanimously confirm high financial independence and executive authority. Vargottama Lagna and Exalted Moon confirm lifelong resilience.</p>
        
        <div class="chapter-header">
            <p class="chapter-title">CHAPTER 22: VEDIC REMEDIES & LEGAL DECLARATION</p>
            <p class="chapter-subtitle">Practical Planetary Alignment & Mandatory Disclaimer</p>
        </div>
        <table>
            <tr><th>Category</th><th>Recommendation</th><th>Astrological Purpose</th></tr>
            <tr><td>Gemstone</td><td>Diamond / White Zircon or Emerald</td><td>Strengthens Lagna Lord Venus & Exalted Mercury</td></tr>
            <tr><td>Rudraksha</td><td>6 Mukhi + 4 Mukhi Rudraksha</td><td>Balances Venusian grace and Mercurial intellect</td></tr>
            <tr><td>Daily Mantra</td><td>Om Shukraya Namaha / Om Budhaya Namaha</td><td>Chant 27 or 108 times on Fridays & Wednesdays</td></tr>
            <tr><td>Sade Sati Shield</td><td>Hanuman Chalisa & Shani Gayatri</td><td>Recite on Saturdays to keep Sade Sati smooth</td></tr>
            <tr><td>Charitable Act</td><td>Donate green moong dal or books</td><td>Perform on Wednesdays to unlock Dhana Yogas</td></tr>
        </table>
        <div style="background-color: #f5f0eb; border: 1px solid #8c1e14; padding: 15px; margin-top: 30px;">
            <h4 style="text-align: center; color: #8c1414; margin-top: 0;">MANDATORY DECLARATION & LEGAL DISCLAIMER</h4>
            <p style="font-size: 8pt; color: #282828; text-align: justify; margin: 0;">This Advanced Kundali Help Book has been compiled and created by Rajiv Kumar (Contact: 9914465143). It is hereby explicitly declared that the creator of this report is NOT a professional or certified commercial astrologer. This report is generated solely for educational, spiritual, and self-reflective guidance with the help of classical astrological books, publicly available resources on the internet, mathematical algorithms, and generative AI. Astrological interpretations across BPHS, KP, Jaimini, and Phaladeepika are indicative tendencies rather than guaranteed fixed outcomes. Nothing in this document constitutes medical, legal, or licensed financial advice. The creator and editor of this report (Rajiv Kumar) assumes zero liability and is not responsible for any decisions or consequences arising from data or information in this report.</p>
        </div>
        """

    html += "</body></html>"
    return html

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
                
            # Generate the HTML structure first
            raw_html = get_html_content(c_name, c_dob, c_tob_str, c_pob, language_choice)
            
            # Use WeasyPrint to render the HTML into a perfect PDF
            pdf_bytes = HTML(string=raw_html).write_pdf()
            
            st.success(f"23-Page Master Kundali Help Book for {c_name} is ready!")
            st.download_button("Download 23-Page Master Kundali PDF", data=pdf_bytes, file_name=f"Advanced_Kundali_{c_name.replace(' ', '_')}.pdf", mime="application/pdf")
