import random
import string

from flask import Flask, g, render_template, request, Response, redirect, url_for
from flask_babel import Babel, gettext as _

app = Flask(__name__)
app.config["BABEL_DEFAULT_LOCALE"] = "en"
app.config["BABEL_TRANSLATION_DIRECTORIES"] = "translations"

SUPPORTED_LANGS = ["pt", "en", "es"]


def get_locale():
    return getattr(g, "lang_code", "en")


babel = Babel(app, locale_selector=get_locale)

# fmt: off
_WORDS = [
    "abacaxi","abismo","agulha","alcova","aldeia","amanho","ancora","anjo",
    "aranha","areia","aroma","arvore","asas","astro","atlas","aurora",
    "aviao","azul","bairro","baleia","bambu","banana","barco","basalto",
    "beija","bigode","bolsa","bosque","braco","brisa","buraco","buzina",
    "cabra","cacau","calma","camelo","campo","canto","caoba","carro",
    "casca","cavalo","chuva","cidade","cinza","cobra","colmeia","coral",
    "corvo","couve","cozinha","cravo","cristal","dagua","danca","deserto",
    "diabo","diamante","dobra","dragao","dunas","eclipse","egua","elmo",
    "enxame","escudo","espada","estrela","faca","farinha","ferro","festa",
    "figueira","flecha","floresta","folha","fonte","forja","fosse","fruta",
    "fumo","furacao","gaiola","gato","gaviao","geada","glaciar","globo",
    "golfinho","graxa","gruta","guarana","guarda","ilhota","inverno","jardim",
    "joelho","junco","lancha","lapis","laranja","leao","lentilha","lima",
    "lince","lobo","lombo","lua","luva","macaco","magia","manto",
    "maraca","marinho","mato","melodia","mestre","milho","mirtilo","monte",
    "navio","nebula","nevoeiro","ninho","norte","nuvem","oceano","oliva",
    "onca","orgulho","orvalho","ostra","ourico","painel","palma","panela",
    "pantano","papiro","passaro","patins","pedra","peixe","pena","petala",
    "piloto","pinheiro","pipa","planeta","polvos","pombo","portal","pouso",
    "prata","preto","primo","pulga","radar","raio","raposa","raiz",
    "reino","relva","remo","riacho","risca","robalo","rocha","rolha",
    "roxo","ruivo","sabao","sabre","safira","sapo","selva","semente",
    "serra","signo","sino","sistema","soalho","sobra","solar","sonho",
    "sorte","suco","tabua","talco","tarefa","templo","tigre","tinta",
    "toalha","tornado","totem","trovao","tucano","tulipa","tundra","turvo",
    "ubere","ultra","umbra","unico","urano","urso","uva","vaca",
    "valsa","vapor","vela","veneno","vento","verde","vidro","viola",
    "virado","visor","vista","vitoria","voador","vulcao","xadrez","zebra",
]
# fmt: on

_AMBIGUOUS = set("0Oo1lIi")
_WIFI_AMBIGUOUS = _AMBIGUOUS | set("S5B8Z2")


def generate_memorable() -> tuple[str, list[str]]:
    words = random.sample(_WORDS, 3)
    words = [w.capitalize() for w in words]
    sep = random.choice(["-", ".", "_"])
    number = str(random.randint(10, 99))
    parts = [words[0], sep, words[1], sep, words[2], sep, number]
    return "".join(parts), parts


def generate_backup_code() -> str:
    digits = [random.choice(string.digits) for _ in range(8)]
    return f"{''.join(digits[:4])} {''.join(digits[4:])}"


def generate_password(
    length: int,
    use_upper: bool,
    use_lower: bool,
    use_numbers: bool,
    use_symbols: bool,
    exclude: str = "",
    child_mode: bool = False,
    wifi_mode: bool = False,
) -> str:
    symbols_chars = "!@#$%^&*()_+-=[]{}|;:,.<>?"
    charset = ""
    required = []

    if child_mode:
        ambiguous = _AMBIGUOUS
    elif wifi_mode:
        ambiguous = _WIFI_AMBIGUOUS
    else:
        ambiguous = set()
    blocked = set(exclude) | ambiguous

    def clean(s: str) -> str:
        return "".join(c for c in s if c not in blocked)

    upper = clean(string.ascii_uppercase)
    lower = clean(string.ascii_lowercase)
    digits = clean(string.digits)
    symbols = clean(symbols_chars)

    if use_upper and upper:
        charset += upper
        required.append(random.choice(upper))
    if use_lower and lower:
        charset += lower
        required.append(random.choice(lower))
    if use_numbers and digits:
        charset += digits
        required.append(random.choice(digits))
    if use_symbols and symbols:
        charset += symbols
        required.append(random.choice(symbols))

    if not charset:
        return ""

    remaining = max(0, length - len(required))
    chars = required + [random.choice(charset) for _ in range(remaining)]
    random.shuffle(chars)
    return "".join(chars)


