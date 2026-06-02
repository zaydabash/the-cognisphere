"""
Real-world data ingestion system for The Cognisphere.

This module handles fetching, processing, and injecting real-world data
as environmental stimuli to influence agent behavior and cultural evolution.
"""

import asyncio
import logging
from dataclasses import dataclass, field
from datetime import datetime, timedelta
from enum import Enum
from typing import Any, Dict, List, Optional

import aiohttp
import feedparser
import numpy as np
from textblob import TextBlob

logger = logging.getLogger(__name__)


class StimulusType(Enum):
    """Types of environmental stimuli."""

    NEWS = "news"
    SOCIAL_MEDIA = "social_media"
    WEATHER = "weather"
    ECONOMIC = "economic"
    TECHNOLOGICAL = "technological"
    POLITICAL = "political"
    CULTURAL = "cultural"
    SCIENTIFIC = "scientific"


class StimulusIntensity(Enum):
    """Intensity levels for stimuli."""

    LOW = 0.1
    MEDIUM = 0.3
    HIGH = 0.6
    CRITICAL = 1.0


@dataclass
class EnvironmentalStimulus:
    """Represents a real-world environmental stimulus."""

    id: str
    stimulus_type: StimulusType
    title: str
    content: str
    source: str
    timestamp: datetime
    intensity: StimulusIntensity
    sentiment: float  # -1.0 to 1.0
    keywords: List[str] = field(default_factory=list)
    cultural_impact: float = 0.0  # How much this affects culture
    economic_impact: float = 0.0  # How much this affects economy
    social_impact: float = 0.0  # How much this affects social dynamics
    processed: bool = False


class DataSource:
    """Base class for data sources."""

    def __init__(self, name: str, enabled: bool = True):
        self.name = name
        self.enabled = enabled
        self.last_fetch: Optional[datetime] = None
        self.fetch_interval = timedelta(minutes=30)

    async def fetch_data(self) -> List[EnvironmentalStimulus]:
        """Fetch data from this source."""
        raise NotImplementedError

    def should_fetch(self) -> bool:
        """Check if it's time to fetch data."""
        if not self.enabled:
            return False
        if self.last_fetch is None:
            return True
        return datetime.now() - self.last_fetch > self.fetch_interval


