"""
Dynamic App Builder — generates truly arbitrary HTML5 apps from natural language.

Works by:
  1. Parsing the description into an AppSpec (entity, fields, features, theme)
  2. Generating a complete single-file HTML5 app from the spec
  3. The generated app is a real, working application — not a template stub

Supports any entity (plants, recipes, employees, bugs, wines, pets, …)
and composes features (search, filter, chart, export, dark mode, …) on demand.
"""

import re
import json


# ══════════════════════════════════════════════════════════════
# THEME
# ══════════════════════════════════════════════════════════════

def _pick_theme(q: str) -> dict:
    if any(w in q for w in ("light", "white", "clean", "minimal", "pastel")):
        return {"bg": "#f8fafc", "surface": "#ffffff", "border": "#e2e8f0",
                "primary": "#4f46e5", "accent": "#db2777", "text": "#1e293b", "muted": "#64748b",
                "hover": "#f1f5f9", "danger": "#ef4444", "success": "#10b981"}
    if any(w in q for w in ("green", "nature", "forest", "emerald", "plant")):
        return {"bg": "#022c22", "surface": "#064e3b", "border": "#065f46",
                "primary": "#10b981", "accent": "#f59e0b", "text": "#ecfdf5", "muted": "#6ee7b7",
                "hover": "#065f46", "danger": "#f43f5e", "success": "#34d399"}
    if any(w in q for w in ("blue", "ocean", "sky", "cool", "navy")):
        return {"bg": "#0c1a2e", "surface": "#0f2b4a", "border": "#1d3a5c",
                "primary": "#38bdf8", "accent": "#f43f5e", "text": "#f0f9ff", "muted": "#7dd3fc",
                "hover": "#1d3a5c", "danger": "#f43f5e", "success": "#34d399"}
    if any(w in q for w in ("purple", "violet", "grape", "lavender")):
        return {"bg": "#0f0728", "surface": "#1e1254", "border": "#2d1b78",
                "primary": "#a78bfa", "accent": "#f472b6", "text": "#f5f3ff", "muted": "#c4b5fd",
                "hover": "#2d1b78", "danger": "#f43f5e", "success": "#34d399"}
    if any(w in q for w in ("red", "fire", "warm", "hot", "rose")):
        return {"bg": "#1c0d02", "surface": "#431407", "border": "#7c2d12",
                "primary": "#f97316", "accent": "#e11d48", "text": "#fff7ed", "muted": "#fdba74",
                "hover": "#7c2d12", "danger": "#e11d48", "success": "#34d399"}
    # default dark
    return {"bg": "#0f172a", "surface": "#1e293b", "border": "#334155",
            "primary": "#6366f1", "accent": "#ec4899", "text": "#e2e8f0", "muted": "#94a3b8",
            "hover": "#334155", "danger": "#ef4444", "success": "#10b981"}


# ══════════════════════════════════════════════════════════════
# ENTITY & FIELD EXTRACTION
# ══════════════════════════════════════════════════════════════

