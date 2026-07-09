#!/usr/bin/env python3
"""Bake the Rockstar Health Shopify theme into a standalone static site for
GitHub Pages. Extracts each page's custom-liquid HTML, rebuilds the hero,
header nav and footer, and rewrites all Shopify links/asset URLs to relative
static paths. Output HTML is fully self-contained (no Shopify dependency)."""
import json, os, re

THEME = os.path.expanduser("~/Desktop/Apps/rockstar-health-theme")
SITE  = os.path.expanduser("~/Desktop/Apps/rockstar-health-site")

def load(name):
    raw = open(f"{THEME}/templates/{name}.json").read()
    raw = re.sub(r'^\s*/\*.*?\*/\s*', '', raw, flags=re.S)
    return json.loads(raw)

def page_html(name):
    d = load(name); out = []
    for sid in d.get("order", []):
        s = d["sections"][sid]
        if s.get("type") == "custom-liquid":
            out.append(s["settings"]["custom_liquid"])
    return "\n\n".join(out)

# slug -> (template or None, <title>, meta description)
PAGES = {
 "index":               ("index", "Rockstar Health", "A nonprofit-owned power wheelchair company building affordable, accessible mobility products."),
 "about":               ("page.about", "About | Rockstar Health", "Who we are and why we started Rockstar Health."),
 "our-products":        ("page.our-products", "Our Products | Rockstar Health", "Adaptive mobility accessories, starting with the carbon fiber joystick topper."),
 "joystick-topper":     ("page.joystick-topper", "Carbon Fiber Joystick Topper | Rockstar Health", "An ergonomic press-on grip for power wheelchair joysticks."),
 "storefronts":         ("page.storefronts", "Storefronts | Rockstar Health", "Where to buy Rockstar Health products."),
 "financial-structure": ("page.financial-structure", "Financial Structure | Rockstar Health", "How our nonprofit and its subsidiary are structured."),
 "faq":                 ("page.faq", "FAQ | Rockstar Health", "Answers to common questions about our products and mission."),
 "contact":             ("page.contact", "Contact | Rockstar Health", "Get in touch with Rockstar Health."),
 "custom-order":        (None, "Custom Order | Rockstar Health", "Request a custom mobility accessory."),
}

NAV = [("index","Home"),("about","About"),("our-products","Our Products"),
       ("financial-structure","Financial Structure"),("faq","FAQ"),("contact","Contact")]

# Shopify path -> static file
LINKS = {
 "/": "index.html",
 "/pages/about": "about.html",
 "/pages/our-products": "our-products.html",
 "/pages/financial-structure": "financial-structure.html",
 "/pages/faq": "faq.html",
 "/pages/contact-1": "contact.html",
 "/pages/contact": "contact.html",
 "/pages/storefronts": "storefronts.html",
 "/pages/custom-order": "custom-order.html",
 "/pages/joystick-topper": "joystick-topper.html",
 "/pages/mission": "about.html",
 "/pages/product-development": "our-products.html",
 "/collections/all": "our-products.html",
 "/products/carbon-fiber-wheelchair-joystick-handle-goalpost-ergonomic-shape-fits-powerchair-joysticks": "joystick-topper.html",
}

def rewrite(html):
    # asset_url -> assets/
    html = re.sub(r"{{\s*'([^']+)'\s*\|\s*asset_url\s*}}", r"assets/\1", html)
    # any product url -> product page
    html = re.sub(r'href="/products/[^"]*"', 'href="joystick-topper.html"', html)
    # /pages/<slug> with optional #anchor or ?query
    def pg(m):
        frag = m.group(2) or ''
        return 'href="' + LINKS.get('/pages/'+m.group(1), m.group(1)+'.html') + frag + '"'
    html = re.sub(r'href="/pages/([a-z0-9-]+)(#[^"]*|\?[^"]*)?"', pg, html)
    html = html.replace('href="/collections/all"', 'href="our-products.html"')
    html = html.replace('href="/"', 'href="index.html"')
    return html

def header(active):
    links = "".join(
        f'<a href="{s}.html"{" aria-current=\"page\"" if s==active else ""}>{t}</a>'
        for s,t in NAV)
    return ('<div class="site-header__pill">'
            '<a class="brand" href="index.html"><img src="assets/rockstar-logo.png" alt="Rockstar Health"></a>'
            f'<nav class="nav" aria-label="Primary">{links}</nav></div>')

def footer():
    fg = open(f"{THEME}/sections/footer-group.json").read()
    fg = re.sub(r'^\s*/\*.*?\*/\s*', '', fg, flags=re.S)
    return rewrite(json.loads(fg)["sections"]["rh_footer_links"]["settings"]["custom_liquid"])

HERO = ('<section class="rh-hero"><div class="rh-hero__inner page-width">'
        '<h1 class="rh-hero__title">The nonprofit power wheelchair company.</h1>'
        '<a href="our-products.html" class="button button-primary">View Our Products</a>'
        '</div></section>')

