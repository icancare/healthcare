
// ==========================================
// TOBACCO LOGIC V3 (HTML Fields)
// ==========================================

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

                // Helper to set HTML content
                const set_html = (fieldname, text) => {
                    let html = `<div style='padding-top: 5px; color: var(--text-color); font-size: 13px;'>${text}</div>`;
                    // Use set_df_property to update 'options'
                    frm.set_df_property(fieldname, "options", html);
                    frm.refresh_field(fieldname);
                };

                // 1. Calculate Age of Starting
                let min_age = 100;
                let found_start = false;
                [...smoking, ...smokeless].forEach(row => {
                    if (row.started_at_age && row.started_at_age < min_age) {
                        min_age = row.started_at_age;
                        found_start = true;
                    }
                });

                if (found_start) {
                    set_html("tobacco_fv_q1_computed", min_age + " years");
                    // Auto-select
                    if (min_age < 18) frm.set_value("tobacco_fv_q1", "Under 18 years");
                    else if (min_age <= 24) frm.set_value("tobacco_fv_q1", "18-24 years");
                    else frm.set_value("tobacco_fv_q1", "Over 24 years");
                } else {
                    set_html("tobacco_fv_q1_computed", "Not found");
                }

                // 2. Calculate Years Using
                let max_years = 0;
                let found_years = false;
                [...smoking, ...smokeless].forEach(row => {
                    if (row.used_for_years && row.used_for_years > max_years) {
                        max_years = row.used_for_years;
                        found_years = true;
                    }
                });

                if (found_years) {
                    set_html("tobacco_fv_q2_computed", max_years + " years");
                    if (max_years < 5) frm.set_value("tobacco_fv_q2", "Less than 5 years");
                    else if (max_years <= 10) frm.set_value("tobacco_fv_q2", "5-10 years");
                    else if (max_years <= 20) frm.set_value("tobacco_fv_q2", "10-20 years");
                    else frm.set_value("tobacco_fv_q2", "More than 20 years");
                } else {
                    set_html("tobacco_fv_q2_computed", "Not found");
                }

                // 3. Smoking Qty sum
                let smoke_qty = 0;
                smoking.forEach(row => {
                    if (row.quantity) {
                        let qty = parseFloat(row.quantity) || 0;
                        if (row.frequency == "Weekly") qty = qty / 7;
                        if (row.frequency == "Monthly") qty = qty / 30;
                        if (row.frequency == "Yearly") qty = qty / 365;
                        smoke_qty += qty;
                    }
                });

                smoke_qty = Math.round(smoke_qty * 10) / 10;

                if (smoke_qty > 0) {
                    set_html("tobacco_fv_q9_computed", smoke_qty + " / day");
                    if (smoke_qty <= 10) frm.set_value("tobacco_fv_q9", "Less than 10");
                    else if (smoke_qty <= 20) frm.set_value("tobacco_fv_q9", "11-20");
                    else if (smoke_qty <= 30) frm.set_value("tobacco_fv_q9", "21-30");
                    else frm.set_value("tobacco_fv_q9", "More than 31");
                } else {
                    set_html("tobacco_fv_q9_computed", "0");
                    frm.set_value("tobacco_fv_q9", "None");
                }

                // 4. Smokeless Qty sum
                let chew_qty = 0;
                smokeless.forEach(row => {
                    if (row.quantity) {
                        let qty = parseFloat(row.quantity) || 0;
                        if (row.frequency == "Weekly") qty = qty / 7;
                        if (row.frequency == "Monthly") qty = qty / 30;
                        if (row.frequency == "Yearly") qty = qty / 365;
                        chew_qty += qty;
                    }
                });

                chew_qty = Math.round(chew_qty * 10) / 10;

                if (chew_qty > 0) {
                    set_html("tobacco_fv_q10_computed", chew_qty + " pouches / day");
                    if (chew_qty < 1) frm.set_value("tobacco_fv_q10", "Less than 1");
                    else if (chew_qty <= 3) frm.set_value("tobacco_fv_q10", "1-3");
                    else frm.set_value("tobacco_fv_q10", "More than 3");
                } else {
                    set_html("tobacco_fv_q10_computed", "0");
                    frm.set_value("tobacco_fv_q10", "None");
                }
            }
        }
    });
}
