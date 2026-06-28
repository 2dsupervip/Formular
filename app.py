import streamlit as st
import pandas as pd
import io
import itertools
import re
from collections import Counter

# ==========================================
# PAGE CONFIG & PREMIUM DARK-THEME STYLE
# ==========================================
st.set_page_config(page_title="2D AI Master V26 Pro", layout="wide", page_icon="🤖")

st.markdown("""
<style>
    .stApp { background-color: #0B031A; color: #E0D5FA; }
    .main-title { color: #A078FF; font-size: 40px; font-weight: bold; text-align: center; margin-bottom: 5px; text-shadow: 0 0 10px rgba(160,120,255,0.5); }
    .sub-title { color: #8F72D6; font-size: 16px; text-align: center; margin-bottom: 30px; }
    
    .card { background-color: #170E2B; padding: 20px; border-radius: 12px; box-shadow: 0 4px 15px rgba(0,0,0,0.3); margin-bottom: 15px; border: 1px solid #2D1B4E; }
    .card-top { border-left: 6px solid #f39c12; background-color: #2e1e05; }
    .card-sniper { border-left: 6px solid #e74c3c; background-color: #3b1111; }
    .card-regular { border-left: 6px solid #9b59b6; background-color: #201135; }
    
    .line-trigger { font-size: 18px; font-weight: bold; color: #E0D5FA; margin-bottom: 6px; display: block; }
    .line-formula { font-size: 22px; font-weight: bold; color: #FFD700; margin-bottom: 6px; display: block; }
    .line-history { font-size: 15px; color: #A294C7; display: block; }
    .line-advisor { font-size: 16px; color: #00FFCC; font-style: italic; margin-top: 10px; display: block; border-top: 1px dashed #3D2B5E; padding-top: 8px; }
    
    .badge-inline { padding: 2px 10px; border-radius: 6px; font-size: 14px; font-weight: bold; margin-left: 6px; margin-right: 6px; display: inline-block; vertical-align: middle; }
    .badge-inline-alert { background-color: #e74c3c; color: white; }
    .badge-inline-reg { background-color: #9b59b6; color: white; }
</style>
""", unsafe_allow_html=True)

st.markdown('<div class="main-title">🤖 THE PERFECT 2D AI MASTER (V26 PRO)</div>', unsafe_allow_html=True)
st.markdown('<div class="sub-title">Ultimate Dual-Mode Matrix Engine | Exact Step Bound & Sniper Notes</div>', unsafe_allow_html=True)

special_groups = {
    "ညီကို": {"01","10","12","21","23","32","34","43","45","54","56","65","67","76","78","87","89","98","90","09"},
    "ပါဝါ": {"05","50","16","61","27","72","38","83","49","94"},
    "နက္ခတ်": {"07","70","18","81","24","42","35","53","69","96"},
    "ထိုင်းပါဝါ": {"09","90","13","31","26","62","47","74","58","85"},
    "အပူး": {"00","11","22","33","44","55","66","77","88","99"},
    "ဆယ်ပြည့်": {"10","01","20","02","30","03","40","04","50","05","60","06","70","07","80","08","90","09"}
}