def password_strength(password: str) -> dict:
    score = 0
    if any(c.isupper() for c in password):
        score += 1
    if any(c.islower() for c in password):
        score += 1
    if any(c.isdigit() for c in password):
        score += 1
    if any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in password):
        score += 1
    if len(password) >= 16:
        score += 1

    levels = {
        1: (_("Muito Fraca"), "text-red-500", "w-1/5", "bg-red-400"),
        2: (_("Fraca"), "text-orange-500", "w-2/5", "bg-orange-400"),
        3: (_("Moderada"), "text-yellow-600", "w-3/5", "bg-yellow-400"),
        4: (_("Forte"), "text-lime-600", "w-4/5", "bg-lime-500"),
        5: (_("Muito Forte"), "text-emerald-600", "w-full", "bg-emerald-500"),
    }
    default = (_("Muito Fraca"), "text-red-500", "w-1/5", "bg-red-400")
    row = levels.get(score, default)
    return {"label": row[0], "text_color": row[1], "bar_width": row[2], "bar_color": row[3]}


@app.template_filter("select_upper")
def select_upper(s):
    return any(c.isupper() for c in s)


@app.template_filter("select_lower")
def select_lower(s):
    return any(c.islower() for c in s)


@app.template_filter("select_digit")
def select_digit(s):
    return any(c.isdigit() for c in s)


@app.template_filter("select_symbol")
def select_symbol(s):
    return any(c in "!@#$%^&*()_+-=[]{}|;:,.<>?" for c in s)


# ── Locale handling ──


@app.url_value_preprocessor
def pull_lang_code(endpoint, values):
    if values:
        g.lang_code = values.pop("lang_code", "en")
    else:
        g.lang_code = "en"


@app.context_processor
def inject_i18n():
    lang = getattr(g, "lang_code", "en")
    lang_labels = {"pt": "PT", "en": "EN", "es": "ES"}

    # Map endpoints to their localized URL patterns
    _url_map = {
        "index":   {"en": "/",            "pt": "/pt/",         "es": "/es/"},
        "privacy": {"en": "/privacy",     "pt": "/pt/privacy",  "es": "/es/privacy"},
        "terms":   {"en": "/terms",       "pt": "/pt/terms",    "es": "/es/terms"},
    }

    def lang_url(code):
        endpoint = request.endpoint or "index"
        # For generate endpoint, map back to index
        if endpoint == "generate":
            endpoint = "index"
        return _url_map.get(endpoint, _url_map["index"]).get(code, "/")

    return {
        "lang_code": lang,
        "supported_langs": SUPPORTED_LANGS,
        "lang_labels": lang_labels,
        "lang_url": lang_url,
        "i18n_js": {
            "senha": _("senha"),
            "senhas": _("senhas"),
            "gerar": _("Gerar"),
            "gerar_senha": _("Gerar Senha"),
            "gerar_memoravel": _("Gerar Senha Memorizável"),
            "gerar_backup": _("Gerar Código de Backup"),
            "senhas_geradas": _("senhas geradas"),
            "sua_senha_gerada": _("Sua senha gerada"),
            "presets": {
                "personal":  {"label": _("Pessoal"),      "desc": _("uso diário")},
                "wifi":      {"label": _("Wi-Fi"),         "desc": _("redes domésticas")},
                "memorable": {"label": _("Memorizável"),   "desc": _("fácil de lembrar")},
                "pin":       {"label": _("PIN"),           "desc": _("desbloqueio")},
                "elderly":   {"label": _("Sênior"),        "desc": _("fácil de ler")},
                "backup":    {"label": _("Backup"),        "desc": _("recuperação")},
                "corporate": {"label": _("Corporativo"),   "desc": _("política de TI")},
                "master":    {"label": _("Master"),        "desc": _("cofre de senhas")},
                "legacy":    {"label": _("Legado"),        "desc": _("sistemas antigos")},
                "apikey":    {"label": _("API Key"),       "desc": _("integrações")},
                "token":     {"label": _("Token"),         "desc": _("acesso a APIs")},
                "shell":     {"label": _("Shell-safe"),    "desc": _("terminais bash")},
                "url":       {"label": _("URL-safe"),      "desc": _("configs e variáveis")},
            },
        },
    }


# ── Routes ──


@app.route("/")
@app.route("/<lang_code>/")
def index():
    if g.lang_code not in SUPPORTED_LANGS:
        return redirect("/")
    # Auto-detect language on root URL (no lang_code in path)
    if request.path == "/" and not request.args.get("hl"):
        best = request.accept_languages.best_match(SUPPORTED_LANGS, default="en")
        if best != "en":
            return redirect(f"/{best}/")
    return render_template("index.html")


