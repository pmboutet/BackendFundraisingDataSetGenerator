import random
import string
from typing import List, Tuple, Dict, Optional

class ContactManager:
    def __init__(self, channels: dict):
        """Initialize the contact manager with channel configurations.
        
        Args:
            channels (dict): Channel configurations from YAML
        """
        self.existing_contacts: Dict[str, List[str]] = {}
        self.unused_contacts: Dict[str, List[str]] = {}
        self.channels = channels
        self._initialize_contacts()

    def _initialize_contacts(self) -> None:
        """Initialize contacts for each channel with their initial numbers."""
        for channel, info in self.channels.items():
            initial_nb = info.get('initial_nb', 0)
            initial_contacts = [self._generate_unique_contact_id() for _ in range(initial_nb)]
            
            self.existing_contacts[channel] = initial_contacts
            self.unused_contacts[channel] = initial_contacts.copy()
            
            print(f'Initialized {len(initial_contacts)} contacts for channel {channel}.')

    def _generate_unique_contact_id(self) -> str:
        """Generate a unique contact ID.
        
        Returns:
            str: A unique 8-character ID
        """
        characters = string.ascii_uppercase + string.digits
        return ''.join(random.choices(characters, k=8))

    def get_contacts(self, channel: str) -> List[str]:
        """Get all contacts from a given channel.
        
        Args:
            channel (str): The channel name
            
        Returns:
            List[str]: List of contact IDs
        """
        return self.existing_contacts.get(channel, [])

    def generate_contacts_on_the_go(self, channel: str, num_required: int) -> List[str]:
        """Generate new contacts dynamically for prospecting.
        
        Args:
            channel (str): The channel name
            num_required (int): Number of contacts needed
            
        Returns:
            List[str]: List of newly generated contact IDs
        """
        new_contacts = [self._generate_unique_contact_id() for _ in range(num_required)]
        self.existing_contacts[channel].extend(new_contacts)
        return new_contacts

    def get_contacts_from_cross_sell(self, channel: str, cross_sell_info: List[Tuple[str, float]]) -> List[str]:
        """Get contacts from cross-sell channels based on specified percentages.
        
        Args:
            channel (str): The current channel
            cross_sell_info (List[Tuple[str, float]]): List of (channel, percentage) tuples
            
        Returns:
            List[str]: List of cross-sell contact IDs
        """
        cross_sell_contacts = []
        
        for cross_channel, percentage in cross_sell_info:
            contacts_in_cross_channel = self.get_contacts(cross_channel)
            cross_channel_num_required = int(len(contacts_in_cross_channel) * (percentage / 100))
            
            if cross_channel_num_required > 0:
                selected_contacts = random.sample(
                    contacts_in_cross_channel, 
                    cross_channel_num_required
                )
                cross_sell_contacts.extend(selected_contacts)

        return list(set(cross_sell_contacts))

    def get_or_create_contacts(
        self, 
        campaign_type: str, 
        channel: str, 
        randomness: float
    ) -> Tuple[int, int, List[str]]:
        """Get or create contacts based on campaign type and apply transformation rate.
        
        Args:
            campaign_type (str): Either 'prospecting' or 'retention'
            channel (str): The channel name
            randomness (float): Random factor to apply to transformation rate
            
        Returns:
            Tuple[int, int, List[str]]: (number reached, number sent, contact IDs)
        """
        channel_info = self.channels[channel]

        if campaign_type == 'prospecting':
            num_required = channel_info["campaigns"]["prospecting"]["max_reach_contact"]
            transformation_rate = (
                channel_info["campaigns"]["prospecting"]["transformation_rate"] 
                * randomness
            )
            
            contacts_ids = self.generate_contacts_on_the_go(
                channel, 
                int(num_required * transformation_rate)
            )
            nb_reach = num_required
            nb_sent = len(contacts_ids)

            print(f"Prospecting campaign in '{channel}': Reach = {nb_reach}, Sent = {nb_sent}")
            return nb_reach, nb_sent, contacts_ids[:nb_sent]

        elif campaign_type == 'retention':
            cross_sell_info = channel_info["campaigns"]["retention"].get("cross_sell", [])
            contacts_ids = self.get_contacts_from_cross_sell(channel, cross_sell_info)
            nb_reach = len(contacts_ids)

            transformation_rate = (
                channel_info["campaigns"]["retention"]["transformation_rate"] 
                * randomness
            )
            nb_sent = int(nb_reach * transformation_rate)

            print(f"Retention campaign in '{channel}': Reach = {nb_reach}, Sent = {nb_sent}")
            
            contact_ids = contacts_ids[:nb_sent]
            self.existing_contacts[channel] = list(
                set(self.existing_contacts[channel]).union(set(contact_ids[:nb_sent]))
            )
            return nb_reach, nb_sent, contact_ids

        else:
            print("Unknown campaign type. Please use 'prospecting' or 'retention'.")
            return 0, 0, []
