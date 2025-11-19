import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import string
from faker import Faker
from scipy.spatial import KDTree
from .contact_manager import ContactManager

class FundraisingDataGenerator:
    def __init__(self, config):
        """Initialize the generator with configuration"""
        self.config = config
        self.load_config()
        self.contact_manager = ContactManager(self.CHANNELS)
        self.fake = Faker(self.LOCALISATION)

    def load_config(self):
        """Load all variables from the config"""
        self.YEARS = self.config.get('YEARS', 10)
        self.FIRST_YEAR = self.config.get('FIRST_YEAR', 2014)
        self.INITIAL_DONOR_DATABASE_SIZE = self.config.get('INITIAL_DONOR_DATABASE_SIZE', 10000)
        self.GLOBAL_CHURN_RATE = self.config.get('GLOBAL_CHURN_RATE', 0.99)
        self.CHANNELS = self.config.get('CHANNELS', {})
        self.CAMPAIGN_THEMES = self.config.get('CAMPAIGN_THEMES', [])
        self.WHERE_POSSIBILITIES = self.config.get('WHERE_POSSIBILITIES', [])
        self.WHO_POSSIBILITIES = self.config.get('WHO_POSSIBILITIES', [])
        self.WHAT_POSSIBILITIES = self.config.get('WHAT_POSSIBILITIES', [])
        self.SALUTATIONS = self.config.get('SALUTATIONS', [])
        self.WEALTHY_JOB = self.config.get('WEALTHY_JOB', [])
        self.NON_WEALTHY_JOB = self.config.get('NON_WEALTHY_JOB', [])
        self.LOCALISATION = self.config.get('LOCALISATION', 'fr_FR')

    def select_by_probability(self, options):
        """Select an option based on the given probabilities"""
        choices, weights = zip(*options)
        total_weight = sum(weights)
        if total_weight != 1.0:
            weights = [w / total_weight for w in weights]
        return random.choices(choices, weights, k=1)[0]

    def _generate_campaign_metadata(self, channel_data, campaign_type, campaign_info, current_year):
        """Generate metadata for a campaign"""
        code_source = {}
        
        # Select theme
        code_source['theme'] = self.select_by_probability(self.CAMPAIGN_THEMES)
        
        # Select options for where, who, and what
        num_where_options = random.randint(1, 3)
        num_who_options = random.randint(1, 3)
        num_what_options = random.randint(1, 3)

        # Generate random start date and duration
        start_day = random.randint(1, 365)
        start_date = datetime(current_year, 1, 1) + timedelta(days=start_day)
        end_date = start_date + timedelta(days=channel_data['duration'])
        
        code_source.update({
            'start': start_date,
            'end': end_date,
            'transformation_rate': campaign_info.get('transformation_rate', 0.1),
            'avg_donation': campaign_info.get('avg_donation', 50),
            'std_deviation': campaign_info.get('std_deviation', 10),
            'name': f"{current_year}-{str(start_day).zfill(2)}_{channel_data}_{code_source['theme']}"
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
        
        # Calculate deciles
        transactions_campaign['amount_decile'] = pd.qcut(
            transactions_campaign['donation_amount'], 
            10, 
            labels=False, 
            duplicates='drop'
        ) + 1

        return transactions_campaign

    def _generate_contacts(self, transactions):
        """Generate contact information for all transactions"""
        # Group transactions by contact_id and get their maximum decile
        grouped_transactions = transactions.groupby('contact_id')['amount_decile'].max().reset_index()
        
        contacts_data = []
        for _, row in grouped_transactions.iterrows():
            contact_id = row['contact_id']
            max_decile = row['amount_decile']
            
            # Generate basic contact info
            chosen_salutation = np.random.choice(
                [sal['civility'] for sal in self.SALUTATIONS],
                p=[sal['probability'] for sal in self.SALUTATIONS]
            )
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

            # Find first transaction date
            first_transaction_date = transactions[
                transactions['contact_id'] == contact_id
            ]['date'].min()

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
                'Creation_year': first_transaction_date.year
            }
            
            contacts_data.append(contact_data)

        return pd.DataFrame(contacts_data)

    def generate(self):
        """Generate fundraising dataset"""
        transactions = pd.DataFrame()

        # Iterate through each year
        for year in range(self.YEARS):
            current_year = self.FIRST_YEAR + year
            
            # Generate transactions for each channel
            for channel_name, channel_data in self.CHANNELS.items():
                transactions = self._generate_channel_transactions(
                    transactions, channel_name, channel_data, current_year
                )

        # Generate contacts data based on transactions
        contacts_df = self._generate_contacts(transactions)

        return transactions, contacts_df

    def _generate_channel_transactions(self, transactions, channel_name, channel_data, current_year):
        """Generate transactions for a specific channel"""
        for campaign_type, campaign_info in channel_data['campaigns'].items():
            num_campaigns = campaign_info.get('nb', 1)
            
            for campaign_num in range(num_campaigns):
                # Get campaign metadata
                code_source = self._generate_campaign_metadata(
                    channel_data, campaign_type, campaign_info, current_year
                )

                # Generate contacts and transactions
                randomness = random.uniform(0.85, 1.15)
                nb_reach, nb_sent, contact_ids = self.contact_manager.get_or_create_contacts(
                    campaign_type, channel_name, randomness
                )

                if contact_ids:
                    transactions_campaign = self._create_campaign_transactions(
                        nb_reach, nb_sent, contact_ids, code_source,
                        channel_name, channel_data, campaign_type
                    )
                    transactions = pd.concat([transactions, transactions_campaign], ignore_index=True)
        
        return transactions