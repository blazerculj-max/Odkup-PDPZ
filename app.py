import streamlit as st
import pandas as pd

# --- LOGIKA IZRAČUNA DOHODNINE (URADNA ZAKONODAJA 2025/2026) ---

def pridobi_razred_2026(osnova):
    """Vrne ime razreda in stopnjo glede na uradno lestvico."""
    if osnova <= 9522.47:
        return "1. razred (16%)", 0.16
    elif osnova <= 28007.27:
        return "2. razred (26%)", 0.26
    elif osnova <= 56014.54:
        return "3. razred (33%)", 0.33
    elif osnova <= 80660.94:
        return "4. razred (39%)", 0.39
    else:
        return "5. razred (50%)", 0.50

def izracun_dohodnine_2026(bruto_vsi, bruto_pok_letna, starost):
    # 1. LINEARNA SPLOŠNA OLAJŠAVA
    # Po zadnjih podatkih ZPIZ/FURS je osnovna splošna olajšava 5.000 € oz. 5.500 € (odvisno od uveljavitve reforme)
    # Tukaj upoštevamo 5.500 € kot predvideno za 2025/26
    osnovna_splosna = 5500.00
    meja_dodatna = 16000.00
    
    if bruto_vsi <= meja_dodatna:
        # Formula za dodatno splošno olajšavo (informativni izračun)
        splosna_olajsava_koncna = osnovna_splosna + (18761.40 - 1.17259 * bruto_vsi)
    else:
        splosna_olajsava_koncna = osnovna_splosna

    # 2. SENIORSKA OLAJŠAVA (nad 70 let)
    # ZPIZ navaja olajšavo v višini 1.500 € za zavezance po dopolnjenem 70. letu starosti
    seniorska_letna = 1500.00 if starost >= 70 else 0.0
    
    # 3. PRISPEVKI
    # OZP (Obvezni zdravstveni prispevek) = 35 € na mesec
    # Prispevek za dolgotrajno oskrbo (od 1.7.2025) = 1% od bruto pokojnine
    ozp_letni = 35.00 * 12 
    prispevek_do = bruto_pok_letna * 0.01
    skupni_prispevki = ozp_letni + prispevek_do
    
    # 4. DAVČNA OSNOVA
    osnova = max(0, bruto_vsi - skupni_prispevki - splosna_olajsava_koncna - seniorska_letna)
    
    # 5. DOHODNINSKA LESTVICA (Uradni pragovi 2025)
    if osnova <= 9522.47:
        davek = osnova * 0.16
    elif osnova <= 28007.27:
        davek = 1523.60 + (osnova - 9522.47) * 0.26
    elif osnova <= 56014.54:
        davek = 1523.60 + 4806.05 + (osnova - 28007.27) * 0.33
    elif osnova <= 80660.94:
        davek = 1523.60 + 4806.05 + 9242.40 + (osnova - 56014.54) * 0.39
    else:
        davek = 1523.60 + 4806.05 + 9242.40 + 9612.10 + (osnova - 80660.94) * 0.50
        
    # 6. POKOJNINSKA OLAJŠAVA (13,5% od odmerjene dohodnine od pokojnine)
    # ZPIZ: "Dohodnina se ne plača od dela pokojnine, ki ustreza 13,5% odmerne osnove"
    # V praksi to deluje kot zmanjšanje odmerjene dohodnine
    olajsava_zpiz = bruto_pok_letna * 0.135
    
    koncni_davek = max(0, davek - olajsava_zpiz)
    return koncni_davek, osnova

# --- NASTAVITVE STRANI ---
st.set_page_config(page_title="PDPZ Odkup 2026 - ZPIZ usklajeno", layout="centered")
st.title("🛡️ Svetovalec za odkup PDPZ (2026)")
st.markdown("Natančen izračun davčnega bremena po podatkih ZPIZ in veljavni zakonodaji.")

