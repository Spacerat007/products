import csv, html, json, urllib.request, sys, io
from typing import List, Dict

def fetch_csv(url: str) -> str:
    with urllib.request.urlopen(url) as resp:
        charset = resp.headers.get_content_charset() or "utf-8"
        data = resp.read().decode(charset, errors="replace")
    return data

def normalize_header(name: str) -> str:
    return name.strip()

def parse_csv(csv_text: str) -> List[Dict[str, str]]:
    reader = csv.reader(io.StringIO(csv_text))
    rows = list(reader)
    if not rows:
        return []
    header = [normalize_header(h) for h in rows[0]]
    data_rows = []
    for raw in rows[1:]:
        if len(raw) < len(header):
            raw = raw + [""] * (len(header) - len(raw))
        elif len(raw) > len(header):
            raw = raw[:len(header)]
        rec = {header[i]: raw[i] for i in range(len(header))}
        data_rows.append(rec)
    return data_rows

def build_cards(rows: List[Dict[str, str]], cfg: dict) -> str:
    c = cfg["card"]
    title_col = c["title_col"]
    desc_col = c["description_col"]
    price_col = c["price_col"]
    img_col = c["image_url_col"]

    card_html_list = []
    for r in rows:
        title = (r.get(title_col) or "").strip()
        desc = (r.get(desc_col) or "").strip()
        price = (r.get(price_col) or "").strip()
        img = (r.get(img_col) or "").strip()

        if not any([title, desc, price, img]):
            continue

        esc_title = html.escape(title)
        esc_desc = html.escape(desc)
        esc_price = html.escape(price)

        if img:
            safe_img = img.replace('"', "%22")
            img_html = f'<img class="card-img" src="{safe_img}" alt="{esc_title} image" loading="lazy" />'
        else:
            img_html = '<div class="card-img" style="display:flex;align-items:center;justify-content:center;color:#aaa;">No image</div>'

        card_html = f"""
<article class="card">
  {img_html}
  <div class="card-body">
    <h2 class="card-title">{esc_title}</h2>
    <div class="card-desc">{esc_desc}</div>
    <div class="card-price">{esc_price}</div>
  </div>
</article>""".strip()
        card_html_list.append(card_html)

    return "\n".join(card_html_list)

def main():
    with open("config.json", "r", encoding="utf-8") as f:
        cfg = json.load(f)

    csv_url = cfg["csv_url"]
    site_title = cfg.get("site_title", "Products")
    output_file = cfg.get("output_file", "index.html")

    with open("index.template.html", "r", encoding="utf-8") as f:
        template = f.read()

    csv_text = fetch_csv(csv_url)
    records = parse_csv(csv_text)
    cards_html = build_cards(records, cfg)

    out_html = template.replace("{{SITE_TITLE}}", html.escape(site_title))
    out_html = out_html.replace("<!-- CARDS_PLACEHOLDER -->", cards_html or "<p>No products found.</p>")

    with open(output_file, "w", encoding="utf-8") as f:
        f.write(out_html)

    print(f"Wrote {output_file} with {len(records)} rows.")

if __name__ == "__main__":
    sys.exit(main())