# ==========================================
# CORE LOGIC: FORMULA EXTRACTION & CHECKING
# ==========================================
def extract_formula_mapping(analysis_pool):
    if not analysis_pool: return {}
    all_singles = "".join(analysis_pool)
    all_heads = [d[0] for d in analysis_pool]
    all_tails = [d[1] for d in analysis_pool]
    all_breaks = [str((int(d[0]) + int(d[1])) % 10) for d in analysis_pool]
    
    c_singles = Counter(all_singles)
    top_single = c_singles.most_common(1)[0][0] if all_singles else ""
    top_oc = "".join([x[0] for x in c_singles.most_common(2)]) if len(c_singles) >= 2 else top_single
    top_key3 = "".join([x[0] for x in c_singles.most_common(3)]) if len(c_singles) >= 3 else top_oc
    top_k4 = "".join([x[0] for x in c_singles.most_common(4)]) if len(c_singles) >= 4 else top_key3
    
    # Upgraded Rule 5: 3 Heads + 3 to 5 Dynamic Attached Tails
    top_h3 = [x[0] for x in Counter(all_heads).most_common(3)]
    head_formula_str = "-"
    if top_h3:
        attached_tails = [d[1] for d in analysis_pool if d[0] in top_h3]
        tail_counts = Counter(attached_tails).most_common(5)
        best_tails = [x[0] for x in tail_counts]
        if len(best_tails) >= 4 and len(tail_counts) >= 4 and tail_counts[2][1] - tail_counts[-1][1] > 2:
            best_tails = best_tails[:4]
        head_formula_str = f"{''.join(top_h3)} ထိပ် / {','.join(best_tails)} ကပ်" if best_tails else "-"

    # Upgraded Rule 6: 3 Tails + 3 to 5 Dynamic Attached Heads
    top_t3 = [x[0] for x in Counter(all_tails).most_common(3)]
    tail_formula_str = "-"
    if top_t3:
        attached_heads = [d[0] for d in analysis_pool if d[1] in top_t3]
        head_counts = Counter(attached_heads).most_common(5)
        best_heads = [x[0] for x in head_counts]
        if len(best_heads) >= 4 and len(head_counts) >= 4 and head_counts[2][1] - head_counts[-1][1] > 2:
            best_heads = best_heads[:4]
        tail_formula_str = f"{''.join(top_t3)} ပိတ် / {','.join(best_heads)} ကပ်" if best_heads else "-"

    top_brk2 = [x[0] for x in Counter(all_breaks).most_common(2)]
    if len(top_brk2) == 1: top_brk2.append(str((int(top_brk2[0])+1)%10))
    brk_label = f"{top_brk2[0]},{top_brk2[1]}" if len(top_brk2) >= 2 else "-"
    
    e_sc = sum(1 for d in analysis_pool if top_single in d and int(d.replace(top_single,'',1) if d.replace(top_single,'',1) else top_single) % 2 == 0)
    o_sc = sum(1 for d in analysis_pool if top_single in d and int(d.replace(top_single,'',1) if d.replace(top_single,'',1) else top_single) % 2 != 0)
    kap_label = f'[{top_single}] "စုံ"ကပ်' if e_sc >= o_sc else (f'[{top_single}] "မ"ကပ်' if top_single else "-")
    
    best_gp = ""
    max_gp_c = 0
    for combo in itertools.combinations(special_groups.keys(), 2):
        c = sum(1 for d in analysis_pool if d in special_groups[combo[0]] or d in special_groups[combo[1]])
        if c > max_gp_c: 
            max_gp_c = c
            best_gp = f"{combo[0]}+{combo[1]}"
            
    kwat_kyin_label = f"{top_key3} ပါသော {brk_label} ဘရိတ်" if top_key3 and brk_label != "-" else "-"

    return {
        "လုံးဘိုင်": f"{top_single} လုံးဘိုင်" if top_single else "-", 
        "One Change": f"{top_oc} One Change" if top_oc else "-",
        "key": f"{top_key3} key" if top_key3 else "-", 
        "အပူးပါခွေ": f"{top_k4} အပူးပါခွေ" if top_k4 else "-",
        "ထိပ်စီးစနစ်သစ်": head_formula_str, 
        "နောက်ပိတ်စနစ်သစ်": tail_formula_str,
        "ဘရိတ်": f"{brk_label} ဘရိတ်" if brk_label != "-" else "-", 
        "စုံ/မ ကပ်": kap_label, 
        "အုပ်စုတွဲ": best_gp if best_gp else "-",
        "ကွက်ကျဉ်းစနစ်": kwat_kyin_label
    }