# Entity → (emoji, suggested fields)
_ENTITY_CATALOG: dict[str, tuple[str, list]] = {
    "task":        ("✅", ["Task", "Priority:select:Low,Medium,High,Critical", "Due Date:date", "Status:select:Todo,In Progress,Done,Cancelled", "Notes:textarea"]),
    "todo":        ("☑️", ["Task", "Priority:select:Low,Medium,High", "Due Date:date", "Done:select:No,Yes"]),
    "habit":       ("🔥", ["Habit", "Frequency:select:Daily,Weekly,Monthly", "Streak:number", "Category:select:Health,Work,Personal,Learning", "Notes:textarea"]),
    "goal":        ("🎯", ["Goal", "Target Date:date", "Progress:number", "Status:select:Not Started,In Progress,Done,Paused", "Category:select:Work,Health,Finance,Learning,Other", "Notes:textarea"]),
    "plant":       ("🌿", ["Plant Name", "Species", "Last Watered:date", "Health:select:Excellent,Good,Fair,Poor", "Location", "Notes:textarea"]),
    "recipe":      ("🍳", ["Recipe Name", "Ingredients:textarea", "Prep Time (min):number", "Servings:number", "Difficulty:select:Easy,Medium,Hard", "Rating:select:⭐,⭐⭐,⭐⭐⭐,⭐⭐⭐⭐,⭐⭐⭐⭐⭐", "Notes:textarea"]),
    "book":        ("📚", ["Title", "Author", "Genre:select:Fiction,Non-Fiction,Sci-Fi,Fantasy,Mystery,Biography,Self-Help,Other", "Status:select:Want to Read,Reading,Finished,DNF", "Rating:select:⭐,⭐⭐,⭐⭐⭐,⭐⭐⭐⭐,⭐⭐⭐⭐⭐", "Notes:textarea"]),
    "movie":       ("🎬", ["Title", "Director", "Genre:select:Action,Comedy,Drama,Horror,Sci-Fi,Romance,Documentary,Other", "Year:number", "Status:select:Want to Watch,Watching,Watched", "Rating:select:⭐,⭐⭐,⭐⭐⭐,⭐⭐⭐⭐,⭐⭐⭐⭐⭐", "Notes:textarea"]),
    "expense":     ("💸", ["Description", "Amount:number", "Category:select:Food,Transport,Housing,Health,Entertainment,Shopping,Work,Other", "Date:date", "Payment:select:Cash,Card,Transfer,Other", "Notes:textarea"]),
    "income":      ("💰", ["Source", "Amount:number", "Category:select:Salary,Freelance,Investment,Gift,Other", "Date:date", "Notes:textarea"]),
    "contact":     ("👤", ["Full Name", "Email:email", "Phone", "Company", "Role", "Category:select:Personal,Work,Client,Vendor,Other", "Notes:textarea"]),
    "customer":    ("🤝", ["Name", "Email:email", "Phone", "Company", "Value:number", "Status:select:Lead,Active,Inactive,Churned", "Notes:textarea"]),
    "employee":    ("👔", ["Full Name", "Role", "Department:select:Engineering,Design,Marketing,Sales,HR,Finance,Operations,Other", "Start Date:date", "Email:email", "Salary:number", "Status:select:Active,On Leave,Terminated"]),
    "product":     ("📦", ["Product Name", "SKU", "Price:number", "Quantity:number", "Category", "Status:select:Active,Out of Stock,Discontinued", "Notes:textarea"]),
    "inventory":   ("📋", ["Item Name", "Quantity:number", "Unit", "Price:number", "Location", "Category", "Reorder Level:number", "Notes:textarea"]),
    "project":     ("🗂️", ["Project Name", "Status:select:Planning,Active,On Hold,Done,Cancelled", "Priority:select:Low,Medium,High,Critical", "Deadline:date", "Team Members", "Description:textarea"]),
    "bug":         ("🐛", ["Title", "Severity:select:Low,Medium,High,Critical", "Status:select:Open,In Progress,Fixed,Won't Fix,Closed", "Assigned To", "Steps to Reproduce:textarea", "Date Reported:date"]),
    "note":        ("📝", ["Title", "Content:textarea", "Category:select:General,Work,Personal,Ideas,Research,Other", "Date:date", "Tags"]),
    "journal":     ("📖", ["Date:date", "Mood:select:😄 Great,🙂 Good,😐 Okay,😕 Bad,😞 Terrible", "Entry:textarea", "Tags", "Gratitude:textarea"]),
    "pet":         ("🐾", ["Pet Name", "Species:select:Dog,Cat,Bird,Fish,Rabbit,Reptile,Other", "Breed", "Age:number", "Vet Date:date", "Health:select:Excellent,Good,Fair,Poor", "Notes:textarea"]),
    "workout":     ("💪", ["Exercise", "Sets:number", "Reps:number", "Weight (kg):number", "Duration (min):number", "Date:date", "Notes:textarea"]),
    "medication":  ("💊", ["Medication Name", "Dose", "Frequency:select:Daily,Twice Daily,Weekly,As Needed", "Start Date:date", "End Date:date", "Notes:textarea"]),
    "appointment": ("📅", ["Title", "Date:date", "Time", "Location", "With", "Status:select:Scheduled,Confirmed,Cancelled,Done", "Notes:textarea"]),
    "link":        ("🔗", ["Title", "URL:url", "Category:select:Article,Video,Tool,Reference,Social,Other", "Tags", "Notes:textarea"]),
    "wine":        ("🍷", ["Name", "Vineyard", "Region", "Vintage:number", "Varietal", "Rating:select:⭐,⭐⭐,⭐⭐⭐,⭐⭐⭐⭐,⭐⭐⭐⭐⭐", "Notes:textarea"]),
    "subscription":("📡", ["Service Name", "Price:number", "Billing Cycle:select:Monthly,Annual,Weekly", "Next Billing:date", "Category:select:Entertainment,Software,Health,Finance,Other", "Status:select:Active,Paused,Cancelled"]),
    "vehicle":     ("🚗", ["Make", "Model", "Year:number", "Mileage:number", "Fuel:select:Petrol,Diesel,Electric,Hybrid", "Last Service:date", "Notes:textarea"]),
    "property":    ("🏠", ["Address", "Type:select:House,Apartment,Commercial,Land,Other", "Value:number", "Status:select:Owned,Rented,For Sale", "Purchase Date:date", "Notes:textarea"]),
    "course":      ("🎓", ["Course Name", "Platform/School", "Status:select:Not Started,In Progress,Completed", "Progress:number", "Start Date:date", "Certificate:select:No,Yes", "Notes:textarea"]),
    "skill":       ("🧠", ["Skill Name", "Category:select:Technical,Soft,Creative,Language,Other", "Level:select:Beginner,Intermediate,Advanced,Expert", "Learning Since:date", "Resources:textarea"]),
    "idea":        ("💡", ["Idea", "Category:select:Business,Product,Creative,Technical,Personal,Other", "Priority:select:Low,Medium,High", "Status:select:Raw,Researching,In Progress,Shelved,Done", "Details:textarea"]),
    "transaction": ("🏦", ["Description", "Amount:number", "Type:select:Income,Expense,Transfer", "Category", "Date:date", "Account", "Notes:textarea"]),
    "event":       ("🎉", ["Event Name", "Date:date", "Time", "Location", "Guests:number", "Status:select:Planning,Confirmed,Cancelled,Done", "Notes:textarea"]),
    "feedback":    ("💬", ["From", "Subject", "Feedback:textarea", "Sentiment:select:Positive,Neutral,Negative", "Date:date", "Status:select:New,Reviewing,Resolved"]),
    "lead":        ("📊", ["Name", "Email:email", "Company", "Source:select:Website,Referral,Social,Ad,Cold,Other", "Value:number", "Stage:select:New,Contacted,Qualified,Proposal,Won,Lost", "Notes:textarea"]),
    "invoice":     ("🧾", ["Invoice #", "Client", "Amount:number", "Due Date:date", "Status:select:Draft,Sent,Paid,Overdue,Cancelled", "Notes:textarea"]),
    "password":    ("🔐", ["Site / App", "Username", "Category:select:Social,Work,Finance,Shopping,Other", "Notes:textarea"]),
    "game":        ("🎮", ["Title", "Platform:select:PC,PS5,Xbox,Nintendo,Mobile,Other", "Genre:select:Action,RPG,Strategy,Sports,Puzzle,Other", "Status:select:Want to Play,Playing,Completed,Dropped", "Rating:select:⭐,⭐⭐,⭐⭐⭐,⭐⭐⭐⭐,⭐⭐⭐⭐⭐", "Notes:textarea"]),
    "clothing":    ("👗", ["Item Name", "Brand", "Size", "Color", "Category:select:Top,Bottom,Dress,Shoes,Accessory,Outerwear", "Season:select:All Year,Spring,Summer,Autumn,Winter", "Notes:textarea"]),
    "food":        ("🍽️", ["Name", "Cuisine:select:Italian,Asian,Mexican,American,Mediterranean,Indian,Other", "Category:select:Breakfast,Lunch,Dinner,Snack,Dessert", "Rating:select:⭐,⭐⭐,⭐⭐⭐,⭐⭐⭐⭐,⭐⭐⭐⭐⭐", "Tried:select:Yes,No", "Notes:textarea"]),
    "travel":      ("✈️", ["Destination", "Country", "Date:date", "Duration (days):number", "Status:select:Dream,Planned,Booked,Done", "Budget:number", "Notes:textarea"]),
    "photo":       ("📷", ["Title", "Location", "Date:date", "Camera/Device", "Tags", "Notes:textarea"]),
    "music":       ("🎵", ["Song/Album", "Artist", "Genre:select:Pop,Rock,Hip-Hop,R&B,Electronic,Jazz,Classical,Other", "Status:select:Want to Listen,Listening,Favourite", "Rating:select:⭐,⭐⭐,⭐⭐⭐,⭐⭐⭐⭐,⭐⭐⭐⭐⭐", "Notes:textarea"]),
}

