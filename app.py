import streamlit as st
import pandas as pd

# --- LOGIKA IZRAČUNA DOHODNINE (URADNA ZAKONODAJA 2026) ---

def pridobi_razred_2026(osnova):
    """Vrne ime razreda in stopnjo glede na uradno lestvico 2026."""
    if osnova <= 9721.43:
        return "1. razred (16%)", 0.16
    elif osnova <= 28592.44:
        return "2. razred (26%)", 0.26
    elif osnova <= 57184.88:
        return "3. razred (33%)", 0.33
    elif osnova <= 82346.23:
        return "4. razred (39%)", 0.39
    else:
        return "5. razred (50%)", 0.50

def izracun_dohodnine_2026(bruto_vsi, bruto_pok_letna, starost):
    # 1. LINEARNA SPLOŠNA OLAJŠAVA 2026
    # Meja za dodatno splošno olajšavo je 17.766,18 €
    osnovna_splosna = 5551.93
    if bruto_vsi <= 17766.18:
        dodatni_del = max(0, 20832.39 - 1.17259 * bruto_vsi)
        splosna_olajsava_koncna = osnovna_splosna + dodatni_del
    else:
        splosna_olajsava_koncna = osnovna_splosna

    # 2. SENIORSKA OLAJŠAVA 2026 (nad 70 let)
    seniorska_letna = 1665.58 if starost >= 70 else 0.0
    
    # 3. PRISPEVKI (OZP 37,17€/mesec + 1% Dolgotrajna oskrba)
    ozp_letni = 37.17 * 12 
    pdo_stopnja = 0.01
    prispevki_pok_letni = ozp_letni + (bruto_pok_letna * pdo_stopnja)
    
    # 4. DAVČNA OSNOVA
    osnova = max(0, bruto_vsi - prispevki_pok_letni - splosna_olajsava_koncna - seniorska_letna)
    
    # 5. DOHODNINSKA LESTVICA 2026
    if osnova <= 9721.43:
        davek = osnova * 0.16
    elif osnova <= 28592.44:
        davek = 1555.43 + (osnova - 9721.43) * 0.26
    elif osnova <= 57184.88:
        davek = 1555.43 + 4906.46 + (osnova - 28592.44) * 0.33
    elif osnova <= 82346.23:
        davek = 1555.43 + 4906.46 + 9435.51 + (osnova - 57184.88) * 0.39
    else:
        davek = 1555.43 + 4906.46 + 9435.51 + 9812.93 + (osnova - 82346.23) * 0.50
        
    # 6. POKOJNINSKA OLAJŠAVA (13,5% od bruto pokojnine)
    # To je ključna olajšava za upokojence v Sloveniji
    olajsava_zpiz = bruto_pok_letna * 0.135
    
    koncni_davek = max(0, davek - olajsava_zpiz)
    return koncni_davek, osnova

# --- NASTAVITVE STRANI ---
st.set_page_config(page_title="PDPZ Odkup 2026 - Natančen izračun", layout="centered")
st.title("🛡️ Svetovalec za odkup PDPZ (2026)")
st.markdown("Natančen izračun davčnega bremena po uradni zakonodaji 2026.")

# --- STRANSKI MENI (VHODNI PODATKI) ---
with st.sidebar:
    st.header("👤 Podatki o prihodkih")
    prihodki_delo = st.number_input("Letni bruto prihodki (plača, regres, sejnine)", value=5000.0, step=500.0)
    letna_pok_bruto = st.number_input("Letna bruto pokojnina (vsi meseci skupaj)", value=18000.0, step=500.0)
    starost = st.slider("Starost stranke ob koncu leta", 50, 95, 67)
    
    st.divider()
    st.header("💰 PDPZ Kapital")
    pdpz_kapital = st.number_input("Skupna sredstva na PDPZ računu (€)", value=30000.0, step=1000.0)
    stroski_odkupa_odstotek = st.slider("Izstopni stroški upravljavca (%)", 0.0, 5.0, 1.0) / 100

# --- IZRAČUNI ---

# 1. Osnovno stanje (brez odkupa)
davek_osnovni, osnova_brez = izracun_dohodnine_2026(prihodki_delo + letna_pok_bruto, letna_pok_bruto, starost)
razred_brez, _ = pridobi_razred_2026(osnova_brez)