CUSTOM_ORDER = """
<section class="rh-page-hero">
  <div class="rh-page-hero__eyebrow">Shop</div>
  <h1 class="rh-page-hero__heading">Custom Order</h1>
  <p class="rh-page-hero__lede">Need something specific? Describe your request and we'll follow up with pricing, availability, and next steps.</p>
</section>
<section class="rh-section rh-custom-order">
  <h2 class="rh-section__title">Request Details</h2>
  <form class="rh-co-form" id="rh-co-form">
    <div class="rh-co-grid">
      <div class="rh-co-field"><label class="rh-co-label" for="co-name">Full name <span class="rh-co-req">*</span></label>
        <input class="rh-co-input" id="co-name" type="text" name="name" required placeholder="Your full name"></div>
      <div class="rh-co-field"><label class="rh-co-label" for="co-email">Email <span class="rh-co-req">*</span></label>
        <input class="rh-co-input" id="co-email" type="email" name="email" required placeholder="you@example.com"></div>
      <div class="rh-co-field"><label class="rh-co-label" for="co-phone">Phone <span class="rh-co-opt">(optional)</span></label>
        <input class="rh-co-input" id="co-phone" type="tel" name="phone" placeholder="+1 (000) 000-0000"></div>
      <div class="rh-co-field"><label class="rh-co-label" for="co-type">What are you looking for?</label>
        <select class="rh-co-input" id="co-type" name="product_type">
          <option value="">Select a category</option><option>Joystick cover</option><option>Joystick topper</option>
          <option>Seating accessory</option><option>Desk accessory</option><option>Other accessory</option><option>General inquiry</option>
        </select></div>
      <div class="rh-co-field"><label class="rh-co-label" for="co-model">Wheelchair or equipment model</label>
        <input class="rh-co-input" id="co-model" type="text" name="equipment_model" placeholder="e.g. Permobil M3, Quantum Q6 Edge, Invacare TDX"></div>
      <div class="rh-co-field rh-co-field--wide"><label class="rh-co-label" for="co-body">Description <span class="rh-co-req">*</span></label>
        <textarea class="rh-co-input" id="co-body" name="message" rows="5" required placeholder="Describe what you need. Include measurements, material preferences, colors, mounting requirements, or anything else relevant."></textarea></div>
      <div class="rh-co-field"><label class="rh-co-label" for="co-budget">Budget range</label>
        <select class="rh-co-input" id="co-budget" name="budget_range">
          <option value="">Select a range</option><option>Under $50</option><option>$50 to $150</option><option>$150 to $500</option><option>Over $500</option><option>Not sure</option>
        </select></div>
      <div class="rh-co-field"><label class="rh-co-label" for="co-timeline">Timeline</label>
        <select class="rh-co-input" id="co-timeline" name="timeline">
          <option value="">Select a timeline</option><option>As soon as possible</option><option>2 to 4 weeks</option><option>1 to 3 months</option><option>Flexible</option>
        </select></div>
    </div>
    <p class="rh-prose" style="font-size:.95rem;margin-top:1.25rem;">To include a reference file, email it to <a href="mailto:support@rockstarhealth.org">support@rockstarhealth.org</a> with your name in the subject line.</p>
    <label class="rh-co-label" style="display:flex;gap:.6rem;align-items:flex-start;margin:1rem 0;font-weight:300;">
      <input type="checkbox" name="pricing_consent" required style="width:auto;margin-top:.3rem;"> I understand pricing is provided per request and confirmed before any work begins.</label>
    <div class="rh-cta-group rh-cta-group--row"><button type="submit" class="button button-primary">Send request</button></div>
  </form>
</section>
<script>
document.getElementById('rh-co-form').addEventListener('submit', function(e){
  e.preventDefault();
  var f = e.target, g = function(n){ var el = f.elements[n]; return el ? el.value.trim() : ''; };
  var lines = [
    'Name: '     + g('name'),
    'Email: '    + g('email'),
    'Phone: '    + g('phone'),
    'Category: ' + g('product_type'),
    'Equipment: '+ g('equipment_model'),
    'Budget: '   + g('budget_range'),
    'Timeline: ' + g('timeline'),
    '',
    'Details:',
    g('message')
  ];
  var subject = 'Custom order request' + (g('name') ? ' from ' + g('name') : '');
  window.location.href = 'mailto:support@rockstarhealth.org'
    + '?subject=' + encodeURIComponent(subject)
    + '&body=' + encodeURIComponent(lines.join('\\n'));
});
</script>
"""

SKELETON = """<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta property="og:title" content="{title}">
<meta property="og:description" content="{desc}">
<meta property="og:type" content="website">
<link rel="icon" href="assets/rockstar-logo.png">
<link rel="stylesheet" href="assets/rockstar-glass.css">
<link rel="stylesheet" href="assets/site.css">
</head>
<body>
<header class="site-header">{header}</header>
{hero}
<main><div class="page-width page-body">{content}</div></main>
<footer class="site-footer"><div class="page-width">{footer}</div></footer>
</body>
</html>
"""

FOOT = footer()
for slug,(tmpl,title,desc) in PAGES.items():
    if slug == "custom-order":
        content = CUSTOM_ORDER
    else:
        content = rewrite(page_html(tmpl))
    hero = HERO if slug == "index" else ""
    html = SKELETON.format(title=title, desc=desc, header=header(slug), hero=hero,
                           content=content, footer=FOOT)
    open(f"{SITE}/{slug}.html", "w").write(html)
print("built:", sorted(f for f in os.listdir(SITE) if f.endswith(".html")))
