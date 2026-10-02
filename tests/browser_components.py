import argparse
import functools
import http.server
import importlib.util
import json
import pathlib
import tempfile
import threading
import time
from jinja2 import Environment, FileSystemLoader, StrictUndefined
from playwright.sync_api import sync_playwright

root = pathlib.Path(__file__).resolve().parents[1]
parser = argparse.ArgumentParser(
    description="Optional Chromium proof of vendored reference components."
)
parser.add_argument(
    "--artifacts", type=pathlib.Path, help="directory for screenshots and results"
)
args = parser.parse_args()
artifacts = args.artifacts or pathlib.Path(
    tempfile.mkdtemp(prefix="patina-components-proof-")
)
artifacts.mkdir(parents=True, exist_ok=True)
spec = importlib.util.spec_from_file_location(
    "component_fixtures", root / "scripts/selftest_components.py"
)
module = importlib.util.module_from_spec(spec)
spec.loader.exec_module(module)
ComponentChecks = module.ComponentChecks
fixture = ComponentChecks()
fixture.setUp()
results = []
server = None
try:
    proc = fixture.sync()
    assert proc.returncode == 0, proc.stderr
    assert not fixture.check().failures
    env = Environment(
        loader=FileSystemLoader([str(fixture.templates), str(root)]),
        autoescape=True,
        undefined=StrictUndefined,
    )
    template = env.get_template("examples/components.html.j2")
    rows = [
        (
            f"Object {n:02}",
            "Needs review" if n <= 3 else "Scheduled" if n <= 7 else "Current",
            "Example team",
        )
        for n in range(1, 13)
    ]
    cases = {
        "normal": ("normal", "all", rows),
        "attention": ("normal", "attention", rows[:3]),
        "scheduled": ("normal", "scheduled", rows[3:7]),
        "empty": ("empty", "all", []),
        "loading": ("loading", "all", []),
        "error": ("error", "all", []),
        "long": (
            "normal",
            "all",
            [("Object-" + ("x" * 160), "Unknown", "Owner-" + ("y" * 120))],
        ),
        "wide": ("normal", "all", [tuple(f"Value {n:02}" for n in range(12))]),
    }
    for name, (state, scope, shown) in cases.items():
        (fixture.static / (name + ".html")).write_text(
            template.render(
                state=state,
                scope=scope,
                rows=shown,
                headers=[f"Column {n:02}" for n in range(12)]
                if name == "wide"
                else ["Name", "State", "Owner"],
            )
        )
    proc = fixture.run_gate("--update-ratchet")
    assert proc.returncode == 0, proc.stdout + proc.stderr
    proc = fixture.run_gate("--upstream", str(fixture.upstream))
    assert proc.returncode == 0, proc.stdout + proc.stderr

    class Handler(http.server.SimpleHTTPRequestHandler):
        def log_message(self, *args):
            pass

    server = http.server.ThreadingHTTPServer(
        ("127.0.0.1", 0), functools.partial(Handler, directory=str(fixture.static))
    )
    threading.Thread(target=server.serve_forever, daemon=True).start()
    base = f"http://127.0.0.1:{server.server_port}"
    with sync_playwright() as p:
        browser = p.chromium.launch()
        for width in [1280, 720, 375, 320]:
            for name, (state, scope, shown) in cases.items():
                context = browser.new_context(viewport={"width": width, "height": 900})
                page = context.new_page()
                errors = []
                page.on("pageerror", lambda e: errors.append(str(e)))
                page.on(
                    "console",
                    lambda m: errors.append(m.text) if m.type == "error" else None,
                )
                page.goto(base + "/" + name + ".html")
                page.evaluate("document.fonts.ready")
                for theme in ["dark", "light"]:
                    assert page.locator("html").get_attribute("data-theme") == theme
                    assert page.evaluate(
                        "document.documentElement.scrollWidth<=innerWidth"
                    ), (width, name, theme, "document overflow")
                    assert page.locator(".pt-page").evaluate(
                        "(el)=>el.scrollWidth<=el.clientWidth+1"
                    ), (width, name, theme, "page overflow")
                    control = page.get_by_role(
                        "textbox", name="Object name", exact=True
                    )
                    assert control.count() == 1
                    assert page.get_by_label("No choices yet", exact=True).is_disabled()
                    assert page.get_by_role(
                        "button", name="Saving", exact=True
                    ).is_disabled()
                    assert page.get_by_role(
                        "button", name="Unavailable", exact=True
                    ).is_disabled()
                    heights = [
                        page.locator(selector).evaluate(
                            "(el)=>el.getBoundingClientRect().height"
                        )
                        for selector in [
                            "#object-name",
                            "#object-state",
                            "#save-example",
                        ]
                    ]
                    assert heights == [36, 36, 36], heights
                    if name == "wide" and width <= 720:
                        region = page.get_by_role("region", name="Object inventory")
                        assert region.evaluate("(el)=>el.scrollWidth>el.clientWidth")
                        region.focus()
                        region.press("ArrowRight")
                        deadline = time.monotonic() + 2
                        while time.monotonic() < deadline:
                            if region.evaluate("(el)=>el.scrollLeft") > 0:
                                break
                            page.wait_for_timeout(50)
                        assert region.evaluate("(el)=>el.scrollLeft") > 0
                    if state == "normal":
                        assert page.locator(".pt-table tbody tr").count() == len(shown)
                    else:
                        assert page.locator(".pt-table tbody tr").count() == 1
                        expected = {
                            "empty": "No data yet",
                            "loading": "Loading data",
                            "error": "Unable to load data",
                        }[state]
                        assert expected in page.locator(".pt-table tbody").inner_text()
                        if state == "loading":
                            assert (
                                page.locator(".pt-table-wrap").get_attribute(
                                    "aria-busy"
                                )
                                == "true"
                            )
                        if state == "error":
                            assert (
                                page.locator(".pt-table tbody [role=alert]").count()
                                == 1
                            )
                    if name == "normal":
                        before = page.locator("#object-name").evaluate(
                            "(el)=>({control:el.getBoundingClientRect().height,field:el.parentElement.getBoundingClientRect().height,border:getComputedStyle(el).borderTopWidth})"
                        )
                        page.locator("#object-name-error").evaluate(
                            '(el)=>el.textContent="Required"'
                        )
                        control.evaluate('(el)=>el.setAttribute("aria-invalid","true")')
                        after = control.evaluate(
                            "(el)=>({control:el.getBoundingClientRect().height,field:el.parentElement.getBoundingClientRect().height,border:getComputedStyle(el).borderTopWidth})"
                        )
                        assert before == after, (before, after)
                        page.locator("#object-name-error").evaluate(
                            '(el)=>el.textContent=""'
                        )
                        control.evaluate(
                            '(el)=>el.setAttribute("aria-invalid","false")'
                        )
                        page.locator("label[for=object-name]").click()
                        assert control.evaluate("(el)=>el===document.activeElement")
                        control.fill("")
                        page.get_by_role(
                            "button", name="Save example", exact=True
                        ).click()
                        assert control.evaluate("(el)=>!el.validity.valid")
                        assert page.url.endswith("/normal.html"), page.url
                        control.fill("Example object")
                        page.get_by_label(
                            "Choose a backup file", exact=True
                        ).set_input_files(
                            {
                                "name": "example.json",
                                "mimeType": "application/json",
                                "buffer": b'{"sample":true}\n',
                            }
                        )
                        assert (
                            page.locator("#backup-file").evaluate(
                                "(el)=>el.files[0].name"
                            )
                            == "example.json"
                        )
                    if width in [1280, 375] and name in ["normal", "empty", "error"]:
                        page.locator(".pt-page").evaluate("(el)=>el.scrollTop=0")
                        page.screenshot(
                            path=str(artifacts / f"{name}-{theme}-{width}.png")
                        )
                    assert not errors, errors
                    results.append(
                        {"width": width, "case": name, "theme": theme, "ok": True}
                    )
                    print("PASS", width, name, theme, flush=True)
                    if theme == "dark":
                        page.get_by_role(
                            "button", name="Switch to light theme", exact=True
                        ).click()
                        assert (
                            page.get_by_role(
                                "button", name="Switch to dark theme", exact=True
                            ).count()
                            == 1
                        )
                if name == "normal":
                    page.get_by_role(
                        "link", name="Needs attention", exact=False
                    ).click()
                    assert page.url.endswith("/attention.html")
                    assert page.locator(".pt-table tbody tr").count() == 3
                    assert (
                        page.locator(".pt-stat.active").get_attribute("href")
                        == "/attention.html"
                    )
                    page.get_by_role("link", name="Scheduled", exact=False).click()
                    assert page.url.endswith("/scheduled.html")
                    assert page.locator(".pt-table tbody tr").count() == 4
                    assert (
                        page.locator(".pt-stat.active").get_attribute("href")
                        == "/scheduled.html"
                    )
                context.close()
        browser.close()
    (artifacts / "results.json").write_text(json.dumps(results, indent=2))
    print(f"{len(results)}/{len(results)} passed; artifacts: {artifacts}")
finally:
    if server is not None:
        server.shutdown()
    fixture.doCleanups()
