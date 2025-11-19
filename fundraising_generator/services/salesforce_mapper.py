"""
Salesforce Non-Profit Cloud column name mapper.
Maps internal column names to Salesforce NPC format: object_name::field_name
"""

# Mapping for Contact object fields
CONTACT_FIELD_MAPPING = {
    'contact_id': 'Contact::Id',
    'salutation': 'Contact::Salutation',
    'gender': 'Contact::Gender__c',
    'first_name': 'Contact::FirstName',
    'last_name': 'Contact::LastName',
    'phone': 'Contact::Phone',
    'address_1': 'Contact::MailingStreet',
    'address_2': 'Contact::MailingStreet2__c',
    'zip_code': 'Contact::MailingPostalCode',
    'city': 'Contact::MailingCity',
    'country': 'Contact::MailingCountry',
    'job': 'Contact::Title',
    'origin_decile': 'Contact::Wealth_Decile__c',
    'Creation_date': 'Contact::CreatedDate',
    'Creation_year': 'Contact::Created_Year__c',
    'longevity_years': 'Contact::Donor_Tenure_Years__c',
    'job_category': 'Contact::Job_Category__c',
    'wealth_category': 'Contact::Wealth_Category__c',
    'longevity_category': 'Contact::Longevity_Category__c',
    'combined_category': 'Contact::Donor_Segment__c',
}

# Mapping for Gift Transaction summary fields (rollup/summary fields)
GIFT_SUMMARY_FIELD_MAPPING = {
    'nb_donations': 'Gift_Transaction__c::Total_Gifts__c',
    'total_donated': 'Gift_Transaction__c::Total_Amount__c',
    'avg_donation': 'Gift_Transaction__c::Average_Gift_Amount__c',
    'first_donation': 'Gift_Transaction__c::First_Gift_Date__c',
    'primary_channel': 'Gift_Transaction__c::Primary_Channel__c',
    'is_regular': 'Gift_Transaction__c::Is_Regular_Donor__c',
}

# Mapping for Gift Transaction (individual transaction) fields
GIFT_TRANSACTION_FIELD_MAPPING = {
    'date': 'Gift_Transaction__c::Transaction_Date__c',
    'campaign_start': 'Campaign::StartDate',
    'campaign_end': 'Campaign::EndDate',
    'channel': 'Gift_Transaction__c::Channel__c',
    'campaign_name': 'Campaign::Name',
    'campaign_type': 'Campaign::Type',
    'donation_amount': 'Gift_Transaction__c::Amount__c',
    'cost': 'Campaign::Cost_Per_Contact__c',
    'reactivity': 'Campaign::Response_Rate__c',
    'contact_id': 'Contact::Id',
    'payment_method': 'Gift_Transaction__c::Payment_Method__c',
    'amount_decile': 'Gift_Transaction__c::Amount_Decile__c',
}

# Additional fields that may appear in analysis data
ANALYSIS_ADDITIONAL_MAPPING = {
    'channel_type': 'Gift_Transaction__c::Channel_Type__c',
}

# Combined mapping for analysis data (Contact + Gift Summary + Additional)
ANALYSIS_FIELD_MAPPING = {
    **CONTACT_FIELD_MAPPING,
    **GIFT_SUMMARY_FIELD_MAPPING,
    **ANALYSIS_ADDITIONAL_MAPPING,
}

def map_dataframe_columns(df, mapping_dict):
    """
    Rename DataFrame columns according to Salesforce NPC mapping.
    
    Args:
        df: pandas DataFrame
        mapping_dict: Dictionary mapping old column names to new Salesforce format names
    
    Returns:
        DataFrame with renamed columns
    """
    # Create rename dictionary with only columns that exist in the DataFrame
    rename_dict = {old: new for old, new in mapping_dict.items() if old in df.columns}
    
    # Rename columns
    df_renamed = df.rename(columns=rename_dict)
    
    return df_renamed

def get_salesforce_column_mapping(data_type='analysis'):
    """
    Get the appropriate column mapping based on data type.
    
    Args:
        data_type: Type of data - 'contacts', 'transactions', 'analysis', or 'gift_summary'
    
    Returns:
        Dictionary mapping internal column names to Salesforce NPC format
    """
    mappings = {
        'contacts': CONTACT_FIELD_MAPPING,
        'transactions': GIFT_TRANSACTION_FIELD_MAPPING,
        'analysis': ANALYSIS_FIELD_MAPPING,
        'gift_summary': GIFT_SUMMARY_FIELD_MAPPING,
    }
    
    return mappings.get(data_type, ANALYSIS_FIELD_MAPPING)

def export_to_salesforce_format(df, data_type='analysis', include_original=False):
    """
    Export DataFrame with Salesforce NPC column naming.
    
    Args:
        df: pandas DataFrame to export
        data_type: Type of data - 'contacts', 'transactions', 'analysis', or 'gift_summary'
        include_original: If True, keep both original and Salesforce columns
    
    Returns:
        DataFrame with Salesforce-formatted column names
    """
    mapping = get_salesforce_column_mapping(data_type)
    
    if include_original:
        # Add Salesforce columns alongside original
        for old_col, new_col in mapping.items():
            if old_col in df.columns:
                df[new_col] = df[old_col]
        return df
    else:
        # Replace column names with Salesforce format
        return map_dataframe_columns(df, mapping)

