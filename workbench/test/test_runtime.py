"""Test Workbench Runtime"""

from unittest import TestCase

from xblock.fields import Scope
from xblock.runtime import KeyValueStore
from ..runtime import ScenarioIdManager, WorkbenchDjangoKeyValueStore


class TestScenarioIds(TestCase):

    def setUp(self):
        # Test basic ID generation meets our expectations
        self.id_mgr = ScenarioIdManager()

    def test_no_scenario_loaded(self):
        self.assertEqual(self.id_mgr.create_definition("my_block"), ".my_block.d0")

    def test_should_increment(self):
        self.assertEqual(self.id_mgr.create_definition("my_block"), ".my_block.d0")
        self.assertEqual(self.id_mgr.create_definition("my_block"), ".my_block.d1")

    def test_slug_support(self):
        self.assertEqual(
            self.id_mgr.create_definition("my_block", "my_slug"),
            ".my_block.my_slug.d0"
        )
        self.assertEqual(
            self.id_mgr.create_definition("my_block", "my_slug"),
            ".my_block.my_slug.d1"
        )

    def test_scenario_support(self):
        self.test_should_increment()

        # Now that we have a scenario, our definition numbering starts over again.
        self.id_mgr.set_scenario("my_scenario")
        self.assertEqual(self.id_mgr.create_definition("my_block"), "my_scenario.my_block.d0")
        self.assertEqual(self.id_mgr.create_definition("my_block"), "my_scenario.my_block.d1")

        self.id_mgr.set_scenario("another_scenario")
        self.assertEqual(self.id_mgr.create_definition("my_block"), "another_scenario.my_block.d0")

    def test_usages(self):
        # Now make sure our usages are attached to definitions
        self.assertIsNone(self.id_mgr.last_created_usage_id())
        self.assertEqual(
            self.id_mgr.create_usage("my_scenario.my_block.d0"),
            "my_scenario.my_block.d0.u0"
        )
        self.assertEqual(
            self.id_mgr.create_usage("my_scenario.my_block.d0"),
            "my_scenario.my_block.d0.u1"
        )
        self.assertEqual(self.id_mgr.last_created_usage_id(), "my_scenario.my_block.d0.u1")

    def test_asides(self):
        definition_id = self.id_mgr.create_definition('my_block')
        usage_id = self.id_mgr.create_usage(definition_id)

        aside_definition, aside_usage = self.id_mgr.create_aside(definition_id, usage_id, 'my_aside')

        self.assertEqual(self.id_mgr.get_aside_type_from_definition(aside_definition), 'my_aside')
        self.assertEqual(self.id_mgr.get_definition_id_from_aside(aside_definition), definition_id)
        self.assertEqual(self.id_mgr.get_aside_type_from_usage(aside_usage), 'my_aside')
        self.assertEqual(self.id_mgr.get_usage_id_from_aside(aside_usage), usage_id)


class TestKVStore(TestCase):
    def setUp(self):
        self.kvs = WorkbenchDjangoKeyValueStore()
        self.key = KeyValueStore.Key(
            scope=Scope.content,
            user_id="rusty",
            block_scope_id="my_scenario.my_block.d0",
            field_name="age"
        )

    def test_storage(self):
        self.assertFalse(self.kvs.has(self.key))
        self.kvs.set(self.key, 7)
        self.assertTrue(self.kvs.has(self.key))
        self.assertEqual(self.kvs.get(self.key), 7)
        self.kvs.delete(self.key)
        self.assertFalse(self.kvs.has(self.key))
