# Configuration Guide

## YAML Configuration File Structure

### Global Settings

| Parameter | Type | Description | Default |
|-----------|------|-------------|----------|
| YEARS | integer | Number of years to generate | 10 |
| FIRST_YEAR | integer | Starting year for data generation | 2014 |
| INITIAL_DONOR_DATABASE_SIZE | integer | Initial number of donors | 10000 |
| GLOBAL_CHURN_RATE | float | Average donor churn rate | 0.99 |
| LOCALISATION | string | Locale for generating realistic data | 'en_GB' |
| GDPR_PROOF | boolean | Whether to follow GDPR restrictions | True |

### Channel Configuration

Each channel can have the following settings:

```yaml
CHANNELS:
  ChannelName:
    distribution: string  # "regular", "exponential", "inverted_exponential"
    duration: integer     # Campaign duration in days
    initial_nb: integer   # Initial number of contacts
    campaigns:
      prospecting:
        nb: integer                 # Number of campaigns
        max_reach_contact: integer  # Maximum contacts to reach
        transformation_rate: float  # Conversion rate
        avg_donation: float         # Average donation amount
        std_deviation: float        # Standard deviation of donations
      retention:
        # Same parameters as prospecting
        cross_sell:
          - [ChannelName, percentage]
    target:
      ses_wealth_decile: [min, max]  # Target wealth deciles
    payment:
      PaymentMethod: percentage    # Payment method distribution
    cost_per_reach: float         # Cost per contact reached
```

### Campaign Themes
```yaml
CAMPAIGN_THEMES:
  - ["Theme Name", probability]  # List of themes with weights
```

### Demographic Settings
```yaml
SALUTATIONS:
  - civility: string
    gender: string
    probability: float

WEALTHY_JOB: [string]    # List of high-income professions
NON_WEALTHY_JOB: [string] # List of standard professions
```

## Best Practices

1. Data Distribution
   - Use "regular" distribution for steady campaigns
   - Use "exponential" for campaigns with early peaks
   - Use "inverted_exponential" for campaigns that build momentum

2. Campaign Parameters
   - Set realistic transformation rates (typically 0.001 to 0.2)
   - Adjust avg_donation based on channel and target audience
   - Use cross_sell carefully to model realistic donor behavior

3. Cost Management
   - Set cost_per_reach based on real channel costs
   - Balance max_reach_contact with transformation_rate
   - Consider channel-specific payment method distributions
