

# Hook: Trigger Vids synthesis on high-value closing event
if gross_amount > 5000: 
    trigger_vids_synthesis(tenant_id, 'closing_presentation')