class NewsAPISource(DataSource):
    """News API data source."""

    def __init__(self, api_key: str, enabled: bool = True):
        super().__init__("News API", enabled)
        self.api_key = api_key
        self.base_url = "https://newsapi.org/v2"
        self.categories = ["technology", "science", "business", "entertainment", "health"]

    async def fetch_data(self) -> List[EnvironmentalStimulus]:
        """Fetch news articles."""
        if not self.should_fetch():
            return []

        stimuli = []

        try:
            async with aiohttp.ClientSession() as session:
                for category in self.categories:
                    url = f"{self.base_url}/everything"
                    params = {
                        "apiKey": self.api_key,
                        "q": category,
                        "sortBy": "publishedAt",
                        "pageSize": 10,
                        "language": "en",
                    }

                    async with session.get(url, params=params) as response:
                        if response.status == 200:
                            data = await response.json()

                            for article in data.get("articles", []):
                                stimulus = self._process_article(article, category)
                                if stimulus:
                                    stimuli.append(stimulus)

        except Exception as e:
            logger.error(f"Error fetching news data: {e}")

        self.last_fetch = datetime.now()
        return stimuli

    def _process_article(self, article: Dict, category: str) -> Optional[EnvironmentalStimulus]:
        """Process a news article into a stimulus."""
        try:
            # Extract sentiment
            content = f"{article.get('title', '')} {article.get('description', '')}"
            sentiment = TextBlob(content).sentiment.polarity

            # Determine stimulus type
            stimulus_type_map = {
                "technology": StimulusType.TECHNOLOGICAL,
                "science": StimulusType.SCIENTIFIC,
                "business": StimulusType.ECONOMIC,
                "entertainment": StimulusType.CULTURAL,
                "health": StimulusType.SCIENTIFIC,
            }

            stimulus_type = stimulus_type_map.get(category, StimulusType.NEWS)

            # Calculate intensity based on sentiment and content
            intensity = self._calculate_intensity(sentiment, content)

            # Extract keywords
            keywords = self._extract_keywords(content)

            # Calculate impacts
            cultural_impact = self._calculate_cultural_impact(content, category)
            economic_impact = self._calculate_economic_impact(content, category)
            social_impact = self._calculate_social_impact(content, category)

            return EnvironmentalStimulus(
                id=f"news_{article.get('url', '')[-10:]}",
                stimulus_type=stimulus_type,
                title=article.get("title", ""),
                content=content,
                source=article.get("source", {}).get("name", "Unknown"),
                timestamp=datetime.now(),
                intensity=intensity,
                sentiment=sentiment,
                keywords=keywords,
                cultural_impact=cultural_impact,
                economic_impact=economic_impact,
                social_impact=social_impact,
            )

        except Exception as e:
            logger.error(f"Error processing article: {e}")
            return None

    def _calculate_intensity(self, sentiment: float, content: str) -> StimulusIntensity:
        """Calculate stimulus intensity."""
        # Base intensity on sentiment magnitude and content length
        sentiment_magnitude = abs(sentiment)
        content_length_factor = min(len(content) / 1000, 1.0)

        intensity_score = (sentiment_magnitude + content_length_factor) / 2

        if intensity_score > 0.7:
            return StimulusIntensity.CRITICAL
        elif intensity_score > 0.5:
            return StimulusIntensity.HIGH
        elif intensity_score > 0.3:
            return StimulusIntensity.MEDIUM
        else:
            return StimulusIntensity.LOW

    def _extract_keywords(self, content: str) -> List[str]:
        """Extract keywords from content."""
        # Simple keyword extraction (could be enhanced with NLP)
        words = content.lower().split()
        # Filter out common words and extract meaningful terms
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
        }
        keywords = [word for word in words if len(word) > 3 and word not in stop_words]
        return list(set(keywords))[:10]  # Return top 10 unique keywords

    def _calculate_cultural_impact(self, content: str, category: str) -> float:
        """Calculate cultural impact score."""
        cultural_keywords = [
            "culture",
            "art",
            "music",
            "film",
            "literature",
            "tradition",
            "heritage",
            "identity",
        ]
        cultural_score = sum(1 for keyword in cultural_keywords if keyword in content.lower())
        return min(cultural_score / 5.0, 1.0)

    def _calculate_economic_impact(self, content: str, category: str) -> float:
        """Calculate economic impact score."""
        economic_keywords = [
            "economy",
            "market",
            "trade",
            "business",
            "finance",
            "investment",
            "recession",
            "growth",
        ]
        economic_score = sum(1 for keyword in economic_keywords if keyword in content.lower())
        return min(economic_score / 5.0, 1.0)

    def _calculate_social_impact(self, content: str, category: str) -> float:
        """Calculate social impact score."""
        social_keywords = [
            "social",
            "community",
            "society",
            "people",
            "public",
            "democracy",
            "rights",
            "justice",
        ]
        social_score = sum(1 for keyword in social_keywords if keyword in content.lower())
        return min(social_score / 5.0, 1.0)


