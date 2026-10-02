"""Template contract tests. Jinja is a test dependency, not a checker dependency.

Run: python3 -m unittest discover -s tests
Consumer applications already provide their Jinja environment; patina has no
installed Python package or build step.
"""

from html.parser import HTMLParser
from pathlib import Path
import unittest

from jinja2 import Environment, FileSystemLoader, StrictUndefined

ROOT = Path(__file__).resolve().parents[1]


class Tags(HTMLParser):
    def __init__(self, markup):
        super().__init__()
        self.nodes = []
        self.text = []
        self.feed(str(markup))

    def handle_starttag(self, tag, attrs):
        self.nodes.append((tag, dict(attrs)))

    def handle_data(self, data):
        self.text.append(data)

    def get(self, tag):
        return [attrs for name, attrs in self.nodes if name == tag]


class ReferenceMacros(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.env = Environment(
            loader=FileSystemLoader(str(ROOT)),
            undefined=StrictUndefined,
            autoescape=True,
        )
        cls.ui = cls.env.get_template("macros/ui.j2").module

    def test_plain_text_is_escaped_with_and_without_environment_autoescape(self):
        label = 'A < B & "quoted"'
        for enabled in (True, False):
            env = Environment(loader=FileSystemLoader(str(ROOT)), autoescape=enabled)
            ui = env.get_template("macros/ui.j2").module
            for output in (
                ui.pill(label),
                ui.chip(label),
                ui.callout(label),
                ui.button(label),
                ui.field("name", "name", label, value=label),
            ):
                with self.subTest(autoescape=enabled, output=str(output)[:30]):
                    parsed = Tags(output)
                    self.assertNotIn("A < B", str(output))
                    self.assertIn(label, "".join(parsed.text))
                    for tag, _attrs in parsed.nodes:
                        self.assertIn(tag, ("span", "div", "button", "label", "input"))

    def test_field_label_description_and_reserved_error_slot(self):
        parsed = Tags(
            self.ui.field("record", "record", "Record", help="Choose a record")
        )
        control = parsed.get("input")[0]
        self.assertEqual(parsed.get("label")[0]["for"], control["id"])
        self.assertEqual(control["aria-describedby"], "record-help record-error")
        self.assertEqual(control["aria-invalid"], "false")
        ids = {attrs.get("id") for _tag, attrs in parsed.nodes}
        self.assertTrue({"record-help", "record-error"} <= ids)
        self.assertIn("pt-error", [attrs.get("class") for attrs in parsed.get("span")])

    def test_field_error_keeps_the_same_control_and_slots(self):
        valid = Tags(self.ui.field("record", "record", "Record"))
        invalid = Tags(self.ui.field("record", "record", "Record", error="Required"))
        self.assertEqual(
            [tag for tag, _attrs in valid.nodes], [tag for tag, _attrs in invalid.nodes]
        )
        self.assertEqual(invalid.get("input")[0]["aria-invalid"], "true")
        self.assertIn("Required", "".join(invalid.text))

    def test_field_zero_is_a_value_and_none_is_empty(self):
        self.assertEqual(
            Tags(self.ui.field("n", "n", "Count", value=0)).get("input")[0]["value"],
            "0",
        )
        self.assertEqual(
            Tags(self.ui.field("n", "n", "Count", value=None)).get("input")[0]["value"],
            "",
        )

    def test_loading_controls_are_natively_disabled_and_marked_busy(self):
        for markup, tag in (
            (self.ui.button("Saving", loading=True), "button"),
            (self.ui.field("x", "x", "Name", loading=True), "input"),
            (self.ui.select("x", "x", "Name", [("a", "A")], loading=True), "select"),
            (self.ui.dropzone("x", "x", "Choose file", loading=True), "input"),
        ):
            with self.subTest(tag=tag):
                parsed = Tags(markup)
                self.assertIn("disabled", parsed.get(tag)[0])
                self.assertTrue(
                    any(attrs.get("aria-busy") == "true" for _, attrs in parsed.nodes)
                )

    def test_required_and_readonly_remain_native_semantics(self):
        control = Tags(
            self.ui.field("x", "x", "Name", required=True, readonly=True)
        ).get("input")[0]
        self.assertIn("required", control)
        self.assertIn("readonly", control)
        self.assertNotIn("disabled", control)

    def test_select_preserves_numeric_zero_selection(self):
        options = Tags(
            self.ui.select("n", "n", "Count", [(0, "None"), (1, "One")], selected=0)
        ).get("option")
        self.assertIn("selected", options[0])
        self.assertNotIn("selected", options[1])

    def test_empty_select_is_disabled_and_explains_why(self):
        parsed = Tags(self.ui.select("n", "n", "Count", []))
        self.assertIn("disabled", parsed.get("select")[0])
        self.assertIn("No options available", "".join(parsed.text))

    def test_buttons_require_an_explicit_valid_submit_type(self):
        for value in ("button", "unexpected"):
            self.assertEqual(
                Tags(self.ui.button("Action", type=value)).get("button")[0]["type"],
                "button",
            )
        self.assertEqual(
            Tags(self.ui.button("Save", type="submit")).get("button")[0]["type"],
            "submit",
        )

    def test_icon_button_has_an_action_name_and_hides_its_glyph(self):
        parsed = Tags(self.ui.icon_button("Switch theme", "T"))
        self.assertEqual(parsed.get("button")[0]["aria-label"], "Switch theme")
        self.assertEqual(parsed.get("span")[0]["aria-hidden"], "true")

    def test_status_never_uses_the_tool_accent(self):
        for tone in ("accent", "unknown"):
            self.assertEqual(
                Tags(self.ui.pill("Unknown", tone)).get("span")[0]["class"],
                "pt-pill neutral",
            )
        self.assertEqual(
            Tags(self.ui.chip("Category", "accent")).get("span")[0]["class"],
            "pt-chip accent",
        )

    def test_zero_and_unknown_scope_counts_remain_neutral(self):
        for value in (0, 0.0, "0", None):
            parsed = Tags(
                self.ui.stat("Needs attention", value, "/attention", tone="crit")
            )
            self.assertIn(
                "pt-stat-val", [attrs.get("class") for attrs in parsed.get("span")]
            )
            self.assertNotIn(
                "pt-stat-val crit", [attrs.get("class") for attrs in parsed.get("span")]
            )
        self.assertIn("Unknown", "".join(Tags(self.ui.stat("All", None, "/all")).text))

    def test_scope_links_have_real_routes_and_current_state(self):
        link = Tags(self.ui.stat("All", 12, "/all", active=True)).get("a")[0]
        self.assertEqual(link["href"], "/all")
        self.assertEqual(link["aria-current"], "true")
        self.assertEqual(Tags(self.ui.stat("All", 12, None)).get("a"), [])
        self.assertEqual(
            Tags(self.ui.stat("All", 12, "/all", disabled=True)).get("a"), []
        )

    def test_table_has_a_caption_and_column_headers(self):
        parsed = Tags(
            self.ui.table(["Name", "State"], [("Object", "Current")], "Inventory")
        )
        self.assertEqual(parsed.get("caption"), [{}])
        self.assertTrue(all(heading["scope"] == "col" for heading in parsed.get("th")))
        self.assertEqual(len(parsed.get("td")), 2)
        self.assertEqual(parsed.get("div")[0]["role"], "region")
        self.assertEqual(parsed.get("div")[0]["tabindex"], "0")

    def test_unknown_table_cells_remain_distinct_from_zero(self):
        parsed = Tags(
            self.ui.table(["Count", "Optional count"], [(0, None)], "Inventory")
        )
        self.assertIn("0", parsed.text)
        self.assertIn("Unknown", parsed.text)
        self.assertNotIn("None", parsed.text)

    def test_table_empty_loading_and_error_states_are_explicit(self):
        for state, role, text in (
            ("normal", None, "No data yet"),
            ("loading", "status", "Loading data"),
            ("error", "alert", "Unable to load data"),
        ):
            parsed = Tags(
                self.ui.table(["Name", "State"], [], "Inventory", state=state)
            )
            self.assertEqual(parsed.get("td")[0]["colspan"], "2")
            self.assertIn(text, "".join(parsed.text))
            if role:
                self.assertTrue(
                    any(attrs.get("role") == role for _, attrs in parsed.nodes)
                )

    def test_nav_active_disabled_and_empty_are_distinct(self):
        links = [("/records", "Records", True, False), ("/admin", "Admin", False, True)]
        parsed = Tags(self.ui.nav(links))
        self.assertEqual(
            parsed.get("a"),
            [{"href": "/records", "class": "active", "aria-current": "page"}],
        )
        self.assertEqual(Tags(self.ui.nav(links, state="empty")).get("a"), [])
        self.assertIn("No navigation items", "".join(Tags(self.ui.nav([])).text))

    def test_breadcrumb_last_item_is_the_current_page(self):
        parsed = Tags(self.ui.breadcrumb([("/home", "Home"), ("/here", "Here")]))
        self.assertEqual(parsed.get("a"), [{"href": "/home"}])
        self.assertEqual(parsed.get("span")[-1]["aria-current"], "page")
        self.assertEqual(str(self.ui.breadcrumb([])), "")

    def test_chain_is_ordered_and_supports_collection_states(self):
        parsed = Tags(self.ui.chain([("First", "Preferred"), ("Second", "Fallback")]))
        self.assertEqual(len(parsed.get("ol")), 1)
        self.assertEqual(len(parsed.get("li")), 2)
        self.assertIn("No data yet", "".join(Tags(self.ui.chain([])).text))
        self.assertTrue(
            any(
                attrs.get("role") == "alert"
                for _, attrs in Tags(self.ui.chain([], state="error")).nodes
            )
        )

    def test_callouts_only_announce_when_requested(self):
        normal = Tags(self.ui.callout("Problem", "crit"))
        self.assertNotIn("role", normal.get("div")[0])
        self.assertEqual(
            Tags(self.ui.callout("Problem", "crit", announce=True)).get("div")[0][
                "role"
            ],
            "alert",
        )

    def test_caller_markup_stays_markup_and_values_stay_text(self):
        template = self.env.from_string(
            '{% import "macros/ui.j2" as ui %}{% call ui.panel("Details") %}<p>{{ label }}</p>{% endcall %}'
        )
        parsed = Tags(template.render(label="A < B"))
        self.assertEqual(len(parsed.get("p")), 1)
        self.assertIn("A < B", "".join(parsed.text))

    def test_shipping_component_sources_are_ascii(self):
        for source in ("components.css", "macros/ui.j2"):
            self.assertTrue((ROOT / source).read_bytes().isascii())


if __name__ == "__main__":
    unittest.main()