# 2. Stanje z odkupom
izstopni_stroski = pdpz_kapital * stroski_odkupa_odstotek
bruto_za_davek = pdpz_kapital - izstopni_stroski

# Pri enkratnem odkupu se v osnovo šteje 100% zneska
davek_z_odkupom, osnova_z = izracun_dohodnine_2026(prihodki_delo + letna_pok_bruto + bruto_za_davek, letna_pok_bruto, starost)
razred_z, _ = pridobi_razred_2026(osnova_z)

# Razlika v davku, ki odpade direktno na PDPZ
dejanski_davek_pdpz = davek_z_odkupom - davek_osnovni
neto_izplacilo = bruto_za_davek - dejanski_davek_pdpz
efektivna_stopnja = (dejanski_davek_pdpz + izstopni_stroski) / pdpz_kapital

# --- PRIKAZ REZULTATOV ---
col1, col2 = st.columns(2)

with col1:
    st.metric("Neto prejemek na TRR", f"{neto_izplacilo:,.2f} €")
    st.write(f"**Prvotni razred:** {razred_brez}")

with col2:
    st.metric("Skupna davčna izguba", f"{(dejanski_davek_pdpz + izstopni_stroski):,.2f} €")
    st.write(f"**Novi davčni razred:** :orange[{razred_z}]")

st.divider()

# --- ANALIZA RAZREDOV ---
st.subheader("📊 Primerjava davčne osnove")

podatki_razred = {
    "Scenarij": ["Brez odkupa PDPZ", "Z enkratnim odkupom"],
    "Letna davčna osnova (€)": [f"{osnova_brez:,.2f}", f"{osnova_z:,.2f}"],
    "Dohodninski razred": [razred_brez, razred_z],
    "Letna dohodnina (€)": [f"{davek_osnovni:,.2f}", f"{davek_z_odkupom:,.2f}"]
}
st.table(pd.DataFrame(podatki_razred))

# --- PODROBNOSTI ---
with st.expander("🔎 Podrobna razčlenitev in akontacije"):
    st.write(f"**Bruto znesek odkupa:** {pdpz_kapital:,.2f} €")
    st.write(f"**Izstopni stroški:** -{izstopni_stroski:,.2f} €")
    st.write(f"**Akontacija (25%):** -{bruto_za_davek * 0.25:,.2f} € (odvede zavarovalnica)")
    st.write(f"**Dodaten poračun dohodnine:** -{max(0, dejanski_davek_pdpz - (bruto_za_davek * 0.25)):,.2f} € (ob odločbi FURS)")
    st.info(f"Skupaj boste za vsak evro na PDPZ računu prejeli **{1 - efektivna_stopnja:.4f} €** neto.")

# --- ZAKONSKA LESTVICA 2026 ---
st.divider()
st.subheader("📑 Dohodninska lestvica in olajšave (2026)")
st.write("Uradni podatki za leto 2026, ki so uporabljeni v izračunu:")

lestvica_data = {
    "Razred": ["1. razred", "2. razred", "3. razred", "4. razred", "5. razred"],
    "Neto letna osnova": ["do 9.721,43 €", "do 28.592,44 €", "do 57.184,88 €", "do 82.346,23 €", "nad 82.346,23 €"],
    "Stopnja": ["16%", "26%", "33%", "39%", "50%"]
}
st.table(pd.DataFrame(lestvica_data))

with st.container():
    st.write("**Upoštevane olajšave:**")
    st.markdown(f"""
    * **Splošna olajšava:** 5.551,93 € (z linearnim povečanjem do 17.766,18 € bruto)
    * **Seniorska olajšava:** 1.665,58 € (za osebe nad 70 let)
    * **Pokojninska olajšava:** 13,5% od bruto pokojnine (zmanjšanje dohodnine)
    """)

# --- OPOZORILO ---
st.error("⚠️ **Opozorilo:** Enkratno izplačilo PDPZ se v celoti prišteje k vašim letnim prihodkom, kar lahko povzroči izgubo socialnih pravic (varstveni dodatek, subvencije) in visok poračun dohodnine.")

st.caption("Izračun je informativne narave. Upoštevajte, da FURS upošteva vse vaše obdavčljive prihodke v letu.")
