from __future__ import absolute_import, print_function, unicode_literals

from django.core.exceptions import ValidationError
from django.db import models
from django.test import TestCase

from ..helpers.models import OrderedModel, check_model_is_unique_with_conditions, unique_slugify


class TestModel(OrderedModel):
    fk = models.PositiveIntegerField(db_index=True)
    name = models.CharField(max_length=100, unique=True)
    slug = models.CharField(max_length=10)

    class Meta:
        order_within_fields = ("fk",)
        ordering = ("ordering", "name")
        app_label = "helpers"

    def __str__(self):
        return "(id={}) {}: {}".format(self.id, self.name, self.ordering)


class OrderedModelTestCase(TestCase):
    def setUp(self):
        self.lut = {}
        self.add_item(1, 1)
        self.add_item(1, 2)
        self.add_item(1, 3)
        self.add_item(1, 4)
        self.add_item(1, 5)
        self.add_item(2, 1)
        self.add_item(2, 2)
        self.add_item(2, 3)

    def tearDown(self):
        pass

    def dump_all(self):
        for item in TestModel.objects.all():
            print(item)

    def add_item(self, fk, num, ordering=None):
        name = "{}-{}".format(fk, num)
        self.lut[name] = TestModel.objects.create(fk=fk, name=name, ordering=ordering)

    def test_inserting(self):
        for i, item in enumerate(TestModel.objects.filter(fk=1), start=1):
            self.assertEqual(item.ordering, i * 100)

        for i, item in enumerate(TestModel.objects.filter(fk=2), start=1):
            self.assertEqual(item.ordering, i * 100)

    def test_rebalancing(self):
        for item in TestModel.objects.all():
            item.ordering = item.id
            item.save()

        TestModel.objects.rebalance_ordering(fk=1)

        self.assertEqual(TestModel.objects.get(name="1-1").ordering, 100)
        self.assertEqual(TestModel.objects.get(name="1-2").ordering, 200)
        self.assertEqual(TestModel.objects.get(name="1-3").ordering, 300)
        self.assertEqual(TestModel.objects.get(name="1-4").ordering, 400)
        self.assertEqual(TestModel.objects.get(name="1-5").ordering, 500)

    def test_reorder_cross_fk(self):
        with self.assertRaises(AssertionError):
            TestModel.objects.reorder(self.lut["1-1"], self.lut["2-2"])

    def test_reorder_1elem(self):
        self.add_item(3, 1)
        TestModel.objects.reorder(self.lut["3-1"], None)
        self.assertEqual(TestModel.objects.get(name="3-1").ordering, 100)

        TestModel.objects.reorder(self.lut["3-1"], self.lut["3-1"])
        self.assertEqual(TestModel.objects.get(name="3-1").ordering, 100)

    def test_reorder_mid2first(self):
        TestModel.objects.reorder(self.lut["1-3"], self.lut["1-1"])
        self.assertEqual(TestModel.objects.get(name="1-1").ordering, 100)
        self.assertEqual(TestModel.objects.get(name="1-2").ordering, 200)
        self.assertEqual(TestModel.objects.get(name="1-3").ordering, 50)
        self.assertEqual(TestModel.objects.get(name="1-4").ordering, 400)
        self.assertEqual(TestModel.objects.get(name="1-5").ordering, 500)
        self.assertEqual(TestModel.objects.get(name="2-1").ordering, 100)
        self.assertEqual(TestModel.objects.get(name="2-2").ordering, 200)
        self.assertEqual(TestModel.objects.get(name="2-3").ordering, 300)

    def test_reorder_end2first(self):
        TestModel.objects.reorder(self.lut["1-5"], self.lut["1-1"])
        self.assertEqual(TestModel.objects.get(name="1-1").ordering, 100)
        self.assertEqual(TestModel.objects.get(name="1-2").ordering, 200)
        self.assertEqual(TestModel.objects.get(name="1-3").ordering, 300)
        self.assertEqual(TestModel.objects.get(name="1-4").ordering, 400)
        self.assertEqual(TestModel.objects.get(name="1-5").ordering, 50)
        self.assertEqual(TestModel.objects.get(name="2-1").ordering, 100)
        self.assertEqual(TestModel.objects.get(name="2-2").ordering, 200)
        self.assertEqual(TestModel.objects.get(name="2-3").ordering, 300)

    def test_reorder_first2first(self):
        TestModel.objects.reorder(self.lut["1-1"], self.lut["1-1"])
        self.assertEqual(TestModel.objects.get(name="1-1").ordering, 100)
        self.assertEqual(TestModel.objects.get(name="1-2").ordering, 200)
        self.assertEqual(TestModel.objects.get(name="1-3").ordering, 300)
        self.assertEqual(TestModel.objects.get(name="1-4").ordering, 400)
        self.assertEqual(TestModel.objects.get(name="1-5").ordering, 500)
        self.assertEqual(TestModel.objects.get(name="2-1").ordering, 100)
        self.assertEqual(TestModel.objects.get(name="2-2").ordering, 200)
        self.assertEqual(TestModel.objects.get(name="2-3").ordering, 300)

    def test_reorder_mid2end(self):
        TestModel.objects.reorder(self.lut["1-3"], self.lut["1-5"])
        self.assertEqual(TestModel.objects.get(name="1-1").ordering, 100)
        self.assertEqual(TestModel.objects.get(name="1-2").ordering, 200)
        self.assertEqual(TestModel.objects.get(name="1-3").ordering, 600)
        self.assertEqual(TestModel.objects.get(name="1-4").ordering, 400)
        self.assertEqual(TestModel.objects.get(name="1-5").ordering, 500)
        self.assertEqual(TestModel.objects.get(name="2-1").ordering, 100)
        self.assertEqual(TestModel.objects.get(name="2-2").ordering, 200)
        self.assertEqual(TestModel.objects.get(name="2-3").ordering, 300)

    def test_reorder_mid2none(self):
        TestModel.objects.reorder(self.lut["1-3"], None)
        self.assertEqual(TestModel.objects.get(name="1-1").ordering, 100)
        self.assertEqual(TestModel.objects.get(name="1-2").ordering, 200)
        self.assertEqual(TestModel.objects.get(name="1-3").ordering, 600)
        self.assertEqual(TestModel.objects.get(name="1-4").ordering, 400)
        self.assertEqual(TestModel.objects.get(name="1-5").ordering, 500)
        self.assertEqual(TestModel.objects.get(name="2-1").ordering, 100)
        self.assertEqual(TestModel.objects.get(name="2-2").ordering, 200)
        self.assertEqual(TestModel.objects.get(name="2-3").ordering, 300)

    def test_reorder_end2end(self):
        TestModel.objects.reorder(self.lut["1-5"], self.lut["1-5"])
        self.assertEqual(TestModel.objects.get(name="1-1").ordering, 100)
        self.assertEqual(TestModel.objects.get(name="1-2").ordering, 200)
        self.assertEqual(TestModel.objects.get(name="1-3").ordering, 300)
        self.assertEqual(TestModel.objects.get(name="1-4").ordering, 400)
        self.assertEqual(TestModel.objects.get(name="1-5").ordering, 500)
        self.assertEqual(TestModel.objects.get(name="2-1").ordering, 100)
        self.assertEqual(TestModel.objects.get(name="2-2").ordering, 200)
        self.assertEqual(TestModel.objects.get(name="2-3").ordering, 300)

    def test_reorder_end2none(self):
        TestModel.objects.reorder(self.lut["1-5"], None)
        self.assertEqual(TestModel.objects.get(name="1-1").ordering, 100)
        self.assertEqual(TestModel.objects.get(name="1-2").ordering, 200)
        self.assertEqual(TestModel.objects.get(name="1-3").ordering, 300)
        self.assertEqual(TestModel.objects.get(name="1-4").ordering, 400)
        self.assertEqual(TestModel.objects.get(name="1-5").ordering, 500)
        self.assertEqual(TestModel.objects.get(name="2-1").ordering, 100)
        self.assertEqual(TestModel.objects.get(name="2-2").ordering, 200)
        self.assertEqual(TestModel.objects.get(name="2-3").ordering, 300)

    def test_reorder_first2end(self):
        TestModel.objects.reorder(self.lut["1-1"], self.lut["1-5"])
        self.assertEqual(TestModel.objects.get(name="1-1").ordering, 600)
        self.assertEqual(TestModel.objects.get(name="1-2").ordering, 200)
        self.assertEqual(TestModel.objects.get(name="1-3").ordering, 300)
        self.assertEqual(TestModel.objects.get(name="1-4").ordering, 400)
        self.assertEqual(TestModel.objects.get(name="1-5").ordering, 500)
        self.assertEqual(TestModel.objects.get(name="2-1").ordering, 100)
        self.assertEqual(TestModel.objects.get(name="2-2").ordering, 200)
        self.assertEqual(TestModel.objects.get(name="2-3").ordering, 300)

    def test_reorder_first2none(self):
        TestModel.objects.reorder(self.lut["1-1"], None)
        self.assertEqual(TestModel.objects.get(name="1-1").ordering, 600)
        self.assertEqual(TestModel.objects.get(name="1-2").ordering, 200)
        self.assertEqual(TestModel.objects.get(name="1-3").ordering, 300)
        self.assertEqual(TestModel.objects.get(name="1-4").ordering, 400)
        self.assertEqual(TestModel.objects.get(name="1-5").ordering, 500)
        self.assertEqual(TestModel.objects.get(name="2-1").ordering, 100)
        self.assertEqual(TestModel.objects.get(name="2-2").ordering, 200)
        self.assertEqual(TestModel.objects.get(name="2-3").ordering, 300)

    def test_reorder_up(self):
        TestModel.objects.reorder(self.lut["1-4"], self.lut["1-2"])
        self.assertEqual(TestModel.objects.get(name="1-1").ordering, 100)
        self.assertEqual(TestModel.objects.get(name="1-2").ordering, 200)
        self.assertEqual(TestModel.objects.get(name="1-3").ordering, 300)
        self.assertEqual(TestModel.objects.get(name="1-4").ordering, 150)
        self.assertEqual(TestModel.objects.get(name="1-5").ordering, 500)
        self.assertEqual(TestModel.objects.get(name="2-1").ordering, 100)
        self.assertEqual(TestModel.objects.get(name="2-2").ordering, 200)
        self.assertEqual(TestModel.objects.get(name="2-3").ordering, 300)

    def test_reorder_down(self):
        TestModel.objects.reorder(self.lut["1-2"], self.lut["1-4"])
        self.assertEqual(TestModel.objects.get(name="1-1").ordering, 100)
        self.assertEqual(TestModel.objects.get(name="1-2").ordering, 450)
        self.assertEqual(TestModel.objects.get(name="1-3").ordering, 300)
        self.assertEqual(TestModel.objects.get(name="1-4").ordering, 400)
        self.assertEqual(TestModel.objects.get(name="1-5").ordering, 500)
        self.assertEqual(TestModel.objects.get(name="2-1").ordering, 100)
        self.assertEqual(TestModel.objects.get(name="2-2").ordering, 200)
        self.assertEqual(TestModel.objects.get(name="2-3").ordering, 300)

    def test_moveup(self):
        TestModel.objects.moveup(self.lut["1-5"])
        self.assertEqual(TestModel.objects.get(name="1-5").ordering, 350)
        TestModel.objects.moveup(self.lut["1-5"])
        self.assertEqual(TestModel.objects.get(name="1-5").ordering, 250)
        TestModel.objects.moveup(self.lut["1-5"])
        self.assertEqual(TestModel.objects.get(name="1-5").ordering, 150)
        TestModel.objects.moveup(self.lut["1-5"])
        self.assertEqual(TestModel.objects.get(name="1-5").ordering, 50)
        TestModel.objects.moveup(self.lut["1-5"])
        self.assertEqual(TestModel.objects.get(name="1-5").ordering, 50)

    def test_movedown(self):
        TestModel.objects.movedown(self.lut["1-1"])
        self.assertEqual(TestModel.objects.get(name="1-1").ordering, 250)
        TestModel.objects.movedown(self.lut["1-1"])
        self.assertEqual(TestModel.objects.get(name="1-1").ordering, 350)
        TestModel.objects.movedown(self.lut["1-1"])
        self.assertEqual(TestModel.objects.get(name="1-1").ordering, 450)
        TestModel.objects.movedown(self.lut["1-1"])
        self.assertEqual(TestModel.objects.get(name="1-1").ordering, 600)
        TestModel.objects.movedown(self.lut["1-1"])
        self.assertEqual(TestModel.objects.get(name="1-1").ordering, 600)

    def test_moveto_down(self):
        TestModel.objects.moveto(self.lut["1-1"], -1)
        self.assertEqual(TestModel.objects.get(name="1-1").ordering, 100)
        TestModel.objects.moveto(self.lut["1-1"], 0)
        self.assertEqual(TestModel.objects.get(name="1-1").ordering, 100)
        TestModel.objects.moveto(self.lut["1-1"], 1)
        self.assertEqual(TestModel.objects.get(name="1-1").ordering, 250)
        TestModel.objects.moveto(self.lut["1-1"], 2)
        self.assertEqual(TestModel.objects.get(name="1-1").ordering, 350)
        TestModel.objects.moveto(self.lut["1-1"], 3)
        self.assertEqual(TestModel.objects.get(name="1-1").ordering, 450)
        TestModel.objects.moveto(self.lut["1-1"], 4)
        self.assertEqual(TestModel.objects.get(name="1-1").ordering, 600)
        TestModel.objects.moveto(self.lut["1-1"], 5)
        self.assertEqual(TestModel.objects.get(name="1-1").ordering, 600)

    def test_moveto_up(self):
        TestModel.objects.moveto(self.lut["1-5"], 5)
        self.assertEqual(TestModel.objects.get(name="1-5").ordering, 500)
        TestModel.objects.moveto(self.lut["1-5"], 4)
        self.assertEqual(TestModel.objects.get(name="1-5").ordering, 500)
        TestModel.objects.moveto(self.lut["1-5"], 3)
        self.assertEqual(TestModel.objects.get(name="1-5").ordering, 350)
        TestModel.objects.moveto(self.lut["1-5"], 2)
        self.assertEqual(TestModel.objects.get(name="1-5").ordering, 250)
        TestModel.objects.moveto(self.lut["1-5"], 1)
        self.assertEqual(TestModel.objects.get(name="1-5").ordering, 150)
        TestModel.objects.moveto(self.lut["1-5"], 0)
        self.assertEqual(TestModel.objects.get(name="1-5").ordering, 50)
        TestModel.objects.moveto(self.lut["1-5"], -1)
        self.assertEqual(TestModel.objects.get(name="1-5").ordering, 50)

    def test_moveto_end(self):
        TestModel.objects.moveto(self.lut["1-3"], None)
        self.assertEqual(TestModel.objects.get(name="1-3").ordering, 600)

    def test_moveto_equal_ordering(self):
        TestModel.objects.filter(fk=1).delete()
        self.add_item(1, 1, 100)
        self.add_item(1, 2, 100)
        self.add_item(1, 3, 100)
        TestModel.objects.moveto(self.lut["1-1"], 0)
        self.assertEqual(TestModel.objects.get(name="1-1").ordering, 50)

        TestModel.objects.filter(fk=1).delete()
        self.add_item(1, 1, 100)
        self.add_item(1, 2, 100)
        self.add_item(1, 3, 100)
        TestModel.objects.moveto(self.lut["1-1"], 1)
        self.assertEqual(TestModel.objects.get(name="1-1").ordering, 250)

        TestModel.objects.filter(fk=1).delete()
        self.add_item(1, 1, 100)
        self.add_item(1, 2, 100)
        self.add_item(1, 3, 100)
        TestModel.objects.moveto(self.lut["1-1"], None)
        self.assertEqual(TestModel.objects.get(name="1-1").ordering, 200)

    def test_reorder_gaps(self):
        TestModel.objects.filter(fk=3).delete()
        self.add_item(3, 1, 5)
        self.add_item(3, 2, 7)
        self.add_item(3, 3, 9)
        TestModel.objects.reorder(self.lut["3-1"], self.lut["3-2"])
        self.assertEqual(TestModel.objects.get(name="3-1").ordering, 8)

        TestModel.objects.filter(fk=3).delete()
        self.add_item(3, 1, 5)
        self.add_item(3, 2, 8)
        self.add_item(3, 3, 11)
        TestModel.objects.reorder(self.lut["3-1"], self.lut["3-2"])
        self.assertEqual(TestModel.objects.get(name="3-1").ordering, 9)

        TestModel.objects.filter(fk=3).delete()
        self.add_item(3, 1, 4)
        self.add_item(3, 2, 8)
        self.add_item(3, 3, 12)
        TestModel.objects.reorder(self.lut["3-1"], self.lut["3-2"])
        self.assertEqual(TestModel.objects.get(name="3-1").ordering, 10)

    def test_reorder_with_balance(self):
        TestModel.objects.all().delete()
        self.add_item(1, 1, 999)
        self.add_item(2, 1, 888)
        self.add_item(3, 1, 5)
        self.add_item(3, 2, 6)
        self.add_item(3, 3, 7)
        TestModel.objects.reorder(self.lut["3-1"], self.lut["3-2"])
        self.assertEqual(TestModel.objects.get(name="3-1").ordering, 250)
        self.assertEqual(TestModel.objects.get(name="3-2").ordering, 200)
        self.assertEqual(TestModel.objects.get(name="3-3").ordering, 300)

        TestModel.objects.all().delete()
        self.add_item(1, 1, 999)
        self.add_item(2, 1, 888)
        self.add_item(3, 1, 1)
        self.add_item(3, 2, 2)
        self.add_item(3, 3, 3)
        TestModel.objects.reorder(self.lut["3-2"], self.lut["3-1"])
        self.assertEqual(TestModel.objects.get(name="3-1").ordering, 100)
        self.assertEqual(TestModel.objects.get(name="3-2").ordering, 50)
        self.assertEqual(TestModel.objects.get(name="3-3").ordering, 300)

    def test_check_model_is_unique_with_conditions(self):
        saved = TestModel.objects.first()
        unsaved = TestModel(fk=3, name="3-1", ordering=100)

        check_model_is_unique_with_conditions(saved, ("fk", "ordering"))
        check_model_is_unique_with_conditions(unsaved, ("fk", "ordering"))

        with self.assertRaises(ValidationError):
            saved.fk = 2
            check_model_is_unique_with_conditions(saved, ("fk", "ordering"))

        with self.assertRaises(ValidationError):
            unsaved.fk = 1
            check_model_is_unique_with_conditions(unsaved, ("fk", "ordering"), error_field="foo")

        check_model_is_unique_with_conditions(unsaved, ("fk", "ordering"), {"fk__gt": 1})

    def test_unique_slugify(self):
        instance1, instance2 = TestModel.objects.all()[:2]
        unique_slugify(instance1, "same slug long text")
        self.assertEqual(instance1.slug, "same-slug")
        instance1.save()

        unique_slugify(instance2, "same slug long text")
        self.assertEqual(instance2.slug, "same-slu-2")