# Aliases so we match more variations
_ENTITY_ALIASES: dict[str, str] = {
    "todo": "todo", "to do": "todo", "to-do": "todo", "tasks": "task",
    "todos": "todo", "goals": "goal", "habits": "habit", "recipes": "recipe",
    "books": "book", "movies": "movie", "film": "movie", "films": "movie",
    "expenses": "expense", "spending": "expense", "spend": "expense",
    "contacts": "contact", "customers": "customer", "clients": "customer",
    "employees": "employee", "staff": "employee", "team members": "employee",
    "products": "product", "items": "inventory", "stock": "inventory",
    "projects": "project", "bugs": "bug", "issues": "bug", "tickets": "bug",
    "notes": "note", "journal": "journal", "diary": "journal",
    "pets": "pet", "animals": "pet",
    "workouts": "workout", "exercise": "workout", "exercises": "workout", "fitness": "workout",
    "medications": "medication", "pills": "medication", "medicines": "medication",
    "appointments": "appointment", "meetings": "appointment", "events": "event",
    "links": "link", "bookmarks": "link", "urls": "link",
    "wines": "wine", "subscriptions": "subscription", "subs": "subscription",
    "vehicles": "vehicle", "cars": "vehicle", "bike": "vehicle", "bikes": "vehicle",
    "properties": "property", "houses": "property", "rentals": "property",
    "courses": "course", "classes": "course", "skills": "skill",
    "ideas": "idea", "transactions": "transaction", "finances": "transaction",
    "feedbacks": "feedback", "reviews": "feedback",
    "leads": "lead", "invoices": "invoice",
    "games": "game", "clothes": "clothing", "outfits": "clothing",
    "foods": "food", "dishes": "food", "restaurants": "food",
    "trips": "travel", "travels": "travel", "places": "travel",
    "photos": "photo", "images": "photo", "pictures": "photo",
    "songs": "music", "albums": "music", "tracks": "music",
    "passwords": "password", "credentials": "password",
    "goals": "goal", "objectives": "goal",
}