class RSSSource(DataSource):
    """RSS feed data source."""

    def __init__(self, feed_url: str, name: str, enabled: bool = True):
        super().__init__(name, enabled)
        self.feed_url = feed_url
        self.fetch_interval = timedelta(hours=1)

    async def fetch_data(self) -> List[EnvironmentalStimulus]:
        """Fetch data from RSS feed."""
        if not self.should_fetch():
            return []

        stimuli = []

        try:
            feed = feedparser.parse(self.feed_url)

            for entry in feed.entries[:10]:  # Limit to 10 entries
                stimulus = self._process_rss_entry(entry)
                if stimulus:
                    stimuli.append(stimulus)

        except Exception as e:
            logger.error(f"Error fetching RSS data from {self.feed_url}: {e}")

        self.last_fetch = datetime.now()
        return stimuli

    def _process_rss_entry(self, entry) -> Optional[EnvironmentalStimulus]:
        """Process RSS entry into stimulus."""
        try:
            content = f"{entry.get('title', '')} {entry.get('summary', '')}"
            sentiment = TextBlob(content).sentiment.polarity

            # Determine stimulus type based on feed name
            stimulus_type = self._determine_stimulus_type()

            intensity = self._calculate_intensity(sentiment, content)
            keywords = self._extract_keywords(content)

            return EnvironmentalStimulus(
                id=f"rss_{hash(entry.get('link', ''))}",
                stimulus_type=stimulus_type,
                title=entry.get("title", ""),
                content=content,
                source=self.name,
                timestamp=datetime.now(),
                intensity=intensity,
                sentiment=sentiment,
                keywords=keywords,
            )

        except Exception as e:
            logger.error(f"Error processing RSS entry: {e}")
            return None

    def _determine_stimulus_type(self) -> StimulusType:
        """Determine stimulus type based on feed name."""
        name_lower = self.name.lower()

        if "tech" in name_lower or "technology" in name_lower:
            return StimulusType.TECHNOLOGICAL
        elif "science" in name_lower:
            return StimulusType.SCIENTIFIC
        elif "business" in name_lower or "economy" in name_lower:
            return StimulusType.ECONOMIC
        elif "culture" in name_lower or "art" in name_lower:
            return StimulusType.CULTURAL
        elif "politics" in name_lower or "political" in name_lower:
            return StimulusType.POLITICAL
        else:
            return StimulusType.NEWS

    def _calculate_intensity(self, sentiment: float, content: str) -> StimulusIntensity:
        """Calculate stimulus intensity."""
        sentiment_magnitude = abs(sentiment)
        content_length_factor = min(len(content) / 1000, 1.0)

        intensity_score = (sentiment_magnitude + content_length_factor) / 2

        if intensity_score > 0.7:
            return StimulusIntensity.CRITICAL
        elif intensity_score > 0.5:
            return StimulusIntensity.HIGH
        elif intensity_score > 0.3:
            return StimulusIntensity.MEDIUM
        else:
            return StimulusIntensity.LOW

    def _extract_keywords(self, content: str) -> List[str]:
        """Extract keywords from content."""
        words = content.lower().split()
        stop_words = {
            "the",
            "a",
            "an",
            "and",
            "or",
            "but",
            "in",
            "on",
            "at",
            "to",
            "for",
            "of",
            "with",
            "by",
        }
        keywords = [word for word in words if len(word) > 3 and word not in stop_words]
        return list(set(keywords))[:10]


class WeatherSource(DataSource):
    """Weather data source."""

    def __init__(self, api_key: str, city: str = "New York", enabled: bool = True):
        super().__init__("Weather", enabled)
        self.api_key = api_key
        self.city = city
        self.fetch_interval = timedelta(hours=6)

    async def fetch_data(self) -> List[EnvironmentalStimulus]:
        """Fetch weather data."""
        if not self.should_fetch():
            return []

        stimuli = []

        try:
            url = "http://api.openweathermap.org/data/2.5/weather"
            params = {"q": self.city, "appid": self.api_key, "units": "metric"}

            async with aiohttp.ClientSession() as session:
                async with session.get(url, params=params) as response:
                    if response.status == 200:
                        data = await response.json()
                        stimulus = self._process_weather_data(data)
                        if stimulus:
                            stimuli.append(stimulus)

        except Exception as e:
            logger.error(f"Error fetching weather data: {e}")

        self.last_fetch = datetime.now()
        return stimuli

    def _process_weather_data(self, data: Dict) -> Optional[EnvironmentalStimulus]:
        """Process weather data into stimulus."""
        try:
            temp = data.get("main", {}).get("temp", 20)
            description = data.get("weather", [{}])[0].get("description", "clear sky")

            # Create weather-based stimulus
            content = f"Weather in {self.city}: {temp}°C, {description}"

            # Calculate intensity based on weather extremes
            intensity = self._calculate_weather_intensity(temp, description)

            # Weather affects social behavior
            social_impact = self._calculate_weather_social_impact(temp, description)

            return EnvironmentalStimulus(
                id=f"weather_{self.city}_{datetime.now().strftime('%Y%m%d%H')}",
                stimulus_type=StimulusType.WEATHER,
                title=f"Weather Update: {self.city}",
                content=content,
                source="OpenWeatherMap",
                timestamp=datetime.now(),
                intensity=intensity,
                sentiment=0.0,  # Weather is neutral
                keywords=[description, "weather", self.city.lower()],
                social_impact=social_impact,
            )

        except Exception as e:
            logger.error(f"Error processing weather data: {e}")
            return None

    def _calculate_weather_intensity(self, temp: float, description: str) -> StimulusIntensity:
        """Calculate intensity based on weather conditions."""
        # Extreme temperatures or severe weather = higher intensity
        if temp < -10 or temp > 40:
            return StimulusIntensity.HIGH
        elif "storm" in description or "extreme" in description:
            return StimulusIntensity.HIGH
        elif temp < 0 or temp > 35:
            return StimulusIntensity.MEDIUM
        else:
            return StimulusIntensity.LOW

    def _calculate_weather_social_impact(self, temp: float, description: str) -> float:
        """Calculate how weather affects social behavior."""
        # Extreme weather affects social behavior more
        if temp < -5 or temp > 35:
            return 0.8
        elif "rain" in description or "snow" in description:
            return 0.6
        elif "sunny" in description or "clear" in description:
            return 0.3
        else:
            return 0.2


