#!/usr/bin/env node
"use strict";

var fs = require("fs");
var path = require("path");
var vm = require("vm");

var source = fs.readFileSync(path.join(__dirname, "..", "theme.js"), "utf8");

function fail(message) {
  throw new Error(message);
}

function equal(actual, expected, message) {
  if (actual !== expected) {
    fail(message + ": expected " + expected + ", got " + actual);
  }
}

function element() {
  return {
    style: {},
    listeners: {},
    addEventListener: function (name, listener) {
      this.listeners[name] = listener;
    }
  };
}

function run(options) {
  options = options || {};
  var attributes = options.attributes || {};
  var root = {
    getAttribute: function (name) { return attributes[name] || null; },
    setAttribute: function (name, value) { attributes[name] = value; }
  };
  var elements = options.elements || {};
  var documentListeners = {};
  var document = {
    documentElement: root,
    readyState: options.readyState || "complete",
    getElementById: function (id) { return elements[id] || null; },
    addEventListener: function (name, listener) { documentListeners[name] = listener; }
  };
  vm.runInNewContext(source, { document: document, localStorage: options.storage });
  return {
    attributes: attributes,
    elements: elements,
    documentListeners: documentListeners,
    fireDOMContentLoaded: function () {
      documentListeners.DOMContentLoaded();
    }
  };
}

function storage(initial) {
  var values = initial || {};
  return {
    getCalls: [],
    setCalls: [],
    getItem: function (key) {
      this.getCalls.push(key);
      return values[key] || null;
    },
    setItem: function (key, value) {
      this.setCalls.push([key, value]);
      values[key] = value;
    },
    values: values
  };
}

(function () {
  var result = run({ storage: storage() });
  equal(result.attributes["data-theme"], "dark", "default theme");
})();

(function () {
  var button = element();
  var darkIcon = element();
  var lightIcon = element();
  var store = storage({ "tool-theme": "light" });
  var result = run({
    attributes: { "data-theme-key": "tool-theme" },
    storage: store,
    readyState: "loading",
    elements: {
      "theme-toggle": button,
      "theme-icon-dark": darkIcon,
      "theme-icon-light": lightIcon
    }
  });
  equal(result.attributes["data-theme"], "light", "persisted theme before DOMContentLoaded");
  equal(typeof result.documentListeners.DOMContentLoaded, "function", "DOMContentLoaded registration");
  equal(button.listeners.click, undefined, "toggle is not wired before DOMContentLoaded");
  equal(darkIcon.style.display, undefined, "icons are not initialized before DOMContentLoaded");
  result.fireDOMContentLoaded();
  equal(darkIcon.style.display, "block", "dark icon after DOMContentLoaded");
  equal(lightIcon.style.display, "none", "light icon after DOMContentLoaded");
  equal(store.getCalls[0], "tool-theme", "custom key used to get persisted theme");
  button.listeners.click();
  equal(store.setCalls[0][0], "tool-theme", "custom key used to persist theme");
  equal(store.setCalls[0][1], "dark", "persisted custom-key toggle");
})();

(function () {
  var button = element();
  var darkIcon = element();
  var lightIcon = element();
  var store = storage();
  var result = run({
    storage: store,
    elements: {
      "theme-toggle": button,
      "theme-icon-dark": darkIcon,
      "theme-icon-light": lightIcon
    }
  });
  equal(darkIcon.style.display, "none", "dark icon before toggle");
  equal(lightIcon.style.display, "block", "light icon before toggle");
  button.listeners.click();
  equal(result.attributes["data-theme"], "light", "theme after toggle");
  equal(store.values["patina-theme"], "light", "persisted toggled theme");
  equal(darkIcon.style.display, "block", "dark icon after toggle");
  equal(lightIcon.style.display, "none", "light icon after toggle");
})();

(function () {
  var button = element();
  var brokenStorage = {
    getItem: function () { throw new Error("blocked"); },
    setItem: function () { throw new Error("blocked"); }
  };
  var result = run({
    storage: brokenStorage,
    elements: { "theme-toggle": button }
  });
  equal(result.attributes["data-theme"], "dark", "storage failure fallback");
  button.listeners.click();
  equal(result.attributes["data-theme"], "light", "toggle after storage failure");
})();

(function () {
  var result = run({ storage: storage(), readyState: "loading" });
  equal(result.attributes["data-theme"], "dark", "missing toggle");
  result.fireDOMContentLoaded();
})();

console.log("test-theme: passed");