@app.route("/privacy")
@app.route("/<lang_code>/privacy")
def privacy():
    if g.lang_code not in SUPPORTED_LANGS:
        return redirect("/privacy")
    return render_template(f"privacy_{g.lang_code}.html")


@app.route("/terms")
@app.route("/<lang_code>/terms")
def terms():
    if g.lang_code not in SUPPORTED_LANGS:
        return redirect("/terms")
    return render_template(f"terms_{g.lang_code}.html")


@app.route("/robots.txt")
def robots():
    content = "User-agent: *\nAllow: /\nSitemap: https://oxepass.com/sitemap.xml\n"
    return Response(content, mimetype="text/plain")


@app.route("/sitemap.xml")
def sitemap():
    content = """<?xml version="1.0" encoding="UTF-8"?>
<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"
        xmlns:xhtml="http://www.w3.org/1999/xhtml">
  <url>
    <loc>https://oxepass.com/</loc>
    <xhtml:link rel="alternate" hreflang="en" href="https://oxepass.com/" />
    <xhtml:link rel="alternate" hreflang="pt" href="https://oxepass.com/pt/" />
    <xhtml:link rel="alternate" hreflang="es" href="https://oxepass.com/es/" />
    <changefreq>monthly</changefreq>
    <priority>1.0</priority>
  </url>
  <url>
    <loc>https://oxepass.com/privacy</loc>
    <xhtml:link rel="alternate" hreflang="en" href="https://oxepass.com/privacy" />
    <xhtml:link rel="alternate" hreflang="pt" href="https://oxepass.com/pt/privacy" />
    <xhtml:link rel="alternate" hreflang="es" href="https://oxepass.com/es/privacy" />
    <changefreq>yearly</changefreq>
    <priority>0.3</priority>
  </url>
  <url>
    <loc>https://oxepass.com/terms</loc>
    <xhtml:link rel="alternate" hreflang="en" href="https://oxepass.com/terms" />
    <xhtml:link rel="alternate" hreflang="pt" href="https://oxepass.com/pt/terms" />
    <xhtml:link rel="alternate" hreflang="es" href="https://oxepass.com/es/terms" />
    <changefreq>yearly</changefreq>
    <priority>0.3</priority>
  </url>
</urlset>"""
    return Response(content, mimetype="application/xml")


@app.route("/generate", methods=["POST"])
@app.route("/<lang_code>/generate", methods=["POST"])
def generate():
    pw_type = request.form.get("type", "random")
    count = max(1, min(10, int(request.form.get("count", 1))))
    exclude = request.form.get("exclude", "")

    entries = []

    for _ in range(count):
        if pw_type == "memorable":
            pwd, parts = generate_memorable()
            entries.append({"password": pwd, "parts": parts})

        elif pw_type == "backup":
            pwd = generate_backup_code()
            entries.append({"password": pwd, "parts": None})

        elif pw_type == "shell":
            length = max(4, min(64, int(request.form.get("length", 20))))
            use_upper = request.form.get("uppercase") == "true"
            use_lower = request.form.get("lowercase") == "true"
            use_nums = request.form.get("numbers") == "true"
            shell_exclude = exclude + "!#$%^&*()[]{}|;<>?"
            pwd = generate_password(length, use_upper, use_lower, use_nums, True, exclude=shell_exclude)
            entries.append({"password": pwd, "parts": None})

        elif pw_type == "url":
            length = max(4, min(64, int(request.form.get("length", 20))))
            use_upper = request.form.get("uppercase") == "true"
            use_lower = request.form.get("lowercase") == "true"
            use_nums = request.form.get("numbers") == "true"
            url_exclude = exclude + "!@#$%^&*()+=[]{}|;:,<>?"
            pwd = generate_password(length, use_upper, use_lower, use_nums, True, exclude=url_exclude)
            entries.append({"password": pwd, "parts": None})

        else:
            length = max(4, min(64, int(request.form.get("length", 16))))
            use_upper = request.form.get("uppercase") == "true"
            use_lower = request.form.get("lowercase") == "true"
            use_nums = request.form.get("numbers") == "true"
            use_syms = request.form.get("symbols") == "true"
            child   = pw_type == "child"
            elderly = pw_type == "elderly"
            wifi    = pw_type == "wifi"

            if not any([use_upper, use_lower, use_nums, use_syms]):
                use_lower = True

            pwd = generate_password(length, use_upper, use_lower, use_nums, use_syms, exclude=exclude, child_mode=child or elderly, wifi_mode=wifi)
            entries.append({"password": pwd, "parts": None})

    strength = password_strength(entries[0]["password"])

    return render_template(
        "partials/password_result.html",
        entries=entries,
        strength=strength,
        pw_type=pw_type,
    )


if __name__ == "__main__":
    app.run(debug=True, port=8080, ssl_context="adhoc")