class EnvironmentalStimuliManager:
    """Manages environmental stimuli and their impact on the simulation."""

    def __init__(self):
        self.sources: List[DataSource] = []
        self.active_stimuli: List[EnvironmentalStimulus] = []
        self.stimulus_history: List[EnvironmentalStimulus] = []
        self.cultural_mirroring_factor = 0.7  # How much culture mirrors reality
        self.divergence_rate = 0.01  # How fast culture diverges from reality
        self.reality_baseline = {}  # Baseline reality patterns

    def add_source(self, source: DataSource):
        """Add a data source."""
        self.sources.append(source)

    async def fetch_all_stimuli(self) -> List[EnvironmentalStimulus]:
        """Fetch stimuli from all sources."""
        all_stimuli = []

        for source in self.sources:
            try:
                stimuli = await source.fetch_data()
                all_stimuli.extend(stimuli)
            except Exception as e:
                logger.error(f"Error fetching from {source.name}: {e}")

        # Process and filter stimuli
        processed_stimuli = self._process_stimuli(all_stimuli)

        # Add to active stimuli
        self.active_stimuli.extend(processed_stimuli)

        # Update reality baseline
        self._update_reality_baseline(processed_stimuli)

        return processed_stimuli

    def _process_stimuli(self, stimuli: List[EnvironmentalStimulus]) -> List[EnvironmentalStimulus]:
        """Process and filter stimuli."""
        processed = []

        for stimulus in stimuli:
            # Skip if already processed
            if stimulus.processed:
                continue

            # Apply cultural mirroring
            self._apply_cultural_mirroring(stimulus)

            # Apply divergence
            self._apply_divergence(stimulus)

            stimulus.processed = True
            processed.append(stimulus)

        return processed

    def _apply_cultural_mirroring(self, stimulus: EnvironmentalStimulus):
        """Apply cultural mirroring to make culture reflect reality."""
        # Increase cultural impact based on mirroring factor
        stimulus.cultural_impact *= 1 + self.cultural_mirroring_factor

        # Adjust sentiment based on reality patterns
        if stimulus.stimulus_type in self.reality_baseline:
            baseline_sentiment = self.reality_baseline[stimulus.stimulus_type].get("sentiment", 0)
            # Blend current sentiment with reality baseline
            stimulus.sentiment = (
                stimulus.sentiment * (1 - self.cultural_mirroring_factor)
                + baseline_sentiment * self.cultural_mirroring_factor
            )

    def _apply_divergence(self, stimulus: EnvironmentalStimulus):
        """Apply divergence to create future version."""
        # Gradually diverge from reality
        divergence_factor = np.random.normal(0, self.divergence_rate)

        # Apply divergence to sentiment
        stimulus.sentiment += divergence_factor
        stimulus.sentiment = max(-1.0, min(1.0, stimulus.sentiment))

        # Apply divergence to cultural impact
        stimulus.cultural_impact += divergence_factor * 0.1
        stimulus.cultural_impact = max(0.0, min(1.0, stimulus.cultural_impact))

        # Add future-oriented keywords
        future_keywords = ["future", "evolution", "transformation", "innovation", "progress"]
        stimulus.keywords.extend(future_keywords[:2])  # Add 2 future keywords

    def _update_reality_baseline(self, stimuli: List[EnvironmentalStimulus]):
        """Update the reality baseline patterns."""
        for stimulus in stimuli:
            stimulus_type = stimulus.stimulus_type

            if stimulus_type not in self.reality_baseline:
                self.reality_baseline[stimulus_type] = {
                    "sentiment_sum": 0,
                    "count": 0,
                    "cultural_impact_sum": 0,
                    "economic_impact_sum": 0,
                    "social_impact_sum": 0,
                }

            baseline = self.reality_baseline[stimulus_type]
            baseline["sentiment_sum"] += stimulus.sentiment
            baseline["count"] += 1
            baseline["cultural_impact_sum"] += stimulus.cultural_impact
            baseline["economic_impact_sum"] += stimulus.economic_impact
            baseline["social_impact_sum"] += stimulus.social_impact

        # Calculate averages
        for stimulus_type, baseline in self.reality_baseline.items():
            if baseline["count"] > 0:
                baseline["sentiment"] = baseline["sentiment_sum"] / baseline["count"]
                baseline["cultural_impact"] = baseline["cultural_impact_sum"] / baseline["count"]
                baseline["economic_impact"] = baseline["economic_impact_sum"] / baseline["count"]
                baseline["social_impact"] = baseline["social_impact_sum"] / baseline["count"]

    def get_active_stimuli(self) -> List[EnvironmentalStimulus]:
        """Get currently active stimuli."""
        return self.active_stimuli

    def get_stimuli_by_type(self, stimulus_type: StimulusType) -> List[EnvironmentalStimulus]:
        """Get stimuli filtered by type."""
        return [s for s in self.active_stimuli if s.stimulus_type == stimulus_type]

    def get_stimuli_by_intensity(
        self, min_intensity: StimulusIntensity
    ) -> List[EnvironmentalStimulus]:
        """Get stimuli filtered by minimum intensity."""
        return [s for s in self.active_stimuli if s.intensity.value >= min_intensity.value]

    def cleanup_old_stimuli(self, max_age_hours: int = 24):
        """Remove old stimuli."""
        cutoff_time = datetime.now() - timedelta(hours=max_age_hours)

        # Move old stimuli to history
        old_stimuli = [s for s in self.active_stimuli if s.timestamp < cutoff_time]
        self.stimulus_history.extend(old_stimuli)

        # Remove from active
        self.active_stimuli = [s for s in self.active_stimuli if s.timestamp >= cutoff_time]

    def get_cultural_divergence_summary(self) -> Dict[str, Any]:
        """Get summary of cultural divergence from reality."""
        return {
            "mirroring_factor": self.cultural_mirroring_factor,
            "divergence_rate": self.divergence_rate,
            "reality_baseline": self.reality_baseline,
            "active_stimuli_count": len(self.active_stimuli),
            "historical_stimuli_count": len(self.stimulus_history),
        }


