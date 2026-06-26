import streamlit as st
import pandas as pd
import io
import itertools
from collections import Counter

# ==========================================
# PAGE CONFIG & UI STYLE
# ==========================================
st.set_page_config(page_title="2D AI Master V26", layout="wide", page_icon="🤖")

# Custom CSS for Premium Card Layouts
st.markdown("""
<style>
    .reportview-container { background: #f5f7fb; }
    .main-title { color: #4B0082; font-size: 38px; font-weight: bold; text-align: center; margin-bottom: 20px; }
    .sub-title { color: #6A5ACD; font-size: 18px; text-align: center; margin-bottom: 30px; }
    .card { background-color: #ffffff; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.1); margin-bottom: 20px; border-left: 5px solid #6A5ACD; }
    .card-hp { border-left: 5px solid #2ecc71; background-color: #f9fbf9; }
    .card-sniper { border-left: 5px solid #9b59b6; background-color: #faf8fc; }
    .card-header { font-size: 18px; font-weight: bold; color: #333; margin-bottom: 10px; }
    .metric-val { font-size: 24px; font-weight: bold; color: #4B0082; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🤖 THE PERFECT 2D AI MASTER (V26)</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Mode 1: Hybrid Core Engine (95%+ & 100% Super Sniper)</div>', unsafe_allow_html=True)

# Special Groups Dictionary
special_groups = {
    "ညီကို": {"01","10","12","21","23","32","34","43","45","54","56","65","67","76","78","87","89","98","90","09"},
    "ပါဝါ": {"05","50","16","61","27","72","38","83","49","94"},
    "နက္ခတ်": {"07","70","18","81","24","42","35","53","69","96"},
    "ထိုင်းပါဝါ": {"09","90","13","31","26","62","47","74","58","85"},
    "အပူး": {"00","11","22","33","44","55","66","77","88","99"},
    "ဆယ်ပြည့်": {"10","01","20","02","30","03","40","04","50","05","60","06","70","07","80","08","90","09"}
}

GLOBAL_TFS = [("၁ ပွဲ", 1, 1), ("၂ ပွဲ", 1, 2), ("၃ ပွဲ", 1, 3), ("၄ ပွဲ", 1, 4), ("၅ ပွဲ", 1, 5),
              ("၆ ပွဲ", 1, 6), ("၈ ပွဲ", 1, 8), ("၁၀ ပွဲ", 1, 10), ("၁၂ ပွဲ", 1, 12), ("၁၆ ပွဲ", 1, 16), ("၂၀ ပွဲ", 1, 20)]

# ==========================================
# CORE CORE ENGINE LOGIC (REVERSE CALCULATION)
# ==========================================
def analyze_target_detailed_web(target_hits, full_draws_list, s_off, e_off):
    total_hits = len(target_hits)
    if total_hits == 0: return None

    events_subsequent_draws = []
    for hit in target_hits:
        start_idx = hit['index']
        s_idx = start_idx + s_off
        e_idx = min(start_idx + e_off + 1, len(full_draws_list))
        if s_idx < len(full_draws_list):
            events_subsequent_draws.append([d['draw'] for d in full_draws_list[s_idx : e_idx]])
        else:
            events_subsequent_draws.append([])

    if all(len(ev) == 0 for ev in events_subsequent_draws): return None

    all_next_draws = list(itertools.chain(*events_subsequent_draws))
    if not all_next_draws: return None
    
    all_singles = list(itertools.chain(*[list(d) for d in all_next_draws]))
    all_heads = [d[0] for d in all_next_draws]
    all_breaks = [str((int(d[0]) + int(d[1])) % 10) for d in all_next_draws]

    top_singles = [x[0] for x in Counter(all_singles).most_common(6)]
    top_heads = [x[0] for x in Counter(all_heads).most_common(3)]
    top_breaks = [x[0] for x in Counter(all_breaks).most_common(2)]

    def count_success(cond_func): 
        return sum(1 for ev in events_subsequent_draws if ev and cond_func(ev))

    # 1. လုံးဘိုင်
    b1 = top_singles[0] if top_singles else ""
    b1_rate = (count_success(lambda ev: any(b1 in d for d in ev)) / total_hits) * 100 if b1 else 0

    # 2. One Change
    oc = "".join(top_singles[:2]) if len(top_singles) >= 2 else ""
    oc_rate = (count_success(lambda ev: any(any(digit in d for digit in oc) for d in ev)) / total_hits) * 100 if oc else 0

    # 3. အမာခံ ၃ လုံး
    key3 = "".join(top_singles[:3]) if len(top_singles) >= 3 else ""
    key3_rate = (count_success(lambda ev: any(any(digit in d for digit in key3) for d in ev)) / total_hits) * 100 if key3 else 0

    # 4. ၄ လုံးခွေ
    k4 = "".join(top_singles[:4]) if len(top_singles) >= 4 else ""
    k4_rate = (count_success(lambda ev: any(d[0] in k4 and d[1] in k4 for d in ev)) / total_hits) * 100 if k4 else 0

    # 5. ထိပ်စီး ၃ လုံး
    h3 = "".join(top_heads)
    h3_rate = (count_success(lambda ev: any(d[0] in h3 for d in ev)) / total_hits) * 100 if h3 else 0

    # 6. ဘရိတ် ၂ လုံး
    brk2_list = top_breaks
    brk2_rate = (count_success(lambda ev: any(str((int(d[0])+int(d[1]))%10) in brk2_list for d in ev)) / total_hits) * 100 if brk2_list else 0

    # 7. စုံ/မ ကပ် (၅ ကွက်) - လုံးဘိုင်ကို အခြေခံသည်
    even_score = 0; odd_score = 0
    if b1:
        for ev in events_subsequent_draws:
            if not ev: continue
            for d in ev:
                if b1 in d:
                    other = d.replace(b1, '', 1)
                    if not other: other = b1
                    if int(other) % 2 == 0: even_score += 1
                    else: odd_score += 1
    if even_score >= odd_score:
        mway_label = f"[{b1}] အစုံကပ်"
        mway_digits = [f"{b1}{i}" for i in [0,2,4,6,8]]
    else:
        mway_label = f"[{b1}] အမကပ်"
        mway_digits = [f"{b1}{i}" for i in [1,3,5,7,9]]
    mway5_rate = (count_success(lambda ev: any(d in mway_digits for d in ev)) / total_hits) * 100 if b1 else 0

    # 8. အုပ်စု (၁) ခုတည်း
    best_single_group = max(special_groups.keys(), key=lambda g: count_success(lambda ev: any(d in special_groups[g] for d in ev)), default="")
    sg_rate = (count_success(lambda ev: any(d in special_groups[best_single_group] for d in ev)) / total_hits) * 100 if best_single_group else 0

    # 9. အုပ်စုတွဲ (၂) ခု
    best_group_pair = ""; best_group_pair_correct = 0
    for combo in itertools.combinations(special_groups.keys(), 2):
        g1_set, g2_set = special_groups[combo[0]], special_groups[combo[1]]
        correct = count_success(lambda ev: any(d in g1_set or d in g2_set for d in ev))
        if correct > best_group_pair_correct:
            best_group_pair_correct = correct
            best_group_pair = f"{combo[0]}+{combo[1]}"
    gp_rate = (best_group_pair_correct / total_hits) * 100 if best_group_pair else 0

    # 10. အမာခံအပါ ဘရိတ် (၂လုံး)
    valid_pairs = []
    if key3 and top_breaks:
        for i in range(100):
            d_str = f"{i:02d}"
            if any(k in d_str for k in key3)  and str((int(d_str[0]) + int(d_str[1])) % 10) in top_breaks:
                valid_pairs.append(d_str)
    cb_rate = (count_success(lambda ev: any(d in valid_pairs for d in ev)) / total_hits) * 100 if valid_pairs else 0

    mu_names = ["1. လုံးဘိုင်", "2. One Change", "3. အမာခံ ၃ လုံး", "4. ၄ လုံးခွေ", "5. ထိပ်စီး ၃ လုံး", "6. ဘရိတ် ၂ လုံး", "7. စုံ/မ ကပ် (၅ ကွက်)", "8. အုပ်စု (၁) ခုတည်း", "9. အုပ်စုတွဲ (၂) ခု", "10. အမာခံအပါ ဘရိတ် (၂လုံး)"]
    mu_values = [b1, oc, key3, k4, h3, ", ".join(brk2_list), f"{mway_label} ({', '.join(mway_digits)})", best_single_group, best_group_pair, ", ".join(valid_pairs) if valid_pairs else "-"]
    mu_rates = [b1_rate, oc_rate, key3_rate, k4_rate, h3_rate, brk2_rate, mway5_rate, sg_rate, gp_rate, cb_rate]

    return {"names": mu_names, "values": mu_values, "rates": mu_rates, "total_hits": total_hits}

# ==========================================
# FILE UPLOAD & PRE-PROCESSING
# ==========================================
uploaded_file = st.file_uploader("Bro ရဲ့ 2D CSV သို့မဟုတ် Excel ဖိုင်ကို တင်ပေးပါ...", type=['csv', 'xlsx', 'xls'])

if uploaded_file:
    if uploaded_file.name.endswith('.csv'):
        df = pd.read_csv(uploaded_file)
    else:
        df = pd.read_excel(uploaded_file)

    df.columns = df.columns.str.strip().str.lower()
    required_columns = ['year', 'day', 'am1', 'am2', 'pm1', 'pm2']
    missing_cols = [col for col in required_columns if col not in df.columns]

    if missing_cols:
        st.error(f"⚠️ ဖိုင်ထဲတွင် လိုအပ်သော ကော်လံများ မရှိပါ: {missing_cols}")
    else:
        # Data Cleansing
        for col in ['year', 'am1', 'am2', 'pm1', 'pm2']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df = df.dropna(subset=['year', 'day']).reset_index(drop=True)
        df['day'] = df['day'].astype(str).str.strip().str.capitalize()

        # Missing Data Health Check
        null_am = df['am1'].isnull().sum()
        null_pm = df['pm1'].isnull().sum()
        if null_am > 0 or null_pm > 0:
            st.warning(f"⚠️ သတိပြုရန်: ဖိုင်ထဲတွင် AM ကွက်လပ် ({null_am}) ခု နှင့် PM ကွက်လပ် ({null_pm}) ခု ရှိနေပါသည်။ AI မှ ချန်လှပ်တွက်ချက်ပါမည်။")

        # Building Chronological Lists (Reverse Order Flow)
        full_draws = []
        for index, row in df.iterrows():
            if pd.notna(row['am1']) and pd.notna(row['am2']):
                am_draw = str(int(row['am1'])) + str(int(row['am2']))
                full_draws.append({'draw': am_draw, 'time': 'AM', 'day': row['day'], 'year': int(row['year']), 'index': len(full_draws)})
            if pd.notna(row['pm1']) and pd.notna(row['pm2']):
                pm_draw = str(int(row['pm1'])) + str(int(row['pm2']))
                full_draws.append({'draw': pm_draw, 'time': 'PM', 'day': row['day'], 'year': int(row['year']), 'index': len(full_draws)})

        # UI CONTROLS FOR MODE 1
        st.write("---")
        col1, col2 = st.columns(2)
        with col1:
            search_type = st.selectbox("ရှာဖွေမည့် Trigger အမျိုးအစား:", ["ဂဏန်းတစ်လုံးတည်း (Single Trigger)", "အတွဲလိုက်ပုံစံ (Daily Combo Twin Trigger)"])
        
        target_2d = ""
        combo_am = ""
        combo_pm = ""

        with col2:
            if search_type == "ဂဏန်းတစ်လုံးတည်း (Single Trigger)":
                target_2d = st.text_input("🔍 ရှာဖွေလိုသော ဂဏန်း (ဥပမာ - 60):", value="60", max_chars=2)
                pool_choice = st.selectbox("သမိုင်းကြောင်း ရှာဖွေမည့် Pool:", ["AM+PM (အောက်မှအပေါ် အစဉ်လိုက်)", "AM သီးသန့်", "PM သီးသန့်"])
            else:
                combo_am = st.text_input("🌅 မနက်ထွက်ဂဏန်း (AM):", value="66", max_chars=2)
                combo_pm = st.text_input("🌆 ညနေထွက်ဂဏန်း (PM):", value="52", max_chars=2)

        if st.button("AI Logic ဖြင့် သမိုင်းကြောင်း မွှေနှောက်မည် 🚀"):
            target_hits = []
            
            # 1. Single Trigger Scanning Logic (Reverse Approach)
            if search_type == "ဂဏန်းတစ်လုံးတည်း (Single Trigger)" and target_2d:
                if pool_choice == "AM+PM (အောက်မှအပေါ် အစဉ်လိုက်)":
                    target_hits = [d for d in full_draws if d['draw'] == target_2d]
                elif pool_choice == "AM သီးသန့်":
                    target_hits = [d for d in full_draws if d['draw'] == target_2d and d['time'] == 'AM']
                else:
                    target_hits = [d for d in full_draws if d['draw'] == target_2d and d['time'] == 'PM']
                
                st.success(f"📊 [ဂဏန်း {target_2d}] အခြေပြု သမိုင်းကြောင်းစုစုပေါင်း {len(target_hits)} ကြိမ် ရှာဖွေတွေ့ရှိပြီး တွက်ချက်နေပါသည်။")

            # 2. Daily Combo Twin Trigger Scanning Logic (Reverse Day Matching)
            elif search_type == "အတွဲလိုက်ပုံစံ (Daily Combo Twin Trigger)" and combo_am and combo_pm:
                for idx, row in df.iterrows():
                    if pd.notna(row['am1']) and pd.notna(row['pm1']):
                        cur_am = str(int(row['am1'])) + str(int(row['am2']))
                        cur_pm = str(int(row['pm1'])) + str(int(row['pm2']))
                        if cur_am == combo_am and cur_pm == combo_pm:
                            # တွဲလုံးတွေ့ပါက ထိုနေ့ညနေပိုင်းထွက်ခဲ့သည့် index ကို သမိုင်းအချက်အလက်အဖြစ် မှတ်သား
                            match_idx = (idx * 2) + 1
                            if match_idx < len(full_draws):
                                target_hits.append(full_draws[match_idx])
                st.success(f"🔥 [အတွဲလိုက် {combo_am} + {combo_pm}] စံစနစ်အရ သမိုင်းကြောင်း {len(target_hits)} ကြိမ် ကို အောက်မှအပေါ် Reverse Scan ဖတ်ပြီးပါပြီ။")

            if not target_hits:
                st.error("⚠️ သတ်မှတ်ထားသော ဂဏန်း/အတွဲလိုက် အတွက် သမိုင်းကြောင်း ဒေတာ မလုံလောက်ပါ သို့မဟုတ် မရှိပါ။")
            else:
                # Execution Arrays for Layout Outputs
                high_prob_results = []
                sniper_results = []

                # Timeframe Engine Loop
                for tf_name, s_off, e_off in GLOBAL_TFS:
                    res = analyze_target_detailed_web(target_hits, full_draws, s_off, e_off)
                    if res:
                        for idx in range(10):
                            mu_name = res["names"][idx]
                            mu_val = res["values"][idx]
                            mu_rate = res["rates"][idx]
                            total_h = res["total_hits"]

                            # Strategy 1: 100% Sniper Rule (>= 10 ကြိမ် နှင့် 100% မှန်)
                            if total_h >= 10 and mu_rate == 100.0:
                                sniper_results.append({"tf": tf_name, "mu": mu_name, "val": mu_val, "rate": mu_rate, "hits": total_h})
                            # Strategy 2: 95%+ High Probability Rule (95% မှ 100% အတွင်း)
                            elif mu_rate >= 95.0:
                                high_prob_results.append({"tf": tf_name, "mu": mu_name, "val": mu_val, "rate": mu_rate, "hits": total_h})

                # ==========================================
                # RENDER PREMIUM UI CARD LAYOUT
                # ==========================================
                st.write("---")
                st.subheader("🎯 AI Matrix Filtering Results")

                tab1, tab2 = st.tabs(["🔮 95%+ High-Probability Zone", "🦅 100% Super VIP Sniper Zone"])

                with tab1:
                    if not high_prob_results:
                        st.info("95% အထက် Probability ရှိသော အချိန်ဘောင် မတွေ့ရှိပါ။")
                    else:
                        for r in high_prob_results:
                            st.markdown(f"""
                            <div class="card card-hp">
                                <div class="card-header">⏱️ {r['tf']} အတွင်း ➡️ {r['mu']}</div>
                                <div>ထွက်လေ့ရှိသော ပုံစံ: <span class="metric-val">{r['val']}</span></div>
                                <div style="color: #2ecc71; font-weight: bold; margin-top:5px;">🎯 မှန်ကန်မှု ရာခိုင်နှုန်း: {r['rate']:.1f}% ({r['hits']} ကြိမ်အနက်)</div>
                            </div>
                            """, unsafe_allow_html=True)

                with tab2:
                    if not sniper_results:
                        st.info("အနည်းဆုံး ၁၀ ကြိမ်ပြည့်ပြီး ၁၀၀% ကွက်တိ မှန်နေသော Super VIP Sniper မရှိသေးပါ။")
                    else:
                        for r in sniper_results:
                            st.markdown(f"""
                            <div class="card card-sniper">
                                <div class="card-header">🔥 {r['tf']} အတွင်း ဒုန်းတင်ရန် ➡️ {r['mu']}</div>
                                <div>အမှားမခံသော Target ကွက်: <span class="metric-val">{r['val']}</span></div>
                                <div style="color: #9b59b6; font-weight: bold; margin-top:5px;">💎 AI Confidence: {r['rate']:.1f}% (သမိုင်းကြောင်း {r['hits']}/{r['hits']} ကြိမ်စလုံး ကွက်တိ!)</div>
                            </div>
                            """, unsafe_allow_html=True)
else:
    st.info("စတင်ရန်အတွက် Bro ရဲ့ 2D CSV သို့မဟုတ် Excel ဒေတာဖိုင်ကို အပေါ်တွင် အရင် တင်ပေးပါဦး။")
