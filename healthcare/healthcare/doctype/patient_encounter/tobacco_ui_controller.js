
// ==========================================
// TOBACCO JSON UI CONTROLLER
// ==========================================

const TOBACCO_QUESTIONS = [
    { id: "q1", text: "1. Age of starting tobacco use", options: ["Under 18 years", "18-24 years", "Over 24 years"], score: { "Under 18 years": 3, "18-24 years": 2, "Over 24 years": 1 } },
    { id: "q2", text: "2. Years using tobacco", options: ["Less than 5 years", "5-10 years", "10-20 years", "More than 20 years"], score: { "Less than 5 years": 1, "5-10 years": 2, "10-20 years": 3, "More than 20 years": 4 } },
    { id: "q3", text: "3. Number of quit attempts", options: ["None", "Less than 3 times", "3-5 times", "More than 5 times"], score: { "None": 0, "Less than 3 times": 1, "3-5 times": 2, "More than 5 times": 3 } },
    { id: "q4", text: "4. Longest period of quitting", options: ["More than 1 year", "1 month – 1 year", "6-30 days", "Less than 5 days"], score: { "More than 1 year": 1, "1 month – 1 year": 2, "6-30 days": 3, "Less than 5 days": 4 } },
    { id: "q5", text: "5. Hard to quit?", options: ["Yes", "No"], score: { "Yes": 2, "No": 1 } },
    { id: "q6", text: "6. Doctor advised to quit?", options: ["Yes", "No"], score: { "Yes": 2, "No": 1 } },
    { id: "q7", text: "7. Previous reasons for relapse", options: ["Withdrawals or Cravings", "Medications didn't work", "No/Inadequate Guidance", "Self-initiated relapse", "Social Influence", "No relapse experience"], score: { "Withdrawals or Cravings": 4, "Medications didn't work": 4, "No/Inadequate Guidance": 3, "Self-initiated relapse": 2, "Social Influence": 1, "No relapse experience": 0 } },
    { id: "q8", text: "8. Alternating smoking/chewing", options: ["Using both at present", "Chewing to smoking", "Smoking to chewing", "Not Alternating"], score: { "Using both at present": 3, "Chewing to smoking": 2, "Smoking to chewing": 2, "Not Alternating": 0 } },
    { id: "q9", text: "9. Smoking qty/day", options: ["None", "Less than 10", "11-20", "21-30", "More than 31"], score: { "None": 0, "Less than 10": 0, "11-20": 1, "21-30": 2, "More than 31": 3 } },
    { id: "q10", text: "10. Chewing pouches/day", options: ["None", "Less than 1", "1-3", "More than 3"], score: { "None": 0, "Less than 1": 0, "1-3": 1, "More than 3": 2 } },
    { id: "q11", text: "11. Use after waking", options: ["Within 5 minutes", "6-30 minutes", "31-60 minutes", "More than 60 minutes"], score: { "Within 5 minutes": 3, "6-30 minutes": 2, "31-60 minutes": 1, "More than 60 minutes": 0 } },
    { id: "q12", text: "12. Severe craving?", options: ["Yes", "No"], score: { "Yes": 2, "No": 1 } },
    { id: "q13", text: "13. Hard to avoid where prohibited?", options: ["Yes", "No"], score: { "Yes": 2, "No": 1 } },
    { id: "q14", text: "14. Diff. concentrating?", options: ["Yes", "No"], score: { "Yes": 2, "No": 1 } },
    { id: "q15", text: "15. Reach without thinking?", options: ["Yes", "No"], score: { "Yes": 2, "No": 1 } }
];

frappe.ui.form.on("Patient Encounter", {
    refresh: function (frm) {
        if (frm.fields_dict['tobacco_fv_ui']) {
            render_tobacco_ui(frm);
            // Fetch history if new or empty computed
            if (!frm.doc.tobacco_fv_data) {
                fetch_tobacco_history_for_json(frm);
            }
        }
    }
});

