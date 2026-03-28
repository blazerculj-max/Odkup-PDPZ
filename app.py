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
    
    # Prispevki (OZP + 1% Dolgotrajna oskrba po 2025)
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
st.set_page_config(page_title="PDPZ Odkup 2026", layout="centered")
st.title("🛡️ Svetovalec za odkup PDPZ (2026)")

# --- STRANSKI MENI ---
with st.sidebar:
    st.header("👤 Podatki o prihodkih")
    prihodki_delo = st.number_input("Letni bruto prihodki (plača, regres, sejnine)", value=0.0, step=500.0)
    letna_pok_bruto = st.number_input("Letna bruto pokojnina", value=15000.0, step=500.0)
    starost = st.slider("Starost stranke ob koncu leta", 50, 95, 67)
    
    st.divider()
    st.header("💰 PDPZ Kapital")
    pdpz_kapital = st.number_input("Vsa sredstva na PDPZ računu (€)", value=20000.0, step=1000.0)
    stroski_odkupa_odstotek = st.slider("Izstopni stroški upravljavca (%)", 0.0, 5.0, 1.0) / 100

# --- IZRAČUNI ---
davek_osnovni, osnova_brez = izracun_dohodnine_2026(prihodki_delo + letna_pok_bruto, letna_pok_bruto, starost)

izstopni_stroski = pdpz_kapital * stroski_odkupa_odstotek
bruto_za_davek = pdpz_kapital - izstopni_stroski

davek_z_odkupom, osnova_z = izracun_dohodnine_2026(prihodki_delo + letna_pok_bruto + bruto_za_davek, letna_pok_bruto, starost)

dejanski_davek_pdpz = davek_z_odkupom - davek_osnovni
skupna_izguba = dejanski_davek_pdpz + izstopni_stroski
neto_izplacilo = pdpz_kapital - skupna_izguba

# Procentualni izračun izgube
odstotek_izgube = (skupna_izguba / pdpz_kapital * 100) if pdpz_kapital > 0 else 0

# --- PRIKAZ REZULTATOV ---
st.subheader("Ključni podatki izplačila")
c1, c2, c3 = st.columns(3)
with c1:
    st.metric("Neto na TRR", f"{neto_izplacilo:,.2f} €")
with c2:
    st.metric("Skupna izguba", f"{skupna_izguba:,.2f} €", delta=f"-{odstotek_izgube:.1f}%", delta_color="inverse")
with c3:
    razred_z, _ = pridobi_razred_2026(osnova_z)
    st.metric("Novi davčni razred", razred_z.split(" ")[0])

st.divider()

# --- VIZUALIZACIJA RAZLIKE ---
preostanek_odstotek = 100 - odstotek_izgube
st.write(f"### Kam gre vaš denar?")
st.progress(preostanek_odstotek / 100)
st.caption(f"Prejmete {preostanek_odstotek:.1f}% kapitala | Država in stroški vzamejo {odstotek_izgube:.1f}% kapitala")

# --- PODROBNOSTI ---
with st.expander("🔎 Podrobna razčlenitev razlike"):
    col_a, col_b = st.columns(2)
    with col_a:
        st.write("**Struktura izgube:**")
        st.write(f"- Stroški upravljavca: {izstopni_stroski:,.2f} €")
        st.write(f"- Dejanska dohodnina: {dejanski_davek_pdpz:,.2f} €")
        st.write(f"**= SKUPAJ IZGUBA:** {skupna_izguba:,.2f} €")
    
    with col_b:
        st.write("**Primerjava:**")
        st.write(f"Vrednost na računu: {pdpz_kapital:,.2f} €")
        st.write(f"Dejansko izplačilo: {neto_izplacilo:,.2f} €")
        st.info(f"Razlika (izguba) znaša natanko **{odstotek_izgube:.2f} %** vašega privarčevanega zneska.")

# --- TABELA ---
st.subheader("📊 Primerjava stanja")
podatki_tabela = {
    "Postavka": ["Bruto kapital na računu", "Stroški in davki (izguba)", "Neto znesek po vseh dajatvah"],
    "Znesek (€)": [f"{pdpz_kapital:,.2f} €", f"- {skupna_izguba:,.2f} €", f"{neto_izplacilo:,.2f} €"],
    "Delež (%)": ["100 %", f"{odstotek_izgube:.2f} %", f"{preostanek_odstotek:.2f} %"]
}
st.table(pd.DataFrame(podatki_tabela))

st.error("⚠️ **Pomembno:** Pri enkratnem dvigu vas progresivna lestvica udari najmočneje. Če bi izbrali rento, bi bila davčna osnova le 50% zneska, kar bi drastično zmanjšalo 'izgubo'.")