def _detect_entity(q: str) -> tuple[str, str, list]:
    """Returns (entity_key, emoji, fields)."""
    # Check aliases first (longer phrases before shorter)
    for alias in sorted(_ENTITY_ALIASES, key=len, reverse=True):
        if alias in q:
            key = _ENTITY_ALIASES[alias]
            emoji, fields = _ENTITY_CATALOG[key]
            return key, emoji, fields

    # Check catalog directly
    for key in sorted(_ENTITY_CATALOG, key=len, reverse=True):
        if key in q or key + "s" in q:
            emoji, fields = _ENTITY_CATALOG[key]
            return key, emoji, fields

    # Try to extract entity from common patterns
    patterns = [
        r"(?:track|manage|organize|log|record|store|keep track of|catalog)\s+(?:my\s+)?(\w[\w\s]{1,20}?)(?:\s+(?:with|and|that|which)|$)",
        r"(\w[\w\s]{1,20}?)\s+(?:tracker|manager|list|log|journal|diary|database|catalog|registry|organizer)",
        r"list\s+of\s+(?:my\s+)?(\w[\w\s]{1,20}?)(?:\s+(?:with|and)|$)",
        r"(?:a|an)\s+(\w[\w\s]{1,20}?)\s+(?:tracker|manager|app|tool|system)",
        r"build\s+(?:me\s+)?(?:a\s+|an\s+)?(\w[\w\s]{1,20}?)\s+(?:app|tool|manager|tracker|system|dashboard)",
    ]
    for pat in patterns:
        m = re.search(pat, q)
        if m:
            raw = m.group(1).strip().rstrip("s")
            # Build generic fields around the entity name
            return raw, "📋", _generic_fields(raw, q)

    return "item", "📋", _generic_fields("item", q)


def _generic_fields(entity: str, q: str) -> list:
    """Build a sensible field list for an unknown entity."""
    fields = [entity.title()]
    if any(w in q for w in ("price", "cost", "amount", "value", "money", "budget", "fee")):
        fields.append("Amount:number")
    if any(w in q for w in ("date", "when", "time", "schedule", "deadline", "due")):
        fields.append("Date:date")
    if any(w in q for w in ("category", "type", "kind", "group")):
        fields.append("Category:select:General,Work,Personal,Other")
    if any(w in q for w in ("status", "state", "progress", "stage")):
        fields.append("Status:select:Active,Done,Pending,Cancelled")
    if any(w in q for w in ("priority", "importance", "urgent")):
        fields.append("Priority:select:Low,Medium,High")
    if any(w in q for w in ("rating", "score", "grade", "star")):
        fields.append("Rating:select:⭐,⭐⭐,⭐⭐⭐,⭐⭐⭐⭐,⭐⭐⭐⭐⭐")
    if any(w in q for w in ("tag", "label", "keyword")):
        fields.append("Tags")
    if any(w in q for w in ("location", "place", "where", "address")):
        fields.append("Location")
    if any(w in q for w in ("description", "detail", "note", "comment", "info")):
        fields.append("Notes:textarea")
    else:
        fields.append("Notes:textarea")
    return fields


def _detect_features(q: str) -> set:
    features = set()
    if any(w in q for w in ("search", "find", "filter")):
        features.add("search")
    if any(w in q for w in ("chart", "graph", "visual", "statistic", "stat", "analytics", "breakdown")):
        features.add("chart")
    if any(w in q for w in ("export", "download", "csv", "save file")):
        features.add("export")
    if any(w in q for w in ("dark mode", "dark theme", "dark")):
        features.add("dark_mode")
    if any(w in q for w in ("sort", "order")):
        features.add("sort")
    if any(w in q for w in ("total", "sum", "count", "summary", "overview", "dashboard", "stats")):
        features.add("stats")
    if any(w in q for w in ("edit", "editable", "update", "modify", "change")):
        features.add("edit")
    if any(w in q for w in ("tag", "label", "keyword")):
        features.add("tags")
    return features


# ══════════════════════════════════════════════════════════════
# FIELD PARSING
# ══════════════════════════════════════════════════════════════

def _parse_field(raw: str) -> dict:
    """
    Parse a field definition like "Amount:number" or "Status:select:Active,Done".
    Returns {"name": str, "label": str, "type": str, "options": list, "id": str}
    """
    parts = raw.split(":", 2)
    label = parts[0].strip()
    ftype = parts[1].strip() if len(parts) > 1 else "text"
    options = parts[2].split(",") if len(parts) > 2 else []
    field_id = re.sub(r"[^a-z0-9]", "_", label.lower()).strip("_")
    return {"name": field_id, "label": label, "type": ftype, "options": options}


# ══════════════════════════════════════════════════════════════
# TITLE GENERATION
# ══════════════════════════════════════════════════════════════

