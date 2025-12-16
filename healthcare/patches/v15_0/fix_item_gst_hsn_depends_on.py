import frappe


def execute():
    """
    Fix India Compliance gst_hsn_code field mandatory_depends_on error
    
    The India Compliance app sets mandatory_depends_on to:
    "eval:gst_settings.validate_hsn_code && doc.is_sales_item"
    
    But gst_settings is not available in the frontend context, causing:
    "Invalid depends_on expression" error when opening Item form.
    
    This patch removes the problematic mandatory_depends_on expression.
    """
    print("=" * 60)
    print("Fixing Item GST HSN Code depends_on Error")
    print("=" * 60)
    
    # Check if the custom field exists
    if not frappe.db.exists("Custom Field", "Item-gst_hsn_code"):
        print("  - Custom Field Item-gst_hsn_code not found, skipping")
        return
    
    # Get current value
    current_value = frappe.db.get_value(
        "Custom Field", 
        "Item-gst_hsn_code", 
        "mandatory_depends_on"
    )
    
    print(f"  Current mandatory_depends_on: {current_value}")
    
    if current_value and "gst_settings" in str(current_value):
        # Remove the problematic expression
        frappe.db.set_value(
            "Custom Field",
            "Item-gst_hsn_code",
            "mandatory_depends_on",
            "",
            update_modified=False
        )
        print("  ✓ Removed problematic mandatory_depends_on expression")
    else:
        print("  - No fix needed")
    
    frappe.db.commit()
    
    # Clear cache
    frappe.clear_cache(doctype="Item")
    
    print()
    print("=" * 60)
    print("✓ Item GST HSN Code Error Fixed!")
    print("=" * 60)