function render_tobacco_ui(frm) {
    let wrapper = frm.fields_dict['tobacco_fv_ui'].wrapper;
    let data = {};
    try {
        data = JSON.parse(frm.doc.tobacco_fv_data || "{}");
    } catch (e) { console.log("JSON Parse error", e); }

    let html = `
	<style>
		.tobacco-table { width: 100%; border-collapse: collapse; margin-top: 10px; }
		.tobacco-table th { text-align: left; padding: 8px; background-color: var(--bg-light-gray); border-bottom: 2px solid var(--border-color); font-weight: 600; }
		.tobacco-table td { padding: 8px; border-bottom: 1px solid var(--border-color); vertical-align: middle; }
		.tobacco-select { width: 100%; padding: 4px; border: 1px solid var(--border-color); border-radius: 4px; background: var(--control-bg); color: var(--text-color); }
		.tobacco-score { font-weight: bold; text-align: center; }
		.tobacco-computed { font-size: 0.9em; color: var(--text-muted); }
	</style>
	<table class="tobacco-table">
		<thead>
			<tr>
				<th style="width: 40%">Criteria / Question</th>
				<th style="width: 30%">Response Options</th>
				<th style="width: 10%; text-align: center;">Score</th>
				<th style="width: 20%">Computed Value (History)</th>
			</tr>
		</thead>
		<tbody>
	`;

    TOBACCO_QUESTIONS.forEach(q => {
        let val = data[q.id]?.val || "";
        let score = data[q.id]?.score || 0;
        let computed = data[q.id]?.computed || "";

        let options_html = `<option value="">Select...</option>`;
        q.options.forEach(opt => {
            let selected = opt === val ? "selected" : "";
            options_html += `<option value="${opt}" ${selected}>${opt}</option>`;
        });

        html += `
		<tr id="row-${q.id}">
			<td>${q.text}</td>
			<td>
				<select class="tobacco-select" onchange="update_tobacco_json('${frm.doctype}', '${frm.docname}', '${q.id}', this.value)">
					${options_html}
				</select>
			</td>
			<td class="tobacco-score" id="score-${q.id}">${score}</td>
			<td class="tobacco-computed" id="computed-${q.id}">${computed}</td>
		</tr>
		`;
    });

    html += `</tbody></table>`;
    $(wrapper).html(html);
}

// Global function to handle change from HTML
window.update_tobacco_json = function (doctype, docname, q_id, value) {
    // Access frm via locals? No, safer to assume active form if single view
    // Or define this function inside refresh scope? No, needs global access for onchange string
    // But we can find the active form.
    let frm = cur_frm;
    if (!frm || frm.doc.name !== docname) return;

    let data = {};
    try {
        data = JSON.parse(frm.doc.tobacco_fv_data || "{}");
    } catch (e) { }

    // Find Score
    let q = TOBACCO_QUESTIONS.find(x => x.id === q_id);
    let score = 0;
    if (q && q.score[value] !== undefined) {
        score = q.score[value];
    }

    // Update Data
    if (!data[q_id]) data[q_id] = {};
    data[q_id].val = value;
    data[q_id].score = score;
    // computed preserved

    // Update UI Score
    $(`#score-${q_id}`).text(score);

    // Calc Total
    let total = 0;
    Object.values(data).forEach(item => total += (item.score || 0));

    frm.set_value("tobacco_fv_data", JSON.stringify(data)); // Save
    frm.set_value("tobacco_fv_total_score", total);

    // Addiction Level
    let level = "";
    let color = "";
    if (total <= 18) { level = "Mild Addiction"; color = "green"; }
    else if (total <= 30) { level = "Moderate Addiction"; color = "orange"; }
    else { level = "Severe Addiction"; color = "red"; }

    if (total > 0) {
        frm.set_value("tobacco_fv_addiction_level", `<div style="background-color: ${color}; color: white; padding: 5px 10px; border-radius: 4px; text-align: center; font-weight: bold;">${level}</div>`);
    } else {
        frm.set_value("tobacco_fv_addiction_level", "");
    }
};