def _make_title(entity: str, q: str) -> str:
    # Look for explicit title patterns
    m = re.search(r"called\s+[\"']?(.+?)[\"']?(?:\s|$)", q)
    if m:
        return m.group(1).strip().title()
    m = re.search(r"named\s+[\"']?(.+?)[\"']?(?:\s|$)", q)
    if m:
        return m.group(1).strip().title()

    # Derive from entity
    entity_title = entity.replace("_", " ").title()
    if any(w in q for w in ("tracker", "tracking")):
        return f"{entity_title} Tracker"
    if any(w in q for w in ("manager", "manage")):
        return f"{entity_title} Manager"
    if any(w in q for w in ("log", "diary", "journal")):
        return f"{entity_title} Journal"
    if any(w in q for w in ("list",)):
        return f"{entity_title} List"
    if any(w in q for w in ("dashboard", "overview")):
        return f"{entity_title} Dashboard"
    if any(w in q for w in ("organizer", "organize")):
        return f"{entity_title} Organizer"
    return f"{entity_title} Manager"


# ══════════════════════════════════════════════════════════════
# HTML GENERATOR
# ══════════════════════════════════════════════════════════════

def _field_input_html(f: dict) -> str:
    fid = f"field_{f['name']}"
    base = f'id="{fid}"'
    if f["type"] == "textarea":
        return f'<textarea {base} placeholder="{f["label"]}..." rows="3"></textarea>'
    if f["type"] == "select":
        opts = "".join(f'<option value="{o.strip()}">{o.strip()}</option>' for o in f["options"])
        return f'<select {base}><option value="">— {f["label"]} —</option>{opts}</select>'
    type_map = {"number": "number", "date": "date", "email": "email", "url": "url",
                "color": "color", "text": "text"}
    t = type_map.get(f["type"], "text")
    return f'<input {base} type="{t}" placeholder="{f["label"]}">'


def _js_get_value(f: dict) -> str:
    fid = f"field_{f['name']}"
    if f["type"] == "textarea":
        return f'document.getElementById("{fid}").value.trim()'
    if f["type"] in ("text", "number", "date", "email", "url", "color"):
        return f'document.getElementById("{fid}").value.trim()'
    if f["type"] == "select":
        return f'document.getElementById("{fid}").value'
    return f'document.getElementById("{fid}").value.trim()'


def _js_set_value(f: dict, expr: str) -> str:
    fid = f"field_{f['name']}"
    return f'document.getElementById("{fid}").value = {expr};'


def _js_clear_field(f: dict) -> str:
    fid = f"field_{f['name']}"
    return f'document.getElementById("{fid}").value = "";'


