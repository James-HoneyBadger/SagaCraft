"""Advanced Trading System - player-to-player direct trading, trade history, insurance."""

from dataclasses import dataclass, field
from enum import Enum
from typing import Dict, List, Optional, Tuple
import time


class TradeStatus(Enum):
    """Status of a trade offer."""
    PENDING = "pending"
    ACCEPTED = "accepted"
    REJECTED = "rejected"
    CANCELLED = "cancelled"
    COMPLETED = "completed"
    EXPIRED = "expired"


class ItemRarity(Enum):
    """Item rarity tiers."""
    COMMON = "common"
    UNCOMMON = "uncommon"
    RARE = "rare"
    EPIC = "epic"
    LEGENDARY = "legendary"


@dataclass
class TradeItem:
    """An item in a trade."""
    item_id: str
    item_name: str
    quantity: int
    rarity: ItemRarity = ItemRarity.COMMON
    value: int = 0  # Estimated market value


@dataclass
class TradeOffer:
    """A trade offer between two players."""
    trade_id: str
    sender_id: str
    receiver_id: str
    sender_items: List[TradeItem] = field(default_factory=list)
    receiver_items: List[TradeItem] = field(default_factory=list)
    sender_gold: int = 0
    receiver_gold: int = 0
    status: TradeStatus = TradeStatus.PENDING
    created_time: int = 0
    expires_time: int = 0
    completed_time: Optional[int] = None
    trade_message: str = ""


@dataclass
class TradeHistory:
    """Record of a completed trade."""
    trade_id: str
    player1_id: str
    player2_id: str
    items_exchanged: List[TradeItem]
    gold_exchanged: int
    timestamp: int
    fair_value_difference: int  # How unbalanced the trade was


@dataclass
class TradeReputation:
    """Player trading reputation."""
    player_id: str
    successful_trades: int = 0
    cancelled_trades: int = 0
    disputed_trades: int = 0
    reputation_score: int = 100  # 0-100
    is_trusted_trader: bool = False
    trading_since: int = 0


@dataclass
class TradeInsurance:
    """Insurance for high-value trades."""
    insurance_id: str
    trade_id: str
    insured_value: int
    premium_paid: int
    coverage_percentage: int = 80  # 80% of value returned if scammed
    expires: int = 0