def is_draw_match_formula(d, mu_name, mu_val):
    if mu_val == "-" or not mu_val: return False
    d_break = str((int(d[0]) + int(d[1])) % 10)
    
    try:
        if mu_name == "လုံးဘိုင်":
            pure_num = mu_val.split()[0]
            if pure_num in d: return True
        elif mu_name == "One Change":
            pure_oc = mu_val.split()[0]
            if any(x in d for x in pure_oc): return True
        elif mu_name == "key":
            pure_key = mu_val.split()[0]
            if any(x in d for x in pure_key): return True
        elif mu_name == "အပူးပါခွေ":
            pure_k4 = mu_val.split()[0]
            if d[0] in pure_k4 and d[1] in pure_k4: return True
        elif mu_name == "ထိပ်စီးစနစ်သစ်":
            match = re.search(r'([0-9]+)\s*ထိပ်\s*/\s*([0-9,]+)\s*ကပ်', mu_val)
            if match:
                heads, tails = match.group(1), [t.strip() for t in match.group(2).split(',')]
                if d[0] in heads and d[1] in tails: return True
        elif mu_name == "နောက်ပိတ်စနစ်သစ်":
            match = re.search(r'([0-9]+)\s*ပိတ်\s*/\s*([0-9,]+)\s*ကပ်', mu_val)
            if match:
                tails, heads = match.group(1), [h.strip() for h in match.group(2).split(',')]
                if d[1] in tails and d[0] in heads: return True
        elif mu_name == "ဘရိတ်":
            pure_brk = mu_val.split()[0].split(',')
            if d_break in [b.strip() for b in pure_brk]: return True
        elif mu_name == "စုံ/မ ကပ်":
            match = re.search(r'\[(\d+)\]\s*"([^"]+)"ကပ်', mu_val)
            if match:
                b1 = match.group(1)
                is_even = "စုံ" in match.group(2)
                if b1 in d:
                    rem = d.replace(b1, '', 1)
                    rem_digit = int(rem if rem else b1)
                    if (is_even and rem_digit % 2 == 0) or (not is_even and rem_digit % 2 != 0): return True
        elif mu_name == "အုပ်စုတွဲ":
            gps = mu_val.split('+')
            for g in gps:
                if d in special_groups.get(g.strip(), set()): return True
        elif mu_name == "ကွက်ကျဉ်းစနစ်":
            match = re.search(r'^(\d+)\s*ပါသော\s*([\d,\s]+)\s*ဘရိတ်', mu_val)
            if match:
                pure_k = match.group(1)
                pure_b = [b.strip() for b in match.group(2).split(',')]
                if any(k in d for k in pure_k) and d_break in pure_b: return True
    except Exception:
        pass
    return False

def is_already_hit(mu_name, mu_val, start_idx, end_idx, full_draws_list):
    if start_idx >= len(full_draws_list): return False, ""
    check_draws = [d['draw'] for d in full_draws_list[start_idx : min(end_idx + 1, len(full_draws_list))]]
    if not check_draws: return False, ""
    for d in check_draws:
        if is_draw_match_formula(d, mu_name, mu_val):
            return True, d
    return False, ""

