import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import string
from faker import Faker
from scipy.spatial import KDTree
try:
    from dateutil.relativedelta import relativedelta
except ImportError:
    # Fallback if dateutil not available
    relativedelta = None
from .contact_manager import ContactManager

class FundraisingDataGenerator:
    def __init__(self, config):
        """Initialize the generator with configuration"""
        self.config = config
        print("      → Loading configuration...")
        import sys
        sys.stdout.flush()
        self.load_config()
        print("      → Initializing contact manager...")
        sys.stdout.flush()
        self.contact_manager = ContactManager(self.CHANNELS)
        print("      → Initializing Faker...")
        sys.stdout.flush()
        self.fake = Faker(self.LOCALISATION)
        print("      ✓ Generator ready")
        sys.stdout.flush()

    def load_config(self):
        """Load all variables from the config"""
        self.YEARS = self.config.get('YEARS', 10)
        self.FIRST_YEAR = self.config.get('FIRST_YEAR', 2014)
        self.INITIAL_DONOR_DATABASE_SIZE = self.config.get('INITIAL_DONOR_DATABASE_SIZE', 10000)
        self.GLOBAL_CHURN_RATE = self.config.get('GLOBAL_CHURN_RATE', 0.99)
        self.GLOBAL_REGULAR_DONOR_RATE = self.config.get('GLOBAL_REGULAR_DONOR_RATE', 0.08)
        self.CHANNELS = self.config.get('CHANNELS', {})
        self.CAMPAIGN_THEMES = self.config.get('CAMPAIGN_THEMES', [])
        self.CAMPAIGN_THEME_CONFIG = {}
        self.CAMPAIGN_THEME_CHOICES = []
        if isinstance(self.CAMPAIGN_THEMES, dict):
            self.CAMPAIGN_THEME_CONFIG = self.CAMPAIGN_THEMES
            self.CAMPAIGN_THEME_CHOICES = [
                (theme, data.get('weight', 1.0))
                for theme, data in self.CAMPAIGN_THEME_CONFIG.items()
            ]
        else:
            self.CAMPAIGN_THEME_CHOICES = self.CAMPAIGN_THEMES
        self.WHERE_POSSIBILITIES = self.config.get('WHERE_POSSIBILITIES', [])
        self.WHO_POSSIBILITIES = self.config.get('WHO_POSSIBILITIES', [])
        self.WHAT_POSSIBILITIES = self.config.get('WHAT_POSSIBILITIES', [])
        self.SALUTATIONS = self.config.get('SALUTATIONS', [])
        self.WEALTHY_JOB = self.config.get('WEALTHY_JOB', [])
        self.NON_WEALTHY_JOB = self.config.get('NON_WEALTHY_JOB', [])
        self.LOCALISATION = self.config.get('LOCALISATION', 'fr_FR')
        # Track regular donors to avoid duplicate monthly generation
        self.regular_donors = set()

    def select_by_probability(self, options):
        """Select an option based on the given probabilities"""
        choices, weights = zip(*options)
        total_weight = sum(weights)
        if total_weight != 1.0:
            weights = [w / total_weight for w in weights]
        return random.choices(choices, weights, k=1)[0]

    def _generate_campaign_metadata(self, channel_name, channel_data, campaign_type, campaign_info, current_year):
        """Generate metadata for a campaign"""
        code_source = {}
        
        # Select theme
        if self.CAMPAIGN_THEME_CHOICES:
            code_source['theme'] = self.select_by_probability(self.CAMPAIGN_THEME_CHOICES)
        else:
            code_source['theme'] = "General"
        
        # Select options for where, who, and what
        num_where_options = random.randint(1, 3)
        num_who_options = random.randint(1, 3)
        num_what_options = random.randint(1, 3)

        # Generate random start date and duration
        start_day = random.randint(1, 365)
        start_date = datetime(current_year, 1, 1) + timedelta(days=start_day)
        end_date = start_date + timedelta(days=channel_data['duration'])
        
        campaign_names = []
        if self.CAMPAIGN_THEME_CONFIG:
            campaign_names = self.CAMPAIGN_THEME_CONFIG.get(code_source['theme'], {}).get('campaign_names', [])
        
        if campaign_names:
            selected_campaign_name = random.choice(campaign_names)
        else:
            selected_campaign_name = code_source['theme']

        code_source.update({
            'start': start_date,
            'end': end_date,
            'transformation_rate': campaign_info.get('transformation_rate', 0.1),
            'avg_donation': campaign_info.get('avg_donation', 50),
            'std_deviation': campaign_info.get('std_deviation', 10),
            'name': f"{current_year}-{str(start_day).zfill(2)}_{channel_name}_{selected_campaign_name.replace(' ', '_')}"
        })
        
        return code_source

    def generate_transaction_dates(self, num_transactions, distribution, start_date, end_date):
        """Generate transaction dates based on distribution"""
        dates = []
        total_days = (end_date - start_date).days

        for _ in range(num_transactions):
            if distribution == "regular":
                random_day = random.randint(0, total_days)
            elif distribution == "inverted_exponential":
                random_day = total_days - int(random.expovariate(1.0 / (total_days // 2)))
            elif distribution == "exponential":
                random_day = int(random.expovariate(1.0 / (total_days // 2)))
            else:
                random_day = random.randint(0, total_days)
            
            random_day = max(0, min(random_day, total_days))
            dates.append(start_date + timedelta(days=random_day))
        
        return dates

    def _create_campaign_transactions(self, nb_reach, nb_sent, contact_ids, code_source, 
                                   channel_name, channel_data, campaign_type):
        """Create transactions for a campaign"""
        num_transactions = len(contact_ids)
        if num_transactions == 0:
            return pd.DataFrame()

        # Generate transaction dates
        transaction_dates = self.generate_transaction_dates(
            num_transactions, 
            channel_data['distribution'],
            code_source['start'],
            code_source['end']
        )

        # Create base transaction data
        transactions_data = {
            'date': transaction_dates,
            'campaign_start': code_source['start'],
            'campaign_end': code_source['end'],
            'channel': channel_name,
            'campaign_name': code_source['name'],
            'campaign_type': campaign_type,
            'donation_amount': [
                max(1, random.gauss(code_source['avg_donation'], code_source['std_deviation']))
                for _ in range(num_transactions)
            ],
            'cost': nb_reach * channel_data['cost_per_reach'] / num_transactions,
            'reactivity': nb_reach / num_transactions,
            'contact_id': contact_ids
        }

        # Add payment methods
        transactions_data['payment_method'] = [
            self.select_by_probability(list(channel_data['payment'].items()))
            for _ in range(num_transactions)
        ]

        # Create DataFrame
        transactions_campaign = pd.DataFrame(transactions_data)
        transactions_campaign['donation_amount'] = transactions_campaign['donation_amount'].round(2)
        transactions_campaign['cost'] = transactions_campaign['cost'].round(2)
        transactions_campaign['reactivity'] = transactions_campaign['reactivity'].round(2)
        
        # Calculate deciles
        transactions_campaign['amount_decile'] = pd.qcut(
            transactions_campaign['donation_amount'], 
            10, 
            labels=False, 
            duplicates='drop'
        ) + 1

        return transactions_campaign

    def _calculate_wealth_category(self, decile):
        """Calculate wealth category from decile"""
        if decile >= 8:
            return 'high'
        elif decile >= 5:
            return 'medium'
        else:
            return 'low'

    def _calculate_regular_donor_probability(self, contact_id, donation_date, amount_decile, channel_data):
        """Calculate probability that a donor becomes regular based on wealth + duration + channel"""
        # Base rate
        base_rate = self.GLOBAL_REGULAR_DONOR_RATE
        
        # Channel-specific rate
        channel_rate = channel_data.get('regular_donor_rate', 0.08)
        
        # Wealth multiplier
        wealth_category = self._calculate_wealth_category(amount_decile)
        wealth_multiplier = channel_data.get('regular_donor_wealth_multiplier', {}).get(wealth_category, 1.0)
        
        # Duration factor (based on how early in the period the donation occurs)
        # Earlier donations (longer tenure) have higher probability
        years_since_start = (donation_date.year - self.FIRST_YEAR) + (donation_date.timetuple().tm_yday / 365.25)
        max_years = self.YEARS
        duration_factor = min(1.0, (years_since_start / max(1, max_years * 0.6)))  # Normalize to 60% of period
        
        # Combined probability formula
        probability = base_rate * channel_rate * wealth_multiplier * (0.5 + 0.5 * duration_factor)
        
        # Cap at reasonable maximum (60% to allow for higher rates)
        probability = min(probability, 0.6)
        
        return probability

    def _generate_monthly_donations(self, contact_id, first_donation_date, channel_name, channel_data, 
                                   campaign_name, campaign_start, campaign_end):
        """Generate all monthly donations for a regular donor"""
        # Get monthly donation amount
        monthly_avg = channel_data.get('regular_donor_monthly_avg', 30)
        monthly_std = monthly_avg * 0.3  # 30% standard deviation
        
        # Start from the month after first donation (same day of month, or 1st if day > 28)
        if first_donation_date.day > 28:
            day_of_month = 1
        else:
            day_of_month = first_donation_date.day
        
        # Calculate next month
        if first_donation_date.month == 12:
            start_date = datetime(first_donation_date.year + 1, 1, day_of_month)
        else:
            start_date = datetime(first_donation_date.year, first_donation_date.month + 1, day_of_month)
        
        # End date: end of generation period
        end_date = datetime(self.FIRST_YEAR + self.YEARS, 12, 31)
        
        # Calculate number of months
        months_diff = (end_date.year - start_date.year) * 12 + (end_date.month - start_date.month)
        if end_date.day >= day_of_month:
            months_diff += 1
        
        if months_diff <= 0:
            return []
        
        # Pre-generate all dates efficiently
        dates = []
        current_date = start_date
        for _ in range(months_diff):
            if current_date > end_date:
                break
            dates.append(current_date)
            # Move to next month
            if current_date.month == 12:
                current_date = datetime(current_date.year + 1, 1, day_of_month)
            else:
                current_date = datetime(current_date.year, current_date.month + 1, day_of_month)
        
        # Pre-generate payment methods (more efficient)
        payment_methods_list = list(channel_data['payment'].items())
        
        # Generate all donations at once using list comprehensions (much faster)
        monthly_donations = [
            {
                'date': date,
                'campaign_start': campaign_start,
                'campaign_end': campaign_end,
                'channel': channel_name,
                'campaign_name': f"Monthly Recurring - {campaign_name}",
                'campaign_type': 'recurring',
                'donation_amount': round(max(1, random.gauss(monthly_avg, monthly_std)), 2),
                'cost': round(channel_data['cost_per_reach'] * 0.1, 2),
                'reactivity': 1.00,
                'contact_id': contact_id,
                'payment_method': self.select_by_probability(payment_methods_list)
            }
            for date in dates
        ]
        
        return monthly_donations

    def _create_campaign_transactions(self, nb_reach, nb_sent, contact_ids, code_source, 
                                   channel_name, channel_data, campaign_type):
        """Create transactions for a campaign"""
        num_transactions = len(contact_ids)
        if num_transactions == 0:
            return pd.DataFrame()

        # Generate transaction dates
        transaction_dates = self.generate_transaction_dates(
            num_transactions, 
            channel_data['distribution'],
            code_source['start'],
            code_source['end']
        )

        # Create base transaction data
        transactions_data = {
            'date': transaction_dates,
            'campaign_start': code_source['start'],
            'campaign_end': code_source['end'],
            'channel': channel_name,
            'campaign_name': code_source['name'],
            'campaign_type': campaign_type,
            'donation_amount': [
                max(1, random.gauss(code_source['avg_donation'], code_source['std_deviation']))
                for _ in range(num_transactions)
            ],
            'cost': nb_reach * channel_data['cost_per_reach'] / num_transactions,
            'reactivity': nb_reach / num_transactions,
            'contact_id': contact_ids
        }

        # Add payment methods
        transactions_data['payment_method'] = [
            self.select_by_probability(list(channel_data['payment'].items()))
            for _ in range(num_transactions)
        ]

        # Create DataFrame
        transactions_campaign = pd.DataFrame(transactions_data)
        
        # Calculate deciles
        transactions_campaign['amount_decile'] = pd.qcut(
            transactions_campaign['donation_amount'], 
            10, 
            labels=False, 
            duplicates='drop'
        ) + 1

        # Determine regular donors and generate monthly donations
        # Only check on first donation per contact
        monthly_transactions_list = []
        regular_donors_this_campaign = 0
        
        # Use itertuples for better performance
        for row in transactions_campaign.itertuples():
            contact_id = row.contact_id
            donation_date = row.date
            amount_decile = row.amount_decile
            # Update donation count
            current_count = self.contact_donation_counts.get(contact_id, 0) + 1
            self.contact_donation_counts[contact_id] = current_count
            
            # Skip if already a regular donor
            if contact_id in self.regular_donors:
                continue
            
            # Check if this is the first donation for this contact
            is_first_donation = contact_id not in self.contact_first_donations
            if is_first_donation:
                self.contact_first_donations[contact_id] = {
                    'date': donation_date,
                    'decile': amount_decile,
                    'channel': channel_name,
                    'campaign': code_source['name']
                }
            
            # Only determine regular status on first donation
            if is_first_donation:
                # Calculate probability of becoming regular donor
                probability = self._calculate_regular_donor_probability(
                    contact_id, donation_date, amount_decile, channel_data
                )
                
                # Determine if becomes regular donor
                if random.random() < probability:
                    self.regular_donors.add(contact_id)
                    regular_donors_this_campaign += 1
                    self.regular_donor_conversion_counts[contact_id] = current_count
                    
                    # Generate all monthly donations starting from month after first donation
                    monthly_donations = self._generate_monthly_donations(
                        contact_id,
                        donation_date,
                        channel_name,
                        channel_data,
                        code_source['name'],
                        code_source['start'],
                        code_source['end']
                    )
                    
                    if monthly_donations:
                        monthly_transactions_list.extend(monthly_donations)
        
        if regular_donors_this_campaign > 0:
            total_monthly = len(monthly_transactions_list)
            if total_monthly > 0:
                import sys
                print(f"         → Generated {regular_donors_this_campaign} regular donors with {total_monthly:,} monthly donations")
                sys.stdout.flush()
        
        # Add monthly donations to transactions
        if monthly_transactions_list:
            monthly_df = pd.DataFrame(monthly_transactions_list)
            # Calculate deciles for monthly donations
            monthly_df['amount_decile'] = pd.qcut(
                monthly_df['donation_amount'], 
                10, 
                labels=False, 
                duplicates='drop'
            ) + 1
            transactions_campaign = pd.concat([transactions_campaign, monthly_df], ignore_index=True)

        return transactions_campaign

    def _generate_contacts(self, transactions):
        """Generate contact information for all transactions"""
        import sys
        print("\n👥 Generating contacts from transactions...")
        sys.stdout.flush()
        # Group transactions by contact_id and get their maximum decile
        grouped_transactions = transactions.groupby('contact_id')['amount_decile'].max().reset_index()
        
        total_contacts = len(grouped_transactions)
        print(f"   → Preparing {total_contacts:,} contacts")
        sys.stdout.flush()

        transactions_dates = transactions[['contact_id', 'date']].groupby('contact_id')['date'].min()
        
        contacts_data = []
        sal_civilities = [sal['civility'] for sal in self.SALUTATIONS]
        sal_probabilities = [sal['probability'] for sal in self.SALUTATIONS]
        
        for idx, row in enumerate(grouped_transactions.itertuples(), 1):
            contact_id = row.contact_id
            max_decile = row.amount_decile
            
            # Generate basic contact info
            chosen_salutation = np.random.choice(sal_civilities, p=sal_probabilities)
            chosen_gender = next(sal['gender'] for sal in self.SALUTATIONS 
                                 if sal['civility'] == chosen_salutation)

            # Generate name based on gender
            if chosen_gender == "male":
                first_name = self.fake.first_name_male()
            elif chosen_gender == "female":
                first_name = self.fake.first_name_female()
            else:
                first_name = self.fake.first_name()

            # Assign job based on decile
            job = np.random.choice(self.WEALTHY_JOB if max_decile > 7 else self.NON_WEALTHY_JOB)

            # Find first transaction date (pre-computed for performance)
            first_transaction_date = transactions_dates[contact_id]

            # Create contact record
            contact_data = {
                'contact_id': contact_id,
                'salutation': chosen_salutation,
                'gender': chosen_gender,
                'first_name': first_name,
                'last_name': self.fake.last_name(),
                'phone': self.fake.phone_number(),
                'address_1': self.fake.street_address(),
                'address_2': self.fake.building_number() if random.random() > 0.5 else '',
                'zip_code': self.fake.postcode(),
                'city': self.fake.city(),
                'country': self.fake.country(),
                'job': job,
                'origin_decile': max_decile,
                'Creation_date': first_transaction_date,
                'Creation_year': first_transaction_date.year,
                'nb_donations_before_regular': self.regular_donor_conversion_counts.get(contact_id, 0)
            }
            
            contacts_data.append(contact_data)

            if idx % 5000 == 0 or idx == total_contacts:
                print(f"      → Generated {idx:,}/{total_contacts:,} contacts")
                sys.stdout.flush()

        print(f"   ✓ Contacts generation completed ({len(contacts_data):,} records)")
        sys.stdout.flush()
        return pd.DataFrame(contacts_data)

    def generate(self):
        """Generate fundraising dataset"""
        import sys
        print(f"\n🔄 Starting data generation for {self.YEARS} years ({self.FIRST_YEAR} to {self.FIRST_YEAR + self.YEARS - 1})...")
        sys.stdout.flush()
        transactions = pd.DataFrame()
        # Reset regular donors tracking for new generation
        self.regular_donors = set()
        # Track first donation per contact to determine regular status only once
        self.contact_first_donations = {}
        # Track donation counts per contact and conversion stats
        self.contact_donation_counts = {}
        self.regular_donor_conversion_counts = {}

        # Iterate through each year
        for year in range(self.YEARS):
            current_year = self.FIRST_YEAR + year
            print(f"\n📅 Processing year {current_year} ({year + 1}/{self.YEARS})...")
            sys.stdout.flush()
            
            # Generate transactions for each channel
            for channel_name, channel_data in self.CHANNELS.items():
                print(f"   → Generating transactions for channel: {channel_name}")
                sys.stdout.flush()
                transactions_before = len(transactions)
                transactions = self._generate_channel_transactions(
                    transactions, channel_name, channel_data, current_year
                )
                transactions_added = len(transactions) - transactions_before
                print(f"   ✓ Added {transactions_added:,} transactions for {channel_name}")
                sys.stdout.flush()

        print(f"\n📊 Generation summary:")
        sys.stdout.flush()
        unique_contacts = transactions['contact_id'].nunique()
        print(f"   • Total transactions: {len(transactions):,}")
        print(f"   • Unique contacts: {unique_contacts:,}")
        print(f"   • Regular donors identified: {len(self.regular_donors):,}")
        if unique_contacts > 0:
            regular_rate = len(self.regular_donors) / unique_contacts
            print(f"   • Regular donor rate: {regular_rate:.2%}")
        sys.stdout.flush()
        
        print(f"\n👥 Generating contact information...")
        # Generate contacts data based on transactions
        contacts_df = self._generate_contacts(transactions)
        print(f"   ✓ Generated {len(contacts_df):,} contacts")

        return transactions, contacts_df

    def _generate_channel_transactions(self, transactions, channel_name, channel_data, current_year):
        """Generate transactions for a specific channel"""
        total_campaigns = sum(campaign_info.get('nb', 1) for campaign_info in channel_data['campaigns'].values())
        campaign_count = 0
        
        for campaign_type, campaign_info in channel_data['campaigns'].items():
            num_campaigns = campaign_info.get('nb', 1)
            
            for campaign_num in range(num_campaigns):
                campaign_count += 1
                import sys
                if campaign_count % 5 == 0 or campaign_count == 1:
                    print(f"      → Campaign {campaign_count}/{total_campaigns} ({campaign_type})...")
                    sys.stdout.flush()
                
                # Get campaign metadata
                code_source = self._generate_campaign_metadata(
                    channel_name, channel_data, campaign_type, campaign_info, current_year
                )

                # Generate contacts and transactions
                randomness = random.uniform(0.85, 1.15)
                nb_reach, nb_sent, contact_ids = self.contact_manager.get_or_create_contacts(
                    campaign_type, channel_name, randomness
                )

                if contact_ids:
                    transactions_before = len(transactions)
                    transactions_campaign = self._create_campaign_transactions(
                        nb_reach, nb_sent, contact_ids, code_source,
                        channel_name, channel_data, campaign_type
                    )
                    transactions = pd.concat([transactions, transactions_campaign], ignore_index=True)
                    if campaign_count % 5 == 0:
                        print(f"         ✓ Added {len(transactions) - transactions_before:,} transactions")
                        sys.stdout.flush()
        
        return transactions