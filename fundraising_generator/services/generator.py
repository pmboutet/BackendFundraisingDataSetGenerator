import pandas as pd
import numpy as np
from datetime import datetime, timedelta
import random
import string
from faker import Faker
from scipy.spatial import KDTree
from .contact_manager import ContactManager  # Added missing import

class FundraisingDataGenerator:
    def __init__(self, config):
        """Initialize the generator with configuration"""
        self.config = config
        self.load_config()
        self.contact_manager = ContactManager(self.CHANNELS)
        self.fake = Faker(self.LOCALISATION)
