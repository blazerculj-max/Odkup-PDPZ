import streamlit as st
import pandas as pd

# --- LOGIKA IZRAČUNA DOHODNINE (ZAKONODAJA 2026) ---
def pridobi_razred(osnova):
    if osnova <= 9000:
        return "1. razred (16%)", 0.16
    elif osnova <= 25000:
        return "2. razred (26%)", 0.26
    else:
        return "3. razred (33%)", 0.33

def izracun_dohodnine_2026(bruto_vsi, bruto_pok_letna, starost):
    # 1. LINEARNA SPLOŠNA OLAJŠAVA
    osnovna_splosna = 5500.0
    if bruto_vsi <= 16000:
        dodatna_splosna = max(0, 18700 - 1.16875 * bruto_vsi)
        splosna_olajsava_koncna = osnovna_splosna + dodatna_splosna
    else:
        splosna_olajsava_koncna = osnovna_splosna

    # Seniorska olajšava (nad 70 let)
    seniorska_letna = 1600.0 if starost >= 70 else 0.0
    
    # Prispevki (OZP in 1% dolgotrajna oskrba)
    ozp_letni = 37.17 * 12 
    pdo_stopnja = 0.01
    prispevki_pok_letni = ozp_letni + (bruto_pok_letna * pdo_stopnja)
    
    # Davčna osnova
    osnova = max(0, bruto_vsi - prispevki_pok_letni - splosna_olajsava_koncna - seniorska_letna)
    
    # Dohodninska lestvica 2026
    if osnova <= 9000:
        davek = osnova * 0.16
    elif osnova <= 25000:
        davek = 1440 + (osnova - 9000) * 0.26
    else:
        davek = 1440 + 4160 + (osnova - 25000) * 0.33
        
    # Pokojninska olajšava (13,5% od bruto pokojnine)
    olajsava_zpiz = bruto_pok_letna * 0.135
    
    return max(0, davek - olajsava_zpiz), osnova

# --- NASTAVITVE STRANI ---
st.set_page_config(page_title="PDPZ Odkup 2026", layout="centered")
st.title("💰 Kalkulator odkupa PDPZ (2026)")
st.markdown("Izračun davčnega bremena pri predčasnem ali enkratnem dvigu sredstev.")

# --- VHODNI PODATKI ---
with st.sidebar:
    st.header("📋 Vhodni podatki")
    prihodki_delo = st.number_input("Letni bruto prihodki (plača, regres)", value=12000.0, step=500.0)
    letna_pok_bruto = st.number_input("Letna bruto pokojnina", value=18000.0, step=500.0)
    starost = st.slider("Starost", 50, 90, 65)
    
    st.divider()
    st.header("🏦 PDPZ Podatki")
    pdpz_kapital = st.number_input("Znesek na PDPZ računu (€)", value=25000.0, step=1000.0)
    stroski_odkupa_odstotek = st.slider("Izstopni stroški (%)", 0.0, 5.0, 1.0) / 100

# --- IZRAČUNI ---
# 1. Osnovno stanje (brez odkupa)
davek_osnovni, osnova_brez = izracun_dohodnine_2026(prihodki_delo + letna_pok_bruto, letna_pok_bruto, starost)
razred_brez, _ = pridobi_razred(osnova_brez)

# 2. Stanje z odkupom
izstopni_stroski = pdpz_kapital * stroski_odkupa_odstotek
bruto_za_davek = pdpz_kapital - izstopni_stroski
# Pri enkratnem odkupu gre celoten znesek v dohodninsko osnovo
davek_z_odkupom, osnova_z = izracun_dohodnine_2026(prihodki_delo + letna_pok_bruto + bruto_za_davek, letna_pok_bruto, starost)
razred_z, _ = pridobi_razred(osnova_z)

# Dejanski strošek davka zaradi PDPZ
dejanski_davek_pdpz = davek_z_odkupom - davek_osnovni
neto_izplacilo = bruto_za_davek - dejanski_davek_pdpz
efektivna_obdavcitev = (dejanski_davek_pdpz + izstopni_stroski) / pdpz_kapital

# --- PRIKAZ REZULTATOV ---
col1, col2 = st.columns(2)

with col1:
    st.metric("Neto izplačilo na TRR", f"{neto_izplacilo:,.2f} €")
    st.write(f"**Davčni razred PRED:** {razred_brez}")

with col2:
    st.metric("Skupna izguba (davek + stroški)", f"{(dejanski_davek_pdpz + izstopni_stroski):,.2f} €")
    st.write(f"**Davčni razred POTEM:** :orange[{razred_z}]")

st.divider()

# --- ANALIZA RAZREDOV ---
st.subheader("📊 Vpliv na dohodninsko lestvico")

podatki_razred = {
    "Scenarij": ["Brez odkupa", "Z enkratnim odkupom"],
    "Letna davčna osnova (€)": [f"{osnova_brez:,.2f}", f"{osnova_z:,.2f}"],
    "Dohodninski razred": [razred_brez, razred_z],
    "Letna dohodnina (€)": [f"{davek_osnovni:,.2f}", f"{davek_z_odkupom:,.2f}"]
}
st.table(pd.DataFrame(podatki_razred))

# --- PODROBNOSTI ---
with st.expander("🔎 Podrobna razčlenitev stroškov"):
    st.write(f"1. **Zbrana sredstva:** {pdpz_kapital:,.2f} €")
    st.write(f"2. **Izstopni stroški upravljavca:** -{izstopni_stroski:,.2f} €")
    st.write(f"3. **Akontacija dohodnine (25% ob izplačilu):** {bruto_za_davek * 0.25:,.2f} €")
    st.write(f"4. **Dodatni poračun dohodnine (ocena):** {max(0, dejanski_davek_pdpz - (bruto_za_davek * 0.25)):,.2f} €")
    st.info(f"Skupna efektivna stopnja obdavčitve vašega privarčevanega denarja je **{efektivna_obdavcitev*100:.2f} %**.")

# --- OPOZORILO ---
st.warning("""
**Pomembno:** Pri enkratnem odkupu PDPZ se v davčno osnovo všteje **100 %** prejetega zneska. 
Če bi se odločili za **dosmrtno rento**, bi se v davčno osnovo štelo le **50 %** zneska rente, 
kar bi vas verjetno ohranilo v nižjem davčnem razredu.
""")

st.caption("Izračun je informativne narave in temelji na predvideni zakonodaji za leto 2026.")