# ==========================================
# MASTER ROUTINE: DUAL MODE ENGINE
# ==========================================
def execute_analysis(target_hits, full_draws, requested_max_step, is_custom_tab=False, sel_session="AM+PM ပေါင်းချုပ်", custom_trigger="", mode="AI Trend"):
    formulas_out = []
    current_latest_idx = len(full_draws) - 1

    filtered_hits = target_hits
    total_count = len(filtered_hits)
    if total_count == 0: return formulas_out

    mu_keys_list = ["လုံးဘိုင်", "One Change", "key", "အပူးပါခွေ", "ထိပ်စီးစနစ်သစ်", "နောက်ပိတ်စနစ်သစ်", "ဘရိတ်", "စုံ/မ ကပ်", "အုပ်စုတွဲ", "ကွက်ကျဉ်းစနစ်"]

    # 1. Global mapping for Calendar Mode (Fixed Pattern)
    global_mapping = {}
    if mode == "Calendar":
        all_sub_draws = []
        for hit in filtered_hits:
            start_post = hit['index'] + 1
            end_post = min(hit['index'] + requested_max_step, len(full_draws) - 1)
            all_sub_draws.extend([d['draw'] for d in full_draws[start_post:end_post + 1]])
        global_mapping = extract_formula_mapping(all_sub_draws)

    # 2. UI Mapping for AI Trend Mode (Current UI display based on the most recent hit's pre-history)
    current_recent_hit = filtered_hits[-1]['index']
    current_pool = [d['draw'] for d in full_draws[max(0, current_recent_hit - 50) : current_recent_hit]]
    ui_trend_prediction_mapping = extract_formula_mapping(current_pool)

    for mu_k in mu_keys_list:
        # The formula to display on UI
        ui_val = global_mapping.get(mu_k, "") if mode == "Calendar" else ui_trend_prediction_mapping.get(mu_k, "")
        if not ui_val or ui_val == "-": continue

        hit_steps_across_history = []
        actual_hit_combinations = []

        # Analyze historical accuracy strictly matching the algorithm
        for hit in filtered_hits:
            hit_idx = hit['index']
            
            # For AI Trend, evaluate historical success using its OWN dynamic local 50-draw pre-history for that hit point
            if mode == "Calendar":
                test_val = global_mapping.get(mu_k, "")
            else:
                local_pool = [d['draw'] for d in full_draws[max(0, hit_idx - 50) : hit_idx]]
                test_val = extract_formula_mapping(local_pool).get(mu_k, "")

            if not test_val or test_val == "-":
                hit_steps_across_history.append(999)
                continue

            found_hit_step = None
            # Absolute bounds lock Check
            for step_check in range(1, requested_max_step + 1):
                t_idx = hit_idx + step_check
                if t_idx >= len(full_draws): break
                
                is_hit, matched_draw = is_already_hit(mu_k, test_val, t_idx, t_idx, full_draws)
                if is_hit:
                    # Target Session Filter for Custom Tab
                    if is_custom_tab and sel_session != "AM+PM ပေါင်းချုပ်" and "သီးသန့်" in sel_session:
                        req_time_str = "AM" if "AM" in sel_session else "PM"
                        if full_draws[t_idx]['time'] != req_time_str:
                            continue 
                    found_hit_step = step_check
                    actual_hit_combinations.append(matched_draw)
                    break
            
            hit_steps_across_history.append(found_hit_step if found_hit_step is not None else 999)

        valid_spans = [s for s in hit_steps_across_history if s <= requested_max_step]
        if not valid_spans: continue
        
        max_required_span = max(valid_spans)
        successful_hits_within_max_span = sum(1 for s in hit_steps_across_history if s <= max_required_span)
        rate = (successful_hits_within_max_span / total_count) * 100

        # Strict Guards
        if rate < 90.0 or total_count < 10: continue

        # Deadline Flag
        is_deadline_flag = False
        last_hit_global_idx = filtered_hits[-1]['index']
        elapsed_draws = current_latest_idx - last_hit_global_idx
        if (elapsed_draws + 1) == max_required_span:
            is_deadline_flag = True
        
        # Hide if already hit (Tab 1 specific)
        if not is_custom_tab:
            is_hit, _ = is_already_hit(mu_k, ui_val, last_hit_global_idx + 1, current_latest_idx, full_draws)
            if is_hit: continue

        # Sniper Note Generataion (Top 3/4 accurate digits)
        sniper_note = ""
        if actual_hit_combinations:
            top_combos = [x[0] for x in Counter(actual_hit_combinations).most_common(4)]
            sniper_note = f"💡 အဖြစ်နိုင်ဆုံး ၃/၄ ကွက်: {', '.join(top_combos)}"

        lbl_prefix = custom_trigger if is_custom_tab else (f"{filtered_hits[-1]['draw']} {filtered_hits[-1]['time']}" if filtered_hits else "")
        rate_str = "100%" if rate == 100.0 else f"{rate:.1f}%"
        
        formulas_out.append({
            "top": f"🔮 [{lbl_prefix}] ထွက်ပြီးလျှင်", 
            "formula": f"{ui_val} {rate_str}", 
            "bottom": f"မှန်ကန်မှု: ({total_count} ကြိမ်မှာ {successful_hits_within_max_span} ကြိမ်မှန်)", 
            "is_deadline": is_deadline_flag, 
            "advisor": sniper_note, 
            "max_span": max_required_span,
            "lbl": custom_trigger if is_custom_tab else lbl_prefix,
            "pure_val": ui_val
        })

    return formulas_out

