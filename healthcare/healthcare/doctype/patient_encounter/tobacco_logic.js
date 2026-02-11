
// ==========================================
// TOBACCO CESSATION LOGIC
// ==========================================

frappe.ui.form.on("Patient Encounter", {
    refresh: function (frm) {
        // Existing refresh logic...
        if (frm.doc.exam_examination_template && frm.doc.exam_examination_template.includes("Quit Tobacco")) {
            // Ensure totals are calculated on load if fields are populated
            calculate_total_tobacco_score(frm);
        }
    },

    exam_examination_template: function (frm) {
        if (frm.doc.exam_examination_template && frm.doc.exam_examination_template.includes("Quit Tobacco First Visit")) {
            fetch_tobacco_history_data(frm);
        }
    },

    // Triggers for all 15 questions
    tobacco_fv_q1: function (frm) { update_tobacco_score(frm, 'tobacco_fv_q1'); },
    tobacco_fv_q2: function (frm) { update_tobacco_score(frm, 'tobacco_fv_q2'); },
    tobacco_fv_q3: function (frm) { update_tobacco_score(frm, 'tobacco_fv_q3'); },
    tobacco_fv_q4: function (frm) { update_tobacco_score(frm, 'tobacco_fv_q4'); },
    tobacco_fv_q5: function (frm) { update_tobacco_score(frm, 'tobacco_fv_q5'); },
    tobacco_fv_q6: function (frm) { update_tobacco_score(frm, 'tobacco_fv_q6'); },
    tobacco_fv_q7: function (frm) { update_tobacco_score(frm, 'tobacco_fv_q7'); },
    tobacco_fv_q8: function (frm) { update_tobacco_score(frm, 'tobacco_fv_q8'); },
    tobacco_fv_q9: function (frm) { update_tobacco_score(frm, 'tobacco_fv_q9'); },
    tobacco_fv_q10: function (frm) { update_tobacco_score(frm, 'tobacco_fv_q10'); },
    tobacco_fv_q11: function (frm) { update_tobacco_score(frm, 'tobacco_fv_q11'); },
    tobacco_fv_q12: function (frm) { update_tobacco_score(frm, 'tobacco_fv_q12'); },
    tobacco_fv_q13: function (frm) { update_tobacco_score(frm, 'tobacco_fv_q13'); },
    tobacco_fv_q14: function (frm) { update_tobacco_score(frm, 'tobacco_fv_q14'); },
    tobacco_fv_q15: function (frm) { update_tobacco_score(frm, 'tobacco_fv_q15'); }
});

function update_tobacco_score(frm, fieldname) {
    let value = frm.doc[fieldname];
    let score = 0;

    const scores = {
        'tobacco_fv_q1': { "Under 18 years": 3, "18-24 years": 2, "Over 24 years": 1 },
        'tobacco_fv_q2': { "Less than 5 years": 1, "5-10 years": 2, "10-20 years": 3, "More than 20 years": 4 },
        'tobacco_fv_q3': { "None": 0, "Less than 3 times": 1, "3-5 times": 2, "More than 5 times": 3 },
        'tobacco_fv_q4': { "More than 1 year": 1, "1 month – 1 year": 2, "6-30 days": 3, "Less than 5 days": 4 },
        'tobacco_fv_q5': { "Yes": 2, "No": 1 },
        'tobacco_fv_q6': { "Yes": 2, "No": 1 },
        'tobacco_fv_q7': {
            "Withdrawals or Cravings": 4, "Medications didn't work": 4,
            "No/Inadequate Guidance": 3, "Self-initiated relapse": 2,
            "Social Influence": 1, "No relapse experience": 0
        },
        'tobacco_fv_q8': { "Using both at present": 3, "Chewing to smoking": 2, "Smoking to chewing": 2, "Not Alternating": 0 },
        'tobacco_fv_q9': { "None": 0, "Less than 10": 0, "11-20": 1, "21-30": 2, "More than 31": 3 },
        'tobacco_fv_q10': { "None": 0, "Less than 1": 0, "1-3": 1, "More than 3": 2 },
        'tobacco_fv_q11': { "Within 5 minutes": 3, "6-30 minutes": 2, "31-60 minutes": 1, "More than 60 minutes": 0 },
        'tobacco_fv_q12': { "Yes": 2, "No": 1 },
        'tobacco_fv_q13': { "Yes": 2, "No": 1 },
        'tobacco_fv_q14': { "Yes": 2, "No": 1 },
        'tobacco_fv_q15': { "Yes": 2, "No": 1 }
    };

    if (scores[fieldname] && (value in scores[fieldname])) {
        score = scores[fieldname][value];
    }

    frm.set_value(fieldname + "_score", score);
    calculate_total_tobacco_score(frm);
}