# --- STRANSKI MENI ---
with st.sidebar:
    st.header("👤 Podatki o prihodkih")
    prihodki_delo = st.number_input("Letni bruto prihodki (plača, regres, sejnine)", value=0.0, step=500.0)
    letna_pok_bruto = st.number_input("Letna bruto pokojnina", value=15000.0, step=500.0)
    starost = st.slider("Starost stranke ob koncu leta", 50, 95, 67)
    
    st.divider()
    st.header("💰 PDPZ Kapital")
    pdpz_kapital = st.number_input("Skupna sredstva na PDPZ računu (€)", value=20000.0, step=1000.0)
    stroski_odkupa_odstotek = st.slider("Izstopni stroški upravljavca (%)", 0.0, 5.0, 1.0) / 100

# --- IZRAČUNI ---
davek_osnovni, osnova_brez = izracun_dohodnine_2026(prihodki_delo + letna_pok_bruto, letna_pok_bruto, starost)
razred_brez, _ = pridobi_razred_2026(osnova_brez)

izstopni_stroski = pdpz_kapital * stroski_odkupa_odstotek
bruto_za_davek = pdpz_kapital - izstopni_stroski

# Enkratni odkup (v davčno osnovo gre 100% zneska)
davek_z_odkupom, osnova_z = izracun_dohodnine_2026(prihodki_delo + letna_pok_bruto + bruto_za_davek, letna_pok_bruto, starost)
razred_z, _ = pridobi_razred_2026(osnova_z)

dejanski_davek_pdpz = davek_z_odkupom - davek_osnovni
neto_izplacilo = bruto_za_davek - dejanski_davek_pdpz
efektivna_stopnja = (dejanski_davek_pdpz + izstopni_stroski) / pdpz_kapital if pdpz_kapital > 0 else 0

# --- PRIKAZ REZULTATOV ---
col1, col2 = st.columns(2)
with col1:
    st.metric("Neto prejemek na TRR", f"{neto_izplacilo:,.2f} €")
    st.write(f"**Prvotni razred:** {razred_brez}")
with col2:
    st.metric("Skupni davčni strošek", f"{(dejanski_davek_pdpz + izstopni_stroski):,.2f} €")
    st.write(f"**Novi davčni razred:** :orange[{razred_z}]")

st.divider()

# --- ANALIZA RAZREDOV ---
st.subheader("📊 Vpliv odkupa na dohodnino")
podatki_razred = {
    "Scenarij": ["Brez odkupa PDPZ", "Z enkratnim odkupom"],
    "Letna davčna osnova (€)": [f"{osnova_brez:,.2f}", f"{osnova_z:,.2f}"],
    "Dohodninski razred": [razred_brez, razred_z],
    "Letna dohodnina (€)": [f"{davek_osnovni:,.2f}", f"{davek_z_odkupom:,.2f}"]
}
st.table(pd.DataFrame(podatki_razred))

# --- PODROBNOSTI ---
with st.expander("🔎 Podrobna razčlenitev pojasnil ZPIZ"):
    st.write(f"**Bruto znesek odkupa:** {pdpz_kapital:,.2f} €")
    st.write(f"**Akontacija (25%):** -{bruto_za_davek * 0.25:,.2f} €")
    st.write(f"**Predviden poračun ob dohodnini:** -{max(0, dejanski_davek_pdpz - (bruto_za_davek * 0.25)):,.2f} €")
    st.info(f"Zaradi progresivne lestvice vas vsak evro iz PDPZ v tem primeru stane {efektivna_stopnja*100:.2f}% vrednosti.")

# --- OPOZORILO ---
st.warning("ℹ️ **Informacija ZPIZ:** Pokojninska olajšava (13,5%) znatno zniža dohodnino od pokojnine, vendar se pri enkratnih odkupih PDPZ ta znesek prišteje k ostalim prihodkom, kar vas lahko hitro premakne v višji davčni razred.")
st.error("⚠️ **Pozor:** Izračun vključuje prispevek za dolgotrajno oskrbo (1%), ki postane obvezen v letu 2025.")