class PlayerTradingSystem:
    """Advanced player-to-player trading system."""

    def __init__(self):
        self.active_trades: Dict[str, TradeOffer] = {}
        self.trade_history: List[TradeHistory] = []
        self.player_reputations: Dict[str, TradeReputation] = {}
        self.trade_insurance: Dict[str, TradeInsurance] = {}
        self.next_trade_id = 0
        self.next_insurance_id = 0
        self.trade_tax_rate = 0.05  # 5% tax on gold trades

    def get_reputation(self, player_id: str) -> TradeReputation:
        """Get or create player reputation."""
        if player_id not in self.player_reputations:
            self.player_reputations[player_id] = TradeReputation(
                player_id=player_id,
                trading_since=int(time.time())
            )
        return self.player_reputations[player_id]

    def create_trade_offer(
        self,
        sender_id: str,
        receiver_id: str,
        sender_items: List[TradeItem],
        receiver_items: List[TradeItem],
        sender_gold: int = 0,
        receiver_gold: int = 0,
        message: str = ""
    ) -> TradeOffer:
        """Create a new trade offer."""
        trade_id = f"trade_{self.next_trade_id}"
        self.next_trade_id += 1

        offer = TradeOffer(
            trade_id=trade_id,
            sender_id=sender_id,
            receiver_id=receiver_id,
            sender_items=sender_items,
            receiver_items=receiver_items,
            sender_gold=sender_gold,
            receiver_gold=receiver_gold,
            created_time=int(time.time()),
            expires_time=int(time.time()) + 3600,  # 1 hour expiry
            trade_message=message
        )

        self.active_trades[trade_id] = offer
        return offer

    def accept_trade(self, trade_id: str, player_id: str) -> Tuple[bool, str]:
        """Accept a trade offer."""
        offer = self.active_trades.get(trade_id)
        if not offer:
            return False, "Trade not found"

        # Only receiver can accept
        if player_id != offer.receiver_id:
            return False, "Only the trade recipient can accept"

        if offer.status != TradeStatus.PENDING:
            return False, f"Trade is {offer.status.value}"

        # Check expiry
        if int(time.time()) > offer.expires_time:
            offer.status = TradeStatus.EXPIRED
            return False, "Trade has expired"

        # Calculate trade fairness
        sender_value = self._calculate_value(offer.sender_items, offer.sender_gold)
        receiver_value = self._calculate_value(offer.receiver_items, offer.receiver_gold)
        value_diff = abs(sender_value - receiver_value)

        # Apply tax to gold
        gold_after_tax = offer.sender_gold * (1 - self.trade_tax_rate)

        # Complete trade
        offer.status = TradeStatus.COMPLETED
        offer.completed_time = int(time.time())

        # Record history
        all_items = offer.sender_items + offer.receiver_items
        history = TradeHistory(
            trade_id=trade_id,
            player1_id=offer.sender_id,
            player2_id=offer.receiver_id,
            items_exchanged=all_items,
            gold_exchanged=offer.sender_gold + offer.receiver_gold,
            timestamp=int(time.time()),
            fair_value_difference=value_diff
        )
        self.trade_history.append(history)

        # Update reputations
        sender_rep = self.get_reputation(offer.sender_id)
        receiver_rep = self.get_reputation(offer.receiver_id)
        sender_rep.successful_trades += 1
        receiver_rep.successful_trades += 1

        # Update trusted status
        if sender_rep.successful_trades >= 10 and sender_rep.reputation_score >= 90:
            sender_rep.is_trusted_trader = True
        if receiver_rep.successful_trades >= 10 and receiver_rep.reputation_score >= 90:
            receiver_rep.is_trusted_trader = True

        return True, f"Trade completed! Gold after tax: {gold_after_tax:.0f}"

    def reject_trade(self, trade_id: str, player_id: str) -> Tuple[bool, str]:
        """Reject a trade offer."""
        offer = self.active_trades.get(trade_id)
        if not offer:
            return False, "Trade not found"

        if player_id != offer.receiver_id:
            return False, "Only the trade recipient can reject"

        if offer.status != TradeStatus.PENDING:
            return False, f"Trade is {offer.status.value}"

        offer.status = TradeStatus.REJECTED
        return True, "Trade rejected"

    def cancel_trade(self, trade_id: str, player_id: str) -> Tuple[bool, str]:
        """Cancel a trade offer."""
        offer = self.active_trades.get(trade_id)
        if not offer:
            return False, "Trade not found"

        if player_id != offer.sender_id:
            return False, "Only the trade sender can cancel"

        if offer.status != TradeStatus.PENDING:
            return False, f"Trade is {offer.status.value}"

        offer.status = TradeStatus.CANCELLED

        # Penalize reputation slightly for cancellations
        rep = self.get_reputation(player_id)
        rep.cancelled_trades += 1
        rep.reputation_score = max(0, rep.reputation_score - 2)

        return True, "Trade cancelled"

    def get_active_trades_for_player(self, player_id: str) -> List[TradeOffer]:
        """Get all active trades involving a player."""
        return [
            offer for offer in self.active_trades.values()
            if (offer.sender_id == player_id or offer.receiver_id == player_id)
            and offer.status == TradeStatus.PENDING
        ]

    def get_trade_history_for_player(self, player_id: str, limit: int = 10) -> List[TradeHistory]:
        """Get trade history for a player."""
        player_trades = [
            trade for trade in self.trade_history
            if trade.player1_id == player_id or trade.player2_id == player_id
        ]
        return sorted(player_trades, key=lambda t: t.timestamp, reverse=True)[:limit]

    def purchase_trade_insurance(
        self,
        trade_id: str,
        insured_value: int,
        buyer_id: str
    ) -> Tuple[Optional[TradeInsurance], str]:
        """Purchase insurance for a high-value trade."""
        offer = self.active_trades.get(trade_id)
        if not offer:
            return None, "Trade not found"

        if buyer_id != offer.sender_id and buyer_id != offer.receiver_id:
            return None, "You are not part of this trade"

        # Calculate premium (5% of insured value)
        premium = int(insured_value * 0.05)

        insurance_id = f"insurance_{self.next_insurance_id}"
        self.next_insurance_id += 1

        insurance = TradeInsurance(
            insurance_id=insurance_id,
            trade_id=trade_id,
            insured_value=insured_value,
            premium_paid=premium,
            expires=int(time.time()) + 86400  # 24 hours
        )

        self.trade_insurance[insurance_id] = insurance
        return insurance, f"Insurance purchased for {premium} gold"

    def _calculate_value(self, items: List[TradeItem], gold: int) -> int:
        """Calculate total value of items and gold."""
        item_value = sum(item.value * item.quantity for item in items)
        return item_value + gold

    def get_trending_items(self, limit: int = 10) -> List[Tuple[str, int]]:
        """Get most traded items."""
        item_counts: Dict[str, int] = {}

        for trade in self.trade_history:
            for item in trade.items_exchanged:
                item_counts[item.item_name] = item_counts.get(item.item_name, 0) + item.quantity

        sorted_items = sorted(item_counts.items(), key=lambda x: x[1], reverse=True)
        return sorted_items[:limit]

    def get_market_price(self, item_name: str) -> Optional[int]:
        """Get average market price for an item based on trade history."""
        prices = []

        for trade in self.trade_history:
            for item in trade.items_exchanged:
                if item.item_name == item_name and item.value > 0:
                    prices.append(item.value)

        if not prices:
            return None

        return int(sum(prices) / len(prices))

    def generate_trade_report(self, player_id: str) -> Dict:
        """Generate trading report for a player."""
        rep = self.get_reputation(player_id)
        history = self.get_trade_history_for_player(player_id, limit=100)

        total_value_traded = sum(t.gold_exchanged for t in history)
        avg_trade_value = total_value_traded // len(history) if history else 0

        return {
            "player_id": player_id,
            "reputation_score": rep.reputation_score,
            "is_trusted_trader": rep.is_trusted_trader,
            "successful_trades": rep.successful_trades,
            "cancelled_trades": rep.cancelled_trades,
            "total_value_traded": total_value_traded,
            "avg_trade_value": avg_trade_value,
            "active_trades": len(self.get_active_trades_for_player(player_id)),
            "trading_since": rep.trading_since,
        }

    def cleanup_expired_trades(self) -> int:
        """Clean up expired trades."""
        current_time = int(time.time())
        expired_count = 0

        for offer in self.active_trades.values():
            if offer.status == TradeStatus.PENDING and current_time > offer.expires_time:
                offer.status = TradeStatus.EXPIRED
                expired_count += 1

        return expired_count
