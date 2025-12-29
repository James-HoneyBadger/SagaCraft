"""Tests for Advanced Trading System."""

import unittest
import time
from sagacraft.systems.trading import (
    PlayerTradingSystem,
    TradeItem,
    ItemRarity,
    TradeStatus,
)


class TestPlayerTradingSystem(unittest.TestCase):
    """Test the player trading system."""

    def setUp(self):
        """Set up test fixtures."""
        self.trading = PlayerTradingSystem()
        self.player1 = "player_1"
        self.player2 = "player_2"

    def test_create_trade_offer(self):
        """Test creating a trade offer."""
        item1 = TradeItem("sword_1", "Iron Sword", 1, ItemRarity.COMMON, 100)
        item2 = TradeItem("shield_1", "Wooden Shield", 1, ItemRarity.COMMON, 50)

        offer = self.trading.create_trade_offer(
            self.player1,
            self.player2,
            [item1],
            [item2],
            sender_gold=50,
            message="Good trade!"
        )

        self.assertIsNotNone(offer.trade_id)
        self.assertEqual(offer.sender_id, self.player1)
        self.assertEqual(offer.receiver_id, self.player2)
        self.assertEqual(offer.status, TradeStatus.PENDING)

    def test_accept_trade(self):
        """Test accepting a trade."""
        item1 = TradeItem("item_1", "Item", 1, ItemRarity.COMMON, 100)

        offer = self.trading.create_trade_offer(
            self.player1,
            self.player2,
            [item1],
            [],
            sender_gold=100
        )

        success, msg = self.trading.accept_trade(offer.trade_id, self.player2)

        self.assertTrue(success)
        self.assertEqual(offer.status, TradeStatus.COMPLETED)

    def test_reject_trade(self):
        """Test rejecting a trade."""
        item1 = TradeItem("item_1", "Item", 1, ItemRarity.COMMON, 100)

        offer = self.trading.create_trade_offer(
            self.player1,
            self.player2,
            [item1],
            []
        )

        success, msg = self.trading.reject_trade(offer.trade_id, self.player2)

        self.assertTrue(success)
        self.assertEqual(offer.status, TradeStatus.REJECTED)

    def test_cancel_trade(self):
        """Test cancelling a trade."""
        item1 = TradeItem("item_1", "Item", 1, ItemRarity.COMMON, 100)

        offer = self.trading.create_trade_offer(
            self.player1,
            self.player2,
            [item1],
            []
        )

        success, msg = self.trading.cancel_trade(offer.trade_id, self.player1)

        self.assertTrue(success)
        self.assertEqual(offer.status, TradeStatus.CANCELLED)

    def test_only_receiver_can_accept(self):
        """Test that only receiver can accept trade."""
        item1 = TradeItem("item_1", "Item", 1, ItemRarity.COMMON, 100)

        offer = self.trading.create_trade_offer(
            self.player1,
            self.player2,
            [item1],
            []
        )

        success, msg = self.trading.accept_trade(offer.trade_id, self.player1)

        self.assertFalse(success)
        self.assertIn("recipient", msg)

    def test_only_sender_can_cancel(self):
        """Test that only sender can cancel trade."""
        item1 = TradeItem("item_1", "Item", 1, ItemRarity.COMMON, 100)

        offer = self.trading.create_trade_offer(
            self.player1,
            self.player2,
            [item1],
            []
        )

        success, msg = self.trading.cancel_trade(offer.trade_id, self.player2)

        self.assertFalse(success)
        self.assertIn("sender", msg)

    def test_reputation_system(self):
        """Test reputation tracking."""
        rep = self.trading.get_reputation(self.player1)

        self.assertEqual(rep.player_id, self.player1)
        self.assertEqual(rep.reputation_score, 100)
        self.assertEqual(rep.successful_trades, 0)

    def test_reputation_increases_with_trades(self):
        """Test reputation increases with successful trades."""
        item1 = TradeItem("item_1", "Item", 1, ItemRarity.COMMON, 100)

        for i in range(3):
            offer = self.trading.create_trade_offer(
                self.player1,
                self.player2,
                [item1],
                []
            )
            self.trading.accept_trade(offer.trade_id, self.player2)

        rep = self.trading.get_reputation(self.player1)
        self.assertEqual(rep.successful_trades, 3)

    def test_reputation_decreases_with_cancellations(self):
        """Test reputation decreases with cancellations."""
        initial_score = self.trading.get_reputation(self.player1).reputation_score

        item1 = TradeItem("item_1", "Item", 1, ItemRarity.COMMON, 100)
        offer = self.trading.create_trade_offer(
            self.player1,
            self.player2,
            [item1],
            []
        )
        self.trading.cancel_trade(offer.trade_id, self.player1)

        rep = self.trading.get_reputation(self.player1)
        self.assertLess(rep.reputation_score, initial_score)

    def test_get_active_trades_for_player(self):
        """Test getting active trades for a player."""
        item1 = TradeItem("item_1", "Item", 1, ItemRarity.COMMON, 100)

        offer1 = self.trading.create_trade_offer(self.player1, self.player2, [item1], [])
        offer2 = self.trading.create_trade_offer(self.player2, self.player1, [item1], [])

        trades = self.trading.get_active_trades_for_player(self.player1)

        self.assertEqual(len(trades), 2)

    def test_get_trade_history(self):
        """Test getting trade history."""
        item1 = TradeItem("item_1", "Item", 1, ItemRarity.COMMON, 100)

        offer = self.trading.create_trade_offer(self.player1, self.player2, [item1], [])
        self.trading.accept_trade(offer.trade_id, self.player2)

        history = self.trading.get_trade_history_for_player(self.player1)

        self.assertEqual(len(history), 1)
        self.assertEqual(history[0].player1_id, self.player1)

    def test_purchase_insurance(self):
        """Test purchasing trade insurance."""
        item1 = TradeItem("legendary_sword", "Legendary Sword", 1, ItemRarity.LEGENDARY, 10000)

        offer = self.trading.create_trade_offer(self.player1, self.player2, [item1], [])

        insurance, msg = self.trading.purchase_trade_insurance(
            offer.trade_id,
            10000,
            self.player1
        )

        self.assertIsNotNone(insurance)
        self.assertEqual(insurance.insured_value, 10000)
        self.assertEqual(insurance.premium_paid, 500)  # 5%

    def test_get_trending_items(self):
        """Test getting trending items."""
        sword = TradeItem("sword", "Sword", 1, ItemRarity.COMMON, 100)
        shield = TradeItem("shield", "Shield", 1, ItemRarity.COMMON, 50)

        # Complete multiple trades
        for i in range(5):
            offer = self.trading.create_trade_offer(
                self.player1,
                self.player2,
                [sword],
                []
            )
            self.trading.accept_trade(offer.trade_id, self.player2)

        for i in range(2):
            offer = self.trading.create_trade_offer(
                self.player1,
                self.player2,
                [shield],
                []
            )
            self.trading.accept_trade(offer.trade_id, self.player2)

        trending = self.trading.get_trending_items(limit=2)

        self.assertEqual(trending[0][0], "Sword")
        self.assertEqual(trending[0][1], 5)

    def test_get_market_price(self):
        """Test getting market price."""
        item1 = TradeItem("sword", "Sword", 1, ItemRarity.COMMON, 100)
        item2 = TradeItem("sword", "Sword", 1, ItemRarity.COMMON, 120)

        # Complete trades with different prices
        offer1 = self.trading.create_trade_offer(self.player1, self.player2, [item1], [])
        self.trading.accept_trade(offer1.trade_id, self.player2)

        offer2 = self.trading.create_trade_offer(self.player1, self.player2, [item2], [])
        self.trading.accept_trade(offer2.trade_id, self.player2)

        market_price = self.trading.get_market_price("Sword")

        self.assertIsNotNone(market_price)
        self.assertEqual(market_price, 110)  # Average of 100 and 120

    def test_generate_trade_report(self):
        """Test generating trade report."""
        item = TradeItem("item", "Item", 1, ItemRarity.COMMON, 100)

        offer = self.trading.create_trade_offer(
            self.player1,
            self.player2,
            [item],
            [],
            sender_gold=100
        )
        self.trading.accept_trade(offer.trade_id, self.player2)

        report = self.trading.generate_trade_report(self.player1)

        self.assertIn("reputation_score", report)
        self.assertIn("successful_trades", report)
        self.assertEqual(report["successful_trades"], 1)

    def test_cleanup_expired_trades(self):
        """Test cleaning up expired trades."""
        item = TradeItem("item", "Item", 1, ItemRarity.COMMON, 100)

        offer = self.trading.create_trade_offer(self.player1, self.player2, [item], [])

        # Manually expire trade
        offer.expires_time = int(time.time()) - 1

        expired = self.trading.cleanup_expired_trades()

        self.assertEqual(expired, 1)
        self.assertEqual(offer.status, TradeStatus.EXPIRED)


if __name__ == "__main__":
    unittest.main()
