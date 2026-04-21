export interface HotelOffer {
  offer_id: string;
  hotel_name: string;
  stars: number;
  rating: number;
  rating_label: string;
  price_per_night_usd: number;
  price_per_night_original: { amount: number; currency: string };
  total_usd: number;
  discount_pct: number | null;
  original_price_usd: number | null;
  amenities: string[];
  distance_to_center_km: number | null;
  distance_to_beach_km: number | null;
  photo_url: string | null;
  booking_url: string;
}

export interface SearchResult {
  offers: HotelOffer[];
  total_found: number;
  source: string;
  fallback_used: boolean;
  warnings: string[];
}

export interface HotelDetails {
  offer_id: string;
  hotel_name: string;
  description: string;
  amenities: string[];
  room_types: Array<{ name: string; price_per_night_usd: number; capacity: number }>;
  cancellation_policy: string | null;
  photos: string[];
  address: string | null;
}
