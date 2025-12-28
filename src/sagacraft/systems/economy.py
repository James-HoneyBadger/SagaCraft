"""Economy System - player-to-player trading with auction house and price history."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple
from collections import deque


@dataclass
class AuctionListing:
    """An item listed on the auction house."""
    listing_id: str
    seller_id: str
    item_id: str
    item_name: str
    quantity: int
    price_per_unit: int
    listed_time: int  # Unix timestamp
    duration_hours: int = 48
    sold: bool = False
    buyer_id: Optional[str] = None


@dataclass
class PriceHistoryEntry:
    """Historical price data for an item."""
    item_id: str
    timestamp: int
    average_price: int
    transaction_count: int
    volume: int  # Total units traded


@dataclass
class PlayerWallet:
    """A player's currency wallet."""
    player_id: str
    gold: int = 1000  # Starting currency
    vault_slots: int = 50  # Item storage
    tax_rate: float = 0.05  # 5% auction tax


class EconomySystem:
    """Manages player economy, trading, and auction house."""

    def __init__(self):
        self.auction_listings: Dict[str, AuctionListing] = {}
        self.player_wallets: Dict[str, PlayerWallet] = {}
        self.price_history: Dict[str, deque] = {}  # item_id -> deque of PriceHistoryEntry
        self.next_listing_id = 0
        self.completed_trades: List[AuctionListing] = []

    def get_wallet(self, player_id: str) -> PlayerWallet:
        """Get or create a player wallet."""
        if player_id not in self.player_wallets:
            self.player_wallets[player_id] = PlayerWallet(player_id=player_id)
        return self.player_wallets[player_id]

    def list_item(
        self,
        seller_id: str,
        item_id: str,
        item_name: str,
        quantity: int,
        price_per_unit: int,
    ) -> Tuple[Optional[AuctionListing], str]:
        """List an item on the auction house."""
        wallet = self.get_wallet(seller_id)

        # Check wallet space (simplified - 1 listing = 1 slot)
        if len(self.auction_listings) >= wallet.vault_slots:
            return None, "Auction house is full"

        listing_id = f"auction_{self.next_listing_id}"
        self.next_listing_id += 1

        listing = AuctionListing(
            listing_id=listing_id,
            seller_id=seller_id,
            item_id=item_id,
            item_name=item_name,
            quantity=quantity,
            price_per_unit=price_per_unit,
            listed_time=int(__import__("time").time()),
        )

        self.auction_listings[listing_id] = listing
        return listing, f"Listed {quantity}x {item_name} at {price_per_unit} gold each"

    def buy_from_auction(self, buyer_id: str, listing_id: str, quantity: int) -> Tuple[bool, str]:
        """Purchase items from auction house."""
        listing = self.auction_listings.get(listing_id)
        if not listing or listing.sold:
            return False, "Listing not found or already sold"

        if quantity > listing.quantity:
            return False, f"Only {listing.quantity} available"

        total_cost = listing.price_per_unit * quantity
        buyer_wallet = self.get_wallet(buyer_id)

        if buyer_wallet.gold < total_cost:
            return False, f"Insufficient gold ({buyer_wallet.gold} < {total_cost})"

        # Calculate tax
        tax = int(total_cost * buyer_wallet.tax_rate)
        seller_receives = total_cost - tax

        # Transfer currency
        buyer_wallet.gold -= total_cost
        seller_wallet = self.get_wallet(listing.seller_id)
        seller_wallet.gold += seller_receives

        # Mark as sold
        listing.sold = True
        listing.buyer_id = buyer_id
        listing.quantity = quantity

        # Record completed trade
        self.completed_trades.append(listing)

        # Update price history
        self._record_price_history(listing.item_id, listing.price_per_unit, quantity)

        return True, f"Purchased {quantity}x {listing.item_name} for {total_cost} gold"

    def _record_price_history(self, item_id: str, price: int, volume: int) -> None:
        """Record a transaction in price history."""
        if item_id not in self.price_history:
            self.price_history[item_id] = deque(maxlen=100)  # Keep last 100 transactions

        entry = PriceHistoryEntry(
            item_id=item_id,
            timestamp=int(__import__("time").time()),
            average_price=price,
            transaction_count=1,
            volume=volume,
        )
        self.price_history[item_id].append(entry)

    def get_item_price_history(self, item_id: str) -> List[PriceHistoryEntry]:
        """Get price history for an item."""
        if item_id in self.price_history:
            return list(self.price_history[item_id])
        return []

    def get_market_price(self, item_id: str) -> Tuple[int, str]:
        """Get current market average price for an item."""
        history = self.get_item_price_history(item_id)
        if not history:
            return 0, "No market data"

        # Average of last 10 transactions
        recent = history[-10:]
        avg = sum(h.average_price for h in recent) // len(recent)
        return avg, f"Market price: {avg} gold"

    def cancel_listing(self, listing_id: str, seller_id: str) -> Tuple[bool, str]:
        """Cancel an auction listing."""
        listing = self.auction_listings.get(listing_id)
        if not listing:
            return False, "Listing not found"

        if listing.seller_id != seller_id:
            return False, "Not the seller"

        if listing.sold:
            return False, "Already sold"

        del self.auction_listings[listing_id]
        return True, f"Cancelled listing for {listing.item_name}"

    def get_active_listings(self, item_id: Optional[str] = None) -> List[AuctionListing]:
        """Get all active auction listings."""
        active = [l for l in self.auction_listings.values() if not l.sold]

        if item_id:
            active = [l for l in active if l.item_id == item_id]

        # Sort by price (lowest first)
        return sorted(active, key=lambda x: x.price_per_unit)

    def get_player_listings(self, seller_id: str) -> List[AuctionListing]:
        """Get all listings by a specific seller."""
        return [l for l in self.auction_listings.values() if l.seller_id == seller_id and not l.sold]

    def transfer_gold(self, from_player: str, to_player: str, amount: int) -> Tuple[bool, str]:
        """Transfer gold between players (simplified - no taxes)."""
        from_wallet = self.get_wallet(from_player)
        to_wallet = self.get_wallet(to_player)

        if from_wallet.gold < amount:
            return False, "Insufficient gold"

        from_wallet.gold -= amount
        to_wallet.gold += amount

        return True, f"Transferred {amount} gold to {to_player}"

    def get_richest_players(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Get the richest players (leaderboard)."""
        players = sorted(
            self.player_wallets.items(), key=lambda x: x[1].gold, reverse=True
        )
        return [(player_id, wallet.gold) for player_id, wallet in players[:limit]]
