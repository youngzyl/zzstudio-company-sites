/* zzstudio — progressive enhancement.
   Nothing here is required for the page to read or navigate correctly. */
(function () {
  "use strict";

  var root = document.documentElement;
  var reduce = window.matchMedia("(prefers-reduced-motion: reduce)").matches;

  /* ------------------------------------------------ theme (light / dark) -- */

  var THEME_KEY = "zzstudio:theme";

  function storedTheme() {
    try { return localStorage.getItem(THEME_KEY); } catch (e) { return null; }
  }

  function applyTheme(value) {
    if (value === "light" || value === "dark") {
      root.setAttribute("data-theme", value);
    } else {
      root.removeAttribute("data-theme");
    }
    document.querySelectorAll("[data-theme-toggle]").forEach(function (btn) {
      var dark = value
        ? value === "dark"
        : window.matchMedia("(prefers-color-scheme: dark)").matches;
      btn.setAttribute("aria-pressed", String(dark));
      btn.setAttribute("aria-label", dark ? "Switch to light appearance" : "Switch to dark appearance");
    });
  }

  applyTheme(storedTheme());

  document.querySelectorAll("[data-theme-toggle]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var current = root.getAttribute("data-theme");
      var isDark = current
        ? current === "dark"
        : window.matchMedia("(prefers-color-scheme: dark)").matches;
      var next = isDark ? "light" : "dark";
      try { localStorage.setItem(THEME_KEY, next); } catch (e) { /* private mode */ }
      applyTheme(next);
    });
  });

  /* --------------------------------------------------------- mobile nav -- */

  var navToggle = document.querySelector("[data-nav-toggle]");
  var nav = document.querySelector("[data-nav]");

  function setNav(open) {
    if (!nav || !navToggle) return;
    nav.setAttribute("data-open", String(open));
    navToggle.setAttribute("aria-expanded", String(open));
  }

  if (navToggle && nav) {
    navToggle.addEventListener("click", function () {
      setNav(nav.getAttribute("data-open") !== "true");
    });
    nav.addEventListener("click", function (e) {
      if (e.target.closest("a")) setNav(false);
    });
    document.addEventListener("keydown", function (e) {
      if (e.key === "Escape") setNav(false);
    });
    document.addEventListener("click", function (e) {
      if (nav.getAttribute("data-open") !== "true") return;
      if (nav.contains(e.target) || navToggle.contains(e.target)) return;
      setNav(false);
    });
    window.addEventListener("resize", function () {
      if (window.innerWidth > 860) setNav(false);
    });
  }

  /* ------------------------------------------------------------- reveals -- */

  var revealables = document.querySelectorAll(".reveal");

  if (reduce || !("IntersectionObserver" in window)) {
    revealables.forEach(function (el) { el.classList.add("is-in"); });
  } else {
    var io = new IntersectionObserver(function (entries) {
      entries.forEach(function (entry) {
        if (!entry.isIntersecting) return;
        entry.target.classList.add("is-in");
        io.unobserve(entry.target);
      });
    }, { rootMargin: "0px 0px -8% 0px", threshold: 0.08 });

    revealables.forEach(function (el, i) {
      // stagger siblings inside the same parent for a calmer cascade
      el.style.transitionDelay = (i % 4) * 60 + "ms";
      io.observe(el);
    });
  }

  /* --------------------------------------------------- scroll progress -- */

  var bar = document.querySelector("[data-progress]");
  if (bar) {
    var ticking = false;
    var update = function () {
      var h = document.documentElement.scrollHeight - window.innerHeight;
      bar.style.transform = "scaleX(" + (h > 0 ? Math.min(1, window.scrollY / h) : 0) + ")";
      ticking = false;
    };
    window.addEventListener("scroll", function () {
      if (ticking) return;
      ticking = true;
      window.requestAnimationFrame(update);
    }, { passive: true });
    update();
  }

  /* ---------------------------------------------------------- copy chips -- */

  document.querySelectorAll("[data-copy]").forEach(function (btn) {
    btn.addEventListener("click", function () {
      var value = btn.getAttribute("data-copy");
      var done = function () {
        var original = btn.getAttribute("data-label") || btn.textContent;
        btn.setAttribute("data-label", original);
        btn.textContent = "Copied";
        window.setTimeout(function () { btn.textContent = original; }, 1600);
      };
      if (navigator.clipboard && navigator.clipboard.writeText) {
        navigator.clipboard.writeText(value).then(done, done);
      } else {
        var t = document.createElement("textarea");
        t.value = value;
        t.setAttribute("readonly", "");
        t.style.position = "absolute";
        t.style.left = "-9999px";
        document.body.appendChild(t);
        t.select();
        try { document.execCommand("copy"); } catch (e) { /* ignore */ }
        document.body.removeChild(t);
        done();
      }
    });
  });

  /* --------------------------------------------------------------- year -- */

  document.querySelectorAll("[data-year]").forEach(function (el) {
    el.textContent = String(new Date().getFullYear());
  });

  /* --------------------------------------------------------------- form -- */

  var form = document.querySelector("[data-contact-form]");
  if (form) {
    var status = form.querySelector("[data-form-status]");
    form.addEventListener("submit", function (e) {
      // No backend by design: hand the message to the visitor's mail client.
      e.preventDefault();
      var data = new FormData(form);
      var name = String(data.get("name") || "").trim();
      var email = String(data.get("email") || "").trim();
      var org = String(data.get("org") || "").trim();
      var topic = String(data.get("topic") || "").trim();
      var brief = String(data.get("brief") || "").trim();

      var subject = "zzstudio enquiry" + (topic ? " — " + topic : "");
      var lines = [
        brief,
        "",
        "—",
        "Name:  " + name,
        "Email: " + email,
        org ? "Org:   " + org : "",
        topic ? "Topic: " + topic : ""
      ].filter(Boolean).join("\n");

      var to = form.getAttribute("data-contact-form") || "hello@zzstudio.youngzyl.me";
      var url = "mailto:" + to +
        "?subject=" + encodeURIComponent(subject) +
        "&body=" + encodeURIComponent(lines);

      // expose the generated URL: useful for debugging, and lets the visitor
      // copy it if the OS has no mail client registered.
      form.setAttribute("data-last-mailto", url);

      window.location.href = url;

      if (status) {
        status.hidden = false;
        status.textContent = "Opening your mail client… ";
        var fallback = document.createElement("a");
        fallback.className = "link";
        fallback.href = url;
        fallback.textContent = "open the draft";
        status.appendChild(fallback);
        status.appendChild(document.createTextNode(" if nothing happened."));
      }
    });
  }
})();