def generate_crud_app(query: str) -> str:
    """Build a complete CRUD manager for any entity from a description."""
    q = query.lower()
    entity_key, emoji, raw_fields = _detect_entity(q)
    fields = [_parse_field(rf) for rf in raw_fields]
    features = _detect_features(q)
    theme = _pick_theme(q)
    title = _make_title(entity_key, q)
    entity_label = entity_key.replace("_", " ").title()
    entity_plural = entity_label + "s"
    t = theme

    has_search = "search" in features or len(raw_fields) > 3
    has_stats = "stats" in features or any(f["type"] == "number" for f in fields)
    has_chart = "chart" in features
    has_export = "export" in features
    has_edit = True  # always include edit

    # --- Form inputs HTML ---
    form_inputs = "\n".join(
        f'<div class="field-group"><label class="field-label">{f["label"]}</label>{_field_input_html(f)}</div>'
        for f in fields
    )

    # --- JS: collect form values ---
    collect_js = ",\n          ".join(
        f'{f["name"]}: {_js_get_value(f)}'
        for f in fields
    )
    required_field = fields[0]["name"] if fields else "name"

    # --- JS: clear form ---
    clear_js = "\n      ".join(_js_clear_field(f) for f in fields)

    # --- JS: populate edit form ---
    populate_js = "\n        ".join(
        _js_set_value(f, f'item.{f["name"]} || ""')
        for f in fields
    )

    # --- Card rendering JS ---
    card_fields_js = "\n        ".join(
        f'if(item.{f["name"]}) parts.push(`<span class="card-field"><span class="field-key">{f["label"]}:</span> ${{item.{f["name"]}}}</span>`);'
        for f in fields[1:]  # skip the primary field (shown as title)
    )

    # --- Stats JS ---
    numeric_fields = [f for f in fields if f["type"] == "number"]
    stats_js = ""
    stats_html = ""
    if has_stats and numeric_fields:
        for nf in numeric_fields[:2]:
            stats_js += f'\n  const {nf["name"]}Total = items.reduce((s,i)=>s+(parseFloat(i.{nf["name"]})||0),0);'
        stats_html = "".join(
            f'<div class="stat-card"><div class="stat-label">{nf["label"]}</div><div class="stat-value" id="stat_{nf["name"]}">0</div></div>'
            for nf in numeric_fields[:2]
        )
        stats_update_js = "\n  ".join(
            f'const statEl_{nf["name"]} = document.getElementById("stat_{nf["name"]}"); if(statEl_{nf["name"]}) statEl_{nf["name"]}.innerText = items.reduce((s,i)=>s+(parseFloat(i.{nf["name"]})||0),0).toLocaleString();'
            for nf in numeric_fields[:2]
        )
    else:
        stats_update_js = ""

    # --- Chart JS ---
    chart_js = ""
    if has_chart:
        # Group by the first select field if one exists
        group_field = next((f for f in fields if f["type"] == "select"), None)
        if group_field:
            chart_js = f"""
  // Chart
  const chartCanvas = document.getElementById('chart');
  if(chartCanvas) {{
    const counts = {{}};
    items.forEach(i => {{ const k = i.{group_field["name"]} || 'Other'; counts[k] = (counts[k]||0)+1; }});
    const ctx = chartCanvas.getContext('2d');
    const keys = Object.keys(counts); const vals = Object.values(counts);
    const maxV = Math.max(...vals, 1);
    const bw = Math.floor((chartCanvas.width - 40) / Math.max(keys.length,1)) - 8;
    ctx.clearRect(0,0,chartCanvas.width,chartCanvas.height);
    keys.forEach((k,i) => {{
      const x = 20 + i*(bw+8), h = Math.round((vals[i]/maxV)*(chartCanvas.height-40));
      const y = chartCanvas.height - h - 20;
      ctx.fillStyle = '{t["primary"]}'; ctx.fillRect(x,y,bw,h);
      ctx.fillStyle = '{t["muted"]}'; ctx.font='10px sans-serif'; ctx.textAlign='center';
      ctx.fillText(k.slice(0,8), x+bw/2, chartCanvas.height-5);
      ctx.fillStyle = '{t["text"]}';
      ctx.fillText(vals[i], x+bw/2, y-4);
    }});
  }}"""

    # --- Export JS ---
    export_js = ""
    if has_export:
        headers = ",".join(f'"{f["label"]}"' for f in fields)
        row_js = "+','+".join(f'"\\""+(item.{f["name"]}||"").toString().replace(/"/g,\'\\\\"\')+"\\""' for f in fields)
        export_js = f"""
function exportCSV() {{
  const headers = [{headers}];
  const rows = items.map(item => [{row_js}]);
  const csv = [headers.join(','), ...rows.map(r=>r.join(','))].join('\\n');
  const a = document.createElement('a');
  a.href = 'data:text/csv;charset=utf-8,' + encodeURIComponent(csv);
  a.download = '{title.replace(" ","_")}.csv';
  a.click();
}}"""

    search_html = f'<input id="searchInput" type="search" placeholder="Search {entity_plural.lower()}..." oninput="render()">' if has_search else ""
    chart_html = f'<div class="chart-section"><div class="section-title">📊 Breakdown</div><canvas id="chart" width="400" height="180"></canvas></div>' if has_chart else ""
    stats_html_block = f'<div class="stats-row">{stats_html}</div>' if stats_html else ""
    export_btn_html = f'<button class="btn btn-ghost" onclick="exportCSV()">⬇ Export CSV</button>' if has_export else ""

    html = f"""<!DOCTYPE html>
<html lang="en">
<head>
<meta charset="UTF-8">
<meta name="viewport" content="width=device-width,initial-scale=1">
<title>{title}</title>
<style>
*{{box-sizing:border-box;margin:0;padding:0}}
body{{background:{t['bg']};color:{t['text']};font-family:-apple-system,BlinkMacSystemFont,'Segoe UI',sans-serif;min-height:100vh;padding:16px}}
h1{{font-size:1.4rem;font-weight:800;letter-spacing:-.02em}}
.app{{max-width:900px;margin:0 auto;display:grid;grid-template-columns:300px 1fr;gap:16px;align-items:start}}
@media(max-width:640px){{.app{{grid-template-columns:1fr}}}}
.panel,.card-panel{{background:{t['surface']};border:1px solid {t['border']};border-radius:14px;padding:18px}}
.panel-title{{font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.1em;color:{t['muted']};margin-bottom:12px}}
.field-group{{margin-bottom:10px}}
.field-label{{display:block;font-size:.68rem;font-weight:600;color:{t['muted']};text-transform:uppercase;letter-spacing:.05em;margin-bottom:4px}}
input,select,textarea{{width:100%;background:{t['bg']};border:1.5px solid {t['border']};color:{t['text']};border-radius:8px;padding:8px 10px;font-size:.82rem;outline:none;font-family:inherit;transition:border-color .15s}}
input:focus,select:focus,textarea:focus{{border-color:{t['primary']}}}
textarea{{resize:vertical;min-height:60px}}
.btn{{display:inline-flex;align-items:center;gap:6px;padding:8px 14px;border-radius:9px;font-size:.78rem;font-weight:700;cursor:pointer;border:none;transition:.15s;white-space:nowrap}}
.btn-primary{{background:{t['primary']};color:#fff}} .btn-primary:hover{{opacity:.85}}
.btn-ghost{{background:transparent;border:1.5px solid {t['border']};color:{t['text']}}} .btn-ghost:hover{{background:{t['hover']}}}
.btn-danger{{background:transparent;border:1.5px solid {t['danger']};color:{t['danger']}}} .btn-danger:hover{{background:{t['danger']};color:#fff}}
.btn-sm{{padding:5px 10px;font-size:.7rem;border-radius:7px}}
.header{{display:flex;align-items:center;justify-content:space-between;margin-bottom:16px;gap:10px;flex-wrap:wrap}}
.header-left{{display:flex;align-items:center;gap:10px}}
.badge{{font-size:.65rem;background:{t['primary']}22;color:{t['primary']};border:1px solid {t['primary']}44;border-radius:99px;padding:2px 8px;font-weight:700}}
.search-bar{{width:100%;margin-bottom:12px}}
.search-bar input{{border-radius:9px}}
.items-grid{{display:grid;grid-template-columns:1fr;gap:10px}}
.card{{background:{t['bg']};border:1.5px solid {t['border']};border-radius:12px;padding:14px;transition:.15s}}
.card:hover{{border-color:{t['primary']}66}}
.card-title{{font-size:.9rem;font-weight:700;margin-bottom:6px;color:{t['text']}}}
.card-fields{{display:flex;flex-wrap:wrap;gap:6px;margin-bottom:8px}}
.card-field{{font-size:.7rem;background:{t['surface']};border:1px solid {t['border']};border-radius:6px;padding:2px 8px;color:{t['muted']}}}
.field-key{{font-weight:600;color:{t['text']}88}}
.card-actions{{display:flex;gap:6px;margin-top:10px;flex-wrap:wrap}}
.empty{{text-align:center;padding:40px 20px;color:{t['muted']};font-size:.85rem}}
.stats-row{{display:flex;gap:10px;margin-bottom:14px;flex-wrap:wrap}}
.stat-card{{flex:1;min-width:100px;background:{t['bg']};border:1px solid {t['border']};border-radius:10px;padding:12px;text-align:center}}
.stat-label{{font-size:.65rem;text-transform:uppercase;letter-spacing:.08em;color:{t['muted']};margin-bottom:4px;font-weight:600}}
.stat-value{{font-size:1.3rem;font-weight:800;color:{t['primary']};font-family:monospace}}
.chart-section{{background:{t['bg']};border:1px solid {t['border']};border-radius:12px;padding:14px;margin-bottom:14px}}
.section-title{{font-size:.7rem;font-weight:700;text-transform:uppercase;letter-spacing:.08em;color:{t['muted']};margin-bottom:10px}}
canvas{{width:100%;display:block}}
/* Modal */
.modal-backdrop{{position:fixed;inset:0;background:rgba(0,0,0,.6);backdrop-filter:blur(4px);z-index:100;display:flex;align-items:center;justify-content:center;padding:16px}}
.modal{{background:{t['surface']};border:1px solid {t['border']};border-radius:16px;padding:22px;width:100%;max-width:420px;max-height:90vh;overflow-y:auto}}
.modal-title{{font-size:1rem;font-weight:800;margin-bottom:16px}}
.modal-actions{{display:flex;gap:8px;margin-top:16px;justify-content:flex-end}}
.hidden{{display:none}}
</style>
</head>
<body>
<div class="app">
  <!-- ── Add / Edit Panel ── -->
  <aside>
    <div class="panel">
      <div class="panel-title">✚ Add {entity_label}</div>
{form_inputs}
      <div style="display:flex;gap:8px;margin-top:12px">
        <button class="btn btn-primary" style="flex:1" onclick="save()">Save {entity_label}</button>
        <button class="btn btn-ghost btn-sm" onclick="clearForm()">Clear</button>
      </div>
    </div>
  </aside>

  <!-- ── Main Area ── -->
  <main>
    <div class="header">
      <div class="header-left">
        <span style="font-size:1.5rem">{emoji}</span>
        <div>
          <h1>{title}</h1>
          <span class="badge" id="countBadge">0 {entity_plural.lower()}</span>
        </div>
      </div>
      <div style="display:flex;gap:8px;flex-wrap:wrap">
        {export_btn_html}
      </div>
    </div>

    {stats_html_block}
    {chart_html}

    <div class="card-panel">
      {'<div class="search-bar">' + search_html + '</div>' if search_html else ""}
      <div class="items-grid" id="itemsGrid"></div>
    </div>
  </main>
</div>

<!-- Edit Modal -->
<div class="modal-backdrop hidden" id="editModal">
  <div class="modal">
    <div class="modal-title">✏️ Edit {entity_label}</div>
    <div id="editFields"></div>
    <div class="modal-actions">
      <button class="btn btn-ghost" onclick="closeModal()">Cancel</button>
      <button class="btn btn-primary" onclick="saveEdit()">Save Changes</button>
    </div>
  </div>
</div>

<script>
const STORAGE_KEY = 'forgeai_{entity_key.replace("-","_")}';
let items = [];
let editingId = null;

// ── Persistence ────────────────────────────────
function save_storage() {{
  try {{ localStorage.setItem(STORAGE_KEY, JSON.stringify(items)); }} catch(e) {{}}
}}
function load_storage() {{
  try {{ items = JSON.parse(localStorage.getItem(STORAGE_KEY) || '[]'); }} catch(e) {{ items = []; }}
}}

// ── Form ───────────────────────────────────────
function collect() {{
  return {{
    id: Date.now() + Math.random(),
    created: new Date().toISOString(),
    {collect_js}
  }};
}}
function clearForm() {{
  {clear_js}
  editingId = null;
}}
function save() {{
  const item = collect();
  if (!item.{required_field}) {{ alert('Please fill in the {fields[0]["label"] if fields else "Name"} field.'); return; }}
  items.unshift(item);
  save_storage(); clearForm(); render();
}}

// ── Edit modal ─────────────────────────────────
const FIELDS = {json.dumps([{"name": f["name"], "label": f["label"], "type": f["type"], "options": f["options"]} for f in fields])};
function openEdit(id) {{
  const item = items.find(i => i.id === id);
  if (!item) return;
  editingId = id;
  const container = document.getElementById('editFields');
  container.innerHTML = FIELDS.map(f => {{
    let input = '';
    if (f.type === 'textarea') {{
      input = `<textarea id="edit_${{f.name}}" rows="3">${{item[f.name] || ''}}</textarea>`;
    }} else if (f.type === 'select') {{
      const opts = f.options.map(o => `<option value="${{o}}" ${{item[f.name]===o?'selected':''}}>` + o + '</option>').join('');
      input = `<select id="edit_${{f.name}}"><option value="">— ${{f.label}} —</option>${{opts}}</select>`;
    }} else {{
      input = `<input id="edit_${{f.name}}" type="${{f.type}}" value="${{item[f.name] || ''}}">`;
    }}
    return `<div class="field-group"><label class="field-label">${{f.label}}</label>${{input}}</div>`;
  }}).join('');
  document.getElementById('editModal').classList.remove('hidden');
}}
function closeModal() {{
  document.getElementById('editModal').classList.add('hidden');
  editingId = null;
}}
function saveEdit() {{
  if (editingId === null) return;
  const idx = items.findIndex(i => i.id === editingId);
  if (idx === -1) return;
  FIELDS.forEach(f => {{
    const el = document.getElementById('edit_' + f.name);
    if (el) items[idx][f.name] = el.value.trim ? el.value.trim() : el.value;
  }});
  items[idx].updated = new Date().toISOString();
  save_storage(); closeModal(); render();
}}

// ── Delete ─────────────────────────────────────
function remove(id) {{
  if (!confirm('Delete this {entity_label.lower()}?')) return;
  items = items.filter(i => i.id !== id);
  save_storage(); render();
}}

// ── Render ─────────────────────────────────────
function render() {{
  const searchEl = document.getElementById('searchInput');
  const q = searchEl ? searchEl.value.toLowerCase() : '';
  const filtered = q
    ? items.filter(item => JSON.stringify(item).toLowerCase().includes(q))
    : items;

  document.getElementById('countBadge').innerText = filtered.length + ' {entity_plural.lower()}';

  const grid = document.getElementById('itemsGrid');
  if (!filtered.length) {{
    grid.innerHTML = `<div class="empty">No {entity_plural.lower()} yet.<br>Add your first {entity_label.lower()} using the panel →</div>`;
  }} else {{
    grid.innerHTML = filtered.map(item => {{
      const parts = [];
      {card_fields_js}
      return `
        <div class="card">
          <div class="card-title">${{item.{required_field} || '—'}}</div>
          <div class="card-fields">${{parts.join('')}}</div>
          <div class="card-actions">
            <button class="btn btn-ghost btn-sm" onclick="openEdit(${{item.id}})">✏️ Edit</button>
            <button class="btn btn-danger btn-sm" onclick="remove(${{item.id}})">🗑 Delete</button>
          </div>
        </div>`;
    }}).join('');
  }}

  // Stats
  {stats_update_js}
  {chart_js}
}}

{export_js}

// ── Init ───────────────────────────────────────
document.getElementById('editModal').addEventListener('click', function(e) {{
  if (e.target === this) closeModal();
}});
load_storage();
render();
</script>
</body>
</html>"""
    return html


# ══════════════════════════════════════════════════════════════
# PUBLIC ENTRY POINT
# ══════════════════════════════════════════════════════════════

def build_dynamic_app(query: str) -> dict:
    q = query.lower()
    entity_key, emoji, _ = _detect_entity(q)
    title = _make_title(entity_key, q)
    code = generate_crud_app(query)
    return {"title": title, "type": "dynamic_crud", "code": code}
