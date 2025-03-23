from dataclasses import dataclass
import requests
from typing import Optional

@dataclass
class CarbonEmissions:
    energy_consumed: float = 0.0  # kWh
    emissions: float = 0.0        # kgCO2
    country_name: str = "NLD"     # Netherlands
    country_iso_code: str = "NLD"
    region: Optional[str] = None
    on_cloud: bool = False
    cloud_provider: Optional[str] = None
    cloud_region: Optional[str] = None

class EmissionsTracker:
    def __init__(self, country_iso_code="NLD"):
        self.country_iso_code = country_iso_code
        self._co2_signal_api_token = None  # Optional CO2 Signal API token
        
        # Carbon intensity data (gCO2/kWh) by country
        # Source: https://ourworldindata.org/grapher/carbon-intensity-electricity
        self._carbon_intensity_data = {
            "NLD": 375.0,  # Netherlands
            "USA": 379.0,  # United States
            "CHN": 549.0,  # China
            "GBR": 231.0,  # United Kingdom
            # Add more countries as needed
        }
        self._world_average_carbon_intensity = 475.0  # Global average

    def get_carbon_intensity(self):
        """Get carbon intensity for the specified country (gCO2/kWh)"""
        # Try to get real-time data from CO2 Signal API
        if self._co2_signal_api_token:
            try:
                response = requests.get(
                    f"https://api.co2signal.com/v1/latest?countryCode={self.country_iso_code}",
                    headers={"auth-token": self._co2_signal_api_token},
                    timeout=5
                )
                if response.status_code == 200:
                    return response.json()["data"]["carbonIntensity"]
            except:
                pass  # Fallback to static data if API call fails

        # Use static data
        return self._carbon_intensity_data.get(
            self.country_iso_code, 
            self._world_average_carbon_intensity
        )

    def compute_emissions(self, energy_consumed: float) -> CarbonEmissions:
        """Calculate carbon emissions based on energy consumption

        Args:
            energy_consumed: Energy consumption in kWh

        Returns:
            CarbonEmissions: Object containing emissions data
        """
        # Get carbon intensity (gCO2/kWh)
        carbon_intensity = self.get_carbon_intensity()
        
        # Calculate emissions (convert gCO2/kWh to kgCO2/kWh)
        emissions = energy_consumed * (carbon_intensity / 1000.0)
        
        return CarbonEmissions(
            energy_consumed=energy_consumed,
            emissions=emissions,
            country_iso_code=self.country_iso_code
        )