def render_top_results_scoring(formulas_list, max_tf):
    scoring_pool = {}
    for f in formulas_list:
        key = f['formula']
        if key not in scoring_pool:
            scoring_pool[key] = {'score': 0, 'details': [], 'is_anchor': False}
        
        scoring_pool[key]['details'].append(f)
        
        if f['is_deadline']:
            scoring_pool[key]['is_anchor'] = True
            scoring_pool[key]['score'] += 100
        else:
            rem_steps = max_tf - f['max_span'] + 1
            scoring_pool[key]['score'] += rem_steps

    valid_top = {k: v for k, v in scoring_pool.items() if len(v['details']) >= 2 or v['is_anchor']}
    top_averages = sorted(valid_top.items(), key=lambda item: item[1]['score'], reverse=True)[:3]
    
    st.markdown("#### 🏆 TOP RESULTS (Sniper & Cover Anchors)")
    if top_averages:
        for idx, (b_val, b_data) in enumerate(top_averages, 1):
            icon = "🔥 Sniper Anchor (ရက်ချိန်းပြည့်)" if b_data['is_anchor'] else "🛡️ Top Cover (အကောင်းဆုံး အရန်)"
            with st.expander(f"🏆 Top {idx}: {b_val} [{icon}] - အမှတ်: {b_data['score']}", expanded=(idx==1)):
                st.markdown(f"<div style='color:#00FFCC; font-size:14px; margin-bottom:10px;'>💡 ဤမူကို အောက်ပါ ထောက်တိုင်များက ဘုံတူညီစွာ ညွှန်ပြနေပါသည်-</div>", unsafe_allow_html=True)
                for d_detail in b_data['details']:
                    badge_class = "badge-inline-alert" if d_detail['is_deadline'] else "badge-inline-reg"
                    deadline_tag = f"<span class='badge-inline {badge_class}'>⚠️ ယခုပွဲ ရက်ချိန်းပြည့်</span>" if d_detail['is_deadline'] else f"<span class='badge-inline {badge_class}'>{d_detail['max_span']} ပွဲအတွင်း</span>"
                    st.markdown(f"""
                    <div class="card card-top" style="padding:10px; margin-bottom:10px;">
                        <span style="font-size:16px; font-weight:bold; color:#E0D5FA;">{d_detail['top']} {deadline_tag}</span>
                        <span style="font-size:13px; color:#A294C7; display:block; margin-top:5px;">{d_detail['advisor']}</span>
                    </div>
                    """, unsafe_allow_html=True)
    else:
        st.markdown("<div style='font-size:15px; font-weight:bold; color:#A294C7; padding:10px;'>ခိုင်မာသော ဘုံတူညီမှု ရလဒ်မရှိပါ (အနည်းဆုံး တိုက်ဆိုင်မှု ၂ ခု လိုအပ်ပါသည်)</div>", unsafe_allow_html=True)
    st.write("---")

