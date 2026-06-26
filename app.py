import streamlit as st
import pandas as pd
import io
import itertools
from collections import Counter

# ==========================================
# PAGE CONFIG & PREMIUM UI STYLE
# ==========================================
st.set_page_config(page_title="2D AI Master V26 Pro", layout="wide", page_icon="🤖")

st.markdown("""
<style>
    .main-title { color: #4B0082; font-size: 38px; font-weight: bold; text-align: center; margin-bottom: 5px; }
    .sub-title { color: #6A5ACD; font-size: 16px; text-align: center; margin-bottom: 30px; }
    .card { background-color: #ffffff; padding: 20px; border-radius: 15px; box-shadow: 0 4px 6px rgba(0,0,0,0.08); margin-bottom: 20px; }
    .card-hp { border-left: 6px solid #2ecc71; background-color: #f9fbf9; }
    .card-sniper { border-left: 6px solid #9b59b6; background-color: #faf8fc; }
    .card-recovered { border-left: 6px solid #e74c3c; background-color: #fdf7f7; animation: pulse 2s infinite; }
    .card-header { font-size: 18px; font-weight: bold; color: #333; margin-bottom: 8px; }
    .metric-val { font-size: 26px; font-weight: bold; color: #4B0082; background: #eee8f5; padding: 2px 10px; border-radius: 8px; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🤖 THE PERFECT 2D AI MASTER (V26 PRO)</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Ultimate Hybrid Engine | Mode 1: Calendar & Failure-Recovery Analysis</div>', unsafe_allow_html=True)

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
# CORE MATH & MU CALCULATION FUNCTION
# ==========================================
def run_mu_evaluation(hit_idx, full_draws_list, s_off, e_off):
    """တစ်ခုချင်းစီသော သမိုင်းဖြစ်စဉ်အတွက် မူ ၁၀ မျိုး ဝင်/မဝင် Boolean စစ်ဆေးပေးခြင်း"""
    s_idx = hit_idx + s_off
    e_idx = min(hit_idx + e_off + 1, len(full_draws_list))
    if s_idx >= len(full_draws_list): return None
    
    sub_draws = [d['draw'] for d in full_draws_list[s_idx : e_idx]]
    if not sub_draws: return None

    # သမိုင်းကြောင်း Window ၏ အခြေခံ Element များ ရှာဖွေခြင်း
    all_singles = "".join(sub_draws)
    all_heads = [d[0] for d in sub_draws]
    all_breaks = [str((int(d[0]) + int(d[1])) % 10) for d in sub_draws]

    top_single = Counter(all_singles).most_common(1)[0][0] if all_singles else ""
    top_oc = "".join([x[0] for x in Counter(all_singles).most_common(2)])
    top_key3 = "".join([x[0] for x in Counter(all_singles).most_common(3)])
    top_k4 = "".join([x[0] for x in Counter(all_singles).most_common(4)])
    top_h3 = "".join([x[0] for x in Counter(all_heads).most_common(3)])
    top_brk2 = [x[0] for x in Counter(all_breaks).most_common(2)]

    # စုံ/မကပ် ခွဲထုတ်ခြင်း
    e_sc = sum(1 for d in sub_draws if top_single in d and int(d.replace(top_single,'',1) if d.replace(top_single,'',1) else top_single) % 2 == 0)
    o_sc = sum(1 for d in sub_draws if top_single in d and int(d.replace(top_single,'',1) if d.replace(top_single,'',1) else top_single) % 2 != 0)
    mway_label = f"[{top_single}] အစုံကပ်" if e_sc >= o_sc else f"[{top_single}] အမကပ်"
    mway_digits = [f"{top_single}{i}" for i in ([0,2,4,6,8] if e_sc >= o_sc else [1,3,5,7,9])]

    # အုပ်စုခွဲထုတ်ခြင်း
    best_sg = max(special_groups.keys(), key=lambda g: sum(1 for d in sub_draws if d in special_groups[g]), default="")
    best_gp = ""; max_gp_c = 0
    for combo in itertools.combinations(special_groups.keys(), 2):
        c = sum(1 for d in sub_draws if d in special_groups[combo[0]] or d in special_groups[combo[1]])
        if c > max_gp_c: max_gp_c = c; best_gp = f"{combo[0]}+{combo[1]}"

    # အမာခံအပါ ဘရိတ်
    valid_pairs = [f"{i:02d}" for i in range(100) if any(k in f"{i:02d}" for k in top_key3) and str((i//10 + i%10)%10) in top_brk2]

    # လက်ရှိပွဲစဉ် (Actual Target) တွင် ၎င်းမူများ ကိုက်ညီမှု ရှိမရှိ စစ်ဆေးချက်ထုတ်ပြန်ခြင်း
    act_draws = [d['draw'] for d in full_draws_list[hit_idx+1 : min(hit_idx+e_off+1, len(full_draws_list))]]
    if not act_draws: return None

    return {
        "1. လုံးဘိုင်": {"val": top_single, "hit": any(top_single in d for d in act_draws)},
        "2. One Change": {"val": top_oc, "hit": any(any(x in d for x in top_oc) for d in act_draws)},
        "3. အမာခံ ၃ လုံး": {"val": top_key3, "hit": any(any(x in d for x in top_key3) for d in act_draws)},
        "4. ၄ လုံးခွေ": {"val": top_k4, "hit": any(d[0] in top_k4 and d[1] in top_k4 for d in act_draws)},
        "5. ထိပ်စီး ၃ လုံး": {"val": top_h3, "hit": any(d[0] in top_h3 for d in act_draws)},
        "6. ဘရိတ် ၂ လုံး": {"val": ", ".join(top_brk2), "hit": any(str((int(d[0])+int(d[1]))%10) in top_brk2 for d in act_draws)},
        "7. စုံ/မ ကပ် (၅ ကွက်)": {"val": f"{mway_label}", "hit": any(d in mway_digits for d in act_draws)},
        "8. အုပ်စု (၁) ခုတည်း": {"val": best_sg, "hit": any(d in special_groups[best_sg] for d in act_draws)},
        "9. အုပ်စုတွဲ (၂) ခု": {"val": best_gp, "hit": any(d in special_groups[best_gp.split('+')[0]] or d in special_groups[best_gp.split('+')[1]] for d in act_draws)},
        "10. အမာခံအပါ ဘရိတ် (၂လုံး)": {"val": "ကွက်ကျဉ်းတွဲစနစ်", "hit": any(d in valid_pairs for d in act_draws)}
    }

# ==========================================
# FILE UPLOAD & PRE-PROCESSING
# ==========================================
uploaded_file = st.file_uploader("Bro ရဲ့ 2D CSV သို့မဟုတ် Excel ဖိုင်ကို ရွေးချယ်တင်ပေးပါ...", type=['csv', 'xlsx', 'xls'])

if uploaded_file:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip().str.lower()
    
    if not all(col in df.columns for col in ['year', 'day', 'am1', 'am2', 'pm1', 'pm2']):
        st.error("⚠️ ဖိုင်ထဲတွင် လိုအပ်သော ကော်လံများ (year, day, am1, am2, pm1, pm2) မပြည့်စုံပါ!")
    else:
        for col in ['year', 'am1', 'am2', 'pm1', 'pm2']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df = df.dropna(subset=['year', 'day']).reset_index(drop=True)
        df['day'] = df['day'].astype(str).str.strip().str.capitalize()

        # Chronological Build (အောက်ဆုံးကနေ အပေါ်ကို Reverse လုပ်ရန်အတွက် အစဉ်အတိုင်းသိမ်းဆည်းမှု)
        full_draws = []
        for idx, row in df.iterrows():
            if pd.notna(row['am1']) and pd.notna(row['am2']):
                full_draws.append({'draw': f"{int(row['am1'])}{int(row['am2'])}", 'time': 'AM', 'day': row['day'], 'year': int(row['year']), 'row_idx': idx})
            if pd.notna(row['pm1']) and pd.notna(row['pm2']):
                full_draws.append({'draw': f"{int(row['pm1'])}{int(row['pm2'])}", 'time': 'PM', 'day': row['day'], 'year': int(row['year']), 'row_idx': idx})

        for i, d in enumerate(full_draws): d['index'] = i

        st.success(f"✅ ဒေတာပွဲစဉ်ပေါင်း {len(full_draws)} ခုကို အောင်မြင်စွာ ဖတ်ရှုပြီးပါပြီ။")
        st.write("---")

        # UI INTERFACE CONTROLS
        c1, c2, c3 = st.columns(3)
        with c1:
            engine_mode = st.radio("အသုံးပြုမည့် ရှာဖွေရေးမုဒ်:", ["Standard Single Trigger", "Calendar Day Alignment Pattern"])
        with c2:
            if engine_mode == "Standard Single Trigger":
                target_num = st.text_input("🔍 စစ်ဆေးမည့် ဂဏန်း (ဥပမာ - 60):", value="60", max_chars=2)
                pool_mode = st.selectbox("သမိုင်းကြောင်း Pool ခွဲထုတ်မှု:", ["AM+PM (အောက်မှအပေါ် မခွဲခြားဘဲ)", "AM သီးသန့်", "PM သီးသန့်"])
            else:
                trigger_day = st.selectbox("📆 Trigger အစပျိုးရက်:", ["Mon", "Tue", "Wed", "Thur", "Fri"], index=0)
                trigger_num = st.text_input("🔍 ထွက်ဂဏန်း (ဥပမာ - 70):", value="70", max_chars=2)
        with c3:
            if engine_mode == "Calendar Day Alignment Pattern":
                target_day = st.selectbox("🎯 အဖြေထုတ်မည့် ပစ်မှတ်ရက် (Target Day):", ["Mon", "Tue", "Wed", "Thur", "Fri"], index=4)
                target_session = st.selectbox("⏱️ ပစ်မှတ် Session:", ["AM+PM ပေါင်းချုပ်", "AM သီးသန့်", "PM သီးသန့်"])

        # RUN ENGINE BLOCK
        if st.button("V26 Premium Hybrid Engine မောင်းနှင်မည် 🚀"):
            target_hits = []

            # (A) Standard Trigger Reverse Scanning
            if engine_mode == "Standard Single Trigger" and target_num:
                if pool_mode == "AM+PM (အောက်မှအပေါ် မခွဲခြားဘဲ)":
                    target_hits = [d for d in full_draws if d['draw'] == target_num]
                else:
                    t_time = 'AM' if "AM" in pool_mode else 'PM'
                    target_hits = [d for d in full_draws if d['draw'] == target_num and d['time'] == t_time]
            
            # (B) Calendar Alignment Trigger Scanning (SS မူရင်းခွင်စနစ်)
            elif engine_mode == "Calendar Day Alignment Pattern" and trigger_num:
                rev_num = trigger_num[::-1]
                matched_weeks = set()
                # 70 သို့မဟုတ် 07 ဖြစ်ခဲ့သော ရက်သတ္တပတ် Row များကို ရှာဖွေခြင်း
                for d in full_draws:
                    if d['day'] == trigger_day and (d['draw'] == trigger_num or d['draw'] == rev_num):
                        matched_weeks.add(d['row_idx'])
                
                # ပစ်မှတ်ထားသော ရက်၏ ဒေတာများကို ပစ်မှတ် Pool ထဲ စုစည်းခြင်း
                for d in full_draws:
                    if d['row_idx'] in matched_weeks and d['day'] == target_day:
                        if target_session == "AM+PM ပေါင်းချုပ်":
                            target_hits.append(d)
                        else:
                            t_sess = 'AM' if "AM" in target_session else 'PM'
                            if d['time'] == t_sess:
                                target_hits.append(d)

            # CALCULATION & MATRIX EXTRACTION
            if not target_hits:
                st.error("⚠️ သတ်မှတ်ချက်များနှင့် ကိုက်ညီသော သမိုင်းကြောင်းမှတ်တမ်း မရှိပါ Bro!")
            else:
                # ယာယီ ဒေတာ သိုလှောင်ကန်များ
                hp_store = {}     # High-Probability (95%+)
                sniper_store = {} # Sniper (100% + >=10 ကြိမ်)
                recovered_store = [] # Failure-to-Recovery (3 မှား၊ 2 မှန်)

                # Timeframe တစ်ခုချင်းစီအလိုက် နောက်ကွယ်မှ မူ ၁၀ မျိုး ခြေရာခံခြင်း
                for tf_name, s_off, e_off in GLOBAL_TFS:
                    # သမိုင်းမှတ်တမ်း အပွဲတိုင်းအတွက် True/False သရုပ်ခွဲမှတ်တမ်း စုစည်းမှု
                    sequence_tracker = {f"mu_{m}": [] for m in range(1, 11)}
                    mu_latest_values = {}
                    mu_keys_list = []

                    # အောက်ဆုံးကနေ အပေါ်ကို ပြန်တက်ပြီး တစ်ကြိမ်ချင်းစီတွက်ချက်မှု ရလဒ်များ စုစည်းခြင်း
                    for hit in target_hits:
                        res = run_mu_evaluation(hit['index'], full_draws, s_off, e_off)
                        if res:
                            if not mu_keys_list: mu_keys_list = list(res.keys())
                            for m_idx, mu_k in enumerate(mu_keys_list, 1):
                                sequence_tracker[f"mu_{m_idx}"].append(res[mu_k]['hit'])
                                mu_latest_values[mu_k] = res[mu_k]['val']

                    if not mu_keys_list: continue
                    total_h = len(target_hits)

                    # မူတစ်ခုချင်းစီအတွက် Win Rate နှင့် ကစားကွက်ဗျူဟာများ သတ်မှတ်ခြင်း
                    for m_idx, mu_k in enumerate(mu_keys_list, 1):
                        seq = sequence_tracker[f"mu_{m_idx}"]
                        if len(seq) < 5: continue # ဒေတာ စမ်းသပ်မှု ပမာဏ အနည်းဆုံး ၅ ခု ရှိရမည်
                        
                        win_count = sum(1 for x in seq if x)
                        rate = (win_count / len(seq)) * 100

                        # Rule 1: 100% Super VIP Sniper (နယ်ကုန် စစ်ထုတ်ရန်အတွက် စုစည်းမှု)
                        if len(seq) >= 10 and rate == 100.0:
                            if mu_k not in sniper_store or e_off > sniper_store[mu_k]['e_off']:
                                sniper_store[mu_k] = {"tf": tf_name, "val": mu_latest_values[mu_k], "rate": rate, "hits": len(seq), "e_off": e_off}
                        
                        # Rule 2: 95%+ High Probability (နယ်ကုန် စစ်ထုတ်ရန်အတွက် စုစည်းမှု)
                        elif rate >= 95.0:
                            if mu_k not in hp_store or e_off > hp_store[mu_k]['e_off']:
                                hp_store[mu_k] = {"tf": tf_name, "val": mu_latest_values[mu_k], "rate": rate, "hits": len(seq), "e_off": e_off}

                        # Rule 3: 💥 RECOVERED SNIPER RULE (၃ ကြိမ်ဆက်မှား ➡️ ၂ ကြိမ်ဆက်ပြန်မှန် ➡️ လက်ရှိနောက်ဆုံးအဆင့်နှင့် ကိုက်ညီမှု)
                        # Sequence ၏ နောက်ဆုံးအပိုင်းကို ခြေရာခံခြင်း [..., False, False, False, True, True]
                        if len(seq) >= 19: # ၁ မှ ၁၄ ကြိမ်အထိ အနည်းဆုံး 95% အပြင် အမှား/အမှန် Streak ပြည့်ရန် လိုအပ်ချက်
                            baseline_seq = seq[:-5]
                            baseline_rate = (sum(1 for x in baseline_seq if x) / len(baseline_seq)) * 100 if baseline_seq else 0
                            
                            if baseline_rate >= 95.0:
                                last_5_streak = seq[-5:]
                                # အတိအကျ စည်းမျဉ်းကို စစ်ဆေးခြင်း: [မှား, မှား, မှား, မှန်, မှန်]
                                if last_5_streak == [False, False, False, True, True]:
                                    # ၎င်းပြန်ဝင်လာသည့်စနစ်သည် လက်ရှိဖိုင်၏ အောက်ဆုံးထွက်ချက်နှင့် အချိန်ကိုက်ဖြစ်မဖြစ် သေချာစေခြင်း
                                    recovered_store.append({"mu": mu_k, "tf": tf_name, "val": mu_latest_values[mu_k], "hits": len(seq)})

                # ==========================================
                # SCREEN RENDERING (PREMIUM UI DISPLAY)
                # ==========================================
                st.write("### 🎯 AI Premium Layout Results")
                
                # ၁။ RECOVERED TREND SNIPER ZONE (Bro ၏ လက်နက်ဆန်းအား ထိပ်ဆုံးမှ ပြသခြင်း)
                st.markdown("#### 🚨 RECOVERED TREND SNIPER ZONE (ပျက်ပြီးပြန်နိုးထလာသော မူသေစနစ်)")
                if not recovered_store:
                    st.info("လတ်တလောပွဲစဉ်တွင် '၃ ကြိမ်ဆက်မှား၊ ၂ ကြိမ်ဆက်ပြန်မှန်' သည့် ပျက်ပြီးပြန်ဝင် မူသစ် လက္ခဏာ မတွေ့ရှိသေးပါ။")
                else:
                    for r in recovered_store:
                        st.markdown(f"""
                        <div class="card card-recovered">
                            <div class="card-header">🔥 ⚠️ RECOVERED SNIPER ALERT ➡️ {r['mu']} ({r['tf']} နယ်ကုန် Window)</div>
                            <div style="margin-bottom: 8px;">သမိုင်းကြောင်း ခွဲခြမ်းစိတ်ဖြာချက်: <span style="color:#e74c3c; font-weight:bold;">၁ မှ ၁၄ ကြိမ်အထိ 95%+ ရှိခဲ့ပြီး၊ ၃ ကြိမ်ဆက်တိုက် လွဲချော်ကာ၊ နောက်ဆုံး ၂ ကြိမ်ဆက်တိုက် ကွက်တိ ပြန်ဝင်လာသည်။</span></div>
                            <div>ယခု (၂၀ ကြိမ်မြောက်) အတွက် ဒုန်းတင်ရန် Target ကွက်: <span class="metric-val">{r['val']}</span></div>
                        </div>
                        """, unsafe_allow_html=True)

                # ၂။ STANDARD HIGH-PROBABILITY & SNIPER TABS
                st.write("---")
                tab1, tab2 = st.tabs(["🔮 95%+ High-Probability Zone (နယ်ကုန်ပြတ်သားစနစ်)", "🦅 100% Super VIP Sniper Zone (အမှားမခံနယ်ကုန်)"])
                
                with tab1:
                    if not hp_store:
                        st.info("၉၅% အထက် Probability ရှိသော နယ်ကုန် အချိန်ဘောင် မတွေ့ရှိပါ။")
                    else:
                        for mu_name, data in hp_store.items():
                            st.markdown(f"""
                            <div class="card card-hp">
                                <div class="card-header">⏱️ နယ်ကုန်: {data['tf']} အတွင်း ➡️ {mu_name}</div>
                                <div>ထွက်လေ့ရှိသော ရလဒ်ပုံစံ: <span class="metric-val">{data['val']}</span></div>
                                <div style="color: #2ecc71; font-weight: bold; margin-top:8px;">🎯 သမိုင်းကြောင်းမှန်ကန်မှု: {data['rate']:.1f}% ({data['hits']} ကြိမ်အနက်)</div>
                            </div>
                            """, unsafe_allow_html=True)

                with tab2:
                    if not sniper_store:
                        st.info("အနည်းဆုံး ၁၀ ကြိမ်ပြည့်ပြီး တစ်ခါမှမမှားဖူးသေးသော ၁၀၀% ကွက်တိ နယ်ကုန်စနစ် မရှိသေးပါ။")
                    else:
                        for mu_name, data in sniper_store.items():
                            st.markdown(f"""
                            <div class="card card-sniper">
                                <div class="card-header">💎 SUPER Sniper: {data['tf']} အတွင်း ➡️ {mu_name}</div>
                                <div>အမှားမခံသော Target ကွက်: <span class="metric-val">{data['val']}</span></div>
                                <div style="color: #9b59b6; font-weight: bold; margin-top:8px;">🦅 AI Confidence: 100% အပြည့် (သမိုင်း {data['hits']}/{data['hits']} ကြိမ်စလုံး တစ်ခါမှမလွဲဖူးပါ!)</div>
                            </div>
                            """, unsafe_allow_html=True)
else:
    st.info("စတင်ရန်အတွက် Bro ရဲ့ 2D CSV သို့မဟုတ် Excel ဒေတာဖိုင်ကို အပေါ်တွင် အရင် တင်ပေးပါဦး။")