function calculate_total_tobacco_score(frm) {
    let total = 0;
    // Sum Q1 to Q15 scores
    for (let i = 1; i <= 15; i++) {
        let score = frm.doc[`tobacco_fv_q${i}_score`] || 0;
        total += score;
    }
    frm.set_value("tobacco_fv_total_score", total);

    let level = "";
    let color = "";
    if (total <= 18) { level = "Mild Addiction"; color = "green"; }
    else if (total <= 30) { level = "Moderate Addiction"; color = "orange"; }
    else { level = "Severe Addiction"; color = "red"; }

    // Use HTML because Read Only Data field doesn't support color styling directly
    if (total > 0) {
        frm.set_value("tobacco_fv_addiction_level", `<div style="background-color: ${color}; color: white; padding: 5px 10px; border-radius: 4px; text-align: center; font-weight: bold;">${level}</div>`);
    } else {
        frm.set_value("tobacco_fv_addiction_level", "");
    }
}

function fetch_tobacco_history_data(frm) {
    if (!frm.doc.patient) return;

    frappe.call({
        method: "frappe.client.get",
        args: { doctype: "Patient", name: frm.doc.patient },
        callback: function (r) {
            if (r.message) {
                let p = r.message;
                let smoking = p.custom_smoking_tobacco_history || [];
                let smokeless = p.custom_smokeless_tobacco_history || [];

                // 1. Calculate Age of Starting (Earliest)
                let min_age = 100;
                let found = false;
                [...smoking, ...smokeless].forEach(row => {
                    if (row.started_at_age && row.started_at_age < min_age) {
                        min_age = row.started_at_age;
                        found = true;
                    }
                });

                if (found) {
                    if (min_age < 18) frm.set_value("tobacco_fv_q1", "Under 18 years");
                    else if (min_age <= 24) frm.set_value("tobacco_fv_q1", "18-24 years");
                    else frm.set_value("tobacco_fv_q1", "Over 24 years");
                }

                // 2. Calculate Years Using (Latest - Earliest)
                // Or simplify: Max(used_for_years)
                let max_years = 0;
                [...smoking, ...smokeless].forEach(row => {
                    if (row.used_for_years && row.used_for_years > max_years) {
                        max_years = row.used_for_years;
                    }
                });

                if (max_years > 0) {
                    if (max_years < 5) frm.set_value("tobacco_fv_q2", "Less than 5 years");
                    else if (max_years <= 10) frm.set_value("tobacco_fv_q2", "5-10 years");
                    else if (max_years <= 20) frm.set_value("tobacco_fv_q2", "10-20 years");
                    else frm.set_value("tobacco_fv_q2", "More than 20 years");
                }

                // 3. Smoking Qty sum
                let smoke_qty = 0;
                smoking.forEach(row => {
                    if (row.quantity) {
                        // Normalize frequency? Assuming Daily quantity field in history
                        let qty = row.quantity;
                        if (row.frequency == "Weekly") qty = qty / 7;
                        if (row.frequency == "Monthly") qty = qty / 30;
                        smoke_qty += qty;
                    }
                });

                if (smoke_qty > 0) {
                    if (smoke_qty <= 10) frm.set_value("tobacco_fv_q9", "Less than 10"); // Assuming <10 includes 1-9
                    else if (smoke_qty <= 20) frm.set_value("tobacco_fv_q9", "11-20");
                    else if (smoke_qty <= 30) frm.set_value("tobacco_fv_q9", "21-30");
                    else frm.set_value("tobacco_fv_q9", "More than 31");
                }

                // 4. Smokeless Qty sum
                let chew_qty = 0;
                smokeless.forEach(row => {
                    if (row.quantity) {
                        let qty = row.quantity;
                        if (row.frequency == "Weekly") qty = qty / 7;
                        if (row.frequency == "Monthly") qty = qty / 30;
                        chew_qty += qty;
                    }
                });

                if (chew_qty > 0) {
                    if (chew_qty < 1) frm.set_value("tobacco_fv_q10", "Less than 1");
                    else if (chew_qty <= 3) frm.set_value("tobacco_fv_q10", "1-3");
                    else frm.set_value("tobacco_fv_q10", "More than 3");
                }
            }
        }
    });
}