def render_grouped_ui(formulas_list, max_tf):
    if not formulas_list:
        st.info("မထွက်သေးဘဲ ကျန်ရှိနေသော ၉၀% အထက် ရက်ချိန်းနယ်ကုန် မူလက်ကျန် လက္ခဏာ မတွေ့ရှိပါ။")
        return

    # Deduplicate matching cards across different sources to keep UI clean
    unique_formulas = []
    seen = set()
    for f in formulas_list:
        uid = f"{f['lbl']}_{f['formula']}_{f['max_span']}"
        if uid not in seen:
            seen.add(uid)
            unique_formulas.append(f)

    # UI Separation: Deadline Group vs Regular Groups
    deadlines = [f for f in unique_formulas if f['is_deadline']]
    regulars = [f for f in unique_formulas if not f['is_deadline']]
    
    st.markdown("#### 📋 အသေးစိတ်အချက်အလက် (Window အလိုက် ခေါက်သိမ်းစနစ်)")
    
    # 1. The Deadline Group (Top Priority)
    if deadlines:
        with st.expander("🔥 ယခုပွဲ ရက်ချိန်းပြည့် မူများ (DEADLINE ALERTS)", expanded=True):
            for d_card in sorted(deadlines, key=lambda x: x['max_span']):
                st.markdown(f"""
                <div class="card card-sniper">
                    <span class="line-trigger">{d_card['top']} <span class='badge-inline badge-inline-alert'>⚠️ ယခုပွဲ ရက်ချိန်းပြည့် ({d_card['max_span']} ပွဲ)</span></span>
                    <span class="line-formula">{d_card['formula']}</span>
                    <span class="line-history">{d_card['bottom']}</span>
                    <span class="line-advisor">{d_card['advisor']}</span>
                </div>
                """, unsafe_allow_html=True)
    
    # 2. The Regular Groups (By step bounds)
    span_groups = {}
    for f in regulars:
        span_groups.setdefault(f['max_span'], []).append(f)
        
    for step_key in range(1, max_tf + 1):
        if step_key not in span_groups: continue
        with st.expander(f"🔽 {step_key} ပွဲအတွင်း မူများ", expanded=(len(deadlines) == 0 and step_key == min(span_groups.keys()))):
            for d_card in span_groups[step_key]:
                st.markdown(f"""
                <div class="card card-regular">
                    <span class="line-trigger">{d_card['top']} <span class='badge-inline badge-inline-reg'>{step_key} ပွဲအတွင်း</span></span>
                    <span class="line-formula">{d_card['formula']}</span>
                    <span class="line-history">{d_card['bottom']}</span>
                    <span class="line-advisor">{d_card['advisor']}</span>
                </div>
                """, unsafe_allow_html=True)

# ==========================================
# FILE UPLOAD & PRE-PROCESSING
# ==========================================
uploaded_file = st.file_uploader("Bro ရဲ့ 2D CSV သို့မဟုတ် Excel ဖိုင်ကို ရွေးချယ်တင်ပေးပါ...", type=['csv', 'xlsx', 'xls'])