function fetch_tobacco_history_for_json(frm) {
    if (!frm.doc.patient) return;

    frappe.call({
        method: "frappe.client.get",
        args: { doctype: "Patient", name: frm.doc.patient },
        callback: function (r) {
            if (r.message) {
                let p = r.message;
                let smoking = p.custom_smoking_tobacco_history || [];
                let smokeless = p.custom_smokeless_tobacco_history || [];
                let data = {};

                // Same computing logic
                // 1. Min Age
                let min_age = 100;
                let found = false;
                [...smoking, ...smokeless].forEach(row => {
                    if (row.started_at_age && row.started_at_age < min_age) {
                        min_age = row.started_at_age;
                        found = true;
                    }
                });
                if (found) {
                    ensure_q(data, "q1");
                    data.q1.computed = min_age + " years";
                    // Auto Select
                    if (min_age < 18) set_val(data, "q1", "Under 18 years");
                    else if (min_age <= 24) set_val(data, "q1", "18-24 years");
                    else set_val(data, "q1", "Over 24 years");
                }

                // 2. Max Years
                let max_years = 0;
                let found_years = false;
                [...smoking, ...smokeless].forEach(row => {
                    if (row.used_for_years && row.used_for_years > max_years) {
                        max_years = row.used_for_years;
                        found_years = true;
                    }
                });
                if (found_years) {
                    ensure_q(data, "q2");
                    data.q2.computed = max_years + " years";
                    if (max_years < 5) set_val(data, "q2", "Less than 5 years");
                    else if (max_years <= 10) set_val(data, "q2", "5-10 years");
                    else if (max_years <= 20) set_val(data, "q2", "10-20 years");
                    else set_val(data, "q2", "More than 20 years");
                }

                // 3. Smoke Qty
                let smoke_qty = 0;
                smoking.forEach(row => {
                    if (row.quantity) {
                        let qty = parseFloat(row.quantity) || 0;
                        if (row.frequency == "Weekly") qty /= 7;
                        if (row.frequency == "Monthly") qty /= 30;
                        if (row.frequency == "Yearly") qty /= 365;
                        smoke_qty += qty;
                    }
                });
                smoke_qty = Math.round(smoke_qty * 10) / 10;
                if (smoke_qty > 0) {
                    ensure_q(data, "q9");
                    data.q9.computed = smoke_qty + " / day";
                    if (smoke_qty <= 10) set_val(data, "q9", "Less than 10");
                    else if (smoke_qty <= 20) set_val(data, "q9", "11-20");
                    else if (smoke_qty <= 30) set_val(data, "q9", "21-30");
                    else set_val(data, "q9", "More than 31");
                }

                // 4. Chew Qty
                let chew_qty = 0;
                smokeless.forEach(row => {
                    if (row.quantity) {
                        let qty = parseFloat(row.quantity) || 0;
                        if (row.frequency == "Weekly") qty /= 7;
                        if (row.frequency == "Monthly") qty /= 30;
                        if (row.frequency == "Yearly") qty /= 365;
                        chew_qty += qty;
                    }
                });
                chew_qty = Math.round(chew_qty * 10) / 10;
                if (chew_qty > 0) {
                    ensure_q(data, "q10");
                    data.q10.computed = chew_qty + " pouches / day";
                    if (chew_qty < 1) set_val(data, "q10", "Less than 1");
                    else if (chew_qty <= 3) set_val(data, "q10", "1-3");
                    else set_val(data, "q10", "More than 3");
                }

                // Save and Refresh UI
                frm.set_value("tobacco_fv_data", JSON.stringify(data));
                render_tobacco_ui(frm);

                // Trigger Score Calc via fake update? Or just recalc
                let total = 0;
                Object.values(data).forEach(item => total += (item.score || 0));
                frm.set_value("tobacco_fv_total_score", total);
                // (Addiction level logic duplicate... handled in update_tobacco_json. Called here if we want)
                // Re-use logic:
                let level = "";
                let color = "";
                if (total <= 18) { level = "Mild Addiction"; color = "green"; }
                else if (total <= 30) { level = "Moderate Addiction"; color = "orange"; }
                else { level = "Severe Addiction"; color = "red"; }
                if (total > 0) frm.set_value("tobacco_fv_addiction_level", `<div style="background: ${color}; color: white; padding: 5px;">${level}</div>`);
            }
        }
    });
}

function ensure_q(data, id) { if (!data[id]) data[id] = {}; }
function set_val(data, id, val) {
    data[id].val = val;
    // Calc score
    let q = TOBACCO_QUESTIONS.find(x => x.id === id);
    if (q && q.score[val] !== undefined) data[id].score = q.score[val];
}
