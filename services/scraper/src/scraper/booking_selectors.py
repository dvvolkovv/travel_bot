"""CSS selectors for Booking.com search-results HTML.

Selectors WILL drift. When the parser breaks, update these first.

Current state (captured 2026-04-21):
- Results-page card root: [data-testid="property-card"]
- Price element is itself the span with data-testid="price-and-discounted-price"
  (no inner span), so the CARD_PRICE selector targets it directly.
- Review score testid container has three inner divs; the rating number is in
  the middle div with aria-hidden="true".
"""

CARD_ROOT = '[data-testid="property-card"]'
CARD_NAME = '[data-testid="title"]'
# Rating number lives on the middle child of review-score container.
# Using attribute selector (aria-hidden="true") is more stable than obfuscated class names.
CARD_RATING = '[data-testid="review-score"] div[aria-hidden="true"]'
# Rating label (e.g. "Exceptional", "Excellent") — first div inside the label sub-container.
CARD_RATING_LABEL = '[data-testid="review-score"] div[aria-hidden="false"] > div:first-child'
# Current price — the span itself carries the testid.
CARD_PRICE = '[data-testid="price-and-discounted-price"]'
# Strike-through original price (if discounted). Class names are obfuscated;
# data-testid is not attached, so we grep the wider container.
CARD_PRICE_ORIGINAL = '[data-testid="availability-rate-information"] .c90c0a70d3'
CARD_PHOTO = '[data-testid="image"]'
CARD_LINK = 'a[data-testid="title-link"]'
CARD_STARS = '[data-testid="rating-stars"] span'
CARD_DISTANCE = '[data-testid="distance"]'
CARD_AMENITIES = '[data-testid="property-card-unit-configuration"]'

AMENITY_KEYWORDS = {
    "wifi": ["free wifi", "wifi", "wi-fi"],
    "pool": ["pool", "swimming pool"],
    "breakfast": ["breakfast included", "free breakfast"],
    "parking": ["free parking", "parking"],
    "gym": ["fitness", "gym"],
    "pet_friendly": ["pets allowed", "pet-friendly"],
}

# Hotel-details page selectors
DETAILS_NAME = 'h2.pp-header__title, h2[class*="pp-header"], header h2'
DETAILS_DESCRIPTION = '#property_description_content, [data-testid="property-description"]'
DETAILS_AMENITIES = '[data-testid="property-most-popular-facilities-wrapper"] [data-testid="facility-highlight-name"], [data-testid="property-section--content"] li'
DETAILS_PHOTOS = 'img[src*="bstatic.com"]'
DETAILS_ADDRESS = '[data-testid="address"], [data-testid="PropertyHeaderAddressDesktop-wrapper"]'