if uploaded_file:
    df = pd.read_csv(uploaded_file) if uploaded_file.name.endswith('.csv') else pd.read_excel(uploaded_file)
    df.columns = df.columns.str.strip().str.lower()
    
    if not all(col in df.columns for col in ['year', 'day', 'am1', 'am2', 'pm1', 'pm2']):
        st.error("⚠️ Phineထဲတွင် လိုအပ်သော ကော်လံများ (year, day, am1, am2, pm1, pm2) မပြည့်စုံပါ!")
    else:
        for col in ['year', 'am1', 'am2', 'pm1', 'pm2']:
            df[col] = pd.to_numeric(df[col], errors='coerce')
        df = df.dropna(subset=['year', 'day']).reset_index(drop=True)
        df['day'] = df['day'].astype(str).str.strip().str.capitalize()

        full_draws = []
        for idx, row in df.iterrows():
            if pd.notna(row['am1']) and pd.notna(row['am2']):
                full_draws.append({'draw': f"{int(row['am1'])}{int(row['am2'])}", 'time': 'AM', 'day': row['day'], 'year': int(row['year']), 'row_idx': idx})
            if pd.notna(row['pm1']) and pd.notna(row['pm2']):
                full_draws.append({'draw': f"{int(row['pm1'])}{int(row['pm2'])}", 'time': 'PM', 'day': row['day'], 'year': int(row['year']), 'row_idx': idx})

        for i, d in enumerate(full_draws): d['index'] = i

        last_recorded_draw = full_draws[-1]
        days_cycle = ["Mon", "Tue", "Wed", "Thur", "Fri"]
        
        if last_recorded_draw['time'] == 'AM':
            target_day_name = last_recorded_draw['day']
            target_time_name = "PM"
        else:
            curr_idx = days_cycle.index(last_recorded_draw['day']) if last_recorded_draw['day'] in days_cycle else 0
            target_day_name = days_cycle[(curr_idx + 1) % 5]
            target_time_name = "AM"
            
        st.success(f"🔮 ဒေတာပွဲစဉ်ပေါင်း {len(full_draws)} ခု ဖတ်ပြီးပါပြီ။ [{target_day_name} {target_time_name}] အတွက် တွက်ချက်မည်ဖြစ်ပါသည်။")
        st.write("---")

        tab_live, tab_custom = st.tabs(["⚡ တွက်ချက်မည် (ယခုပွဲစဉ်)", "🔍 2D Formulas (Custom)"])

        # ------------------------------------------
        # TAB 1: AUTOMATED ENGINE TRACKER
        # ------------------------------------------
        with tab_live:
            c1_tf, c2_md = st.columns([1, 2])
            with c1_tf:
                input_box_val = st.text_input("⏳ ပွဲစဉ်အရေအတွက် (Default: 10):", value="10", key="live_input")
                live_max_tf = int(input_box_val.strip()) if input_box_val.strip().isdigit() else 10
            with c2_md:
                st.markdown("##### 🧠 တွက်ချက်မှုစနစ် (Mode)")
                live_mode = st.radio("", ["AI Trend (ရှေ့သမိုင်း ၅၀ အထိုင်)", "Calendar (Fixed Pattern)"], horizontal=True, key="live_mode")
                live_session_target = f"{target_time_name} သီးသန့်"

            if st.button("ယခုပွဲအတွက် Auto ရှာဖွေမည် ⚡", key="btn_auto"):
                current_end_idx = len(full_draws) - 1
                master_formulas = []
                
                # Fetch exact matching bounds from recent history
                for step in range(1, live_max_tf + 1):
                    target_past_idx = current_end_idx - step + 1
                    if target_past_idx < 0: continue
                    
                    past_obj = full_draws[target_past_idx]
                    past_val = past_obj['draw']
                    past_time = past_obj['time']
                    
                    condition_pools = [
                        {"hits": [d for d in full_draws[:target_past_idx+1] if d['draw'] == past_val and d['time'] == past_time], "lbl": f"{past_val} {past_time} စစ်စစ်"},
                        {"hits": [d for d in full_draws[:target_past_idx+1] if d['draw'] == past_val], "lbl": f"{past_val} ပေါင်းချုပ်"}
                    ]
                    
                    for pool in condition_pools:
                        if not pool['hits']: continue
                        res = execute_analysis(pool['hits'], full_draws, live_max_tf, is_custom_tab=False, sel_session=live_session_target, mode="Calendar" if "Calendar" in live_mode else "AI Trend")
                        for r in res: 
                            r['lbl'] = pool['lbl']
                            master_formulas.append(r)

                st.write("---")
                render_top_results_scoring(master_formulas, live_max_tf)
                render_grouped_ui(master_formulas, live_max_tf)

        # ------------------------------------------
        # TAB 2: CLEAN CUSTOM FORMULARS ENGINE 
        # ------------------------------------------
        with tab_custom:
            st.markdown("##### 🧠 တွက်ချက်မှုစနစ် (Mode) ရွေးချယ်ရန်")
            custom_mode = st.radio("", ["AI Trend (ရှေ့သမိုင်း ၅၀ အထိုင်)", "Calendar (Fixed Pattern)"], horizontal=True, key="custom_mode")
            st.write("---")
            
            c1, c2, c3 = st.columns(3)
            with c1:
                trigger_day = st.selectbox("📆 Trigger Day:", ["All", "Mon", "Tue", "Wed", "Thur", "Fri"], index=0)
                trigger_num = st.text_input("🔍 ရှာလိုသောဂဏန်း ရိုက်ထည့်ပါ:", value="01", max_chars=7)
            with c2:
                if trigger_day != "All":
                    st.markdown("<span style='color:#00FFCC; font-size:13px;'>ℹ️ Day စနစ်သုံးထားသဖြင့် အကြိမ်ရေပြည့်မီစေရန် R-စနစ် နှင့် AM+PM ပေါင်းချုပ် စနစ်ကို Backend က Auto Lock ချပေးထားပါသည်။</span>", unsafe_allow_html=True)
                    target_session_custom = "AM+PM ပေါင်းချုပ်"
                else:
                    target_session_custom = st.selectbox("⏱️ Target ပွဲစဉ် အခြေအနေ ရွေးရန်:", ["AM+PM ပေါင်းချုပ်", "AM သီးသန့်", "PM သီးသန့်"], index=2)
            with c3:
                custom_max_tf = st.number_input("⏳ စစ်ဆေးမည့် ပွဲစဉ်အရေအတွက်", min_value=1, max_value=25, value=16, key="custom_input_tf")

            if st.button("ရှာဖွေမည် 🚀", key="btn_custom"):
                target_hits = []
                clean_trigger = trigger_num.strip().upper()
                is_composite = "+" in clean_trigger or "R" in clean_trigger or (trigger_day != "All")
                
                digits_found = re.findall(r'\d+', clean_trigger)
                
                if digits_found:
                    primary_digit = digits_found[0]
                    
                    if trigger_day == "All":
                        if is_composite:
                            secondary_digit = digits_found[1] if len(digits_found) > 1 else primary_digit[::-1]
                            target_hits = [d for d in full_draws if d['draw'] == primary_digit or d['draw'] == secondary_digit]
                        else:
                            if target_session_custom != "AM+PM ပေါင်းချုပ်" and "သီးသန့်" in target_session_custom:
                                req_time_init = "AM" if "AM" in target_session_custom else "PM"
                                target_hits = [d for d in full_draws if d['draw'] == primary_digit and d['time'] == req_time_init]
                            else:
                                target_hits = [d for d in full_draws if d['draw'] == primary_digit]
                    else:
                        secondary_digit = digits_found[1] if len(digits_found) > 1 else primary_digit[::-1]
                        matched_weeks = {d['row_idx'] for d in full_draws if d['day'] == trigger_day and (d['draw'] == primary_digit or d['draw'] == secondary_digit)}
                        for d in full_draws:
                            if d['row_idx'] in matched_weeks:
                                target_hits.append(d)
                
                if trigger_day == "All" and target_session_custom != "AM+PM ပေါင်းချုပ်" and len(target_hits) > 0:
                    req_time_filter = "AM" if "AM" in target_session_custom else "PM"
                    target_hits = [h for h in target_hits if h['time'] == req_time_filter]

                r_val = "R" if (trigger_day != "All" and "R" not in trigger_num) else ""
                d_val = trigger_day if trigger_day != "All" else ""
                t_time_label = "PM" if target_session_custom == "PM သီးသန့်" else "AM" if target_session_custom == "AM သီးသန့်" else ""
                
                lbl_prefix_custom = f"{trigger_num}{r_val} {d_val} {t_time_label}".strip()

                if not target_hits:
                    st.error("⚠️ သတ်မှတ်ချက်များနှင့် ကိုက်ညီသော သမိုင်းကြောင်းမှတ်တမ်း မရှိပါ Bro!")
                else:
                    st.write("---")
                    master_step_res = execute_analysis(
                        target_hits, full_draws, custom_max_tf, 
                        is_custom_tab=True, sel_session=target_session_custom, 
                        custom_trigger=lbl_prefix_custom,
                        mode="Calendar" if "Calendar" in custom_mode else "AI Trend"
                    )
                    render_grouped_ui(master_step_res, custom_max_tf)

else:
    st.info("စတင်ရန်အတွက် Bro ရဲ့ 2D CSV သို့မဟုတ် Excel ဒေတာဖိုင်ကို အပေါ်တွင် အရင် တင်ပေးပါဦး။")