# Example usage and configuration
def create_default_stimuli_manager() -> EnvironmentalStimuliManager:
    """Create a default stimuli manager with common data sources."""
    manager = EnvironmentalStimuliManager()

    # Add RSS sources (no API keys required)
    rss_sources = [
        ("https://feeds.bbci.co.uk/news/technology/rss.xml", "BBC Technology"),
        ("https://feeds.bbci.co.uk/news/science_and_environment/rss.xml", "BBC Science"),
        ("https://feeds.bbci.co.uk/news/business/rss.xml", "BBC Business"),
        ("https://feeds.bbci.co.uk/news/entertainment/rss.xml", "BBC Entertainment"),
        ("https://rss.cnn.com/rss/edition_technology.rss", "CNN Technology"),
        ("https://rss.cnn.com/rss/edition.rss", "CNN World News"),
    ]

    for feed_url, name in rss_sources:
        rss_source = RSSSource(feed_url, name)
        manager.add_source(rss_source)

    return manager


if __name__ == "__main__":
    # Example usage
    async def main():
        manager = create_default_stimuli_manager()

        # Fetch stimuli
        stimuli = await manager.fetch_all_stimuli()

        print(f"Fetched {len(stimuli)} environmental stimuli:")
        for stimulus in stimuli[:5]:  # Show first 5
            print(f"- {stimulus.title} ({stimulus.stimulus_type.value})")
            print(f"  Sentiment: {stimulus.sentiment:.2f}, Intensity: {stimulus.intensity.value}")
            print(f"  Cultural Impact: {stimulus.cultural_impact:.2f}")
            print()

    asyncio.run(main())
