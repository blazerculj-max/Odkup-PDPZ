import streamlit as st
import pandas as pd

# --- LOGIKA IZRAČUNA DOHODNINE (URADNA ZAKONODAJA 2025/2026) ---

def pridobi_razred_2026(osnova):
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
    osnovna_splosna = 5500.00
    meja_dodatna = 16000.00
    
    if bruto_vsi <= meja_dodatna:
        splosna_olajsava_koncna = osnovna_splosna + (18761.40 - 1.17259 * bruto_vsi)
    else:
        splosna_olajsava_koncna = osnovna_splosna

    seniorska_letna = 1500.00 if starost >= 70 else 0.0
    
    # Prispevki (OZP + 1% Dolgotrajna oskrba)
    ozp_letni = 35.00 * 12 
    prispevek_do = bruto_pok_letna * 0.01
    skupni_prispevki = ozp_letni + prispevek_do
    
    osnova = max(0, bruto_vsi - skupni_prispevki - splosna_olajsava_koncna - seniorska_letna)
    
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
        
    olajsava_zpiz = bruto_pok_letna * 0.135
    koncni_davek = max(0, davek - olajsava_zpiz)
    return koncni_davek, osnova

# --- NASTAVITVE STRANI ---
st.set_page_config(page_title="PDPZ Analiza Izgube", layout="centered")
st.title("🛡️ Analiza enkratnega odkupa PDPZ (2026)")

# --- STRANSKI MENI ---
with st.sidebar:
    st.header("👤 Vaši podatki")
    letna_pok_bruto = st.number_input("Letna bruto pokojnina (€)", value=15000.0, step=500.0)
    drugi_prihodki = st.number_input("Ostali bruto prihodki (€)", value=0.0, step=500.0)
    starost = st.slider("Starost", 50, 95, 67)
    
    st.divider()
    st.header("💰 PDPZ Sredstva")
    pdpz_kapital = st.number_input("Stanje na PDPZ računu (€)", value=20000.0, step=1000.0)
    st.info("Upoštevano: 1% izstopni stroški in 25% akontacija dohodnine.")

# --- IZRAČUNI ---

# 1. Osnovno stanje brez odkupa
davek_osnovni, osnova_brez = izracun_dohodnine_2026(letna_pok_bruto + drugi_prihodki, letna_pok_bruto, starost)

# 2. Odkup
izstopni_stroski = pdpz_kapital * 0.01  # Fiksno 1%
osnova_za_davek = pdpz_kapital - izstopni_stroski
akontacija_25 = osnova_za_davek * 0.25  # Takojšen odbitek

# 3. Končni poračun dohodnine na letni ravni
vsi_prihodki_z_odkupom = letna_pok_bruto + drugi_prihodki + osnova_za_davek
davek_skupaj_z_odkupom, osnova_z = izracun_dohodnine_2026(vsi_prihodki_z_odkupom, letna_pok_bruto, starost)

# Dejanski strošek dohodnine, ki odpade na PDPZ
dejanska_dohodnina_na_pdpz = davek_skupaj_z_odkupom - davek_osnovni
dodatni_poracun = max(0, dejanska_dohodnina_na_pdpz - akontacija_25)

# Skupna izguba in neto izplačilo
skupna_izguba = izstopni_stroski + dejanska_dohodnina_na_pdpz
neto_izplacilo_na_trr = pdpz_kapital - skupna_izguba
odstotek_izgube = (skupna_izguba / pdpz_kapital * 100) if pdpz_kapital > 0 else 0

# --- PRIKAZ ---

st.subheader("Končni finančni učinek")
c1, c2 = st.columns(2)
with c1:
    st.metric("Neto izplačilo na TRR", f"{neto_izplacilo_na_trr:,.2f} €")
    st.caption("Znesek, ki vam ostane po vseh dajatvah in stroških.")
with c2:
    st.metric("Skupna izguba (%)", f"{odstotek_izgube:.2f} %", delta=f"-{skupna_izguba:,.2f} €", delta_color="inverse")
    st.caption("Delež, ki ga vzamejo država in stroški.")

st.divider()

# --- RAZČLENITEV ---
st.write("### Kam izgine vaš denar?")
razclenitev_data = {
    "Postavka": ["Bruto kapital na računu", "Izstopni stroški (1%)", "Akontacija dohodnine (25%)", "Morebitni dodatni poračun (FURS)", "NETO IZPLAČILO"],
    "Znesek (€)": [
        f"{pdpz_kapital:,.2f}", 
        f"-{izstopni_stroski:,.2f}", 
        f"-{akontacija_25:,.2f}", 
        f"-{dodatni_poracun:,.2f}", 
        f"**{neto_izplacilo_na_trr:,.2f}**"
    ],
    "Opomba": ["100%", "Strošek upravljavca", "Odvedeno takoj", "Zaradi progresije", "Vaš čisti denar"]
}
st.table(pd.DataFrame(razclenitev_data))

# --- OPOZORILO ---
if dodatni_poracun > 0:
    st.warning(f"**Pozor:** Ker ste vstopili v višje davčne razrede, vam 25% akontacija ne zadošča. Pričakujete lahko dodatno plačilo dohodnine v višini **{dodatni_poracun:,.2f} €** ob prejemu odločbe FURS.")
else:
    st.success("Vaši prihodki so dovolj nizki, da 25% akontacija verjetno pokrije vso dohodnino (ali pa celo prejmete nekaj vrnjeno).")

st.info("💡 **Nasvet:** Pri enkratnem dvigu država obravnava vaš dolgoletni prihranek kot 'zaslužek v enem letu', kar povzroči visoko obdavčitev. Premislite o rentnem izplačilu.")
